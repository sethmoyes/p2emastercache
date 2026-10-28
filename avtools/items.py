"""
What the shop pages know about an item beyond its table row: its Archives of
Nethys page and summary (etc/item_details.json, built once by
bin/data_management/fetch_item_details.py), a picture if the GM has given it one
(etc/item_images.json), and otherwise the kind of thing it is, which picks its
icon in static/icons/icons.svg.
"""

import re
import urllib.parse
from functools import lru_cache

from avtools.data import AON_BASE, etc_path, read_json


def _read_optional(name):
    try:
        return read_json(etc_path(name))
    except (OSError, ValueError):
        return {}


@lru_cache(maxsize=None)
def details():
    """{'items': {name: {url, summary, subcategory}}, 'spells': {...}}, or empty when not built."""
    data = _read_optional('item_details.json')
    return {'items': data.get('items', {}), 'spells': data.get('spells', {})}


@lru_cache(maxsize=None)
def image_overrides():
    """Item name -> picture URL, for items the GM wants shown with real art."""
    return {name: url for name, url in _read_optional('item_images.json').get('items', {}).items()
            if isinstance(url, str) and re.match(r'^(https://|/static/)', url)}


@lru_cache(maxsize=None)
def _equipment():
    by_name = {}
    for item in read_json(etc_path('equipment.json')):
        by_name.setdefault(item['name'], item)
    return by_name


def search_name(name):
    """The base item name AoN's search understands: no '(Lesser)', no '+1'."""
    name = re.sub(r'\([^)]*\)', '', name)
    name = re.split(r'\d', name)[0]
    name = re.sub(r"[^a-zA-Z\s'-]", '', name)
    return ' '.join(name.split())


def item_detail(name, spell=False):
    return details()['spells' if spell else 'items'].get(name, {})


def aon_url(name, spell=False):
    """The item's or spell's own AoN page, else an AoN search for it."""
    page = item_detail(name, spell).get('url')
    if page:
        return AON_BASE + page
    query = name if spell else search_name(name)
    return f'{AON_BASE}/Search.aspx?query={urllib.parse.quote(query)}'


