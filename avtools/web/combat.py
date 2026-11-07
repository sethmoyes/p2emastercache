"""
The GM's combat tracker: the party, the fight (initiative, monster HP,
conditions), and finding monsters by name, by room code, or from a
dungeon-turn roll.

The rules live in avtools/combat.py; this file stores the party and the fight
in DATA_DIR/state (the Fly volume, so both survive deploys) and looks creatures
up on the Archives of Nethys through avtools/aon.py.
"""

import json
import os
import re
import threading
import uuid

from flask import Blueprint, jsonify, render_template, request

from avtools import aon, combat
from avtools.data import AON_BASE, DATA_DIR, conditions, floor_ecology, room_encounters
from avtools.web.core import gm_write, json_body, write_json_atomic
from avtools.web.render import render_markdown

bp = Blueprint('combat', __name__)

HEROES_PATH = os.path.join(DATA_DIR, 'state', 'heroes.json')
COMBAT_PATH = os.path.join(DATA_DIR, 'state', 'combat.json')
MAX_HEROES = 12
NAME_MAX = 40
ROOM_CODE = re.compile(r'^[A-Ja-j]\d{1,2}[a-z]?$')
lock = threading.Lock()


def _read(path, default):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


@bp.route('/gm/combat')
def combat_page():
    """Initiative and monster HP for the fight at the table"""
    return render_template('combat.html')


# ------------------------------------------------------------------- party

def load_heroes():
    return _read(HEROES_PATH, {'heroes': []})['heroes']


def clean_heroes(heroes):
    if not isinstance(heroes, list) or len(heroes) > MAX_HEROES:
        raise combat.CombatError(f'Send a list of up to {MAX_HEROES} heroes')
    cleaned = []
    for hero in heroes:
        if not isinstance(hero, dict):
            raise combat.CombatError('Each hero needs a name')
        name = str(hero.get('name', '')).strip()[:NAME_MAX]
        if not name:
            raise combat.CombatError('Each hero needs a name')
        hero_id = str(hero.get('id') or '')
        cleaned.append({'id': hero_id if re.fullmatch(r'h[0-9a-f]{8}', hero_id) else f'h{uuid.uuid4().hex[:8]}',
                        'name': name, 'player': str(hero.get('player', '')).strip()[:NAME_MAX],
                        'active': bool(hero.get('active', True))})
    return cleaned


@bp.route('/api/heroes', methods=['GET'])
def get_heroes():
    return jsonify({'heroes': load_heroes()})


@bp.route('/api/heroes', methods=['POST'])
@gm_write
def save_heroes():
    """Body: {"heroes": [{"id"?, "name", "player"?, "active"?}]}, the whole party."""
    try:
        heroes = clean_heroes(json_body().get('heroes'))
    except combat.CombatError as error:
        return jsonify({'error': str(error)}), 400
    with lock:
        write_json_atomic(HEROES_PATH, {'heroes': heroes})
        # Renaming a hero renames them in the fight too
        state = load_combat()
        names = {h['id']: h['name'] for h in heroes}
        for slot in state['slots']:
            if slot.get('hero_id') in names:
                slot['name'] = names[slot['hero_id']]
        write_json_atomic(COMBAT_PATH, state)
    return jsonify({'heroes': heroes})


# ------------------------------------------------------------------- fight

def load_combat():
    return {**combat.new_state(), **_read(COMBAT_PATH, {})}


def combat_view(state):
    out = combat.view(state)
    out['creatures'] = {k: {f: v for f, v in s.items() if f != 'statblock'} for k, s in state['creatures'].items()}
    return out


@bp.route('/api/combat', methods=['GET'])
def get_combat():
    return jsonify(combat_view(load_combat()))


@bp.route('/api/combat', methods=['POST'])
@gm_write
def change_combat():
    """Body: {"op": ..., ...}; see avtools.combat.OPS. Also "add_room" with a
    room code and "add_event" with a dungeon-turn event, which become "add"."""
    op = json_body()
    try:
        if op.get('op') == 'add_room':
            op = {'op': 'add', 'roll': op.get('roll'), 'creatures': room_creatures(op.get('code'))}
        elif op.get('op') == 'add_event':
            op = {'op': 'add', 'roll': op.get('roll'), 'creatures': event_creatures(op.get('event'))}
        with lock:
            state = load_combat()
            if 'version' in op and op['version'] != state['version']:
                return jsonify({'error': 'The fight changed on another screen; showing the latest.',
                                'combat': combat_view(state)}), 409
            state = combat.apply(state, op, heroes=load_heroes(), lookup=aon.creature)
            write_json_atomic(COMBAT_PATH, state)
    except combat.CombatError as error:
        return jsonify({'error': str(error)}), 400
    return jsonify(combat_view(state))


