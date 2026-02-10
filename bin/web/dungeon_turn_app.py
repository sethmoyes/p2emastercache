#!/usr/bin/env python3
"""
Dungeon Turn V2 - Web Interface
A beautiful, simple web app for generating random encounters at the table
"""

from flask import Flask, render_template, jsonify, request, send_file
import random
import sys
import os

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
                    'weaknesses': creature.get('weaknesses', [])
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
    sys.path.insert(0, os.path.join(PROJECT_ROOT, 'bin', 'generators'))
    from generate_npc_lore import generate_npc, format_npc_narrative
    
    npc = generate_npc()
    content = format_npc_narrative(npc)
    
    return jsonify({
        'name': npc['name'],
        'content': content
    })

@app.route('/api/generate-merchant', methods=['POST'])
def generate_merchant_api():
    """Generate a merchant with inventory"""
    data = request.json
    name = data.get('name', 'Random Merchant')
    level = data.get('level', 4)
    
    # For now, return a placeholder
    # TODO: Implement full merchant generation
    content = f"""# {name}
    
**Level:** {level}
**Type:** General Goods Merchant

## Inventory
- Common items appropriate for level {level}
- Uncommon items (limited stock)
- Basic adventuring gear

## Services
- Buy/sell equipment
- Repairs and maintenance
- Special orders (1d4 days)

*Full merchant generation coming soon!*
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
    
    # For now, return a placeholder
    # TODO: Implement full 4d20 encounter generation
    content = f"""# Fogfen/Otari Wilderness Encounter
    
**4d20 Total:** {total}

## Encounter Type
{get_4d20_category(total)}

## Description
A wilderness encounter appropriate for the Fogfen or Otari region.

*Full 4d20 encounter generation coming soon!*
"""
    
    return jsonify({
        'total': total,
        'content': content
    })

def get_4d20_category(total):
    """Determine 4d20 encounter category"""
    if total <= 20:
        return "Safe/Beneficial"
    elif total <= 40:
        return "Minor Complication"
    elif total <= 60:
        return "Moderate Threat"
    else:
        return "Dangerous Encounter"

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
