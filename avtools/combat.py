"""
The GM's combat tracker: who's in the fight, the initiative order, monster HP
and conditions.

The state is a plain dict (saved by the web app as DATA_DIR/state/combat.json)
and every change goes through apply(state, op), so the rules live here and the
tests can drive them without a browser. Heroes only get an initiative slot:
the players track their own HP.

Initiative order follows the rules: highest result first, and on a tie the
monsters go before the heroes. The GM can still nudge any slot up or down
(a Delay, or a tie the table settled differently).
"""

import copy
import re
import secrets

from avtools.data import conditions as condition_table

COLORS = ('white', 'blue', 'green', 'red')
INIT_SKILLS = ('perception', 'stealth')
MAX_SLOTS = 40
MAX_COUNT = 30          # creatures added at once
MAX_HP = 2000
UNDO_KEEP = 30
CONDITION_MAX = 9

ALL_STATS = ('ac', 'fort', 'ref', 'will', 'perception', 'melee', 'ranged', 'spell_dc', 'spell_attack', 'skills')
STAT_GROUPS = {'all': ALL_STATS, 'saves': ('fort', 'ref', 'will')}


class CombatError(ValueError):
    """A change that doesn't fit the fight (unknown id, bad value)."""


# -------------------------------------------------------------------- dice

def d20():
    """One d20, every face exactly 1 in 20, like a real die.

    secrets.randbelow draws from the OS's cryptographic generator and uses
    rejection sampling, so there's no modulo bias and no seedable pattern.
    """
    return secrets.randbelow(20) + 1


def roll_die(sides):
    return secrets.randbelow(sides) + 1


DICE = re.compile(r'^\s*(\d*)\s*d\s*(\d+)\s*(?:([+-])\s*(\d+))?\s*$', re.I)


def roll_expression(text):
    """Roll "1d3+1", "2d6" or a plain number; returns (total, "2+1") or None."""
    text = str(text).strip()
    if text.isdigit():
        return int(text), text
    m = DICE.match(text)
    if not m:
        return None
    count, sides = int(m.group(1) or 1), int(m.group(2))
    if not (1 <= count <= 20 and 2 <= sides <= 100):
        return None
    faces = [roll_die(sides) for _ in range(count)]
    bonus = int(m.group(4) or 0) * (-1 if m.group(3) == '-' else 1)
    detail = '+'.join(map(str, faces)) + (f'{bonus:+d}' if bonus else '')
    return sum(faces) + bonus, detail


# ------------------------------------------------------------------- state

def new_state():
    return {'version': 0, 'round': 0, 'turn': None, 'next_id': 1, 'slots': [], 'creatures': {},
            'last_turn': [], 'undo': []}


def _id(state, prefix):
    state['next_id'] += 1
    return f'{prefix}{state["next_id"]}'


def _slot(state, slot_id):
    for slot in state['slots']:
        if slot['id'] == slot_id:
            return slot
    raise CombatError(f'No such initiative slot: {slot_id}')


def _member(state, member_id):
    for slot in state['slots']:
        for member in slot.get('members', []):
            if member['id'] == member_id:
                return slot, member
    raise CombatError(f'No such creature: {member_id}')


def _int(value, low, high, name):
    try:
        value = int(value)
    except (TypeError, ValueError):
        raise CombatError(f'{name} must be a whole number')
    if not low <= value <= high:
        raise CombatError(f'{name} must be between {low} and {high}')
    return value


def hero_slot(state, hero):
    return {'id': _id(state, 's'), 'side': 'hero', 'hero_id': hero['id'], 'name': hero['name'],
            'init': None, 'd20': None, 'mod': None}


# ----------------------------------------------------------- initiative

def initiative_mod(slot, stats):
    """The monster's initiative modifier: Perception, or a skill (Stealth when it
    was sneaking), plus any adjustment the GM set (e.g. -2 from the book)."""
    skill = slot.get('skill', 'perception')
    base = stats.get('perception') if skill == 'perception' else stats.get('skills', {}).get(skill)
    return (base if base is not None else stats.get('perception') or 0) + slot.get('adjust', 0)


def order_key(slot):
    """Highest first; on a tie monsters act before heroes, then the higher modifier."""
    init = slot['init']
    return (init is None, -(init or 0), slot['side'] != 'monster', -(slot.get('mod') or 0))


def sort_slots(state):
    state['slots'].sort(key=order_key)   # stable: equal slots keep the GM's order


def place(state, slot):
    """Move one slot to where its initiative belongs without reshuffling the rest
    (for someone joining a fight already under way)."""
    state['slots'].remove(slot)
    key = order_key(slot)
    index = next((i for i, other in enumerate(state['slots']) if order_key(other) > key), len(state['slots']))
    state['slots'].insert(index, slot)


