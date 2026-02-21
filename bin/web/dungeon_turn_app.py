#!/usr/bin/env python3
"""
Dungeon Turn V2 - Web Interface
A beautiful, simple web app for generating random encounters at the table
"""

from flask import Flask, render_template, jsonify, request, send_file
import random
import sys
import os
import json

# Get the project root directory (2 levels up from this file)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'bin', 'generators'))

from generate_dungeon_turn_v2 import (
    generate_event_for_sum,
    parse_gauntlight_levels,
    load_json,
    load_markdown
)

app = Flask(__name__)

# Load data once at startup
print("Loading dungeon data...")
gauntlight_path = os.path.join(PROJECT_ROOT, 'etc', 'gauntlight_keep_levels.md')
creatures_path = os.path.join(PROJECT_ROOT, 'etc', 'creatures.json')

gauntlight_content = load_markdown(gauntlight_path)
levels_data = parse_gauntlight_levels(gauntlight_content)
creatures = load_json(creatures_path)
print(f"Loaded {len(levels_data)} floors and {len(creatures)} creatures")

# Session state (in-memory, resets on restart)
dice_jar = 0
roll_history = []

@app.route('/')
def index():
    """Landing page with PLAYER and GM buttons"""
    return render_template('landing.html')

@app.route('/players')
def players():
    """Player-facing market square page"""
    return render_template('players.html')

@app.route('/gm')
def gm():
    """GM tools page (password protected on frontend)"""
    return render_template('gm.html')

@app.route('/api/roll', methods=['POST'])
def roll_dice():
    """Roll 5d20 and return sum"""
    rolls = [random.randint(1, 20) for _ in range(5)]
    total = sum(rolls)
    return jsonify({
        'rolls': rolls,
        'total': total
    })

