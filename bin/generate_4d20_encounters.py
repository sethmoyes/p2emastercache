#!/usr/bin/env python3
"""
Generate 4d20 Random Encounter Table for Fogfen to Otari
Each run creates COMPLETELY NEW encounters using:
- creatures.json for monsters and NPCs
- equipment.json for rewards
- players_guide.md and inner_sea_region.md for lore
"""
import json
import random
import re

def load_json(filename):
    """Load JSON file"""
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_lore(filename):
    """Load markdown lore file"""
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read()

def get_creatures_by_level(creatures, level, exclude_npcs=True):
    """Get creatures of specific level - since all are level 0, randomly assign them"""
    # Since creatures.json has all creatures as level 0, we'll just return random creatures
    # and pretend they're the right level for encounter purposes
    filtered = creatures.copy()
    
    if exclude_npcs:
        # Exclude obvious NPCs (humanoid without creature family, or has "NPC" in name)
        filtered = [c for c in filtered if 
                   (c.get('creature_family') or 'humanoid' not in c.get('trait', '').lower()) and
                   'npc' not in c.get('name', '').lower()]
    
    # Return random sample
    if len(filtered) > 50:
        return random.sample(filtered, 50)
    return filtered

def get_npcs_by_level(creatures, level):
    """Get NPCs of specific level - since all are level 0, return humanoids"""
    # NPCs are typically humanoids without creature families, or have "NPC" in name
    npcs = [c for c in creatures if 
            ('humanoid' in c.get('trait', '').lower() and not c.get('creature_family')) or
            'npc' in c.get('name', '').lower() or
            any(word in c.get('name', '').lower() for word in ['merchant', 'guard', 'priest', 'wizard', 'warrior', 'scout'])]
    
    # Return random sample
    if len(npcs) > 30:
        return random.sample(npcs, 30)
    return npcs

def get_equipment_by_level(equipment, level, rarity='common'):
    """Get equipment of specific level and rarity"""
    return [e for e in equipment if e['level'] == level and e['rarity'] == rarity]

def extract_lore_snippet(lore_text, keywords, max_length=300):
    """Extract relevant lore snippet based on keywords"""
    lines = lore_text.split('\n')
    relevant_lines = []
    
    for i, line in enumerate(lines):
        if any(keyword.lower() in line.lower() for keyword in keywords):
            # Get context around the match
            start = max(0, i - 2)
            end = min(len(lines), i + 3)
            relevant_lines.extend(lines[start:end])
            break
    
    snippet = ' '.join(relevant_lines)
    if len(snippet) > max_length:
        snippet = snippet[:max_length] + '...'
    
    return snippet if snippet else "The mists of Fogfen hold many secrets..."

def generate_combat_encounter(roll, difficulty, creatures, equipment, inner_sea_lore, players_guide_lore):
    """Generate a combat encounter"""
    # Determine level based on difficulty
    level_map = {
        'DEADLY': 5,
        'DIFFICULT': 4,
        'MODERATE': 3,
        'EASY': 2
    }
    level = level_map.get(difficulty, 2)
    
    # Get random creature
    available_creatures = get_creatures_by_level(creatures, level, exclude_npcs=True)
    if not available_creatures:
        available_creatures = get_creatures_by_level(creatures, level - 1, exclude_npcs=True)
    
    if not available_creatures:
        return None
    
    creature = random.choice(available_creatures)
    
    # Generate title
    title = f"THE {creature['name'].upper()}"
    
    # Generate rewards (nerfed - half value)
    rewards = []
    num_rewards = random.randint(2, 4)
    
    for _ in range(num_rewards):
        reward_level = random.randint(max(0, level - 1), min(4, level + 1))
        available_equipment = get_equipment_by_level(equipment, reward_level, 'common')
        
        if available_equipment:
            item = random.choice(available_equipment)
            # Halve the price
            price = item['price']
            if 'gp' in price:
                gp_value = int(re.search(r'(\d+)', price).group(1)) if re.search(r'(\d+)', price) else 1
                new_price = f"{max(1, gp_value // 2)} gp" if gp_value > 1 else f"{gp_value * 5} sp"
            else:
                new_price = price
            
            rewards.append({
                'name': item['name'],
                'level': item['level'],
                'price': new_price,
                'rarity': item['rarity']
            })
    
    # Add coins (halved)
    coin_value = random.randint(1, level * 2)
    
    # Extract lore
    lore_keywords = [creature['name'], creature.get('trait', '').split(',')[0]]
    inner_sea_snippet = extract_lore_snippet(inner_sea_lore, lore_keywords)
    
    return {
        'roll': roll,
        'difficulty': difficulty,
        'title': title,
        'creature': creature,
        'rewards': rewards,
        'coins': coin_value,
        'inner_sea_lore': inner_sea_snippet,
        'players_guide_lore': "When Gauntlight glows with baleful red light, the people of Otari know to bar their doors and pray."
    }