def _settle(state, slots):
    if state['round'] == 0:
        sort_slots(state)
    else:
        for slot in slots:
            place(state, slot)


def roll_initiative(state, slot):
    stats = state['creatures'][slot['key']]
    slot['d20'] = d20()
    slot['mod'] = initiative_mod(slot, stats)
    slot['init'] = slot['d20'] + slot['mod']


# -------------------------------------------------------------- monsters

def _pick_color(state, key):
    """The colour fewest of this creature already wear, and its number within that colour."""
    used = {c: 0 for c in COLORS}
    taken = {c: set() for c in COLORS}
    for slot in state['slots']:
        for member in slot.get('members', []):
            if slot.get('key') == key:
                used[member['color']] += 1
                taken[member['color']].add(member['num'])
    color = min(COLORS, key=lambda c: used[c])
    num = next(n for n in range(1, MAX_COUNT * 2) if n not in taken[color])
    return color, num


def new_member(state, key, stats):
    color, num = _pick_color(state, key)
    return {'id': _id(state, 'm'), 'color': color, 'num': num, 'hp': stats['hp'], 'max_hp': stats['hp'],
            'conditions': []}


def add_creatures(state, key, stats, count, grouped):
    """count of one creature: one shared initiative slot, or one slot each."""
    state['creatures'][key] = stats
    groups = [count] if grouped else [1] * count
    if len(state['slots']) + len(groups) > MAX_SLOTS:
        raise CombatError(f'That would be more than {MAX_SLOTS} initiative slots')
    added = []
    for size in groups:
        slot = {'id': _id(state, 's'), 'side': 'monster', 'key': key, 'name': stats['name'],
                'init': None, 'd20': None, 'mod': None, 'skill': 'perception', 'adjust': 0, 'members': []}
        state['slots'].append(slot)   # appended first so colours count earlier members
        for _ in range(size):
            slot['members'].append(new_member(state, key, stats))
        added.append(slot)
    return added


def defeated(slot):
    return slot['side'] == 'monster' and all(m['hp'] <= 0 for m in slot['members'])


# ------------------------------------------------------------- conditions

def active_conditions(member):
    """The member's conditions plus the ones they imply (prone -> off-guard), by key."""
    table = condition_table()
    active = {}
    pending = [(c['key'], c.get('value')) for c in member['conditions']]
    while pending:
        key, value = pending.pop()
        if key not in table:
            continue
        if key in active and (active[key] or 0) >= (value or 0):
            continue
        active[key] = value
        pending += [(k, None) for k in table[key].get('implies', [])]
    return active


def penalties(member):
    """{stat: (total penalty, "frightened 2, off-guard")}; the worst status and
    the worst circumstance penalty each apply, and they add up."""
    table = condition_table()
    worst = {}
    for key, value in active_conditions(member).items():
        for p in table[key].get('penalties', []):
            amount = (value or 0) if p['amount'] == 'value' else p['amount']
            if amount <= 0:
                continue
            label = f'{key} {value}' if value else key
            for group in p['stats']:
                for stat in STAT_GROUPS.get(group, (group,)):
                    current = worst.setdefault(stat, {}).get(p['type'])
                    if current is None or amount > current[0]:
                        worst[stat][p['type']] = (amount, label)
    return {stat: (sum(a for a, _ in kinds.values()), ', '.join(l for _, l in kinds.values()))
            for stat, kinds in worst.items()}


def drained_hp(member, stats):
    drained = active_conditions(member).get('drained') or 0
    return max(1, stats.get('level', 1)) * drained


def effective(member, stats):
    """A member's numbers after its conditions."""
    pen = penalties(member)
    minus = lambda stat: pen.get(stat, (0, ''))[0]
    saves = stats.get('saves') or {}
    out = {
        'ac': stats['ac'] - minus('ac') if stats.get('ac') is not None else None,
        'saves': {s: (v - minus(s) if v is not None else None) for s, v in saves.items()},
        'perception': stats['perception'] - minus('perception') if stats.get('perception') is not None else None,
        'max_hp': max(1, member['max_hp'] - drained_hp(member, stats)),
        'strikes': [],
        'spells': [{**s, 'dc': s['dc'] - minus('spell_dc'),
                    'attack': s['attack'] - minus('spell_attack') if s.get('attack') is not None else None}
                    for s in stats.get('spells', [])],
        'skills': {k: v - minus('skills') for k, v in stats.get('skills', {}).items()},
        'penalties': {stat: {'amount': amount, 'from': why} for stat, (amount, why) in pen.items()},
    }
    for strike in stats.get('strikes', []):
        bonus = strike['bonus'] - minus(strike['kind'])
        step = 4 if strike.get('agile') else 5
        out['strikes'].append({**strike, 'bonus': bonus, 'map': [bonus, bonus - step, bonus - 2 * step]})
    return out