# ---------------------------------------------------------- finding monsters

def room_creatures(code):
    room = room_encounters().get(str(code or '').strip().upper())
    if not room:
        raise combat.CombatError(f'No keyed room {code} with creatures')
    if not room['creatures']:
        raise combat.CombatError(f'{code}: nothing on AoN to add (' + '; '.join(room.get('unresolved', [])) + ')')
    return [{'key': c['key'], 'count': c['count']} for c in room['creatures']]


DICE_COUNT = re.compile(r'(\d+d\d+(?:\s*[+-]\s*\d+)?|\d+)\s+(?:[A-Za-z\'-]+\s+){0,3}$')


def _count_before(text, name):
    """The count written in front of a creature's name: "1d3+1 Morlocks" -> "1d3+1"."""
    stem = name.lower()[:max(4, len(name) - 2)]
    i = text.lower().find(stem)
    if i < 0:
        return 1
    m = DICE_COUNT.search(text[max(0, i - 30):i])
    return m.group(1).replace(' ', '') if m else 1


def event_creatures(event):
    """The creatures in a dungeon-turn event, with counts: from the roster
    combat events carry, else their "2x Ghoul (Level 1...)" summary, else the
    count written before each name in a template's creature text."""
    if not isinstance(event, dict):
        raise combat.CombatError('Send the event')
    refs = event.get('creature_reference') or {}

    def key(name):
        url = ((refs.get(name) or {}).get('aon_url') or '').replace(AON_BASE, '')
        return url if aon.valid_key(url) else aon.key_for_name(name)

    if isinstance(event.get('roster'), list):
        found = [(r.get('key'), r.get('count', 1)) for r in event['roster'] if isinstance(r, dict)]
    elif event.get('creature_summary'):
        found = [(key(name.strip()), int(n)) for n, name in
                 re.findall(r'(\d+)x ([^(,]+?) \(Level', event['creature_summary'])]
    else:
        text = event.get('creatures') if isinstance(event.get('creatures'), str) else ''
        names = list(refs) or [c.get('name') for c in event.get('creature_stats') or [] if c.get('name')]
        found = [(key(name), _count_before(text, name)) for name in names]
    creatures = [{'key': k, 'count': n} for k, n in found if k]
    if not creatures:
        raise combat.CombatError('This event has no creatures to fight')
    return creatures


def _favored():
    names = {c['name'] for room in room_encounters().values() for c in room['creatures']}
    for floor in floor_ecology().values():
        for entry in floor['entries']:
            names.update(g['creature'] for g in entry.get('group', []))
            if entry.get('creature'):
                names.add(entry['creature'])
    return names


FAVORED = None


@bp.route('/api/creatures/search')
def search_creatures():
    """?q=morlock (or a room code like A10): matching rooms and creatures."""
    global FAVORED
    if FAVORED is None:
        FAVORED = _favored()
    q = request.args.get('q', '').strip()
    rooms = []
    if ROOM_CODE.match(q):
        code = q.upper()
        # A1 shows A1 first, then A10-A19, as you type
        matches = sorted((c for c in room_encounters() if c.startswith(code)), key=lambda c: (c != code, len(c), c))
        rooms = [{'code': c, **room_encounters()[c]} for c in matches[:8]]
    result = aon.search(q, FAVORED) if len(q) >= 2 and not (ROOM_CODE.match(q) and rooms) else {'results': [], 'source': 'aon'}
    return jsonify({'rooms': rooms, **result})


@bp.route('/api/creatures/stats')
def creature_stats():
    """?key=/Monsters.aspx?ID=731: the full stat record, with the stat block as HTML."""
    stats = aon.creature(request.args.get('key', ''))
    if not stats:
        return jsonify({'error': 'Creature not found'}), 404
    stats['statblock_html'] = render_markdown(stats.pop('statblock', ''))
    return jsonify(stats)


@bp.route('/api/rooms')
def list_rooms():
    return jsonify({'rooms': [{'code': c, **r} for c, r in room_encounters().items()]})


@bp.route('/api/conditions')
def list_conditions():
    return jsonify({'conditions': [{**c, 'url': AON_BASE + c['url']} for c in conditions().values()]})
