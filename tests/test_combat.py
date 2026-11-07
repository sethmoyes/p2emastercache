"""The combat tracker: fair dice, initiative order, groups and colours, HP,
conditions, turns, the web routes, and the room and condition data."""
import json
import re
import secrets
from collections import Counter

import pytest

from avtools import aon, combat
from avtools.data import conditions, room_encounters

MORLOCK = {
    'key': '/Monsters.aspx?ID=731', 'name': 'Morlock', 'level': 2, 'hp': 38, 'ac': 17,
    'saves': {'fort': 7, 'ref': 11, 'will': 9}, 'perception': 7, 'skills': {'stealth': 9, 'athletics': 8},
    'strikes': [{'kind': 'melee', 'name': 'club', 'bonus': 9, 'agile': False, 'damage': '1d6+4 bludgeoning', 'traits': ''},
                {'kind': 'melee', 'name': 'jaws', 'bonus': 9, 'agile': True, 'damage': '1d4+4 piercing', 'traits': 'Agile'},
                {'kind': 'ranged', 'name': 'club', 'bonus': 8, 'agile': False, 'damage': '1d6+4 bludgeoning', 'traits': ''}],
    'spells': [{'name': 'Primal Innate Spells', 'dc': 17, 'attack': 9}],
    'immunities': [], 'resistances': {}, 'weaknesses': {}, 'traits': ['Humanoid'], 'statblock': '**AC** 17',
    'url': 'https://2e.aonprd.com/Monsters.aspx?ID=731', 'source': 'aon',
}
OGRE = {**MORLOCK, 'key': '/Monsters.aspx?ID=1', 'name': 'Ogre', 'level': 3, 'hp': 50, 'perception': 5}
STATS = {MORLOCK['key']: MORLOCK, OGRE['key']: OGRE}
HEROES = [{'id': 'h00000001', 'name': 'Ezren', 'active': True}, {'id': 'h00000002', 'name': 'Merisiel', 'active': True},
          {'id': 'h00000003', 'name': 'Benched', 'active': False}]


def lookup(key):
    return json.loads(json.dumps(STATS[key])) if key in STATS else None


def run(state, *ops):
    for op in ops:
        state = combat.apply(state, op, heroes=HEROES, lookup=lookup)
    return state


def fresh(*ops):
    return run(combat.new_state(), {'op': 'new'}, *ops)


def monsters(state):
    return [s for s in state['slots'] if s['side'] == 'monster']


# --------------------------------------------------------------------- dice

def test_d20_maps_every_draw_to_its_own_face(monkeypatch):
    """randbelow(20) gives 0-19 with equal odds; each must land on a different face."""
    draws = iter(range(20))
    monkeypatch.setattr(secrets, 'randbelow', lambda n: (n == 20 or pytest.fail(f'randbelow({n})')) and next(draws))
    assert sorted(combat.d20() for _ in range(20)) == list(range(1, 21))


def test_d20_is_flat_like_a_real_die():
    rolls = Counter(combat.d20() for _ in range(200_000))
    assert set(rolls) == set(range(1, 21))
    expected = 200_000 / 20
    chi_square = sum((n - expected) ** 2 / expected for n in rolls.values())
    assert chi_square < 63   # 19 degrees of freedom: a fair die fails this about once in a million runs


@pytest.mark.parametrize('text,low,high', [('1d3+1', 2, 4), ('2d6', 2, 12), ('4', 4, 4), ('d4-1', 0, 3)])
def test_dice_expressions(text, low, high):
    for _ in range(200):
        total, _ = combat.roll_expression(text)
        assert low <= total <= high


def test_bad_dice_expressions():
    assert combat.roll_expression('lots') is None
    assert combat.roll_expression('100d6') is None


# --------------------------------------------------------------- initiative

def test_new_fight_seats_the_active_heroes():
    state = fresh()
    assert [s['name'] for s in state['slots']] == ['Ezren', 'Merisiel']


