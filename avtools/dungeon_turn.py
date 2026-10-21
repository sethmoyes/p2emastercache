#!/usr/bin/env python3
"""
Dungeon turn encounters for Gauntlight Keep.

Probability distribution (5d20):
- Extreme (5-15, 90-100): Always COMBAT (very rare)
- Non-extreme: 50% NO EVENT, then:
  - Sum <= 44: COMBAT or ACTIVE_THREAT (danger)
  - Sum 45-62: OPPORTUNITY, COMPLICATION, or DILEMMA (non-combat)
  - Sum >= 63: ACTIVE_THREAT or COMBAT (danger)
"""

import random

from avtools import data
from avtools.ecology import build_ecology_combat_event, build_ecology_threat_event, ECOLOGY_THREAT_CHANCE
from avtools.events import select_template


def floor_levels():
    """{floor: {'name', 'theme'}} for floors 1-10, from etc/floor_ecology.json."""
    return {n: {'name': f['name'], 'theme': f['ecology']} for n, f in data.floor_ecology().items()}


def get_category_from_sum(total, is_extreme=False, allow_no_event=True):
    """
    Determine event category based on 5d20 sum.
    
    New distribution with "no event" mechanic:
    - Extreme rolls (5-15, 90-100): Always COMBAT
    - Non-extreme rolls: 50% chance of NO EVENT
    - 5-44: COMBAT/ACTIVE_THREAT (danger)
    - 45-62: OPPORTUNITIES/COMPLICATIONS/DILEMMAS (middle range)
    - 63-100: ACTIVE_THREAT/COMBAT (danger)

    allow_no_event=False skips the no-event coin flip (used by the test generator).
    """
    # Extreme rolls always generate combat
    if is_extreme:
        return "COMBAT"
    
    # Non-extreme rolls: 50% chance of no event
    if allow_no_event and random.random() < 0.5:
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



def generate_opportunity_event(floor_num, floor_data, party_level):
    """An OPPORTUNITY event from this floor's templates"""
    template = select_template(data.events()['OPPORTUNITY'], floor=floor_num)
    
    # Customize for floor
    event = template.copy()
    event['floor'] = floor_num
    event['floor_name'] = floor_data['name']
    
    return event

def generate_complication_event(floor_num, floor_data, party_level):
    """A COMPLICATION event from this floor's templates"""
    template = select_template(data.events()['COMPLICATION'], floor=floor_num)
    
    event = template.copy()
    event['floor'] = floor_num
    event['floor_name'] = floor_data['name']
    
    return event

def generate_dilemma_event(floor_num, floor_data, party_level):
    """A DILEMMA event from this floor's templates"""
    template = select_template(data.events()['DILEMMA'], floor=floor_num)
    
    event = template.copy()
    event['floor'] = floor_num
    event['floor_name'] = floor_data['name']
    
    # Add floor-specific context
    if floor_num <= 3:
        event['context'] = "You're still in the upper levels. Escape is possible if things go wrong."
    elif floor_num <= 6:
        event['context'] = "You're deep enough that retreat is costly. Choose wisely."
    else:
        event['context'] = "You're in the deep dungeon. Every choice matters. No easy escape."
    
    return event


def generate_active_threat_event(floor_num, floor_data, party_level):
    """An ACTIVE_THREAT: usually a floor hazard or event, otherwise a template"""
    # Most threats come from the floor's own hazards and residents
    if random.random() < ECOLOGY_THREAT_CHANCE:
        event = build_ecology_threat_event(floor_num, floor_data)
        if event:
            return event

    template = select_template(data.events()['ACTIVE_THREAT'], floor=floor_num)
    
    event = template.copy()
    event['floor'] = floor_num
    event['floor_name'] = floor_data['name']
    
    # Add urgency
    event['urgency'] = "IMMEDIATE ACTION REQUIRED! No time to discuss!"
    
    return event

def no_residents_event(floor_num, dice_sum):
    """What a combat roll returns on a floor with no ecology entries."""
    return {
        'title': 'No residents listed for this floor',
        'description': 'Nothing in etc/floor_ecology.json lives here yet. Pick something from the floor doc.',
        'gm_notes': f'Add creature entries for floor {floor_num} to etc/floor_ecology.json.',
        'creatures': [],
        'dice_sum': dice_sum,
    }


