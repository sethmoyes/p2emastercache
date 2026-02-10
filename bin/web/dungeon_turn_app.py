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
    """Main page"""
    return render_template('index.html')

@app.route('/api/roll', methods=['POST'])
def roll_dice():
    """Roll 5d20 and return sum"""
    rolls = [random.randint(1, 20) for _ in range(5)]
    total = sum(rolls)
    return jsonify({
        'rolls': rolls,
        'total': total
    })

@app.route('/api/encounter', methods=['POST'])
def get_encounter():
    """Generate random encounter for given floor and sum"""
    data = request.json
    floor = data.get('floor', 1)
    dice_sum = data.get('sum')
    party_level = data.get('party_level', 4)
    
    if not dice_sum:
        return jsonify({'error': 'Sum required'}), 400
    
    # Get floor data
    floor_data = levels_data.get(floor)
    if not floor_data:
        return jsonify({'error': f'Floor {floor} not found'}), 404
    
    # Generate event
    event = generate_event_for_sum(dice_sum, floor, floor_data, party_level, creatures)
    
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
                    'url': creature.get('url', '')
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

if __name__ == '__main__':
    print("\n" + "="*80)
    print("DUNGEON TURN V2 - WEB INTERFACE")
    print("="*80)
    print("\nStarting server...")
    print("Open your browser to: http://localhost:5001")
    print("\nPress Ctrl+C to stop")
    print("="*80 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5001)
