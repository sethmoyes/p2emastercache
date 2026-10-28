"""
The GM's table: the session (floor, party, dice jar, Prepared tokens, roll
history), rolling encounters, and the quick tools (NPCs, hazards, GM docs).
"""

import json
import os
import threading
import time

from flask import Blueprint, current_app, jsonify

from avtools.data import creatures as load_creatures, find_creature
from avtools.dungeon_turn import generate_event_for_sum, floor_levels
from avtools.hazards import generate_hazard, format_output
from avtools.npcs import generate_npc, format_npc_narrative, generate_npc_encounter_template
from avtools.web.core import DATA_DIR, PROJECT_ROOT, gm_write, int_field, json_body, markdown_page, write_json_atomic

bp = Blueprint('table', __name__)

levels_data = floor_levels()
creatures = load_creatures()

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


def session_view(state):
    return {**state, 'roll_at': JAR_ROLL_AT,
            'floors': {n: levels_data[n]['name'] for n in sorted(levels_data)}}


@bp.route('/api/session', methods=['GET'])
def get_session():
    return jsonify(session_view(load_session()))


@bp.route('/api/session', methods=['POST'])
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


@bp.route('/api/encounter', methods=['POST'])
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


@bp.route('/api/generate-npc', methods=['GET'])
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
        current_app.logger.exception('NPC generation failed')
        return jsonify({'error': f'Could not generate an NPC: {e}'}), 500

# The documents the GM page can open, by id. Nothing outside this list is served.
GM_DOCS = {
    'quick-reference': 'gm/DUNGEON_TURN_V2_QUICK_REFERENCE.md',
    'exploration-guide': 'docs/DUNGEON_EXPLORATION_GUIDE.md',
}


@bp.route('/api/gm-doc/<doc_id>', methods=['GET'])
def get_gm_doc(doc_id):
    rel = GM_DOCS.get(doc_id)
    if not rel:
        return jsonify({'error': 'Document not found'}), 404
    title, html = markdown_page(os.path.join(PROJECT_ROOT, rel))
    return jsonify({'title': title or doc_id.replace('-', ' ').title(), 'html': html})

@bp.route('/api/generate-hazard', methods=['POST'])
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
        current_app.logger.exception('hazard generation failed')
        return jsonify({'error': f'Could not generate a hazard: {e}'}), 500
