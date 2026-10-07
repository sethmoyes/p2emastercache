#!/usr/bin/env python3
"""
Unified Otari Merchant Generator
Generates merchant inventories with images scraped from Google Images
"""
import random
import re
import os
import urllib.parse
import json
import requests
from bs4 import BeautifulSoup
import time

def load_equipment_json(filename):
    """Load equipment from JSON file"""
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_spells_json(filename):
    """Load spells from JSON file"""
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

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

def clean_item_name(name):
    """Clean item name for search - remove everything after special chars/numbers"""
    # Remove parentheses and everything inside
    name = re.sub(r'\([^)]*\)', '', name)
    # Remove everything after first digit
    name = re.split(r'\d', name)[0]
    # Remove special characters except spaces, hyphens, apostrophes
    name = re.sub(r'[^a-zA-Z\s\'-]', '', name)
    # Clean up extra spaces
    name = ' '.join(name.split())
    return name.strip()

# Default merchant images to cycle through
DEFAULT_MERCHANT_IMAGES = [
    "https://2e.aonprd.com/Images/Monsters/Merchant.webp",
    "https://2e.aonprd.com/Images/Monsters/Guildmaster.webp",
    "https://i.redd.it/mr6j0g84qplc1.jpeg"
]

def get_merchant_image(npc_name, merchant_index=0):
    """Get merchant portrait from PathfinderWiki or use default from cycle"""
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
    except Exception as e:
        pass  # Silently fail and use default
    
    # Return default image from cycle
    return DEFAULT_MERCHANT_IMAGES[merchant_index % len(DEFAULT_MERCHANT_IMAGES)]

def try_direct_aon_image(item_name):
    """Try to construct direct AoN image URL"""
    clean_name = clean_item_name(item_name)
    
    # Try common AoN image paths
    base_url = "https://2e.aonprd.com/Images/"
    
    # Create URL-safe name: replace spaces with underscores, remove apostrophes, capitalize words
    url_name = clean_name.replace("'", "").replace(" ", "_")
    # Capitalize each word
    url_name = "_".join(word.capitalize() for word in url_name.split("_"))
    
    # Try different category paths
    categories = [
        f"Weapons/{url_name}.webp",
        f"Armor/{url_name}.webp",
        f"Equipment/{url_name}.webp",
        f"Items/{url_name}.webp",
        f"Treasure/{url_name}.webp",
    ]
    
    for category in categories:
        url = base_url + category
        try:
            response = requests.head(url, timeout=2)
            if response.status_code == 200:
                return url
        except:
            pass
    
    return None

def get_image_from_aon(item_name):
    """Search Google Images for item and return first result URL"""
    # First try direct AoN URLs
    direct_url = try_direct_aon_image(item_name)
    if direct_url:
        return direct_url
    
    try:
        clean_name = clean_item_name(item_name)
        # Use the exact query format: "2e.aonprd.com: item name"
        search_query = f"2e.aonprd.com: {clean_name}"
        encoded_query = urllib.parse.quote_plus(search_query)
        
        # Use Google Images search
        search_url = f"https://www.google.com/search?q={encoded_query}&tbm=isch"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        
        # Extract first image URL from response
        # Look for the "ou" (original URL) pattern in Google Images JSON
        img_pattern = r'"ou":"(https?://[^"]+)"'
        matches = re.findall(img_pattern, response.text)
        
        if matches:
            # Filter for 2e.aonprd.com images first
            aon_matches = [m for m in matches if '2e.aonprd.com' in m.lower()]
            if aon_matches:
                return aon_matches[0]
            # Return first match if no AoN images
            return matches[0]
        
        # Fallback: try to find any 2e.aonprd.com image URL directly
        img_pattern2 = r'https?://2e\.aonprd\.com/[^\s<>"]+?\.(?:jpg|jpeg|png|webp|gif)'
        matches2 = re.findall(img_pattern2, response.text, re.IGNORECASE)
        
        if matches2:
            return matches2[0]
            
    except Exception as e:
        pass  # Silently fail

    return None

# Image lookups are most of a run's time; settings can turn them off for a fast restock
FETCH_IMAGES = True
FETCH_PORTRAITS = True

def item_image(item_name, label):
    """Look up an item's image (rate limited), or return None when lookups are off"""
    if not FETCH_IMAGES:
        return None
    image_url = get_image_from_aon(item_name)
    print(f"{label}... {'OK' if image_url else 'X'}")
    time.sleep(0.3)  # Rate limiting
    return image_url

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