@app.route('/api/events', methods=['GET'])
def get_events():
    """Return all dungeon turn events for client-side filtering"""
    events_file = os.path.join(PROJECT_ROOT, 'etc', 'dungeon_turn_events.json')
    try:
        with open(events_file, 'r') as f:
            events_data = json.load(f)
        return jsonify(events_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def apply_event_filters(events, filters, floor=None):
    """
    Apply filter criteria to event list.
    
    Args:
        events: List of event dictionaries
        filters: Dictionary with filter parameters:
            - categories: List of category strings (OR logic)
            - skills: List of skill strings (OR logic)
            - timeCost: List of time cost patterns ['quick', 'short', 'long'] (OR logic)
            - newArea: String 'yes', 'no', or 'either'
            - reward: String for text search (case-insensitive, OPPORTUNITY only)
            - threatLevel: List of threat level strings (OR logic, ACTIVE_THREAT only)
        floor: Floor number (1-10) to filter by. If provided, only returns events for that floor or generic events (floor=0)
    
    Returns:
        List of filtered events (AND logic across all filters)
    """
    filtered = events
    
    # Floor filter - CRITICAL for floor selector to work!
    # Events with floor=0 are generic (appear on all floors)
    # Events with floor=1-10 only appear on that specific floor
    if floor is not None:
        filtered = [e for e in filtered if e.get('floor', 0) == 0 or e.get('floor', 0) == floor]
    
    # Category filter (OR logic within filter)
    if filters.get('categories'):
        filtered = [e for e in filtered if e.get('category') in filters['categories']]
    
    # Skills filter (OR logic within filter)
    if filters.get('skills'):
        filtered = [e for e in filtered 
                   if e.get('skills') and any(skill in e['skills'] for skill in filters['skills'])]
    
    # Time cost filter (OR logic within filter)
    if filters.get('timeCost'):
        def matches_time_cost(event, time_costs):
            time_str = event.get('time_cost', '').lower()
            for tc in time_costs:
                if tc == 'quick' and 'action' in time_str:
                    return True
                if tc == 'short' and ('5 min' in time_str or '10 min' in time_str):
                    return True
                if tc == 'long' and ('20 min' in time_str or '30 min' in time_str):
                    return True
            return False
        
        filtered = [e for e in filtered if matches_time_cost(e, filters['timeCost'])]
    
    # New area filter
    if filters.get('newArea') and filters['newArea'] != 'either':
        requires_new = filters['newArea'] == 'yes'
        filtered = [e for e in filtered if e.get('requires_new_area', False) == requires_new]
    
    # Reward filter (text search, case-insensitive, OPPORTUNITY only)
    if filters.get('reward'):
        reward_text = filters['reward'].lower()
        filtered = [e for e in filtered 
                   if e.get('category') == 'OPPORTUNITY' and 
                   reward_text in e.get('reward', '').lower()]
    
    # Threat level filter (OR logic within filter, ACTIVE_THREAT only)
    if filters.get('threatLevel'):
        filtered = [e for e in filtered 
                   if e.get('category') == 'ACTIVE_THREAT' and 
                   any(tl.lower() in e.get('threat_level', '').lower() for tl in filters['threatLevel'])]
    
    return filtered

def generate_filtered_event(filters, floor, floor_data, party_level, creatures):
    """
    Generate event based on filter criteria.
    
    Args:
        filters: Dictionary with filter parameters (see apply_event_filters)
        floor: Floor number (1-10) - NOW USED FOR FILTERING!
        floor_data: Floor data dictionary (for context)
        party_level: Party level (for context)
        creatures: Creatures database (for context)
    
    Returns:
        Dictionary representing the selected event, or an error event if no matches
    """
    # Load all events from dungeon_turn_events.json
    events_file = os.path.join(PROJECT_ROOT, 'etc', 'dungeon_turn_events.json')
    with open(events_file, 'r') as f:
        all_events = json.load(f)
    
    # Flatten events from all categories
    flat_events = []
    for category, events_list in all_events.items():
        for event in events_list:
            # Add category to each event for filtering
            event['category'] = category
            flat_events.append(event)
    
    # Apply filters using apply_event_filters function - NOW INCLUDES FLOOR!
    filtered_events = apply_event_filters(flat_events, filters, floor=floor)
    
    # Handle empty filtered set - return error event
    if not filtered_events:
        return {
            'category': 'ERROR',
            'title': 'No Matching Events',
            'description': f'No events match your criteria for Floor {floor}. Try adjusting your filters or selecting a different floor.',
            'error': True,
            'floor': floor
        }
    
    # Select random event from filtered set
    selected_event = random.choice(filtered_events)
    
    return selected_event

@app.route('/api/encounter', methods=['POST'])
def get_encounter():
    """Generate random encounter for given floor and sum with optional filters"""
    # Import EventContext here to avoid circular imports
    sys.path.insert(0, os.path.join(PROJECT_ROOT, 'bin', 'generators'))
    from event_context import EventContext
    
    data = request.json
    floor = data.get('floor', 1)
    dice_sum = data.get('sum')
    party_level = data.get('party_level', 4)
    
    # Extract filter parameters (optional)
    filters = data.get('filters', {})
    
    # Check if filters are provided and non-empty
    # Consider a filter active if it has non-empty arrays or non-default values
    has_filters = False
    if filters:
        has_filters = (
            (filters.get('categories') and len(filters['categories']) > 0) or
            (filters.get('skills') and len(filters['skills']) > 0) or
            (filters.get('timeCost') and len(filters['timeCost']) > 0) or
            (filters.get('newArea') and filters['newArea'] != 'either') or
            (filters.get('reward') and len(filters['reward'].strip()) > 0) or
            (filters.get('threatLevel') and len(filters['threatLevel']) > 0)
        )
    
    # Get floor data
    floor_data = levels_data.get(floor)
    if not floor_data:
        return jsonify({'error': f'Floor {floor} not found'}), 404
    
    # If filters provided, use filtered event generation
    if has_filters:
        event = generate_filtered_event(filters, floor, floor_data, party_level, creatures)
    else:
        # Use existing event generation logic for backward compatibility
        # Extract context parameters (with defaults)
        space_type = data.get('space_type', 'unknown')
        recent_combat = data.get('recent_combat', False)
        new_area = data.get('new_area', True)
        party_status = data.get('party_status', 'healthy')
        
        if not dice_sum:
            return jsonify({'error': 'Sum required'}), 400
        
        # Create context
        try:
            context = EventContext(
                space_type=space_type,
                recent_combat=recent_combat,
                new_area=new_area,
                party_status=party_status
            )
            context.validate()
        except ValueError as e:
            return jsonify({'error': f'Invalid context: {str(e)}'}), 400
        
        # Generate event with context
        event = generate_event_for_sum(dice_sum, floor, floor_data, party_level, creatures, context)
    
    # If it's a combat encounter, add full creature stats
    if event.get('category') == 'COMBAT' and event.get('creatures'):
        creature_names = event.get('creatures', [])
        creature_stats = []
        for name in creature_names:
            # Find creature in database
            creature = next((c for c in creatures if c['name'] == name), None)
            if creature:
                creature_stats.append({
                    'name': creature['name'],
                    'level': creature['level'],
                    'hp': creature.get('hp', 'Unknown'),
                    'ac': creature.get('ac', 'Unknown'),
                    'fort': creature.get('fort', ''),
                    'reflex': creature.get('reflex', ''),
                    'will': creature.get('will', ''),
                    'perception': creature.get('perception', ''),
                    'attacks': creature.get('attacks', []),
                    'abilities': creature.get('abilities', []),
                    'skills': creature.get('skills', {}),
                    'languages': creature.get('languages', []),
                    'immunities': creature.get('immunities', []),
                    'resistances': creature.get('resistances', []),
                    'weaknesses': creature.get('weaknesses', []),
                    'traits': creature.get('traits', []),
                    'rarity': creature.get('rarity', 'common'),
                    'size': creature.get('size', 'Medium'),
                    'alignment': creature.get('alignment', ''),
                    'creature_type': creature.get('creature_type', ''),
                    'url': creature.get('url', ''),
                    'image': creature.get('image', [''])[0] if creature.get('image') else ''
                })
        event['creature_stats'] = creature_stats
    
    # Add to history
    roll_history.append({
        'floor': floor,
        'sum': dice_sum,
        'category': event['category'],
        'title': event['title']
    })
    
    return jsonify(event)

@app.route('/api/dice-jar', methods=['GET', 'POST'])
def dice_jar_api():
    """Get or update dice jar count"""
    global dice_jar
    
    if request.method == 'POST':
        data = request.json
        action = data.get('action')
        
        if action == 'add':
            dice_jar = min(dice_jar + 1, 5)
        elif action == 'reset':
            dice_jar = 0
        elif action == 'set':
            dice_jar = max(0, min(data.get('value', 0), 5))
        
        return jsonify({'dice_jar': dice_jar})
    
    return jsonify({'dice_jar': dice_jar})

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get roll history"""
    return jsonify({'history': roll_history[-10:]})  # Last 10 rolls

@app.route('/api/clear-history', methods=['POST'])
def clear_history():
    """Clear roll history"""
    global roll_history
    roll_history = []
    return jsonify({'success': True})

@app.route('/api/test-ghoul', methods=['GET'])
def test_ghoul():
    """Test endpoint to force a Ghoul encounter"""
    # Find Ghoul in database
    ghoul = next((c for c in creatures if c['name'] == 'Ghoul' and c.get('attacks')), None)
    
    if not ghoul:
        return jsonify({'error': 'Ghoul not found'}), 404
    
    event = {
        'title': 'Test Ghoul Encounter',
        'description': 'A Ghoul emerges from the shadows, hungry for flesh.',
        'category': 'COMBAT',
        'floor': 1,
        'sum': 90,
        'creatures': ['Ghoul'],
        'num_creatures': 1,
        'creature_level': ghoul['level'],
        'difficulty': 'Test',
        'ecology': 'Test encounter to verify enhanced creature display',
        'tactical_option': 'This is a test',
        'avoidable': False,
        'surprise_available': False,
        'creature_stats': [{
            'name': ghoul['name'],
            'level': ghoul['level'],
            'hp': ghoul.get('hp', 'Unknown'),
            'ac': ghoul.get('ac', 'Unknown'),
            'fort': ghoul.get('fort', ''),
            'reflex': ghoul.get('reflex', ''),
            'will': ghoul.get('will', ''),
            'perception': ghoul.get('perception', ''),
            'attacks': ghoul.get('attacks', []),
            'abilities': ghoul.get('abilities', []),
            'skills': ghoul.get('skills', {}),
            'languages': ghoul.get('languages', []),
            'immunities': ghoul.get('immunities', []),
            'resistances': ghoul.get('resistances', []),
            'weaknesses': ghoul.get('weaknesses', [])
        }]
    }
    
    return jsonify(event)

@app.route('/api/generate-npc', methods=['GET'])
def generate_npc_api():
    """Generate a random NPC"""
    try:
        sys.path.insert(0, os.path.join(PROJECT_ROOT, 'bin', 'generators'))
        from generate_npc_lore import generate_npc, format_npc_narrative, generate_npc_encounter_template
        
        npc = generate_npc()
        template = generate_npc_encounter_template(npc)
        narrative = format_npc_narrative(npc)
        
        content = f"""# {template['name']}

**Race:** {template['race']}
**Profession:** {template['profession']}
**Personality:** {template['personality']}

## Setup
{template['setup']}

## Read-Aloud
{template['readaloud']}

## Background
{narrative}

## GM Notes
- Use this NPC for social encounters
- Can provide information, quests, or complications
- Personality: {template['personality']}
"""
        
        return jsonify({
            'name': template['name'],
            'content': content
        })
    except Exception as e:
        return jsonify({
            'name': 'Error',
            'content': f'Error generating NPC: {str(e)}'
        }), 500

@app.route('/api/generate-merchant', methods=['POST'])
def generate_merchant_api():
    """Generate a merchant with inventory"""
    data = request.json
    name = data.get('name', 'Random Merchant')
    level = data.get('level', 4)
    
    # Load equipment data
    equipment_path = os.path.join(PROJECT_ROOT, 'etc', 'equipment.json')
    try:
        with open(equipment_path, 'r') as f:
            equipment = json.load(f)
    except:
        equipment = []
    
    # Filter items by level
    available_items = [item for item in equipment if item.get('level', 0) <= level and item.get('level', 0) > 0]
    
    # Separate by rarity
    common_items = [item for item in available_items if item.get('rarity', '').lower() == 'common']
    uncommon_items = [item for item in available_items if item.get('rarity', '').lower() == 'uncommon']
    
    # Select random items
    num_common = min(10, len(common_items))
    num_uncommon = min(5, len(uncommon_items))
    
    selected_common = random.sample(common_items, num_common) if common_items else []
    selected_uncommon = random.sample(uncommon_items, num_uncommon) if uncommon_items else []
    
    # Generate merchant personality
    personalities = ['friendly', 'gruff', 'suspicious', 'enthusiastic', 'bored', 'chatty']
    personality = random.choice(personalities)
    
    content = f"""# {name}
**Level:** {level}
**Personality:** {personality.title()}

## Common Items ({len(selected_common)})
"""
    
    for item in selected_common:
        content += f"- **{item['name']}** (Level {item.get('level', '?')}) - {item.get('price', '?')} gp\n"
    
    if selected_uncommon:
        content += f"\n## Uncommon Items ({len(selected_uncommon)})\n"
        for item in selected_uncommon:
            content += f"- **{item['name']}** (Level {item.get('level', '?')}) - {item.get('price', '?')} gp\n"
    
    content += """
## Services
- Buy/sell equipment at standard prices
- Repairs and maintenance (10% of item cost)
- Special orders available (1d4 days, +20% cost)
"""
    
    return jsonify({
        'name': name,
        'content': content
    })

@app.route('/api/generate-4d20', methods=['POST'])
def generate_4d20_api():
    """Generate 4d20 wilderness encounter"""
    data = request.json
    total = data.get('total', 40)
    
    # Determine encounter type based on total
    if total <= 20:
        category = "Safe Travel"
        encounters = [
            "Clear weather and easy terrain. Make good time.",
            "Find a safe campsite with fresh water nearby.",
            "Spot wildlife in the distance - deer, rabbits, birds.",
            "Discover edible berries or mushrooms (DC 15 Nature to identify).",
            "Meet friendly travelers heading the opposite direction."
        ]
    elif total <= 40:
        category = "Minor Complication"
        encounters = [
            "Muddy terrain slows travel. Lose 1 hour.",
            "Light rain begins. DC 12 Survival to stay dry.",
            "Hear strange noises in the distance. Nothing dangerous.",
            "Path is blocked by fallen tree. Must find way around.",
            "One party member's rations spoil. Need to forage or share."
        ]
    elif total <= 60:
        category = "Moderate Challenge"
        encounters = [
            f"Encounter {random.randint(1,3)} hostile creatures (level {max(1, total//20)}).",
            "Dangerous terrain. DC 15 Acrobatics or take 1d6 damage.",
            "Sudden storm. Must find shelter or risk exposure.",
            "Bandit scouts watching from distance. May attack if party looks weak.",
            "Trapped area. DC 16 Perception to notice, DC 14 Thievery to disarm."
        ]
    else:
        category = "Dangerous Encounter"
        encounters = [
            f"Combat! {random.randint(2,4)} creatures (level {max(2, total//15)}) attack!",
            "Ambush! Enemies have surprise round. DC 18 Perception to avoid.",
            "Severe weather. Must make DC 17 Fortitude saves or gain Fatigued.",
            "Territorial predator. Large creature (level {}) defends its hunting ground.".format(max(3, total//12)),
            "Hostile humanoids demand toll. Fight or pay 50gp per person."
        ]
    
    encounter = random.choice(encounters)
    
    content = f"""# Fogfen/Otari Wilderness Encounter

**4d20 Total:** {total}
**Category:** {category}

## Encounter
{encounter}

## Terrain
The Fogfen is a misty marshland between Otari and the wilderness. Visibility is limited, and the ground is treacherous.

## GM Notes
- Adjust difficulty based on party level
- Consider time of day and weather
- Use this as opportunity for roleplay or resource management
- Can lead to side quests or discoveries

## Possible Developments
- Party finds clues about larger threats
- NPCs encountered may reappear later
- Environmental hazards can create memorable moments
"""
    
    return jsonify({
        'total': total,
        'content': content
    })

@app.route('/api/generate-v1', methods=['POST'])
def generate_v1_api():
    """Generate Dungeon Turn V1 encounter"""
    data = request.json
    floor = data.get('floor', 1)
    
    # Roll 5d20
    rolls = [random.randint(1, 20) for _ in range(5)]
    total = sum(rolls)
    
    # Simple V1 logic
    if total <= 25:
        category = "Nothing"
        result = "The dungeon is quiet. No encounter."
    elif total <= 50:
        category = "Clue/Discovery"
        discoveries = [
            "Find old graffiti on the wall",
            "Discover a hidden cache with minor supplies",
            "Notice tracks leading deeper into the dungeon",
            "Hear distant sounds echoing through the halls",
            "Find evidence of recent activity"
        ]
        result = random.choice(discoveries)
    elif total <= 75:
        category = "Hazard/Trap"
        hazards = [
            "Pit trap! DC 15 Perception to notice, DC 13 Reflex to avoid",
            "Unstable floor. DC 14 Acrobatics or fall through",
            "Poison gas seeps from cracks. DC 16 Fortitude save",
            "Magical ward triggers. DC 15 Will save or Frightened 1",
            "Collapsing ceiling. DC 17 Reflex or take 2d6 damage"
        ]
        result = random.choice(hazards)
    else:
        category = "Combat Encounter"
        result = f"Encounter {random.randint(1, 3)} creatures appropriate for Floor {floor}"
    
    content = f"""# Dungeon Turn V1 - Floor {floor}

**Dice Rolls:** {rolls[0]}, {rolls[1]}, {rolls[2]}, {rolls[3]}, {rolls[4]}
**Total:** {total}
**Category:** {category}

## Result
{result}

## Notes
This is the original Dungeon Turn system (V1). For the enhanced system with ecology and tactical options, use the main encounter generator above.
"""
    
    return jsonify({
        'floor': floor,
        'content': content
    })

@app.route('/api/view-doc', methods=['POST'])
def view_doc_api():
    """View a markdown document"""
    data = request.json
    doc_path = data.get('path', '')
    
    full_path = os.path.join(PROJECT_ROOT, doc_path)
    
    if not os.path.exists(full_path):
        return jsonify({'error': 'Document not found'}), 404
    
    with open(full_path, 'r') as f:
        content = f.read()
    
    # Simple markdown to HTML conversion (basic)
    html = content.replace('\n', '<br>')
    html = html.replace('# ', '<h1 class="text-3xl font-bold mt-6 mb-4">')
    html = html.replace('## ', '<h2 class="text-2xl font-bold mt-4 mb-3">')
    html = html.replace('### ', '<h3 class="text-xl font-bold mt-3 mb-2">')
    html = html.replace('**', '<strong>')
    html = html.replace('*', '<em>')
    
    title = os.path.basename(doc_path).replace('.md', '').replace('_', ' ').title()
    
    return jsonify({
        'title': title,
        'html': html,
        'raw': content
    })

@app.route('/api/download-doc', methods=['GET'])
def download_doc_api():
    """Download a markdown document"""
    doc_path = request.args.get('path', '')
    full_path = os.path.join(PROJECT_ROOT, doc_path)
    
    if not os.path.exists(full_path):
        return jsonify({'error': 'Document not found'}), 404
    
    return send_file(full_path, as_attachment=True)

@app.route('/api/generate-hazard', methods=['POST'])
def generate_hazard_api():
    """Generate a random hazard of specified level"""
    data = request.json
    level = data.get('level', 1)
    
    try:
        sys.path.insert(0, os.path.join(PROJECT_ROOT, 'bin', 'generators'))
        from generate_hazard import generate_hazard, format_output
        
        hazard = generate_hazard(level)
        content = format_output(hazard)
        
        return jsonify({
            'level': level,
            'name': hazard.get('name', 'Unknown'),
            'content': content,
            'hazard': hazard
        })
    except Exception as e:
        return jsonify({
            'level': level,
            'name': 'Error',
            'content': f'Error generating hazard: {str(e)}'
        }), 500

@app.route('/api/merchant/<merchant_file>', methods=['GET'])
def get_merchant(merchant_file):
    """Load a merchant markdown file and return as HTML"""
    # Sanitize filename
    if not merchant_file.replace('_', '').isalnum():
        return jsonify({'error': 'Invalid merchant file'}), 400
    
    merchant_path = os.path.join(PROJECT_ROOT, 'players', f'{merchant_file}.md')
    
    if not os.path.exists(merchant_path):
        return jsonify({'error': 'Merchant not found'}), 404
    
    try:
        with open(merchant_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Convert markdown to HTML (basic conversion)
        html = markdown_to_html(content)
        
        # Extract title from first # heading
        title_match = content.split('\n')[0]
        if title_match.startswith('#'):
            title = title_match.lstrip('#').strip()
        else:
            title = merchant_file.replace('_', ' ').title()
        
        return jsonify({
            'title': title,
            'html': html,
            'raw': content
        })
    except Exception as e:
        return jsonify({'error': f'Error loading merchant: {str(e)}'}), 500

@app.route('/api/document/<doc_name>', methods=['GET'])
def get_document(doc_name):
    """Load a documentation file and return as HTML"""
    # Sanitize filename
    if not doc_name.replace('_', '').isalnum():
        return jsonify({'error': 'Invalid document name'}), 400
    
    doc_path = os.path.join(PROJECT_ROOT, 'docs', f'{doc_name}.md')
    
    if not os.path.exists(doc_path):
        return jsonify({'error': 'Document not found'}), 404
    
    try:
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Convert markdown to HTML
        html = markdown_to_html(content)
        
        # Extract title
        title_match = content.split('\n')[0]
        if title_match.startswith('#'):
            title = title_match.lstrip('#').strip()
        else:
            title = doc_name.replace('_', ' ').title()
        
        return jsonify({
            'title': title,
            'html': html,
            'raw': content
        })
    except Exception as e:
        return jsonify({'error': f'Error loading document: {str(e)}'}), 500

def markdown_to_html(markdown_text):
    """Convert markdown to HTML with proper table support"""
    import re
    
    # Process tables first (before line breaks)
    lines = markdown_text.split('\n')
    result = []
    in_table = False
    table_lines = []
    
    for i, line in enumerate(lines):
        # Detect table rows (contains |)
        if '|' in line and line.strip().startswith('|'):
            if not in_table:
                in_table = True
                table_lines = []
            table_lines.append(line)
        else:
            # End of table
            if in_table:
                result.append(convert_table_to_html(table_lines))
                in_table = False
                table_lines = []
            result.append(line)
    
    # Handle table at end of file
    if in_table:
        result.append(convert_table_to_html(table_lines))
    
    html = '\n'.join(result)
    
    # Headers
    html = re.sub(r'^# (.+)$', r'<h1 class="text-4xl font-bold mt-8 mb-4 text-blue-400">\1</h1>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2 class="text-3xl font-bold mt-6 mb-3 text-purple-400">\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.+)$', r'<h3 class="text-2xl font-bold mt-4 mb-2 text-pink-400">\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^#### (.+)$', r'<h4 class="text-xl font-bold mt-3 mb-2 text-white">\1</h4>', html, flags=re.MULTILINE)
    
    # Horizontal rules
    html = re.sub(r'^---+$', r'<hr class="my-6 border-gray-600">', html, flags=re.MULTILINE)
    
    # Bold and italic
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong class="text-white font-bold">\1</strong>', html)
    html = re.sub(r'\*(.+?)\*', r'<em class="text-gray-300">\1</em>', html)
    
    # Images (convert markdown syntax to HTML)
    html = re.sub(r'!\[([^\]]*)\]\(([^\)]+)\)', r'<img src="\2" alt="\1" class="max-w-xs h-auto rounded border border-gray-600" loading="lazy">', html)
    
    # Links
    html = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2" class="text-blue-400 hover:text-blue-300 underline" target="_blank">\1</a>', html)
    
    # Lists
    lines = html.split('\n')
    in_list = False
    result = []
    for line in lines:
        if line.strip().startswith('- '):
            if not in_list:
                result.append('<ul class="list-disc list-inside ml-4 space-y-1 text-gray-300 mb-4">')
                in_list = True
            result.append(f'<li class="ml-4">{line.strip()[2:]}</li>')
        else:
            if in_list:
                result.append('</ul>')
                in_list = False
            result.append(line)
    if in_list:
        result.append('</ul>')
    html = '\n'.join(result)
    
    # Paragraphs (but not for lines that are already HTML)
    lines = html.split('\n')
    result = []
    for line in lines:
        if line.strip() and not line.strip().startswith('<') and not line.strip().endswith('>'):
            result.append(f'<p class="mb-3 text-gray-300">{line}</p>')
        else:
            result.append(line)
    html = '\n'.join(result)
    
    return html

def convert_table_to_html(table_lines):
    """Convert markdown table to HTML table"""
    if len(table_lines) < 2:
        return '\n'.join(table_lines)
    
    # Parse header
    header_line = table_lines[0]
    headers = [cell.strip() for cell in header_line.split('|')[1:-1]]  # Skip first and last empty
    
    # Skip separator line (table_lines[1])
    
    # Parse rows
    rows = []
    for line in table_lines[2:]:
        if '|' in line:
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            rows.append(cells)
    
    # Build HTML table
    html = '<div class="overflow-x-auto my-6">'
    html += '<table class="min-w-full bg-gray-900 border border-gray-700 rounded-lg">'
    
    # Header
    html += '<thead class="bg-gray-800">'
    html += '<tr>'
    for header in headers:
        html += f'<th class="px-4 py-3 text-left text-sm font-bold text-purple-400 border-b border-gray-700">{header}</th>'
    html += '</tr>'
    html += '</thead>'
    
    # Body
    html += '<tbody>'
    for i, row in enumerate(rows):
        bg_class = 'bg-gray-900' if i % 2 == 0 else 'bg-gray-850'
        html += f'<tr class="{bg_class} hover:bg-gray-800 transition">'
        for cell in row:
            html += f'<td class="px-4 py-3 text-sm text-gray-300 border-b border-gray-700">{cell}</td>'
        html += '</tr>'
    html += '</tbody>'
    
    html += '</table>'
    html += '</div>'
    
    return html

@app.route('/api/generate-merchants', methods=['POST'])
def generate_merchants_api():
    """Generate merchants using the generate_merchants.py script"""
    import subprocess
    import threading
    from queue import Queue
    
    data = request.json
    player_level = data.get('player_level', 4)
    
    # Validate player level
    if not isinstance(player_level, int) or player_level < 1 or player_level > 20:
        return jsonify({'error': 'Player level must be between 1 and 20'}), 400
    
    # Path to the script
    script_path = os.path.join(PROJECT_ROOT, 'bin', 'generators', 'generate_merchants.py')
    
    # Run the script as a subprocess
    try:
        # Change to the project root directory so relative paths work
        process = subprocess.Popen(
            [sys.executable, script_path, str(player_level)],
            cwd=PROJECT_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # Collect output
        output_lines = []
        for line in process.stdout:
            output_lines.append(line.strip())
        
        process.wait()
        
        if process.returncode == 0:
            return jsonify({
                'success': True,
                'message': 'Merchants generated successfully!',
                'output': '\n'.join(output_lines)
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Script failed',
                'output': '\n'.join(output_lines)
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/generate-merchants-stream', methods=['GET'])
def generate_merchants_stream():
    """Stream merchant generation progress"""
    import subprocess
    from flask import Response, stream_with_context
    
    player_level = request.args.get('player_level', 4, type=int)
    
    # Validate player level
    if player_level < 1 or player_level > 20:
        return jsonify({'error': 'Player level must be between 1 and 20'}), 400
    
    # Path to the script
    script_path = os.path.join(PROJECT_ROOT, 'bin', 'generators', 'generate_merchants.py')
    
    def generate():
        try:
            process = subprocess.Popen(
                [sys.executable, script_path, '--level', str(player_level)],
                cwd=PROJECT_ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            for line in process.stdout:
                yield f"data: {json.dumps({'line': line.strip()})}\n\n"
            
            process.wait()
            
            if process.returncode == 0:
                yield f"data: {json.dumps({'done': True, 'success': True})}\n\n"
            else:
                yield f"data: {json.dumps({'done': True, 'success': False, 'error': 'Script failed'})}\n\n"
                
        except Exception as e:
            yield f"data: {json.dumps({'done': True, 'success': False, 'error': str(e)})}\n\n"
    
    return Response(stream_with_context(generate()), mimetype='text/event-stream')

@app.route('/api/run-data-integrity', methods=['POST'])
def run_data_integrity():
    """Run data integrity checker"""
    import subprocess
    
    data = request.json
    data_type = data.get('type', 'equipment')
    count = data.get('count', 10)
    fix = data.get('fix', False)
    
    script_path = os.path.join(PROJECT_ROOT, 'bin', 'data_management', 'check_data_integrity.py')
    
    try:
        args = [sys.executable, script_path, str(count), data_type]
        if fix:
            args.append('--replace')
        
        process = subprocess.Popen(
            args,
            cwd=PROJECT_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        output_lines = []
        for line in process.stdout:
            output_lines.append(line.strip())
        
        process.wait()
        
        return jsonify({
            'success': process.returncode == 0,
            'output': '\n'.join(output_lines[-50:])  # Last 50 lines
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/scrape-creatures', methods=['POST'])
def scrape_creatures():
    """Scrape all creatures from AoN"""
    import subprocess
    
    script_path = os.path.join(PROJECT_ROOT, 'bin', 'scrapers', 'scrape_all_creatures.py')
    
    try:
        process = subprocess.Popen(
            [sys.executable, script_path],
            cwd=PROJECT_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        output_lines = []
        for line in process.stdout:
            output_lines.append(line.strip())
        
        process.wait()
        
        return jsonify({
            'success': process.returncode == 0,
            'output': '\n'.join(output_lines[-50:])
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/scrape-creature-lore', methods=['POST'])
def scrape_creature_lore():
    """Scrape creature lore from AoN"""
    import subprocess
    
    script_path = os.path.join(PROJECT_ROOT, 'bin', 'scrapers', 'scrape_creature_lore.py')
    
    try:
        process = subprocess.Popen(
            [sys.executable, script_path],
            cwd=PROJECT_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        output_lines = []
        for line in process.stdout:
            output_lines.append(line.strip())
        
        process.wait()
        
        return jsonify({
            'success': process.returncode == 0,
            'output': '\n'.join(output_lines[-50:])
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/scrape-spells', methods=['POST'])
def scrape_spells():
    """Scrape spells from AoN"""
    import subprocess
    
    script_path = os.path.join(PROJECT_ROOT, 'bin', 'scrapers', 'scrape_spells.py')
    
    try:
        process = subprocess.Popen(
            [sys.executable, script_path],
            cwd=PROJECT_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        output_lines = []
        for line in process.stdout:
            output_lines.append(line.strip())
        
        process.wait()
        
        return jsonify({
            'success': process.returncode == 0,
            'output': '\n'.join(output_lines[-50:])
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/expand-encounter-pools', methods=['POST'])
def expand_encounter_pools():
    """Expand encounter pools"""
    import subprocess
    
    script_path = os.path.join(PROJECT_ROOT, 'bin', 'data_management', 'expand_encounter_pools.py')
    
    try:
        process = subprocess.Popen(
            [sys.executable, script_path],
            cwd=PROJECT_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        output_lines = []
        for line in process.stdout:
            output_lines.append(line.strip())
        
        process.wait()
        
        return jsonify({
            'success': process.returncode == 0,
            'output': '\n'.join(output_lines[-50:])
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/reset-verification', methods=['POST'])
def reset_verification():
    """Reset verification dates"""
    import subprocess
    
    data = request.json
    data_type = data.get('type', 'equipment')
    
    script_path = os.path.join(PROJECT_ROOT, 'bin', 'data_management', 'reset_verification_dates.py')
    
    try:
        process = subprocess.Popen(
            [sys.executable, script_path, data_type],
            cwd=PROJECT_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        output_lines = []
        for line in process.stdout:
            output_lines.append(line.strip())
        
        process.wait()
        
        return jsonify({
            'success': process.returncode == 0,
            'output': '\n'.join(output_lines[-50:])
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*80)
    print("DUNGEON TURN V2 - WEB INTERFACE")
    print("="*80)
    print("\nStarting server...")
    print("Open your browser to: http://localhost:5001")
    print("\nPress Ctrl+C to stop")
    print("="*80 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5001)
