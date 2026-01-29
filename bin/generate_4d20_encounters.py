#!/usr/bin/env python3
"""
Generate 4d20 Random Encounter Table for Fogfen to Otari
Creates encounters by randomly selecting from MASSIVE curated pools
Each run = completely different table!
"""
import json
import random
import re

def load_json(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_lore(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read()

def get_equipment_by_level(equipment, level, rarity='common'):
    filtered = [e for e in equipment if e['level'] == level and e['rarity'] == rarity]
    return filtered if filtered else [e for e in equipment if e['level'] == max(0, level-1) and e['rarity'] == rarity]

def extract_lore_snippet(lore_text, keywords, max_length=400):
    lines = lore_text.split('\n')
    relevant_lines = []
    
    for i, line in enumerate(lines):
        if any(keyword.lower() in line.lower() for keyword in keywords):
            start = max(0, i - 1)
            end = min(len(lines), i + 4)
            relevant_lines.extend(lines[start:end])
            break
    
    snippet = ' '.join(relevant_lines).strip()
    if len(snippet) > max_length:
        snippet = snippet[:max_length].rsplit('.', 1)[0] + '.'
    
    return snippet if snippet else "The mists of Fogfen conceal ancient secrets."

# Import the massive encounter pools
from encounter_pools import DEADLY_POOL, DIFFICULT_POOL, MODERATE_POOL, EASY_POOL, NPC_POOL

def generate_combat_encounter(roll, difficulty, equipment, inner_sea_lore):
    """Select random encounter from appropriate pool"""
    pool_map = {
        'DEADLY': DEADLY_POOL,
        'DIFFICULT': DIFFICULT_POOL,
        'MODERATE': MODERATE_POOL,
        'EASY': EASY_POOL
    }
    
    encounter_template = random.choice(pool_map[difficulty])
    
    # Generate rewards
    level_map = {'DEADLY': 5, 'DIFFICULT': 4, 'MODERATE': 3, 'EASY': 2}
    level = level_map[difficulty]
    
    rewards = []
    num_items = random.randint(2, 4)
    
    for _ in range(num_items):
        item_level = random.randint(max(0, level - 1), min(4, level))
        available = get_equipment_by_level(equipment, item_level, 'common')
        
        if available:
            item = random.choice(available)
            price = item['price']
            if 'gp' in price:
                match = re.search(r'(\d+)', price)
                if match:
                    gp_value = int(match.group(1))
                    new_price = f"{max(1, gp_value // 2)} gp" if gp_value > 1 else f"{gp_value * 5} sp"
                else:
                    new_price = price
            else:
                new_price = price
            
            rewards.append({'name': item['name'], 'level': item['level'], 'price': new_price})
    
    coins = random.randint(2, level * 3)
    
    lore_snippet = extract_lore_snippet(inner_sea_lore, encounter_template.get('lore_keywords', ['Fogfen']))
    
    return {
        'roll': roll,
        'difficulty': difficulty,
        'template': encounter_template,
        'rewards': rewards,
        'coins': coins,
        'lore': lore_snippet
    }

def generate_lore_encounter(roll, inner_sea_lore):
    """Select random NPC encounter from pool"""
    npc_template = random.choice(NPC_POOL)
    
    skills = ['Diplomacy', 'Deception', 'Intimidation', 'Society', 'Occultism', 'Religion', 'Nature']
    selected_skills = random.sample(skills, 4)
    
    interactions = {}
    for skill in selected_skills:
        dc = random.randint(13, 20)
        interactions[skill] = dc
    
    lore_snippet = extract_lore_snippet(inner_sea_lore, npc_template.get('lore_keywords', ['Otari']))
    
    gifts = [
        "Good luck charm (+1 circumstance bonus to next save)",
        "Detailed map of safe paths (saves 2 hours travel)",
        "Letter of introduction to Otari contact",
        "Minor healing potion",
        "Valuable Gauntlight information",
    ]
    
    return {
        'roll': roll,
        'difficulty': 'LORE ONLY',
        'template': npc_template,
        'interactions': interactions,
        'lore': lore_snippet,
        'gift': random.choice(gifts)
    }

def write_markdown(encounters, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# 4D20 RANDOM ENCOUNTER TABLE — FOGFEN TO OTARI V2\n")
        f.write("**Bell Curve Distribution (4d20 = 4-80)**\n\n")
        f.write("**RANDOMLY GENERATED** - Each run creates new encounters!\n\n")
        f.write("---\n\n")
        
        f.write("## DISTRIBUTION GUIDE\n")
        f.write("- **4-9**: DEADLY | **10-19**: DIFFICULT | **20-29**: MODERATE\n")
        f.write("- **30-31**: EASY | **32-52**: LORE ONLY | **53-54**: EASY\n")
        f.write("- **55-64**: MODERATE | **65-74**: DIFFICULT | **75-80**: DEADLY\n\n")
        f.write("---\n\n")
        
        current_diff = None
        for enc in sorted(encounters, key=lambda x: x['roll']):
            if enc['difficulty'] != current_diff:
                current_diff = enc['difficulty']
                f.write(f"\n## {enc['difficulty']} ENCOUNTERS\n\n")
            
            f.write(f"### Roll: {enc['roll']}\n\n")
            
            if enc['difficulty'] == 'LORE ONLY':
                t = enc['template']
                f.write(f"**Title:** THE {t['name'].upper()}\n\n")
                f.write(f"**Setup:** {t['setup']}\n\n")
                f.write(f"**Read-Aloud:** *{t['readaloud']}*\n\n")
                f.write(f"**NPC:** {t['name']}\n*No combat*\n\n")
                f.write(f"**Lore (Inner Sea):** {enc['lore']}\n\n")
                f.write(f"**Interaction Opportunities:**\n")
                for skill, dc in enc['interactions'].items():
                    f.write(f"- **{skill} DC {dc}**\n")
                f.write(f"\n**GM Notes:** {t['personality']} | Knows: {t['knowledge']}\n\n")
                f.write(f"**Reward:** {enc['gift']}\n\n")
            else:
                t = enc['template']
                f.write(f"**Title:** THE {t['name'].upper()}\n\n")
                f.write(f"**Setup:** {t['setup']}\n\n")
                f.write(f"**Read-Aloud:** *{t['readaloud']}*\n\n")
                f.write(f"**Creature:** {t['name']}\n")
                f.write(f"HP: {t['hp']} | AC: {t['ac']} | Fort: {t['fort']} | Reflex: {t['reflex']} | Will: {t['will']}\n\n")
                f.write(f"**Lore (Inner Sea):** {enc['lore']}\n\n")
                f.write(f"**GM Notes:** {t['tactics']}\n\n")
                f.write(f"**Rewards:**\n")
                for r in enc['rewards']:
                    f.write(f"- {r['name']} (Lvl {r['level']}) - {r['price']}\n")
                f.write(f"- Coins: {enc['coins']} gp\n\n")
            
            f.write("---\n\n")

if __name__ == "__main__":
    print("Loading data...")
    equipment = load_json("etc/equipment.json")
    inner_sea_lore = load_lore("etc/inner_sea_region.md")
    
    print(f"  Equipment: {len(equipment)} items")
    print(f"  Lore: {len(inner_sea_lore)} chars")
    print(f"  Encounter pools: {len(DEADLY_POOL)} deadly, {len(DIFFICULT_POOL)} difficult,", end=" ")
    print(f"{len(MODERATE_POOL)} moderate, {len(EASY_POOL)} easy, {len(NPC_POOL)} NPCs")
    
    print("\nGenerating encounters...")
    encounters = []
    
    for roll in range(4, 81):
        if roll <= 9 or roll >= 75:
            diff = 'DEADLY'
        elif roll <= 19 or roll >= 65:
            diff = 'DIFFICULT'
        elif roll <= 29 or roll >= 55:
            diff = 'MODERATE'
        elif roll <= 31 or roll >= 53:
            diff = 'EASY'
        else:
            diff = 'LORE ONLY'
        
        if diff == 'LORE ONLY':
            enc = generate_lore_encounter(roll, inner_sea_lore)
        else:
            enc = generate_combat_encounter(roll, diff, equipment, inner_sea_lore)
        
        encounters.append(enc)
    
    write_markdown(encounters, "gm/4d20_fogfen_otari_encounters_v2.md")
    
    print(f"\n✓ Generated {len(encounters)} encounters!")
    print(f"  - {len([e for e in encounters if e['difficulty'] == 'LORE ONLY'])} lore encounters")
    print(f"  - {len([e for e in encounters if e['difficulty'] != 'LORE ONLY'])} combat encounters")
    print("\nOutput: gm/4d20_fogfen_otari_encounters_v2.md")
