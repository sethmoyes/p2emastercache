"""
Shop items as a Pathbuilder 2e custom pack, so players can add what they bought
to their characters. Pathbuilder's own item list misses many official items;
a custom pack (a JSON file imported from its Custom Pack menu, a paid feature)
fills the gap.

The format follows packs the community already shares: lists of weapons,
armor, shields and other equipment. Weapons, armor and shields carry the
numbers Pathbuilder does math with (from etc/pathbuilder_items.json, built by
bin/data_management/fetch_pathbuilder_items.py); everything else goes in as
gear with its rules text. Every shop exports into one pack with a fixed ID, and
each item's ID comes from its name, so importing again updates the pack
instead of adding a second copy.
"""

import re
import time
import uuid
from functools import lru_cache

from avtools import items
from avtools.aon import ascii_text
from avtools.data import AON_BASE, etc_path, read_json

PACK_NAME = 'Otari Shops (Abomination Vaults)'
SOURCE = 'Otari shops'
NAMESPACE = uuid.UUID('6f1c1d52-3f0e-4c55-9a51-2d0f6c8a7b3e')
PACK_ID = str(uuid.uuid5(NAMESPACE, 'pack:otari'))
GEAR = 8          # Pathbuilder's category for custom equipment
SHIELD = -1       # ...and for custom shields
WEAPON_PROFICIENCY = {'Simple': 0, 'Martial': 1, 'Advanced': 2, 'Unarmed': 3}
ARMOR_PROFICIENCY = {'Light': 0, 'Medium': 1, 'Heavy': 2, 'Unarmored': 3}
COINS = {'pp': 10, 'gp': 1, 'sp': 0.1, 'cp': 0.01}

SCROLL_RULES = (f'<p><b>Casting from a scroll</b> {items.SCROLL_CASTING}</p>'
                f'<p><b>Learning the spell</b> {items.SCROLL_LEARNING}</p>')


@lru_cache(maxsize=None)
def item_data():
    try:
        return read_json(etc_path('pathbuilder_items.json')).get('items', {})
    except (OSError, ValueError):
        return {}


@lru_cache(maxsize=None)
def _equipment():
    by_name = {}
    for item in read_json(etc_path('equipment.json')):
        by_name.setdefault(item['name'], item)
    return by_name


@lru_cache(maxsize=None)
def _spells():
    """Spell name -> its record, the newest AoN page when a name repeats (remaster over legacy)."""
    def aon_id(spell):
        found = re.search(r'ID=(\d+)', spell.get('url') or '')
        return int(found.group(1)) if found else 0
    by_name = {}
    for spell in read_json(etc_path('spells.json')):
        if spell['name'] not in by_name or aon_id(spell) > aon_id(by_name[spell['name']]):
            by_name[spell['name']] = spell
    return by_name


def item_id(name):
    return str(uuid.uuid5(NAMESPACE, 'item:' + name.lower()))


def price_gp(text):
    """'1,200 gp' -> 1200, '5 sp' -> 0.5; the first amount in the cell."""
    found = re.search(r'([\d,]+(?:\.\d+)?)\s*(pp|gp|sp|cp)\b', text or '', re.I)
    if not found:
        return None
    value = float(found.group(1).replace(',', '')) * COINS[found.group(2).lower()]
    return int(value) if value == int(value) else round(value, 2)


def _int(text):
    try:
        return int(str(text).strip())
    except (TypeError, ValueError):
        return None


def _bulk(value):
    if value in (None, '', '-', '0', 0):
        return None
    if value == 0.1 or str(value).upper() == 'L':
        return 'L'
    return str(int(value)) if isinstance(value, float) and value == int(value) else str(value)