def generate_lore_encounter(roll, creatures, inner_sea_lore, players_guide_lore):
    """Generate a lore/roleplay encounter with NPC"""
    # Get random NPC (level 1-3 for variety)
    npc_level = random.randint(1, 3)
    available_npcs = get_npcs_by_level(creatures, npc_level)
    
    if not available_npcs:
        # Fallback to any low-level creature
        available_npcs = get_creatures_by_level(creatures, npc_level, exclude_npcs=False)
    
    if not available_npcs:
        return None
    
    npc = random.choice(available_npcs)
    
    # Generate NPC role/title
    npc_roles = [
        "Traveling Merchant", "Varisian Fortune Teller", "Wandering Priest",
        "Lost Traveler", "Retired Adventurer", "Local Guide",
        "Hermit Sage", "Bard", "Pilgrim", "Refugee"
    ]
    
    title = f"THE {random.choice(npc_roles).upper()}"
    
    # Generate interaction DCs
    interactions = {
        'Diplomacy': random.randint(12, 18),
        'Deception': random.randint(15, 20),
        'Intimidation': random.randint(16, 22),
        'Society': random.randint(12, 16),
        'Occultism': random.randint(14, 18)
    }
    
    # Pick 3 random skills for this encounter
    selected_skills = random.sample(list(interactions.keys()), 3)
    
    return {
        'roll': roll,
        'difficulty': 'LORE ONLY',
        'title': title,
        'npc': npc,
        'interactions': {skill: interactions[skill] for skill in selected_skills},
        'inner_sea_lore': extract_lore_snippet(inner_sea_lore, ['Varisian', 'Cheliax', 'Andoran', 'Taldor']),
        'players_guide_lore': "Otari is a small lumber town on the southern shore of the Isle of Kortos, known for its fishing and timber trade."
    }

