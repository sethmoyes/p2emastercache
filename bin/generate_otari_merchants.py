#!/usr/bin/env python3
"""
Generate Otari merchant inventories with separate files per merchant
Based on Abomination Vaults Player's Guide
"""
import random
import re
import os

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
        if len(parts) < 10:
            continue
        
        name = parts[1]
        rarity = parts[4].lower()
        category = parts[6].lower()
        level_str = parts[8]
        price = parts[9]
        
        # Parse level
        try:
            if level_str and level_str.strip():
                level = int(level_str.strip().split()[0])
            else:
                level = 0
        except:
            continue
        
        # Filter for levels -1 to 4
        if level < -1 or level > 4:
            continue
        
        # Skip if no name or price
        if not name or not price or name == 'Name':
            continue
        
        item = {
            'name': name,
            'level': level,
            'price': price,
            'rarity': rarity
        }
        
        # Categorize
        if 'weapon' in category or 'base weapons' in category:
            if 'common' in rarity:
                items['weapons']['common'].append(item)
            elif 'uncommon' in rarity:
                items['weapons']['uncommon'].append(item)
            elif 'rare' in rarity:
                items['weapons']['rare'].append(item)
        elif 'armor' in category:
            if 'common' in rarity:
                items['armor']['common'].append(item)
            elif 'uncommon' in rarity:
                items['armor']['uncommon'].append(item)
            elif 'rare' in rarity:
                items['armor']['rare'].append(item)
        elif 'alchemical' in category:
            if 'common' in rarity:
                items['alchemical']['common'].append(item)
            elif 'uncommon' in rarity:
                items['alchemical']['uncommon'].append(item)
            elif 'rare' in rarity:
                items['alchemical']['rare'].append(item)
        elif 'scroll' in category.lower() or 'scroll' in name.lower():
            if 'common' in rarity:
                items['scrolls']['common'].append(item)
            elif 'uncommon' in rarity:
                items['scrolls']['uncommon'].append(item)
            elif 'rare' in rarity:
                items['scrolls']['rare'].append(item)
        elif 'adventuring' in category or 'gear' in category:
            if 'common' in rarity:
                items['adventuring']['common'].append(item)
            elif 'uncommon' in rarity:
                items['adventuring']['uncommon'].append(item)
            elif 'rare' in rarity:
                items['adventuring']['rare'].append(item)
        elif 'consumable' in category or 'held' in category or 'worn' in category:
            if 'common' in rarity:
                items['magical']['common'].append(item)
            elif 'uncommon' in rarity:
                items['magical']['uncommon'].append(item)
            elif 'rare' in rarity:
                items['magical']['rare'].append(item)
    
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
        ],
        'magical_uncommon': [
            {'name': 'Wand of Heal (1st, 3 charges)', 'level': 3, 'price': '18 gp'},
            {'name': 'Wand of Burning Hands (1st, 2 charges)', 'level': 2, 'price': '12 gp'},
            {'name': 'Lesser Healing Potion', 'level': 3, 'price': '12 gp'},
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
        
        # Get common items
        if 'scrolls' in categories and 'scrolls_common' in manual:
            inventory['common'].extend(random.sample(manual['scrolls_common'], min(10, len(manual['scrolls_common']))))
        if 'magical' in categories and 'magical_common' in manual:
            remaining = 10 - len(inventory['common'])
            if remaining > 0:
                inventory['common'].extend(random.sample(manual['magical_common'], min(remaining, len(manual['magical_common']))))
        
        # Get uncommon items
        num_uncommon = random.randint(num_uncommon_range[0], num_uncommon_range[1])
        if 'scrolls' in categories and 'scrolls_uncommon' in manual:
            inventory['uncommon'].extend(random.sample(manual['scrolls_uncommon'], min(num_uncommon, len(manual['scrolls_uncommon']))))
        if 'magical' in categories and 'magical_uncommon' in manual:
            remaining = num_uncommon - len(inventory['uncommon'])
            if remaining > 0:
                inventory['uncommon'].extend(random.sample(manual['magical_uncommon'], min(remaining, len(manual['magical_uncommon']))))
        
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
    num_uncommon = random.randint(num_uncommon_range[0], num_uncommon_range[1])
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
            f.write("| Item | Level | Price | Image |\n")
            f.write("|------|-------|-------|-------|\n")
            for item in merchant_data['inventory']['common']:
                f.write(f"| {item['name']} | {item['level']} | {item['price']} | ![{item['name']}](IMAGE_PLACEHOLDER) |\n")
            f.write("\n")
        
        # Uncommon items
        if merchant_data['inventory']['uncommon']:
            f.write(f"### Uncommon Items ({len(merchant_data['inventory']['uncommon'])})\n")
            f.write("| Item | Level | Price | Image |\n")
            f.write("|------|-------|-------|-------|\n")
            for item in merchant_data['inventory']['uncommon']:
                f.write(f"| {item['name']} | {item['level']} | {item['price']} | ![{item['name']}](IMAGE_PLACEHOLDER) |\n")
            f.write("\n")
        
        # Rare items
        if merchant_data['inventory']['rare']:
            f.write(f"### Rare Items ({len(merchant_data['inventory']['rare'])})\n")
            f.write("| Item | Level | Price | Image |\n")
            f.write("|------|-------|-------|-------|\n")
            for item in merchant_data['inventory']['rare']:
                f.write(f"| {item['name']} | {item['level']} | {item['price']} | ![{item['name']}](IMAGE_PLACEHOLDER) |\n")
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
            'categories': ['magical', 'scrolls'],
            'use_manual': True,
            'inventory': None
        },
        {
            'name': "Otari Market",
            'subtitle': "One-stop shop for basic goods",
            'proprietor': "Keeleno Lathenar (dour, humorless human merchant)",
            'description': "Part open-air farmer's market, part log-cabin trading post. Keeleno pays handsomely for wolf pelts, as a wolf-like monster slew his wife years ago, and he hopes to one day acquire the skin of her killer.",
            'specialties': "All adventuring gear, light armor, and simple weapons",
            'categories': ['weapons', 'armor', 'adventuring'],
            'use_manual': False,
            'special': ["Keeleno pays 5 gp per wolf pelt (double normal price)"],
            'inventory': None
        },
        {
            'name': "Odd Stories",
            'subtitle': "Bookshop specializing in fiction, textbooks, and scrolls",
            'proprietor': "Morlibint (wizard 5) and his husband Yinyasmera",
            'description': "The wizard Morlibint specializes in fanciful fiction, but he and his husband also sell textbooks, teaching tools, and scrolls. Morlibint is incredibly well-read and can help the heroes decipher tomes in ancient or unusual languages. He eagerly purchases rare books the heroes come across in their adventures.",
            'specialties': "Books, scrolls, and knowledge",
            'categories': ['scrolls'],
            'use_manual': True,
            'services': [
                "Translation of ancient/unusual languages: 5-20 gp depending on complexity",
                "Purchases rare books at 50% of value, resells at 150%",
                "Can special order specific books (1d6 days, +50% cost)"
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
        }
    ]
    
    # Generate inventories
    print("\nGenerating merchant inventories...")
    for merchant in merchants:
        if merchant['categories']:
            merchant['inventory'] = generate_inventory(
                merchant['categories'],
                items,
                num_common=10,
                num_uncommon_range=(1, 4),
                rare_chance=0.1,
                manual_items=merchant.get('use_manual', False)
            )
        
        write_merchant_file(merchant)
    
    print("\n✓ All merchant files created in 'players/' directory")
    print("\nNext step: Run fix_item_images.py on each file to add image URLs")
