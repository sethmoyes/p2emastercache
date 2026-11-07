"""Pathbuilder custom packs: the pack's shape, each kind of item, and the shop download."""
import html
import re

import pytest

from avtools import pathbuilder as pb
from avtools.web.render import parse_shop


def record(name, level='0', price='1 gp', scroll=False, **extra):
    return {'name': name, 'level': level, 'price': price, 'scroll': scroll, 'rarity': 'common',
            'facts': [], 'summary': '', 'url': '', **extra}


def test_weapons_carry_the_numbers_pathbuilder_uses():
    key, entry = pb.item_entry(record('Longsword'))
    assert key == 'listCustomWeapons'
    assert (entry['damage'], entry['damageType'], entry['group'], entry['proficiencyType']) == (8, 'S', 'Sword', 1)
    assert 'Versatile P' in entry['weaponTraits']
    key, entry = pb.item_entry(record('Hand Crossbow', price='3 gp'))
    assert (entry['rangedType'], entry['range'], entry['reload']) == (1, '60 ft.', '1')


def test_armor_and_shields():
    key, entry = pb.item_entry(record('Full Plate', level='2', price='30 gp'))
    assert key == 'listCustomArmor'
    assert (entry['acBonus'], entry['dexCap'], entry['strength'], entry['checkPenalty'],
            entry['speedPenalty'], entry['proficiencyType']) == (6, 0, 4, -3, -10, 2)
    key, entry = pb.item_entry(record('Buckler'))
    assert key == 'listCustomShields'
    assert (entry['category'], entry['hardness'], entry['hp']) == (pb.SHIELD, 3, 6)


def test_other_gear_and_items_aon_lacks():
    key, entry = pb.item_entry(record('Healing Potion (Minor)', level='1', price='4 gp'))
    assert key == 'listCustomEquipment' and entry['category'] == pb.GEAR
    assert '1d8 Hit Points' in entry['description'] and entry['bulk'] == 'L'
    # Campaign items with no AoN page still go in, with what the shop knows
    key, entry = pb.item_entry(record('Spell Slot Restoration Potion (Minor)', level='1', price='8 gp',
                                      summary='Restores one expended 1st-level spell slot'))
    assert key == 'listCustomEquipment' and 'spell slot' in entry['description']


def test_scrolls_say_how_they_work():
    key, entry = pb.item_entry(record('Fireball', level='3', price='30 gp', scroll=True, facts=[('DC', '20')]))
    assert entry['name'] == 'Scroll of Fireball (Rank 3)'
    assert entry['itemLevel'] == 5 and 'Scroll' in entry['traits']
    assert 'used up' in entry['description'] and 'Learn a Spell' in entry['description']
    assert '6d6 fire damage' in entry['description']


@pytest.mark.parametrize('text,gp', [('4 gp', 4), ('1,200 gp', 1200), ('5 sp', 0.5), ('1 cp (price for 10)', 0.01),
                                     ('2 pp', 20), ('n/a', None)])
def test_prices_in_gold(text, gp):
    assert pb.price_gp(text) == gp


def test_ids_are_stable_so_reimporting_updates():
    one = pb.build_pack([record('Longsword'), record('Longsword')])
    two = pb.build_pack([record('Longsword')])
    assert one['customPackID'] == two['customPackID'] == pb.PACK_ID
    assert len(one['listCustomWeapons']) == 1
    assert one['listCustomWeapons'][0]['uniqueIdentiier'] == two['listCustomWeapons'][0]['uniqueIdentiier']


def test_every_shop_exports(client):
    from avtools.merchants import MERCHANT_CONFIGS, merchant_slug
    from avtools.web.core import merchant_path
    for config in MERCHANT_CONFIGS:
        slug = merchant_slug(config['name'])
        path = merchant_path('players', f'{slug}.md')
        if not path:
            continue
        with open(path, encoding='utf-8') as f:
            count = sum(len(g['entries']) for s in parse_shop(f.read()) for g in s['groups'])
        response = client.get(f'/players/shop/{slug}/pathbuilder.json')
        assert response.status_code == 200
        assert 'attachment' in response.headers['Content-Disposition']
        pack = response.get_json()
        assert sum(len(v) for v in pack.values() if isinstance(v, list)) <= count
        response.get_data().decode('ascii')  # ASCII only (claude.md)


def test_the_form_exports_only_what_was_picked(client):
    page = client.get('/players/shop/wrins_wonders').get_data(as_text=True)
    assert 'Paid Pathbuilder only' in page and '/players/pathbuilder' in page
    keys = re.findall(r'name="item" value="([^"]+)"', page)
    assert keys and all(k.startswith(('item:', 'scroll:')) for k in keys)
    pick = next(k for k in keys if k.startswith('item:'))
    pack = client.post('/players/shop/wrins_wonders/pathbuilder.json',
                       data={'item': [pick, 'item:Not On Sale']}).get_json()
    assert [e['name'] for v in pack.values() if isinstance(v, list) for e in v] == [html.unescape(pick[5:])]
    assert client.post('/players/shop/wrins_wonders/pathbuilder.json', data={}).status_code == 400
    assert client.get('/players/shop/nowhere/pathbuilder.json').status_code == 404


def test_help_page_and_scroll_rules_on_the_shop_page(client):
    help_page = client.get('/players/pathbuilder').get_data(as_text=True)
    assert 'paid version' in help_page and 'Import Custom Pack' in help_page
    shop = client.get('/players/shop/wrins_wonders').get_data(as_text=True)
    if 'data-kind="scroll"' in shop:
        assert 'studied with the merchant' not in shop and 'Learn a Spell' in shop