def test_ties_go_to_the_monsters():
    state = fresh({'op': 'add', 'creatures': [{'key': MORLOCK['key'], 'count': 1}]})
    hero, monster = state['slots'][0], monsters(state)[0]
    state = run(state, {'op': 'init', 'slot': hero['id'], 'value': 15}, {'op': 'init', 'slot': monster['id'], 'value': 15},
                {'op': 'init', 'slot': state['slots'][1]['id'], 'value': 20})
    assert [s['name'] for s in state['slots']] == ['Merisiel', 'Morlock', 'Ezren']


def test_monster_roll_is_d20_plus_perception_or_stealth(monkeypatch):
    monkeypatch.setattr(combat, 'd20', lambda: 12)
    state = fresh({'op': 'add', 'creatures': [{'key': MORLOCK['key'], 'count': 1}]}, {'op': 'roll'})
    slot = monsters(state)[0]
    assert (slot['d20'], slot['mod'], slot['init']) == (12, 7, 19)
    state = run(state, {'op': 'skill', 'slot': slot['id'], 'skill': 'stealth', 'adjust': -2})
    assert monsters(state)[0]['init'] == 12 + 9 - 2


def test_start_needs_everyone_to_have_initiative():
    state = fresh()
    with pytest.raises(combat.CombatError, match='Ezren'):
        run(state, {'op': 'start'})


# ------------------------------------------------------- groups and colours

def test_a_group_shares_one_turn_and_wears_different_colours():
    state = fresh({'op': 'add', 'creatures': [{'key': MORLOCK['key'], 'count': 5, 'grouped': True}]})
    (slot,) = monsters(state)
    assert [(m['color'], m['num']) for m in slot['members']] == [
        ('white', 1), ('blue', 1), ('green', 1), ('red', 1), ('white', 2)]
    labels = [m['label'] for m in combat.view(state)['slots'][-1]['members']]
    assert labels[0] == 'Morlock (white)' and labels[-1] == 'Morlock (white 2)'


def test_split_then_group_again():
    state = fresh({'op': 'add', 'creatures': [{'key': MORLOCK['key'], 'count': 3, 'grouped': True}]})
    state = run(state, {'op': 'split', 'slot': monsters(state)[0]['id']})
    assert [len(s['members']) for s in monsters(state)] == [1, 1, 1]
    state = run(state, {'op': 'group', 'slot': monsters(state)[1]['id']})
    assert [len(s['members']) for s in monsters(state)] == [3]


def test_colour_change_renumbers():
    state = fresh({'op': 'add', 'creatures': [{'key': MORLOCK['key'], 'count': 2, 'grouped': True}]})
    second = monsters(state)[0]['members'][1]
    state = run(state, {'op': 'color', 'member': second['id'], 'color': 'white'})
    assert [(m['color'], m['num']) for m in monsters(state)[0]['members']] == [('white', 1), ('white', 2)]


def test_dice_counts_are_rolled():
    state = fresh({'op': 'add', 'creatures': [{'key': MORLOCK['key'], 'count': '1d3+1', 'grouped': True}]})
    assert 2 <= len(monsters(state)[0]['members']) <= 4
    assert 'rolled' in state['last_turn'][0]


# ------------------------------------------------------------------------ HP

def test_damage_and_healing_stay_between_zero_and_max():
    state = fresh({'op': 'add', 'creatures': [{'key': MORLOCK['key'], 'count': 1}]})
    member = monsters(state)[0]['members'][0]['id']
    state = run(state, {'op': 'hp', 'member': member, 'delta': -27})
    assert monsters(state)[0]['members'][0]['hp'] == 11
    state = run(state, {'op': 'hp', 'member': member, 'delta': -50})
    assert monsters(state)[0]['members'][0]['hp'] == 0
    state = run(state, {'op': 'hp', 'member': member, 'delta': 100})
    assert monsters(state)[0]['members'][0]['hp'] == 38