def generate_extreme_combat_event(floor_num, floor_data, party_level, creatures, dice_sum, party_size=4):
    """
    An EXTREME combat encounter for extreme rolls (5-15, 90-100): the floor's
    ecology at a Severe budget (Extreme on a 5 or 100).
    """
    threat = 'Extreme' if dice_sum in (5, 100) else 'Severe'
    return (build_ecology_combat_event(floor_num, floor_data, party_level, creatures, dice_sum,
                                       threat=threat, party_size=party_size, extreme=True)
            or no_residents_event(floor_num, dice_sum))


def generate_combat_event(floor_num, floor_data, party_level, creatures, dice_sum=50, party_size=4):
    """A COMBAT encounter from the floor's ecology at a Low budget."""
    return (build_ecology_combat_event(floor_num, floor_data, party_level, creatures, dice_sum,
                                       threat='Low', party_size=party_size)
            or no_residents_event(floor_num, dice_sum))


def generate_event_for_sum(dice_sum, floor_num, floor_data, party_level, creatures, party_size=4,
                           allow_no_event=True):
    """Generate appropriate event based on dice sum"""
    # Check if this is an extreme roll
    is_extreme = dice_sum <= 15 or dice_sum >= 90
    
    # Get category (with extreme flag and no-event mechanic)
    category = get_category_from_sum(dice_sum, is_extreme, allow_no_event)
    
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
        event = generate_extreme_combat_event(floor_num, floor_data, party_level, creatures, dice_sum, party_size)
    elif category == "OPPORTUNITY":
        event = generate_opportunity_event(floor_num, floor_data, party_level)
    elif category == "COMPLICATION":
        event = generate_complication_event(floor_num, floor_data, party_level)
    elif category == "DILEMMA":
        event = generate_dilemma_event(floor_num, floor_data, party_level)
    elif category == "ACTIVE_THREAT":
        event = generate_active_threat_event(floor_num, floor_data, party_level)
    else:  # COMBAT (non-extreme)
        event = generate_combat_event(floor_num, floor_data, party_level, creatures, dice_sum, party_size)
    
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
    
    # Category-specific formatting. Templates don't all carry every field, so
    # missing ones are skipped rather than crashing the whole table.
    def add_fields(fields):
        for key, label in fields:
            value = event.get(key)
            if value:
                if isinstance(value, list):
                    value = ', '.join(value)
                lines.append(f"**{label}:** {value}")

    if event['category'] == "OPPORTUNITY":
        add_fields([('challenge', 'Challenge'), ('success', 'Success'), ('failure', 'Failure'),
                    ('skills', 'Skills'), ('time_cost', 'Time Cost'), ('reward', 'Reward'),
                    ('flavor', 'Floor Flavor')])

    elif event['category'] == "COMPLICATION":
        add_fields([('challenge', 'Challenge'), ('success', 'Success'), ('failure', 'Failure'),
                    ('skills', 'Skills'), ('time_cost', 'Time Cost'), ('consequence', 'Consequence'),
                    ('flavor', 'Floor Flavor')])

    elif event['category'] == "DILEMMA":
        add_fields([('choice_a', 'Choice A'), ('choice_b', 'Choice B'), ('choice_c', 'Choice C'),
                    ('skills', 'Skills'), ('time_cost', 'Time Cost'), ('consequence', 'Consequence'),
                    ('context', 'Context')])

    elif event['category'] == "ACTIVE_THREAT":
        lines.append(f"**{event.get('urgency', 'IMMEDIATE ACTION REQUIRED!')}**")
        lines.append("")
        add_fields([('immediate_action', 'Immediate Action'), ('success', 'Success'), ('failure', 'Failure'),
                    ('skills', 'Skills'), ('threat_level', 'Threat Level')])

    elif event['category'] == "NO_EVENT":
        pass

    else:  # COMBAT
        lines.append(f"**Ecology:** {event['ecology']}")
        if 'creature_summary' in event:
            lines.append(f"**Creatures:** {event['creature_summary']}")
            refs = event.get('creature_reference', {})
            links = [f"[{name}]({ref['aon_url']})" for name, ref in refs.items() if ref.get('aon_url')]
            if links:
                lines.append(f"**Stat Blocks:** {', '.join(links)}")
        else:
            lines.append(f"**Creatures:** {event['num_creatures']}x {', '.join(event['creatures'])} (Level {event['creature_level']})")
        lines.append(f"**Difficulty:** {event['difficulty']}")
        lines.append(f"**Tactical Option:** {event['tactical_option']}")
        lines.append(f"**Avoidable:** {'Yes' if event['avoidable'] else 'No'}")
        lines.append(f"**Surprise Available:** {'Yes' if event['surprise_available'] else 'No'}")
        if 'lore_hook' in event:
            lines.append(f"**Lore Hook:** {event['lore_hook']}")
        else:
            lines.append(f"**Floor Ecology:** {event['floor_ecology']}")
    
    # GM notes for all events
    if 'gm_notes' in event:
        lines.append("")
        lines.append(f"**GM Notes:** {event['gm_notes']}")
    
    lines.append("")
    lines.append("---")
    lines.append("")
    
    return "\n".join(lines)


