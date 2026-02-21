#!/usr/bin/env python3
"""
Dungeon Turn Encounter Generator V2 - The Fun Version!

Creates tension, rewards creativity, and makes the dungeon feel ALIVE.
50/50 combat vs non-combat split with meaningful choices.

New probability distribution:
- 5-25: OPPORTUNITIES (reward creativity)
- 26-45: COMPLICATIONS (force skill use)
- 46-65: DILEMMAS (meaningful choices)
- 66-85: ACTIVE THREATS (immediate danger)
- 86-100: COMBAT (actual fights)
"""

import random
import sys
import json
import re
import os

# Add parent directory (bin) to path for event_loader import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from event_loader import load_events_from_json, ValidationError

def load_json(filename):
    """Load JSON file"""
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_markdown(filename):
    """Load markdown file"""
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read()

def parse_gauntlight_levels(content):
    """Parse gauntlight_keep_levels.md to extract floor information"""
    levels = {}
    
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
        
        # Extract threats
        threats = []
        threats_section = re.search(r'\*\*Threats:\*\* (.+)', level_content)
        if threats_section:
            threats = [t.strip() for t in threats_section.group(1).split(',')]
        
        levels[level_num] = {
            'name': level_name,
            'theme': theme,
            'threats': threats,
            'content': level_content
        }
    
    return levels

def get_category_from_sum(total, is_extreme=False):
    """
    Determine event category based on 5d20 sum.
    
    New distribution with "no event" mechanic:
    - Extreme rolls (5-15, 90-100): Always COMBAT
    - Non-extreme rolls: 50% chance of NO EVENT
    - 5-44: COMBAT/ACTIVE_THREAT (danger)
    - 45-62: OPPORTUNITIES/COMPLICATIONS/DILEMMAS (middle range)
    - 63-100: ACTIVE_THREAT/COMBAT (danger)
    """
    # Extreme rolls always generate combat
    if is_extreme:
        return "COMBAT"
    
    # Non-extreme rolls: 50% chance of no event
    if random.random() < 0.5:
        return "NO_EVENT"
    
    # Distribute remaining events
    if total <= 44:
        # Low rolls: danger (combat or active threats)
        return random.choice(["COMBAT", "ACTIVE_THREAT"])
    elif total <= 62:
        # Middle rolls: non-combat encounters
        return random.choice(["OPPORTUNITY", "COMPLICATION", "DILEMMA"])
    else:
        # High rolls: danger (active threats or combat)
        return random.choice(["ACTIVE_THREAT", "COMBAT"])


def get_party_member_spotlight():
    """Rotate through party members to spotlight"""
    return random.choice([
        {"class": "Cleric", "skills": ["Religion", "Medicine", "Diplomacy"]},
        {"class": "Wizard", "skills": ["Arcana", "Recall Knowledge", "Society"]},
        {"class": "Rogue", "skills": ["Thievery", "Stealth", "Acrobatics", "Deception"]},
        {"class": "Swashbuckler", "skills": ["Acrobatics", "Deception", "Performance", "Intimidation"]},
        {"class": "Monk", "skills": ["Athletics", "Acrobatics", "Perception"]}
    ])

def get_creatures_for_floor(creatures, floor_num, party_level):
    """Get appropriate creatures for this floor (2 levels below party)"""
    target_level = max(1, party_level - 2)
    
    # Filter creatures by level
    appropriate = [c for c in creatures if c['level'] == target_level]
    
    return appropriate if appropriate else creatures

# Load events from JSON file
# Use relative path from script location to work in containers
SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EVENTS_FILE = os.path.join(SCRIPT_DIR, 'etc', 'dungeon_turn_events.json')

try:
    LOADED_EVENTS = load_events_from_json(EVENTS_FILE)
    OPPORTUNITY_TEMPLATES = LOADED_EVENTS['OPPORTUNITY']
    COMPLICATION_TEMPLATES = LOADED_EVENTS['COMPLICATION']
    DILEMMA_TEMPLATES = LOADED_EVENTS['DILEMMA']
    ACTIVE_THREAT_TEMPLATES = LOADED_EVENTS['ACTIVE_THREAT']
except FileNotFoundError:
    print(f"ERROR: Event file not found: {EVENTS_FILE}")
    print("Please ensure dungeon_turn_events.json exists in etc/ directory")
    sys.exit(1)
except json.JSONDecodeError as e:
    print(f"ERROR: Invalid JSON in {EVENTS_FILE}: {e}")
    sys.exit(1)
except ValidationError as e:
    print(f"ERROR: Invalid event structure: {e}")
    sys.exit(1)

# OPPORTUNITY EVENT TEMPLATES (5-25)
# Loaded from JSON file at module initialization

# COMPLICATION EVENT TEMPLATES (26-45)
# Loaded from JSON file at module initialization

# DILEMMA EVENT TEMPLATES (46-65)
# Loaded from JSON file at module initialization

# ACTIVE THREAT EVENT TEMPLATES (66-85)
# Loaded from JSON file at module initialization