def generate_potion_inventory(equipment, player_level, count_range=(3, 6), level_offset=-3):
    """Generate healing potions for merchant

    Args:
        equipment: List of all equipment items
        player_level: Current player level
        count_range: (min, max) number of potions
        level_offset: Minimum potion level relative to player level

    Returns:
        List of potions, with at least 1 Spell Slot Restoration Potion
    """
    # Calculate minimum potion level (player_level + offset, minimum 1)
    min_potion_level = max(1, player_level + level_offset)
    
    # Get all healing potions and spell slot restoration potions
    healing_potions = [e for e in equipment if 'Healing Potion' in e['name'] and e['level'] >= min_potion_level]
    spell_slot_potions = [e for e in equipment if 'Spell Slot Restoration Potion' in e['name'] and e['level'] >= min_potion_level]
    
    num_potions = random.randint(*count_range)

    # Always include at least 1 Spell Slot Restoration Potion
    potions = []
    if spell_slot_potions and num_potions > 0:
        potions.append(random.choice(spell_slot_potions))
    
    # Fill remaining slots with random mix of healing and spell slot potions
    all_potions = healing_potions + spell_slot_potions
    remaining = num_potions - len(potions)
    
    if all_potions and remaining > 0:
        # Sample with replacement to allow duplicates
        for _ in range(remaining):
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
    common_pool = [e for e in equipment if e['type'] in categories and e['rarity'] == 'common']
    uncommon_pool = [e for e in equipment if e['type'] in categories and e['rarity'] == 'uncommon']
    
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

