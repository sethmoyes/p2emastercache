"""The data files agree with each other and with the rules in claude.md."""
import json
import os

import pytest

from conftest import ROOT
from avtools.validation import validate_event
from avtools.data import find_creature, floor_ecology
from avtools.merchants import MERCHANT_CONFIGS, merchant_slug, prepare_equipment


def load(name):
    with open(os.path.join(ROOT, 'etc', name), encoding='utf-8') as f:
        return json.load(f)


CREATURES = load('creatures.json')
EVENTS = load('dungeon_turn_events.json')
LIVE = [(cat, e) for cat, events in EVENTS.items() for e in events if not e.get('retired')]
REQUIRED = {
    'OPPORTUNITY': {'challenge', 'success', 'failure', 'reward'},
    'COMPLICATION': {'challenge', 'success', 'failure', 'consequence'},
    'DILEMMA': {'choice_a', 'choice_b', 'consequence'},
    'ACTIVE_THREAT': {'immediate_action', 'success', 'failure', 'threat_level'},
}
COMMON = {'title', 'description', 'skills', 'time_cost', 'gm_notes', 'floor'}


@pytest.mark.parametrize('cat,event', LIVE, ids=[e['title'] for _, e in LIVE])
def test_event_has_its_fields_and_passes_validation(cat, event):
    assert COMMON | REQUIRED[cat] <= event.keys()
    assert 0 <= event['floor'] <= 10
    ok, why = validate_event(event)
    assert ok, why


def test_events_are_ascii():
    bad = [e['title'] for _, e in LIVE if any(ord(c) > 127 for c in json.dumps(e, ensure_ascii=False))]
    assert not bad


def test_event_creature_references_match_creatures_json():
    for _, event in LIVE:
        for name, ref in (event.get('creature_reference') or {}).items():
            creature = find_creature(CREATURES, name)
            assert creature, f"{event['title']}: {name} is not in creatures.json"
            assert (ref['level'], ref['hp'], ref['ac']) == (creature['level'], creature['hp'], creature['ac']), \
                f"{event['title']}: {name} stats don't match creatures.json"
            assert ref['aon_url'].endswith(creature['url'])


@pytest.mark.parametrize('floor', range(1, 11))
def test_every_floor_has_events_of_every_category(floor):
    for cat in REQUIRED:
        assert any(e['floor'] in (0, floor) for c, e in LIVE if c == cat), (cat, floor)


@pytest.mark.parametrize('floor', range(1, 11))
def test_every_floor_has_ecology_creatures_and_threats(floor):
    kinds = {e['kind'] for e in floor_ecology()[floor]['entries']}
    assert 'creature' in kinds
    assert kinds & {'hazard', 'event'}


def test_every_ecology_creature_exists():
    for floor in floor_ecology().values():
        for entry in floor['entries']:
            names = [entry['creature']] if entry.get('creature') else []
            names += [g['creature'] for g in entry.get('group', []) + entry.get('companions', [])]
            for name in names:
                assert find_creature(CREATURES, name), f"{entry['id']}: {name}"


def test_find_creature_prefers_the_remaster_stat_block():
    # Mitflit has a legacy (alignment LE) and a remaster record
    assert 'LE' not in find_creature(CREATURES, 'Mitflit')['traits']


def test_every_shop_has_its_people():
    shops = load('otari_shops.json')
    for config in MERCHANT_CONFIGS:
        assert merchant_slug(config['name']) in shops
        assert config['proprietor'] and config['specialties']


@pytest.mark.parametrize('level', range(1, 21))
def test_potions_exist_at_or_below_every_level(level):
    items = [e for e in prepare_equipment(load('equipment.json')) if e['level'] <= level]
    assert any('Healing Potion' in e['name'] for e in items)
    assert any('Spell Slot Restoration Potion' in e['name'] for e in items)