def test_undo_takes_back_the_last_change():
    state = fresh({'op': 'add', 'creatures': [{'key': MORLOCK['key'], 'count': 1}]})
    member = monsters(state)[0]['members'][0]['id']
    state = run(state, {'op': 'hp', 'member': member, 'delta': -10}, {'op': 'undo'})
    assert monsters(state)[0]['members'][0]['hp'] == 38


# ---------------------------------------------------------------- conditions

def effective(state):
    slot = monsters(state)[0]
    return combat.effective(slot['members'][0], state['creatures'][slot['key']])


def with_conditions(*conds):
    state = fresh({'op': 'add', 'creatures': [{'key': MORLOCK['key'], 'count': 1}]})
    member = monsters(state)[0]['members'][0]['id']
    return run(state, *[{'op': 'condition', 'members': [member], **c} for c in conds])


def test_only_the_worst_status_penalty_counts_but_circumstance_stacks():
    eff = effective(with_conditions({'key': 'frightened', 'value': 2}, {'key': 'sickened', 'value': 1},
                                    {'key': 'off-guard'}))
    assert eff['ac'] == 17 - 2 - 2
    assert eff['saves'] == {'fort': 5, 'ref': 9, 'will': 7}
    assert eff['perception'] == 5


def test_prone_means_off_guard_and_worse_attacks():
    eff = effective(with_conditions({'key': 'prone'}))
    assert eff['ac'] == 15
    jaws = eff['strikes'][1]
    assert jaws['bonus'] == 7 and jaws['map'] == [7, 3, -1]   # agile: -4 and -8
    assert eff['strikes'][0]['map'] == [7, 2, -3]


def test_clumsy_hits_ac_reflex_and_ranged_only():
    eff = effective(with_conditions({'key': 'clumsy', 'value': 1}))
    assert (eff['ac'], eff['saves']['ref'], eff['saves']['fort']) == (16, 10, 7)
    assert [s['bonus'] for s in eff['strikes']] == [9, 9, 7]


def test_stupefied_lowers_spells():
    eff = effective(with_conditions({'key': 'stupefied', 'value': 2}))
    assert eff['spells'][0]['dc'] == 15 and eff['spells'][0]['attack'] == 7


def test_drained_takes_hp_and_max_hp():
    state = with_conditions({'key': 'drained', 'value': 1})
    member = monsters(state)[0]['members'][0]
    assert effective(state)['max_hp'] == 36 and member['hp'] == 36


def test_value_zero_removes_a_condition():
    state = with_conditions({'key': 'frightened', 'value': 2})
    member = monsters(state)[0]['members'][0]['id']
    state = run(state, {'op': 'condition', 'members': [member], 'key': 'frightened', 'value': 0})
    assert monsters(state)[0]['members'][0]['conditions'] == []


def test_unknown_condition_is_refused():
    with pytest.raises(combat.CombatError):
        with_conditions({'key': 'sparkly'})


# --------------------------------------------------------------------- turns

def ready(*conds, count=1):
    state = with_conditions(*conds)
    for slot in state['slots']:
        if slot['init'] is None:
            state = run(state, {'op': 'init', 'slot': slot['id'], 'value': 30 if slot['side'] == 'monster' else 10})
    return run(state, {'op': 'start'})


def test_turns_go_round_and_count_rounds():
    state = ready()
    order = [s['id'] for s in state['slots']]
    assert state['round'] == 1 and state['turn'] == order[0]
    state = run(state, {'op': 'next'}, {'op': 'next'}, {'op': 'next'})
    assert state['round'] == 2 and state['turn'] == order[0]


def test_frightened_drops_at_the_end_of_its_turn():
    state = run(ready({'key': 'frightened', 'value': 2}), {'op': 'next'})
    assert monsters(state)[0]['members'][0]['conditions'][0]['value'] == 1
    assert any('frightened 1' in note for note in state['last_turn'])