# COMBAT ENCOUNTER TEMPLATES (86-100)
# These will be generated dynamically based on floor and creatures
COMBAT_ECOLOGY_TYPES = [
    "feeding",      # Monsters eating, distracted
    "fighting",     # Two groups fighting each other
    "sleeping",     # Resting, can be avoided or ambushed
    "patrolling",   # Moving through area
    "working",      # Performing tasks
    "guarding",     # Stationed at post
    "hunting",      # Tracking prey
    "scavenging",   # Picking over remains
    "ritual",       # Performing ceremony
    "arguing"       # Internal conflict
]


def generate_opportunity_event(floor_num, floor_data, party_level, context=None):
    """Generate an OPPORTUNITY event (5-25)"""
    from event_context import EventContext
    from template_selector import select_template
    from context_description import apply_all_context
    
    if context is None:
        context = EventContext()
    
    # Select template based on context AND floor
    template = select_template(OPPORTUNITY_TEMPLATES, context, floor=floor_num)
    
    # Customize for floor
    event = template.copy()
    event['floor'] = floor_num
    event['floor_name'] = floor_data['name']
    
    # Apply context-aware modifications
    event = apply_all_context(event, context)
    
    # Add floor-specific flavor
    if floor_num == 1:
        event['flavor'] = "Mitflit trinkets scattered nearby suggest they pass through here often."
    elif floor_num == 2:
        event['flavor'] = "The musty smell of morlock occupation is strong here."
    elif floor_num == 3:
        event['flavor'] = "Dusty books and the smell of old parchment fill the air."
    elif floor_num == 4:
        event['flavor'] = "This area feels personal, intimate - Belcorra's private space."
    elif floor_num == 5:
        event['flavor'] = "Blood-soaked sand and the echo of past battles."
    elif floor_num == 6:
        event['flavor'] = "The clinical smell of alchemical preservatives mixed with rot."
    elif floor_num == 7:
        event['flavor'] = "Oppressive heat and the smell of brimstone."
    elif floor_num == 8:
        event['flavor'] = "Damp fungal smell and bioluminescent glow."
    elif floor_num == 9:
        event['flavor'] = "Wild Darklands cavern, untamed and dangerous."
    elif floor_num == 10:
        event['flavor'] = "Reality feels thin here. Ancient and alien."
    
    return event

def generate_complication_event(floor_num, floor_data, party_level, context=None):
    """Generate a COMPLICATION event (26-45)"""
    from event_context import EventContext
    from template_selector import select_template
    from context_description import apply_all_context
    
    if context is None:
        context = EventContext()
    
    # Select template based on context AND floor
    template = select_template(COMPLICATION_TEMPLATES, context, floor=floor_num)
    
    event = template.copy()
    event['floor'] = floor_num
    event['floor_name'] = floor_data['name']
    
    # Apply context-aware modifications
    event = apply_all_context(event, context)
    
    # Add floor-specific complications
    if floor_num == 1:
        event['flavor'] = "Mitflit graffiti covers the walls - crude drawings of their 'Sky King'."
    elif floor_num == 2:
        event['flavor'] = "Morlock claw marks score the surfaces."
    elif floor_num == 3:
        event['flavor'] = "Ghoulish scribes have been through here - books disturbed."
    elif floor_num == 4:
        event['flavor'] = "Volluk's influence is evident - leech trails on the floor."
    elif floor_num == 5:
        event['flavor'] = "Arena sand has drifted into this area."
    elif floor_num == 6:
        event['flavor'] = "Seugathi slime trails glisten on the walls."
    elif floor_num == 7:
        event['flavor'] = "Infernal runes glow faintly in the darkness."
    elif floor_num == 8:
        event['flavor'] = "Bog mummy moans echo distantly."
    elif floor_num == 9:
        event['flavor'] = "Multiple faction territories overlap here - dangerous."
    elif floor_num == 10:
        event['flavor'] = "Nhimbaloth's presence is palpable."
    
    return event

def generate_dilemma_event(floor_num, floor_data, party_level, context=None):
    """Generate a DILEMMA event (46-65)"""
    from event_context import EventContext
    from template_selector import select_template
    from context_description import apply_all_context
    
    if context is None:
        context = EventContext()
    
    # Select template based on context AND floor
    template = select_template(DILEMMA_TEMPLATES, context, floor=floor_num)
    
    event = template.copy()
    event['floor'] = floor_num
    event['floor_name'] = floor_data['name']
    
    # Apply context-aware modifications
    event = apply_all_context(event, context)
    
    # Add floor-specific context
    if floor_num <= 3:
        event['context'] = "You're still in the upper levels. Escape is possible if things go wrong."
    elif floor_num <= 6:
        event['context'] = "You're deep enough that retreat is costly. Choose wisely."
    else:
        event['context'] = "You're in the deep dungeon. Every choice matters. No easy escape."
    
    return event