def set_condition(state, member, stats, key, value=None, rounds=None, detail=''):
    table = condition_table()
    if key not in table:
        raise CombatError(f'Unknown condition: {key}')
    info = table[key]
    value = _int(value if value is not None else 1, 0, CONDITION_MAX, 'value') if info.get('valued') else None
    rounds = _int(rounds, 1, 100, 'rounds') if rounds not in (None, '', 0) else None
    detail = str(detail or '')[:40].strip() if info.get('detail') else ''
    before = drained_hp(member, stats)
    member['conditions'] = [c for c in member['conditions'] if c['key'] != key]
    if not info.get('valued') or value:
        member['conditions'].append({'key': key, 'value': value, 'rounds': rounds, 'detail': detail})
    # Drained takes HP as it rises (level x the increase); recovering doesn't give it back
    gained = drained_hp(member, stats) - before
    if gained > 0:
        member['hp'] = max(0, member['hp'] - gained)
    member['hp'] = min(member['hp'], effective(member, stats)['max_hp'])


def end_of_turn(state, slot):
    """What happens to the creatures in a slot when their turn ends: frightened
    drops, persistent damage hits and gets its flat check, timed conditions run
    down. Returns notes for the GM."""
    notes = []
    if slot['side'] != 'monster':
        return notes
    table = condition_table()
    stats = state['creatures'][slot['key']]
    for member in slot['members']:
        if member['hp'] <= 0:
            continue
        who = label(slot, member)
        kept = []
        for cond in member['conditions']:
            info = table.get(cond['key'], {})
            if info.get('end_of_turn') == 'decrease':
                cond['value'] = (cond['value'] or 0) - 1
                notes.append(f'{who}: {cond["key"]} {cond["value"]}' if cond['value'] else f'{who}: no longer {cond["key"]}')
                if cond['value'] <= 0:
                    continue
            if info.get('end_of_turn') == 'persistent':
                amount, _, kind = cond['detail'].partition(' ')
                rolled = roll_expression(amount)
                if rolled:
                    member['hp'] = max(0, member['hp'] - rolled[0])
                    notes.append(f'{who}: {rolled[0]} persistent {kind or "damage"} ({rolled[1]}), HP {member["hp"]}')
                else:
                    notes.append(f'{who}: persistent {cond["detail"] or "damage"} (apply it by hand)')
                check = d20()
                if check >= 15:
                    notes.append(f'{who}: flat check {check} vs DC 15, persistent {kind or "damage"} ends')
                    continue
                notes.append(f'{who}: flat check {check} vs DC 15, it continues')
            if cond.get('rounds'):
                cond['rounds'] -= 1
                if cond['rounds'] <= 0:
                    notes.append(f'{who}: {cond["key"]} runs out')
                    continue
            kept.append(cond)
        member['conditions'] = kept
        member['hp'] = min(member['hp'], effective(member, stats)['max_hp'])
    return notes


def label(slot, member):
    """'Morlock (blue 2)'; the number only when the colour repeats."""
    return f'{slot["name"]} ({member["color"]} {member["num"]})' if member['num'] > 1 else f'{slot["name"]} ({member["color"]})'


# ------------------------------------------------------------------ turns

def _acting(state):
    return [s for s in state['slots'] if not defeated(s)]


def start(state):
    if not state['slots']:
        raise CombatError('Add heroes and monsters first')
    missing = [s['name'] for s in state['slots'] if s['init'] is None]
    if missing:
        raise CombatError('No initiative yet for: ' + ', '.join(missing))
    sort_slots(state)
    state['round'] = 1
    state['turn'] = _acting(state)[0]['id'] if _acting(state) else None
    state['last_turn'] = []


def _advance(state, index, skip=None):
    """Hand the turn to the next slot after index that can still act; passing
    the bottom of the order starts a new round."""
    order = state['slots']
    for step in range(1, len(order) + 1):
        position = index + step
        candidate = order[position % len(order)]
        if candidate is not skip and not defeated(candidate):
            if position >= len(order):
                state['round'] += 1
            state['turn'] = candidate['id']
            return
    state['turn'] = None


def next_turn(state):
    if state['round'] == 0:
        start(state)
        return
    current = next((s for s in state['slots'] if s['id'] == state['turn']), None)
    state['last_turn'] = end_of_turn(state, current) if current else []
    _advance(state, state['slots'].index(current) if current else -1)


