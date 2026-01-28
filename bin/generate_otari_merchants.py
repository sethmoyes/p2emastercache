#!/usr/bin/env python3
"""
Generate Otari merchant inventories with separate files per merchant
Based on Abomination Vaults Player's Guide
"""
import random
import re
import os
import requests
from bs4 import BeautifulSoup
import urllib.parse
import time

def get_aon_equipment_url(item_name):
    """Search Google for Archives of Nethys equipment page URL"""
    try:
        # Clean up item name for search
        clean_name = re.sub(r'\([^)]*\)', '', item_name).strip()
        search_query = f"{clean_name} p2e archives of nethys"
        encoded_query = urllib.parse.quote(search_query)
        search_url = f"https://www.google.com/search?q={encoded_query}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(search_url, headers=headers, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for Archives of Nethys links
            for link in soup.find_all('a', href=True):
                href = link['href']
                if '2e.aonprd.com/Equipment.aspx' in href:
                    # Extract the actual URL from Google's redirect
                    match = re.search(r'(https://2e\.aonprd\.com/Equipment\.aspx\?ID=\d+)', href)
                    if match:
                        return match.group(1)
        
        # Fallback: construct a search URL
        return f"https://2e.aonprd.com/Search.aspx?query={urllib.parse.quote(clean_name)}"
    except Exception as e:
        # If search fails, return a search URL
        clean_name = re.sub(r'\([^)]*\)', '', item_name).strip()
        return f"https://2e.aonprd.com/Search.aspx?query={urllib.parse.quote(clean_name)}"

def parse_equipment_md(filename):
    """Parse equipment.md and return items by category and rarity"""
    items = {
        'weapons': {'common': [], 'uncommon': [], 'rare': []},
        'armor': {'common': [], 'uncommon': [], 'rare': []},
        'alchemical': {'common': [], 'uncommon': [], 'rare': []},
        'adventuring': {'common': [], 'uncommon': [], 'rare': []},
        'magical': {'common': [], 'uncommon': [], 'rare': []},
        'scrolls': {'common': [], 'uncommon': [], 'rare': []}
    }
    
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for line in lines[7:]:  # Skip header
        if not line.strip() or line.startswith('|---'):
            continue
        
        parts = [p.strip() for p in line.split('|')]
        if len(parts) < 9:
            continue
        
        name = parts[1]
        
        # Skip if no valid name
        if not name or name == 'Name' or len(name) < 2:
            continue
        
        # Find rarity - check multiple columns
        rarity = 'common'  # Default
        for i in range(3, min(7, len(parts))):
            part_lower = parts[i].lower()
            if 'uncommon' in part_lower:
                rarity = 'uncommon'
                break
            elif 'rare' in part_lower and 'uncommon' not in part_lower:
                rarity = 'rare'
                break
            elif 'common' in part_lower:
                rarity = 'common'
                break
        
        # Find category (usually in column 5 or 6)
        category = ''
        for i in range(5, min(8, len(parts))):
            if parts[i]:
                category = parts[i].lower()
                break
        
        # Find level and price - they can be in different positions
        level = 0
        price = ''
        
        for i in range(7, min(len(parts), 10)):
            part = parts[i].strip()
            if not part:
                continue
            
            # Try to parse as level
            if not price and part.isdigit() and int(part) <= 20:
                try:
                    level = int(part)
                except:
                    pass
            # Check if it's a price
            elif any(curr in part.lower() for curr in ['gp', 'sp', 'cp']):
                price = part
                break
        
        # Filter for levels -1 to 4
        if level < -1 or level > 4:
            continue
        
        # Skip if no price found
        if not price:
            continue
        
        item = {
            'name': name,
            'level': level,
            'price': price,
            'rarity': rarity
        }
        
        # Categorize based on category and name
        if 'weapon' in category or 'base weapons' in category or any(w in name.lower() for w in ['sword', 'axe', 'bow', 'crossbow', 'dagger', 'spear', 'mace', 'hammer', 'arrow', 'bolt', 'dart', 'javelin']):
            items['weapons'][rarity].append(item)
        elif 'armor' in category or any(a in name.lower() for a in ['armor', 'mail', 'plate', 'leather', 'chain']):
            items['armor'][rarity].append(item)
        elif 'alchemical' in category or 'alchemist' in name.lower():
            items['alchemical'][rarity].append(item)
        elif 'scroll' in category.lower() or 'scroll' in name.lower():
            items['scrolls'][rarity].append(item)
        elif 'adventuring' in category or 'gear' in category or any(g in category for g in ['tool', 'equipment', 'clothing']):
            items['adventuring'][rarity].append(item)
        elif 'consumable' in category or 'held' in category or 'worn' in category or 'potion' in name.lower() or 'elixir' in name.lower():
            items['magical'][rarity].append(item)
        else:
            # Default to adventuring gear for misc items
            items['adventuring'][rarity].append(item)
    
    return items

