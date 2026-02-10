#!/usr/bin/env python3
"""
Dungeon Turn Encounter Generator for Pathfinder 2e

This script implements a "dice jar" system where every 10-minute exploration activity
adds a die to the jar. At 5 dice, roll all 5d20 and check for encounters.

Generates encounters for all floors from 1 to X (where X is current floor).
"""

import random
import sys
import os
import re
import json

def roll_dice_jar(num_dice=5):
    """Roll the dice jar and return individual rolls and sum"""
    rolls = [random.randint(1, 20) for _ in range(num_dice)]
    total = sum(rolls)
    return rolls, total

def parse_gauntlight_levels(filepath='etc/gauntlight_keep_levels.md'):
    """Parse the Gauntlight Keep markdown file to extract level information"""
    levels = {}
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract each level section
        level_pattern = r'### Level (\d+): (.+?)\n(.*?)(?=### Level|\n---|\Z)'
        matches = re.finditer(level_pattern, content, re.DOTALL)
        
        for match in matches:
            level_num = int(match.group(1))
            level_name = match.group(2).strip()
            level_content = match.group(3).strip()
            
            # Extract theme
            theme_match = re.search(r'\*\*Theme:\*\* (.+)', level_content)
            theme = theme_match.group(1) if theme_match else ""
            
            # Extract key features
            features = []
            features_section = re.search(r'\*\*Key Features:\*\*(.*?)(?=\*\*|$)', level_content, re.DOTALL)
            if features_section:
                feature_lines = features_section.group(1).strip().split('\n')
                features = [line.strip('- ').strip() for line in feature_lines if line.strip().startswith('-')]
            
            # Extract threats
            threats = []
            threats_section = re.search(r'\*\*Threats:\*\* (.+)', level_content)
            if threats_section:
                threats = [t.strip() for t in threats_section.group(1).split(',')]
            
            levels[level_num] = {
                'name': level_name,
                'theme': theme,
                'features': features,
                'threats': threats
            }
    
    except FileNotFoundError:
        print(f"Warning: Could not find {filepath}, using fallback data")
        return None
    
    return levels

def generate_level_flavor_events(level_num, level_data):
    """Generate flavor events specific to a dungeon level"""
    if not level_data:
        return []
    
    name = level_data['name']
    theme = level_data['theme']
    features = level_data['features']
    
    # Load floor-specific events from JSON file
    try:
        with open('etc/dungeon_flavor_events.json', 'r', encoding='utf-8') as f:
            floor_specific_events = json.load(f)
    except FileNotFoundError:
        print("Warning: Could not find etc/dungeon_flavor_events.json, using fallback")
        floor_specific_events = {}
    except json.JSONDecodeError as e:
        print(f"Warning: Error parsing etc/dungeon_flavor_events.json: {e}")
        floor_specific_events = {}
    
    # Get floor-specific events (convert level_num to string for JSON keys)
    events = floor_specific_events.get(str(level_num), [])
    
    # If no floor-specific events, generate from features
    if not events:
        for feature in features:
            feature_clean = feature.strip()
            if feature_clean:
                events.append({
                    "title": f"Evidence of {feature_clean[:40]}",
                    "description": f"You discover clear signs of {feature_clean.lower()}. The remnants tell a story of this level's dark purpose.",
                    "teaching": f"Reveals: {feature_clean}"
                })
    
    # Add theme-based event as fallback
    if theme and len(events) < 5:
        events.append({
            "title": f"Atmosphere: {name}",
            "description": f"{theme} The oppressive atmosphere weighs heavily on you.",
            "teaching": f"Establishes the mood and theme of {name}"
        })
    
    return events

