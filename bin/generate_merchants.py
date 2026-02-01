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

def generate_merchant_inventory(equipment, categories, num_common, num_uncommon, item_filter=None):
    """Generate random inventory from equipment (max level 6)
    
    Args:
        equipment: List of all equipment items
        categories: List of category types (weapon, armor, etc.)
        num_common: Number of common items to generate
        num_uncommon: Number of uncommon items to generate
        item_filter: Optional function to further filter items beyond category
    """
    inventory = {'common': [], 'uncommon': [], 'rare': []}
    
    # Filter by categories, rarity, AND level (max 6)
    common_pool = [e for e in equipment if e['type'] in categories and e['rarity'] == 'common' and e['level'] <= 6]
    uncommon_pool = [e for e in equipment if e['type'] in categories and e['rarity'] == 'uncommon' and e['level'] <= 6]
    
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

def write_merchant_with_header(merchant_name, description, proprietor, specialties, inventory, services=None, output_dir='players'):
    """Write merchant file with header, proprietor image, and full item details"""
    filename = merchant_name.lower().replace(' ', '_').replace("'", '') + '.md'
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        # Header with proprietor image
        f.write(f"# {merchant_name}\n\n")
        f.write(f"<div align=\"center\">\n\n")
        f.write(f"![Proprietor](IMAGE_PLACEHOLDER)\n\n")
        f.write(f"</div>\n\n")
        f.write(f"*{description}*\n\n")
        f.write(f"**Proprietor:** {proprietor}\n\n")
        f.write(f"**Specialties:** {specialties}\n\n")
        
        # Common items
        if inventory['common']:
            f.write(f"## Common Items ({len(inventory['common'])})\n\n")
            f.write("| Image | Name | Level | Price | Rarity | Category | Type | Link |\n")
            f.write("|-------|------|-------|-------|--------|----------|------|------|\n")
            
            total = len(inventory['common'])
            for idx, item in enumerate(inventory['common'], 1):
                # Get image URL
                print(f"  [{idx}/{total}] {item['name'][:50]}", end='... ')
                image_url = get_image_from_aon(item['name'])
                
                if image_url:
                    print(f"OK")
                else:
                    print(f"X")
                
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
                
                time.sleep(0.3)  # Rate limiting
            
            f.write("\n")
        
        # Uncommon items
        if inventory['uncommon']:
            f.write(f"## Uncommon Items ({len(inventory['uncommon'])})\n\n")
            f.write("| Image | Name | Level | Price | Rarity | Category | Type | Link |\n")
            f.write("|-------|------|-------|-------|--------|----------|------|------|\n")
            
            total = len(inventory['uncommon'])
            for idx, item in enumerate(inventory['uncommon'], 1):
                # Get image URL
                print(f"  [{idx}/{total}] {item['name'][:50]}", end='... ')
                image_url = get_image_from_aon(item['name'])
                
                if image_url:
                    print(f"OK")
                else:
                    print(f"X")
                
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
                
                time.sleep(0.3)
            
            f.write("\n")
        
        # Rare items
        if inventory['rare']:
            f.write(f"## Rare Items ({len(inventory['rare'])})\n\n")
            f.write("| Image | Name | Level | Price | Rarity | Category | Type | Link |\n")
            f.write("|-------|------|-------|-------|--------|----------|------|------|\n")
            
            total = len(inventory['rare'])
            for idx, item in enumerate(inventory['rare'], 1):
                # Get image URL
                print(f"  [{idx}/{total}] {item['name'][:50]}", end='... ')
                image_url = get_image_from_aon(item['name'])
                
                if image_url:
                    print(f"OK")
                else:
                    print(f"X")
                
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
                
                time.sleep(0.3)
            
            f.write("\n")
        
        # Services section
        if services:
            f.write("## Services\n\n")
            for service in services:
                f.write(f"- {service}\n")
            f.write("\n")
    
    print(f"OK Created: {filepath}")

