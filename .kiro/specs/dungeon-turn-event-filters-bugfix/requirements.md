# Generate 50 NPC Detail Events Per Floor for Gauntlight Keep

## Introduction

The dungeon turn event generation system needs richer NPC details for encounters with intelligent beings. Currently, events reference generic creature types, but they lack the narrative flavor that makes each encounter feel unique and connected to the specific floor's lore. This feature will generate 50 unique NPC detail events for each of the 10 floors of Gauntlight Keep, drawing from floor-specific themes, factions, and creature types.

Each time an encounter is generated that involves anything with intelligence - combat encounters, patrols, friendly ghosts, NPCs, etc. - they should have humanizing details that make them feel alive: distinctive scars, notes for lovers, pictures of children, personal quirks, or other small touches that add personality and depth.

This is an invisible enhancement to the existing dungeon turn event generation system - no separate UI or generation step required.

## Glossary

- **NPC_Detail_Event**: A narrative description that adds personality, backstory, or distinctive features to an intelligent being
- **Floor_Theme**: The thematic identity of a dungeon floor (e.g., "Mitflit infestation", "Ghoul library", "Devil prison")
- **Creature_Pool**: The set of creatures appropriate for a specific floor based on lore and level
- **Event_Generator**: The system that creates dungeon turn encounters (generate_dungeon_turn_v2.py)
- **Gauntlight_Keep**: The 10-level megadungeon from Pathfinder 2e Abomination Vaults
- **Floor_Data**: Information about each floor from gauntlight_keep_levels.md
- **Creature_Database**: The creatures.json file containing creature statistics
- **Intelligent_Being**: Any creature, NPC, or entity with intelligence that can have personality or possessions

## Requirements

### Requirement 1: Generate 50 NPC Details Per Floor

**User Story:** As a GM, I want 50 unique NPC detail events for each floor, so that every encounter with intelligent beings feels fresh and connected to the dungeon's story.

#### Acceptance Criteria

1. THE Event_Generator SHALL generate exactly 50 NPC detail events for each floor (1-10)
2. WHEN generating NPC details, THE Event_Generator SHALL use floor-specific themes from gauntlight_keep_levels.md
3. WHEN generating NPC details, THE Event_Generator SHALL reference appropriate creatures from creatures.json
4. THE Event_Generator SHALL ensure each NPC detail is unique within its floor
5. THE Event_Generator SHALL store generated NPC details in a structured format
6. THE Event_Generator SHALL generate a total of 500 NPC details (50 per floor × 10 floors)

### Requirement 2: Floor-Specific Thematic Consistency

**User Story:** As a GM, I want NPC details to match each floor's theme and factions, so that encounters feel authentic to the dungeon's lore.

#### Acceptance Criteria

1. FOR floor 1, THE Event_Generator SHALL generate NPC details featuring mitflits, their "Sky King" worship, and basic undead
2. FOR floor 2, THE Event_Generator SHALL generate NPC details featuring morlocks, the "Ghost Queen" worship, and undead servants
3. FOR floor 3, THE Event_Generator SHALL generate NPC details featuring ghoul librarians, the Cult of the Canker, and minor devils
4. FOR floor 4, THE Event_Generator SHALL generate NPC details featuring drow, velstracs, Volluk's forces, and Belcorra's servants
5. FOR floor 5, THE Event_Generator SHALL generate NPC details featuring arena beasts, fleshwarp experiments, and combat-trained creatures
6. FOR floor 6, THE Event_Generator SHALL generate NPC details featuring seugathi fleshwarpers, driders, and experimental creatures
7. FOR floor 7, THE Event_Generator SHALL generate NPC details featuring devils, infernal creatures, and denizens of Leng
8. FOR floor 8, THE Event_Generator SHALL generate NPC details featuring bog mummies (Children of Belcorra), deep gnomes, and Darklands creatures
9. FOR floor 9, THE Event_Generator SHALL generate NPC details featuring drow, urdefhan, caligni factions, and Darklands fauna
10. FOR floor 10, THE Event_Generator SHALL generate NPC details featuring ancient undead, serpentfolk remnants, and Nhimbaloth's servants
11. THE Event_Generator SHALL reference specific NPCs, factions, and lore from gauntlight_keep_levels.md
12. THE Event_Generator SHALL maintain thematic consistency with the floor's atmosphere and history

