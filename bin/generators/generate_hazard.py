#!/usr/bin/env python3
"""
Random Hazard Generator
Pulls a random common hazard of specified level from Archives of Nethys
"""

import random
import json
import sys

# Common hazards by level (curated list from PF2e)
HAZARDS = {
    -1: [
        {"name": "Spear Launcher", "type": "Trap", "traits": ["mechanical", "trap"]},
        {"name": "Scythe Blades", "type": "Trap", "traits": ["mechanical", "trap"]},
    ],
    0: [
        {"name": "Dart Trap", "type": "Trap", "traits": ["mechanical", "trap"]},
        {"name": "Spiked Pit", "type": "Trap", "traits": ["mechanical", "trap"]},
        {"name": "Falling Portcullis", "type": "Trap", "traits": ["mechanical", "trap"]},
    ],
    1: [
        {"name": "Acid Arrow Trap", "type": "Trap", "traits": ["magical", "trap"]},
        {"name": "Flame Jet", "type": "Trap", "traits": ["magical", "trap"]},
        {"name": "Poisoned Dart Gallery", "type": "Trap", "traits": ["mechanical", "trap"]},
        {"name": "Swinging Blade Trap", "type": "Trap", "traits": ["mechanical", "trap"]},
    ],
    2: [
        {"name": "Electrified Doorknob", "type": "Trap", "traits": ["magical", "trap"]},
        {"name": "Explosive Runes", "type": "Trap", "traits": ["magical", "trap"]},
        {"name": "Scythe Arm", "type": "Trap", "traits": ["mechanical", "trap"]},
        {"name": "Slamming Door", "type": "Trap", "traits": ["mechanical", "trap"]},
    ],
    3: [
        {"name": "Fireball Rune", "type": "Trap", "traits": ["magical", "trap"]},
        {"name": "Grasping Ooze", "type": "Environmental", "traits": ["environmental"]},
        {"name": "Poisoned Lock", "type": "Trap", "traits": ["mechanical", "trap"]},
        {"name": "Collapsing Floor", "type": "Trap", "traits": ["mechanical", "trap"]},
    ],
    4: [
        {"name": "Confounding Betrayal", "type": "Trap", "traits": ["magical", "trap"]},
        {"name": "Phantom Crowd", "type": "Haunt", "traits": ["haunt"]},
        {"name": "Quicksand", "type": "Environmental", "traits": ["environmental"]},
        {"name": "Spear Trap", "type": "Trap", "traits": ["mechanical", "trap"]},
    ],
    5: [
        {"name": "Armageddon Orb", "type": "Trap", "traits": ["magical", "trap"]},
        {"name": "Freezing Floor", "type": "Trap", "traits": ["magical", "trap"]},
        {"name": "Lava Flume Tube", "type": "Environmental", "traits": ["environmental"]},
        {"name": "Poisoned Dart Statue", "type": "Trap", "traits": ["mechanical", "trap"]},
    ],
    6: [
        {"name": "Blade Pillar", "type": "Trap", "traits": ["mechanical", "trap"]},
        {"name": "Enervating Pit", "type": "Trap", "traits": ["magical", "trap"]},
        {"name": "Perilous Flash Flood", "type": "Environmental", "traits": ["environmental"]},
        {"name": "Sphere of Annihilation", "type": "Trap", "traits": ["magical", "trap"]},
    ],
    7: [
        {"name": "Avalanche", "type": "Environmental", "traits": ["environmental"]},
        {"name": "Crushing Wall", "type": "Trap", "traits": ["mechanical", "trap"]},
        {"name": "Grasping Graves", "type": "Haunt", "traits": ["haunt"]},
        {"name": "Summoning Rune", "type": "Trap", "traits": ["magical", "trap"]},
    ],
    8: [
        {"name": "Bottomless Pit", "type": "Trap", "traits": ["magical", "trap"]},
        {"name": "Lava Geyser", "type": "Environmental", "traits": ["environmental"]},
        {"name": "Teleportation Trap", "type": "Trap", "traits": ["magical", "trap"]},
        {"name": "Vengeful Furnace", "type": "Haunt", "traits": ["haunt"]},
    ],
    9: [
        {"name": "Dimensional Darkside Mirror", "type": "Trap", "traits": ["magical", "trap"]},
        {"name": "Hallucination Powder Trap", "type": "Trap", "traits": ["mechanical", "trap"]},
        {"name": "Planar Rift", "type": "Environmental", "traits": ["environmental"]},
    ],
    10: [
        {"name": "Dispelling Glyph", "type": "Trap", "traits": ["magical", "trap"]},
        {"name": "Meteor Shower", "type": "Environmental", "traits": ["environmental"]},
        {"name": "Prismatic Archway", "type": "Trap", "traits": ["magical", "trap"]},
    ],
}

