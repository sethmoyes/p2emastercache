#!/usr/bin/env python3
"""
Generate detailed NPC lore using d20pfsrd background generator tables
Creates cohesive, interesting NPCs for LORE ONLY encounters
"""
import random
import json

# Race tables
RACES = ['Human', 'Elf', 'Dwarf', 'Halfling', 'Gnome', 'Half-Elf', 'Half-Orc']

# Human Homeland
HUMAN_HOMELAND = [
    ("Town or Village", "Militia Veteran"),
    ("City or Metropolis", "Civilized/Vagabond Child"),
    ("Frontier", "Frontier-Forged"),
]

# Circumstance of Birth (simplified for NPCs)
BIRTH_CIRCUMSTANCES = [
    ("Lower-Class Birth", "grew up among peasants, working the land"),
    ("Middle-Class Birth", "born to merchants or artisans"),
    ("Noble Birth", "born to privilege among the nobility"),
    ("Adopted", "raised by another family"),
    ("Orphaned", "lost parents at a young age"),
]

# Parents' Profession
PARENTS_PROFESSION = [
    "Serfs/Peasants", "Entertainers", "Soldiers", "Sailors", "Thieves",
    "Yeomen", "Tradespeople", "Artisans", "Merchants", "Clergy"
]

# Major Childhood Events
CHILDHOOD_EVENTS = [
    ("Academy Training", "attended a private academy"),
    ("Betrayal", "was betrayed by a trusted friend or family member"),
    ("Bullied", "was a victim of bullying in youth"),
    ("Death in the Family", "lost someone close"),
    ("Fell in with a Bad Crowd", "ran with a rough crowd"),
    ("First Kill", "took a life at a young age"),
    ("Imprisoned", "was imprisoned for a crime"),
    ("Kidnapped", "was kidnapped and later escaped"),
    ("Mentorship", "was mentored by a skilled teacher"),
    ("Ordinary Childhood", "had an unremarkable childhood"),
    ("Raiders", "survived a raid on their settlement"),
    ("The War", "grew up during wartime"),
]

# Professions/Classes (simplified)
NPC_PROFESSIONS = [
    "Merchant", "Guard", "Sailor", "Farmer", "Craftsperson",
    "Entertainer", "Scholar", "Priest", "Soldier", "Thief",
    "Healer", "Hunter", "Innkeeper", "Messenger", "Scribe"
]

# Influential Associates
INFLUENTIAL_ASSOCIATES = [
    ("The Mentor", "had a wise teacher"),
    ("The Lover", "had a significant romantic relationship"),
    ("The Relative", "was close to a family member"),
    ("The Criminal", "knew someone in the criminal underworld"),
    ("The Wanderer", "befriended a traveling merchant or minstrel"),
    ("The Champion", "knew an athletic or competitive person"),
    ("The Mystic", "was influenced by a holy person"),
]

# Conflicts (simplified for NPCs)
CONFLICTS = [
    ("Minor Failure", "failed someone who depended on them"),
    ("Told a Lie", "lied to further their goals"),
    ("Broke a Promise", "failed to keep an important oath"),
    ("Humiliation", "publicly embarrassed someone"),
    ("Negligence", "caused suffering through inaction"),
    ("Betrayal", "betrayed someone's trust"),
    ("Major Theft", "stole something valuable"),
]

# Motivations
MOTIVATIONS = [
    "Justice", "Love", "Pressured", "Religion", "Family",
    "Money", "Jealousy", "Hatred"
]

# Personality Traits
PERSONALITY_TRAITS = [
    "cautious", "friendly", "suspicious", "cheerful", "grumpy",
    "nervous", "confident", "humble", "proud", "curious",
    "secretive", "talkative", "quiet", "brave", "cowardly"
]

# Current Situations
CURRENT_SITUATIONS = [
    "traveling to Otari for work",
    "fleeing from trouble",
    "searching for a lost relative",
    "on a pilgrimage",
    "delivering an important message",
    "seeking adventure",
    "running from the law",
    "looking for employment",
    "visiting family in Otari",
    "escorting goods to market"
]

def generate_npc():
    """Generate a complete NPC with cohesive background"""
    npc = {}
    
    # Basic info
    npc['race'] = random.choice(RACES)
    npc['gender'] = random.choice(['Male', 'Female'])
    npc['profession'] = random.choice(NPC_PROFESSIONS)
    
    # Homeland
    homeland = random.choice(HUMAN_HOMELAND)
    npc['homeland'] = homeland[0]
    
    # Birth
    birth = random.choice(BIRTH_CIRCUMSTANCES)
    npc['birth_circumstance'] = birth[0]
    npc['birth_detail'] = birth[1]
    
    # Parents
    npc['parents_profession'] = random.choice(PARENTS_PROFESSION)
    
    # Childhood event
    event = random.choice(CHILDHOOD_EVENTS)
    npc['childhood_event'] = event[0]
    npc['childhood_detail'] = event[1]
    
    # Influential associate
    associate = random.choice(INFLUENTIAL_ASSOCIATES)
    npc['influential_associate'] = associate[0]
    npc['associate_detail'] = associate[1]
    
    # Conflict
    conflict = random.choice(CONFLICTS)
    npc['conflict'] = conflict[0]
    npc['conflict_detail'] = conflict[1]
    npc['conflict_motivation'] = random.choice(MOTIVATIONS)
    
    # Personality
    npc['personality'] = random.choice(PERSONALITY_TRAITS)
    
    # Current situation
    npc['current_situation'] = random.choice(CURRENT_SITUATIONS)
    
    return npc