### Requirement 3: Creature-Appropriate Details

**User Story:** As a GM, I want NPC details to reference creatures that actually exist on each floor, so that encounters are mechanically valid.

#### Acceptance Criteria

1. WHEN generating NPC details, THE Event_Generator SHALL filter creatures by floor-appropriate level ranges
2. WHEN generating NPC details, THE Event_Generator SHALL filter creatures by floor-appropriate traits and types
3. THE Event_Generator SHALL use the same creature filtering logic as combat event generation
4. THE Event_Generator SHALL prioritize creatures with common or uncommon rarity
5. THE Event_Generator SHALL exclude creatures with invalid names (book references, trait lists)
6. THE Event_Generator SHALL reference creatures that match floor keywords from gauntlight_keep_levels.md
7. WHEN no creatures match floor criteria, THE Event_Generator SHALL use generic descriptions based on floor theme

### Requirement 4: Distinctive Humanizing Characteristics

**User Story:** As a GM, I want NPCs to have distinctive features and personalities, so that they feel like individuals rather than generic monsters.

#### Acceptance Criteria

1. THE Event_Generator SHALL include physical distinctive features (scars, markings, unusual coloring, missing body parts)
2. THE Event_Generator SHALL include personality traits (nervous, aggressive, cunning, lazy, zealous)
3. THE Event_Generator SHALL include possessions or equipment (letters, trinkets, weapons, armor details, personal items)
4. THE Event_Generator SHALL include behavioral quirks (muttering, twitching, humming, collecting things)
5. THE Event_Generator SHALL include backstory hints (former occupation, relationships, motivations)
6. THE Event_Generator SHALL include humanizing details (notes for lovers, pictures of family, mementos)
7. THE Event_Generator SHALL vary detail types across the 50 entries per floor
8. THE Event_Generator SHALL make details specific enough to be memorable but brief enough to use quickly

### Requirement 5: Output Format and Storage

**User Story:** As a developer, I want NPC details stored in a structured format, so that they can be easily accessed and integrated into encounters.

#### Acceptance Criteria

1. THE Event_Generator SHALL output NPC details to etc/dungeon_npc_details.json
2. THE JSON file SHALL be organized by floor number (keys "1" through "10")
3. EACH floor key SHALL contain an array of exactly 50 string entries
4. EACH string entry SHALL be a complete narrative description (1-3 sentences)
5. THE JSON file SHALL use UTF-8 encoding
6. THE JSON file SHALL be valid JSON (parseable without errors)
7. THE JSON structure SHALL be: {"1": [50 strings], "2": [50 strings], ..., "10": [50 strings]}

### Requirement 6: Invisible Integration with Existing Generator

**User Story:** As a GM, I want NPC details to enhance all encounters with intelligent beings automatically, so that I don't need to manually add flavor.

#### Acceptance Criteria

1. WHEN generating any encounter with intelligent beings, THE Event_Generator SHALL randomly select an NPC detail from the current floor
2. THE Event_Generator SHALL append the NPC detail to the encounter description
3. THE Event_Generator SHALL format NPC details as a separate "NPC Detail" or "Character Note" field in encounters
4. WHEN dungeon_npc_details.json is missing, THE Event_Generator SHALL generate encounters without NPC details
5. WHEN dungeon_npc_details.json is present, THE Event_Generator SHALL include NPC details in all applicable encounters
6. THE Event_Generator SHALL log a warning if NPC details file is missing
7. THE Event_Generator SHALL apply details to combat encounters, patrols, social encounters, and any event with intelligent NPCs
8. THE Event_Generator SHALL not apply details to purely environmental hazards or non-intelligent creature encounters