def get_manual_items():
    """Return manually curated items for specific merchants"""
    return {
        'scrolls_common': [
            {'name': 'Scroll of Detect Magic (Cantrip)', 'level': 1, 'price': '3 gp'},
            {'name': 'Scroll of Read Aura (Cantrip)', 'level': 1, 'price': '3 gp'},
            {'name': 'Scroll of Magic Missile (1st)', 'level': 1, 'price': '4 gp'},
            {'name': 'Scroll of Heal (1st)', 'level': 1, 'price': '4 gp'},
            {'name': 'Scroll of Mage Armor (1st)', 'level': 1, 'price': '4 gp'},
            {'name': 'Scroll of Grease (1st)', 'level': 1, 'price': '4 gp'},
            {'name': 'Scroll of Bless (1st)', 'level': 1, 'price': '4 gp'},
            {'name': 'Scroll of Command (1st)', 'level': 1, 'price': '4 gp'},
            {'name': 'Scroll of Fear (1st)', 'level': 1, 'price': '4 gp'},
            {'name': 'Scroll of Sanctuary (1st)', 'level': 1, 'price': '4 gp'},
            {'name': 'Scroll of Comprehend Language (2nd)', 'level': 3, 'price': '12 gp'},
            {'name': 'Basic Crafter\'s Book', 'level': 0, 'price': '1 sp'},
            {'name': 'Writing Set', 'level': 0, 'price': '1 gp'},
        ],
        'scrolls_uncommon': [
            {'name': 'Scroll of Invisibility (2nd)', 'level': 3, 'price': '12 gp'},
            {'name': 'Scroll of Restoration (2nd)', 'level': 3, 'price': '12 gp'},
            {'name': 'Scroll of Dispel Magic (2nd)', 'level': 3, 'price': '12 gp'},
            {'name': 'Scroll of Darkvision (2nd)', 'level': 3, 'price': '12 gp'},
            {'name': 'Scroll of See Invisibility (2nd)', 'level': 3, 'price': '12 gp'},
        ],
        'magical_common': [
            {'name': 'Wand of Magic Missile (1st, 1 charge)', 'level': 1, 'price': '6 gp'},
            {'name': 'Holy Water', 'level': 1, 'price': '3 gp'},
            {'name': 'Silver Weapon Blanch', 'level': 2, 'price': '6 gp'},
            {'name': 'Cold Iron Weapon Blanch', 'level': 2, 'price': '6 gp'},
            {'name': 'Religious Symbol (Silver)', 'level': 0, 'price': '2 gp'},
            {'name': 'Religious Symbol (Wooden)', 'level': 0, 'price': '1 sp'},
            {'name': 'Everburning Torch', 'level': 1, 'price': '15 gp'},
            {'name': 'Chalk (10 pieces)', 'level': 0, 'price': '1 cp'},
            {'name': 'Compass', 'level': 0, 'price': '1 gp'},
            {'name': 'Spellbook (Blank)', 'level': 0, 'price': '1 gp'},
            {'name': 'Formula Book (Blank)', 'level': 0, 'price': '1 gp'},
            {'name': 'Mirror', 'level': 0, 'price': '1 gp'},
            {'name': 'Lantern (Bull\'s-Eye)', 'level': 0, 'price': '1 gp'},
            {'name': 'Lantern (Hooded)', 'level': 0, 'price': '7 sp'},
        ],
        'magical_uncommon': [
            {'name': 'Wand of Heal (1st, 3 charges)', 'level': 3, 'price': '18 gp'},
            {'name': 'Wand of Burning Hands (1st, 2 charges)', 'level': 2, 'price': '12 gp'},
            {'name': 'Lesser Healing Potion', 'level': 3, 'price': '12 gp'},
            {'name': 'Potion of Water Breathing', 'level': 3, 'price': '11 gp'},
            {'name': 'Potion of Darkvision', 'level': 2, 'price': '7 gp'},
        ],
        'alchemical_common': [
            {'name': 'Alchemist\'s Fire (Lesser)', 'level': 1, 'price': '3 gp'},
            {'name': 'Antidote (Lesser)', 'level': 1, 'price': '3 gp'},
            {'name': 'Antiplague (Lesser)', 'level': 1, 'price': '3 gp'},
            {'name': 'Elixir of Life (Minor)', 'level': 1, 'price': '3 gp'},
            {'name': 'Smokestick (Lesser)', 'level': 1, 'price': '3 gp'},
            {'name': 'Tanglefoot Bag (Lesser)', 'level': 1, 'price': '3 gp'},
            {'name': 'Thunderstone (Lesser)', 'level': 1, 'price': '3 gp'},
        ],
        'market_uncommon': [
            # Uncommon weapons
            {'name': 'Dogslicer', 'level': 0, 'price': '1 sp'},
            {'name': 'Katar', 'level': 0, 'price': '3 sp'},
            {'name': 'Nunchaku', 'level': 0, 'price': '2 sp'},
            {'name': 'Shuriken (10)', 'level': 0, 'price': '1 sp'},
            {'name': 'Tonfa', 'level': 0, 'price': '1 sp'},
            # Uncommon armor
            {'name': 'Armored Skirt', 'level': 0, 'price': '2 gp'},
            {'name': 'Lamellar Armor', 'level': 1, 'price': '3 gp'},
            # Uncommon adventuring gear
            {'name': 'Grappling Arrow', 'level': 1, 'price': '3 sp'},
            {'name': 'Grappling Bolt', 'level': 1, 'price': '3 sp'},
            {'name': 'Tracking Tag', 'level': 1, 'price': '5 sp'},
            {'name': 'Waterproof Carrying Case', 'level': 1, 'price': '5 sp'},
            {'name': 'Earplugs', 'level': 0, 'price': '1 sp'},
            {'name': 'Shield Sconce', 'level': 1, 'price': '5 sp'},
            {'name': 'Marked Playing Cards', 'level': 0, 'price': '1 gp'},
            {'name': 'Wax Key Blank', 'level': 0, 'price': '1 gp'},
        ]
    }