def generate_active_threat_event(floor_num, floor_data, party_level, context=None):
    """Generate an ACTIVE THREAT event (66-85)"""
    from event_context import EventContext
    from template_selector import select_template
    from context_description import apply_all_context
    
    if context is None:
        context = EventContext()
    
    # Select template based on context AND floor
    template = select_template(ACTIVE_THREAT_TEMPLATES, context, floor=floor_num)
    
    event = template.copy()
    event['floor'] = floor_num
    event['floor_name'] = floor_data['name']
    
    # Apply context-aware modifications
    event = apply_all_context(event, context)
    
    # Add urgency
    event['urgency'] = "IMMEDIATE ACTION REQUIRED! No time to discuss!"
    
    return event

def generate_extreme_combat_event(floor_num, floor_data, party_level, creatures, dice_sum):
    """
    Generate an EXTREME combat encounter for extreme rolls (5-15, 90-100).
    These encounters use creatures at dungeon floor level, making them very dangerous.
    """
    # Extreme encounters always use floor level
    target_level = floor_num
    difficulty = "EXTREME (Floor Level)"
    difficulty_note = f"💀 EXTREME ROLL ({dice_sum})! Creatures at floor level {floor_num}!"
    
    # Get creatures at floor level
    level_creatures = [c for c in creatures if c['level'] == target_level]
    
    # Filter for valid creatures
    def is_valid_creature(creature):
        name = creature.get('name', '')
        rarity = creature.get('rarity', 'common').lower()
        
        if rarity not in ['common', 'uncommon']:
            return False
        if len(name) < 3:
            return False
        if 'Pathfinder #' in name or ' pg. ' in name or 'Monster Core' in name or 'Bestiary' in name:
            return False
        if ',' in name:
            return False
        return True
    
    level_creatures = [c for c in level_creatures if is_valid_creature(c)]
    
    if not level_creatures:
        # Fallback if no creatures at floor level
        level_creatures = [c for c in creatures if c['level'] == max(1, party_level)]
    
    # Select creatures
    num_creatures = random.choice([1, 2, 2, 3])  # Weighted toward 2
    selected_creatures = random.sample(level_creatures, min(num_creatures, len(level_creatures)))
    
    creature_names = [c['name'] for c in selected_creatures]
    
    # Generate ecology based on floor
    floor_name = floor_data.get('name', f'Floor {floor_num}')
    floor_theme = floor_data.get('theme', 'Unknown')
    
    ecology_options = [
        f"These creatures are native to {floor_name}. They know the terrain and use it to their advantage.",
        f"Drawn by the {floor_theme.lower()}, these creatures are at home in this environment.",
        f"These are the dominant predators of {floor_name}, perfectly adapted to this floor.",
        f"Ancient guardians of {floor_name}, these creatures have claimed this territory."
    ]
    
    tactical_options = [
        "Use terrain to your advantage - look for chokepoints or cover",
        "Consider retreating to a more favorable position",
        "Focus fire on one enemy at a time to reduce their action economy",
        "Use buffs and debuffs - every bonus counts in a deadly fight",
        "Coordinate attacks for flanking bonuses"
    ]
    
    return {
        'title': f"EXTREME ENCOUNTER: {', '.join(creature_names)}",
        'description': f"An extremely dangerous encounter! {num_creatures} powerful creature(s) at floor level {floor_num}.",
        'difficulty': difficulty,
        'difficulty_note': difficulty_note,
        'ecology': random.choice(ecology_options),
        'creatures': creature_names,
        'num_creatures': num_creatures,
        'creature_level': target_level,
        'tactical_option': random.choice(tactical_options),
        'avoidable': False,  # Extreme encounters are not avoidable
        'surprise_available': dice_sum <= 15,  # Low extreme rolls can surprise
        'gm_notes': f"EXTREME encounter at floor level. This is a deadly fight. Consider allowing creative solutions or retreat options.",
        'dice_sum': dice_sum,
        'floor': floor_num
    }

