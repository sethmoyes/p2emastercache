#!/usr/bin/env python3
"""
Parse Archives of Nethys data files and convert to markdown tables
"""
import re

def parse_deities(input_file, output_file):
    """Parse deities.txt and create markdown table"""
    
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find where data starts (after "Showing 444 of 444 results")
    start_idx = None
    for i, line in enumerate(lines):
        if 'Showing 444 of 444 results' in line:
            start_idx = i + 2  # Skip the header line too
            break
    
    if start_idx is None:
        print("Could not find data start")
        return
    
    # Create markdown table
    with open(output_file, 'w', encoding='utf-8') as out:
        out.write("# Pathfinder 2e Deities Database\n\n")
        out.write("Source: Archives of Nethys\n\n")
        
        # Write table header
        out.write("| Name | PFS | Edict | Anathema | Domains | Harm/Heal | Sanctification | Ability | Skills | Weapon | Category | Pantheons | Source |\n")
        out.write("|------|-----|-------|----------|---------|-----------|----------------|---------|--------|--------|----------|-----------|--------|\n")
        
        i = start_idx
        while i < len(lines):
            line = lines[i].strip()
            
            # Check if this is a deity name (non-empty, not indented, has letters)
            if line and not line.startswith('\t') and not line.startswith(' ') and any(c.isalpha() for c in line):
                deity_name = line
                i += 1
                
                # Get PFS status
                pfs = lines[i].strip() if i < len(lines) else ""
                i += 1
                
                # Skip 2 empty lines
                while i < len(lines) and not lines[i].strip():
                    i += 1
                
                # Get Edict
                edict = lines[i].strip() if i < len(lines) else ""
                i += 1
                
                # Skip 2 empty lines
                while i < len(lines) and not lines[i].strip():
                    i += 1
                
                # Get Anathema
                anathema = lines[i].strip() if i < len(lines) else ""
                i += 1
                
                # Skip 2 empty lines
                while i < len(lines) and not lines[i].strip():
                    i += 1
                
                # Get Domains (first line)
                domains = lines[i].strip() if i < len(lines) else ""
                i += 1
                
                # Get Domains line 2 (has tabs for Harm/Heal, Sanctification, Ability)
                domains_line2 = lines[i] if i < len(lines) else ""
                parts = domains_line2.split('\t')
                # First part is usually empty/whitespace, real data starts at index 1
                harm_heal = parts[1].strip() if len(parts) > 1 else ""
                sanctification = parts[2].strip() if len(parts) > 2 else ""
                ability = parts[3].strip() if len(parts) > 3 else ""
                i += 1
                
                # Skip empty line
                while i < len(lines) and not lines[i].strip():
                    i += 1
                
                # Get Skills
                skills = lines[i].strip() if i < len(lines) else ""
                i += 1
                
                # Skip 2 empty lines
                while i < len(lines) and not lines[i].strip():
                    i += 1
                
                # Get Weapon
                weapon = lines[i].strip() if i < len(lines) else ""
                i += 1
                
                # Get Category line (has tabs)
                category_line = lines[i] if i < len(lines) else ""
                cat_parts = category_line.split('\t')
                category = cat_parts[1].strip() if len(cat_parts) > 1 else cat_parts[0].strip()
                i += 1
                
                # Skip empty line
                while i < len(lines) and not lines[i].strip():
                    i += 1
                
                # Get Pantheons
                pantheons = lines[i].strip() if i < len(lines) else ""
                i += 1
                
                # Skip 2 empty lines
                while i < len(lines) and not lines[i].strip():
                    i += 1
                
                # Get Source
                source = lines[i].strip() if i < len(lines) else ""
                i += 1
                
                # Clean all fields
                def clean(s):
                    return s.replace('|', '\\|').replace('\n', ' ').strip()
                
                # Write row
                out.write(f"| {clean(deity_name)} | {clean(pfs)} | {clean(edict)} | {clean(anathema)} | {clean(domains)} | {clean(harm_heal)} | {clean(sanctification)} | {clean(ability)} | {clean(skills)} | {clean(weapon)} | {clean(category)} | {clean(pantheons)} | {clean(source)} |\n")
            else:
                i += 1
    
    print(f"Deities markdown table created: {output_file}")