def generate_inventory(categories, items, num_common=10, num_uncommon_range=(1,4), rare_chance=0.1, manual_items=None):
    """Generate inventory from specified categories"""
    inventory = {
        'common': [],
        'uncommon': [],
        'rare': []
    }
    
    # Use manual items if provided
    if manual_items:
        manual = get_manual_items()
        
        # Handle market-specific manual items
        if manual_items == 'market':
            # Get all common items from parsed data
            all_common = []
            for cat in categories:
                if cat in items:
                    all_common.extend(items[cat]['common'])
            
            if all_common:
                inventory['common'] = random.sample(all_common, min(num_common, len(all_common)))
            
            # Get uncommon from manual market items
            num_uncommon = num_uncommon_range[1] if isinstance(num_uncommon_range, tuple) else num_uncommon_range
            if 'market_uncommon' in manual:
                inventory['uncommon'] = random.sample(manual['market_uncommon'], min(num_uncommon, len(manual['market_uncommon'])))
            
            return inventory
        
        # Mix of manual and parsed items for common (for Wrin's Wonders, etc.)
        common_pool = []
        if 'scrolls' in categories and 'scrolls_common' in manual:
            common_pool.extend(manual['scrolls_common'])
        if 'magical' in categories and 'magical_common' in manual:
            common_pool.extend(manual['magical_common'])
        if 'alchemical' in categories and 'alchemical_common' in manual:
            common_pool.extend(manual['alchemical_common'])
        
        # Add some parsed items too for variety
        for cat in categories:
            if cat in items and cat not in ['scrolls', 'magical', 'alchemical']:
                common_pool.extend(items[cat]['common'][:5])  # Add up to 5 from each category
        
        if common_pool:
            inventory['common'] = random.sample(common_pool, min(num_common, len(common_pool)))
        
        # Get uncommon items
        num_uncommon = random.randint(num_uncommon_range[0], num_uncommon_range[1]) if isinstance(num_uncommon_range, tuple) else num_uncommon_range
        uncommon_pool = []
        if 'scrolls' in categories and 'scrolls_uncommon' in manual:
            uncommon_pool.extend(manual['scrolls_uncommon'])
        if 'magical' in categories and 'magical_uncommon' in manual:
            uncommon_pool.extend(manual['magical_uncommon'])
        
        if uncommon_pool:
            inventory['uncommon'] = random.sample(uncommon_pool, min(num_uncommon, len(uncommon_pool)))
        
        return inventory
    
    # Collect all items from specified categories
    all_common = []
    all_uncommon = []
    all_rare = []
    
    for cat in categories:
        if cat in items:
            all_common.extend(items[cat]['common'])
            all_uncommon.extend(items[cat]['uncommon'])
            all_rare.extend(items[cat]['rare'])
    
    # Get common items
    if all_common:
        inventory['common'] = random.sample(
            all_common,
            min(num_common, len(all_common))
        )
    
    # Get uncommon items
    num_uncommon = random.randint(num_uncommon_range[0], num_uncommon_range[1]) if isinstance(num_uncommon_range, tuple) else num_uncommon_range
    uncommon_filtered = [i for i in all_uncommon if i['level'] >= 1]
    if uncommon_filtered:
        inventory['uncommon'] = random.sample(
            uncommon_filtered,
            min(num_uncommon, len(uncommon_filtered))
        )
    
    # Rare items
    if random.random() < rare_chance:
        rare_level4 = [i for i in all_rare if i['level'] == 4]
        if rare_level4:
            inventory['rare'] = [random.choice(rare_level4)]
    
    return inventory