def test_timed_conditions_run_out():
    state = run(ready({'key': 'slowed', 'value': 1, 'rounds': 1}), {'op': 'next'})
    assert monsters(state)[0]['members'][0]['conditions'] == []


def test_persistent_damage_hits_then_flat_check(monkeypatch):
    monkeypatch.setattr(combat, 'd20', lambda: 15)
    state = run(ready({'key': 'persistent', 'detail': '5 fire'}), {'op': 'next'})
    member = monsters(state)[0]['members'][0]
    assert member['hp'] == 33 and member['conditions'] == []


def test_defeated_monsters_lose_their_turn():
    state = ready()
    member = monsters(state)[0]['members'][0]['id']
    state = run(state, {'op': 'hp', 'member': member, 'delta': -100}, {'op': 'next'}, {'op': 'next'}, {'op': 'next'})
    assert state['turn'] != monsters(state)[0]['id']


def test_late_arrivals_slot_in_without_reshuffling():
    state = ready()
    before = [s['id'] for s in state['slots']]
    state = run(state, {'op': 'add', 'creatures': [{'key': OGRE['key'], 'count': 1}], 'roll': True})
    assert [s['id'] for s in state['slots'] if s['id'] in before] == before


# -------------------------------------------------------- AoN stat blocks

AON_MARKDOWN = '''<title level="1">[Morlock](/Monsters.aspx?ID=731)</title>
Lore that isn't the stat block.
<title level="2" right="Creature 2">[Morlock](/Monsters.aspx?ID=731)</title>
<traits><trait label="Humanoid" /></traits>
<column gap="tiny">
**Perception** +7; [darkvision](/MonsterAbilities.aspx?ID=12)
</column>
**Melee**
<actions string="Single Action" />
jaws +9 ([Agile](/Traits.aspx?ID=170)),
**Damage** 1d4+4 piercing

**Primal Innate Spells** DC 17, attack +9
<aside>A sidebar</aside>'''


def test_statblock_drops_lore_and_layout_tags():
    md = aon.statblock_markdown(AON_MARKDOWN)
    assert 'Lore' not in md and 'sidebar' not in md and '<' not in md
    assert '[1] jaws +9' in md
    assert '(https://2e.aonprd.com/MonsterAbilities.aspx?ID=12)' in md


def test_strikes_and_spells_parse():
    assert aon.parse_strikes(AON_MARKDOWN) == [{'kind': 'melee', 'name': 'jaws', 'bonus': 9, 'traits': 'Agile',
                                               'agile': True, 'damage': '1d4+4 piercing'}]
    assert aon.parse_spells(AON_MARKDOWN) == [{'name': 'Primal Innate Spells', 'dc': 17, 'attack': 9}]


def test_resistance_all_is_not_spelled_out():
    assert aon._amounts({'all': 10, 'fire': 10, 'cold': 15}) == {'all': 10, 'cold': 15}


def test_offline_lookup_falls_back_to_creatures_json():
    stats = aon.creature('/Monsters.aspx?ID=731')     # the network is blocked in tests
    assert stats['name'] == 'Morlock' and stats['source'] == 'local'
    assert aon.creature('/etc/passwd') is None


# ----------------------------------------------------------------- web app

@pytest.fixture
def fake_aon(monkeypatch):
    from avtools.web import combat as web
    def fake(key):
        local = next((c for c in aon.creatures() if c['url'] == key), None)
        return lookup(key) or (aon.from_local(local) if local else None)
    monkeypatch.setattr(web.aon, 'creature', fake)


@pytest.mark.parametrize('url', ['/gm/combat', '/api/combat', '/api/heroes', '/api/rooms', '/api/conditions',
                                 '/api/creatures/search?q=A10', '/api/creatures/search?q=morlock'])
def test_combat_pages_load(client, url):
    assert client.get(url).status_code == 200


def test_combat_writes_need_the_gm_password(client, monkeypatch):
    from avtools.web import core
    monkeypatch.setattr(core, 'GM_PASSWORD', 'sekrit')
    assert client.post('/api/combat', json={'op': 'new'}).status_code == 401
    assert client.post('/api/heroes', json={'heroes': []}).status_code == 401