# First match wins: (pattern on the item's name, icon). Names are more specific
# than AoN's categories (a "Worn Item" may be boots, a ring or a hat).
NAME_RULES = [
    (r'\bscroll\b|\bmissive\b', 'scroll'),
    (r'\bspellgun\b', 'gun'),
    (r'\bblack powder\b', 'bomb'),
    (r'\b(?:saddle|harness|barding|horseshoes)\b', 'animal'),
    (r'\b(?:haversack|pouch|bag|sack|backpack|satchel|box|chest|case)\b', 'item'),
    (r'\bpotion\b', 'potion'),
    (r'\b(?:elixir|mutagen|tonic|draught|brew|philter|tincture)\b', 'elixir'),
    (r'\boil\b|\bbalm\b|\bsalve\b|\bointment\b', 'elixir'),
    (r'\bbomb\b|\bflask\b(?=.*\b(?:fire|frost|acid))|\bfire\b(?=.*\bflask)', 'bomb'),
    (r'\bpoison\b|\bvenom\b|\btoxin\b', 'poison'),
    (r'\bwand\b', 'wand'),
    (r'\bstaff\b|\bstave\b', 'staff'),
    (r'\brune\b|\bpotency\b|\bstriking\b|\bresilient\b|\breinforcing\b', 'rune'),
    (r'\btattoo\b', 'tattoo'),
    (r'\bring\b', 'ring'),
    (r'\b(?:amulet|necklace|pendant|torc|choker|medallion|periapt|locket|collar)\b', 'neck'),
    (r'\b(?:boots|shoes|slippers|sandals|greaves|anklets?)\b', 'boots'),
    (r'\b(?:cloak|cape|mantle|robe|robes|shawl|scarf|vestments?)\b', 'cloak'),
    (r'\b(?:hat|cap|circlet|crown|helm|helmet|headband|diadem|mask|hood|tiara)\b', 'hat'),
    (r'\b(?:gloves?|gauntlets?|mitts?|handwraps?)\b', 'gloves'),
    (r'\b(?:bracers?|bracelets?|armbands?|wristbands?|bangles?)\b', 'bracers'),
    (r'\b(?:belt|sash|girdle|bandolier)\b', 'belt'),
    (r'\b(?:goggles|spectacles|lenses|lens|monocle|eyepiece|glasses|eye)\b', 'eyes'),
    (r'\b(?:arrows?|bolts?|bullets?|rounds|shot|darts?|sling stones?|ammunition)\b', 'ammo'),
    (r'\b(?:talisman|fulu|charm|amulet)\b', 'talisman'),
    (r'\b(?:book|tome|grimoire|manual|codex|journal|almanac)\b', 'book'),
    (r'\b(?:lantern|lamp|candle|torch|sunrod|everlight)\b', 'light'),
    (r'\b(?:snare|trap|caltrops|mine)\b', 'snare'),
    (r'\b(?:kit|tools|toolkit|instruments?)\b', 'tools'),
    (r'\b(?:rations|food|tea|bread|meal|feast|cake|candy|jerky)\b', 'food'),
    (r'\b(?:ale|wine|beer|mead|stein|keg|liquor|whiskey|rum)\b', 'drink'),
    (r'\b(?:herb|herbs|root|leaf|flower|blossom|petal|moss|fungus|toadstool)\b', 'herb'),
    (r'\b(?:gem|gems|crystal|stone|spellheart|jewel|pearl|aeon)\b', 'gem'),
]
WEAPON_RULES = [
    (r'\b(?:gauntlet|knuckles?|cestus|brass knuckles|fighting fan)\b', 'gloves'),
    (r'\b(?:gun|pistol|musket|rifle|arquebus|blunderbuss|pepperbox|cannon|dragon mouth|firearm|spellgun)\b', 'gun'),
    (r'\b(?:bow|crossbow|sling|longbow|shortbow|gakgung|launcher|blowgun|atlatl|bola)\b', 'bow'),
    (r'\b(?:axe|hatchet|halberd|glaive|scythe|pick|bardiche)\b', 'axe'),
    (r'\b(?:hammer|mace|maul|club|flail|morningstar|staff|bludgeon|tonfa|sap|nunchaku|frying pan)\b', 'hammer'),
    (r'\b(?:dagger|knife|kukri|sickle|kama|katar|stiletto|dirk|main-gauche|claw|fist)\b', 'dagger'),
    (r'\b(?:spear|lance|trident|pike|javelin|harpoon|ranseur|guisarme|naginata|polearm)\b', 'spear'),
]
SUBCATEGORY_KINDS = {
    'Potions': 'potion', 'Oils': 'elixir', 'Alchemical Elixirs': 'elixir', 'Alchemical Bombs': 'bomb',
    'Alchemical Poisons': 'poison', 'Alchemical Tools': 'alchemy', 'Alchemical Ammunition': 'ammo',
    'Alchemical Food': 'food', 'Alchemical Plants': 'herb', 'Magical Ammunition': 'ammo',
    'Talismans': 'talisman', 'Fulu': 'talisman', 'Spell Catalysts': 'gem', 'Gadgets': 'gadget',
    'Animals': 'animal', 'Animal Caretaking Gear': 'animal', 'Tea': 'drink', 'Drugs': 'herb',
    'Base Armor': 'armor', 'Specific Magic Armor': 'armor', 'Precious Material Armor': 'armor',
    'Basic Magic Armor': 'armor', 'Base Shields': 'shield', 'Specific Shields': 'shield',
    'Precious Material Shields': 'shield', 'Beast Guns': 'gun', 'Scopes': 'eyes',
    'Weapon Property Runes': 'rune', 'Armor Property Runes': 'rune', 'Accessory Runes': 'rune',
    'Fundamental Armor Runes': 'rune', 'Shield Runes': 'rune', 'Specialty Wands': 'wand',
    'Magic Wands': 'wand',
}
CATEGORY_KINDS = {
    'Weapons': 'sword', 'Armor': 'armor', 'Shields': 'shield', 'Runes': 'rune', 'Wands': 'wand',
    'Staves': 'staff', 'Tattoos': 'tattoo', 'Spellhearts': 'gem', 'Grimoires': 'book',
    'Snares': 'snare', 'Alchemical Items': 'alchemy', 'Consumables': 'item', 'Worn Items': 'neck',
    'Held Items': 'held', 'Animals and Gear': 'animal', 'Adventuring Gear': 'gear',
    'Assistive Items': 'tools', 'Customizations': 'tools', 'Materials': 'gem', 'Trade Goods': 'coins',
    'Grafts': 'alchemy', 'Potions': 'potion',
}
SECTION_KINDS = {'potion': 'potion', 'scroll': 'scroll', 'rune': 'rune'}


def item_kind(name, section=None):
    """The icon for an item: what the shop section, its name or its AoN category says it is."""
    if section in SECTION_KINDS:
        return SECTION_KINDS[section]
    lowered = name.lower()
    item = _equipment().get(name, {})
    category = item.get('item_category')
    if category == 'Weapons' or item.get('weapon_type'):
        for pattern, kind in WEAPON_RULES:
            if re.search(pattern, lowered):
                return kind
        return 'bow' if item.get('weapon_type') == 'Ranged' else 'sword'
    if category in ('Armor', 'Shields'):
        return CATEGORY_KINDS[category]
    for pattern, kind in NAME_RULES:
        if re.search(pattern, lowered):
            return kind
    sub = item_detail(name).get('subcategory')
    if sub in SUBCATEGORY_KINDS:
        return SUBCATEGORY_KINDS[sub]
    if category in CATEGORY_KINDS:
        return CATEGORY_KINDS[category]
    return {'weapon': 'sword', 'armor': 'armor', 'magical': 'held', 'alchemical': 'alchemy'}.get(
        item.get('type'), 'item')
