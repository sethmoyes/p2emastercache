#!/usr/bin/env python3
"""
Generate 4d20 Random Encounter Table for Fogfen to Otari
Creates DETAILED encounters with extensive lore, GM notes, and development
Each run = completely different table!
"""
import json
import random
import re
import requests
from bs4 import BeautifulSoup
import time

# Import NPC generator
from generate_npc_lore import generate_npc, generate_npc_encounter_template

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

def save_creature_lore(creature_lore_db):
    """Save creature lore to JSON"""
    with open('etc/creature_lore.json', 'w', encoding='utf-8') as f:
        json.dump(creature_lore_db, f, indent=2, ensure_ascii=False)

def get_creature_lore_text(creature_name, creature_lore_db):
    """Get lore for a specific creature from the database, or scrape if not found"""
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
    
    # If not found, try to scrape from PathfinderWiki
    print(f"  Creature lore not found for '{creature_name}', attempting to scrape...")
    scraped_lore = scrape_pathfinderwiki_lore(creature_name)
    
    if scraped_lore:
        # Cache the scraped lore
        creature_lore_db[creature_name] = scraped_lore
        save_creature_lore(creature_lore_db)
        print(f"  ✓ Scraped and cached lore for '{creature_name}'")
        return scraped_lore['lore']
    
    # If scraping failed, return None to use fallback
    print(f"  X Could not scrape lore for '{creature_name}', using fallback")
    return None