def generate_all_encounters(party_level, max_floor, output_file, party_size=4):
    """Generate comprehensive encounter table for all floors"""
    print(f"=" * 80)
    print(f"DUNGEON TURN GENERATOR V2 - THE FUN VERSION")
    print(f"=" * 80)
    print(f"Party Level: {party_level}")
    print(f"Floors: 1-{max_floor}")
    print(f"Total Events: {96 * max_floor} (96 sums per floor)")
    print(f"")
    print(f"New Probability Distribution:")
    print(f"  Extreme (5-15, 90-100): Always COMBAT")
    print(f"  Non-extreme: 50% NO EVENT, then:")
    print(f"    Sum <= 44:  COMBAT or ACTIVE_THREAT (danger)")
    print(f"    Sum 45-62: OPPORTUNITY, COMPLICATION, or DILEMMA (non-combat)")
    print(f"    Sum >= 63:  ACTIVE_THREAT or COMBAT (danger)")
    print(f"")
    print(f"Combat potential: ~37% (ACTIVE THREATS can become combat)")
    print(f"=" * 80)
    print(f"")
    
    # Load data
    print("Loading data files...")
    levels_data = floor_levels()
    creatures = data.creatures()
    print(f"  Loaded {len(levels_data)} floor definitions")
    print(f"  Loaded {len(creatures)} creatures")
    print("")
    
    # Start building output
    lines = []
    lines.append("# Dungeon Turn Encounters V2 - Gauntlight Keep")
    lines.append("")
    lines.append(f"**Party Level:** {party_level} ({party_size} PCs)")
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
    lines.append("- **Extreme (5-15, 90-100):** Always COMBAT (very rare)")
    lines.append("- **Non-extreme:** 50% chance of NO EVENT, then:")
    lines.append("  - **Sum <= 44:** COMBAT or ACTIVE_THREAT (danger)")
    lines.append("  - **Sum 45-62:** OPPORTUNITY, COMPLICATION, or DILEMMA (non-combat)")
    lines.append("  - **Sum >= 63:** ACTIVE_THREAT or COMBAT (danger)")
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
            event = generate_event_for_sum(dice_sum, floor, level_data, party_level, creatures, party_size)
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

    parser = argparse.ArgumentParser(description='Generate Dungeon Turn Encounters V2')
    parser.add_argument('--level', type=int, default=4, help='Party level (default: 4)')
    parser.add_argument('--floors', type=int, default=3, help='Number of floors to generate (1 to X)')
    parser.add_argument('--party-size', type=int, default=4, help='Number of PCs, for encounter budgets (default: 4)')
    parser.add_argument('--output', type=str, default='dungeon_turn_encounters_v2.md', help='Output file path')
    args = parser.parse_args()

    generate_all_encounters(
        party_level=args.level,
        max_floor=args.floors,
        output_file=args.output,
        party_size=args.party_size
    )

if __name__ == "__main__":
    main()
