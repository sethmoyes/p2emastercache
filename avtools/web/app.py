#!/usr/bin/env python3
"""
The campaign web app: the GM's table view, the players' market square, and
the atlas.

    python3 -m avtools.web.app        # http://localhost:5001
"""

from flask import Flask, render_template, jsonify, request, session, Response, abort
from functools import wraps
import hashlib
import hmac
import io
import random
import re
import secrets
import subprocess
import sys
import os
import json
import threading
import time
import zipfile

from avtools.data import DATA_DIR, ROOT as PROJECT_ROOT, creatures as load_creatures, find_creature
from avtools.dungeon_turn import generate_event_for_sum, floor_levels
from avtools.hazards import generate_hazard, format_output
from avtools.merchants import (
    MERCHANT_CONFIGS,
    SETTINGS_SCHEMA,
    TRAVELING_FILE,
    merchant_slug,
    normalize_settings
)
from avtools.npcs import generate_npc, format_npc_narrative, generate_npc_encounter_template
from avtools.web.render import render_markdown

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024

# ------------------------------------------------------------------- GM login
# Anything that changes shared state (restocks, map pins, the dice jar, roll
# history) needs the GM password, which lives in the GM_PASSWORD secret. Pages
# and read-only APIs stay open. Without a password set, writes are open too,
# which is what you want running locally, but never on Fly.
GM_PASSWORD = os.environ.get('GM_PASSWORD', '')
ON_FLY = bool(os.environ.get('FLY_APP_NAME'))

app.secret_key = (os.environ.get('SECRET_KEY')
                  or (hashlib.sha256(b'p2e-session:' + GM_PASSWORD.encode()).hexdigest() if GM_PASSWORD
                      else secrets.token_hex(32)))
app.config.update(
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=ON_FLY,
    PERMANENT_SESSION_LIFETIME=60 * 60 * 24 * 30,
)


def gm_write(view):
    """Refuse a write unless the GM has logged in (or no password is set locally)."""
    @wraps(view)
    def guarded(*args, **kwargs):
        if not GM_PASSWORD:
            if ON_FLY:
                return jsonify({'error': 'GM_PASSWORD is not set on this server.'}), 503
        elif not session.get('gm'):
            return jsonify({'error': 'GM login required.', 'login': True}), 401
        return view(*args, **kwargs)
    return guarded


def is_gm():
    return session.get('gm') or (not GM_PASSWORD and not ON_FLY)


def json_body():
    """The request's JSON object. A form or text/plain post (the kind another
    site can send) is refused, and so is anything that isn't an object."""
    body = request.get_json(silent=False)
    if not isinstance(body, dict):
        from werkzeug.exceptions import BadRequest
        raise BadRequest('Expected a JSON object.')
    return body


@app.route('/api/gm-login', methods=['POST'])
def gm_login():
    password = str(json_body().get('password', ''))
    if GM_PASSWORD and not hmac.compare_digest(password, GM_PASSWORD):
        return jsonify({'error': 'Incorrect password'}), 401
    session.permanent = True
    session['gm'] = True
    return jsonify({'success': True})


@app.errorhandler(400)
@app.errorhandler(413)
@app.errorhandler(415)
def bad_request(error):
    return jsonify({'error': getattr(error, 'description', str(error))}), error.code


@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'The server hit an error. Check the logs.'}), 500

# DATA_DIR is where anything the app writes goes: restocked merchants, map
# pins, the GM's session (dice jar, history). On Fly it's a mounted volume,
# because a machine's own disk resets to the image every time it stops;
# locally it's the repo itself, same as running the generator by hand.


def data_file(rel):
    """The newest copy of a data file, on the volume or baked into the image.

    Newest wins both ways: a restock on the server beats the copy in the image,
    and a copy you regenerated locally and deployed beats an older restock.
    """
    candidates = [os.path.join(root, rel) for root in (DATA_DIR, PROJECT_ROOT)]
    existing = [path for path in candidates if os.path.exists(path)]
    return max(existing, key=os.path.getmtime) if existing else None


def merchant_path(subdir, filename):
    return data_file(os.path.join(subdir, filename))


