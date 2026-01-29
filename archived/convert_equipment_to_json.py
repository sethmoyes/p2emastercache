#!/usr/bin/env python3
"""
Convert equipment.md to clean JSON format
"""
import json
import re

def parse_equipment_md_to_json(filename):
    """Parse equipment.md and convert to clean JSON structure"""
    items = []
    
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
        
        # Skip malformed entries with tabs or weird formatting
        if '\t' in name or name.count('\t') > 0:
            continue
        
        # Skip entries that look like they're just category headers
        if any(x in name.lower() for x in ['common\t', 'uncommon\t', 'rare\t', 'weapons\t', 'armor\t']):
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
                category = parts[i].strip()
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
        
        # Skip if no price found
        if not price:
            continue
        
        # Determine item type based on category and name
        item_type = 'adventuring'  # Default
        
        if 'weapon' in category.lower() or 'base weapons' in category.lower() or any(w in name.lower() for w in ['sword', 'axe', 'bow', 'crossbow', 'dagger', 'spear', 'mace', 'hammer', 'arrow', 'bolt', 'dart', 'javelin']):
            item_type = 'weapon'
        elif 'armor' in category.lower() or any(a in name.lower() for a in ['armor', 'mail', 'plate', 'leather', 'chain', 'shield', 'buckler']):
            item_type = 'armor'
        elif 'alchemical' in category.lower() or 'alchemist' in name.lower():
            item_type = 'alchemical'
        elif 'scroll' in category.lower() or 'scroll' in name.lower():
            item_type = 'scroll'
        elif 'consumable' in category.lower() or 'held' in category.lower() or 'worn' in category.lower() or 'potion' in name.lower() or 'elixir' in name.lower() or 'wand' in name.lower():
            item_type = 'magical'
        elif 'adventuring' in category.lower() or 'gear' in category.lower() or any(g in category.lower() for g in ['tool', 'equipment', 'clothing']):
            item_type = 'adventuring'
        
        item = {
            'name': name,
            'level': level,
            'price': price,
            'rarity': rarity,
            'category': category,
            'type': item_type
        }
        
        items.append(item)
    
    return items

if __name__ == "__main__":
    print("Converting equipment.md to JSON...")
    
    items = parse_equipment_md_to_json("etc/equipment.md")
    
    # Filter for levels -1 to 4 (appropriate for early campaign)
    filtered_items = [item for item in items if -1 <= item['level'] <= 4]
    
    print(f"Found {len(items)} total items")
    print(f"Filtered to {len(filtered_items)} items (levels -1 to 4)")
    
    # Save to JSON
    output_file = "etc/equipment.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(filtered_items, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Saved to {output_file}")
    
    # Print summary by type and rarity
    print("\nSummary by type and rarity:")
    types = {}
    for item in filtered_items:
        item_type = item['type']
        rarity = item['rarity']
        
        if item_type not in types:
            types[item_type] = {'common': 0, 'uncommon': 0, 'rare': 0}
        
        types[item_type][rarity] += 1
    
    for item_type, counts in sorted(types.items()):
        print(f"  {item_type.capitalize()}: {counts['common']} common, {counts['uncommon']} uncommon, {counts['rare']} rare")
