#!/usr/bin/env python3
"""
Generate 4d20 Random Encounter Table for Fogfen to Otari
Creates DETAILED encounters with extensive lore, GM notes, and development
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

def load_creature_lore():
    """Load creature lore from JSON"""
    try:
        with open('etc/creature_lore.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def get_creature_lore_text(creature_name, creature_lore_db):
    """Get lore for a specific creature from the database"""
    # Try exact match first
    if creature_name in creature_lore_db:
        return creature_lore_db[creature_name]['lore']
    
    # Try without level indicators
    clean_name = re.sub(r'\(Level \d+\)', '', creature_name).strip()
    if clean_name in creature_lore_db:
        return creature_lore_db[clean_name]['lore']
    
    # Try partial match
    for key in creature_lore_db.keys():
        if key.lower() in creature_name.lower() or creature_name.lower() in key.lower():
            return creature_lore_db[key]['lore']
    
    return None

def get_equipment_by_level(equipment, level, rarity='common'):
    filtered = [e for e in equipment if e['level'] == level and e['rarity'] == rarity]
    return filtered if filtered else [e for e in equipment if e['level'] == max(0, level-1) and e['rarity'] == rarity]

def extract_lore_snippet(lore_text, keywords, max_length=600):
    """Extract relevant lore based on keywords"""
    lines = lore_text.split('\n')
    relevant_lines = []
    
    for i, line in enumerate(lines):
        if any(keyword.lower() in line.lower() for keyword in keywords):
            start = max(0, i - 2)
            end = min(len(lines), i + 6)
            relevant_lines.extend(lines[start:end])
            break
    
    snippet = ' '.join(relevant_lines).strip()
    
    # Remove markdown headers
    snippet = re.sub(r'^#+\s+', '', snippet, flags=re.MULTILINE)
    snippet = re.sub(r'\n#+\s+', '\n', snippet)
    
    if len(snippet) > max_length:
        snippet = snippet[:max_length].rsplit('.', 1)[0] + '.'
    
    # If no relevant snippet found, return creature-type specific lore
    if not snippet:
        snippet = get_fallback_lore(keywords)
    
    return snippet

def get_fallback_lore(keywords):
    """Generate appropriate fallback lore based on creature keywords"""
    
    # Undead-specific lore
    if any(k in ['undead', 'Urgathoa', 'Pharasma', 'zombie', 'skeleton', 'wight', 'wraith', 'vampire'] for k in keywords):
        undead_lore = [
            "Undead creatures are tragically common in the Inner Sea region, particularly near sites of ancient battles, mass graves, or places touched by necromantic magic. The goddess Urgathoa, the Pallid Princess, is patron of undead and disease, while Pharasma, the Lady of Graves, opposes all undead as abominations against the natural cycle of death and rebirth.",
            "The rise of undead is often tied to powerful necromantic rituals, cursed locations, or the lingering hatred of those who died violently. In Ustalav, entire counties are overrun with undead, while in Geb, an entire nation is ruled by undead aristocracy. Gauntlight itself was built by the necromancer Belcorra Haruvex, whose dark magic still animates the dead centuries after her defeat.",
            "Undead creatures retain fragments of their former lives—memories, skills, and hatreds that drove them in life. The most dangerous undead are those with intelligence intact, capable of planning, tactics, and spreading their curse to others. Pharasma's clergy work tirelessly to put such abominations to rest, while Urgathoa's followers see undeath as a gift.",
            "The creation of undead is considered one of the darkest forms of magic, forbidden in most civilized lands. Yet necromancers continue their work in hidden laboratories and forgotten ruins, seeking immortality or power over death itself. The undead they create often escape their control, becoming threats to all living things.",
        ]
        return random.choice(undead_lore)
    
    # Fiend-specific lore
    elif any(k in ['fiend', 'demon', 'devil', 'Cheliax', 'Asmodeus'] for k in keywords):
        fiend_lore = [
            "Fiends—demons, devils, and daemons—are extraplanar beings of pure evil that seek to corrupt, destroy, or enslave mortal souls. In Cheliax, House Thrune openly contracts with devils, binding them to service through infernal pacts. The nation's very laws are written in consultation with Hell's legalists.",
            "The Worldwound in northern Avistan serves as a permanent portal to the Abyss, from which demons pour forth in endless hordes. The crusaders of Mendev have fought for over a century to contain this threat, but demonic corruption spreads like a plague wherever these fiends tread.",
            "Devils are creatures of law and contracts, while demons embody chaos and destruction. Both seek mortal souls, but through different means—devils through temptation and bargains, demons through violence and corruption. Daemons, the third type of fiend, simply seek to end all life.",
        ]
        return random.choice(fiend_lore)
    
    # Beast/Animal lore
    elif any(k in ['beast', 'animal', 'wilderness', 'nature'] for k in keywords):
        beast_lore = [
            "The wilderness of the Inner Sea region teems with dangerous creatures, from dire wolves the size of horses to giant spiders that spin webs between ancient trees. Fogfen, the swampland between Otari and Gauntlight, is particularly notorious for its aggressive wildlife, made more dangerous by the corrupting influence of the lighthouse's dark magic.",
            "Natural predators in the region have grown bolder and more aggressive in recent years, possibly drawn by the same dark energies that animate the undead near Gauntlight. Hunters and lumber workers report encounters with creatures of unusual size and ferocity, as if the land itself has turned hostile.",
            "Varisia's untamed wilderness harbors creatures that have survived since the age of Thassilon, ancient beasts that have adapted to magical corruption and learned to thrive in cursed lands. These creatures are often more intelligent and dangerous than their mundane cousins.",
        ]
        return random.choice(beast_lore)
    
    # Aberration lore
    elif any(k in ['aberration', 'Darklands', 'madness'] for k in keywords):
        aberration_lore = [
            "Aberrations are creatures that defy natural law—beings from beyond reality, experiments gone wrong, or entities warped by exposure to alien magic. The Darklands beneath Golarion's surface are home to countless such horrors, and occasionally they find their way to the surface through forgotten tunnels or magical mishaps.",
            "The ancient empire of Thassilon experimented extensively with transmutation and conjuration magic, creating aberrations that still haunt Varisia's ruins. These creatures often possess alien intelligence and motivations incomprehensible to mortal minds.",
            "Exposure to aberrations can drive mortals mad, as the mind struggles to comprehend forms and geometries that should not exist. Scholars who study such creatures often find their sanity eroding, their dreams filled with visions of impossible angles and colors that have no name.",
        ]
        return random.choice(aberration_lore)
    
    # Giant/Humanoid lore
    elif any(k in ['giant', 'ogre', 'troll', 'goblin', 'humanoid'] for k in keywords):
        humanoid_lore = [
            "Giants and their kin have inhabited the Inner Sea region since before human civilization. In Varisia, hill giants and marsh giants claim territories in the wilderness, raiding settlements and demanding tribute. These creatures possess a crude intelligence and often serve as muscle for more cunning villains.",
            "Goblins, hobgoblins, and bugbears plague the roads and forests of the Inner Sea region. While individually weak, they gather in large tribes and can overwhelm unprepared travelers. Their chaotic nature makes them unpredictable—sometimes cowardly, sometimes suicidally brave.",
            "Trolls are among the most feared creatures in the wilderness, their regenerative abilities making them nearly impossible to kill without fire or acid. They hunt alone or in small family groups, claiming territories and devouring anything that enters their domain.",
        ]
        return random.choice(humanoid_lore)
    
    # Default fallback
    else:
        return "The mists of Fogfen conceal ancient secrets and forgotten horrors. This creature is but one of many dangers that lurk in the wilderness between Otari and Gauntlight, drawn by the lighthouse's cursed beacon or simply claiming territory in the untamed swampland."

def get_otari_connection_combat():
    """Generate Otari-specific connection for COMBAT encounters"""
    connections = [
        "When Gauntlight glows with baleful red light, the people of Otari bar their doors and pray to Pharasma. This creature is one of many drawn to the lighthouse's cursed beacon.",
        "Otari's townsfolk whisper of disappearances near Fogfen. The Lumber Consortium has lost three workers this month to creatures like this.",
        "Wrin Sivinxi at Wrin's Wonders has warned adventurers about these creatures. She's seen them in her star charts—bad omens.",
        "The Rowdy Rockfish's patrons trade stories of encounters like this. Tamily Tanderveil keeps a tally of survivors on her wall.",
        "Captain Longsaddle of the town guard has posted bounties for proof of creatures like this. Bring evidence to collect your reward.",
        "Morlibint at Odd Stories has ancient texts describing these creatures. He'll pay well for firsthand accounts.",
        "This creature was likely drawn from the depths of Gauntlight by Belcorra Haruvex's ancient magic, still pulsing after centuries.",
        "Vandy Banderdash at the Dawnflower Library has blessed many who've faced creatures like this. She offers prayers and healing to survivors.",
        "Lumber workers from Otari have reported seeing creatures like this near the old logging roads. Several have gone missing.",
        "The town guard warns travelers about these threats. Captain Longsaddle maintains a bestiary of local dangers at the garrison.",
        "Fishermen at the Otari Fishery have spotted these creatures from their boats. They avoid certain areas of Fogfen now.",
        "Jorsk Hinterclaw at Blades for Glades has repaired armor damaged by creatures like this. He knows their attack patterns.",
        "Keeleno Lathenar at Otari Market pays extra for pelts or parts from dangerous creatures. This one would fetch a good price.",
        "Tamily Tanderveil offers free drinks to anyone who brings proof of eliminating threats like this near Otari.",
        "The Lumber Consortium has posted warnings about this type of creature. They're losing too many workers to continue operations safely.",
    ]
    return random.choice(connections)

def get_otari_connection_npc():
    """Generate Otari-specific connection for NPC encounters"""
    connections = [
        "This traveler mentions they're heading to Otari for supplies. They've heard the town is welcoming to adventurers.",
        "The NPC knows several people in Otari and can provide introductions to merchants, guards, or other useful contacts.",
        "They recently passed through Otari and can share current news: the Lumber Consortium is hiring, Gauntlight has been glowing more frequently, and Captain Longsaddle is looking for capable people.",
        "This person has family in Otari—a relative works at the Otari Fishery, the Rowdy Rockfish, or one of the other local businesses.",
        "They're familiar with Otari's layout and can recommend the best places to stay, eat, and resupply. The Rowdy Rockfish has the best food, Wrin's Wonders for magic items.",
        "The NPC mentions that Otari is a good base for exploring the region. Many adventurers use it as a staging point for Gauntlight expeditions.",
        "They know Vandy Banderdash at the Dawnflower Library and can provide a letter of introduction if the party needs healing or blessings.",
        "This traveler has done business with Keeleno Lathenar at Otari Market. They can vouch for the party if they need credit or special orders.",
        "They're acquainted with Wrin Sivinxi and mention she's always interested in meeting adventurers—especially those who've seen strange omens.",
        "The NPC knows Captain Longsaddle personally and can put in a good word with the town guard if the party helps them.",
        "They mention Morlibint at Odd Stories is always buying interesting books, maps, and historical documents. The party might have something he'd want.",
        "This person recently attended a festival in Otari and speaks highly of the town's hospitality. They recommend the party visit.",
        "They know the safe routes between here and Otari, including where to find fresh water and good camping spots.",
        "The NPC has heard rumors in Otari about Gauntlight: strange lights, missing explorers, and ancient treasures. They can share what they know.",
        "They're traveling to Otari for the same reason as the party—opportunity, safety, or curiosity about Gauntlight.",
    ]
    return random.choice(connections)

def generate_gm_notes_npc(template):
    """Generate GM notes specifically for NPC encounters"""
    base_notes = []
    
    # Personality and behavior
    base_notes.append(f"Personality: {template.get('personality', 'Friendly and helpful')}")
    base_notes.append(f"Knowledge: {template.get('knowledge', 'Local area and rumors')}")
    
    # NPC-specific behaviors
    npc_behaviors = [
        "Will not fight unless attacked—prefers to flee or negotiate",
        "Genuinely wants to help the party if treated with respect",
        "Has no combat stats—this is a roleplay encounter only",
        "Can become a recurring ally if the party makes a good impression",
        "May offer to travel with the party to Otari for safety",
        "Willing to share information freely if approached diplomatically",
        "Becomes defensive if threatened but will cooperate if intimidated successfully",
        "Appreciates gifts or kind gestures—will remember the party fondly",
    ]
    
    base_notes.extend(random.sample(npc_behaviors, 3))
    
    return base_notes

def generate_gm_notes(template, difficulty):
    """Generate detailed GM notes"""
    base_notes = template.get('tactics', 'Fights to the death')
    
    additional_notes = []
    
    if difficulty in ['DEADLY', 'DIFFICULT']:
        additional_notes.append("This is a serious threat—play it smart and dangerous")
        additional_notes.append("Use terrain and tactics to maximum effect")
        additional_notes.append("Consider foreshadowing this encounter with signs/tracks")
    
    if 'undead' in template.get('lore_keywords', []):
        additional_notes.append("Immune to mental effects, doesn't need to breathe")
        additional_notes.append("Can be turned by clerics of Pharasma or Sarenrae")
        additional_notes.append("Knows information about Gauntlight if questioned with magic")
    
    if 'Cheliax' in template.get('lore_keywords', []):
        additional_notes.append("Speaks Chelish (Common with accent)")
        additional_notes.append("May have military orders or identification papers")
        additional_notes.append("Could be reasoned with if party mentions Thrune or Cheliax")
    
    return [base_notes] + additional_notes

def generate_development(template, difficulty):
    """Generate development/aftermath section"""
    developments = []
    
    if difficulty == 'LORE ONLY':
        developments.append("If party is helpful, NPC remembers them and may offer aid in Otari")
        developments.append("Information gained here can be used for advantage in future encounters")
        developments.append("NPC may appear again as recurring friendly contact")
    else:
        developments.append("Searching the area reveals tracks leading toward Gauntlight")
        developments.append("Locals in Otari will be grateful for news of this threat being eliminated")
        
        if 'undead' in template.get('lore_keywords', []):
            developments.append("Pharasma's priests will pay 10gp for proof of undead destruction")
            developments.append("The creature's remains can be consecrated to prevent reanimation")
        
        if 'bandit' in template.get('lore_keywords', []):
            developments.append("Bandit camp location can be found with DC 18 Survival check")
            developments.append("Captain Longsaddle offers 25gp bounty for bandit leader's capture")
    
    return developments

# Import the massive encounter pools
from encounter_pools import DEADLY_POOL, DIFFICULT_POOL, MODERATE_POOL, EASY_POOL, NPC_POOL

def generate_combat_encounter(roll, difficulty, equipment, inner_sea_lore, players_guide_lore, creature_lore_db):
    """Select random encounter from appropriate pool with EXTENSIVE detail"""
    pool_map = {
        'DEADLY': DEADLY_POOL,
        'DIFFICULT': DIFFICULT_POOL,
        'MODERATE': MODERATE_POOL,
        'EASY': EASY_POOL
    }
    
    encounter_template = random.choice(pool_map[difficulty])
    
    # Generate rewards with halved prices
    level_map = {'DEADLY': 5, 'DIFFICULT': 4, 'MODERATE': 3, 'EASY': 2}
    level = level_map[difficulty]
    
    rewards = []
    num_items = random.randint(2, 5)
    
    for _ in range(num_items):
        item_level = random.randint(max(0, level - 1), min(4, level + 1))
        rarity = 'uncommon' if random.random() < 0.2 else 'common'
        available = get_equipment_by_level(equipment, item_level, rarity)
        
        if available:
            item = random.choice(available)
            price = item['price']
            
            # Halve the price
            if 'gp' in price:
                match = re.search(r'(\d+)', price)
                if match:
                    gp_value = int(match.group(1))
                    halved = max(1, gp_value // 2)
                    new_price = f"{halved} gp" if halved >= 1 else f"{halved * 10} sp"
                else:
                    new_price = price
            elif 'sp' in price:
                match = re.search(r'(\d+)', price)
                if match:
                    sp_value = int(match.group(1))
                    halved = max(1, sp_value // 2)
                    new_price = f"{halved} sp"
                else:
                    new_price = price
            else:
                new_price = price
            
            # Add flavor text
            flavor = random.choice([
                "Worn but serviceable",
                "Bears marks of previous owner",
                "Slightly damaged",
                "Well-maintained",
                "Tarnished but functional"
            ])
            
            rewards.append({
                'name': item['name'],
                'level': item['level'],
                'rarity': item['rarity'],
                'price': new_price,
                'flavor': flavor
            })
    
    coins = random.randint(level * 2, level * 5)
    
    # Get creature-specific lore if available, otherwise use fallback
    creature_name = encounter_template['name']
    creature_lore_text = get_creature_lore_text(creature_name, creature_lore_db)
    
    if creature_lore_text:
        # Use creature lore from PathfinderWiki
        inner_sea_snippet = creature_lore_text
    else:
        # Fallback to generic Inner Sea lore
        inner_sea_snippet = extract_lore_snippet(inner_sea_lore, encounter_template.get('lore_keywords', ['Fogfen']))
    
    otari_connection = get_otari_connection_combat()  # Use combat-specific connection
    gm_notes = generate_gm_notes(encounter_template, difficulty)
    developments = generate_development(encounter_template, difficulty)
    
    return {
        'roll': roll,
        'difficulty': difficulty,
        'template': encounter_template,
        'rewards': rewards,
        'coins': coins,
        'inner_sea_lore': inner_sea_snippet,
        'otari_connection': otari_connection,
        'gm_notes': gm_notes,
        'developments': developments
    }

def generate_lore_encounter(roll, inner_sea_lore, players_guide_lore):
    """Select random NPC encounter from pool with EXTENSIVE detail"""
    npc_template = random.choice(NPC_POOL)
    
    # Generate 5-6 skill interactions with varied DCs
    all_skills = [
        ('Diplomacy', 'Friendly conversation and persuasion'),
        ('Deception', 'Trick or mislead the NPC'),
        ('Intimidation', 'Threaten or coerce information'),
        ('Society', 'Recall relevant cultural knowledge'),
        ('Occultism', 'Recognize magical or esoteric elements'),
        ('Religion', 'Understand religious significance'),
        ('Nature', 'Knowledge of natural world'),
        ('Arcana', 'Identify magical phenomena'),
        ('Medicine', 'Offer healing or medical aid'),
        ('Performance', 'Entertain or impress'),
    ]
    
    selected_skills = random.sample(all_skills, random.randint(5, 6))
    
    interactions = {}
    for skill, description in selected_skills:
        dc = random.randint(13, 22)
        interactions[skill] = {'dc': dc, 'description': description}
    
    # Get lore
    inner_sea_snippet = extract_lore_snippet(inner_sea_lore, npc_template.get('lore_keywords', ['Otari']))
    otari_connection = get_otari_connection_npc()  # Use NPC-specific connection
    gm_notes = generate_gm_notes_npc(npc_template)  # Use NPC-specific GM notes
    developments = generate_development(npc_template, 'LORE ONLY')
    
    # Generate detailed rewards/gifts
    gifts = [
        {"item": "Varisian good luck charm", "effect": "+1 circumstance bonus to next saving throw", "value": "Priceless to owner"},
        {"item": "Detailed map of safe paths", "effect": "Saves 2 hours travel time through Fogfen", "value": "Worth 5gp to right buyer"},
        {"item": "Letter of introduction", "effect": "Grants access to Otari contact (merchant, guard, or priest)", "value": "Invaluable for reputation"},
        {"item": "Minor healing potion", "effect": "Heals 1d8 HP", "value": "3gp"},
        {"item": "Gauntlight information", "effect": "Reveals hidden entrance or safe path", "value": "Could save lives"},
        {"item": "Blessed medallion", "effect": "+1 to next Religion check", "value": "2gp"},
        {"item": "Herbal remedy", "effect": "+2 to next Medicine check", "value": "1gp"},
        {"item": "Ancient coin", "effect": "Collectible, Morlibint will pay 10gp", "value": "10gp to collector"},
    ]
    
    gift = random.choice(gifts)
    
    # Generate detailed knowledge the NPC possesses
    knowledge_details = [
        f"Knows about {random.choice(['recent disappearances', 'bandit activity', 'undead sightings', 'Gauntlight history'])}",
        f"Can provide {random.choice(['safe camping spots', 'water sources', 'shortcuts', 'danger warnings'])}",
        f"Has information about {random.choice(['Otari merchants', 'local politics', 'ancient ruins', 'regional threats'])}",
    ]
    
    return {
        'roll': roll,
        'difficulty': 'LORE ONLY',
        'template': npc_template,
        'interactions': interactions,
        'inner_sea_lore': inner_sea_snippet,
        'otari_connection': otari_connection,
        'gm_notes': gm_notes,
        'developments': developments,
        'gift': gift,
        'knowledge_details': knowledge_details
    }

def write_markdown(encounters, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# 4D20 RANDOM ENCOUNTER TABLE — FOGFEN TO OTARI V2\n\n")
        f.write("**Bell Curve Distribution (4d20 = 4-80)**\n\n")
        f.write("**RANDOMLY GENERATED WITH EXTENSIVE DETAIL** - Each run creates completely new encounters!\n\n")
        f.write("---\n\n")
        
        f.write("## DISTRIBUTION GUIDE\n\n")
        f.write("- **4-9**: DEADLY (Level 5) | **10-19**: DIFFICULT (Level 4) | **20-29**: MODERATE (Level 3)\n")
        f.write("- **30-31**: EASY (Level 2) | **32-52**: LORE ONLY (No Combat) | **53-54**: EASY (Level 2)\n")
        f.write("- **55-64**: MODERATE (Level 3) | **65-74**: DIFFICULT (Level 4) | **75-80**: DEADLY (Level 5)\n\n")
        f.write("---\n\n")
        
        current_diff = None
        for enc in sorted(encounters, key=lambda x: x['roll']):
            if enc['difficulty'] != current_diff:
                current_diff = enc['difficulty']
                f.write(f"\n# {enc['difficulty']} ENCOUNTERS\n\n")
            
            f.write(f"## Roll: {enc['roll']} ({enc['difficulty']})\n\n")
            
            if enc['difficulty'] == 'LORE ONLY':
                t = enc['template']
                f.write(f"### Title: THE {t['name'].upper()}\n\n")
                f.write(f"**Setup:** {t['setup']}\n\n")
                f.write(f"**Read-Aloud:** *\"{t['readaloud']}\"*\n\n")
                f.write(f"**NPC:** {t['name']}\n\n")
                f.write(f"*{t['description']}*\n\n")
                f.write(f"**No combat encounter**\n\n")
                
                f.write(f"#### Lore Connection (Inner Sea Region):\n\n")
                f.write(f"{enc['inner_sea_lore']}\n\n")
                
                f.write(f"#### Otari Connection (Players Guide):\n\n")
                f.write(f"{enc['otari_connection']}\n\n")
                
                f.write(f"#### Interaction Opportunities:\n\n")
                for skill, data in enc['interactions'].items():
                    f.write(f"- **{skill} DC {data['dc']}**: {data['description']}\n")
                
                f.write(f"\n#### GM Notes:\n\n")
                for note in enc['gm_notes']:
                    f.write(f"- {note}\n")
                for detail in enc['knowledge_details']:
                    f.write(f"- {detail}\n")
                
                f.write(f"\n#### Rewards:\n\n")
                f.write(f"**No combat rewards**\n\n")
                f.write(f"**Gift (if treated with respect):**\n")
                f.write(f"- **{enc['gift']['item']}**: {enc['gift']['effect']} (Value: {enc['gift']['value']})\n")
                
                f.write(f"\n#### Development:\n\n")
                for dev in enc['developments']:
                    f.write(f"- {dev}\n")
                
            else:
                t = enc['template']
                f.write(f"### Title: THE {t['name'].upper()}\n\n")
                f.write(f"**Setup:** {t['setup']}\n\n")
                f.write(f"**Read-Aloud:** *\"{t['readaloud']}\"*\n\n")
                
                f.write(f"**Creature:** {t['name']} (Level {enc['difficulty'].split()[0].lower()}, {t.get('description', 'Dangerous foe')})\n\n")
                f.write(f"**Stats:** HP: {t['hp']} | AC: {t['ac']} | Fort: {t['fort']} | Reflex: {t['reflex']} | Will: {t['will']}\n\n")
                
                f.write(f"#### Creature Lore (PathfinderWiki):\n\n")
                f.write(f"{enc['inner_sea_lore']}\n\n")
                
                f.write(f"#### Otari Connection (Players Guide):\n\n")
                f.write(f"{enc['otari_connection']}\n\n")
                
                f.write(f"#### GM Notes:\n\n")
                for note in enc['gm_notes']:
                    f.write(f"- {note}\n")
                
                f.write(f"\n#### Rewards (from equipment.json, prices halved):\n\n")
                for r in enc['rewards']:
                    f.write(f"- **{r['name']}** (Level {r['level']}, {r['rarity']}) - {r['price']} - *{r['flavor']}*\n")
                f.write(f"- **Coins:** {enc['coins']} gp in mixed currency\n")
                
                f.write(f"\n#### Development:\n\n")
                for dev in enc['developments']:
                    f.write(f"- {dev}\n")
            
            f.write("\n---\n\n")

if __name__ == "__main__":
    print("Loading data...")
    equipment = load_json("etc/equipment.json")
    inner_sea_lore = load_lore("etc/inner_sea_region.md")
    players_guide_lore = load_lore("etc/players_guide.md")
    creature_lore_db = load_creature_lore()
    
    print(f"  Equipment: {len(equipment)} items")
    print(f"  Inner Sea Lore: {len(inner_sea_lore)} chars")
    print(f"  Players Guide: {len(players_guide_lore)} chars")
    print(f"  Creature Lore: {len(creature_lore_db)} creatures")
    print(f"  Encounter pools: {len(DEADLY_POOL)} deadly, {len(DIFFICULT_POOL)} difficult,", end=" ")
    print(f"{len(MODERATE_POOL)} moderate, {len(EASY_POOL)} easy, {len(NPC_POOL)} NPCs")
    
    print("\nGenerating encounters with EXTENSIVE detail...")
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
            enc = generate_lore_encounter(roll, inner_sea_lore, players_guide_lore)
        else:
            enc = generate_combat_encounter(roll, diff, equipment, inner_sea_lore, players_guide_lore, creature_lore_db)
        
        encounters.append(enc)
    
    write_markdown(encounters, "gm/4d20_fogfen_otari_encounters_v2.md")
    
    print(f"\n✓ Generated {len(encounters)} DETAILED encounters!")
    print(f"  - {len([e for e in encounters if e['difficulty'] == 'LORE ONLY'])} lore encounters")
    print(f"  - {len([e for e in encounters if e['difficulty'] != 'LORE ONLY'])} combat encounters")
    print("\nOutput: gm/4d20_fogfen_otari_encounters_v2.md")