def write_json_atomic(path, data):
    """Write to a temp file and swap it in, so a reader never sees half a file."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = f'{path}.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)

# Load data once at startup
print("Loading dungeon data...")
levels_data = floor_levels()
creatures = load_creatures()
print(f"Loaded {len(levels_data)} floors and {len(creatures)} creatures")

# --------------------------------------------------------------- GM session
# The table's running state lives in a file in DATA_DIR, so it survives the
# machine stopping between rolls and every GM device sees the same jar.
SESSION_PATH = os.path.join(DATA_DIR, 'state', 'session.json')
SESSION_DEFAULTS = {
    'floor': 1,
    'party_level': 4,
    'party_size': 4,
    'dice_jar': 0,
    'prepared_tokens': 0,
    'history': [],
}
# Settable fields and their allowed ranges
SESSION_FIELDS = {
    'floor': (1, 10),
    'party_level': (1, 20),
    'party_size': (1, 8),
    'dice_jar': (0, 12),
    'prepared_tokens': (0, 9),
}
JAR_ROLL_AT = 5      # a roll uses up this many dice
HISTORY_KEEP = 20    # full events, so the GM can reopen them
session_lock = threading.Lock()


def load_session():
    try:
        with open(SESSION_PATH, 'r', encoding='utf-8') as f:
            saved = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        saved = {}
    state = {**json.loads(json.dumps(SESSION_DEFAULTS)), **saved}
    # Older session files kept only a summary per roll
    state['history'] = [h for h in state['history'] if isinstance(h, dict) and 'event' in h]
    return state


def update_session(change):
    """Apply change(state) under the lock and save; returns the new state."""
    with session_lock:
        state = load_session()
        change(state)
        for key, (low, high) in SESSION_FIELDS.items():
            state[key] = max(low, min(high, int(state[key])))
        state['history'] = state['history'][-HISTORY_KEEP:]
        write_json_atomic(SESSION_PATH, state)
        return state


def int_field(data, key, low, high, default=None):
    """An integer from the request body, or a 400 if it's missing or out of range."""
    from werkzeug.exceptions import BadRequest
    value = data.get(key, default)
    try:
        value = int(value)
    except (TypeError, ValueError):
        raise BadRequest(f'{key} must be a whole number')
    if not low <= value <= high:
        raise BadRequest(f'{key} must be between {low} and {high}')
    return value


def session_view(state):
    return {**state, 'roll_at': JAR_ROLL_AT,
            'floors': {n: levels_data[n]['name'] for n in sorted(levels_data)}}


@app.route('/api/session', methods=['GET'])
def get_session():
    return jsonify(session_view(load_session()))


@app.route('/api/session', methods=['POST'])
@gm_write
def change_session():
    """Body: {"set": {field: value}, "add": {"dice_jar": n, "prepared_tokens": n},
    "clear_history": true}. Values are clamped to each field's range."""
    body = json_body()
    sets = body.get('set') or {}
    adds = body.get('add') or {}
    if not isinstance(sets, dict) or not isinstance(adds, dict):
        return jsonify({'error': 'set and add must be objects'}), 400
    for key in list(sets) + list(adds):
        if key not in SESSION_FIELDS:
            return jsonify({'error': f'unknown field: {key}'}), 400
    for key, value in sets.items():
        int_field(sets, key, *SESSION_FIELDS[key])
    for key in adds:
        int_field(adds, key, -12, 12)

    def change(state):
        for key, value in sets.items():
            state[key] = int(value)
        for key, value in adds.items():
            state[key] = state[key] + int(value)
        if body.get('clear_history'):
            state['history'] = []

    return jsonify(session_view(update_session(change)))


@app.route('/healthz')
def healthz():
    return jsonify({'ok': True, 'commit': os.environ.get('GIT_SHA', 'unknown')})

@app.route('/')
def index():
    """Landing page with PLAYER and GM buttons"""
    return render_template('landing.html')

def shop_list():
    shops = []
    for config in MERCHANT_CONFIGS:
        slug = merchant_slug(config['name'])
        path = merchant_path('players', f'{slug}.md')
        shops.append({
            'slug': slug,
            'name': config['name'],
            'description': config['description'],
            'proprietor': config['proprietor'],
            'specialties': config['specialties'],
            'updated': time.strftime('%b %d', time.localtime(os.path.getmtime(path))) if path else None,
        })
    return shops


def markdown_page(path):
    """(title, html) for a markdown file; the title is its first # heading."""
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    first = content.split('\n', 1)[0]
    if first.startswith('# '):
        content = content.split('\n', 1)[1] if '\n' in content else ''
        return first[2:].strip(), render_markdown(content)
    return None, render_markdown(content)