def generate_combat_event(floor_num, floor_data, party_level, creatures, dice_sum=86):
    """Generate a COMBAT encounter (86-100) with dungeon ecology
    
    Dice sum ranges:
    - 86-94: Standard combat (2 levels below party) - "Low threat"
    - 95-99: Dangerous combat (at party level) - "Moderate threat"  
    - 100: EXTREME combat (at floor level) - "DEADLY threat"
    """
    
    # Determine target level and difficulty based on dice sum
    if dice_sum == 100:
        # EXTREME: Creatures at floor level (deadly)
        target_level = floor_num
        difficulty = "DEADLY (Floor Level)"
        difficulty_note = "⚠️ EXTREME ENCOUNTER - Creatures at floor level!"
    elif dice_sum >= 95:
        # High roll: Creatures at party level (moderate)
        target_level = party_level
        difficulty = "Moderate (Party Level)"
        difficulty_note = "Dangerous encounter - creatures at your level"
    else:
        # Normal combat: 2 levels below party (low)
        target_level = max(1, party_level - 2)
        difficulty = "Low (2 levels below party)"
        difficulty_note = "Standard encounter"
    
    # Define floor-appropriate creature traits/types based on gauntlight_keep_levels.md
    floor_traits = {
        1: {
            'keywords': ['mitflit', 'gremlin', 'undead', 'skeleton', 'zombie', 'shambling'],
            'description': 'Mitflits and basic undead from Belcorra\'s forces'
        },
        2: {
            'keywords': ['morlock', 'humanoid', 'undead', 'degenerate', 'servant'],
            'description': 'Morlocks worshipping the Ghost Queen and undead servants'
        },
        3: {
            'keywords': ['ghoul', 'undead', 'librarian', 'scribe', 'devil', 'zebub', 'imp'],
            'description': 'Ghoul librarians (Cult of the Canker) and minor devils'
        },
        4: {
            'keywords': ['drow', 'elf', 'undead', 'velstrac', 'worm', 'leech', 'werewolf'],
            'description': 'Drow, velstracs, and Belcorra\'s personal servants'
        },
        5: {
            'keywords': ['beast', 'animal', 'lizard', 'grothlut', 'fleshwarp', 'devil'],
            'description': 'Arena beasts and failed fleshwarp experiments'
        },
        6: {
            'keywords': ['seugathi', 'aberration', 'fleshwarp', 'drider', 'ooze', 'grothlut'],
            'description': 'Seugathi fleshwarpers and their experiments'
        },
        7: {
            'keywords': ['devil', 'fiend', 'imp', 'erinyes', 'contract', 'infernal', 'denizen', 'leng'],
            'description': 'Devils and infernal creatures in the prison'
        },
        8: {
            'keywords': ['mummy', 'bog', 'undead', 'bodak', 'gnome', 'svirfneblin', 'gug', 'caligni'],
            'description': 'Bog mummies (Children of Belcorra) and Darklands creatures'
        },
        9: {
            'keywords': ['drow', 'elf', 'urdefhan', 'caligni', 'darklands', 'duergar', 'xulgath', 'ratfolk', 'spider'],
            'description': 'Darklands factions: drow, urdefhan, and caligni'
        },
        10: {
            'keywords': ['undead', 'ghost', 'serpentfolk', 'aberration', 'void', 'empty', 'nhimbaloth'],
            'description': 'Ancient serpentfolk temple and Nhimbaloth\'s servants'
        }
    }
    
    # Get creatures at target level
    level_creatures = [c for c in creatures if c['level'] == target_level]
    
    # Filter out creatures with bad names (book references, trait lists, etc.)
    def is_valid_creature(creature):
        name = creature.get('name', '')
        rarity = creature.get('rarity', 'common').lower()
        
        # Only allow common or uncommon creatures
        if rarity not in ['common', 'uncommon']:
            return False
        
        # Skip if name is too short
        if len(name) < 3:
            return False
        # Skip book references
        if 'Pathfinder #' in name or ' pg. ' in name or 'Monster Core' in name or 'Bestiary' in name:
            return False
        # Skip if name contains ANY commas (trait lists)
        if ',' in name:
            return False
        # Skip generic single-word names
        generic_names = ['Undead', 'Demon', 'Devil', 'Dragon', 'Elemental', 'Beast', 'Aberration', 
                        'Fiend', 'Construct', 'Ooze', 'Plant', 'Fungus', 'Humanoid', 'Animal']
        if name in generic_names:
            return False
        return True
    
    level_creatures = [c for c in level_creatures if is_valid_creature(c)]
    
    # Prioritize manually enhanced creatures (they have full stats)
    enhanced_creatures = [c for c in level_creatures if c.get('attacks') and len(c.get('attacks', [])) > 0]
    if enhanced_creatures:
        # Use enhanced creatures preferentially
        level_creatures = enhanced_creatures
    
    # Filter by floor-appropriate traits
    floor_data = floor_traits.get(floor_num, {})
    floor_keywords = floor_data.get('keywords', [])
    if floor_keywords and level_creatures:
        # Check if creature name or traits match floor keywords
        filtered = []
        for c in level_creatures:
            name_lower = c['name'].lower()
            traits_lower = ' '.join(c.get('traits', [])).lower()
            creature_type_lower = c.get('creature_type', '').lower()
            combined = name_lower + ' ' + traits_lower + ' ' + creature_type_lower
            
            # Check if any floor keyword appears in creature
            if any(keyword in combined for keyword in floor_keywords):
                filtered.append(c)
        
        # Use filtered list if we found matches, otherwise use all at level
        if filtered:
            floor_creatures = filtered
        else:
            floor_creatures = level_creatures
    else:
        floor_creatures = level_creatures
    
    # Fallback if no creatures at exact level
    if not floor_creatures:
        # Try within 1 level
        floor_creatures = [c for c in creatures if abs(c['level'] - target_level) <= 1]
        floor_creatures = [c for c in floor_creatures if is_valid_creature(c)]
        
        # Apply floor trait filtering again
        if floor_keywords and floor_creatures:
            filtered = []
            for c in floor_creatures:
                name_lower = c['name'].lower()
                traits_lower = ' '.join(c.get('traits', [])).lower()
                combined = name_lower + ' ' + traits_lower
                if any(keyword in combined for keyword in floor_keywords):
                    filtered.append(c)
            if filtered:
                floor_creatures = filtered
    
    if not floor_creatures:
        # Last resort: any creatures up to target level
        floor_creatures = [c for c in creatures if c['level'] <= target_level and c['level'] > 0]
        floor_creatures = [c for c in floor_creatures if is_valid_creature(c)]
    
    # For extreme encounters, prefer higher level creatures
    if dice_sum >= 95 and floor_creatures:
        # Sort by level descending and take top half
        floor_creatures.sort(key=lambda x: x['level'], reverse=True)
        cutoff = max(1, len(floor_creatures) // 2)
        floor_creatures = floor_creatures[:cutoff]
    
    # Select ecology type
    ecology_type = random.choice(COMBAT_ECOLOGY_TYPES)
    
    # Select 1-3 creatures of the SAME type
    num_creatures = random.randint(1, 3)
    # Pick one creature type and use it multiple times
    selected_creature = random.choice(floor_creatures)
    selected_creatures = [selected_creature]  # Only one type for consistency
    
    # Build encounter based on ecology
    if ecology_type == "feeding":
        event = {
            "title": f"{selected_creatures[0]['name']} Feeding",
            "description": f"You come upon {num_creatures} {selected_creatures[0]['name']}(s) feasting on a fresh corpse. They're completely focused on their meal.",
            "ecology": "The creatures are distracted by food. Blood and gore everywhere.",
            "tactical_option": "DC 15 Stealth to sneak past OR surprise round if you attack",
            "avoidable": True,
            "surprise_available": True
        }
    
    elif ecology_type == "fighting":
        creature_a = selected_creatures[0]
        creature_b = selected_creatures[1] if len(selected_creatures) > 1 else random.choice(floor_creatures)
        event = {
            "title": f"Territorial Dispute",
            "description": f"Two groups are fighting: {creature_a['name']} vs {creature_b['name']}. They're so focused on each other they haven't noticed you.",
            "ecology": "Monsters fighting each other over territory or resources.",
            "tactical_option": "Wait for them to weaken each other, join one side, or sneak past (DC 16 Stealth)",
            "avoidable": True,
            "surprise_available": True
        }
    
    elif ecology_type == "sleeping":
        event = {
            "title": f"Sleeping {selected_creatures[0]['name']}",
            "description": f"{num_creatures} {selected_creatures[0]['name']}(s) are sleeping in a pile. They're exhausted from a recent patrol.",
            "ecology": "Creatures need rest too. They're vulnerable but will wake if you're loud.",
            "tactical_option": "DC 17 Stealth to sneak past OR automatic surprise round if you attack",
            "avoidable": True,
            "surprise_available": True
        }

    
    elif ecology_type == "patrolling":
        event = {
            "title": f"{selected_creatures[0]['name']} Patrol",
            "description": f"A patrol of {num_creatures} {selected_creatures[0]['name']}(s) is making rounds. They're alert and armed.",
            "ecology": "Regular patrol route. They'll return this way in 1 hour.",
            "tactical_option": "DC 18 Stealth to hide OR prepare ambush for surprise round",
            "avoidable": True,
            "surprise_available": True
        }
    
    elif ecology_type == "working":
        event = {
            "title": f"{selected_creatures[0]['name']} Working",
            "description": f"{num_creatures} {selected_creatures[0]['name']}(s) are hauling supplies, repairing walls, or performing maintenance. They're distracted by their task.",
            "ecology": "Monsters have jobs and responsibilities. Not just waiting to fight.",
            "tactical_option": "DC 16 Stealth to sneak past OR surprise round if you attack",
            "avoidable": True,
            "surprise_available": True
        }
    
    elif ecology_type == "guarding":
        event = {
            "title": f"{selected_creatures[0]['name']} Guard Post",
            "description": f"{num_creatures} {selected_creatures[0]['name']}(s) are stationed at a guard post. They're bored but watchful.",
            "ecology": "Stationed guards. Can be distracted or negotiated with.",
            "tactical_option": "DC 19 Stealth to sneak past OR DC 18 Deception to distract them",
            "avoidable": True,
            "surprise_available": False
        }
    
    elif ecology_type == "hunting":
        event = {
            "title": f"{selected_creatures[0]['name']} Hunting Party",
            "description": f"{num_creatures} {selected_creatures[0]['name']}(s) are tracking prey. They're focused on the trail ahead.",
            "ecology": "Hunting other creatures (or maybe hunting YOU if you've been loud).",
            "tactical_option": "DC 17 Stealth to avoid OR follow them to their prey",
            "avoidable": True,
            "surprise_available": True
        }
    
    elif ecology_type == "scavenging":
        event = {
            "title": f"{selected_creatures[0]['name']} Scavenging",
            "description": f"{num_creatures} {selected_creatures[0]['name']}(s) are picking through an old battlefield, looking for valuables.",
            "ecology": "Scavengers cleaning up after past battles. Opportunistic.",
            "tactical_option": "DC 16 Stealth to sneak past OR they might flee if you're intimidating",
            "avoidable": True,
            "surprise_available": True
        }
    
    elif ecology_type == "ritual":
        event = {
            "title": f"{selected_creatures[0]['name']} Ritual",
            "description": f"{num_creatures} {selected_creatures[0]['name']}(s) are performing some kind of ceremony. Chanting, candles, offerings.",
            "ecology": "Religious or magical ritual. They're deeply focused.",
            "tactical_option": "DC 15 Stealth to sneak past OR surprise round if you interrupt",
            "avoidable": True,
            "surprise_available": True
        }
    
    else:  # arguing
        event = {
            "title": f"{selected_creatures[0]['name']} Argument",
            "description": f"{num_creatures} {selected_creatures[0]['name']}(s) are arguing loudly about something. Voices raised, gestures wild.",
            "ecology": "Internal conflict. They have disagreements and politics.",
            "tactical_option": "DC 14 Stealth to sneak past (they're very distracted) OR surprise round",
            "avoidable": True,
            "surprise_available": True
        }
    
    # Add combat stats
    event['creatures'] = [c['name'] for c in selected_creatures]
    event['num_creatures'] = num_creatures
    event['creature_level'] = target_level
    event['floor'] = floor_num
    event['floor_name'] = floor_data.get('name', f'Floor {floor_num}')
    event['difficulty'] = difficulty
    event['difficulty_note'] = difficulty_note
    event['dice_sum'] = dice_sum
    
    # Add floor-specific ecology notes
    if floor_num == 1:
        event['floor_ecology'] = "Mitflits are chaotic and disorganized. They worship a rusty helmet as their 'Sky King'."
    elif floor_num == 2:
        event['floor_ecology'] = "Morlocks worship Belcorra as the 'Ghost Queen'. They're territorial and aggressive."
    elif floor_num == 3:
        event['floor_ecology'] = "Ghouls are stuck in an endless loop: collect flesh, eat flesh, need more flesh."
    elif floor_num == 4:
        event['floor_ecology'] = "This is Belcorra's personal floor. Creatures here serve her directly."
    elif floor_num == 5:
        event['floor_ecology'] = "Arena creatures are trained for combat. Aggressive and dangerous."
    elif floor_num == 6:
        event['floor_ecology'] = "Seugathi are curious researchers. They observe and experiment."
    elif floor_num == 7:
        event['floor_ecology'] = "Devils are lawful and organized. They follow strict hierarchies."
    elif floor_num == 8:
        event['floor_ecology'] = "Bog mummies are the 'Children of Belcorra' - enthralled deep gnomes."
    elif floor_num == 9:
        event['floor_ecology'] = "Multiple factions compete: drow, urdefhan, caligni. Dangerous politics."
    elif floor_num == 10:
        event['floor_ecology'] = "Ancient serpentfolk temple. Reality is thin here."
    
    return event


def generate_event_for_sum(dice_sum, floor_num, floor_data, party_level, creatures, context=None):
    """Generate appropriate event based on dice sum with optional context"""
    from event_context import EventContext
    
    # Use default context if none provided (backward compatibility)
    if context is None:
        context = EventContext()
    
    # Validate context
    context.validate()
    
    # Check if this is an extreme roll
    is_extreme = dice_sum <= 15 or dice_sum >= 90
    
    # Get category (with extreme flag and no-event mechanic)
    category = get_category_from_sum(dice_sum, is_extreme)
    
    # Handle NO_EVENT
    if category == "NO_EVENT":
        return {
            'title': 'Quiet Passage',
            'description': 'The dungeon is quiet. Nothing of note occurs as you continue exploring.',
            'category': 'NO_EVENT',
            'sum': dice_sum,
            'gm_notes': 'No encounter this turn. Continue exploration.'
        }
    
    # For extreme rolls, generate combat at dungeon floor level
    if is_extreme and category == "COMBAT":
        event = generate_extreme_combat_event(floor_num, floor_data, party_level, creatures, dice_sum)
    elif category == "OPPORTUNITY":
        event = generate_opportunity_event(floor_num, floor_data, party_level, context)
    elif category == "COMPLICATION":
        event = generate_complication_event(floor_num, floor_data, party_level, context)
    elif category == "DILEMMA":
        event = generate_dilemma_event(floor_num, floor_data, party_level, context)
    elif category == "ACTIVE_THREAT":
        event = generate_active_threat_event(floor_num, floor_data, party_level, context)
    else:  # COMBAT (non-extreme)
        event = generate_combat_event(floor_num, floor_data, party_level, creatures, dice_sum)
    
    event['sum'] = dice_sum
    event['category'] = category
    if is_extreme:
        event['is_extreme'] = True
    
    return event

def format_event_markdown(event):
    """Format event as markdown for output"""
    lines = []
    
    lines.append(f"## Sum: {event['sum']} - {event['category']}")
    lines.append("")
    lines.append(f"### {event['title']}")
    lines.append("")
    lines.append(f"**Description:** {event['description']}")
    lines.append("")
    
    # Category-specific formatting
    if event['category'] == "OPPORTUNITY":
        lines.append(f"**Challenge:** {event['challenge']}")
        lines.append(f"**Success:** {event['success']}")
        lines.append(f"**Failure:** {event['failure']}")
        lines.append(f"**Spotlight:** {', '.join(event['spotlight'])}")
        lines.append(f"**Skills:** {', '.join(event['skills'])}")
        lines.append(f"**Time Cost:** {event['time_cost']}")
        lines.append(f"**Reward:** {event['reward']}")
        if 'flavor' in event:
            lines.append(f"**Floor Flavor:** {event['flavor']}")
    
    elif event['category'] == "COMPLICATION":
        lines.append(f"**Challenge:** {event['challenge']}")
        lines.append(f"**Success:** {event['success']}")
        lines.append(f"**Failure:** {event['failure']}")
        lines.append(f"**Spotlight:** {', '.join(event['spotlight'])}")
        lines.append(f"**Skills:** {', '.join(event['skills'])}")
        lines.append(f"**Time Cost:** {event['time_cost']}")
        lines.append(f"**Consequence:** {event['consequence']}")
        if 'flavor' in event:
            lines.append(f"**Floor Flavor:** {event['flavor']}")
    
    elif event['category'] == "DILEMMA":
        lines.append(f"**Choice A:** {event['choice_a']}")
        if 'choice_b' in event:
            lines.append(f"**Choice B:** {event['choice_b']}")
        if 'choice_c' in event:
            lines.append(f"**Choice C:** {event['choice_c']}")
        lines.append(f"**Spotlight:** {', '.join(event['spotlight'])}")
        lines.append(f"**Skills:** {', '.join(event['skills'])}")
        lines.append(f"**Time Cost:** {event['time_cost']}")
        lines.append(f"**Consequence:** {event['consequence']}")
        if 'context' in event:
            lines.append(f"**Context:** {event['context']}")
    
    elif event['category'] == "ACTIVE_THREAT":
        lines.append(f"**{event['urgency']}**")
        lines.append("")
        lines.append(f"**Immediate Action:** {event['immediate_action']}")
        lines.append(f"**Success:** {event['success']}")
        lines.append(f"**Failure:** {event['failure']}")
        lines.append(f"**Spotlight:** {', '.join(event['spotlight'])}")
        lines.append(f"**Skills:** {', '.join(event['skills'])}")
        lines.append(f"**Threat Level:** {event['threat_level']}")
    
    else:  # COMBAT
        lines.append(f"**Ecology:** {event['ecology']}")
        lines.append(f"**Creatures:** {event['num_creatures']}x {', '.join(event['creatures'])} (Level {event['creature_level']})")
        lines.append(f"**Difficulty:** {event['difficulty']}")
        lines.append(f"**Tactical Option:** {event['tactical_option']}")
        lines.append(f"**Avoidable:** {'Yes' if event['avoidable'] else 'No'}")
        lines.append(f"**Surprise Available:** {'Yes' if event['surprise_available'] else 'No'}")
        lines.append(f"**Floor Ecology:** {event['floor_ecology']}")
    
    # GM notes for all events
    if 'gm_notes' in event:
        lines.append("")
        lines.append(f"**GM Notes:** {event['gm_notes']}")
    
    lines.append("")
    lines.append("---")
    lines.append("")
    
    return "\n".join(lines)


def generate_all_encounters(party_level, max_floor, output_file, context=None):
    """Generate comprehensive encounter table for all floors with optional context"""
    from event_context import EventContext
    
    # Use default context if none provided
    if context is None:
        context = EventContext()
    
    print(f"=" * 80)
    print(f"DUNGEON TURN GENERATOR V2 - THE FUN VERSION")
    print(f"=" * 80)
    print(f"Party Level: {party_level}")
    print(f"Floors: 1-{max_floor}")
    print(f"Total Events: {96 * max_floor} (96 sums per floor)")
    print(f"")
    print(f"Context Settings:")
    print(f"  Space Type: {context.space_type}")
    print(f"  Recent Combat: {context.recent_combat}")
    print(f"  New Area: {context.new_area}")
    print(f"  Party Status: {context.party_status}")
    print(f"")
    print(f"New Probability Distribution:")
    print(f"  5-25:  OPPORTUNITIES (21 sums, ~22%)")
    print(f"  26-45: COMPLICATIONS (20 sums, ~21%)")
    print(f"  46-65: DILEMMAS (20 sums, ~21%)")
    print(f"  66-85: ACTIVE THREATS (20 sums, ~21%)")
    print(f"  86-100: COMBAT (15 sums, ~16%)")
    print(f"")
    print(f"Combat potential: ~37% (ACTIVE THREATS can become combat)")
    print(f"=" * 80)
    print(f"")
    
    # Load data
    print("Loading data files...")
    gauntlight_content = load_markdown('etc/gauntlight_keep_levels.md')
    levels_data = parse_gauntlight_levels(gauntlight_content)
    creatures = load_json('etc/creatures.json')
    print(f"  Loaded {len(levels_data)} floor definitions")
    print(f"  Loaded {len(creatures)} creatures")
    print("")
    
    # Start building output
    lines = []
    lines.append("# Dungeon Turn Encounters V2 - Gauntlight Keep")
    lines.append("")
    lines.append(f"**Party Level:** {party_level}")
    lines.append(f"**Floors Covered:** 1-{max_floor}")
    lines.append(f"**Generated:** {96 * max_floor} events (sums 5-100 for each floor)")
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
    lines.append("## New Probability Distribution")
    lines.append("")
    lines.append("- **5-25:** OPPORTUNITIES (~22%) - Reward creativity, shortcuts, intel")
    lines.append("- **26-45:** COMPLICATIONS (~21%) - Force skill use, environmental puzzles")
    lines.append("- **46-65:** DILEMMAS (~21%) - Meaningful choices with trade-offs")
    lines.append("- **66-85:** ACTIVE THREATS (~21%) - Immediate danger, patrols, alarms")
    lines.append("- **86-100:** COMBAT (~16%) - Actual fights with dungeon ecology")
    lines.append("")
    lines.append("**Combat Potential:** ~37% (ACTIVE THREATS can escalate to combat)")
    lines.append("")
    lines.append("## Design Philosophy")
    lines.append("")
    lines.append("This system creates **tension** and rewards **creativity**:")
    lines.append("")
    lines.append("- **Every 10 minutes matters** - Dice jar fills, pressure builds")
    lines.append("- **Use ALL your skills** - Not just Detect Magic and Listen")
    lines.append("- **Meaningful choices** - Trade-offs with real consequences")
    lines.append("- **Living dungeon** - Monsters eat, sleep, fight each other")
    lines.append("- **Resource drain** - Without TPK or bogging down gameplay")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Generate events for each floor
    for floor in range(1, max_floor + 1):
        level_data = levels_data.get(floor)
        if not level_data:
            print(f"Warning: No data for floor {floor}, skipping...")
            continue
        
        level_name = level_data['name']
        print(f"Generating Floor {floor}: {level_name}...")
        
        lines.append(f"# Floor {floor}: {level_name}")
        lines.append("")
        
        if level_data.get('theme'):
            lines.append(f"**Theme:** {level_data['theme']}")
            lines.append("")
        
        lines.append("---")
        lines.append("")
        
        # Generate all 96 possible sums (5-100)
        for dice_sum in range(5, 101):
            event = generate_event_for_sum(dice_sum, floor, level_data, party_level, creatures, context)
            lines.append(format_event_markdown(event))
        
        print(f"  [OK] Generated 96 events for Floor {floor}")
        lines.append("")
    
    # Write to file
    print(f"")
    print(f"Writing to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"")
    print(f"=" * 80)
    print(f"GENERATION COMPLETE!")
    print(f"=" * 80)
    print(f"Total events generated: {96 * max_floor}")
    print(f"Output file: {output_file}")
    print(f"")
    print(f"The dungeon is now ALIVE and FUN!")
    print(f"=" * 80)

def main():
    """Main function"""
    import argparse
    from event_context import EventContext
    
    parser = argparse.ArgumentParser(description='Generate Dungeon Turn Encounters V2')
    parser.add_argument('--level', type=int, default=4, help='Party level (default: 4)')
    parser.add_argument('--floors', type=int, default=3, help='Number of floors to generate (1 to X)')
    parser.add_argument('--output', type=str, default='gm/dungeon_turn_encounters_v2.md', help='Output file path')
    
    # Context parameters
    parser.add_argument('--space-type', type=str, default='unknown',
                       choices=['hallway', 'large_room', 'small_room', 'outside', 'vertical_space', 'water', 'unknown'],
                       help='Type of space for event generation (default: unknown)')
    parser.add_argument('--recent-combat', action='store_true',
                       help='Party just finished combat')
    parser.add_argument('--new-area', action='store_true', default=True,
                       help='Party is in unfamiliar area (default: True)')
    parser.add_argument('--party-status', type=str, default='healthy',
                       choices=['healthy', 'injured', 'low_resources'],
                       help='Current party condition (default: healthy)')
    
    args = parser.parse_args()
    
    # Create context from arguments
    context = EventContext(
        space_type=args.space_type,
        recent_combat=args.recent_combat,
        new_area=args.new_area,
        party_status=args.party_status
    )
    
    generate_all_encounters(
        party_level=args.level,
        max_floor=args.floors,
        output_file=args.output,
        context=context
    )

if __name__ == "__main__":
    main()
