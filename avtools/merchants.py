#!/usr/bin/env python3
"""
Unified Otari Merchant Generator
Stocks Otari's shops and rolls traveling merchants, written as markdown
"""
import random
import re
import os
import json
import requests
from bs4 import BeautifulSoup

from avtools import data
from avtools.data import ROOT as PROJECT_ROOT
from avtools.items import aon_url

def load_equipment_json(filename):
    """Load equipment from JSON file"""
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)


# equipment.json files almost everything under type "adventuring"; the real
# kind of item is in item_category. Shops stock by kind.
KIND_BY_CATEGORY = {
    'Weapons': 'weapon',
    'Armor': 'armor', 'Shields': 'armor',
    'Alchemical Items': 'alchemical', 'Potions': 'alchemical',
    'Wands': 'magical', 'Staves': 'magical', 'Worn Items': 'magical', 'Held Items': 'magical',
    'Grimoires': 'magical', 'Spellhearts': 'magical', 'Runes': 'magical', 'Tattoos': 'magical',
    'Grafts': 'magical',
}
# Not things a shop sells
UNSTOCKED_CATEGORIES = {'Services', 'Structures', 'High-Tech', 'Artifacts', 'Relics',
                        'Intelligent Items', 'Cursed Items', 'Apex Items', 'Figurehead'}


def has_price(price):
    return bool(price) and str(price).strip() not in ('0', '0 gp', '0 sp', '0 cp', '-', 'N/A')


def prepare_equipment(items):
    """Sellable items, one per name, each with a 'kind' shops can stock by."""
    seen = set()
    prepared = []
    for item in items:
        if item['name'] in seen or item.get('item_category') in UNSTOCKED_CATEGORIES:
            continue
        if not has_price(item.get('price')):
            continue
        seen.add(item['name'])
        kind = KIND_BY_CATEGORY.get(item.get('item_category'))
        if not kind:
            kind = item['type'] if item.get('type') in ('weapon', 'armor', 'alchemical', 'magical') else 'adventuring'
        prepared.append({**item, 'kind': kind})
    return prepared

def load_spells_json(filename):
    """Load spells from JSON file"""
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)


TRADITIONS = ('Arcane', 'Divine', 'Occult', 'Primal')


def prepare_spells(spells):
    """One record per spell name (the remaster one, newest on AoN), listing only
    the four magical traditions ("Elemental" is a spell list, not a tradition)."""
    def aon_id(spell):
        try:
            return int(spell.get('url', '').rsplit('=', 1)[1])
        except (IndexError, ValueError):
            return 0
    newest = {}
    for spell in spells:
        if spell['name'] not in newest or aon_id(spell) > aon_id(newest[spell['name']]):
            newest[spell['name']] = spell
    return [{**s, 'traditions': [t for t in s.get('traditions', []) if t in TRADITIONS]} for s in newest.values()]

def get_spell_price_and_dc(spell_level):
    """Get the price and DC for learning a spell based on its level"""
    price_table = {
        0: ("2 gp", 15),   # Cantrip
        1: ("2 gp", 15),
        2: ("6 gp", 18),
        3: ("16 gp", 20),
        4: ("36 gp", 23),
        5: ("70 gp", 26),
        6: ("140 gp", 28),
        7: ("300 gp", 31),
        8: ("650 gp", 34),
        9: ("1,500 gp", 36),
        10: ("7,000 gp", 41)
    }
    return price_table.get(spell_level, ("N/A", "N/A"))

def generate_spell_inventory(spells, max_level, num_common, num_uncommon, has_rare=False):
    """Generate random spell inventory (scrolls for learning)"""
    inventory = {'common': [], 'uncommon': [], 'rare': []}
    
    # Filter spells by level and rarity - only actual spells, not focus or cantrips
    common_pool = [s for s in spells if s['level'] <= max_level and s['rarity'] == 'common' and s['type'] == 'Spell']
    uncommon_pool = [s for s in spells if s['level'] <= max_level and s['rarity'] == 'uncommon' and s['type'] == 'Spell']
    rare_pool = [s for s in spells if s['level'] <= max_level and s['rarity'] == 'rare' and s['type'] == 'Spell']
    
    # Select spells
    if common_pool:
        inventory['common'] = random.sample(common_pool, min(num_common, len(common_pool)))
    
    if uncommon_pool:
        inventory['uncommon'] = random.sample(uncommon_pool, min(num_uncommon, len(uncommon_pool)))
    
    if has_rare and rare_pool:
        inventory['rare'] = [random.choice(rare_pool)]
    
    return inventory

def generate_rune_inventory(equipment, max_level, fundamental_range=(2, 3), property_range=(1, 3)):
    """Generate rune inventory for magic shops

    Returns:
        dict with 'fundamental' (fundamental_range copies of each fundamental weapon rune) and
        'other' (property_range non-fundamental runes)
    """
    inventory = {'fundamental': [], 'other': []}
    
    # Filter for runes at or below max level
    all_runes = [e for e in equipment if e.get('item_category') == 'Runes' and e['level'] <= max_level]
    
    # Fundamental weapon runes are: Striking, Greater Striking, Major Striking
    # We identify them by name patterns (not by traits since traits aren't in the JSON)
    fundamental_weapon_runes = []
    other_runes = []
    
    for rune in all_runes:
        name_lower = rune['name'].lower()
        
        # Check if it's a fundamental weapon rune by name
        # Fundamental weapon runes: striking (but NOT in armor/handwraps context)
        # We want actual rune items, not handwraps or armor
        is_striking = 'striking' in name_lower and 'handwraps' not in name_lower
        
        # Potency runes for weapons (not armor potency)
        is_weapon_potency = 'potency' in name_lower and 'armor' not in name_lower
        
        if is_striking or is_weapon_potency:
            fundamental_weapon_runes.append(rune)
        else:
            other_runes.append(rune)
    
    # Add several copies of each fundamental weapon rune
    for rune in fundamental_weapon_runes:
        quantity = random.randint(*fundamental_range)
        for _ in range(quantity):
            inventory['fundamental'].append(rune)

    # Add a few property runes
    num_other = random.randint(*property_range)
    if other_runes:
        inventory['other'] = random.sample(other_runes, min(num_other, len(other_runes)))
    
    return inventory