def _esc(text):
    return (text or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def _traits(record, known):
    """Pathbuilder lists rarity among the traits, the way AoN prints them."""
    traits = list(known)
    rarity = record.get('rarity', 'common')
    if rarity != 'common' and rarity.title() not in traits:
        traits.insert(0, rarity.title())
    return ', '.join(traits)


def _link(url):
    return f'<p>Full rules: {_esc(url)}</p>' if url else ''


def _base(record, name, level, price, description):
    entry = {
        'databaseID': 1,
        'timestamp': str(int(time.time() * 1000)),
        'uniqueIdentiier': item_id(name),  # sic: Pathbuilder's own spelling
        'name': name,
        'itemLevel': level,
        'description': description,
        'src': SOURCE,
    }
    if price is not None:
        entry['price'] = price
    return entry


def scroll_entry(record):
    """A spell scroll: one-use gear named for its spell and rank."""
    spell = _spells().get(record['name'], {})
    rank = _int(record.get('level')) or spell.get('level') or 1
    name = f"Scroll of {record['name']} (Rank {rank})"
    facts = ''.join(f'<p><b>Spell {_esc(k)}</b> {_esc(v)}</p>' for k, v in record.get('facts', []) if k == 'DC')
    entry = _base(record, name, max(1, rank * 2 - 1), price_gp(record.get('price')),
                  facts + spell_html(spell) + SCROLL_RULES + _link(record.get('url')))
    entry.update({'category': GEAR, 'bulk': 'L', 'usage': 'held in 1 hand',
                  'traits': _traits(record, ['Consumable', 'Magical', 'Scroll'])})
    return 'listCustomEquipment', entry


def spell_html(spell):
    """The spell's own text from spells.json: its casting line, then each part."""
    text = ' '.join(ascii_text(spell.get('text') or '').split())
    parts = [p.strip() for p in text.split(' --- ') if p.strip()]
    if not parts:
        return ''
    header, body = parts[0], parts[1:]
    labels = r'\b(Cast|Range|Area|Targets|Target|Duration|Saving Throw|Defense|Trigger|Requirements)\b'
    start = re.search(r'\bCast\b|\bRange\b|\bArea\b|\bTargets?\b', header)
    lines = []
    if start:
        chunks = re.split(labels, header[start.start():])
        lines = [f'<b>{_esc(chunks[i])}</b> {_esc(chunks[i + 1].strip())}'
                 for i in range(1, len(chunks) - 1, 2) if chunks[i + 1].strip()]
    html = f"<p>{'; '.join(lines)}</p>" if lines else ''
    for part in body:
        part = _esc(part)
        part = re.sub(r'^(Heightened \([^)]*\)|Critical Success|Success|Failure|Critical Failure)', r'<b>\1</b>',
                      part)
        part = re.sub(r' (Heightened \([^)]*\)|Critical Success|Success|Failure|Critical Failure) ',
                      r'</p><p><b>\1</b> ', part)
        html += f'<p>{part}</p>'
    return html


def item_entry(record):
    """(list name, entry) for one shop item."""
    if record.get('scroll'):
        return scroll_entry(record)
    name = record['name']
    known = item_data().get(name, {})
    local = _equipment().get(name, {})
    level = _int(record.get('level'))
    level = level if level is not None else known.get('level', local.get('level', 0))
    price = price_gp(record.get('price'))
    if not price and known.get('price_cp'):  # older shop files list some items at "0 gp"
        price = price_gp(f"{known['price_cp']} cp")
    summary = record.get('summary') or local.get('effect') or items.item_detail(name).get('summary', '')
    description = (known.get('description') or (f'<p>{_esc(summary)}</p>' if summary else '')) + _link(
        record.get('url') or (AON_BASE + known['url'] if known.get('url') else ''))
    bulk = _bulk(known.get('bulk') if known else local.get('bulk'))
    trait_list = known.get('traits') or local.get('traits') or []
    entry = _base(record, name, level, price, description)
    if bulk:
        entry['bulk'] = bulk

    weapon, armor, shield = known.get('weapon'), known.get('armor'), known.get('shield')
    if weapon:
        entry.update({'damage': weapon['die'], 'damageType': weapon['damage_type'], 'group': weapon['group'],
                      'hands': weapon['hands'], 'weaponTraits': _traits(record, trait_list)})
        proficiency = WEAPON_PROFICIENCY.get(weapon['category'], 0)
        if proficiency:
            entry['proficiencyType'] = proficiency
        if weapon['ranged']:
            entry['rangedType'] = 1
            if weapon.get('range'):
                entry['range'] = f"{weapon['range']} ft."
            if weapon.get('reload') is not None:
                entry['reload'] = weapon['reload']
        return 'listCustomWeapons', entry
    if armor:
        entry.update({'acBonus': armor['ac'], 'dexCap': armor['dex_cap'] if armor['dex_cap'] is not None else 5,
                      'checkPenalty': armor['check_penalty'], 'armorTraits': _traits(record, trait_list)})
        if armor.get('strength'):
            entry['strength'] = armor['strength']
        if armor.get('speed_penalty'):
            entry['speedPenalty'] = armor['speed_penalty']
        proficiency = ARMOR_PROFICIENCY.get(armor['category'], 0)
        if proficiency:
            entry['proficiencyType'] = proficiency
        return 'listCustomArmor', entry
    if shield:
        entry.update({'category': SHIELD, 'hardness': shield['hardness'], 'hp': shield['hp'],
                      'traits': _traits(record, trait_list)})
        return 'listCustomShields', entry
    entry.update({'category': GEAR, 'traits': _traits(record, trait_list)})
    if known.get('usage'):
        entry['usage'] = known['usage']
    return 'listCustomEquipment', entry


def build_pack(records):
    """A Pathbuilder custom pack holding these shop items (records from render.parse_shop)."""
    pack = {'customPackID': PACK_ID, 'customPackName': PACK_NAME}
    lists = {key: [] for key in ('listCustomWeapons', 'listCustomArmor', 'listCustomShields',
                                 'listCustomEquipment')}
    seen = set()
    for record in records:
        key, entry = item_entry(record)
        if entry['uniqueIdentiier'] in seen:
            continue
        seen.add(entry['uniqueIdentiier'])
        lists[key].append(entry)
    pack.update({key: entries for key, entries in lists.items() if entries})
    return pack
