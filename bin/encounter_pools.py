"""
MASSIVE pools of encounters - expanded from creatures.json
Thousands of variations ensure every run is unique!
"""
import json

# Load expanded pools from JSON
with open('expanded_pools.json', 'r', encoding='utf-8') as f:
    pools = json.load(f)

DEADLY_POOL = pools['DEADLY_POOL']
DIFFICULT_POOL = pools['DIFFICULT_POOL']
MODERATE_POOL = pools['MODERATE_POOL']
EASY_POOL = pools['EASY_POOL']

# NPC ENCOUNTERS - Preserved from original
NPC_POOL = [
    {
        'name': 'Varisian Fortune Teller',
        'description': 'Elderly woman with colorful scarves, Harrow deck',
        'personality': 'Wise, mysterious, genuinely helpful',
        'knowledge': 'Gauntlight legends, safe paths, Varisian customs, Desna blessings',
        'setup': 'Colorful fabric and incense scent drift through fog.',
        'readaloud': 'A painted wagon sits beside trail. Inside, an elderly Varisian shuffles cards. "The cards told me you would come."',
        'lore_keywords': ['Varisian', 'Desna', 'Cosmic Caravan']
    },
    {
        'name': 'Wandering Priest of Pharasma',
        'description': 'Solemn cleric in gray robes, spiral symbol',
        'personality': 'Serious but compassionate, fights undead',
        'knowledge': 'Undead lore, burial rites, Gauntlight history, Pharasma teachings',
        'setup': 'Figure in gray robes walks slowly, staff tapping.',
        'readaloud': 'A Pharasma priest approaches, spiral gleaming. "The Lady of Graves watches over these cursed paths."',
        'lore_keywords': ['Pharasma', 'death', 'undead']
    },
    {
        'name': 'Retired Pathfinder',
        'description': 'Weathered adventurer with countless scars',
        'personality': 'Friendly, loves sharing tales',
        'knowledge': 'Dungeon survival, monster weaknesses, Otari connections',
        'setup': 'Well-equipped traveler waves from ahead.',
        'readaloud': 'An older human in practical gear greets warmly. "Fellow travelers! Heading to Otari?"',
        'lore_keywords': ['Pathfinder', 'Absalom', 'adventure']
    },
    {
        'name': 'Chelish Deserter',
        'description': 'Haunted soldier in tattered uniform',
        'personality': 'Desperate, afraid, can be helped or hostile',
        'knowledge': 'Gauntlight interior, Chelish military, hidden paths',
        'setup': 'A figure in torn uniform huddles by tree.',
        'readaloud': '"Stay back! I won\'t go back to that lighthouse!"',
        'lore_keywords': ['Cheliax', 'military', 'deserter']
    },
    {
        'name': 'Lumber Worker from Otari',
        'description': 'Burly worker taking break',
        'personality': 'Down-to-earth, gossips freely',
        'knowledge': 'Otari rumors, recent disappearances, local geography',
        'setup': 'Sound of axes, voices ahead.',
        'readaloud': 'Lumber workers share food. "Travelers! Join us?"',
        'lore_keywords': ['Otari', 'lumber', 'worker']
    },
    {
        'name': 'Andoran Merchant',
        'description': 'Well-dressed trader with pack mule',
        'personality': 'Business-minded but fair',
        'knowledge': 'Trade routes, bandit locations, Otari market prices',
        'setup': 'A cart sits tilted, wheel broken.',
        'readaloud': 'A frustrated merchant stands by broken cart. "Can you help?"',
        'lore_keywords': ['Andoran', 'merchant', 'trade']
    },
    {
        'name': 'Hermit Druid',
        'description': 'Wild figure covered in moss',
        'personality': 'Cryptic, speaks in riddles, protects nature',
        'knowledge': 'Fogfen ecology, safe camping, natural hazards',
        'setup': 'A moss-covered figure emerges from reeds.',
        'readaloud': 'The hermit speaks: "The swamp remembers all."',
        'lore_keywords': ['druid', 'nature', 'Gozreh']
    },
    {
        'name': 'Lost Child',
        'description': 'Young girl from Otari, scared',
        'personality': 'Frightened, needs escort home',
        'knowledge': 'Saw "pretty lights" (will-o\'-wisps), parents worried',
        'setup': 'Crying sounds echo through fog.',
        'readaloud': 'A young girl sits sobbing. "I want to go home!"',
        'lore_keywords': ['Otari', 'child', 'rescue']
    },
    {
        'name': 'Cleric of Sarenrae',
        'description': 'Warm priest in golden robes',
        'personality': 'Compassionate, offers healing, fights undead',
        'knowledge': 'Redemption, healing magic, Sarenrae teachings, undead weaknesses',
        'setup': 'Golden light glows through fog.',
        'readaloud': 'A priest in sun-emblazoned robes approaches. "The Dawnflower\'s light reaches even here."',
        'lore_keywords': ['Sarenrae', 'healing', 'redemption']
    },
    {
        'name': 'Taldan Noble',
        'description': 'Haughty aristocrat, lost and afraid',
        'personality': 'Arrogant but desperate, will pay for escort',
        'knowledge': 'Taldan politics, Oppara gossip, will pay 50gp for safe escort',
        'setup': 'Expensive perfume cuts through swamp stench.',
        'readaloud': 'A well-dressed Taldan stumbles through mud. "You there! I require assistance!"',
        'lore_keywords': ['Taldor', 'noble', 'Oppara']
    },
    {
        'name': 'Halfling Trader',
        'description': 'Cheerful merchant with goods',
        'personality': 'Friendly, loves to haggle, shares rumors',
        'knowledge': 'Trade goods, Otari market, recent bandit activity',
        'setup': 'A small figure waves cheerfully.',
        'readaloud': 'A halfling with pack mule grins. "Care to see my wares? Fair prices!"',
        'lore_keywords': ['halfling', 'merchant', 'trade']
    },
    {
        'name': 'Ranger Tracking Bandits',
        'description': 'Grim tracker with bow',
        'personality': 'Focused, professional, hunting criminals',
        'knowledge': 'Bandit locations, tracking, wilderness survival',
        'setup': 'A figure kneels, examining tracks.',
        'readaloud': 'A ranger looks up. "Seen any Chelish deserters? There\'s a bounty."',
        'lore_keywords': ['ranger', 'bounty hunter', 'tracking']
    },
    {
        'name': 'Bard Collecting Stories',
        'description': 'Charismatic performer with lute',
        'personality': 'Entertaining, trades stories for stories',
        'knowledge': 'Local legends, Gauntlight ballads, Otari gossip',
        'setup': 'Music drifts through fog.',
        'readaloud': 'A bard strums a lute. "Travelers! Care to trade tales?"',
        'lore_keywords': ['bard', 'music', 'stories']
    },
    {
        'name': 'Wizard Researching Gauntlight',
        'description': 'Scholarly mage with notebooks',
        'personality': 'Curious, absent-minded, pays for information',
        'knowledge': 'Gauntlight history, Belcorra lore, arcane theory',
        'setup': 'Someone mutters while scribbling notes.',
        'readaloud': 'A wizard looks up from notes. "Fascinating! Have you been inside Gauntlight?"',
        'lore_keywords': ['wizard', 'research', 'Gauntlight']
    },
    {
        'name': 'Escaped Prisoner',
        'description': 'Desperate person in chains',
        'personality': 'Frightened, may be innocent or guilty',
        'knowledge': 'Bandit camp location, prison conditions, plea for help',
        'setup': 'Chains rattle. Someone runs desperately.',
        'readaloud': 'A person in broken chains stumbles forward. "Please, help me!"',
        'lore_keywords': ['prisoner', 'escape', 'bandits']
    },
    {
        'name': 'Gnome Alchemist',
        'description': 'Eccentric gnome with bubbling vials',
        'personality': 'Enthusiastic, slightly mad, loves experiments',
        'knowledge': 'Alchemy, potion recipes, explosive compounds',
        'setup': 'Colorful smoke rises from a small camp.',
        'readaloud': 'A gnome looks up from bubbling vials. "Want to see my latest creation?"',
        'lore_keywords': ['gnome', 'alchemy', 'experiments']
    },
    {
        'name': 'Dwarf Prospector',
        'description': 'Grizzled dwarf with mining tools',
        'personality': 'Gruff but honest, knows the land',
        'knowledge': 'Mineral deposits, underground passages, dwarven lore',
        'setup': 'The sound of a pickaxe echoes.',
        'readaloud': 'A dwarf wipes sweat from his brow. "Looking for gold? I know where to find it."',
        'lore_keywords': ['dwarf', 'mining', 'prospector']
    },
    {
        'name': 'Elven Scout',
        'description': 'Graceful elf with longbow',
        'personality': 'Aloof but helpful, protects the forest',
        'knowledge': 'Forest paths, creature tracking, elven traditions',
        'setup': 'An arrow thuds into a tree near you.',
        'readaloud': 'An elf steps from the trees. "You\'re being followed. I can help."',
        'lore_keywords': ['elf', 'scout', 'forest']
    },
    {
        'name': 'Traveling Monk',
        'description': 'Serene monk in simple robes',
        'personality': 'Peaceful, philosophical, skilled fighter',
        'knowledge': 'Meditation techniques, martial arts, inner peace',
        'setup': 'Someone meditates beside the path.',
        'readaloud': 'A monk opens their eyes. "The path to enlightenment is also the path to Otari."',
        'lore_keywords': ['monk', 'meditation', 'martial arts']
    },
    {
        'name': 'Shoanti Warrior',
        'description': 'Tattooed warrior from the Storval Plateau',
        'personality': 'Proud, honorable, respects strength',
        'knowledge': 'Shoanti customs, tribal lore, survival skills',
        'setup': 'A tall figure with tribal tattoos approaches.',
        'readaloud': 'A Shoanti warrior nods. "You fight well. I respect that."',
        'lore_keywords': ['Shoanti', 'warrior', 'tribal']
    },
    {
        'name': 'Aspis Consortium Agent',
        'description': 'Suspicious merchant in fine clothes',
        'personality': 'Greedy, manipulative, dangerous if crossed',
        'knowledge': 'Black market goods, smuggling routes, Aspis operations',
        'setup': 'A well-dressed figure watches you carefully.',
        'readaloud': 'An Aspis agent smiles coldly. "Perhaps we can do business?"',
        'lore_keywords': ['Aspis', 'merchant', 'conspiracy']
    },
    {
        'name': 'Bellflower Network Operative',
        'description': 'Mysterious figure helping escaped slaves',
        'personality': 'Secretive, compassionate, fights slavery',
        'knowledge': 'Safe houses, escape routes, Chelish politics',
        'setup': 'Someone signals you from the shadows.',
        'readaloud': 'A hooded figure whispers: "Are you fleeing Cheliax? I can help."',
        'lore_keywords': ['Bellflower', 'freedom', 'slavery']
    },
    {
        'name': 'Hellknight Armiger',
        'description': 'Young Hellknight in training',
        'personality': 'Lawful, rigid, seeks order',
        'knowledge': 'Chelish law, Hellknight orders, discipline',
        'setup': 'Armor clanks. A stern figure approaches.',
        'readaloud': 'A Hellknight armiger stops you. "State your business in these lands."',
        'lore_keywords': ['Hellknight', 'law', 'Cheliax']
    },
    {
        'name': 'Qadiran Merchant',
        'description': 'Exotic trader from distant Qadira',
        'personality': 'Charming, worldly, loves to haggle',
        'knowledge': 'Foreign goods, Qadiran culture, trade routes',
        'setup': 'Exotic spices scent the air.',
        'readaloud': 'A Qadiran merchant bows. "Greetings! I have wonders from the east!"',
        'lore_keywords': ['Qadira', 'merchant', 'exotic']
    },
    {
        'name': 'Ulfen Raider',
        'description': 'Massive warrior from the Lands of the Linnorm Kings',
        'personality': 'Boisterous, loves fighting and drinking',
        'knowledge': 'Northern legends, raiding tactics, Ulfen customs',
        'setup': 'A huge figure sings a drinking song.',
        'readaloud': 'An Ulfen warrior grins. "Ho! Care for a drink and a tale?"',
        'lore_keywords': ['Ulfen', 'raider', 'north']
    },
]

print(f"Loaded encounter pools: {len(DEADLY_POOL)} deadly, {len(DIFFICULT_POOL)} difficult, {len(MODERATE_POOL)} moderate, {len(EASY_POOL)} easy, {len(NPC_POOL)} NPCs")
print(f"TOTAL TEMPLATES: {len(DEADLY_POOL) + len(DIFFICULT_POOL) + len(MODERATE_POOL) + len(EASY_POOL) + len(NPC_POOL)}")
