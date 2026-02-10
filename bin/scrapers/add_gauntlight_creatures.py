#!/usr/bin/env python3
"""
Add complete stats for Gauntlight Keep creatures
Manually curated from Archives of Nethys for accuracy
"""

import json
from pathlib import Path

# Complete creature data for Gauntlight Keep encounters
GAUNTLIGHT_CREATURES = {
    "Mitflit": {
        "attacks": [
            "Melee dart +5 (agile, finesse), Damage 1d4 piercing",
            "Ranged dart +5 (agile, thrown 20 feet), Damage 1d4 piercing"
        ],
        "abilities": [
            "Self-Loathing (emotion, mental) - A mitflit's self-loathing makes it easy to influence",
            "Vengeful Anger (emotion, mental) - As long as it isn't frightened, a mitflit gains a +2 status bonus to damage rolls against a creature that has previously damaged or tormented it"
        ],
        "skills": {
            "Acrobatics": "+5",
            "Crafting": "+3",
            "Diplomacy": "+0",
            "Nature": "+3",
            "Stealth": "+5",
            "Thievery": "+5"
        },
        "languages": ["Undercommon"],
        "immunities": [],
        "resistances": [],
        "weaknesses": []
    },
    
    "Morlock": {
        "attacks": [
            "Melee club +8 (agile), Damage 1d6+3 bludgeoning",
            "Ranged sling +6 (propulsive, range increment 50 feet), Damage 1d4+1 bludgeoning"
        ],
        "abilities": [
            "Light Blindness",
            "Sneak Attack - The morlock deals an extra 1d6 precision damage to flat-footed creatures",
            "Swarming Stance - A morlock can share the same space as another morlock"
        ],
        "skills": {
            "Acrobatics": "+6",
            "Athletics": "+8",
            "Crafting": "+4",
            "Stealth": "+8"
        },
        "languages": ["Undercommon"],
        "immunities": [],
        "resistances": [],
        "weaknesses": []
    },
    
    "Ghoul": {
        "attacks": [
            "Melee jaws +7 (finesse), Damage 1d6+1 piercing plus ghoul fever and paralysis",
            "Melee claw +7 (agile, finesse), Damage 1d4+1 slashing plus paralysis"
        ],
        "abilities": [
            "Consume Flesh (manipulate) - Requirements The ghoul is adjacent to the corpse of a creature that died within the last hour",
            "Ghoul Fever (disease) - Saving Throw DC 15 Fortitude",
            "Paralysis (incapacitation, occult, necromancy) - Any living, non-elf creature hit by a ghoul's attack must succeed at a DC 15 Fortitude save or become paralyzed"
        ],
        "skills": {
            "Acrobatics": "+7",
            "Athletics": "+5",
            "Stealth": "+7",
            "Survival": "+5"
        },
        "languages": ["Common", "Necril"],
        "immunities": ["death effects", "disease", "paralyzed", "poison", "unconscious"],
        "resistances": [],
        "weaknesses": []
    },
    
    "Skeleton Guard": {
        "attacks": [
            "Melee scimitar +7 (forceful, sweep), Damage 1d6+3 slashing",
            "Melee claw +7 (agile), Damage 1d4+3 slashing"
        ],
        "abilities": [
            "Shield Block"
        ],
        "skills": {
            "Acrobatics": "+5",
            "Athletics": "+7"
        },
        "languages": [],
        "immunities": ["death effects", "disease", "mental", "paralyzed", "poison", "unconscious"],
        "resistances": ["cold 5", "electricity 5", "fire 5", "piercing 5", "slashing 5"],
        "weaknesses": ["bludgeoning 5"]
    },
    
    "Zombie Shambler": {
        "attacks": [
            "Melee fist +7, Damage 1d6+3 bludgeoning plus Grab"
        ],
        "abilities": [
            "Grab",
            "Slow - A zombie is permanently slowed 1 and can't use reactions"
        ],
        "skills": {},
        "languages": [],
        "immunities": ["death effects", "disease", "mental", "paralyzed", "poison", "unconscious"],
        "resistances": [],
        "weaknesses": ["slashing 5"]
    },
    
    "Giant Monitor Lizard": {
        "attacks": [
            "Melee jaws +9, Damage 1d10+4 piercing plus Grab",
            "Melee tail +9 (agile), Damage 1d8+4 bludgeoning"
        ],
        "abilities": [
            "Grab",
            "Lurching Charge (two actions) - The giant monitor lizard Strides twice and then makes a Strike"
        ],
        "skills": {
            "Acrobatics": "+5",
            "Athletics": "+9",
            "Stealth": "+7"
        },
        "languages": [],
        "immunities": [],
        "resistances": [],
        "weaknesses": []
    },
    
    "Wight": {
        "attacks": [
            "Melee claw +10 (finesse), Damage 1d6+4 slashing plus drain life"
        ],
        "abilities": [
            "Drain Life (divine, necromancy) - When the wight damages a living creature with its claw Strike, the wight gains 3 temporary Hit Points and the creature must succeed at a DC 17 Fortitude save or become drained 1"
        ],
        "skills": {
            "Athletics": "+10",
            "Intimidation": "+9",
            "Stealth": "+9"
        },
        "languages": ["Common", "Necril"],
        "immunities": ["death effects", "disease", "paralyzed", "poison", "unconscious"],
        "resistances": [],
        "weaknesses": []
    },
    
    "Shadow": {
        "attacks": [
            "Melee shadow hand +10 (finesse, magical), Damage 1d6+2 negative plus 1d6 persistent negative"
        ],
        "abilities": [
            "Light Vulnerability - An object shedding magical light (such as from the light spell) is treated as a magical light source by the shadow",
            "Shadow Spawn (divine, necromancy) - When a creature's shadow is pulled free by Steal Shadow, it becomes a shadow spawn under the command of the shadow that created it"
        ],
        "skills": {
            "Acrobatics": "+10",
            "Stealth": "+12"
        },
        "languages": ["Necril"],
        "immunities": ["death effects", "disease", "paralyzed", "poison", "precision", "unconscious"],
        "resistances": ["all damage 5 (except force, ghost touch, or positive; double resistance vs. non-magical)"],
        "weaknesses": []
    }
}