def scrape_pathfinderwiki_lore(creature_name):
    """Scrape creature lore from PathfinderWiki"""
    import requests
    from bs4 import BeautifulSoup
    import urllib.parse
    import time
    
    # Clean the creature name for URL
    clean_name = re.sub(r'\([^)]*\)', '', creature_name)
    clean_name = re.sub(r'Level \d+', '', clean_name)
    clean_name = clean_name.strip()
    clean_name = clean_name.replace("'", "")
    clean_name = clean_name.replace(' ', '_')
    
    url = f"https://pathfinderwiki.com/wiki/{clean_name}"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        content_div = soup.find('div', {'id': 'mw-content-text'})
        if not content_div:
            return None
        
        parser_output = content_div.find('div', {'class': 'mw-parser-output'})
        if not parser_output:
            parser_output = content_div
        
        # Get first few paragraphs
        paragraphs = []
        for element in parser_output.children:
            if element.name == 'p':
                text = element.get_text().strip()
                if text and len(text) > 50 and not text.startswith('This page is a stub'):
                    # Clean up citation markers
                    text = re.sub(r'\[\d+\]', '', text)
                    text = re.sub(r'citation needed', '', text)
                    text = ' '.join(text.split())
                    paragraphs.append(text)
                    if len(paragraphs) >= 3:
                        break
        
        if not paragraphs:
            return None
        
        lore = '\n\n'.join(paragraphs)
        
        # Limit to reasonable length
        if len(lore) > 1000:
            lore = lore[:1000].rsplit('.', 1)[0] + '.'
        
        # Rate limiting
        time.sleep(0.5)
        
        return {
            'source': 'PathfinderWiki',
            'url': url,
            'lore': lore
        }
        
    except Exception as e:
        print(f"    Error scraping: {e}")
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
    
    # Check for specific creature types in keywords
    keyword_str = ' '.join(keywords).lower()
    
    # Undead-specific lore
    if any(k in keyword_str for k in ['undead', 'ghost', 'zombie', 'skeleton', 'wight', 'wraith', 'vampire', 'lich', 'mummy']):
        return "Undead creatures are tragically common in the Inner Sea region, particularly near sites of ancient battles, mass graves, or places touched by necromantic magic. The goddess Urgathoa is patron of undead and disease, while Pharasma opposes all undead as abominations against the natural cycle. Gauntlight itself was built by the necromancer Belcorra Haruvex, whose dark magic still animates the dead centuries after her defeat."
    
    # Fiend-specific lore
    if any(k in keyword_str for k in ['fiend', 'demon', 'devil', 'daemon']):
        return "Fiends—demons, devils, and daemons—are extraplanar beings of pure evil that seek to corrupt, destroy, or enslave mortal souls. In Cheliax, House Thrune openly contracts with devils, binding them to service through infernal pacts. Devils are creatures of law and contracts, while demons embody chaos and destruction."
    
    # Dragon-specific lore
    if any(k in keyword_str for k in ['dragon', 'drake', 'wyrm', 'wyvern']):
        return "Dragons are among the most powerful and intelligent creatures in the Inner Sea region. These ancient beings hoard treasure, command powerful magic, and can live for thousands of years. Some dragons are benevolent protectors, while others are tyrannical destroyers. Even young dragons pose a serious threat to unprepared adventurers."
    
    # Fey-specific lore
    if any(k in keyword_str for k in ['fey', 'sprite', 'pixie', 'gremlin', 'nymph']):
        return "Fey creatures hail from the First World, a realm of primal magic and impossible beauty. These beings are capricious and unpredictable, following their own alien logic. Some fey are helpful to mortals, while others delight in causing mischief or harm. The forests and wild places of Varisia are home to many fey, drawn by the region's ancient magic."
    
    # Aberration lore
    if any(k in keyword_str for k in ['aberration', 'ooze', 'slime']):
        return "Aberrations are creatures that defy natural law—beings from beyond reality, experiments gone wrong, or entities warped by exposure to alien magic. The Darklands beneath Golarion's surface are home to countless such horrors. These creatures often possess alien intelligence and motivations incomprehensible to mortal minds."
    
    # Construct lore
    if any(k in keyword_str for k in ['construct', 'golem', 'animated', 'clockwork']):
        return "Constructs are artificial beings created through magic or advanced engineering. Golems are animated by binding elemental spirits, while clockwork creatures rely on intricate mechanisms. The ancient empire of Thassilon created countless constructs to serve as guardians, and many still function in forgotten ruins throughout Varisia."
    
    # Giant/Humanoid lore
    if any(k in keyword_str for k in ['giant', 'ogre', 'troll', 'cyclops']):
        return "Giants and their kin have inhabited the Inner Sea region since before human civilization. In Varisia, hill giants and marsh giants claim territories in the wilderness, raiding settlements and demanding tribute. These creatures possess a crude intelligence and often serve as muscle for more cunning villains."
    
    # Beast/Animal lore
    if any(k in keyword_str for k in ['beast', 'animal']):
        return "The wilderness of the Inner Sea region teems with dangerous creatures, from dire wolves the size of horses to giant spiders that spin webs between ancient trees. Fogfen, the swampland between Otari and Gauntlight, is particularly notorious for its aggressive wildlife, made more dangerous by the corrupting influence of the lighthouse's dark magic."
    
    # Humanoid lore (goblins, orcs, etc.)
    if any(k in keyword_str for k in ['goblin', 'orc', 'hobgoblin', 'bugbear', 'kobold']):
        return "Goblins, orcs, and their kin plague the roads and forests of the Inner Sea region. While individually weak, they gather in large tribes and can overwhelm unprepared travelers. Their chaotic nature makes them unpredictable—sometimes cowardly, sometimes suicidally brave. Many serve as minions for more powerful villains."
    
    # Plant lore
    if any(k in keyword_str for k in ['plant', 'fungus']):
        return "Animated plants and fungi are common in regions touched by primal magic or necromantic corruption. These creatures range from mindless predators to cunning hunters. The swamps and forests near Gauntlight harbor many such threats, their growth accelerated by the lighthouse's dark energies."
    
    # Elemental lore
    if any(k in keyword_str for k in ['elemental', 'air', 'earth', 'fire', 'water']):
        return "Elementals are beings of pure elemental energy from the Elemental Planes. They can be summoned by spellcasters or appear naturally in areas of strong elemental influence. These creatures embody the raw power of their element—destructive, relentless, and utterly alien to mortal concerns."
    
    # Default fallback - generic but useful
    return f"This creature is one of many dangers that lurk in the wilderness between Otari and Gauntlight. The region's untamed swampland and ancient ruins attract all manner of threats, from natural predators to creatures drawn by the lighthouse's cursed beacon. Travelers who venture into Fogfen must be prepared for the unexpected."

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