# ------------------------------------------------------------------- apply

def _snapshot(state):
    return copy.deepcopy({k: v for k, v in state.items() if k not in ('undo', 'creatures')})


def apply(state, op, heroes=(), lookup=None):
    """Make one change. op is {"op": name, ...}; heroes is the saved party;
    lookup(key) returns a creature's stats (the AoN lookup in production).
    Returns the new state; raises CombatError for a change that doesn't fit."""
    state = copy.deepcopy(state)
    name = op.get('op')
    if name == 'undo':
        if not state['undo']:
            raise CombatError('Nothing to undo')
        previous = state['undo'].pop()
        state.update(previous)
        state['version'] += 1
        return state

    state['undo'] = (state['undo'] + [_snapshot(state)])[-UNDO_KEEP:]
    handler = OPS.get(name)
    if not handler:
        raise CombatError(f'Unknown change: {name}')
    handler(state, op, heroes, lookup)
    state['version'] += 1
    return state


def _new(state, op, heroes, lookup):
    keep_undo = state['undo']
    state.clear()
    state.update(new_state())
    state['undo'] = keep_undo
    for hero in heroes:
        if hero.get('active', True):
            state['slots'].append(hero_slot(state, hero))


def _add_hero(state, op, heroes, lookup):
    hero = next((h for h in heroes if h['id'] == op.get('hero')), None)
    if not hero:
        raise CombatError('No such hero')
    if any(s.get('hero_id') == hero['id'] for s in state['slots']):
        raise CombatError(f'{hero["name"]} is already in the fight')
    state['slots'].append(hero_slot(state, hero))


def _add(state, op, heroes, lookup):
    entries = op.get('creatures')
    if not isinstance(entries, list) or not entries:
        raise CombatError('Nothing to add')
    added, rolled = [], []
    for entry in entries[:20]:
        if not isinstance(entry, dict):
            raise CombatError('Each creature needs a key and a count')
        stats = lookup(entry.get('key')) if lookup else None
        if not stats:
            raise CombatError(f'Creature not found: {entry.get("key")}')
        count = entry.get('count', 1)
        if isinstance(count, str) and not count.strip().isdigit():
            result = roll_expression(count)
            if not result:
                raise CombatError(f'Count must be a number or dice like 1d3+1: {count}')
            rolled.append(f'{count} {stats["name"]}: rolled {result[0]} ({result[1]})')
            count = result[0]
        count = _int(count, 1, MAX_COUNT, 'count')
        added += add_creatures(state, stats['key'], stats, count, bool(entry.get('grouped', count >= 3)))
    if op.get('roll'):
        for slot in added:
            roll_initiative(state, slot)
        _settle(state, added)
    state['last_turn'] = rolled


def _remove(state, op, heroes, lookup):
    slot = _slot(state, op.get('slot'))
    if state['turn'] == slot['id']:
        _advance(state, state['slots'].index(slot), skip=slot)
    state['slots'].remove(slot)


def _remove_member(state, op, heroes, lookup):
    slot, member = _member(state, op.get('member'))
    slot['members'].remove(member)
    if not slot['members']:
        _remove(state, {'slot': slot['id']}, heroes, lookup)


def _init(state, op, heroes, lookup):
    slot = _slot(state, op.get('slot'))
    value = op.get('value')
    if value in (None, ''):
        slot['init'] = slot['d20'] = slot['mod'] = None
        return
    slot['init'] = _int(value, -20, 80, 'initiative')
    slot['d20'] = slot['mod'] = None
    _settle(state, [slot])


def _roll(state, op, heroes, lookup):
    wanted = op.get('slots')
    slots = [s for s in state['slots'] if s['side'] == 'monster'
             and (s['id'] in wanted if isinstance(wanted, list) else s['init'] is None or op.get('all'))]
    if not slots:
        raise CombatError('No monsters to roll for')
    for slot in slots:
        roll_initiative(state, slot)
    _settle(state, slots)


def _skill(state, op, heroes, lookup):
    slot = _slot(state, op.get('slot'))
    if slot['side'] != 'monster':
        raise CombatError('Heroes give you their own initiative')
    skill = op.get('skill', slot['skill'])
    stats = state['creatures'][slot['key']]
    if skill not in INIT_SKILLS and skill not in stats.get('skills', {}):
        raise CombatError(f'{stats["name"]} has no {skill} modifier')
    slot['skill'] = skill
    slot['adjust'] = _int(op.get('adjust', slot['adjust']), -10, 10, 'adjust')
    if slot['d20'] is not None:
        slot['mod'] = initiative_mod(slot, stats)
        slot['init'] = slot['d20'] + slot['mod']
        _settle(state, [slot])


