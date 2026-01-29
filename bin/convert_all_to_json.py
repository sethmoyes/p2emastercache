#!/usr/bin/env python3
"""
Convert equipment.md, creatures.md, and dieties.md to clean JSON format
Properly handles markdown table parsing with correct column mapping
"""
import json
import re

def parse_table_row(line, expected_columns):
    """Parse a markdown table row and return list of cell values"""
    # Split by | and strip whitespace
    parts = [p.strip() for p in line.split('|')]
    # Remove empty first/last elements from leading/trailing |
    if parts and not parts[0]:
        parts = parts[1:]
    if parts and not parts[-1]:
        parts = parts[:-1]
    
    # Pad or truncate to expected number of columns
    while len(parts) < expected_columns:
        parts.append('')
    
    return parts[:expected_columns]

def parse_equipment_md_to_json(filename):
    """Parse equipment.md with correct column mapping"""
    items = []
    
    # Expected columns: Name | PFS | Source | Rarity | Trait | Category | Subcategory | Level | Price | Bulk | Usage
    expected_cols = 11
    
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find header row
    header_idx = None
    for i, line in enumerate(lines):
        if '| Name |' in line and '| PFS |' in line:
            header_idx = i
            break
    
    if header_idx is None:
        print("Could not find header row in equipment.md")
        return []
    
    # Skip header and separator rows
    for line in lines[header_idx + 2:]:
        if not line.strip() or line.startswith('#'):
            continue
        
        if '|' not in line:
            continue
        
        parts = parse_table_row(line, expected_cols)
        
        name = parts[0]
        pfs = parts[1]
        source = parts[2]
        rarity = parts[3]
        trait = parts[4]
        category = parts[5]
        subcategory = parts[6]
        level = parts[7]
        price = parts[8]
        bulk = parts[9]
        usage = parts[10]
        
        # Skip invalid rows
        if not name or name == 'Name' or len(name) < 2:
            continue
        
        # Skip malformed entries
        if '\t' in name or any(x in name.lower() for x in ['weapons\t', 'armor\t', 'common\t']):
            continue
        
        # Skip placeholder entries
        if name.lower() in ['loading...', 'loading']:
            continue
        
        # Parse level
        try:
            level_num = int(level) if level and level.strip() else 0
        except:
            level_num = 0
        
        # Only include items level -1 to 4
        if level_num < -1 or level_num > 4:
            continue
        
        # Determine rarity
        rarity_clean = 'common'
        if rarity:
            rarity_lower = rarity.lower()
            if 'uncommon' in rarity_lower:
                rarity_clean = 'uncommon'
            elif 'rare' in rarity_lower and 'uncommon' not in rarity_lower:
                rarity_clean = 'rare'
        
        # Determine type from category/trait
        item_type = 'adventuring'  # default
        cat_lower = (category + ' ' + trait + ' ' + subcategory).lower()
        
        if 'weapon' in cat_lower:
            item_type = 'weapon'
        elif 'armor' in cat_lower or 'shield' in cat_lower:
            item_type = 'armor'
        elif 'alchemical' in cat_lower:
            item_type = 'alchemical'
        elif 'scroll' in cat_lower or 'scroll' in name.lower():
            item_type = 'scroll'
        elif 'magical' in cat_lower or 'magic' in cat_lower or 'wand' in name.lower() or 'potion' in name.lower():
            item_type = 'magical'
        
        items.append({
            'name': name,
            'level': level_num,
            'price': price if price else '0 gp',
            'rarity': rarity_clean,
            'category': category,
            'type': item_type
        })
    
    return items