def sanitize_filename(name):
    """Convert merchant name to safe filename"""
    # Remove special characters and convert to lowercase
    safe = re.sub(r'[^\w\s-]', '', name.lower())
    safe = re.sub(r'[-\s]+', '_', safe)
    return safe

def write_merchant_file(merchant_data, output_dir='players'):
    """Write individual merchant file"""
    filename = sanitize_filename(merchant_data['name']) + '.md'
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"# {merchant_data['name']}\n\n")
        
        if 'subtitle' in merchant_data:
            f.write(f"*{merchant_data['subtitle']}*\n\n")
        
        if 'proprietor' in merchant_data:
            f.write(f"**Proprietor:** {merchant_data['proprietor']}\n\n")
        
        if 'description' in merchant_data:
            f.write(f"**Description:** {merchant_data['description']}\n\n")
        
        if 'specialties' in merchant_data:
            f.write(f"**Specialties:** {merchant_data['specialties']}\n\n")
        
        # Common items
        if merchant_data['inventory']['common']:
            f.write(f"### Common Items ({len(merchant_data['inventory']['common'])})\n")
            f.write("| Item | Level | Price | Details | Image |\n")
            f.write("|------|-------|-------|---------|-------|\n")
            for item in merchant_data['inventory']['common']:
                item_url = get_aon_equipment_url(item['name'])
                f.write(f"| {item['name']} | {item['level']} | {item['price']} | [View]({item_url}) | ![{item['name']}](IMAGE_PLACEHOLDER) |\n")
                time.sleep(0.3)  # Small delay to avoid rate limiting
            f.write("\n")
        
        # Uncommon items
        if merchant_data['inventory']['uncommon']:
            f.write(f"### Uncommon Items ({len(merchant_data['inventory']['uncommon'])})\n")
            f.write("| Item | Level | Price | Details | Image |\n")
            f.write("|------|-------|-------|---------|-------|\n")
            for item in merchant_data['inventory']['uncommon']:
                item_url = get_aon_equipment_url(item['name'])
                f.write(f"| {item['name']} | {item['level']} | {item['price']} | [View]({item_url}) | ![{item['name']}](IMAGE_PLACEHOLDER) |\n")
                time.sleep(0.3)  # Small delay to avoid rate limiting
            f.write("\n")
        
        # Rare items
        if merchant_data['inventory']['rare']:
            f.write(f"### Rare Items ({len(merchant_data['inventory']['rare'])})\n")
            f.write("| Item | Level | Price | Details | Image |\n")
            f.write("|------|-------|-------|---------|-------|\n")
            for item in merchant_data['inventory']['rare']:
                item_url = get_aon_equipment_url(item['name'])
                f.write(f"| {item['name']} | {item['level']} | {item['price']} | [View]({item_url}) | ![{item['name']}](IMAGE_PLACEHOLDER) |\n")
                time.sleep(0.3)  # Small delay to avoid rate limiting
            f.write("\n")
        
        # Special notes
        if 'special' in merchant_data:
            f.write("**Special:**\n")
            for note in merchant_data['special']:
                f.write(f"- {note}\n")
            f.write("\n")
        
        # Services
        if 'services' in merchant_data:
            f.write("**Services:**\n")
            for service in merchant_data['services']:
                f.write(f"- {service}\n")
            f.write("\n")
    
    print(f"Created: {filepath}")
    return filepath