### Requirement 7: Generation Script

**User Story:** As a developer, I want a standalone script to generate NPC details, so that I can regenerate them independently of the main event generator.

#### Acceptance Criteria

1. THE system SHALL provide a script bin/generators/generate_npc_details.py
2. THE script SHALL accept a --floors parameter to specify which floors to generate (default: all 10)
3. THE script SHALL accept an --output parameter to specify output file path (default: etc/dungeon_npc_details.json)
4. THE script SHALL accept a --count parameter to specify how many details per floor (default: 50)
5. THE script SHALL load floor data from etc/gauntlight_keep_levels.md
6. THE script SHALL load creature data from etc/creatures.json
7. THE script SHALL display progress as it generates details for each floor
8. THE script SHALL validate output JSON before writing to file

### Requirement 8: Variety and Randomization

**User Story:** As a GM, I want NPC details to be varied and unpredictable, so that encounters don't feel repetitive.

#### Acceptance Criteria

1. THE Event_Generator SHALL use randomization when generating NPC details
2. THE Event_Generator SHALL vary detail categories (physical, personality, possessions, behavior, backstory, humanizing)
3. THE Event_Generator SHALL avoid repeating the same detail patterns within a floor
4. THE Event_Generator SHALL combine multiple detail types in some entries (e.g., physical + personality)
5. THE Event_Generator SHALL include both serious and quirky details for tonal variety
6. THE Event_Generator SHALL reference specific floor lore elements in at least 30% of details per floor

### Requirement 9: Leverage NPC Lore Generation for Enhanced Details

**User Story:** As a GM, I want some NPC details to include full character profiles from the NPC lore generator, so that I can have rich, detailed NPCs for social encounters.

#### Acceptance Criteria

1. THE Event_Generator SHALL optionally integrate with bin/generators/generate_npc_lore.py
2. FOR approximately 20% of NPC details per floor, THE Event_Generator SHALL generate full NPC profiles using the lore generator
3. WHEN generating full NPC profiles, THE Event_Generator SHALL exclude the "Setup" and "Read-Aloud" fields
4. WHEN generating full NPC profiles, THE Event_Generator SHALL include: name, race, profession, personality, and background narrative
5. THE Event_Generator SHALL format full NPC profiles as markdown within the NPC detail string
6. THE Event_Generator SHALL ensure full NPC profiles are thematically appropriate for the floor
7. THE Event_Generator SHALL adapt NPC professions to match floor themes (e.g., "Ghoul Librarian" for floor 3)
8. THE Event_Generator SHALL adapt NPC races to match floor creatures (e.g., "Drow" for floors 4 and 9)
9. THE Event_Generator SHALL maintain a mix of brief details (80%) and full profiles (20%) per floor
10. WHEN the NPC lore generator is unavailable, THE Event_Generator SHALL generate only brief details

### Requirement 10: Invisible Integration - No Separate UI

**User Story:** As a GM using the dungeon turn generator, I want NPC details to automatically enhance all encounters with intelligent beings, so that every interaction feels more alive and memorable without requiring extra work.

#### Acceptance Criteria

1. THE Event_Generator SHALL automatically add NPC details to any encounter involving intelligent beings
2. THE Event_Generator SHALL apply NPC details to combat encounters, patrols, social encounters, and any event with NPCs
3. THE Event_Generator SHALL add details invisibly without requiring user configuration or separate generation steps
4. THE Event_Generator SHALL maintain backward compatibility - existing encounter generation continues to work
5. THE Event_Generator SHALL gracefully handle missing NPC details file (generate encounters without details)
6. THE Event_Generator SHALL not create any separate UI or web interface for NPC detail generation
7. THE Event_Generator SHALL integrate NPC details directly into the existing encounter output format
8. THE Event_Generator SHALL apply appropriate details based on encounter type (combat vs social vs patrol)
9. THE Event_Generator SHALL ensure details match the intelligence level and nature of the beings involved
10. THE Event_Generator SHALL make the enhancement feel seamless and natural to the GM

