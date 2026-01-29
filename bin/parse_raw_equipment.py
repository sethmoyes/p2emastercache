#!/usr/bin/env python3
"""
Parse raw equipment data from etc/equipment.md (new format)
Multi-line tab-separated format
"""
import json
import re

def parse_raw_equipment(filename):
    """Parse the raw equipment format"""
    items = []
    
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Skip header - find where actual data starts
    start_idx = 0
    for idx, line in enumerate(lines):
        if 'Showing' in line and 'results' in line:
            start_idx = idx + 2  # Skip the "Showing" line and next line
            break
    
    print(f"Starting parse at line {start_idx}")
    
    i = start_idx
    found_names = 0
    while i < len(lines):
        line = lines[i]
        line_stripped = line.strip()
        
        # Look for item name (line ends with tab, not blank, and doesn't have multiple tabs)
        if line_stripped and line.rstrip('\r\n').endswith('\t') and '\t' not in line_stripped.rstrip('\t'):
            name = line_stripped.rstrip('\t')
            found_names += 1
            
            if found_names <= 5:
                print(f"Found name at line {i}: {name}")
            
            # Skip header lines
            if len(name) < 3 or name in ['Trait', 'Usage']:
                i += 1
                continue
            
            try:
                # Next line: PFS
                i += 1
                if i >= len(lines):
                    break
                
                # Skip blank lines to source
                while i < len(lines) and not lines[i].strip():
                    i += 1
                
                # Source line (don't skip past it)
                source_line = lines[i].strip() if i < len(lines) else ''
                i += 1
                
                # Rarity line
                rarity_line = lines[i].strip().rstrip('\t')
                i += 1
                
                # Skip blank
                while i < len(lines) and not lines[i].strip():
                    i += 1
                
                # Traits line
                traits_line = lines[i].strip().rstrip('\t')
                i += 1
                
                # Category line with tabs
                cat_line = lines[i]
                parts = cat_line.split('\t')
                
                # Remove empty first element if line starts with tab
                if parts and not parts[0].strip():
                    parts = parts[1:]
                
                if found_names <= 2:
                    print(f"  Category line parts: {len(parts)}")
                    print(f"  Parts: {parts[:6]}")
                
                if len(parts) >= 4:
                    category = parts[0].strip()
                    subcategory = parts[1].strip()
                    level_str = parts[2].strip()
                    price_str = parts[3].strip()
                    
                    if found_names <= 2:
                        print(f"  Level: {level_str}, Price: {price_str}")
                    
                    # Parse level
                    try:
                        level = int(level_str)
                    except:
                        if found_names <= 2:
                            print(f"  Failed to parse level: {level_str}")
                        i += 1
                        continue
                    
                    # Only level -1 to 5
                    if level < -1 or level > 5:
                        i += 1
                        continue
                    
                    # Parse rarity
                    rarity = 'common'
                    if 'uncommon' in rarity_line.lower():
                        rarity = 'uncommon'
                    elif 'rare' in rarity_line.lower() and 'uncommon' not in rarity_line.lower():
                        rarity = 'rare'
                    
                    # Determine type
                    item_type = 'adventuring'
                    traits_lower = traits_line.lower()
                    cat_lower = (category + ' ' + subcategory).lower()
                    
                    if 'weapon' in cat_lower or 'weapon' in traits_lower:
                        item_type = 'weapon'
                    elif 'armor' in cat_lower or 'shield' in cat_lower:
                        item_type = 'armor'
                    elif 'alchemical' in cat_lower or 'alchemical' in traits_lower:
                        item_type = 'alchemical'
                    elif 'scroll' in traits_lower or 'wand' in name.lower():
                        item_type = 'magical'
                    
                    items.append({
                        'name': name,
                        'level': level,
                        'price': price_str,
                        'rarity': rarity,
                        'category': category,
                        'type': item_type
                    })
                    
            except Exception as e:
                pass
        
        i += 1
    
    return items

if __name__ == "__main__":
    print("Parsing raw equipment data...")
    items = parse_raw_equipment("etc/equipment.md")
    
    print(f"\nFound {len(items)} items (level -1 to 5)")
    
    # Show first 10
    print("\nFirst 10 items:")
    for item in items[:10]:
        print(f"  {item['name']} - Level {item['level']} - {item['price']} - {item['rarity']}")
    
    # Save
    with open("etc/equipment.json", 'w', encoding='utf-8') as f:
        json.dump(items, f, indent=2, ensure_ascii=False)
    
    print(f"\nSaved {len(items)} items to etc/equipment.json")
