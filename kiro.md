# Kiro Project Guidelines - Pathfinder 2e Campaign Tools

## Project Overview
This is a Pathfinder 2e campaign management system for the Abomination Vaults adventure path, set in Otari. All scripts and tools should reference the comprehensive data files in the `etc/` directory.

## Critical Data Sources (ALWAYS REFERENCE THESE)

### `/etc/` Directory - The Treasure Trove
All generation scripts MUST pull from these comprehensive data files:

- **`creatures.json`** - Complete creature database with stats, abilities, and lore for Pathfinder 2e
- **`equipment.json`** - All items, weapons, armor, potions, and gear with prices and levels
- **`spells.json`** - Complete spell database with levels, schools, and effects
- **`gauntlight_keep_levels.md`** - Comprehensive lore for all 10 floors of Gauntlight Keep (Abomination Vaults)
- **`creature_lore.json`** - Additional creature lore and flavor text
- **`dieties.json`** - Gods and religious information
- **`expanded_pools.json`** - Expanded encounter pools for various locations
- **`inner_sea_region.md`** - Golarion world lore and geography
- **`players_guide.md`** - Player-facing campaign information

## Generation Scripts

### Merchant Generation (`bin/generate_merchants.py`)
- Generates merchant inventories for Otari shops
- References: `equipment.json`, `spells.json`
- Rules:
  - Common items: 3-15 per merchant
  - Uncommon items: 1-3 per merchant
  - Rare items: 2 random merchants get 1 each
  - Otari Market gets DOUBLE (6-30 common, 2-6 uncommon)
  - Equipment max level: player_level + 2
  - Spell max level: player_level (NOT +2)
  - Healing potions: 3-6 per merchant, level X-3 minimum (min level 1)
  - At least 1 MUST be Spell Slot Restoration Potion

### Dungeon Turn Encounters (`bin/generate_dungeon_turn.py`)
- Generates 5d20 dice jar encounter system for Gauntlight Keep
- References: `gauntlight_keep_levels.md`, `creatures.json`
- Rules:
  - 5d20 probability distribution: 5-35 beneficial, 36-69 flavor (middle 50%), 70-100 threats
  - Flavor events should be TINY environmental details - fragments, traces, small clues
  - NOT major locations or plot points - just hints
  - Creature encounters should reference specific creatures from `creatures.json`
  - Encounters are 2 levels below party level
  - Generate for all floors 1 to X (where X is current floor)
  - Filter out all boss NPCs and unique named entities
  - Hazards vs creatures: sinkholes, traps, wards, manifestations, effects = hazards

### 4d20 Encounter Generation (`bin/generate_4d20_encounters.py`)
- Generates overland/Fogfen encounters
- References: `expanded_pools.json`, `creatures.json`

## Important Rules

### Character Encoding
- Replace Unicode characters (✓/✗) with ASCII (OK/X) to avoid encoding errors on Windows

### Data Integrity
- DO NOT run data integrity scripts - user has them running in other windows
- Use JSON parsing instead of markdown parsing when possible

### Creature Encounters
- Always reference `creatures.json` for accurate creature stats and abilities
- Use specific creature names, not generic types
- Example: "1 Ghoul Stalker (Level 2)" not "1-2x ghouls (Level 2 creatures)"

### Flavor Events Philosophy
- Should be SMALL discoveries: a single cushion, a tool, a stain, a sound
- NOT full rooms or major plot points
- Should prompt questions, not answer them
- Example GOOD: "A single leech crawls across the floor. Where did it come from?"
- Example BAD: "A ritual vat filled with thousands of leeches for transformation"

## File Structure

```
/
├── bin/                    # Generation scripts
├── etc/                    # DATA SOURCE - reference these!
├── gm/                     # GM-facing generated content
├── players/                # Player-facing location descriptions
└── kiro.md                 # This file
```

## Workflow
1. User requests generation (merchants, encounters, etc.)
2. Read relevant data from `/etc/` directory
3. Apply generation rules
4. Output to appropriate directory (`gm/` or `players/`)
5. Verify output quality

## Remember
- The `/etc/` directory is the source of truth
- Always check what data is available before generating
- Maintain consistency with existing lore and mechanics
- Keep flavor text mysterious and discovery-based

## Recent Updates

### Dungeon Turn V2 - Extreme Encounters & No-Event Mechanic (Feb 2026)

Major overhaul to the dungeon turn system with new probability distribution:

#### New Event Distribution
- **Extreme rolls (5-15, 90-100)**: Always generate COMBAT at floor level (deadly!)
- **Non-extreme rolls**: 50% chance of NO_EVENT (quiet passage)
- **Low rolls (5-44)**: COMBAT or ACTIVE_THREAT
- **Middle rolls (45-62)**: OPPORTUNITY, COMPLICATION, or DILEMMA
- **High rolls (63-100)**: ACTIVE_THREAT or COMBAT

#### Extreme Combat Encounters
- Use creatures at dungeon floor level (not party level -2)
- Generate 1-3 creatures from floor-appropriate pool
- Include floor-specific ecology and tactical notes
- Mark as unavoidable with special GM notes
- Low extreme rolls (5-15) can provide surprise rounds

#### Bug Fixes
- Fixed creature consistency bug where description said "2 Zombie Brute(s)" but creature list included random other creatures (e.g., Nuglub)
- Now selects ONE creature type and uses it consistently throughout the encounter
- Changed from `random.sample()` selecting multiple types to `random.choice()` selecting one type

### Dungeon Event Tweaker Integration (Feb 2026)

Added tactical variation system to web interface:

#### Features
- New "Tweak Event" button on generated encounters
- Generates 3 spatial variations: Narrow Space, Open Area, Vertical Space
- Each variation includes:
  - Adapted positioning and terrain features
  - Context-specific tactical options
  - Modified skill checks for the environment
  - Preserved core encounter elements
- Copy-to-clipboard functionality for each variation
- Modal interface with color-coded contexts

#### API Endpoint
- `/api/tweak` - POST endpoint for generating variations
- Accepts event data in standard format
- Returns array of tactical variations
- Error handling for invalid events

#### Implementation
- Integrated `dungeon_event_tweaker` module into web app
- Added modal UI with gradient styling
- JavaScript functions for displaying and copying variations
- Keyboard shortcut (ESC) to close modal