## Technical Requirements

### Command-Line Interface

```bash
# Generate NPC details for all floors
python bin/generators/generate_npc_details.py

# Generate for specific floors
python bin/generators/generate_npc_details.py --floors 1 2 3

# Specify output location
python bin/generators/generate_npc_details.py --output custom/path/npc_details.json

# Generate more or fewer details per floor
python bin/generators/generate_npc_details.py --count 100
```

### Output Format Example

```json
{
  "1": [
    "This mitflit wears a rusty crown made from bent nails and mutters prayers to the 'Sky King' between attacks.",
    "A skeletal warrior still clutches a faded letter from Belcorra, ordering it to guard the eastern passage.",
    "This mitflit has bright blue war paint and carries a sack of 'shinies' - mostly worthless junk.",
    "An undead servant with a broken jaw that clicks rhythmically as it moves, wearing tattered livery.",
    "This mitflit is missing an ear and has a nervous twitch, constantly looking over its shoulder.",
    ...
  ],
  "2": [
    "A morlock with ritual scars spelling 'Ghost Queen' across its chest, zealously devoted.",
    "This morlock wears a necklace of finger bones and hums a tuneless dirge.",
    "An undead servant still performing cleaning duties, methodically sweeping the same spot forever.",
    ...
  ],
  ...
}
```

### Integration Example

When encounter is generated:

```python
# Load NPC details
npc_details = load_npc_details("etc/dungeon_npc_details.json")

# Select random detail for current floor
if floor_num in npc_details:
    detail = random.choice(npc_details[str(floor_num)])
    event['npc_detail'] = detail
```

### Data Sources

- **etc/gauntlight_keep_levels.md**: Floor themes, factions, NPCs, lore
- **etc/creatures.json**: Creature names, levels, traits, types
- **Floor keywords** (from generate_dungeon_turn_v2.py):
  - Floor 1: mitflit, gremlin, undead, skeleton, zombie, shambling
  - Floor 2: morlock, humanoid, undead, degenerate, servant
  - Floor 3: ghoul, undead, librarian, scribe, devil, zebub, imp
  - Floor 4: drow, elf, undead, velstrac, worm, leech, werewolf
  - Floor 5: beast, animal, lizard, grothlut, fleshwarp, devil
  - Floor 6: seugathi, aberration, fleshwarp, drider, ooze, grothlut
  - Floor 7: devil, fiend, imp, erinyes, contract, infernal, denizen, leng
  - Floor 8: mummy, bog, undead, bodak, gnome, svirfneblin, gug, caligni
  - Floor 9: drow, elf, urdefhan, caligni, darklands, duergar, xulgath, ratfolk, spider
  - Floor 10: undead, ghost, serpentfolk, aberration, void, empty, nhimbaloth

## Out of Scope

- Creating a separate web UI for NPC detail generation
- Modifying existing combat event generation logic (beyond adding NPC details)
- Creating new creature entries in creatures.json
- Generating NPC details for non-combat events without intelligent beings
- Creating full NPC stat blocks (only narrative descriptions)
- Translating or localizing NPC details
- Creating NPC portraits or images
- Generating NPC names (use creature type names)

## Success Criteria

1. 500 total NPC details generated (50 per floor × 10 floors)
2. Each floor's details match its theme and lore
3. Details reference appropriate creatures from creatures.json
4. Output is valid JSON in the specified format
5. Encounters with intelligent beings automatically include NPC details when file is present
6. Generation script runs successfully and produces valid output
7. NPC details add narrative flavor without slowing down gameplay
8. Integration is invisible - no separate UI or generation step required

## Dependencies

- etc/gauntlight_keep_levels.md (existing)
- etc/creatures.json (existing)
- bin/generators/generate_dungeon_turn_v2.py (existing)
- bin/generators/generate_npc_lore.py (existing - for full NPC profiles)
- Python 3.x with json, random, re, os modules