def _group(state, op, heroes, lookup):
    """Fold every other slot of this creature into this one (one shared turn)."""
    slot = _slot(state, op.get('slot'))
    if slot['side'] != 'monster':
        raise CombatError('Only monsters can be grouped')
    for other in [s for s in state['slots'] if s is not slot and s.get('key') == slot['key']]:
        slot['members'] += other['members']
        if state['turn'] == other['id']:
            state['turn'] = slot['id']
        state['slots'].remove(other)


def _split(state, op, heroes, lookup):
    """Give every creature in a group its own slot, keeping the group's roll."""
    slot = _slot(state, op.get('slot'))
    if slot['side'] != 'monster' or len(slot['members']) < 2:
        raise CombatError('Nothing to split')
    index = state['slots'].index(slot)
    for offset, member in enumerate(slot['members'][1:], start=1):
        state['slots'].insert(index + offset, {**copy.deepcopy({k: v for k, v in slot.items() if k != 'members'}),
                                               'id': _id(state, 's'), 'members': [member]})
    slot['members'] = slot['members'][:1]
    if len(state['slots']) > MAX_SLOTS:
        raise CombatError(f'That would be more than {MAX_SLOTS} initiative slots')


def _move(state, op, heroes, lookup):
    slot = _slot(state, op.get('slot'))
    by = -1 if op.get('by', 1) < 0 else 1
    i = state['slots'].index(slot)
    j = max(0, min(len(state['slots']) - 1, i + by))
    state['slots'][i], state['slots'][j] = state['slots'][j], state['slots'][i]


def _sort(state, op, heroes, lookup):
    sort_slots(state)


def _start(state, op, heroes, lookup):
    start(state)


def _next(state, op, heroes, lookup):
    next_turn(state)


def _end(state, op, heroes, lookup):
    state['round'] = 0
    state['turn'] = None
    state['last_turn'] = []


def _hp(state, op, heroes, lookup):
    slot, member = _member(state, op.get('member'))
    stats = state['creatures'][slot['key']]
    top = effective(member, stats)['max_hp']
    if 'set' in op:
        member['hp'] = _int(op['set'], 0, top, 'HP')
    else:
        member['hp'] = max(0, min(top, member['hp'] + _int(op.get('delta'), -MAX_HP, MAX_HP, 'damage')))


def _max_hp(state, op, heroes, lookup):
    slot, member = _member(state, op.get('member'))
    old = member['max_hp']
    member['max_hp'] = _int(op.get('value'), 1, MAX_HP, 'max HP')
    member['hp'] = max(0, min(member['max_hp'], member['hp'] + member['max_hp'] - old))


def _color(state, op, heroes, lookup):
    slot, member = _member(state, op.get('member'))
    color = op.get('color')
    if color not in COLORS:
        raise CombatError(f'Colour must be one of {", ".join(COLORS)}')
    taken = {m['num'] for s in state['slots'] if s.get('key') == slot['key']
             for m in s['members'] if m['color'] == color and m is not member}
    member['color'] = color
    member['num'] = next(n for n in range(1, MAX_COUNT * 2) if n not in taken)


def _condition(state, op, heroes, lookup):
    members = op.get('members') or [op.get('member')]
    for member_id in members:
        slot, member = _member(state, member_id)
        set_condition(state, member, state['creatures'][slot['key']], op.get('key'),
                      op.get('value'), op.get('rounds'), op.get('detail', ''))


OPS = {
    'new': _new, 'add_hero': _add_hero, 'add': _add, 'remove': _remove, 'remove_member': _remove_member,
    'init': _init, 'roll': _roll, 'skill': _skill, 'group': _group, 'split': _split, 'move': _move,
    'sort': _sort, 'start': _start, 'next': _next, 'end': _end, 'hp': _hp, 'max_hp': _max_hp,
    'color': _color, 'condition': _condition,
}


# -------------------------------------------------------------------- view

def view(state):
    """The state as the page draws it: each monster's numbers after conditions."""
    out = {k: v for k, v in state.items() if k != 'undo'}
    out['can_undo'] = bool(state['undo'])
    out['slots'] = []
    for slot in state['slots']:
        shown = copy.deepcopy(slot)
        if slot['side'] == 'monster':
            stats = state['creatures'][slot['key']]
            shown['defeated'] = defeated(slot)
            for member in shown['members']:
                member['label'] = label(slot, member)
                member['effective'] = effective(member, stats)
        out['slots'].append(shown)
    return out