def generate_level_encounters(level_num, level_data, party_level):
    """Generate encounters specific to a dungeon level"""
    if not level_data:
        return []
    
    threats = level_data['threats']
    encounters = []
    
    # Named NPCs and specific entities that should NEVER be random encounters
    # These are major story beats, bosses, or unique NPCs
    forbidden_names = [
        'BOSS', 'EXTREME', 'King Graulgust', 'Nhakazarin', 'Volluk', 'Voidglutton',
        'Jaul Mezmin', 'Vaulgrist', 'Cratonys', 'Jafaki', 'Urevian', 'Ysondkhelir',
        'Sacuisha', 'Cynemi', 'Urthagul', 'Froghemoth', 'Quara', 'Khurfel',
        'Belcorra', 'Lady\'s Whisper', 'Ravirex', 'Caliddo', 'lazy naga',
        'living flesh golem', 'shanrigol behemoth', 'goliath spider'
    ]
    
    # Things that are definitely hazards, not creatures
    hazard_types = [
        'trap', 'hazard', 'environmental', 'wards', 'barrier', 'effect', 'challenge',
        'manifestation', 'warping', 'sinkhole', 'magical'
    ]
    
    # Map generic threat types to specific creatures from creatures.json
    creature_specifics = {
        'Mitflits': ['Mitflit Scout', 'Mitflit Scavenger'],
        'Morlocks': ['Morlock Scavenger', 'Morlock Engineer'],
        'Ghouls': ['Ghoul Stalker', 'Ghoul Soldier'],
        'undead': ['Skeleton Guard', 'Zombie Shambler'],
        'basic undead': ['Skeleton Guard', 'Zombie Shambler'],
        'undead servants': ['Skeleton Guard', 'Zombie Shambler'],
        'web lurkers': ['Web Lurker'],
        'animated books': ['Animated Statue'],  # Placeholder - use construct
        'zebubs': ['Zebub (Accuser Devil)'],
        'Arena beasts': ['Hell Hound', 'Manticore'],
        'fleshwarped creatures': ['Grothlut', 'Drider'],
        'devils': ['Lemure', 'Imp'],
        'grothluts': ['Grothlut'],
        'seugathi researchers': ['Seugathi'],
        'driders': ['Drider'],
        'destrachan': ['Destrachan'],
        'giant crawling hand': ['Crawling Hand'],
        'will-o\'-wisps': ['Will-o\'-Wisp'],
        'bodaks': ['Bodak'],
        'caligni cultists': ['Caligni Creeper', 'Caligni Dancer'],
        'urdefhan war bands': ['Urdefhan Hunter', 'Urdefhan Warrior'],
        'drow patrols': ['Drow Fighter', 'Drow Rogue'],
        'caligni factions': ['Caligni Creeper', 'Caligni Dancer'],
        'derghodaemon': ['Derghodaemon'],
        'Darklands fauna': ['Cave Scorpion', 'Giant Bat']
    }
    
    # Generate encounters based on threats
    for threat in threats:
        threat_clean = threat.strip()
        if not threat_clean:
            continue
        
        # SKIP anything with forbidden names
        if any(name.lower() in threat_clean.lower() for name in forbidden_names):
            continue
        
        # SKIP if the ENTIRE threat is in parentheses (like descriptions)
        # But allow threats like "Ghouls (Cult of the Canker)" - just remove the parenthetical part
        if threat_clean.startswith('(') and threat_clean.endswith(')'):
            continue
        
        # Remove parenthetical descriptions but keep the main threat
        # "Ghouls (Cult of the Canker)" becomes "Ghouls"
        if '(' in threat_clean:
            threat_clean = threat_clean.split('(')[0].strip()
        
        # Determine if it's a hazard or creature
        is_hazard = any(word in threat_clean.lower() for word in hazard_types)
        
        if is_hazard:
            # Generate better descriptions for specific hazard types
            if 'sinkhole' in threat_clean.lower():
                desc = "The floor beneath you suddenly gives way! A sinkhole opens up, threatening to swallow you into the darkness below."
            elif 'manifestation' in threat_clean.lower():
                desc = f"Reality warps around you as {threat_clean.lower()} appear, drawn by the dungeon's dark power."
            elif 'challenge' in threat_clean.lower():
                desc = f"You face {threat_clean.lower()} - tests designed to prove your worth or break your spirit."
            elif 'warping' in threat_clean.lower():
                desc = "The fabric of reality twists and bends unnaturally. The laws of physics seem negotiable here."
            else:
                desc = f"You trigger {threat_clean.lower()} - a remnant of the dungeon's defenses."
            
            encounters.append({
                "title": f"{threat_clean}",
                "description": desc,
                "hazard": f"DC {13 + party_level} save or take 2d6 damage",
                "difficulty": f"Level {max(1, party_level - 2)} Hazard"
            })
        else:
            # Get specific creature name if available
            specific_creature = None
            for generic, specifics in creature_specifics.items():
                if generic.lower() in threat_clean.lower():
                    specific_creature = random.choice(specifics)
                    break
            
            if specific_creature:
                encounters.append({
                    "title": f"Wandering {specific_creature}",
                    "description": f"You encounter a {specific_creature.lower()} in this area.",
                    "encounter": f"1 {specific_creature} (Level {max(1, party_level - 2)})",
                    "difficulty": "Low threat encounter"
                })
            else:
                # Fallback to generic
                encounters.append({
                    "title": f"Wandering {threat_clean}",
                    "description": f"You encounter {threat_clean.lower()} in this area.",
                    "encounter": f"1-2 {threat_clean} (Level {max(1, party_level - 2)})",
                    "difficulty": "Low threat encounter"
                })
    
    return encounters