def test_party_and_fight_survive_on_disk(client, fake_aon):
    heroes = client.post('/api/heroes', json={'heroes': [{'name': 'Ezren'}, {'name': 'Kyra', 'player': 'Sam'}]}).get_json()
    assert [h['name'] for h in heroes['heroes']] == ['Ezren', 'Kyra']
    client.post('/api/combat', json={'op': 'new'})
    fight = client.post('/api/combat', json={'op': 'add_room', 'code': 'a4'}).get_json()
    assert [s['name'] for s in fight['slots']] == ['Ezren', 'Kyra', 'Mitflit', 'Giant Maggot']
    assert len(fight['slots'][2]['members']) == 3
    assert 'statblock' not in json.dumps(fight['creatures'])
    assert client.get('/api/combat').get_json()['version'] == fight['version']


def test_bad_changes_are_a_400(client, fake_aon):
    client.post('/api/combat', json={'op': 'new'})
    for body in [{'op': 'nonsense'}, {'op': 'hp', 'member': 'm999', 'delta': -3}, {'op': 'add_room', 'code': 'Z9'},
                 {'op': 'add', 'creatures': [{'key': '/etc/passwd', 'count': 1}]}]:
        assert client.post('/api/combat', json=body).status_code == 400, body


def test_dungeon_turn_events_become_combatants():
    from avtools.web.combat import event_creatures
    template = {'creatures': '1d3+1 Morlocks (Level 2, HP 38, AC 17 each) and 1 Grothlut',
                'creature_reference': {'Morlock': {'aon_url': 'https://2e.aonprd.com/Monsters.aspx?ID=731'},
                                       'Grothlut': {'aon_url': 'https://2e.aonprd.com/Monsters.aspx?ID=2997'}}}
    assert event_creatures(template) == [{'key': '/Monsters.aspx?ID=731', 'count': '1d3+1'},
                                         {'key': '/Monsters.aspx?ID=2997', 'count': '1'}]
    combat_event = {'creature_summary': '2x Morlock (Level 2, HP 38, AC 17), 1x Grothlut (Level 3, HP 50, AC 19)',
                    'creature_reference': template['creature_reference']}
    assert event_creatures(combat_event) == [{'key': '/Monsters.aspx?ID=731', 'count': 2},
                                             {'key': '/Monsters.aspx?ID=2997', 'count': 1}]


def test_ecology_combat_events_carry_a_roster(client):
    for total in range(40, 46):
        event = client.post('/api/encounter', json={'sum': total, 'allow_no_event': False, 'record': False}).get_json()
        if event['category'] == 'COMBAT' and 'roster' in event:
            assert sum(r['count'] for r in event['roster']) == event['num_creatures']
            return


# ---------------------------------------------------------------------- data

def test_room_index_is_sound():
    rooms = room_encounters()
    assert len(rooms) > 150
    for code, room in rooms.items():
        assert re.fullmatch(r'[A-J]\d{1,2}[a-z]?', code)
        assert 'ABCDEFGHIJ'.index(code[0]) + 1 == room['floor'], code
        for c in room['creatures']:
            assert aon.valid_key(c['key']), (code, c)
            assert 1 <= c['count'] <= combat.MAX_COUNT
        assert room['creatures'] or room.get('unresolved'), code
    assert json.dumps(rooms).isascii()


def test_conditions_are_sound():
    table = conditions()
    for key, cond in table.items():
        assert cond['url'].startswith('/Conditions.aspx?ID=')
        for implied in cond.get('implies', []):
            assert implied in table, (key, implied)
        for p in cond.get('penalties', []):
            assert p['type'] in ('status', 'circumstance')
            for stat in p['stats']:
                assert stat in combat.ALL_STATS or stat in combat.STAT_GROUPS, (key, stat)