def parse_dieties_md_to_json(filename):
    """Parse dieties.md with correct column mapping"""
    dieties = []
    
    # Expected columns: Name | PFS | Edict | Anathema | Domains | Harm/Heal | Sanctification | Ability | Skills | Weapon | Category | Pantheons | Source
    expected_cols = 13
    
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find header row
    header_idx = None
    for i, line in enumerate(lines):
        if '| Name |' in line and '| Edict |' in line:
            header_idx = i
            break
    
    if header_idx is None:
        print("Could not find header row in dieties.md")
        return []
    
    # Skip header and separator rows
    for line in lines[header_idx + 2:]:
        if not line.strip() or line.startswith('#'):
            continue
        
        if '|' not in line:
            continue
        
        parts = parse_table_row(line, expected_cols)
        
        name = parts[0]
        pfs = parts[1]
        edict = parts[2]
        anathema = parts[3]
        domains = parts[4]
        harm_heal = parts[5]
        sanctification = parts[6]
        ability = parts[7]
        skills = parts[8]
        weapon = parts[9]
        category = parts[10]
        pantheons = parts[11]
        source = parts[12]
        
        # Handle malformed rows where name is in the source column
        # Pattern: Name column has PFS value AND PFS column is empty
        if (name in ['PFS Standard', 'PFS Limited', 'PFS Restricted']) and not pfs.strip():
            # Name is actually in the source column, everything shifts left by 1
            actual_name = source
            actual_pfs = name  # The PFS value that was in the name column
            actual_edict = edict
            actual_anathema = anathema
            actual_domains = domains
            actual_harm_heal = harm_heal
            actual_sanctification = sanctification
            actual_ability = ability
            actual_skills = skills
            actual_weapon = weapon
            actual_category = category
            actual_pantheons = pantheons
            actual_source = ''  # No source since name took that spot
            
            # Reassign
            name = actual_name
            pfs = actual_pfs
            edict = actual_edict
            anathema = actual_anathema
            domains = actual_domains
            harm_heal = actual_harm_heal
            sanctification = actual_sanctification
            ability = actual_ability
            skills = actual_skills
            weapon = actual_weapon
            category = actual_category
            pantheons = actual_pantheons
            source = actual_source
        
        # Skip invalid rows
        if not name or name == 'Name' or len(name) < 2:
            continue
        
        # Skip rows that are still malformed after correction
        if not edict or not domains:
            continue
        
        dieties.append({
            'name': name,
            'pfs': pfs,
            'edict': edict,
            'anathema': anathema,
            'domains': domains,
            'harm_heal': harm_heal,
            'sanctification': sanctification,
            'ability': ability,
            'skills': skills,
            'weapon': weapon,
            'category': category,
            'pantheons': pantheons,
            'source': source
        })
    
    return dieties

def parse_creatures_md_to_json(filename):
    """Parse creatures.md with correct column mapping"""
    creatures = []
    
    # Expected columns: Name | Creature Family | Source | Rarity | Size | Trait | Level | HP | AC | Fort | Reflex | Will | Perception | Sense | Speed
    expected_cols = 15
    
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find header row
    header_idx = None
    for i, line in enumerate(lines):
        if '| Name |' in line and '| Creature Family |' in line:
            header_idx = i
            break
    
    if header_idx is None:
        print("Could not find header row in creatures.md")
        return []
    
    # Skip header and separator rows
    for line in lines[header_idx + 2:]:
        if not line.strip() or line.startswith('#'):
            continue
        
        if '|' not in line:
            continue
        
        parts = parse_table_row(line, expected_cols)
        
        name = parts[0]
        creature_family = parts[1]
        source = parts[2]
        rarity = parts[3]
        size = parts[4]
        trait = parts[5]
        level = parts[6]
        hp = parts[7]
        ac = parts[8]
        fort = parts[9]
        reflex = parts[10]
        will = parts[11]
        perception = parts[12]
        sense = parts[13]
        speed = parts[14]
        
        # Skip invalid rows
        if not name or name == 'Name' or len(name) < 2:
            continue
        
        # Parse level
        try:
            level_num = int(level) if level and level.strip() else 0
        except:
            level_num = 0
        
        # Only include creatures level 0 to 5
        if level_num < 0 or level_num > 5:
            continue
        
        creatures.append({
            'name': name,
            'creature_family': creature_family,
            'source': source,
            'rarity': rarity,
            'size': size,
            'trait': trait,
            'level': level_num,
            'hp': hp,
            'ac': ac,
            'fort': fort,
            'reflex': reflex,
            'will': will,
            'perception': perception,
            'sense': sense,
            'speed': speed
        })
    
    return creatures

if __name__ == "__main__":
    print("Converting markdown files to JSON...\n")
    
    # Convert equipment
    print("1. Converting equipment.md...")
    equipment = parse_equipment_md_to_json("etc/equipment.md")
    print(f"   Found {len(equipment)} items (levels -1 to 4)")
    
    with open("etc/equipment.json", 'w', encoding='utf-8') as f:
        json.dump(equipment, f, indent=2, ensure_ascii=False)
    print("   ✓ Saved to etc/equipment.json")
    
    # Convert creatures
    print("\n2. Converting creatures.md...")
    creatures = parse_creatures_md_to_json("etc/creatures.md")
    print(f"   Found {len(creatures)} creatures (levels 0 to 5)")
    
    with open("etc/creatures.json", 'w', encoding='utf-8') as f:
        json.dump(creatures, f, indent=2, ensure_ascii=False)
    print("   ✓ Saved to etc/creatures.json")
    
    # Convert dieties
    print("\n3. Converting dieties.md...")
    dieties = parse_dieties_md_to_json("etc/dieties.md")
    print(f"   Found {len(dieties)} dieties")
    
    with open("etc/dieties.json", 'w', encoding='utf-8') as f:
        json.dump(dieties, f, indent=2, ensure_ascii=False)
    print("   ✓ Saved to etc/dieties.json")
    
    print("\n" + "="*50)
    print("✓ All conversions complete!")
    print("="*50)