# Generic beneficial events
BENEFICIAL_EVENTS = [
    {
        "title": "Hidden Cache",
        "description": "You discover a hidden cache left by previous adventurers! It contains basic supplies and a note: 'If you're reading this, you made it further than we did. Good luck.'",
        "reward": "Roll 1d4: 1) 2d6 gp, 2) 1d3 healing potions (minor), 3) Useful tool, 4) Treasure map fragment",
        "difficulty": "None - Beneficial"
    },
    {
        "title": "Fortunate Timing",
        "description": "You hear footsteps approaching and quickly hide. A patrol passes by without noticing you. That was close.",
        "reward": "Avoided an encounter - no combat",
        "difficulty": "None - Beneficial"
    },
    {
        "title": "Helpful Spirit",
        "description": "A translucent figure appears briefly, pointing away from danger and whispering 'Not that way...' before fading.",
        "reward": "Gain advantage on next trap/hazard detection",
        "difficulty": "None - Beneficial"
    },
    {
        "title": "Lucky Find",
        "description": "You spot a trap before triggering it. Someone else wasn't so lucky - their skeleton lies nearby with a small pouch of coins.",
        "reward": "1d6 gp and avoid trap damage",
        "difficulty": "None - Beneficial"
    }
]

def get_encounter_category(total):
    """Determine encounter category based on 5d20 sum"""
    if total <= 35:
        return "beneficial"
    elif total <= 52:
        return "flavor_low"
    elif total <= 69:
        return "flavor_high"
    else:
        return "threat"

def generate_dungeon_turn_encounter(party_level, dungeon_level, levels_data):
    """Generate a dungeon turn encounter for a specific level"""
    
    # Roll the dice jar
    rolls, total = roll_dice_jar()
    
    # Determine category
    category = get_encounter_category(total)
    
    # Get level data
    level_data = levels_data.get(dungeon_level) if levels_data else None
    level_name = level_data['name'] if level_data else f"Level {dungeon_level}"
    
    # Build result
    result = {
        "rolls": rolls,
        "total": total,
        "category": category,
        "party_level": party_level,
        "dungeon_level": dungeon_level,
        "dungeon_level_name": level_name
    }
    
    # Select appropriate encounter
    if category == "beneficial":
        # Very low rolls - beneficial outcomes
        encounter = random.choice(BENEFICIAL_EVENTS)
        result["type"] = "Beneficial Event"
        result["encounter"] = encounter
        
    elif category in ["flavor_low", "flavor_high"]:
        # Middle 50% - flavor events
        flavor_events = generate_level_flavor_events(dungeon_level, level_data)
        if flavor_events:
            encounter = random.choice(flavor_events)
        else:
            # Fallback
            encounter = {
                "title": "Dungeon Atmosphere",
                "description": f"The oppressive atmosphere of {level_name} weighs on you. Every shadow seems to hide danger.",
                "teaching": "Establishes dungeon mood"
            }
        result["type"] = "Flavor Event"
        result["encounter"] = encounter
        
    else:  # threat
        # High rolls - actual hazards/encounters
        level_encounters = generate_level_encounters(dungeon_level, level_data, party_level)
        if level_encounters:
            encounter = random.choice(level_encounters)
        else:
            # Fallback
            encounter = {
                "title": "Generic Hazard",
                "description": "You trigger an old trap mechanism.",
                "hazard": f"DC {13 + party_level} Reflex save or take 2d6 damage",
                "difficulty": f"Level {party_level - 2} Hazard"
            }
        result["type"] = "Hazard/Encounter"
        result["encounter"] = encounter
    
    return result