# Default merchant images to cycle through
def get_merchant_image(npc_name):
    """A proprietor's portrait from PathfinderWiki, or None if it has none"""
    try:
        # Extract just the name (before parentheses)
        clean_name = npc_name.split('(')[0].strip()
        
        # For names with multiple words, try different variations
        name_variations = [
            clean_name.replace(' ', '_'),  # Full name with underscores
            clean_name.split()[0],  # First name only
        ]
        
        # If there's a last name, try that too
        if len(clean_name.split()) > 1:
            name_variations.append(clean_name.split()[-1])  # Last name only
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        # Try each name variation
        for name_underscore in name_variations:
            # Try both .jpg and .png extensions
            for ext in ['.png', '.jpg']:
                wiki_url = f"https://pathfinderwiki.com/wiki/File:{name_underscore}{ext}"
                
                response = requests.get(wiki_url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Look for the full resolution image link
                    fullres = soup.find('div', class_='fullImageLink')
                    if fullres:
                        a_tag = fullres.find('a')
                        if a_tag and a_tag.get('href'):
                            img_url = a_tag['href']
                            # Make sure it's a full URL
                            if img_url.startswith('//'):
                                img_url = 'https:' + img_url
                            elif img_url.startswith('/'):
                                img_url = 'https://pathfinderwiki.com' + img_url
                            return img_url
                    
                    # Fallback: look for any img with the name in src
                    imgs = soup.find_all('img')
                    for img in imgs:
                        src = img.get('src', '')
                        if name_underscore in src and (ext in src):
                            if src.startswith('//'):
                                return 'https:' + src
                            elif src.startswith('/'):
                                return 'https://pathfinderwiki.com' + src
                            return src
    except Exception:
        pass  # No portrait is better than a broken one

    return None

# Portrait lookups hit PathfinderWiki; settings can turn them off
FETCH_PORTRAITS = True

def fix_price(price):
    """Fix malformed prices from source data"""
    if not price or price == 'L':
        return "5 sp"  # Default for 'L' (likely means "Light" bulk, but used as price)
    
    # Handle integer prices (from Elasticsearch API)
    if isinstance(price, int):
        # Convert copper to proper denomination
        if price < 10:
            return f"{price} cp"
        elif price < 100:
            return f"{price} sp"
        else:
            # Convert to gold pieces
            gp = price / 100
            if gp == int(gp):
                return f"{int(gp)} gp"
            else:
                return f"{gp:.1f} gp"
    
    # Handle string prices
    price_str = str(price)
    
    # If it's just a number string, assume gp
    if price_str.isdigit():
        return f"{price_str} gp"
    
    return price_str

def capitalize_field(text):
    """Capitalize first letter of text, handle N/A"""
    if not text or text == 'N/A' or text == '':
        return 'N/A'
    return text[0].upper() + text[1:] if len(text) > 0 else text

def potions_for_level(potions, min_level):
    """Potions at min_level or above; if none (they only come in a few levels),
    the highest ones below it, so a shop is never left without."""
    in_band = [p for p in potions if p['level'] >= min_level]
    if in_band or not potions:
        return in_band
    best = max(p['level'] for p in potions)
    return [p for p in potions if p['level'] == best]


def generate_potion_inventory(equipment, player_level, count_range=(3, 6), level_offset=-3):
    """Generate healing potions for merchant

    Args:
        equipment: List of all equipment items (already capped at the max item level)
        player_level: Current player level
        count_range: (min, max) number of potions
        level_offset: Minimum potion level relative to player level

    Returns:
        List of potions, with at least 1 Spell Slot Restoration Potion
    """
    min_potion_level = max(1, player_level + level_offset)

    healing_potions = potions_for_level([e for e in equipment if 'Healing Potion' in e['name']], min_potion_level)
    spell_slot_potions = potions_for_level([e for e in equipment if 'Spell Slot Restoration Potion' in e['name']], min_potion_level)

    num_potions = random.randint(*count_range)

    # Always include at least 1 Spell Slot Restoration Potion
    potions = []
    if spell_slot_potions and num_potions > 0:
        potions.append(random.choice(spell_slot_potions))

    # Fill remaining slots with random mix of healing and spell slot potions
    all_potions = healing_potions + spell_slot_potions
    for _ in range(num_potions - len(potions)):
        if all_potions:
            potions.append(random.choice(all_potions))

    return potions

def generate_merchant_inventory(equipment, categories, num_common, num_uncommon, item_filter=None):
    """Generate random inventory from equipment filtered by player level
    
    Args:
        equipment: List of equipment items (pre-filtered by max level)
        categories: List of category types (weapon, armor, etc.)
        num_common: Number of common items to generate
        num_uncommon: Number of uncommon items to generate
        item_filter: Optional function to further filter items beyond category
    """
    inventory = {'common': [], 'uncommon': [], 'rare': []}
    
    # Filter by categories and rarity (level already filtered in equipment list)
    common_pool = [e for e in equipment if e['kind'] in categories and e['rarity'] == 'common']
    uncommon_pool = [e for e in equipment if e['kind'] in categories and e['rarity'] == 'uncommon']
    
    # Apply additional filter if provided
    if item_filter:
        common_pool = [e for e in common_pool if item_filter(e)]
        uncommon_pool = [e for e in uncommon_pool if item_filter(e)]
    
    # Select items
    if common_pool:
        inventory['common'] = random.sample(common_pool, min(num_common, len(common_pool)))
    
    if uncommon_pool:
        inventory['uncommon'] = random.sample(uncommon_pool, min(num_uncommon, len(uncommon_pool)))
    
    # Rare items are handled separately in main
    
    return inventory

def _item_link(name):
    return f"[View]({aon_url(name)})"


def _write_spell_table(f, title, spells):
    f.write(f"## {title} ({len(spells)})\n\n")
    f.write("| Spell Name | Level | Price | DC | Traditions | Range | Traits | Link |\n")
    f.write("|------------|-------|-------|-------|------------|-------|--------|------|\n")
    for spell in spells:
        level = spell['level']
        price, dc = get_spell_price_and_dc(level)
        traditions = ', '.join(spell.get('traditions', ['N/A']))
        traits = ', '.join(spell.get('traits', [])[:3]) or 'N/A'
        url = f"https://2e.aonprd.com{spell['url']}" if spell.get('url') else aon_url(spell['name'], spell=True)
        f.write(f"| SCROLL OF {spell['name'].upper()} | {level} | {price} | {dc} | {traditions} "
                f"| {spell.get('range', 'N/A')} | {traits} | [View]({url}) |\n")
    f.write("\n")


def _write_item_table(f, title, items):
    f.write(f"## {title} ({len(items)})\n\n")
    f.write("| Name | Level | Price | Rarity | Category | Type | Link |\n")
    f.write("|------|-------|-------|--------|----------|------|------|\n")
    for item in items:
        f.write(f"| {item['name']} | {item['level']} | {fix_price(item['price'])} "
                f"| {capitalize_field(item['rarity'])} | {capitalize_field(item.get('category', 'N/A'))} "
                f"| {capitalize_field(item['type'])} | {_item_link(item['name'])} |\n")
    f.write("\n")


def stack(items):
    """[(item, count)] in first-seen order, identical names counted once"""
    counts = {}
    for item in items:
        counts.setdefault(item['name'], [item, 0])[1] += 1
    return [tuple(pair) for pair in counts.values()]


def write_merchant_with_header(merchant_name, description, proprietor, specialties, inventory, services=None, spell_inventory=None, rune_inventory=None, potion_inventory=None, output_dir='players', portrait=None, filename=None):
    """Write merchant file with header, proprietor portrait, and full item details"""
    filename = filename or merchant_name.lower().replace(' ', '_').replace("'", '') + '.md'
    filepath = os.path.join(output_dir, filename)

    # Write to a temp file and swap it in, so the live site never serves a half-written shop
    tmp_path = filepath + '.tmp'
    with open(tmp_path, 'w', encoding='utf-8') as f:
        # Header with proprietor image (small size - 250px)
        f.write(f"# {merchant_name}\n\n")
        if portrait:
            f.write(f"<div align=\"center\">\n\n")
            f.write(f"<img src=\"{portrait}\" alt=\"{proprietor.split('(')[0].strip()}\" width=\"250\">\n\n")
            f.write(f"</div>\n\n")
        f.write(f"*{description}*\n\n")
        f.write(f"**Proprietor:** {proprietor}\n\n")
        f.write(f"**Specialties:** {specialties}\n\n")

        # Potion section (if applicable) - ALWAYS FIRST; identical potions stack into one row
        if potion_inventory:
            f.write("---\n\n")
            f.write("# HEALING POTIONS\n\n")
            f.write("*These potions restore Hit Points or spell slots when consumed.*\n\n")
            f.write("| Name | Qty | Level | Price | Effect | Link |\n")
            f.write("|------|-----|-------|-------|--------|------|\n")
            for potion, qty in stack(potion_inventory):
                f.write(f"| {potion['name']} | {qty} | {potion['level']} | {fix_price(potion['price'])} "
                        f"| {potion.get('effect', 'N/A')} | {_item_link(potion['name'])} |\n")
            f.write("\n")
            f.write("---\n\n")

        # Spell scrolls section (if applicable)
        if spell_inventory:
            f.write("---\n\n")
            f.write("# SPELL SCROLLS FOR LEARNING\n\n")
            f.write("*These scrolls can be studied with the merchant to permanently learn the spell.*\n\n")
            f.write("*Study time: 1 hour (common), 5 hours (uncommon), 1 day (rare).*\n\n")
            for rarity in ('common', 'uncommon', 'rare'):
                if spell_inventory[rarity]:
                    _write_spell_table(f, f"{rarity.capitalize()} Spell Scrolls", spell_inventory[rarity])
            f.write("---\n\n")

        # Rune section (if applicable)
        if rune_inventory:
            f.write("# RUNES\n\n")
            f.write("*Runes can be etched onto weapons and armor to enhance their properties.*\n\n")

            # Fundamental weapon runes (always available, several of each)
            if rune_inventory['fundamental']:
                f.write(f"## Fundamental Weapon Runes (Always Available)\n\n")
                f.write("| Name | Quantity | Level | Price | Rarity | Link |\n")
                f.write("|------|----------|-------|-------|--------|------|\n")
                for rune, quantity in stack(rune_inventory['fundamental']):
                    f.write(f"| {rune['name']} | {quantity} | {rune['level']} | {fix_price(rune['price'])} "
                            f"| {capitalize_field(rune['rarity'])} | {_item_link(rune['name'])} |\n")
                f.write("\n")
            else:
                # If no fundamental runes in database, show standard availability
                f.write(f"## Fundamental Runes (Always Available on Request)\n\n")
                f.write("*The following fundamental runes can be purchased at standard prices (2-3 of each in stock):*\n\n")
                f.write("**Weapon Runes:**\n")
                f.write("- **Weapon Potency (+1)** (Level 2): 35 gp - [View](https://2e.aonprd.com/Equipment.aspx?ID=2829)\n")
                f.write("- **Weapon Potency (+2)** (Level 10): 935 gp - [View](https://2e.aonprd.com/Equipment.aspx?ID=2829)\n")
                f.write("- **Weapon Potency (+3)** (Level 16): 8,935 gp - [View](https://2e.aonprd.com/Equipment.aspx?ID=2829)\n")
                f.write("- **Striking** (Level 4): 65 gp - [View](https://2e.aonprd.com/Equipment.aspx?ID=2830)\n")
                f.write("- **Greater Striking** (Level 12): 1,065 gp - [View](https://2e.aonprd.com/Equipment.aspx?ID=2830)\n")
                f.write("- **Major Striking** (Level 19): 31,065 gp - [View](https://2e.aonprd.com/Equipment.aspx?ID=2830)\n\n")
                f.write("**Armor Runes:**\n")
                f.write("- **Armor Potency (+1)** (Level 5): 160 gp - [View](https://2e.aonprd.com/Equipment.aspx?ID=2785)\n")
                f.write("- **Armor Potency (+2)** (Level 11): 1,060 gp - [View](https://2e.aonprd.com/Equipment.aspx?ID=2785)\n")
                f.write("- **Armor Potency (+3)** (Level 18): 20,560 gp - [View](https://2e.aonprd.com/Equipment.aspx?ID=2785)\n")
                f.write("- **Resilient** (Level 8): 340 gp - [View](https://2e.aonprd.com/Equipment.aspx?ID=2786)\n")
                f.write("- **Greater Resilient** (Level 14): 3,440 gp - [View](https://2e.aonprd.com/Equipment.aspx?ID=2786)\n")
                f.write("- **Major Resilient** (Level 20): 49,440 gp - [View](https://2e.aonprd.com/Equipment.aspx?ID=2786)\n\n")
                f.write("**Shield Runes:**\n")
                f.write("- **Reinforcing** (Level 4): 100 gp - [View](https://2e.aonprd.com/Equipment.aspx?ID=2811)\n")
                f.write("- **Greater Reinforcing** (Level 11): 1,400 gp - [View](https://2e.aonprd.com/Equipment.aspx?ID=2811)\n")
                f.write("- **Major Reinforcing** (Level 17): 15,000 gp - [View](https://2e.aonprd.com/Equipment.aspx?ID=2811)\n\n")

            # Other runes
            if rune_inventory['other']:
                f.write(f"## Property Runes ({len(rune_inventory['other'])})\n\n")
                f.write("| Name | Level | Price | Rarity | Link |\n")
                f.write("|------|-------|-------|--------|------|\n")
                for rune in rune_inventory['other']:
                    f.write(f"| {rune['name']} | {rune['level']} | {fix_price(rune['price'])} "
                            f"| {capitalize_field(rune['rarity'])} | {_item_link(rune['name'])} |\n")
                f.write("\n")

            f.write("---\n\n")

        # Regular items section
        if inventory['common'] or inventory['uncommon'] or inventory['rare']:
            f.write("# REGULAR ITEMS\n\n")
        for rarity in ('common', 'uncommon', 'rare'):
            if inventory[rarity]:
                _write_item_table(f, f"{rarity.capitalize()} Items", inventory[rarity])

        # Services section
        if services:
            f.write("## Services\n\n")
            for service in services:
                f.write(f"- {service}\n")
            f.write("\n")

    os.replace(tmp_path, filepath)
    print(f"OK Created: {filepath}")


def merchant_slug(name):
    """File name (without .md) a merchant is written to"""
    return name.lower().replace(' ', '_').replace("'", '')

def named(item, *words):
    """True if the item's name contains any of these as whole words (plurals too)."""
    pattern = r'\b(?:' + '|'.join(re.escape(w) for w in words) + r')(?:e?s)?\b'
    return re.search(pattern, item['name'], re.I) is not None


def category(item, *categories):
    return item.get('item_category') in categories


# The ten Otari shops: what each one stocks. Who runs them (proprietor,
# description, specialties, portrait) lives in etc/otari_shops.json.
MERCHANT_CONFIGS = [
    {
        'name': 'Otari Market',
        'categories': ['weapon', 'armor', 'adventuring', 'alchemical', 'magical'],
        'item_filter': None,
        'double_items': True,  # Market uses the market_* stock settings
        'services': None
    },
    {
        'name': "Wrin's Wonders",
        'categories': ['magical', 'alchemical', 'adventuring'],
        'item_filter': lambda item: (
            item['kind'] in ('magical', 'alchemical')
            or category(item, 'Runes', 'Staves', 'Spellhearts', 'Wands')
            or named(item, 'scroll', 'talisman', 'elixir', 'potion')
        ),
        'double_items': False,
        'sells_spells': True,
        'sells_runes': True,
        'services': [
            "Spellcasting Services: Price varies by spell level (GM discretion)",
            "Spell Learning/Training: Price negotiable (GM discretion)",
            "Magical item identification: 1-10 gp depending on complexity",
            "Astrological readings: 5 sp - 5 gp"
        ]
    },
    {
        'name': 'Odd Stories',
        'categories': ['magical', 'adventuring'],
        'item_filter': lambda item: (
            category(item, 'Runes', 'Grimoires', 'Staves', 'Wands')
            or named(item, 'book', 'scroll', 'tome', 'manual', 'grimoire', 'formula', 'journal', 'map', 'ink', 'writing set')
        ),
        'double_items': False,
        'sells_spells': True,
        'sells_runes': True,
        'services': [
            "Spellcasting Services: Price varies by spell level (GM discretion)",
            "Spell Learning/Training: Price negotiable (GM discretion)",
            "Book copying and restoration: 1-5 gp per page",
            "Research assistance: 5 gp per day"
        ]
    },
    {
        'name': 'Gallentine Deliveries',
        'categories': ['adventuring'],
        'item_filter': lambda item: category(item, 'Animals and Gear'),
        'double_items': False,
        'services': [
            "Local delivery (within Otari): 1 sp per package",
            "Regional delivery (to nearby towns): 5 sp - 2 gp depending on distance",
            "Long-distance delivery: Price negotiable (GM discretion)",
            "Stabling: 2 sp per day",
            "Caravan or carriage transport: price negotiable (GM discretion)"
        ]
    },
    {
        'name': 'Blades for Glades',
        'categories': ['weapon', 'armor', 'adventuring'],
        'item_filter': lambda item: (
            item['kind'] in ('weapon', 'armor')
            or named(item, 'saw', 'axe', 'hatchet', 'tool', 'crowbar', 'chain', 'piton', 'grappling hook', 'manacle')
        ),
        'double_items': False,
        'services': [
            "Weapon sharpening: 5 sp",
            "Armor repair: 1-5 gp depending on damage",
            "Custom weapon crafting: Price negotiable (GM discretion)",
            "Weapon engraving: 1 gp"
        ]
    },
    {
        'name': "Crow's Casks",
        'categories': ['adventuring', 'alchemical'],
        'item_filter': lambda item: (
            item['kind'] == 'alchemical'
            or named(item, 'tea', 'oil', 'ration', 'meal', 'wine', 'ale', 'beer', 'mead', 'brew', 'tonic', 'elixir', 'potion')
        ),
        'double_items': False,
        'services': [
            "Meals: 1 cp (poor) to 1 gp (fine)",
            "Lodging: 3 cp (floor space) to 5 sp (private room)",
            "Ale/Wine: 1 cp (mug) to 1 sp (bottle); ask about Magiloy's latest experiment",
            "Rumors and information: Free with purchase"
        ]
    },
    {
        'name': "Crook's Nook",
        'categories': ['adventuring', 'alchemical'],
        'item_filter': lambda item: (
            category(item, 'Snares')
            or named(item, "thieves' toolkit", 'thieves', 'lockpick', 'poison', 'caltrop', 'smoke', 'disguise kit', 'manacle', 'grappling hook')
        ),
        'double_items': False,
        'services': [
            "Meals: seafood, 1 cp to 5 sp",
            "Lodging: 3 cp (floor space) to 3 sp (shared room)",
            "Ale: 1 cp",
            "A word with the Osprey Club: price and availability at Yinyasmera's discretion"
        ]
    },
    {
        'name': 'The Rowdy Rockfish',
        'categories': ['adventuring'],
        'item_filter': lambda item: named(item, 'ration', 'meal', 'wine', 'ale', 'beer', 'mead', 'tea', 'waterskin', 'bedroll', 'candle', 'soap'),
        'double_items': False,
        'services': [
            "Meals: 5 cp (square) to 2 gp (fine)",
            "Lodging: 5 cp (bed) to 1 gp (private room with bath)",
            "Ale/Wine: 1 cp (mug) to 5 sp (fine bottle)",
            "Hot bath: 2 cp"
        ]
    },
    {
        'name': 'Otari Fishery',
        'categories': ['adventuring'],
        'item_filter': lambda item: named(item, 'fish', 'fishing', 'net', 'rope', 'ration', 'waterskin', 'boat', 'oar', 'swim'),
        'double_items': False,
        'services': [
            "Fresh fish: 1 cp - 5 sp depending on type",
            "Passage on a sailing ship: price by destination (GM discretion)",
            "Games and snacks on the ground floor, nightly",
            "Net repair: 1 sp"
        ]
    },
    {
        'name': 'Dawnflower Library',
        'categories': ['magical', 'adventuring', 'alchemical'],
        'item_filter': lambda item: (
            category(item, 'Runes')
            or named(item, 'book', 'scroll', 'tome', 'manual', 'scripture', 'religious', 'holy', 'healing', 'antidote', 'antiplague', 'healer')
        ),
        'double_items': False,
        'sells_runes': True,
        'services': [
            "Spellcasting Services: Price varies by spell level (GM discretion)",
            "Healing: 1-20 gp depending on severity",
            "Remove curse/disease: 10-50 gp (GM discretion)",
            "Research assistance: Free for worshippers, 2 gp per day for others",
            "Blessings: Donation-based"
        ]
    }
]

for _config in MERCHANT_CONFIGS:
    _config.update(data.shops()[merchant_slug(_config['name'])])

TRAVELING = 'Traveling merchants (GM only)'

# Every knob the generator has. The GM page builds its restock form from this list,
# so a new setting only needs adding here. Ranges are [min, max], rolled per merchant.
SETTINGS_SCHEMA = [
    {'group': 'Basics', 'key': 'player_level', 'type': 'int', 'default': 4, 'min': 1, 'max': 20,
     'label': 'Party level'},
    {'group': 'Basics', 'key': 'item_level_offset', 'type': 'int', 'default': 0, 'min': -10, 'max': 10,
     'label': 'Max item level (party level +)'},
    {'group': 'Basics', 'key': 'spell_level_offset', 'type': 'int', 'default': 0, 'min': -10, 'max': 10,
     'label': 'Max spell level (party level +)'},
    {'group': 'Basics', 'key': 'fetch_portraits', 'type': 'bool', 'default': True,
     'label': 'Look up shopkeeper portraits',
     'help': 'Checks PathfinderWiki for each proprietor, falling back to a stock portrait.'},
    {'group': 'Shops to restock', 'key': 'merchants', 'type': 'merchants',
     'default': [merchant_slug(c['name']) for c in MERCHANT_CONFIGS],
     'label': 'Shops', 'help': 'Unchecked shops keep their current stock.'},
    {'group': 'Shop stock', 'key': 'common', 'type': 'range', 'default': [9, 45], 'min': 0, 'max': 150,
     'label': 'Common items per shop'},
    {'group': 'Shop stock', 'key': 'uncommon', 'type': 'range', 'default': [3, 9], 'min': 0, 'max': 100,
     'label': 'Uncommon items per shop'},
    {'group': 'Shop stock', 'key': 'rare_shops', 'type': 'int', 'default': 6, 'min': 0, 'max': 10,
     'label': 'Shops that get 1 rare item',
     'help': 'Picked at random from the checked shops. Otari Market rolls its own rares.'},
    {'group': 'Otari Market', 'key': 'market_common', 'type': 'range', 'default': [60, 150], 'min': 0, 'max': 400,
     'label': 'Common items'},
    {'group': 'Otari Market', 'key': 'market_uncommon', 'type': 'range', 'default': [15, 45], 'min': 0, 'max': 100,
     'label': 'Uncommon items'},
    {'group': 'Otari Market', 'key': 'market_rare', 'type': 'range', 'default': [3, 9], 'min': 0, 'max': 20,
     'label': 'Rare items'},
    {'group': 'Spells & runes', 'key': 'spells_common', 'type': 'range', 'default': [15, 45], 'min': 0, 'max': 100,
     'label': 'Common spell scrolls', 'help': "Wrin's Wonders and Odd Stories."},
    {'group': 'Spells & runes', 'key': 'spells_uncommon', 'type': 'range', 'default': [9, 15], 'min': 0, 'max': 50,
     'label': 'Uncommon spell scrolls'},
    {'group': 'Spells & runes', 'key': 'rare_spell', 'type': 'bool', 'default': True,
     'label': 'One spell shop gets a rare spell'},
    {'group': 'Spells & runes', 'key': 'fundamental_runes', 'type': 'range', 'default': [6, 9], 'min': 0, 'max': 30,
     'label': 'Copies of each fundamental rune',
     'help': "Wrin's Wonders, Odd Stories and Dawnflower Library."},
    {'group': 'Spells & runes', 'key': 'property_runes', 'type': 'range', 'default': [3, 9], 'min': 0, 'max': 20,
     'label': 'Property runes'},
    {'group': 'Potions', 'key': 'potions', 'type': 'range', 'default': [9, 18], 'min': 0, 'max': 40,
     'label': 'Healing potions per shop', 'help': 'At least one is a Spell Slot Restoration Potion.'},
    {'group': 'Potions', 'key': 'potion_level_offset', 'type': 'int', 'default': -3, 'min': -20, 'max': 5,
     'label': 'Min potion level (party level +)', 'help': 'Never below level 1.'},
    {'group': TRAVELING, 'key': 'random_merchants', 'type': 'int', 'default': 2, 'min': 0, 'max': 10,
     'label': 'Traveling merchants to create',
     'help': 'Added to the Random Merchants list on the GM page. Earlier ones are kept.'},
    {'group': TRAVELING, 'key': 'random_common', 'type': 'range', 'default': [15, 36], 'min': 0, 'max': 150,
     'label': 'Common items'},
    {'group': TRAVELING, 'key': 'random_uncommon', 'type': 'range', 'default': [3, 12], 'min': 0, 'max': 50,
     'label': 'Uncommon items'},
    {'group': TRAVELING, 'key': 'random_rare', 'type': 'range', 'default': [0, 6], 'min': 0, 'max': 20,
     'label': 'Rare items'},
]

def normalize_settings(raw=None):
    """Fill in defaults and clamp every value to its schema bounds"""
    raw = raw or {}
    known_merchants = [merchant_slug(c['name']) for c in MERCHANT_CONFIGS]
    settings = {}
    for field in SETTINGS_SCHEMA:
        value = raw.get(field['key'], field['default'])
        try:
            if field['type'] == 'bool':
                value = bool(value)
            elif field['type'] == 'int':
                value = min(field['max'], max(field['min'], int(value)))
            elif field['type'] == 'range':
                low, high = sorted(min(field['max'], max(field['min'], int(v))) for v in value)
                value = [low, high]
            elif field['type'] == 'merchants':
                if not isinstance(value, list):
                    raise TypeError(value)
                value = [slug for slug in known_merchants if slug in value]
        except (TypeError, ValueError):
            value = field['default']
        settings[field['key']] = value
    return settings

def shop_portrait(config):
    """The shop's known portrait, else one looked up by the proprietor's name."""
    if config.get('portrait') or not FETCH_PORTRAITS:
        return config.get('portrait')
    print("  Looking up the proprietor's portrait...", end=' ')
    found = get_merchant_image(config['proprietor'])
    print('OK' if found else 'none')
    return found


TRAVELING_FILE = re.compile(r'^traveling_merchant_(\d+)\.md$')


def traveling_merchant_filename(number):
    return f'traveling_merchant_{number}.md'


def generate_all(settings, output_root=PROJECT_ROOT):
    """Restock the selected Otari shops (players/) and create traveling merchants (gm/)"""
    global FETCH_PORTRAITS
    FETCH_PORTRAITS = settings['fetch_portraits']

    player_level = settings['player_level']
    max_item_level = player_level + settings['item_level_offset']
    spell_level = player_level + settings['spell_level_offset']
    selected = [c for c in MERCHANT_CONFIGS if merchant_slug(c['name']) in settings['merchants']]
    total = len(selected) + settings['random_merchants']

    print(f"Generating merchants for player level {player_level}")
    print(f"  Max item level: {max_item_level}")
    print(f"  Max spell level: {spell_level}")
    print(f"  Portraits: {'on' if FETCH_PORTRAITS else 'off'}")
    print()

    print("Loading equipment...")
    equipment = prepare_equipment(load_equipment_json(os.path.join(PROJECT_ROOT, 'etc', 'equipment.json')))

    # Filter equipment by max level
    equipment = [e for e in equipment if e['level'] <= max_item_level]
    print(f"  Loaded {len(equipment)} items (level {max_item_level} or below)")

    print("Loading spells...")
    spells = prepare_spells(load_spells_json(os.path.join(PROJECT_ROOT, 'etc', 'spells.json')))
    print(f"  Loaded {len(spells)} spells")

    # Create output directories
    players_dir = os.path.join(output_root, 'players')
    gm_dir = os.path.join(output_root, 'gm')
    os.makedirs(players_dir, exist_ok=True)
    os.makedirs(gm_dir, exist_ok=True)

    # Pick which shops get a rare item (Otari Market rolls its own; service-only shops can't stock one)
    rare_eligible = [c['name'] for c in selected if c['categories'] and not c.get('double_items')]
    rare_shops = random.sample(rare_eligible, min(settings['rare_shops'], len(rare_eligible)))
    if rare_shops:
        print(f"  Rare items: {', '.join(rare_shops)}")

    # Pick which spell shop gets a rare spell
    spell_shops = [c['name'] for c in selected if c.get('sells_spells')]
    rare_spell_shop = random.choice(spell_shops) if settings['rare_spell'] and spell_shops else None
    if rare_spell_shop:
        print(f"  Rare spell: {rare_spell_shop}")

    for step, config in enumerate(selected, 1):
        print(f"\n[{step}/{total}] Generating {config['name']}...")

        if config.get('double_items', False):
            num_common = random.randint(*settings['market_common'])
            num_uncommon = random.randint(*settings['market_uncommon'])
            num_rare = random.randint(*settings['market_rare'])
        else:
            num_common = random.randint(*settings['common'])
            num_uncommon = random.randint(*settings['uncommon'])
            num_rare = 1 if config['name'] in rare_shops else 0

        if config['categories']:  # Skip if service-only
            inventory = generate_merchant_inventory(
                equipment,
                categories=config['categories'],
                num_common=num_common,
                num_uncommon=num_uncommon,
                item_filter=config.get('item_filter')
            )

            # Add rare items
            if num_rare:
                rare_pool = [e for e in equipment if e['kind'] in config['categories'] and e['rarity'] == 'rare']
                # Apply item filter to rare pool too
                if config.get('item_filter'):
                    rare_pool = [e for e in rare_pool if config['item_filter'](e)]
                if rare_pool:
                    inventory['rare'] = random.sample(rare_pool, min(num_rare, len(rare_pool)))
                    print(f"  * Added {len(inventory['rare'])} rare item(s)")
        else:
            inventory = {'common': [], 'uncommon': [], 'rare': []}

        # Spell scrolls for Wrin's Wonders and Odd Stories
        spell_inventory = None
        if config.get('sells_spells'):
            spell_inventory = generate_spell_inventory(
                spells,
                max_level=spell_level,
                num_common=random.randint(*settings['spells_common']),
                num_uncommon=random.randint(*settings['spells_uncommon']),
                has_rare=(config['name'] == rare_spell_shop)
            )

            print(f"  Added {len(spell_inventory['common'])} common spells")
            print(f"  Added {len(spell_inventory['uncommon'])} uncommon spells")
            if spell_inventory['rare']:
                print(f"  * Added rare spell")

        # Runes for Wrin's Wonders, Odd Stories, and Dawnflower Library
        rune_inventory = None
        if config.get('sells_runes'):
            rune_inventory = generate_rune_inventory(
                equipment, max_item_level, settings['fundamental_runes'], settings['property_runes']
            )
            print(f"  Fundamental runes in stock: {len(rune_inventory['fundamental'])}")
            print(f"  Added {len(rune_inventory['other'])} property runes")

        # Every merchant stocks healing potions
        potion_inventory = generate_potion_inventory(
            equipment, player_level, settings['potions'], settings['potion_level_offset']
        )
        print(f"  Added {len(potion_inventory)} healing potions (at least 1 Spell Slot Restoration)")

        write_merchant_with_header(
            config['name'],
            config['description'],
            config['proprietor'],
            config['specialties'],
            inventory,
            config['services'],
            spell_inventory,
            rune_inventory,
            potion_inventory,
            output_dir=players_dir,
            portrait=shop_portrait(config)
        )

    # Generate random merchants for GM
    if settings['random_merchants']:
        print("\n" + "="*60)
        print("GENERATING RANDOM MERCHANTS FOR GM")
        print("="*60)

        # Load NPC generator for random merchant names
        from avtools.npcs import generate_npc, format_npc_narrative

        # Simple name lists for random merchants
        first_names = [
            "Aldric", "Brenna", "Cedric", "Dara", "Eldon", "Fiona", "Gareth", "Hilda",
            "Ivor", "Jana", "Kael", "Lyra", "Milo", "Nessa", "Orin", "Petra",
            "Quinn", "Rolf", "Sable", "Thane", "Una", "Vex", "Wren", "Xander"
        ]
        last_names = [
            "Ashwood", "Blackstone", "Copperfield", "Darkwater", "Emberforge", "Frostwind",
            "Goldleaf", "Hawthorne", "Ironside", "Jadeheart", "Keenedge", "Lightfoot",
            "Moonwhisper", "Nightshade", "Oakenshield", "Proudfoot", "Quicksilver", "Ravencrest",
            "Silverstream", "Thornblade", "Underhill", "Valorheart", "Windrunner", "Youngblood"
        ]

        for merchant_num in range(1, settings['random_merchants'] + 1):
            print(f"\n[{len(selected) + merchant_num}/{total}] Generating random merchant {merchant_num}...")

            # Generate random NPC
            npc = generate_npc()
            npc_name = f"{random.choice(first_names)} {random.choice(last_names)}"
            npc_background = format_npc_narrative(npc)
            merchant_name = f"Traveling Merchant {merchant_num}: {npc_name}"

            # Random specialty
            specialties_pool = [
                "General goods and supplies",
                "Weapons and armor",
                "Magical items and curiosities",
                "Alchemical items and potions",
                "Books and scrolls",
                "Food and provisions",
                "Tools and equipment",
                "Rare and exotic goods"
            ]
            specialty = random.choice(specialties_pool)

            # Generate inventory - all categories, mostly common
            num_rare = random.randint(*settings['random_rare'])

            all_categories = ['weapon', 'armor', 'adventuring', 'alchemical', 'magical']
            inventory = generate_merchant_inventory(
                equipment,
                categories=all_categories,
                num_common=random.randint(*settings['random_common']),
                num_uncommon=random.randint(*settings['random_uncommon']),
                item_filter=None
            )

            # Add rare items
            if num_rare > 0:
                rare_pool = [e for e in equipment if e['kind'] in all_categories and e['rarity'] == 'rare']
                if rare_pool:
                    inventory['rare'] = random.sample(rare_pool, min(num_rare, len(rare_pool)))
                    print(f"  * Added {len(inventory['rare'])} rare item(s)")

            # Generate potion inventory for random merchants too
            potion_inventory = generate_potion_inventory(
                equipment, player_level, settings['potions'], settings['potion_level_offset']
            )
            print(f"  Added {len(potion_inventory)} healing potions (at least 1 Spell Slot Restoration)")

            # Write to GM directory
            write_merchant_with_header(
                merchant_name,
                f"A traveling merchant encountered during an encounter. {npc_background}",
                f"{npc_name} ({npc['race']} {npc['profession']})",
                specialty,
                inventory,
                services=[
                    "Negotiable prices (GM discretion)",
                    "May have rumors or information to share",
                    "Willing to trade for interesting items"
                ],
                spell_inventory=None,
                rune_inventory=None,
                potion_inventory=potion_inventory,
                output_dir=gm_dir,
                filename=traveling_merchant_filename(merchant_num)
            )

        # A restock replaces the whole set of traveling merchants, so drop any
        # slots past this run's count (and the old random_merchant_* files).
        for name in os.listdir(gm_dir):
            slot = TRAVELING_FILE.match(name)
            if (slot and int(slot.group(1)) > settings['random_merchants']) or name.startswith('random_merchant_'):
                os.remove(os.path.join(gm_dir, name))

    print("\nOK All merchants generated!")

if __name__ == "__main__":
    import sys

    # Usage: python3 -m avtools.merchants [LEVEL] [--level N] [--tm SHOP] [--settings-json JSON] [--output-root DIR]
    raw_settings = {}
    output_root = PROJECT_ROOT
    test_merchant = None  # Test mode: generate only one merchant

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        arg = args[i]
        has_value = i + 1 < len(args)
        if arg == '--level' and has_value:
            try:
                raw_settings['player_level'] = int(args[i + 1])
            except ValueError:
                print(f"Invalid level: {args[i + 1]}, using default level 4")
            i += 2
        elif arg in ['--tm', '-tm'] and has_value:
            test_merchant = merchant_slug(args[i + 1])
            i += 2
        elif arg == '--settings-json' and has_value:
            raw_settings.update(json.loads(args[i + 1]))
            i += 2
        elif arg == '--output-root' and has_value:
            output_root = args[i + 1]
            i += 2
        else:
            # Accept bare number as player level
            try:
                raw_settings['player_level'] = int(arg)
            except ValueError:
                pass
            i += 1

    if test_merchant:
        known = [merchant_slug(c['name']) for c in MERCHANT_CONFIGS]
        if test_merchant not in known:
            print(f"ERROR: Merchant '{test_merchant}' not found!")
            print(f"Available merchants:")
            for slug in known:
                print(f"  - {slug}")
            sys.exit(1)
        print(f"TEST MODE: Only generating {test_merchant}\n")
        raw_settings['merchants'] = [test_merchant]
        raw_settings['random_merchants'] = 0

    generate_all(normalize_settings(raw_settings), output_root)
