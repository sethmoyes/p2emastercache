"""The 5d20 dungeon turn: category mapping, its odds, and generation on every floor."""
import random
from fractions import Fraction

import pytest

from conftest import ROOT  # noqa: F401  (sets up import paths)
import avtools.dungeon_turn as v2
from avtools.ecology import THREAT_ORDER, creature_xp, rate_encounter
from avtools.events import select_template

DANGER = {'COMBAT', 'ACTIVE_THREAT'}
MIDDLE = {'OPPORTUNITY', 'COMPLICATION', 'DILEMMA'}


@pytest.mark.parametrize('total,expected', [
    (16, DANGER), (44, DANGER), (45, MIDDLE), (62, MIDDLE), (63, DANGER), (89, DANGER),
])
def test_category_bands(total, expected):
    for _ in range(50):
        assert v2.get_category_from_sum(total, allow_no_event=False) in expected


@pytest.mark.parametrize('total', [5, 15, 90, 100])
def test_extreme_rolls_are_always_combat(total):
    assert v2.get_category_from_sum(total, is_extreme=True) == 'COMBAT'


def sum_odds(dice=5, sides=20):
    odds = {0: Fraction(1)}
    for _ in range(dice):
        nxt = {}
        for total, p in odds.items():
            for face in range(1, sides + 1):
                nxt[total + face] = nxt.get(total + face, 0) + p / sides
        odds = nxt
    return odds


def test_documented_odds():
    """README and claude.md say extreme rolls come up about once in 530."""
    odds = sum_odds()
    extreme = sum(p for total, p in odds.items() if total <= 15 or total >= 90)
    assert 1 / 540 < extreme < 1 / 520
    middle = sum(p for total, p in odds.items() if 45 <= total <= 62)
    # Half of non-extreme rolls are quiet; of the rest, the middle band is non-combat
    assert 0.24 < float(middle) / 2 < 0.26


def test_retired_templates_never_roll():
    templates = [{'title': 'old', 'floor': 1, 'retired': 'off-book'}, {'title': 'new', 'floor': 1}]
    assert all(select_template(templates, floor=1)['title'] == 'new' for _ in range(50))


def test_templates_stay_on_their_floor():
    templates = [{'title': 'f2', 'floor': 2}, {'title': 'any', 'floor': 0}]
    assert {select_template(templates, floor=3)['title'] for _ in range(50)} == {'any'}


@pytest.mark.parametrize('floor', range(1, 11))
def test_every_sum_generates_on_every_floor(floor):
    random.seed(floor)
    levels = v2.floor_levels()
    from conftest import ROOT as root
    import json, os
    creatures = json.load(open(os.path.join(root, 'etc', 'creatures.json')))
    for level in (1, 5, 10, 15, 20):
        for total in range(5, 101):
            event = v2.generate_event_for_sum(total, floor, levels[floor], level, creatures, 4, False)
            assert event['category'] in DANGER | MIDDLE
            assert event['title']


def test_creatures_far_above_the_party_rate_beyond_extreme():
    assert creature_xp(9, 1) is None
    assert rate_encounter(0, 4, off_chart=True) == 'Beyond Extreme'
    assert THREAT_ORDER[-1] == 'Beyond Extreme'