def enhance_creatures():
    """Add complete data to creatures in database"""
    
    print("=" * 80)
    print("GAUNTLIGHT CREATURES ENHANCEMENT")
    print("=" * 80)
    
    # Load existing database
    creatures_file = Path("etc/creatures.json")
    if not creatures_file.exists():
        print("❌ creatures.json not found!")
        return
    
    with open(creatures_file) as f:
        creatures = json.load(f)
    
    print(f"\n📊 Loaded {len(creatures)} creatures from database")
    
    # Backup original
    backup_file = Path("etc/creatures_backup.json")
    if not backup_file.exists():
        with open(backup_file, 'w') as f:
            json.dump(creatures, f, indent=2)
        print(f"💾 Created backup: {backup_file}")
    
    # Enhance creatures
    enhanced_count = 0
    
    for creature in creatures:
        name = creature.get('name', '')
        
        if name in GAUNTLIGHT_CREATURES:
            print(f"\n✨ Enhancing: {name}")
            
            enhancement = GAUNTLIGHT_CREATURES[name]
            
            # Add all the new fields
            creature['attacks'] = enhancement['attacks']
            creature['abilities'] = enhancement['abilities']
            creature['skills'] = enhancement['skills']
            creature['languages'] = enhancement['languages']
            creature['immunities'] = enhancement['immunities']
            creature['resistances'] = enhancement['resistances']
            creature['weaknesses'] = enhancement['weaknesses']
            
            print(f"  ✓ Added {len(enhancement['attacks'])} attacks")
            print(f"  ✓ Added {len(enhancement['abilities'])} abilities")
            
            enhanced_count += 1
    
    # Save enhanced database
    with open(creatures_file, 'w') as f:
        json.dump(creatures, f, indent=2)
    
    print(f"\n✅ Enhanced {enhanced_count} creatures")
    print(f"💾 Saved to {creatures_file}")
    print(f"\n📋 Enhanced creatures:")
    for name in GAUNTLIGHT_CREATURES.keys():
        print(f"   - {name}")

if __name__ == "__main__":
    enhance_creatures()