@app.route('/players')
def players():
    """Player-facing market square: Otari's shops, the town map, the guide"""
    return render_template('players.html', shops=shop_list(), otari=next(
        (m for m in load_maps() if m['id'] == 'otari'), None))


@app.route('/players/shop/<slug>')
def player_shop(slug):
    config = next((c for c in MERCHANT_CONFIGS if merchant_slug(c['name']) == slug), None)
    path = merchant_path('players', f'{slug}.md') if config else None
    if not path:
        abort(404)
    title, html = markdown_page(path)
    return render_template('shop.html', title=title or config['name'], html=html)


@app.route('/players/guide')
def player_guide():
    title, html = markdown_page(os.path.join(PROJECT_ROOT, 'docs', 'DUNGEON_EXPLORATION_GUIDE.md'))
    return render_template('shop.html', title=title or 'Exploration Guide', html=html)

@app.route('/gm')
def gm():
    """The GM's table view: session bar, rolls, encounter card, quick tools"""
    return render_template('gm.html')


@app.route('/gm/admin')
def gm_admin():
    """Restocking, backups and the test generator"""
    return render_template('gm_admin.html')

# ---------------------------------------------------------------- Atlas / maps

MAPS_REGISTRY = os.path.join(PROJECT_ROOT, 'etc', 'maps.json')