def format_encounter_output(result):
    """Format the encounter result for display"""
    output = []
    output.append("=" * 70)
    output.append("DUNGEON TURN ENCOUNTER")
    output.append("=" * 70)
    output.append(f"Location: {result['dungeon_level_name']} (Level {result['dungeon_level']})")
    output.append(f"Party Level: {result['party_level']}")
    output.append("")
    output.append(f"Dice Rolled: {' + '.join(map(str, result['rolls']))} = {result['total']}")
    output.append(f"Category: {result['category'].upper()}")
    output.append("")
    output.append("-" * 70)
    output.append(f"TYPE: {result['type']}")
    output.append("-" * 70)
    output.append("")
    
    enc = result['encounter']
    output.append(f"## {enc['title']}")
    output.append("")
    output.append(f"**Description:** {enc['description']}")
    output.append("")
    
    if 'teaching' in enc:
        output.append(f"**What This Teaches:** {enc['teaching']}")
        output.append("")
    
    if 'reward' in enc:
        output.append(f"**Reward:** {enc['reward']}")
        output.append("")
    
    if 'hazard' in enc:
        output.append(f"**Hazard:** {enc['hazard']}")
        output.append("")
    
    if 'encounter' in enc:
        output.append(f"**Encounter:** {enc['encounter']}")
        output.append("")
    
    if 'difficulty' in enc:
        output.append(f"**Difficulty:** {enc['difficulty']}")
        output.append("")
    
    output.append("=" * 70)
    
    return "\n".join(output)