def write_merchant_with_header(merchant_name, description, proprietor, specialties, inventory, services=None, spell_inventory=None, rune_inventory=None, potion_inventory=None, output_dir='players', merchant_index=0):
    """Write merchant file with header, proprietor image, and full item details"""
    filename = merchant_name.lower().replace(' ', '_').replace("'", '') + '.md'
    filepath = os.path.join(output_dir, filename)
    
    # Get merchant image
    if FETCH_PORTRAITS:
        print(f"  Fetching merchant portrait...", end=' ')
        merchant_img = get_merchant_image(proprietor, merchant_index)
        print(f"OK" if "pathfinderwiki" in merchant_img else "Using default")
    else:
        merchant_img = DEFAULT_MERCHANT_IMAGES[merchant_index % len(DEFAULT_MERCHANT_IMAGES)]

    # Write to a temp file and swap it in, so the live site never serves a half-written shop
    tmp_path = filepath + '.tmp'
    with open(tmp_path, 'w', encoding='utf-8') as f:
        # Header with proprietor image (small size - 250px)
        f.write(f"# {merchant_name}\n\n")
        f.write(f"<div align=\"center\">\n\n")
        f.write(f"<img src=\"{merchant_img}\" alt=\"Proprietor\" width=\"250\">\n\n")
        f.write(f"</div>\n\n")
        f.write(f"*{description}*\n\n")
        f.write(f"**Proprietor:** {proprietor}\n\n")
        f.write(f"**Specialties:** {specialties}\n\n")
        
        # Potion section (if applicable) - ALWAYS FIRST
        if potion_inventory:
            f.write("---\n\n")
            f.write("# HEALING POTIONS\n\n")
            f.write("*These potions restore Hit Points or spell slots when consumed.*\n\n")
            f.write("| Image | Name | Level | Price | Effect | Link |\n")
            f.write("|-------|------|-------|-------|--------|------|\n")
            
            total = len(potion_inventory)
            for idx, potion in enumerate(potion_inventory, 1):
                image_url = item_image(potion['name'], f"  [POTION {idx}/{total}] {potion['name'][:50]}")
                
                # Fix and capitalize fields
                name = potion['name']
                level = potion['level']
                price = fix_price(potion['price'])
                effect = potion.get('effect', 'N/A')
                
                # Create image markdown
                if image_url:
                    img_md = f"![{name}]({image_url})"
                else:
                    img_md = "🖼️"
                
                # Create AoN search link
                search_url = f"https://2e.aonprd.com/Search.aspx?query={urllib.parse.quote(clean_item_name(name))}"
                link_md = f"[View]({search_url})"
                
                f.write(f"| {img_md} | {name} | {level} | {price} | {effect} | {link_md} |\n")
            
            f.write("\n")
            f.write("---\n\n")
        
        # Spell scrolls section (if applicable)
        if spell_inventory:
            f.write("---\n\n")
            f.write("# SPELL SCROLLS FOR LEARNING\n\n")
            f.write("*These scrolls can be studied with the merchant to permanently learn the spell.*\n\n")
            f.write("*Study time: 1 hour (common), 5 hours (uncommon), 1 day (rare).*\n\n")
            
            # Common spells
            if spell_inventory['common']:
                f.write(f"## Common Spell Scrolls ({len(spell_inventory['common'])})\n\n")
                f.write("| Spell Name | Level | Price | DC | Traditions | Range | Traits | Link |\n")
                f.write("|------------|-------|-------|-------|------------|-------|--------|------|\n")
                
                for spell in spell_inventory['common']:
                    spell_name = f"SCROLL OF {spell['name'].upper()}"
                    level = spell['level']
                    price, dc = get_spell_price_and_dc(level)
                    traditions = ', '.join(spell.get('traditions', ['N/A']))
                    spell_range = spell.get('range', 'N/A')
                    traits = ', '.join(spell.get('traits', [])[:3])  # Limit to 3 traits
                    if not traits:
                        traits = 'N/A'
                    
                    # Create AoN link
                    if spell.get('url'):
                        link_md = f"[View](https://2e.aonprd.com{spell['url']})"
                    else:
                        search_url = f"https://2e.aonprd.com/Search.aspx?query={urllib.parse.quote(spell['name'])}"
                        link_md = f"[View]({search_url})"
                    
                    f.write(f"| {spell_name} | {level} | {price} | {dc} | {traditions} | {spell_range} | {traits} | {link_md} |\n")
                
                f.write("\n")
            
            # Uncommon spells
            if spell_inventory['uncommon']:
                f.write(f"## Uncommon Spell Scrolls ({len(spell_inventory['uncommon'])})\n\n")
                f.write("| Spell Name | Level | Price | DC | Traditions | Range | Traits | Link |\n")
                f.write("|------------|-------|-------|-------|------------|-------|--------|------|\n")
                
                for spell in spell_inventory['uncommon']:
                    spell_name = f"SCROLL OF {spell['name'].upper()}"
                    level = spell['level']
                    price, dc = get_spell_price_and_dc(level)
                    traditions = ', '.join(spell.get('traditions', ['N/A']))
                    spell_range = spell.get('range', 'N/A')
                    traits = ', '.join(spell.get('traits', [])[:3])
                    if not traits:
                        traits = 'N/A'
                    
                    if spell.get('url'):
                        link_md = f"[View](https://2e.aonprd.com{spell['url']})"
                    else:
                        search_url = f"https://2e.aonprd.com/Search.aspx?query={urllib.parse.quote(spell['name'])}"
                        link_md = f"[View]({search_url})"
                    
                    f.write(f"| {spell_name} | {level} | {price} | {dc} | {traditions} | {spell_range} | {traits} | {link_md} |\n")
                
                f.write("\n")
            
            # Rare spells
            if spell_inventory['rare']:
                f.write(f"## Rare Spell Scrolls ({len(spell_inventory['rare'])})\n\n")
                f.write("| Spell Name | Level | Price | DC | Traditions | Range | Traits | Link |\n")
                f.write("|------------|-------|-------|-------|------------|-------|--------|------|\n")
                
                for spell in spell_inventory['rare']:
                    spell_name = f"SCROLL OF {spell['name'].upper()}"
                    level = spell['level']
                    price, dc = get_spell_price_and_dc(level)
                    traditions = ', '.join(spell.get('traditions', ['N/A']))
                    spell_range = spell.get('range', 'N/A')
                    traits = ', '.join(spell.get('traits', [])[:3])
                    if not traits:
                        traits = 'N/A'
                    
                    if spell.get('url'):
                        link_md = f"[View](https://2e.aonprd.com{spell['url']})"
                    else:
                        search_url = f"https://2e.aonprd.com/Search.aspx?query={urllib.parse.quote(spell['name'])}"
                        link_md = f"[View]({search_url})"
                    
                    f.write(f"| {spell_name} | {level} | {price} | {dc} | {traditions} | {spell_range} | {traits} | {link_md} |\n")
                
                f.write("\n")
            
            f.write("---\n\n")
        
        # Rune section (if applicable)
        if rune_inventory:
            f.write("# RUNES\n\n")
            f.write("*Runes can be etched onto weapons and armor to enhance their properties.*\n\n")
            
            # Fundamental weapon runes (always available, 2-3 of each)
            if rune_inventory['fundamental']:
                # Count quantities
                rune_counts = {}
                for rune in rune_inventory['fundamental']:
                    rune_name = rune['name']
                    if rune_name not in rune_counts:
                        rune_counts[rune_name] = {'count': 0, 'rune': rune}
                    rune_counts[rune_name]['count'] += 1
                
                f.write(f"## Fundamental Weapon Runes (Always Available)\n\n")
                f.write("| Image | Name | Quantity | Level | Price | Rarity | Link |\n")
                f.write("|-------|------|----------|-------|-------|--------|------|\n")
                
                for rune_name, data in rune_counts.items():
                    rune = data['rune']
                    quantity = data['count']
                    
                    image_url = item_image(rune['name'], f"  [RUNE] {rune['name'][:50]}")
                    
                    # Fix and capitalize fields
                    name = rune['name']
                    level = rune['level']
                    price = fix_price(rune['price'])
                    rarity = capitalize_field(rune['rarity'])
                    
                    # Create image markdown
                    if image_url:
                        img_md = f"![{name}]({image_url})"
                    else:
                        img_md = "🖼️"
                    
                    # Create AoN search link
                    search_url = f"https://2e.aonprd.com/Search.aspx?query={urllib.parse.quote(clean_item_name(name))}"
                    link_md = f"[View]({search_url})"
                    
                    f.write(f"| {img_md} | {name} | {quantity} | {level} | {price} | {rarity} | {link_md} |\n")
                
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
            
            # Other runes (2-7 random)
            if rune_inventory['other']:
                f.write(f"## Property Runes ({len(rune_inventory['other'])})\n\n")
                f.write("| Image | Name | Level | Price | Rarity | Link |\n")
                f.write("|-------|------|-------|-------|--------|------|\n")
                
                total = len(rune_inventory['other'])
                for idx, rune in enumerate(rune_inventory['other'], 1):
                    image_url = item_image(rune['name'], f"  [RUNE {idx}/{total}] {rune['name'][:50]}")
                    
                    # Fix and capitalize fields
                    name = rune['name']
                    level = rune['level']
                    price = fix_price(rune['price'])
                    rarity = capitalize_field(rune['rarity'])
                    
                    # Create image markdown
                    if image_url:
                        img_md = f"![{name}]({image_url})"
                    else:
                        img_md = "🖼️"
                    
                    # Create AoN search link
                    search_url = f"https://2e.aonprd.com/Search.aspx?query={urllib.parse.quote(clean_item_name(name))}"
                    link_md = f"[View]({search_url})"
                    
                    f.write(f"| {img_md} | {name} | {level} | {price} | {rarity} | {link_md} |\n")
                
                f.write("\n")
            
            f.write("---\n\n")
        
        # Regular items section
        if inventory['common'] or inventory['uncommon'] or inventory['rare']:
            f.write("# REGULAR ITEMS\n\n")
        
        # Common items
        if inventory['common']:
            f.write(f"## Common Items ({len(inventory['common'])})\n\n")
            f.write("| Image | Name | Level | Price | Rarity | Category | Type | Link |\n")
            f.write("|-------|------|-------|-------|--------|----------|------|------|\n")
            
            total = len(inventory['common'])
            for idx, item in enumerate(inventory['common'], 1):
                # Get image URL
                image_url = item_image(item['name'], f"  [{idx}/{total}] {item['name'][:50]}")
                
                # Fix and capitalize fields
                name = item['name']
                level = item['level']
                price = fix_price(item['price'])
                rarity = capitalize_field(item['rarity'])
                category = capitalize_field(item.get('category', 'N/A'))
                item_type = capitalize_field(item['type'])
                
                # Create image markdown
                if image_url:
                    img_md = f"![{name}]({image_url})"
                else:
                    img_md = "🖼️"  # Placeholder icon if no image
                
                # Create AoN search link
                search_url = f"https://2e.aonprd.com/Search.aspx?query={urllib.parse.quote(clean_item_name(name))}"
                link_md = f"[View]({search_url})"
                
                f.write(f"| {img_md} | {name} | {level} | {price} | {rarity} | {category} | {item_type} | {link_md} |\n")
            
            f.write("\n")
        
        # Uncommon items
        if inventory['uncommon']:
            f.write(f"## Uncommon Items ({len(inventory['uncommon'])})\n\n")
            f.write("| Image | Name | Level | Price | Rarity | Category | Type | Link |\n")
            f.write("|-------|------|-------|-------|--------|----------|------|------|\n")
            
            total = len(inventory['uncommon'])
            for idx, item in enumerate(inventory['uncommon'], 1):
                # Get image URL
                image_url = item_image(item['name'], f"  [{idx}/{total}] {item['name'][:50]}")
                
                # Fix and capitalize fields
                name = item['name']
                level = item['level']
                price = fix_price(item['price'])
                rarity = capitalize_field(item['rarity'])
                category = capitalize_field(item.get('category', 'N/A'))
                item_type = capitalize_field(item['type'])
                
                # Create image markdown
                if image_url:
                    img_md = f"![{name}]({image_url})"
                else:
                    img_md = "🖼️"
                
                # Create AoN search link
                search_url = f"https://2e.aonprd.com/Search.aspx?query={urllib.parse.quote(clean_item_name(name))}"
                link_md = f"[View]({search_url})"
                
                f.write(f"| {img_md} | {name} | {level} | {price} | {rarity} | {category} | {item_type} | {link_md} |\n")
            
            f.write("\n")
        
        # Rare items
        if inventory['rare']:
            f.write(f"## Rare Items ({len(inventory['rare'])})\n\n")
            f.write("| Image | Name | Level | Price | Rarity | Category | Type | Link |\n")
            f.write("|-------|------|-------|-------|--------|----------|------|------|\n")
            
            total = len(inventory['rare'])
            for idx, item in enumerate(inventory['rare'], 1):
                # Get image URL
                image_url = item_image(item['name'], f"  [{idx}/{total}] {item['name'][:50]}")
                
                # Fix and capitalize fields
                name = item['name']
                level = item['level']
                price = fix_price(item['price'])
                rarity = capitalize_field(item['rarity'])
                category = capitalize_field(item.get('category', 'N/A'))
                item_type = capitalize_field(item['type'])
                
                # Create image markdown
                if image_url:
                    img_md = f"![{name}]({image_url})"
                else:
                    img_md = "🖼️"
                
                # Create AoN search link
                search_url = f"https://2e.aonprd.com/Search.aspx?query={urllib.parse.quote(clean_item_name(name))}"
                link_md = f"[View]({search_url})"
                
                f.write(f"| {img_md} | {name} | {level} | {price} | {rarity} | {category} | {item_type} | {link_md} |\n")
            
            f.write("\n")
        
        # Services section
        if services:
            f.write("## Services\n\n")
            for service in services:
                f.write(f"- {service}\n")
            f.write("\n")

    os.replace(tmp_path, filepath)
    print(f"OK Created: {filepath}")

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