def format_npc_narrative(npc):
    """Format NPC data into a cohesive narrative"""
    narrative = []
    
    # Opening
    narrative.append(f"This {npc['personality']} {npc['race'].lower()} {npc['profession'].lower()} ")
    
    # Birth and upbringing
    if npc['birth_circumstance'] == "Orphaned":
        narrative.append(f"lost their parents at a young age. ")
    elif npc['birth_circumstance'] == "Noble Birth":
        narrative.append(f"was born to privilege among the nobility. ")
    else:
        narrative.append(f"{npc['birth_detail']}. ")
    
    # Parents
    if npc['birth_circumstance'] != "Orphaned":
        narrative.append(f"Their parents were {npc['parents_profession'].lower()}. ")
    
    # Childhood
    narrative.append(f"In their youth, they {npc['childhood_detail']}. ")
    
    # Associate
    narrative.append(f"They {npc['associate_detail']} who greatly influenced them. ")
    
    # Conflict
    narrative.append(f"At one point, they {npc['conflict_detail']}, motivated by {npc['conflict_motivation'].lower()}. ")
    
    # Current
    narrative.append(f"Now they are {npc['current_situation']}.")
    
    return ''.join(narrative)

def generate_npc_encounter_template(npc):
    """Generate a full encounter template for the NPC"""
    narrative = format_npc_narrative(npc)
    
    # Generate name
    first_names = {
        'Human': ['Aldric', 'Brenna', 'Cedric', 'Delia', 'Edric', 'Fiona', 'Gareth', 'Helena'],
        'Elf': ['Aerendyl', 'Caelynn', 'Erevan', 'Faelyn', 'Galaeron', 'Ilyana'],
        'Dwarf': ['Baern', 'Dagnal', 'Eberk', 'Kathra', 'Rurik', 'Torbera'],
        'Halfling': ['Alton', 'Cora', 'Eldon', 'Lidda', 'Merric', 'Nedda'],
        'Gnome': ['Boddynock', 'Breena', 'Dimble', 'Nissa', 'Seebo', 'Warryn'],
        'Half-Elf': ['Aramil', 'Bree', 'Faral', 'Immeral', 'Shandri', 'Thamior'],
        'Half-Orc': ['Dench', 'Feng', 'Gell', 'Holg', 'Imsh', 'Keth', 'Ront', 'Shump']
    }
    
    name = random.choice(first_names.get(npc['race'], first_names['Human']))
    
    # Setup and read-aloud
    setups = [
        "A figure approaches on the road ahead.",
        "You hear someone calling out for help.",
        "A traveler waves to you from the roadside.",
        "Someone is resting by the path.",
        "A person emerges from the mist.",
    ]
    
    template = {
        'name': f"{name} the {npc['profession']}",
        'race': npc['race'],
        'profession': npc['profession'],
        'personality': npc['personality'],
        'setup': random.choice(setups),
        'readaloud': f'A {npc['personality']} {npc['race'].lower()} {npc['profession'].lower()} greets you. "{random.choice(["Well met, travelers!", "Greetings, friends!", "Hail, adventurers!", "Good day to you!"])}"',
        'description': narrative,
        'lore_keywords': ['humanoid', npc['race'], 'NPC', 'social']
    }
    
    return template

def test_npc_generation(count=100):
    """Test NPC generation and check for coherence"""
    print(f"Testing NPC Generation - Creating {count} NPCs")
    print("=" * 80)
    
    npcs = []
    issues = []
    
    for i in range(count):
        try:
            npc = generate_npc()
            template = generate_npc_encounter_template(npc)
            narrative = template['description']
            
            # Coherence checks
            if len(narrative) < 50:
                issues.append(f"NPC {i+1}: Narrative too short")
            
            if "None" in narrative or "null" in narrative.lower():
                issues.append(f"NPC {i+1}: Contains None/null values")
            
            # Check for contradictions
            if "Orphaned" in npc['birth_circumstance'] and "parents were" in narrative:
                issues.append(f"NPC {i+1}: Orphan has parents mentioned")
            
            npcs.append(template)
            
            # Print first 10 for review
            if i < 10:
                print(f"\nNPC #{i+1}: {template['name']}")
                print(f"Race: {template['race']}, Profession: {template['profession']}")
                print(f"Personality: {template['personality']}")
                print(f"Background: {narrative}")
                print("-" * 80)
        
        except Exception as e:
            issues.append(f"NPC {i+1}: Exception - {str(e)}")
    
    # Summary
    print(f"\n{'=' * 80}")
    print(f"GENERATION TEST COMPLETE")
    print(f"{'=' * 80}")
    print(f"Total NPCs Generated: {len(npcs)}")
    print(f"Success Rate: {len(npcs)/count*100:.1f}%")
    print(f"Issues Found: {len(issues)}")
    
    if issues:
        print(f"\nISSUES DETECTED:")
        for issue in issues[:10]:  # Show first 10 issues
            print(f"  - {issue}")
    else:
        print(f"\n✓ ALL NPCS GENERATED SUCCESSFULLY WITH NO ISSUES!")
    
    # Save sample NPCs
    with open('test_npcs.json', 'w', encoding='utf-8') as f:
        json.dump(npcs[:20], f, indent=2, ensure_ascii=False)
    print(f"\nSaved 20 sample NPCs to test_npcs.json for review")
    
    return len(issues) == 0

if __name__ == "__main__":
    success = test_npc_generation(100)
    
    if success:
        print(f"\n{'=' * 80}")
        print("✓ NPC GENERATOR IS READY FOR PRODUCTION USE")
        print("=" * 80)
    else:
        print(f"\n{'=' * 80}")
        print("✗ ISSUES DETECTED - NEEDS FIXES")
        print("=" * 80)