if __name__ == "__main__":
    print("Parsing equipment database...")
    items = parse_equipment_md("etc/equipment.md")
    
    # Create output directory if it doesn't exist
    os.makedirs('players', exist_ok=True)
    
    # Define Otari merchants
    merchants = [
        {
            'name': "Wrin's Wonders",
            'subtitle': "Eccentric tiefling-elf oddities merchant and stargazer",
            'proprietor': "Wrin Sivinxi (CG female tiefling elf oddities merchant 5)",
            'description': "This odd, domed building is always open. Wrin is a bit unusual, seeing menace in every corner and truths in the constellations above, but she's eager to get to know adventurers and show off the many magical trinkets in her collection.",
            'specialties': "Adventuring gear and magic items",
            'categories': ['magical', 'scrolls', 'adventuring', 'alchemical'],
            'use_manual': True,
            'services': [
                "Spellcasting Services: Price varies by spell level and complexity (GM discretion)",
                "Spell Learning/Training: Price negotiable based on spell level (GM discretion)",
                "Magical item identification: 1-10 gp depending on complexity",
                "Astrological readings: 5 sp - 5 gp"
            ],
            'inventory': None
        },
        {
            'name': "Otari Market",
            'subtitle': "One-stop shop for basic goods",
            'proprietor': "Keeleno Lathenar (dour, humorless human merchant)",
            'description': "Part open-air farmer's market, part log-cabin trading post. Keeleno pays handsomely for wolf pelts, as a wolf-like monster slew his wife years ago, and he hopes to one day acquire the skin of her killer.",
            'specialties': "All adventuring gear, light armor, and simple weapons",
            'categories': ['weapons', 'armor', 'adventuring', 'alchemical', 'magical'],
            'use_manual': 'market',  # Use market-specific manual items for uncommon
            'num_common': 75,
            'num_uncommon': 15,
            'special': ["Keeleno pays 5 gp per wolf pelt (double normal price)"],
            'inventory': None
        },
        {
            'name': "Odd Stories",
            'subtitle': "Bookshop specializing in fiction, textbooks, and scrolls",
            'proprietor': "Morlibint (wizard 5) and his husband Yinyasmera",
            'description': "The wizard Morlibint specializes in fanciful fiction, but he and his husband also sell textbooks, teaching tools, and scrolls. Morlibint is incredibly well-read and can help the heroes decipher tomes in ancient or unusual languages. He eagerly purchases rare books the heroes come across in their adventures.",
            'specialties': "Books, scrolls, and knowledge",
            'categories': ['scrolls', 'adventuring'],
            'use_manual': True,
            'services': [
                "Spellcasting Services: Price varies by spell level and complexity (GM discretion)",
                "Spell Learning/Training: Price negotiable based on spell level (GM discretion)",
                "Translation of ancient/unusual languages: 5-20 gp depending on complexity",
                "Purchases rare books at 50% of value, resells at 150%",
                "Can special order specific books (1d6 days, +50% cost)",
                "Research assistance: 1-10 gp depending on topic"
            ],
            'inventory': None
        },
        {
            'name': "Gallentine Deliveries",
            'subtitle': "Fastest and most reliable delivery service",
            'proprietor': "Oloria Gallentine (seventh-generation Otari citizen)",
            'description': "Oloria can probably acquire anything the heroes need that they can't find in Otari, although the price for such orders might be steep.",
            'services': [
                "Local Delivery: 1 sp per item within Otari",
                "Regional Delivery: 5 sp per item to nearby settlements (1-3 days)",
                "Special Orders: Can acquire items not available in Otari",
                "  - Common items: Base price + 20%, 1d4 days",
                "  - Uncommon items: Base price + 50%, 1d6+2 days",
                "  - Rare items: Base price + 100%, 2d6+4 days",
                "Express Service: Double delivery cost, half the time"
            ],
            'categories': [],  # Service only, no inventory
            'use_manual': False,
            'inventory': {'common': [], 'uncommon': [], 'rare': []}
        },
        {
            'name': "Blades for Glades",
            'subtitle': "Otari's primary smithy",
            'proprietor': "Carman Rajani (expert blacksmith)",
            'description': "Otari's primary smithy sells armor and weapons in addition to saws and axes for the lumber industry. The forge is always hot and Carman is always busy, but she takes pride in quality work.",
            'specialties': "Weapons, armor, and tools",
            'categories': ['weapons', 'armor'],
            'use_manual': False,
            'num_common': random.randint(5, 20),
            'num_uncommon': random.randint(3, 8),
            'services': [
                "Weapon/Armor repair: 10% of item cost",
                "Custom orders: +25% cost, 1d6 days",
                "Sharpening: 5 sp per weapon"
            ],
            'inventory': None
        },
        {
            'name': "Crow's Casks",
            'subtitle': "Brewery and tavern",
            'proprietor': "Temmin 'Crow' Brassbuckle (jovial halfling brewer)",
            'description': "A brewery and tavern popular among local farmers and merchants. Known for excellent ales and a warm atmosphere. Crow is always happy to share local gossip over a pint.",
            'specialties': "Food, drink, and lodging",
            'categories': ['adventuring'],
            'use_manual': False,
            'num_common': random.randint(5, 20),
            'services': [
                "Ale (mug): 1 cp",
                "Ale (pitcher): 5 cp",
                "Fine wine (bottle): 1 gp",
                "Meal (common): 3 cp",
                "Meal (good): 1 sp",
                "Lodging (common room): 1 sp per night",
                "Lodging (private room): 5 sp per night"
            ],
            'inventory': None
        },
        {
            'name': "Crook's Nook",
            'subtitle': "Sailors' tavern and bridge",
            'proprietor': "Tamily Tanderveil (retired sailor)",
            'description': "A sailors' tavern built as a bridge across the Osprey River. Popular with sailors, fishermen, and anyone with a taste for adventure stories. The food is hearty and the drinks are strong.",
            'specialties': "Food, drink, and sailor's tales",
            'categories': ['adventuring'],
            'use_manual': False,
            'num_common': random.randint(5, 20),
            'services': [
                "Grog (mug): 2 cp",
                "Rum (shot): 5 cp",
                "Sailor's stew: 5 cp",
                "Fish and chips: 1 sp",
                "Lodging (hammock): 5 cp per night",
                "Lodging (bunk): 2 sp per night",
                "Sailor rumors and information: Free with drinks"
            ],
            'inventory': None
        },
        {
            'name': "The Rowdy Rockfish",
            'subtitle': "A surprisingly calm and quiet tavern",
            'proprietor': "Aaric (calm, contemplative bartender)",
            'description': "Despite its name, The Rowdy Rockfish is surprisingly calm and quiet. Aaric keeps the peace with a steady hand and wise words. A favorite of scholars and those seeking a peaceful drink.",
            'specialties': "Quiet atmosphere and quality drinks",
            'categories': ['adventuring'],
            'use_manual': False,
            'num_common': random.randint(5, 20),
            'services': [
                "House wine: 5 sp",
                "Imported spirits: 1-5 gp",
                "Cheese plate: 2 sp",
                "Meal (fine): 5 sp",
                "Lodging (quiet room): 1 gp per night",
                "Private meeting room: 5 gp per evening"
            ],
            'inventory': None
        },
        {
            'name': "Otari Fishery",
            'subtitle': "Fishery, shipyard, and entertainment venue",
            'proprietor': "Mendi Grantham (shipwright and fisher)",
            'description': "Fishery and shipyard by day, gathering place for games and entertainment by night. Mendi runs a tight ship and knows everything about boats and the waters around Otari.",
            'specialties': "Fish, boats, and maritime services",
            'categories': ['adventuring'],
            'use_manual': False,
            'num_common': random.randint(5, 20),
            'services': [
                "Fresh fish: 1-5 sp per pound",
                "Boat rental (rowboat): 5 sp per day",
                "Boat rental (sailing boat): 2 gp per day",
                "Boat repair: Varies by damage",
                "Fishing gear rental: 1 sp per day",
                "Maritime charts: 5-20 gp"
            ],
            'inventory': None
        },
        {
            'name': "Dawnflower Library",
            'subtitle': "Library and temple to Sarenrae",
            'proprietor': "Vandy Banderdash (cleric of Sarenrae)",
            'description': "A large library and temple to Sarenrae, with shrines to many other deities. Vandy is welcoming to all seekers of knowledge and offers healing services to those in need.",
            'specialties': "Religious services, healing, and knowledge",
            'categories': ['scrolls', 'magical'],
            'use_manual': True,
            'num_common': random.randint(5, 20),
            'num_uncommon': random.randint(2, 5),
            'services': [
                "Healing (1st level): 4 gp",
                "Healing (2nd level): 12 gp",
                "Remove Disease: 12 gp",
                "Restoration: 12 gp",
                "Research assistance: 1-10 gp depending on topic",
                "Religious ceremonies: Donation based"
            ],
            'inventory': None
        }
    ]
    
    # Generate inventories
    print("\nGenerating merchant inventories...")
    for merchant in merchants:
        if merchant['categories']:
            num_common = merchant.get('num_common', 10)
            num_uncommon = merchant.get('num_uncommon', (1, 4))
            
            # Convert single number to range tuple
            if isinstance(num_uncommon, int):
                num_uncommon = (num_uncommon, num_uncommon)
            
            merchant['inventory'] = generate_inventory(
                merchant['categories'],
                items,
                num_common=num_common,
                num_uncommon_range=num_uncommon,
                rare_chance=0.1,
                manual_items=merchant.get('use_manual', False)
            )
        
        write_merchant_file(merchant)
    
    print("\n✓ All merchant files created in 'players/' directory")
    print("\nNext step: Run fix_item_images.py on each file to add image URLs")