def load_maps():
    """Map registry written by bin/maps/tile_map.py."""
    try:
        with open(MAPS_REGISTRY, 'r', encoding='utf-8') as f:
            return json.load(f).get('maps', [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def poi_file(filename):
    """A POI file's name, if it is a plain file name listed under etc/."""
    name = os.path.basename(filename or '')
    return name if name and name == filename and name.endswith('.json') else None


def poi_path(filename):
    """The newest copy of a POI file (pins saved on the server, or the repo's)."""
    name = poi_file(filename)
    return data_file(os.path.join('etc', name)) if name else None


@app.route('/atlas')
def atlas():
    """Interactive tiled map atlas with clickable points of interest.

    ?embed=1 hides the page header so the viewer can be framed inside another
    page, such as the players' market square.
    """
    return render_template('atlas.html', embed=request.args.get('embed') == '1', can_place=is_gm())


@app.route('/api/maps', methods=['GET'])
def api_maps():
    return jsonify({'maps': load_maps()})


@app.route('/api/pois/<map_id>', methods=['GET'])
def api_pois(map_id):
    """Every POI for a map, including unplaced ones (x/y null).

    A POI file can back several maps (the whole city and one district, say), so
    coordinates are stored per map under "coords". Here we flatten this map's
    entry into plain x/y, which keeps the viewer's job simple.
    """
    entry = next((m for m in load_maps() if m['id'] == map_id), None)
    if not entry:
        return jsonify({'error': f'unknown map: {map_id}'}), 404

    path = poi_path(entry.get('pois'))
    if not path:
        return jsonify({'map': map_id, 'groups': [], 'locations': [], 'count': 0})

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # A district map shows only its own slice of a shared POI file.
    only_groups = entry.get('poi_groups')
    locations = []
    for loc in data.get('locations', []):
        if only_groups and loc.get('group') not in only_groups:
            continue
        here = (loc.get('coords') or {}).get(map_id) or {}
        flat = {k: v for k, v in loc.items() if k != 'coords'}
        flat['x'] = here.get('x')
        flat['y'] = here.get('y')
        flat['approx'] = bool(here.get('approx'))
        locations.append(flat)

    groups = data.get('groups', [])
    if only_groups:
        groups = [g for g in groups if g in only_groups]

    return jsonify({
        'map': map_id,
        'group_by': data.get('group_by', 'type'),
        'groups': groups,
        'count': len(locations),
        'locations': locations,
    })


poi_lock = threading.Lock()


@app.route('/api/pois/<map_id>', methods=['POST'])
@gm_write
def api_save_pois(map_id):
    """Persist pin coordinates from the viewer's placement mode.

    Body: {"placements": {"<poi id>": {"x": 0.42, "y": 0.61} | null, ...}}
    Coordinates are 0-1 fractions of the image, so they survive swapping the
    underlying map image for a higher-resolution one, and are stored under
    coords[<map id>] so one POI file can back several maps.
    """
    entry = next((m for m in load_maps() if m['id'] == map_id), None)
    if not entry:
        return jsonify({'error': f'unknown map: {map_id}'}), 404

    path = poi_path(entry.get('pois'))
    if not path:
        return jsonify({'error': f'no POI file configured for {map_id}'}), 400

    placements = json_body().get('placements') or {}
    if not isinstance(placements, dict):
        return jsonify({'error': 'placements must be an object'}), 400

    with poi_lock:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        updated = 0
        cleared = 0
        for loc in data.get('locations', []):
            if loc.get('id') not in placements:
                continue
            coords = placements[loc['id']]
            store = loc.setdefault('coords', {})
            if coords is None:
                if store.pop(map_id, None) is not None:
                    cleared += 1
            else:
                try:
                    x = min(1.0, max(0.0, float(coords['x'])))
                    y = min(1.0, max(0.0, float(coords['y'])))
                except (TypeError, ValueError, KeyError):
                    continue
                # A hand placement is deliberate, so it is no longer approximate.
                store[map_id] = {'x': round(x, 6), 'y': round(y, 6)}
                updated += 1

        data['count'] = len(data.get('locations', []))
        write_json_atomic(os.path.join(DATA_DIR, 'etc', poi_file(entry.get('pois'))), data)

    only_groups = entry.get('poi_groups')
    scoped = [l for l in data.get('locations', [])
              if not only_groups or l.get('group') in only_groups]
    placed = sum(1 for l in scoped if (l.get('coords') or {}).get(map_id))
    return jsonify({
        'success': True, 'updated': updated, 'cleared': cleared,
        'placed': placed, 'total': len(scoped),
    })

@app.route('/api/encounter', methods=['POST'])
@gm_write
def get_encounter():
    """Generate the encounter for a 5d20 total on a floor.

    Floor and party default to the saved session. "use_jar": true spends the
    jar's dice (the roll came out of the jar); the test generator leaves it off.
    """
    data = json_body()
    state = load_session()
    floor = int_field(data, 'floor', 1, 10, state['floor'])
    dice_sum = int_field(data, 'sum', 5, 100)
    party_level = int_field(data, 'party_level', 1, 20, state['party_level'])
    party_size = int_field(data, 'party_size', 1, 8, state['party_size'])
    allow_no_event = bool(data.get('allow_no_event', True))

    floor_data = levels_data.get(floor)
    if not floor_data:
        return jsonify({'error': f'Floor {floor} not found'}), 404

    event = generate_event_for_sum(dice_sum, floor, floor_data, party_level, creatures, party_size,
                                   allow_no_event)
    event['floor'] = floor
    if event.get('creature_reference'):
        event['creature_stats'] = creature_stats_for(event)

    if data.get('record', True):
        def change(state):
            state['history'].append({'time': time.time(), 'event': event})
            if data.get('use_jar'):
                state['dice_jar'] = max(0, state['dice_jar'] - JAR_ROLL_AT)
        update_session(change)

    return jsonify(event)


creatures_by_url = {c['url']: c for c in creatures if c.get('url')}


def creature_stats_for(event):
    """Full stat blocks for a combat's creatures. Names repeat across legacy and
    remaster entries, so match the AoN link the event cites when it has one."""
    refs = event.get('creature_reference') or {}
    # Combat events list creature names; templates describe them in prose ("1d3 Ghouls")
    names = event['creatures'] if isinstance(event.get('creatures'), list) else list(refs)
    stats = []
    for name in names:
        url = (refs.get(name) or {}).get('aon_url', '').replace('https://2e.aonprd.com', '')
        creature = creatures_by_url.get(url) or find_creature(creatures, name)
        if not creature:
            continue
        stats.append({
            'name': creature['name'],
            'level': creature['level'],
            'hp': creature.get('hp'),
            'ac': creature.get('ac'),
            'fort': creature.get('fort', ''),
            'reflex': creature.get('reflex', ''),
            'will': creature.get('will', ''),
            'perception': creature.get('perception', ''),
            'attacks': creature.get('attacks', []),
            'abilities': creature.get('abilities', []),
            'languages': creature.get('languages', []),
            'immunities': creature.get('immunities', []),
            'resistances': creature.get('resistances', []),
            'weaknesses': creature.get('weaknesses', []),
            'traits': creature.get('traits', []),
            'rarity': creature.get('rarity', 'common'),
            'size': creature.get('size', ''),
            'url': creature.get('url', ''),
            'image': creature.get('image', [''])[0] if creature.get('image') else '',
        })
    return stats


@app.route('/api/generate-npc', methods=['GET'])
def generate_npc_api():
    """Generate a random NPC"""
    try:
        
        npc = generate_npc()
        template = generate_npc_encounter_template(npc)
        narrative = format_npc_narrative(npc)
        
        content = f"""# {template['name']}

**Race:** {template['race']}
**Profession:** {template['profession']}
**Personality:** {template['personality']}

## Setup
{template['setup']}

## Read-Aloud
{template['readaloud']}

## Background
{narrative}

## GM Notes
- Use this NPC for social encounters
- Can provide information, quests, or complications
- Personality: {template['personality']}
"""
        
        return jsonify({
            'name': template['name'],
            'content': content
        })
    except Exception as e:
        app.logger.exception('NPC generation failed')
        return jsonify({'error': f'Could not generate an NPC: {e}'}), 500

# The documents the GM page can open, by id. Nothing outside this list is served.
GM_DOCS = {
    'quick-reference': 'gm/DUNGEON_TURN_V2_QUICK_REFERENCE.md',
    'exploration-guide': 'docs/DUNGEON_EXPLORATION_GUIDE.md',
}


@app.route('/api/gm-doc/<doc_id>', methods=['GET'])
def get_gm_doc(doc_id):
    rel = GM_DOCS.get(doc_id)
    if not rel:
        return jsonify({'error': 'Document not found'}), 404
    title, html = markdown_page(os.path.join(PROJECT_ROOT, rel))
    return jsonify({'title': title or doc_id.replace('-', ' ').title(), 'html': html})

@app.route('/api/generate-hazard', methods=['POST'])
def generate_hazard_api():
    """Generate a random hazard of specified level"""
    level = int_field(json_body(), 'level', -1, 10, 1)

    try:
        
        hazard = generate_hazard(level)
        content = format_output(hazard)
        
        return jsonify({
            'level': level,
            'name': hazard.get('name', 'Unknown'),
            'content': content,
            'hazard': hazard
        })
    except Exception as e:
        app.logger.exception('hazard generation failed')
        return jsonify({'error': f'Could not generate a hazard: {e}'}), 500

def traveling_merchant_dir():
    """The gm/ folder holding the newest set of traveling merchants.

    A restock writes the whole set at once, so the set comes from whichever
    copy (volume or image) was written last, never a mix of the two.
    """
    newest, newest_time = None, -1
    for root in (DATA_DIR, PROJECT_ROOT):
        gm_dir = os.path.join(root, 'gm')
        if not os.path.isdir(gm_dir):
            continue
        times = [os.path.getmtime(os.path.join(gm_dir, name))
                 for name in os.listdir(gm_dir) if TRAVELING_FILE.match(name)]
        if times and max(times) > newest_time:
            newest, newest_time = gm_dir, max(times)
    return newest


@app.route('/api/gm-merchants', methods=['GET'])
def get_gm_merchants():
    """The current traveling merchants, in slot order."""
    gm_dir = traveling_merchant_dir()
    merchants = []
    for name in os.listdir(gm_dir) if gm_dir else []:
        slot = TRAVELING_FILE.match(name)
        if not slot:
            continue
        path = os.path.join(gm_dir, name)
        with open(path, 'r', encoding='utf-8') as f:
            first = f.readline()
        merchants.append({
            'file': name[:-3],
            'slot': int(slot.group(1)),
            'name': first.lstrip('#').strip() or name[:-3],
            'updated': os.path.getmtime(path),
        })
    merchants.sort(key=lambda m: m['slot'])
    return jsonify({'merchants': merchants})


@app.route('/api/gm-merchant/<merchant_file>', methods=['GET'])
def get_gm_merchant(merchant_file):
    """Load a traveling merchant and return it as HTML"""
    gm_dir = traveling_merchant_dir()
    if not gm_dir or not TRAVELING_FILE.match(f'{merchant_file}.md'):
        return jsonify({'error': 'Merchant not found'}), 404
    path = os.path.join(gm_dir, f'{merchant_file}.md')
    if not os.path.exists(path):
        return jsonify({'error': 'Merchant not found'}), 404

    title, html = markdown_page(path)
    return jsonify({'title': title or merchant_file.replace('_', ' ').title(), 'html': html})

# ------------------------------------------------------------------ Export
# What the server has written (restocks, pins, the session), zipped with the
# same layout as the repo, so `unzip -o export.zip` in the repo root brings it
# home to be committed.
EXPORT_GLOBS = [('players', '.md'), ('gm', '.md'), ('etc', '_locations.json'), ('state', '.json')]


@app.route('/api/export', methods=['GET'])
@gm_write
def export_data():
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as archive:
        for folder, suffix in EXPORT_GLOBS:
            path = os.path.join(DATA_DIR, folder)
            if not os.path.isdir(path):
                continue
            for name in sorted(os.listdir(path)):
                if name.endswith(suffix):
                    archive.write(os.path.join(path, name), f'{folder}/{name}')
    stamp = time.strftime('%Y-%m-%d')
    return Response(buffer.getvalue(), mimetype='application/zip',
                    headers={'Content-Disposition': f'attachment; filename="p2e-export-{stamp}.zip"'})


# ---------------------------------------------------------- Merchant restocking

PROGRESS_LINE = re.compile(r'^\[(\d+)/(\d+)\] Generating (.+?)\.\.\.$')

# The latest restock run. Only one runs at a time, and it lives in this process,
# which is why gunicorn runs a single worker (see Dockerfile).
merchant_job = None
merchant_job_lock = threading.Lock()


def run_merchant_job(job):
    """Run the generator script, recording its output and progress on the job."""
    try:
        process = subprocess.Popen(
            [sys.executable, '-u', '-m', 'avtools.merchants',
             '--settings-json', json.dumps(job['settings']),
             '--output-root', DATA_DIR],
            cwd=PROJECT_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        for line in process.stdout:
            line = line.rstrip()
            job['log'].append(line)
            progress = PROGRESS_LINE.match(line)
            if progress:
                job['step'], job['total'] = int(progress.group(1)), int(progress.group(2))
                job['current'] = progress.group(3)
        process.wait()
        job['status'] = 'done' if process.returncode == 0 else 'failed'
    except Exception as e:
        job['log'].append(f'ERROR: {e}')
        job['status'] = 'failed'
    job['finished'] = time.time()


def merchant_job_view(job, since=0):
    """The job as the GM page sees it, with log lines from `since` onward."""
    return {
        'status': job['status'],
        'step': job['step'],
        'total': job['total'],
        'current': job['current'],
        'started': job['started'],
        'finished': job['finished'],
        'log': job['log'][since:],
        'next': len(job['log']),
    }


@app.route('/api/merchant-generator', methods=['GET'])
def merchant_generator_config():
    """Everything the restock form needs: the settings schema and the shop list."""
    return jsonify({
        'schema': SETTINGS_SCHEMA,
        'merchants': [
            {'slug': merchant_slug(c['name']), 'name': c['name'], 'specialties': c['specialties']}
            for c in MERCHANT_CONFIGS
        ],
        'job': merchant_job_view(merchant_job) if merchant_job else None,
    })


@app.route('/api/merchant-generator/run', methods=['POST'])
@gm_write
def start_merchant_job():
    """Start a restock in the background; the GM page polls the status endpoint."""
    global merchant_job
    settings = normalize_settings(json_body())
    if not settings['merchants'] and not settings['random_merchants']:
        return jsonify({'error': 'Pick at least one shop or traveling merchant.'}), 400

    with merchant_job_lock:
        if merchant_job and merchant_job['status'] == 'running':
            return jsonify({'error': 'A restock is already running.'}), 409
        job = {
            'status': 'running',
            'settings': settings,
            'step': 0,
            'total': len(settings['merchants']) + settings['random_merchants'],
            'current': None,
            'started': time.time(),
            'finished': None,
            'log': [],
        }
        merchant_job = job
        threading.Thread(target=run_merchant_job, args=(job,), daemon=True).start()

    return jsonify(merchant_job_view(job))


@app.route('/api/merchant-generator/status', methods=['GET'])
def merchant_job_status():
    if not merchant_job:
        return jsonify({'status': 'idle'})
    return jsonify(merchant_job_view(merchant_job, request.args.get('since', 0, type=int)))

if __name__ == '__main__':
    print("\n" + "="*80)
    print("DUNGEON TURN V2 - WEB INTERFACE")
    print("="*80)
    print("\nStarting server...")
    print("Open your browser to: http://localhost:5001")
    print("\nPress Ctrl+C to stop")
    print("="*80 + "\n")

    # FLASK_DEBUG=1 for the reloader and debugger; it stays on this machine only.
    app.run(debug=os.environ.get('FLASK_DEBUG') == '1', host='127.0.0.1', port=5001)
