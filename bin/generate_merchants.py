#!/usr/bin/env python3
"""
Generate merchant inventories from equipment database
"""
import random
import re

def parse_equipment_md(filename):
    """Parse equipment.md and return items by category and rarity"""
    items = {
        'weapons': {'common': [], 'uncommon': [], 'rare': []},
        'armor': {'common': [], 'uncommon': [], 'rare': []},
        'alchemical': {'common': [], 'uncommon': [], 'rare': []},
        'adventuring': {'common': [], 'uncommon': [], 'rare': []},
        'magical': {'common': [], 'uncommon': [], 'rare': []}
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
        elif 'adventuring' in category or 'gear' in category:
            if 'common' in rarity:
                items['adventuring']['common'].append(item)
            elif 'uncommon' in rarity:
                items['adventuring']['uncommon'].append(item)
            elif 'rare' in rarity:
                items['adventuring']['rare'].append(item)
    
    return items

def generate_merchant(name, category, items):
    """Generate a merchant inventory"""
    inventory = {
        'name': name,
        'category': category,
        'common': [],
        'uncommon': [],
        'rare': []
    }
    
    # Get 10 common items (levels -1 to 4)
    if items[category]['common']:
        inventory['common'] = random.sample(
            items[category]['common'],
            min(10, len(items[category]['common']))
        )
    
    # Get 1-4 uncommon items (levels 1-4)
    num_uncommon = random.randint(1, 4)
    uncommon_filtered = [i for i in items[category]['uncommon'] if i['level'] >= 1]
    if uncommon_filtered:
        inventory['uncommon'] = random.sample(
            uncommon_filtered,
            min(num_uncommon, len(uncommon_filtered))
        )
    
    # 10% chance for 1 rare level 4 item
    if random.random() < 0.1:
        rare_level4 = [i for i in items[category]['rare'] if i['level'] == 4]
        if rare_level4:
            inventory['rare'] = [random.choice(rare_level4)]
    
    return inventory

def format_merchant_md(merchant):
    """Format merchant inventory as markdown"""
    output = []
    output.append(f"## {merchant['name']}")
    output.append(f"*Specializes in {merchant['category']}*\n")
    
    output.append("### Common Items (10)")
    output.append("| Item | Level | Price |")
    output.append("|------|-------|-------|")
    for item in merchant['common']:
        output.append(f"| {item['name']} | {item['level']} | {item['price']} |")
    output.append("")
    
    if merchant['uncommon']:
        output.append(f"### Uncommon Items ({len(merchant['uncommon'])})")
        output.append("| Item | Level | Price |")
        output.append("|------|-------|-------|")
        for item in merchant['uncommon']:
            output.append(f"| {item['name']} | {item['level']} | {item['price']} |")
        output.append("")
    
    if merchant['rare']:
        output.append("### Rare Items (1)")
        output.append("| Item | Level | Price |")
        output.append("|------|-------|-------|")
        for item in merchant['rare']:
            output.append(f"| {item['name']} | {item['level']} | {item['price']} |")
        output.append("")
    
    return "\n".join(output)

if __name__ == "__main__":
    print("Parsing equipment database...")
    items = parse_equipment_md("etc/equipment.md")
    
    print(f"Found {len(items['weapons']['common'])} common weapons")
    print(f"Found {len(items['armor']['common'])} common armor")
    print(f"Found {len(items['alchemical']['common'])} common alchemical")
    print(f"Found {len(items['adventuring']['common'])} common adventuring gear")
    
    # Generate merchants
    merchants = [
        generate_merchant("Ironforge Arms", "weapons", items),
        generate_merchant("Steelguard Armory", "armor", items),
        generate_merchant("Bubbling Cauldron", "alchemical", items),
        generate_merchant("Wanderer's Supply", "adventuring", items),
    ]
    
    # Write to file
    with open("merchant_inventories.md", 'w', encoding='utf-8') as f:
        f.write("# Merchant Inventories\n\n")
        f.write("*Generated for shopping trip to town*\n\n")
        f.write("---\n\n")
        
        for merchant in merchants:
            f.write(format_merchant_md(merchant))
            f.write("\n---\n\n")
    
    print("\nMerchant inventories created: merchant_inventories.md")
