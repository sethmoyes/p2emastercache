#!/usr/bin/env python3
"""
Dungeon Turn V2 - Web Interface
A beautiful, simple web app for generating random encounters at the table
"""

from flask import Flask, render_template, jsonify, request
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

if __name__ == '__main__':
    print("\n" + "="*80)
    print("DUNGEON TURN V2 - WEB INTERFACE")
    print("="*80)
    print("\nStarting server...")
    print("Open your browser to: http://localhost:5001")
    print("\nPress Ctrl+C to stop")
    print("="*80 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5001)