def generate_all_encounters_markdown(party_level, max_floor, levels_data, output_file):
    """Generate a comprehensive markdown file with all possible encounters"""
    
    print(f"Generating comprehensive encounter table for floors 1-{max_floor}...")
    print(f"Party Level: {party_level}")
    print(f"Total encounters to generate: {96 * max_floor} (96 sums per floor)")
    print("")
    
    lines = []
    
    # Header
    lines.append("# Dungeon Turn Encounters - Gauntlight Keep")
    lines.append("")
    lines.append(f"**Party Level:** {party_level}")
    lines.append(f"**Floors Covered:** 1-{max_floor}")
    lines.append(f"**Generated:** {96 * max_floor} encounters (sums 5-100 for each floor)")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## How to Use")
    lines.append("")
    lines.append("1. When the dice jar reaches 5 dice, roll all 5d20")
    lines.append("2. Sum the total")
    lines.append("3. Find your current floor level below")
    lines.append("4. Look up the sum in that floor's table")
    lines.append("5. Read the encounter to your players")
    lines.append("")
    lines.append("## Probability Distribution")
    lines.append("")
    lines.append("- **5-35:** Beneficial/Very Minor (~10%)")
    lines.append("- **36-52:** Flavor Events - Low (~20%)")
    lines.append("- **53-69:** Flavor Events - High (~20%)")
    lines.append("- **70-100:** Hazards/Encounters (~10%)")
    lines.append("")
    lines.append("The middle 50% (36-69) are flavor events that teach about the world.")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Generate encounters for each floor
    for floor in range(1, max_floor + 1):
        level_data = levels_data.get(floor) if levels_data else None
        level_name = level_data['name'] if level_data else f"Level {floor}"
        
        print(f"Generating encounters for Floor {floor}: {level_name}...")
        
        lines.append(f"# Floor {floor}: {level_name}")
        lines.append("")
        
        if level_data and level_data.get('theme'):
            lines.append(f"**Theme:** {level_data['theme']}")
            lines.append("")
        
        lines.append("---")
        lines.append("")
        
        # Generate all 96 possible sums (5-100)
        for dice_sum in range(5, 101):
            category = get_encounter_category(dice_sum)
            
            # Generate encounter based on category
            if category == "beneficial":
                encounter = random.choice(BENEFICIAL_EVENTS)
                enc_type = "Beneficial Event"
            elif category in ["flavor_low", "flavor_high"]:
                flavor_events = generate_level_flavor_events(floor, level_data)
                if flavor_events:
                    encounter = random.choice(flavor_events)
                else:
                    encounter = {
                        "title": "Dungeon Atmosphere",
                        "description": f"The oppressive atmosphere of {level_name} weighs on you.",
                        "teaching": "Establishes dungeon mood"
                    }
                enc_type = "Flavor Event"
            else:  # threat
                level_encounters = generate_level_encounters(floor, level_data, party_level)
                if level_encounters:
                    encounter = random.choice(level_encounters)
                else:
                    encounter = {
                        "title": "Generic Hazard",
                        "description": "You trigger an old trap mechanism.",
                        "hazard": f"DC {13 + party_level} Reflex save or take 2d6 damage",
                        "difficulty": f"Level {party_level - 2} Hazard"
                    }
                enc_type = "Hazard/Encounter"
            
            # Format encounter
            lines.append(f"## Sum: {dice_sum} - {enc_type}")
            lines.append("")
            lines.append(f"### {encounter['title']}")
            lines.append("")
            lines.append(f"**Description:** {encounter['description']}")
            lines.append("")
            
            if 'teaching' in encounter:
                lines.append(f"**What This Teaches:** {encounter['teaching']}")
                lines.append("")
            
            if 'reward' in encounter:
                lines.append(f"**Reward:** {encounter['reward']}")
                lines.append("")
            
            if 'hazard' in encounter:
                lines.append(f"**Hazard:** {encounter['hazard']}")
                lines.append("")
            
            if 'encounter' in encounter:
                lines.append(f"**Encounter:** {encounter['encounter']}")
                lines.append("")
            
            if 'difficulty' in encounter:
                lines.append(f"**Difficulty:** {encounter['difficulty']}")
                lines.append("")
            
            lines.append("---")
            lines.append("")
        
        print(f"  [OK] Generated {96} encounters for Floor {floor}")
        lines.append("")
    
    # Write to file
    print(f"\nWriting to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"[OK] Complete! Generated {96 * max_floor} encounters")
    print(f"[OK] File saved: {output_file}")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate Dungeon Turn Encounters')
    parser.add_argument('--level', type=int, default=4, help='Party level (default: 4)')
    parser.add_argument('--floors', type=int, default=1, help='Number of floors to generate (1 to X)')
    parser.add_argument('--output', type=str, default='gm/dungeon_turn_encounters.md', help='Output file path')
    parser.add_argument('--stats', action='store_true', help='Show probability statistics')
    parser.add_argument('--generate-all', action='store_true', help='Generate comprehensive encounter table for all floors')
    
    args = parser.parse_args()
    
    if args.stats:
        # Show probability distribution
        print("=" * 70)
        print("DUNGEON TURN PROBABILITY DISTRIBUTION (5d20)")
        print("=" * 70)
        print(f"Minimum: 5 (all 1s)")
        print(f"Maximum: 100 (all 20s)")
        print(f"Mean: 52.5")
        print(f"Median: 52-53")
        print("")
        print("ENCOUNTER CATEGORIES:")
        print(f"  5-35:  Beneficial/Very Minor (~10%)")
        print(f"  36-52: Flavor Events - Low (~20%)")
        print(f"  53-69: Flavor Events - High (~20%)")
        print(f"  70-100: Hazards/Encounters (~10%)")
        print("")
        print("The middle 50% (36-69) are flavor events that teach about the world.")
        print("The outer 50% include beneficial events, hazards, and encounters.")
        print("=" * 70)
        return
    
    # Parse Gauntlight levels
    levels_data = parse_gauntlight_levels()
    
    if not levels_data:
        print("Warning: Could not load level data from gauntlight_keep_levels.md")
        print("Using fallback encounter generation")
        print("")
    
    if args.generate_all:
        # Generate comprehensive markdown file
        generate_all_encounters_markdown(
            party_level=args.level,
            max_floor=args.floors,
            levels_data=levels_data,
            output_file=args.output
        )
    else:
        # Generate single encounter (original behavior)
        for floor in range(1, args.floors + 1):
            if floor > 1:
                print("\n\n")
            
            result = generate_dungeon_turn_encounter(
                party_level=args.level,
                dungeon_level=floor,
                levels_data=levels_data
            )
            
            print(format_encounter_output(result))

if __name__ == "__main__":
    main()