if __name__ == "__main__":
    import sys
    
    # Parse command line arguments
    player_level = 4  # Default level
    if len(sys.argv) > 1:
        for i, arg in enumerate(sys.argv[1:]):
            if arg == '--level' and i + 1 < len(sys.argv) - 1:
                try:
                    player_level = int(sys.argv[i + 2])
                except ValueError:
                    print(f"Invalid level: {sys.argv[i + 2]}, using default level 4")
    
    max_item_level = player_level + 2
    
    print(f"Generating merchants for player level {player_level}")
    print(f"  Max item level: {max_item_level}")
    print()
    
    print("Loading equipment...")
    equipment = load_equipment_json("etc/equipment.json")
    
    # Filter equipment by max level
    equipment = [e for e in equipment if e['level'] <= max_item_level]
    print(f"  Loaded {len(equipment)} items (level {max_item_level} or below)")
    
    # Create output directory
    os.makedirs('players', exist_ok=True)
    
    # Randomly select 2 merchants to get rare items
    merchants_with_rares = random.sample(range(10), 2)
    print(f"  Merchants {merchants_with_rares[0]+1} and {merchants_with_rares[1]+1} will have rare items\n")
    
    merchant_configs = [
        # 1. Otari Market - All types, DOUBLE items
        {
            'name': 'Otari Market',
            'description': 'Large open-air market with diverse goods',
            'proprietor': 'Keeleno Lathenar (dour, humorless human merchant)',
            'specialties': 'All adventuring gear, weapons, armor, and general supplies',
            'categories': ['weapon', 'armor', 'adventuring', 'alchemical', 'magical'],
            'item_filter': None,  # No restrictions
            'double_items': True,  # Market has double items
            'services': None
        },
        # 2. Wrin's Wonders - Magical items, spells, scrolls, staffs, spellhearts, runes, alchemical potions
        {
            'name': "Wrin's Wonders",
            'description': 'Eccentric tiefling-elf oddities merchant and stargazer',
            'proprietor': 'Wrin Sivinxi (CG female tiefling elf oddities merchant 5)',
            'specialties': 'Magical items, spells, scrolls, staffs, spellhearts, runes, and alchemical potions',
            'categories': ['magical', 'alchemical'],
            'item_filter': lambda item: any(keyword in item['name'].lower() for keyword in [
                'scroll', 'staff', 'stave', 'spellheart', 'rune', 'potion', 'elixir', 
                'wand', 'talisman', 'amulet', 'ring', 'cloak', 'boots', 'gloves', 'hat', 'circlet'
            ]),
            'double_items': False,
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
            'item_filter': lambda item: any(keyword in item['name'].lower() for keyword in [
                'book', 'scroll', 'tome', 'manual', 'grimoire', 'rune', 'spell', 
                'wand', 'staff', 'stave', 'talisman'
            ]),
            'double_items': False,
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
            'item_filter': lambda item: any(keyword in item['name'].lower() for keyword in [
                'book', 'scroll', 'tome', 'manual', 'text', 'grimoire', 'rune', 'scripture'
            ]),
            'double_items': False,
            'services': [
                "Spellcasting Services: Price varies by spell level (GM discretion)",
                "Healing: 1-20 gp depending on severity",
                "Remove curse/disease: 10-50 gp (GM discretion)",
                "Research assistance: Free for worshippers, 2 gp per day for others",
                "Blessings: Donation-based"
            ]
        }
    ]
    
    for idx, config in enumerate(merchant_configs):
        print(f"\n[{idx+1}/10] Generating {config['name']}...")
        
        # Generate inventory with new limits
        # Otari Market gets DOUBLE items
        if config.get('double_items', False):
            num_common = random.randint(6, 30)  # Double: 3-15 becomes 6-30
            num_uncommon = random.randint(2, 6)  # Double: 1-3 becomes 2-6
        else:
            num_common = random.randint(3, 15)
            num_uncommon = random.randint(1, 3)
        
        has_rare = idx in merchants_with_rares
        
        if config['categories']:  # Skip if service-only
            inventory = generate_merchant_inventory(
                equipment,
                categories=config['categories'],
                num_common=num_common,
                num_uncommon=num_uncommon,
                item_filter=config.get('item_filter')
            )
            
            # Add rare item if this merchant was selected
            if has_rare:
                rare_pool = [e for e in equipment if e['type'] in config['categories'] and e['rarity'] == 'rare' and e['level'] <= 6]
                # Apply item filter to rare pool too
                if config.get('item_filter'):
                    rare_pool = [e for e in rare_pool if config['item_filter'](e)]
                if rare_pool:
                    inventory['rare'] = [random.choice(rare_pool)]
                    print(f"  ⭐ Added rare item!")
        else:
            inventory = {'common': [], 'uncommon': [], 'rare': []}
        
        write_merchant_with_header(
            config['name'],
            config['description'],
            config['proprietor'],
            config['specialties'],
            inventory,
            config['services']
        )
    
    print("\nOK All merchants generated!")

