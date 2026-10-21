"""Restocking follows the shop rules at every party level."""
import contextlib
import io
import os
import random
import re

import pytest

from conftest import ROOT  # noqa: F401
import generate_merchants as g


def restock(root, level, **settings):
    random.seed(level)
    settings = g.normalize_settings({'player_level': level, 'fetch_images': False, 'fetch_portraits': False,
                                     **settings})
    with contextlib.redirect_stdout(io.StringIO()):
        g.generate_all(settings, str(root))


def potion_count(text):
    section = re.search(r'# HEALING POTIONS.*?\n\n---', text, re.S)
    return sum(int(n) for n in re.findall(r'\| [^|]*Potion[^|]*\| (\d+) \|', section.group(0))) if section else 0


@pytest.mark.parametrize('level', [1, 4, 10, 11, 16, 17, 20])
def test_every_shop_follows_the_rules(tmp_path, level):
    restock(tmp_path, level, random_merchants=1)
    for folder in ('players', 'gm'):
        for name in os.listdir(tmp_path / folder):
            text = (tmp_path / folder / name).read_text()
            assert 3 <= potion_count(text) <= 6, name
            assert 'Spell Slot Restoration' in text, name
            assert '| 0 gp |' not in text, name


def test_blades_for_glades_sells_weapons(tmp_path):
    restock(tmp_path, 4, merchants=['blades_for_glades'], random_merchants=0)
    text = (tmp_path / 'players' / 'blades_for_glades.md').read_text()
    weapons = {e['name'] for e in g.prepare_equipment(g.load_equipment_json(os.path.join(g.PROJECT_ROOT, 'etc', 'equipment.json')))
               if e['kind'] == 'weapon'}
    assert any(f'| {w} |' in text for w in weapons)


def test_restock_replaces_the_traveling_merchants(tmp_path):
    (tmp_path / 'gm').mkdir()
    (tmp_path / 'gm' / 'random_merchant_1:_old.md').write_text('# old')
    restock(tmp_path, 4, merchants=[], random_merchants=3)
    restock(tmp_path, 4, merchants=[], random_merchants=1)
    assert sorted(os.listdir(tmp_path / 'gm')) == ['traveling_merchant_1.md']


def test_named_matches_whole_words_only():
    assert g.named({'name': 'Wizard Hat'}, 'hat')
    assert not g.named({'name': 'Hatchet'}, 'hat')
    assert g.named({'name': 'Fishing Nets'}, 'net')


def test_items_get_a_kind_from_their_category():
    items = g.prepare_equipment([
        {'name': 'Longsword', 'type': 'adventuring', 'item_category': 'Weapons', 'price': '1 gp', 'level': 0, 'rarity': 'common'},
        {'name': 'Free Thing', 'type': 'adventuring', 'item_category': 'Consumables', 'price': '0 gp', 'level': 0, 'rarity': 'common'},
        {'name': 'A House', 'type': 'adventuring', 'item_category': 'Structures', 'price': '100 gp', 'level': 0, 'rarity': 'common'},
    ])
    assert [(i['name'], i['kind']) for i in items] == [('Longsword', 'weapon')]