def parse_equipment(input_file, output_file):
    """Parse equipment.txt and create markdown table"""
    
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find where data starts
    start_idx = None
    for i, line in enumerate(lines):
        if 'Showing 5717 of 5717 results' in line:
            start_idx = i + 2
            break
    
    if start_idx is None:
        print("Could not find data start")
        return
    
    # First pass: find all tab lines (these mark the end of each item's data)
    tab_line_indices = []
    for i in range(start_idx, len(lines)):
        if lines[i] and lines[i][0].isspace() and '\t' in lines[i]:
            tab_line_indices.append(i)
    
    # Create markdown table
    with open(output_file, 'w', encoding='utf-8') as out:
        out.write("# Pathfinder 2e Equipment Database\n\n")
        out.write("Source: Archives of Nethys\n\n")
        
        # Write table header
        out.write("| Name | PFS | Source | Rarity | Trait | Category | Subcategory | Level | Price | Bulk | Usage |\n")
        out.write("|------|-----|--------|--------|-------|----------|-------------|-------|-------|------|-------|-------|\n")
        
        # Process each item by working backwards from tab lines
        for tab_idx in tab_line_indices:
            # Parse the tab line
            data_line = lines[tab_idx]
            parts = data_line.split('\t')
            rarity = parts[1].strip() if len(parts) > 1 else ""
            trait = parts[3].strip() if len(parts) > 3 else ""
            category = parts[4].strip() if len(parts) > 4 else ""
            subcategory = parts[5].strip() if len(parts) > 5 else ""
            level = parts[6].strip() if len(parts) > 6 else ""
            price = parts[7].strip() if len(parts) > 7 else ""
            bulk = parts[8].strip() if len(parts) > 8 else ""
            usage = parts[9].strip() if len(parts) > 9 else ""
            
            # Work backwards to find item name, PFS, and source
            # Pattern: Name, PFS (optional), empty lines, Source, optional lines, tab line
            item_name = ""
            pfs = ""
            source = ""
            
            # Go back from tab line
            i = tab_idx - 1
            
            # Skip empty lines
            while i >= start_idx and not lines[i].strip():
                i -= 1
            
            # Get source (line before tab, after skipping empties)
            # Source typically has "pg." or "Core"
            if i >= start_idx:
                potential_source = lines[i].strip()
                if 'pg.' in potential_source or 'Core' in potential_source:
                    source = potential_source
                    i -= 1
                    
                    # Skip empty lines and trait lines
                    while i >= start_idx and (not lines[i].strip() or lines[i][0].isspace()):
                        i -= 1
                    
                    # Skip more non-indented lines (traits)
                    while i >= start_idx and lines[i].strip() and not lines[i][0].isspace():
                        next_line = lines[i].strip()
                        # Stop if we hit something that looks like PFS or a name
                        if next_line.startswith('PFS') or (i > start_idx and not lines[i-1].strip()):
                            break
                        i -= 1
                    
                    # Check for PFS line
                    if i >= start_idx and lines[i].strip().startswith('PFS'):
                        pfs = lines[i].strip()
                        i -= 1
                    
                    # Skip empty lines
                    while i >= start_idx and not lines[i].strip():
                        i -= 1
                    
                    # Get item name
                    if i >= start_idx:
                        item_name = lines[i].strip()
            
            # Clean all fields
            def clean(s):
                return s.replace('|', '\\|').replace('\n', ' ').strip()
            
            # Write row
            if item_name:  # Only write if we found a name
                out.write(f"| {clean(item_name)} | {clean(pfs)} | {clean(source)} | {clean(rarity)} | {clean(trait)} | {clean(category)} | {clean(subcategory)} | {clean(level)} | {clean(price)} | {clean(bulk)} | {clean(usage)} |\n")
    
    print(f"Equipment markdown table created: {output_file}")