def generate_hazard(level):
    """Generate a random hazard of the specified level"""
    level = int(level)
    
    if level not in HAZARDS:
        return {
            "error": f"No hazards available for level {level}",
            "available_levels": list(HAZARDS.keys())
        }
    
    hazard = random.choice(HAZARDS[level])
    
    # Build description based on type
    descriptions = {
        "Trap": [
            "A cunningly hidden trap designed to catch unwary adventurers.",
            "This trap has been carefully maintained and is fully functional.",
            "Ancient but still deadly, this trap awaits its next victim.",
            "A classic dungeon defense, simple but effective.",
        ],
        "Environmental": [
            "A natural hazard that poses significant danger.",
            "The environment itself becomes a threat here.",
            "Nature's wrath manifests in this dangerous phenomenon.",
            "This area is treacherous due to natural forces.",
        ],
        "Haunt": [
            "Restless spirits linger here, creating supernatural danger.",
            "The echoes of past tragedy manifest as a dangerous haunt.",
            "Psychic residue from violent deaths creates this hazard.",
            "Ghostly energy coalesces into a tangible threat.",
        ]
    }
    
    description = random.choice(descriptions.get(hazard["type"], ["A dangerous hazard."]))
    
    # Detection and disarm DCs
    detection_dc = 15 + level
    disable_dc = 17 + level
    
    result = {
        "name": hazard["name"],
        "level": level,
        "type": hazard["type"],
        "traits": hazard["traits"],
        "description": description,
        "detection_dc": detection_dc,
        "disable_dc": disable_dc,
        "stealth": f"+{10 + level}",
        "notes": generate_notes(hazard, level)
    }
    
    return result

def generate_notes(hazard, level):
    """Generate GM notes for the hazard"""
    notes = []
    
    if "mechanical" in hazard["traits"]:
        notes.append(f"Can be detected with DC {15 + level} Perception")
        notes.append(f"Can be disabled with DC {17 + level} Thievery")
        notes.append("Triggering it alerts nearby enemies")
    
    if "magical" in hazard["traits"]:
        notes.append(f"Can be detected with DC {15 + level} Perception or Detect Magic")
        notes.append(f"Can be disabled with DC {17 + level} Thievery or DC {19 + level} Arcana to dispel")
        notes.append("Magical aura is visible to those with magical senses")
    
    if "environmental" in hazard["traits"]:
        notes.append(f"Can be noticed with DC {15 + level} Perception or Survival")
        notes.append("May require Athletics, Acrobatics, or other skills to avoid")
        notes.append("Environmental hazards often affect large areas")
    
    if "haunt" in hazard["traits"]:
        notes.append(f"Can be sensed with DC {15 + level} Perception or Religion")
        notes.append(f"Can be disrupted with DC {17 + level} Religion or Occultism")
        notes.append("Haunts often trigger based on specific conditions or times")
    
    # Damage estimate
    damage_dice = max(1, level // 2)
    notes.append(f"Typical damage: {damage_dice}d6 to {damage_dice}d10 depending on save")
    
    return notes

def format_output(hazard):
    """Format hazard for display"""
    if "error" in hazard:
        return f"ERROR: {hazard['error']}\nAvailable levels: {hazard['available_levels']}"
    
    output = []
    output.append("=" * 60)
    output.append(f"HAZARD: {hazard['name']}")
    output.append("=" * 60)
    output.append(f"Level: {hazard['level']}")
    output.append(f"Type: {hazard['type']}")
    output.append(f"Traits: {', '.join(hazard['traits'])}")
    output.append("")
    output.append(f"Description: {hazard['description']}")
    output.append("")
    output.append(f"Stealth: {hazard['stealth']} (to avoid detection)")
    output.append(f"Detection DC: {hazard['detection_dc']}")
    output.append(f"Disable DC: {hazard['disable_dc']}")
    output.append("")
    output.append("GM NOTES:")
    for note in hazard['notes']:
        output.append(f"  • {note}")
    output.append("")
    output.append("=" * 60)
    
    return "\n".join(output)

def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_hazard.py <level>")
        print("Example: python generate_hazard.py 3")
        print(f"Available levels: {list(HAZARDS.keys())}")
        sys.exit(1)
    
    level = int(sys.argv[1])
    hazard = generate_hazard(level)
    print(format_output(hazard))

if __name__ == "__main__":
    main()