def generate_combat_encounter(roll, difficulty, equipment, inner_sea_lore, players_guide_lore, creature_lore_db, encounter_template):
    """Generate combat encounter from pre-selected creature template"""
    
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
            
            # Convert price to string if it's an integer
            if isinstance(price, int):
                # Convert copper to proper denomination
                if price < 10:
                    price = f"{price} cp"
                elif price < 100:
                    price = f"{price} sp"
                else:
                    gp = price / 100
                    if gp == int(gp):
                        price = f"{int(gp)} gp"
                    else:
                        price = f"{gp:.1f} gp"
            
            price = str(price)  # Ensure it's a string
            
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
        # Use keyword-based fallback lore
        inner_sea_snippet = get_fallback_lore(encounter_template.get('lore_keywords', ['creature']))
    
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

def generate_npc_request():
    """Generate a request, ask, or demand that gives players a choice"""
    requests = [
        {
            'situation': 'Broken Wagon',
            'request': 'The NPC\'s wagon wheel is broken and they\'re stranded. They ask for help repairing it or defending them while they work.',
            'choices': [
                'Help repair the wagon (Crafting DC 15, takes 30 minutes)',
                'Stand guard while they repair it themselves (possible random encounter)',
                'Offer to escort them to Otari on foot (slower travel)',
                'Leave them and continue on'
            ]
        },
        {
            'situation': 'Lost Item',
            'request': 'The NPC lost something valuable in the swamp nearby. They offer a reward if the party can retrieve it.',
            'choices': [
                'Search the swamp (Survival DC 17, takes 1 hour, possible danger)',
                'Negotiate for a better reward before helping',
                'Decline and offer directions to Otari instead',
                'Ignore the request and move on'
            ]
        },
        {
            'situation': 'Dangerous Path Ahead',
            'request': 'The NPC warns of danger ahead and asks to travel together for safety. They seem nervous.',
            'choices': [
                'Allow them to join the party temporarily',
                'Investigate what danger they\'re referring to',
                'Offer to scout ahead for them',
                'Decline and part ways'
            ]
        },
        {
            'situation': 'Seeking Information',
            'request': 'The NPC is searching for someone/something and asks if the party has seen it. They seem desperate.',
            'choices': [
                'Share any relevant information freely',
                'Offer to help search (takes time)',
                'Negotiate for payment in exchange for help',
                'Lie or withhold information'
            ]
        },
        {
            'situation': 'Medical Emergency',
            'request': 'The NPC or their companion is injured/sick. They desperately need healing or medicine.',
            'choices': [
                'Provide healing (spell, potion, or Medicine check)',
                'Escort them to Otari for proper treatment',
                'Offer basic first aid and directions',
                'Apologize but continue on your way'
            ]
        },
        {
            'situation': 'Suspicious Activity',
            'request': 'The NPC claims they saw something suspicious nearby and asks the party to investigate with them.',
            'choices': [
                'Investigate together',
                'Investigate alone while they wait',
                'Question them about what they saw (Sense Motive)',
                'Decline and warn them to be careful'
            ]
        },
        {
            'situation': 'Trade Opportunity',
            'request': 'The NPC offers to trade goods or information. They have something the party might want.',
            'choices': [
                'Negotiate a fair trade (Diplomacy)',
                'Try to get a better deal (Deception or Intimidation)',
                'Accept their initial offer',
                'Decline the trade'
            ]
        },
        {
            'situation': 'Fleeing Danger',
            'request': 'The NPC is running from something and begs for help or a place to hide.',
            'choices': [
                'Help them hide and face whatever is chasing them',
                'Question them about what they\'re running from',
                'Offer to mediate/negotiate with their pursuers',
                'Step aside and let them pass'
            ]
        },
        {
            'situation': 'Moral Dilemma',
            'request': 'The NPC confesses to a crime or wrongdoing and asks for the party\'s help or forgiveness.',
            'choices': [
                'Help them make amends',
                'Turn them in to authorities in Otari',
                'Offer advice but remain neutral',
                'Judge them harshly and refuse to help'
            ]
        },
        {
            'situation': 'Delivery Request',
            'request': 'The NPC asks the party to deliver a message or package to someone in Otari. They offer payment.',
            'choices': [
                'Accept the delivery job',
                'Inspect the package first (Perception)',
                'Negotiate for higher payment',
                'Decline the request'
            ]
        },
        {
            'situation': 'Shelter Request',
            'request': 'Night is falling and the NPC asks to share the party\'s camp for safety. They offer to contribute supplies.',
            'choices': [
                'Welcome them to camp',
                'Allow them but keep watch (Perception)',
                'Decline but point them to a safe spot nearby',
                'Refuse and send them away'
            ]
        },
        {
            'situation': 'Warning',
            'request': 'The NPC urgently warns the party about danger ahead and insists they turn back or take another route.',
            'choices': [
                'Heed the warning and change course',
                'Question them about the danger (Diplomacy or Intimidation)',
                'Thank them but continue on the current path',
                'Ignore the warning entirely'
            ]
        },
    ]
    
    return random.choice(requests)