def parse_creatures(input_file, output_file):
    """Parse creatures.txt and create markdown table"""
    
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find where data starts
    start_idx = None
    for i, line in enumerate(lines):
        if 'Showing 3635 of 3635 results' in line:
            start_idx = i + 2
            break
    
    if start_idx is None:
        print("Could not find data start")
        return
    
    # Create markdown table
    with open(output_file, 'w', encoding='utf-8') as out:
        out.write("# Pathfinder 2e Creatures Database\n\n")
        out.write("Source: Archives of Nethys\n\n")
        
        # Write table header
        out.write("| Name | Creature Family | Source | Rarity | Size | Trait | Level | HP | AC | Fort | Reflex | Will | Perception | Sense | Speed |\n")
        out.write("|------|-----------------|--------|--------|------|-------|-------|----|----|------|--------|------|------------|-------|-------|\n")
        
        i = start_idx
        while i < len(lines):
            line = lines[i].strip()
            
            # Check if this is a creature name
            if line and not line.startswith('\t') and not line.startswith(' ') and any(c.isalpha() for c in line):
                creature_name = line
                i += 1
                
                # Skip empty line
                while i < len(lines) and not lines[i].strip():
                    i += 1
                
                # Check if next line is a family or source
                # Source lines typically have "pg." in them
                next_line = lines[i].strip() if i < len(lines) else ""
                if 'pg.' in next_line or 'Core' in next_line:
                    # It's a source, no family
                    family = ""
                    source = next_line
                    i += 1
                else:
                    # It's a family
                    family = next_line
                    i += 1
                    
                    # Skip empty lines
                    while i < len(lines) and not lines[i].strip():
                        i += 1
                    
                    # Get source
                    source = lines[i].strip() if i < len(lines) else ""
                    i += 1
                
                # Get line 1 with tabs: [spaces] Rarity Size [empty]
                data_line1 = lines[i] if i < len(lines) else ""
                parts1 = data_line1.split('\t')
                rarity = parts1[0].strip() if len(parts1) > 0 else ""
                size = parts1[1].strip() if len(parts1) > 1 else ""
                i += 1
                
                # Skip empty line
                while i < len(lines) and not lines[i].strip():
                    i += 1
                
                # Get Trait
                trait = lines[i].strip() if i < len(lines) else ""
                i += 1
                
                # Get line 2 with tabs: [spaces] Level HP AC Fort Reflex Will Perception [empty]
                data_line2 = lines[i] if i < len(lines) else ""
                parts2 = data_line2.split('\t')
                level = parts2[0].strip() if len(parts2) > 0 else ""
                hp = parts2[1].strip() if len(parts2) > 1 else ""
                ac = parts2[2].strip() if len(parts2) > 2 else ""
                fort = parts2[3].strip() if len(parts2) > 3 else ""
                reflex = parts2[4].strip() if len(parts2) > 4 else ""
                will = parts2[5].strip() if len(parts2) > 5 else ""
                perception = parts2[6].strip() if len(parts2) > 6 else ""
                i += 1
                
                # Skip empty line
                while i < len(lines) and not lines[i].strip():
                    i += 1
                
                # Get Sense (might be empty)
                sense = lines[i].strip() if i < len(lines) else ""
                i += 1
                
                # Skip empty lines
                while i < len(lines) and not lines[i].strip():
                    i += 1
                
                # Get Speed
                speed = lines[i].strip() if i < len(lines) else ""
                i += 1
                
                # Clean all fields
                def clean(s):
                    return s.replace('|', '\\|').replace('\n', ' ').strip()
                
                # Write row
                out.write(f"| {clean(creature_name)} | {clean(family)} | {clean(source)} | {clean(rarity)} | {clean(size)} | {clean(trait)} | {clean(level)} | {clean(hp)} | {clean(ac)} | {clean(fort)} | {clean(reflex)} | {clean(will)} | {clean(perception)} | {clean(sense)} | {clean(speed)} |\n")
            else:
                i += 1
    
    print(f"Creatures markdown table created: {output_file}")


if __name__ == "__main__":
    print("Parsing deities...")
    parse_deities("dieties.txt", "dieties.md")
    
    print("\nParsing equipment...")
    parse_equipment("equipment.txt", "equipment.md")
    
    print("\nParsing creatures...")
    parse_creatures("creatures.txt", "creatures.md")
    
    print("\nDone!")