def merchant_slug(name):
    """File name (without .md) a merchant is written to"""
    return name.lower().replace(' ', '_').replace("'", '')

# The ten Otari shops. Order matters: a shop's position picks its default portrait.
MERCHANT_CONFIGS = [
    # 1. Otari Market - All types, DOUBLE items
    {
        'name': 'Otari Market',
        'description': 'Large open-air market with diverse goods',
        'proprietor': 'Keeleno Lathenar (dour, humorless human merchant)',
        'specialties': 'All adventuring gear, weapons, armor, and general supplies',
        'categories': ['weapon', 'armor', 'adventuring', 'alchemical', 'magical'],
        'item_filter': None,  # No restrictions
        'double_items': True,  # Market uses the market_* stock settings
        'services': None
    },
    # 2. Wrin's Wonders - Magical items, spells, scrolls, staffs, spellhearts, runes, alchemical potions
    {
        'name': "Wrin's Wonders",
        'description': 'Eccentric tiefling-elf oddities merchant and stargazer',
        'proprietor': 'Wrin Sivinxi (CG female tiefling elf oddities merchant 5)',
        'specialties': 'Magical items, spells, scrolls, staffs, spellhearts, runes, and alchemical potions',
        'categories': ['magical', 'alchemical', 'adventuring'],  # Added adventuring for staffs and runes!
        'item_filter': lambda item: (
            # Check item_category field for Runes
            item.get('item_category') == 'Runes' or
            # Check for Staff of X pattern (magical staffs)
            'staff of' in item['name'].lower() or
            # Check name for specific magical items
            any(keyword in item['name'].lower() for keyword in [
                'scroll', 'spellheart', 'potion', 'elixir',
                'wand', 'talisman', 'amulet', 'ring', 'cloak', 'boots', 'gloves', 'hat', 'circlet'
            ])
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
    # 3. Odd Stories - Books, magical items, runes, spells
    {
        'name': 'Odd Stories',
        'description': 'Bookshop and scroll emporium',
        'proprietor': 'Morlibint (NG male gnome bookseller 3)',
        'specialties': 'Books, scrolls, magical items, runes, and spells',
        'categories': ['magical', 'adventuring'],
        'item_filter': lambda item: (
            # Check item_category field for Runes
            item.get('item_category') == 'Runes' or
            # Check for Staff of X pattern (magical staffs)
            'staff of' in item['name'].lower() or
            # Check name for books and magical items
            any(keyword in item['name'].lower() for keyword in [
                'book', 'scroll', 'tome', 'manual', 'grimoire', 'spell',
                'wand', 'talisman'
            ])
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
    # 4. Gallentine Deliveries - Service only (no inventory)
    {
        'name': 'Gallentine Deliveries',
        'description': 'Courier and delivery service',
        'proprietor': 'Gallentine (N female human courier 2)',
        'specialties': 'Package delivery, message running, and escort services',
        'categories': [],
        'item_filter': None,
        'double_items': False,
        'services': [
            "Local delivery (within Otari): 1 sp per package",
            "Regional delivery (to nearby towns): 5 sp - 2 gp depending on distance",
            "Long-distance delivery: Price negotiable (GM discretion)",
            "Escort services: 5 gp per day",
            "Rush delivery: Double normal price"
        ]
    },
    # 5. Blades for Glades - Weapons, armor, and shields ONLY
    {
        'name': 'Blades for Glades',
        'description': 'Weaponsmith and armorer',
        'proprietor': 'Jorsk Hinterclaw (LN male dwarf weaponsmith 4)',
        'specialties': 'Weapons, armor, and shields of all types',
        'categories': ['weapon', 'armor'],
        'item_filter': None,  # Category filter is sufficient
        'double_items': False,
        'services': [
            "Weapon sharpening: 5 sp",
            "Armor repair: 1-5 gp depending on damage",
            "Custom weapon crafting: Price negotiable (GM discretion)",
            "Weapon engraving: 1 gp"
        ]
    },
    # 6. Crow's Casks - Tea, oils, food, beverages, alchemical items (potions)
    {
        'name': "Crow's Casks",
        'description': 'Tavern specializing in teas, oils, and fine beverages',
        'proprietor': 'Crow (CN female human tavernkeeper 2)',
        'specialties': 'Tea, oils, food, beverages, and alchemical potions',
        'categories': ['adventuring', 'alchemical'],
        'item_filter': lambda item: any(keyword in item['name'].lower() for keyword in [
            'tea', 'oil', 'food', 'ration', 'meal', 'drink', 'beverage', 'wine', 'ale',
            'beer', 'mead', 'potion', 'elixir', 'tonic', 'brew'
        ]),
        'double_items': False,
        'services': [
            "Meals: 1 cp (poor) to 1 gp (fine)",
            "Lodging: 3 cp (floor space) to 5 sp (private room)",
            "Ale/Wine: 1 cp (mug) to 1 sp (bottle)",
            "Rumors and information: Free with purchase"
        ]
    },
    # 7. Crook's Nook - Snares, tattoos, consumables
    {
        'name': "Crook's Nook",
        'description': 'Seedy tavern dealing in traps and questionable goods',
        'proprietor': 'Crook (NE male half-orc tavernkeeper 3)',
        'specialties': 'Snares, tattoos, and consumable items',
        'categories': ['adventuring', 'alchemical', 'magical'],
        'item_filter': lambda item: any(keyword in item['name'].lower() for keyword in [
            'snare', 'trap', 'tattoo', 'potion', 'elixir', 'oil', 'tonic', 'consumable',
            'bomb', 'poison', 'drug', 'talisman', 'scroll'
        ]),
        'double_items': False,
        'services': [
            "Meals: 1 cp (poor quality)",
            "Lodging: 3 cp (floor space) to 3 sp (shared room)",
            "Ale: 1 cp (watered down)",
            "Black market contacts: 5-50 gp (GM discretion)"
        ]
    },
    # 8. The Rowdy Rockfish - All items EXCEPT weapons/armor/shields
    {
        'name': 'The Rowdy Rockfish',
        'description': 'Lively tavern and general store',
        'proprietor': 'Tamily Tanderveil (CG female halfling innkeeper 4)',
        'specialties': 'General goods, supplies, and adventuring gear (no weapons or armor)',
        'categories': ['adventuring', 'alchemical', 'magical'],
        'item_filter': lambda item: not any(keyword in item['name'].lower() for keyword in [
            'sword', 'axe', 'mace', 'hammer', 'spear', 'bow', 'crossbow', 'dagger', 'knife',
            'armor', 'shield', 'breastplate', 'chainmail', 'plate', 'helmet', 'gauntlet'
        ]) and item['type'] not in ['weapon', 'armor'],
        'double_items': False,
        'services': [
            "Meals: 5 cp (square) to 2 gp (fine)",
            "Lodging: 5 cp (bed) to 1 gp (private room with bath)",
            "Ale/Wine: 1 cp (mug) to 5 sp (fine bottle)",
            "Entertainment: Free nightly performances",
            "Hot bath: 2 cp"
        ]
    },
    # 9. Otari Fishery - Food and beverages ONLY
    {
        'name': 'Otari Fishery',
        'description': 'Fresh fish and fishing supplies',
        'proprietor': 'Lillia Dusklight (NG female human fisher 2)',
        'specialties': 'Fresh fish, food, and beverages',
        'categories': ['adventuring'],
        'item_filter': lambda item: any(keyword in item['name'].lower() for keyword in [
            'fish', 'food', 'ration', 'meal', 'drink', 'beverage', 'water', 'ale', 'wine'
        ]),
        'double_items': False,
        'services': [
            "Fresh fish: 1 cp - 5 sp depending on type",
            "Fishing lessons: 5 sp per hour",
            "Boat rental: 5 sp per day",
            "Net repair: 1 sp"
        ]
    },
    # 10. Dawnflower Library - Books, scrolls, runes ONLY
    {
        'name': 'Dawnflower Library',
        'description': 'Temple library and scriptorium',
        'proprietor': 'Vandy Banderdash (LG female halfling cleric of Sarenrae 5)',
        'specialties': 'Religious texts, scrolls, and runes',
        'categories': ['magical', 'adventuring'],
        'item_filter': lambda item: (
            # Check item_category field for Runes (this is the key fix!)
            item.get('item_category') == 'Runes' or
            # Check name for books and scrolls
            any(keyword in item['name'].lower() for keyword in [
                'book', 'scroll', 'tome', 'manual', 'text', 'grimoire', 'scripture'
            ])
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
    {'group': 'Basics', 'key': 'fetch_images', 'type': 'bool', 'default': False,
     'label': 'Look up item images',
     'help': 'Searches the web for every item, which adds several minutes. '
             'When off, items show a placeholder.'},
    {'group': 'Shops to restock', 'key': 'merchants', 'type': 'merchants',
     'default': [merchant_slug(c['name']) for c in MERCHANT_CONFIGS],
     'label': 'Shops', 'help': 'Unchecked shops keep their current stock.'},
    {'group': 'Shop stock', 'key': 'common', 'type': 'range', 'default': [3, 15], 'min': 0, 'max': 100,
     'label': 'Common items per shop'},
    {'group': 'Shop stock', 'key': 'uncommon', 'type': 'range', 'default': [1, 3], 'min': 0, 'max': 100,
     'label': 'Uncommon items per shop'},
    {'group': 'Shop stock', 'key': 'rare_shops', 'type': 'int', 'default': 2, 'min': 0, 'max': 9,
     'label': 'Shops that get 1 rare item',
     'help': 'Picked at random from the checked shops. Otari Market rolls its own rares.'},
    {'group': 'Otari Market', 'key': 'market_common', 'type': 'range', 'default': [20, 50], 'min': 0, 'max': 200,
     'label': 'Common items'},
    {'group': 'Otari Market', 'key': 'market_uncommon', 'type': 'range', 'default': [5, 15], 'min': 0, 'max': 100,
     'label': 'Uncommon items'},
    {'group': 'Otari Market', 'key': 'market_rare', 'type': 'range', 'default': [1, 3], 'min': 0, 'max': 20,
     'label': 'Rare items'},
    {'group': 'Spells & runes', 'key': 'spells_common', 'type': 'range', 'default': [5, 15], 'min': 0, 'max': 100,
     'label': 'Common spell scrolls', 'help': "Wrin's Wonders and Odd Stories."},
    {'group': 'Spells & runes', 'key': 'spells_uncommon', 'type': 'range', 'default': [3, 5], 'min': 0, 'max': 50,
     'label': 'Uncommon spell scrolls'},
    {'group': 'Spells & runes', 'key': 'rare_spell', 'type': 'bool', 'default': True,
     'label': 'One spell shop gets a rare spell'},
    {'group': 'Spells & runes', 'key': 'fundamental_runes', 'type': 'range', 'default': [2, 3], 'min': 0, 'max': 10,
     'label': 'Copies of each fundamental rune',
     'help': "Wrin's Wonders, Odd Stories and Dawnflower Library."},
    {'group': 'Spells & runes', 'key': 'property_runes', 'type': 'range', 'default': [1, 3], 'min': 0, 'max': 20,
     'label': 'Property runes'},
    {'group': 'Potions', 'key': 'potions', 'type': 'range', 'default': [3, 6], 'min': 0, 'max': 20,
     'label': 'Healing potions per shop', 'help': 'At least one is a Spell Slot Restoration Potion.'},
    {'group': 'Potions', 'key': 'potion_level_offset', 'type': 'int', 'default': -3, 'min': -20, 'max': 5,
     'label': 'Min potion level (party level +)', 'help': 'Never below level 1.'},
    {'group': TRAVELING, 'key': 'random_merchants', 'type': 'int', 'default': 2, 'min': 0, 'max': 10,
     'label': 'Traveling merchants to create',
     'help': 'Added to the Random Merchants list on the GM page. Earlier ones are kept.'},
    {'group': TRAVELING, 'key': 'random_common', 'type': 'range', 'default': [5, 12], 'min': 0, 'max': 100,
     'label': 'Common items'},
    {'group': TRAVELING, 'key': 'random_uncommon', 'type': 'range', 'default': [1, 4], 'min': 0, 'max': 50,
     'label': 'Uncommon items'},
    {'group': TRAVELING, 'key': 'random_rare', 'type': 'range', 'default': [0, 2], 'min': 0, 'max': 20,
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

def generate_all(settings, output_root=PROJECT_ROOT):
    """Restock the selected Otari shops (players/) and create traveling merchants (gm/)"""
    global FETCH_IMAGES, FETCH_PORTRAITS
    FETCH_IMAGES = settings['fetch_images']
    FETCH_PORTRAITS = settings['fetch_portraits']

    player_level = settings['player_level']
    max_item_level = player_level + settings['item_level_offset']
    spell_level = player_level + settings['spell_level_offset']
    selected = [c for c in MERCHANT_CONFIGS if merchant_slug(c['name']) in settings['merchants']]
    total = len(selected) + settings['random_merchants']

    print(f"Generating merchants for player level {player_level}")
    print(f"  Max item level: {max_item_level}")
    print(f"  Max spell level: {spell_level}")
    print(f"  Item images: {'on' if FETCH_IMAGES else 'off'}, portraits: {'on' if FETCH_PORTRAITS else 'off'}")
    print()

    print("Loading equipment...")
    equipment = load_equipment_json(os.path.join(PROJECT_ROOT, 'etc', 'equipment.json'))

    # Filter equipment by max level
    equipment = [e for e in equipment if e['level'] <= max_item_level]
    print(f"  Loaded {len(equipment)} items (level {max_item_level} or below)")

    print("Loading spells...")
    spells = load_spells_json(os.path.join(PROJECT_ROOT, 'etc', 'spells.json'))
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
                rare_pool = [e for e in equipment if e['type'] in config['categories'] and e['rarity'] == 'rare']
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
            merchant_index=MERCHANT_CONFIGS.index(config)
        )

    # Generate random merchants for GM
    if settings['random_merchants']:
        print("\n" + "="*60)
        print("GENERATING RANDOM MERCHANTS FOR GM")
        print("="*60)

        # Load NPC generator for random merchant names
        from generate_npc_lore import generate_npc, format_npc_narrative

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
            merchant_name = f"Random Merchant {merchant_num}: {npc_name}"

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
                rare_pool = [e for e in equipment if e['type'] in all_categories and e['rarity'] == 'rare']
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
                merchant_index=10 + merchant_num  # Random merchants cycle portraits after the shops
            )

    print("\nOK All merchants generated!")

if __name__ == "__main__":
    import sys

    # Usage: generate_merchants.py [LEVEL] [--level N] [--tm SHOP] [--settings-json JSON] [--output-root DIR]
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