def generate_lore_encounter(roll, inner_sea_lore, players_guide_lore, npc_template):
    """Generate lore encounter from pre-selected NPC template"""
    
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
    
    # Generate NPC request/situation
    npc_request = generate_npc_request()
    
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
        'npc_request': npc_request,
        'otari_connection': otari_connection,
        'gm_notes': gm_notes,
        'developments': developments,
        'gift': gift,
        'knowledge_details': knowledge_details
    }

def write_markdown(encounters, output_file, player_level, deadly_level, difficult_level, moderate_level, easy_level):
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# 4D20 RANDOM ENCOUNTER TABLE — FOGFEN TO OTARI V2\n\n")
        f.write("**Bell Curve Distribution (4d20 = 4-80)**\n\n")
        f.write("**RANDOMLY GENERATED WITH EXTENSIVE DETAIL** - Each run creates completely new encounters!\n\n")
        f.write(f"**Player Level: {player_level}**\n\n")
        f.write("---\n\n")
        
        f.write("## DISTRIBUTION GUIDE\n\n")
        f.write(f"- **4-9**: DEADLY (Level {deadly_level}) | **10-19**: DIFFICULT (Level {difficult_level}) | **20-29**: MODERATE (Level {moderate_level})\n")
        f.write(f"- **30-31**: EASY (Level {easy_level}) | **32-52**: LORE ONLY (No Combat) | **53-54**: EASY (Level {easy_level})\n")
        f.write(f"- **55-64**: MODERATE (Level {moderate_level}) | **65-74**: DIFFICULT (Level {difficult_level}) | **75-80**: DEADLY (Level {deadly_level})\n\n")
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
                
                # Write the NPC request/situation
                req = enc['npc_request']
                f.write(f"#### The Situation: {req['situation']}\n\n")
                f.write(f"{req['request']}\n\n")
                f.write(f"**Player Choices:**\n")
                for choice in req['choices']:
                    f.write(f"- {choice}\n")
                f.write(f"\n")
                
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
    import sys
    
    # Parse command line arguments
    player_level = 4  # Default level
    if len(sys.argv) > 1:
        for i, arg in enumerate(sys.argv[1:]):
            if arg == '--level' and i + 1 < len(sys.argv) - 1:
                try:
                    player_level = int(sys.argv[i + 2])
                except ValueError:
                    print(f"Invalid level: {sys.argv[i + 2]}, using default level 4")
    
    # Calculate level ranges based on player level
    deadly_level = player_level + 2      # Max difficulty: player level + 2
    difficult_level = player_level + 1   # Hard: player level + 1
    moderate_level = player_level        # Moderate: player level
    easy_level = max(1, player_level // 2)  # Easy: half player level (min 1)
    max_item_level = player_level + 2    # Items: max player level + 2
    
    print(f"Generating encounters for player level {player_level}")
    print(f"  Deadly encounters: Level {deadly_level}")
    print(f"  Difficult encounters: Level {difficult_level}")
    print(f"  Moderate encounters: Level {moderate_level}")
    print(f"  Easy encounters: Level {easy_level}")
    print(f"  Max item level: {max_item_level}")
    print()
    
    print("Loading data...")
    equipment = load_json("etc/equipment.json")
    
    # Filter equipment by max level
    equipment = [e for e in equipment if e['level'] <= max_item_level]
    
    inner_sea_lore = load_lore("etc/inner_sea_region.md")
    players_guide_lore = load_lore("etc/players_guide.md")
    creature_lore_db = load_creature_lore()
    
    # Filter encounter pools by level
    DEADLY_POOL_FILTERED = [c for c in DEADLY_POOL if c.get('level', 99) <= deadly_level]
    DIFFICULT_POOL_FILTERED = [c for c in DIFFICULT_POOL if c.get('level', 99) <= difficult_level]
    MODERATE_POOL_FILTERED = [c for c in MODERATE_POOL if c.get('level', 99) <= moderate_level]
    EASY_POOL_FILTERED = [c for c in EASY_POOL if c.get('level', 99) <= easy_level]
    
    print(f"  Equipment: {len(equipment)} items (level {max_item_level} or below)")
    print(f"  Inner Sea Lore: {len(inner_sea_lore)} chars")
    print(f"  Players Guide: {len(players_guide_lore)} chars")
    print(f"  Creature Lore: {len(creature_lore_db)} creatures")
    print(f"  Encounter pools: {len(DEADLY_POOL_FILTERED)} deadly, {len(DIFFICULT_POOL_FILTERED)} difficult,", end=" ")
    print(f"{len(MODERATE_POOL_FILTERED)} moderate, {len(EASY_POOL_FILTERED)} easy")
    
    print("\nGenerating encounters with EXTENSIVE detail...")
    encounters = []
    
    # Generate unique NPCs dynamically for lore encounters
    lore_count = sum(1 for roll in range(4, 81) if 32 <= roll <= 52)
    print(f"  Generating {lore_count} unique NPCs for lore encounters...")
    selected_npcs = []
    for i in range(lore_count):
        npc = generate_npc()
        npc_template = generate_npc_encounter_template(npc)
        selected_npcs.append(npc_template)
    print(f"  ✓ Generated {len(selected_npcs)} NPCs")
    npc_index = 0
    
    # Pre-select unique creatures for combat encounters to avoid duplicates
    combat_by_difficulty = {}
    for diff in ['DEADLY', 'DIFFICULT', 'MODERATE', 'EASY']:
        count = sum(1 for roll in range(4, 81) if (
            (diff == 'DEADLY' and (roll <= 9 or roll >= 75)) or
            (diff == 'DIFFICULT' and (roll <= 19 or roll >= 65) and not (roll <= 9 or roll >= 75)) or
            (diff == 'MODERATE' and (roll <= 29 or roll >= 55) and not (roll <= 19 or roll >= 65)) or
            (diff == 'EASY' and ((roll <= 31 or roll >= 53) and not (roll <= 29 or roll >= 55) and not (32 <= roll <= 52)))
        ))
        pool_map = {
            'DEADLY': DEADLY_POOL_FILTERED, 
            'DIFFICULT': DIFFICULT_POOL_FILTERED, 
            'MODERATE': MODERATE_POOL_FILTERED, 
            'EASY': EASY_POOL_FILTERED
        }
        pool = pool_map[diff]
        if count > len(pool):
            print(f"WARNING: Need {count} {diff} encounters but only have {len(pool)} in pool!")
            combat_by_difficulty[diff] = random.choices(pool, k=count)
        else:
            combat_by_difficulty[diff] = random.sample(pool, count)
    
    combat_indices = {diff: 0 for diff in ['DEADLY', 'DIFFICULT', 'MODERATE', 'EASY']}
    
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
            enc = generate_lore_encounter(roll, inner_sea_lore, players_guide_lore, selected_npcs[npc_index])
            npc_index += 1
        else:
            creature_template = combat_by_difficulty[diff][combat_indices[diff]]
            combat_indices[diff] += 1
            enc = generate_combat_encounter(roll, diff, equipment, inner_sea_lore, players_guide_lore, creature_lore_db, creature_template)
        
        encounters.append(enc)
    
    write_markdown(encounters, "gm/4d20_fogfen_otari_encounters_v2.md", player_level, deadly_level, difficult_level, moderate_level, easy_level)
    
    print(f"\n✓ Generated {len(encounters)} DETAILED encounters!")
    print(f"  - {len([e for e in encounters if e['difficulty'] == 'LORE ONLY'])} lore encounters")
    print(f"  - {len([e for e in encounters if e['difficulty'] != 'LORE ONLY'])} combat encounters")
    print("\nOutput: gm/4d20_fogfen_otari_encounters_v2.md")