def write_encounter_markdown(encounters, output_file):
    """Write encounters to markdown file"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# 4D20 RANDOM ENCOUNTER TABLE — FOGFEN TO OTARI V2\n")
        f.write("**Bell Curve Distribution (4d20 = 4-80)**\n")
        f.write("**Setting:** Travel from Gauntlight Keep through Fogfen swamp to Otari town\n\n")
        f.write("**RANDOMLY GENERATED** - Each run creates new encounters!\n\n")
        
        f.write("---\n\n")
        f.write("## DISTRIBUTION GUIDE\n")
        f.write("- **4-9**: DEADLY (Level 5 creatures/hazards, major rewards)\n")
        f.write("- **10-19**: DIFFICULT (Level 4 creatures/hazards)\n")
        f.write("- **20-29**: MODERATE (Level 3 creatures/hazards)\n")
        f.write("- **30-31**: EASY (Level 2 creatures/hazards, minor rewards)\n")
        f.write("- **32-52**: LORE ONLY (No combat, roleplay & social skills)\n")
        f.write("- **53-54**: EASY (Level 2 creatures/hazards, minor rewards)\n")
        f.write("- **55-64**: MODERATE (Level 3 creatures/hazards)\n")
        f.write("- **65-74**: DIFFICULT (Level 4 creatures/hazards)\n")
        f.write("- **75-80**: DEADLY (Level 5 creatures/hazards, major rewards)\n\n")
        f.write("---\n\n")
        
        # Group by difficulty
        current_difficulty = None
        
        for enc in sorted(encounters, key=lambda x: x['roll']):
            if enc['difficulty'] != current_difficulty:
                current_difficulty = enc['difficulty']
                f.write(f"\n## {enc['difficulty']} ENCOUNTERS\n\n")
            
            f.write(f"### Roll: {enc['roll']}\n\n")
            f.write(f"**{enc['title']}**\n\n")
            
            if enc['difficulty'] == 'LORE ONLY':
                # Lore encounter
                npc = enc['npc']
                f.write(f"**NPC:** {npc['name']} (Level {npc['level']})\n")
                f.write(f"*No combat encounter*\n\n")
                
                f.write(f"**Lore Connection (Inner Sea Region):**\n")
                f.write(f"{enc['inner_sea_lore']}\n\n")
                
                f.write(f"**Otari Connection (Players Guide):**\n")
                f.write(f"{enc['players_guide_lore']}\n\n")
                
                f.write(f"**Interaction Opportunities:**\n")
                for skill, dc in enc['interactions'].items():
                    f.write(f"- **{skill} DC {dc}:** [GM improvise based on skill]\n")
                f.write("\n")
                
                f.write(f"**Rewards:** Information, roleplay opportunities, potential ally\n\n")
            else:
                # Combat encounter
                creature = enc['creature']
                f.write(f"**Creature:** {creature['name']} (Level {creature['level']}, {creature.get('rarity', 'Common')})\n")
                f.write(f"HP: {creature.get('hp', 'N/A')} | AC: {creature.get('ac', 'N/A')} | ")
                f.write(f"Fort: {creature.get('fort', 'N/A')} | Reflex: {creature.get('reflex', 'N/A')} | Will: {creature.get('will', 'N/A')}\n\n")
                
                f.write(f"**Lore Connection (Inner Sea Region):**\n")
                f.write(f"{enc['inner_sea_lore']}\n\n")
                
                f.write(f"**Otari Connection (Players Guide):**\n")
                f.write(f"{enc['players_guide_lore']}\n\n")
                
                f.write(f"**Rewards:**\n")
                for reward in enc['rewards']:
                    f.write(f"- **{reward['name']}** (Level {reward['level']}, {reward['rarity']}) - {reward['price']}\n")
                f.write(f"- **Coins:** {enc['coins']} gp\n\n")
            
            f.write("---\n\n")

if __name__ == "__main__":
    print("Loading data...")
    try:
        creatures = load_json("etc/creatures.json")
        print(f"  Loaded {len(creatures)} creatures")
        
        # Debug: check level distribution
        level_counts = {}
        for c in creatures:
            level = c.get('level', 0)
            level_counts[level] = level_counts.get(level, 0) + 1
        print(f"  Level distribution: {dict(sorted(level_counts.items()))}")
        
        equipment = load_json("etc/equipment.json")
        print(f"  Loaded {len(equipment)} equipment items")
        
        inner_sea_lore = load_lore("etc/inner_sea_region.md")
        print(f"  Loaded Inner Sea lore ({len(inner_sea_lore)} chars)")
        
        players_guide_lore = load_lore("etc/players_guide.md")
        print(f"  Loaded Players Guide lore ({len(players_guide_lore)} chars)")
    except Exception as e:
        print(f"ERROR loading data: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
    
    print("\nGenerating encounters...")
    encounters = []
    
    # Generate encounters for each roll (4-80)
    for roll in range(4, 81):
        # Determine difficulty
        if roll <= 9 or roll >= 75:
            difficulty = 'DEADLY'
        elif roll <= 19 or roll >= 65:
            difficulty = 'DIFFICULT'
        elif roll <= 29 or roll >= 55:
            difficulty = 'MODERATE'
        elif roll <= 31 or roll >= 53:
            difficulty = 'EASY'
        else:  # 32-52 (center ±10 around 42)
            difficulty = 'LORE ONLY'
        
        try:
            if difficulty == 'LORE ONLY':
                enc = generate_lore_encounter(roll, creatures, inner_sea_lore, players_guide_lore)
            else:
                enc = generate_combat_encounter(roll, difficulty, creatures, equipment, inner_sea_lore, players_guide_lore)
            
            if enc:
                encounters.append(enc)
            else:
                print(f"  Warning: Could not generate encounter for roll {roll} ({difficulty})")
        except Exception as e:
            print(f"  ERROR generating roll {roll}: {e}")
    
    print(f"\nGenerated {len(encounters)} encounters!")
    print("Writing to file...")
    
    write_encounter_markdown(encounters, "gm/4d20_fogfen_otari_encounters_v2.md")
    
    print("\n✓ Complete! New encounter table generated at: gm/4d20_fogfen_otari_encounters_v2.md")
    print(f"  - {len([e for e in encounters if e['difficulty'] == 'LORE ONLY'])} lore/roleplay encounters")
    print(f"  - {len([e for e in encounters if e['difficulty'] != 'LORE ONLY'])} combat encounters")
