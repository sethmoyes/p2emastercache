#!/usr/bin/env python3
"""
Expand encounter pools by pulling creatures from creatures.json
Creates massive pools to eliminate duplicate encounters
"""
import json
import random

# Load creatures
with open('etc/creatures.json', 'r', encoding='utf-8') as f:
    creatures = json.load(f)

# Setup templates for variety
SETUPS = [
    'Strange sounds echo ahead.',
    'Something moves in the shadows.',
    'The air grows thick with menace.',
    'Danger approaches rapidly.',
    'An unnatural presence fills the area.',
    'You sense hostile intent nearby.',
    'The path ahead is blocked.',
    'A threatening shape emerges.',
]

READALOUDS = [
    'A {name} emerges from the mist!',
    'The {name} roars and charges!',
    'You spot a {name} ahead, and it spots you.',
    'A {name} stalks toward you with hostile intent.',
    'From the shadows, a {name} attacks!',
    'A {name} blocks your path menacingly.',
    'A {name} rises before you, ready for battle.',
]

TACTICS_BY_TYPE = {
    'dragon': 'Breath weapon, flies',
    'undead': 'Relentless, no morale',
    'aberration': 'Alien tactics, unpredictable',
    'beast': 'Animal instincts, territorial',
    'fey': 'Trickery, illusions',
    'fiend': 'Evil, cunning',
    'giant': 'Overwhelming strength',
    'humanoid': 'Intelligent, may negotiate',
    'default': 'Standard combat tactics'
}

def get_tactics(creature):
    """Determine tactics based on creature type"""
    # Check for dragon in name
    if 'dragon' in creature['name'].lower():
        return 'Intelligent, may negotiate'
    if 'dragon' in creature.get('type', '').lower():
        return 'Breath weapon, flies'
    
    # Check creature type
    ctype = creature.get('type', '').lower()
    for key in TACTICS_BY_TYPE:
        if key in ctype:
            return TACTICS_BY_TYPE[key]
    
    return TACTICS_BY_TYPE['default']

def create_encounter(creature):
    """Create an encounter template from a creature"""
    # Extract traits as keywords for better lore matching
    traits = creature.get('trait', '').split(', ')
    # Add creature family if available
    if creature.get('creature_family'):
        traits.append(creature['creature_family'])
    
    # Clean up traits - remove empty strings and generic ones
    keywords = [t.strip() for t in traits if t.strip() and t.strip() not in ['Common', 'Uncommon', 'Rare', 'Unique']]
    
    # If no good keywords, use generic ones
    if not keywords:
        keywords = ['creature', 'monster', 'wilderness']
    
    return {
        'name': creature['name'],
        'level': creature['level'],  # Include level for filtering
        'hp': creature['hp'],
        'ac': creature['ac'],
        'fort': creature.get('fort', ''),
        'reflex': creature.get('reflex', ''),
        'will': creature.get('will', ''),
        'description': f"A dangerous {creature['name']}",
        'tactics': get_tactics(creature),
        'setup': random.choice(SETUPS),
        'readaloud': random.choice(READALOUDS).format(name=creature['name']),
        'lore_keywords': keywords
    }

# Filter creatures by level
print("Filtering creatures by level...")
deadly = [c for c in creatures if c['level'] >= 5]
difficult = [c for c in creatures if c['level'] == 4]
moderate = [c for c in creatures if c['level'] == 3]
easy = [c for c in creatures if c['level'] == 2]

print(f"Found: {len(deadly)} deadly, {len(difficult)} difficult, {len(moderate)} moderate, {len(easy)} easy")

# Create encounter pools
print("\nCreating encounter pools...")
DEADLY_POOL = [create_encounter(c) for c in deadly]
DIFFICULT_POOL = [create_encounter(c) for c in difficult]
MODERATE_POOL = [create_encounter(c) for c in moderate]
EASY_POOL = [create_encounter(c) for c in easy]

print(f"Created: {len(DEADLY_POOL)} deadly, {len(DIFFICULT_POOL)} difficult, {len(MODERATE_POOL)} moderate, {len(EASY_POOL)} easy")

# Save to file
output = {
    'DEADLY_POOL': DEADLY_POOL,
    'DIFFICULT_POOL': DIFFICULT_POOL,
    'MODERATE_POOL': MODERATE_POOL,
    'EASY_POOL': EASY_POOL
}

with open('etc/expanded_pools.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"\nSaved expanded pools to etc/expanded_pools.json")
print(f"Total encounters: {len(DEADLY_POOL) + len(DIFFICULT_POOL) + len(MODERATE_POOL) + len(EASY_POOL)}")
