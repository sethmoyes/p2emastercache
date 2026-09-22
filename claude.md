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

## Dungeon Turn Mechanics

### Time and Movement
- **Moving between floors**: Takes 10 minutes (ADD 1 DIE TO JAR)
- **Exploring within a floor**: Varies by action (see event time costs)
- **Resting**: Short rest (10 min) = 1 die, Long rest (1 hour) = 6 dice

### Dice Jar System
- Roll 5d20 to determine encounter type
- Each die in jar represents 10 minutes of dungeon time
- When jar reaches certain thresholds, increase encounter danger

### Prepared Tokens (NEW!)
Some events grant "Prepared" tokens that represent efficient preparation:
- **How to get**: Choose "preparation" option on tactical advantage events
- **Cost**: ADD 1 DIE TO JAR (10 minutes to prepare)
- **Benefit**: Next time you would add dice to jar, spend this token to add 1 fewer die (minimum 0)
- **Example**: You spend 10 min preparing fallback positions (add 1 die, gain token). Later, moving between floors would cost 1 die, but you spend the token and add 0 dice instead.
- **Tracking**: Mark tokens on character sheets or party tracker
- **Use case**: When no immediate combat expected, invest time now to save time later

This rewards tactical thinking even when combat isn't imminent!

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
- **NEVER create summary documents** - summarize work in chat only
- No SUMMARY.md, STATUS.md, CHANGES.md, or similar files
- User can read chat history for summaries

## Event Generation Philosophy - How to Make Generic Events SPECIFIC

### The Problem with Generic Events
Generic events like "A creature attacks" or "Enemies approach" are USELESS at the table. They force the GM to improvise everything, break immersion, and waste the goldmine of lore you already have.

### The Solution: Specificity Through Lore Integration

**STEP 1: Read the Lore Files**
- `gauntlight_keep_levels.md` - Know EVERY floor's theme, factions, NPCs, and ecology
- `creatures.json` - Know EVERY creature's stats (Level, HP, AC, special abilities)
- `creature_lore.json` - Know creature behavior and motivations

**STEP 2: Floor-Specific Creatures**
Every floor has its own ecology. Use it:
- Floor 1: Mitflits (worship rusty helmet as "Sky King"), Boss Skrawng, giant maggots
- Floor 2: Morlocks (worship Belcorra as "Ghost Queen"), King Graulgust
- Floor 3: Ghouls (Cult of the Canker), Nhakazarin, seeking "cankerous flesh for golem"
- Floor 4: Wights, skeletons (Belcorra's ancient guards), Volluk, Voidglutton
- Floor 5: Arena beasts, Cratonys (feral velstrac), Chafkhem
- Floor 6: Seugathi (fleshwarpers), Jafaki, driders, Shadow Malice band, Warped Brew tavern
- Floor 7: Devils (Urevian's prison), Szek (imp), Ysondkhelir (denizen of Leng), Cynemi
- Floor 8: Bog mummies (Children of Belcorra), Urthagul (gug with Crimson Lens), caligni cult
- Floor 9: Drow (Yldaris, Quara), Urdefhan (Khurfel with Emerald Lens), caligni refugees (Galudu)
- Floor 10: Nhimbaloth cultists, The Lady's Whisper, Belcorra (final boss)

**STEP 3: Include Complete Stats with References**
ALWAYS include from creatures.json with links:
- Creature name (exact match from creatures.json)
- Quantity (dice notation: 1d3, 2d4, etc.)
- Reference link (AON URL or creatures.json lookup)
- Quick stats in description for GM convenience

Example: 
```json
"creatures": "1d3 Ghouls",
"creature_reference": {
  "Ghoul": {
    "source": "creatures.json",
    "aon_url": "https://2e.aonprd.com/Monsters.aspx?ID=218",
    "level": 1,
    "hp": 20,
    "ac": 16,
    "key_abilities": ["Paralytic claws: DC 15 Fort", "Ghoul fever: DC 15 Fort"]
  }
}
```

This allows:
- GMs to click through to full stat blocks
- Quick reference without leaving the event
- Validation that creature exists in creatures.json
- Easy updates if creature stats change

**STEP 4: Add Faction Context**
Every creature serves someone or something:
- Mitflits → Boss Skrawng → "Sky King" (rusty helmet)
- Morlocks → "Ghost Queen" (Belcorra)
- Ghouls → Cult of the Canker → Nhakazarin → flesh golem
- Seugathi → Jafaki → fleshwarping experiments
- Devils → Urevian → contract enforcement
- Urdefhan → Khurfel → Emerald Fulcrum Lens

**STEP 5: Add Tactical Flavor**
Make each encounter feel different:
- Mitflits: Cowardly, flee if 2+ die, alert Boss Skrawng
- Morlocks: Swarming (+1 if 2+ adjacent), darkvision 120ft, light-sensitive
- Ghouls: Paralytic claws (DC 15 Fort), ghoul fever, scent ability
- Wights: Drain Life (1d6 negative + drained 1), undead immunities
- Seugathi: Psychic Crush (4d6 mental, DC 24 Will), telepathy 100ft
- Devils: Respect authority/contracts, immune to fire, beard attack
- Urdefhan: Wicked Bite (1d8 + 1d4 evil), Ferocity (don't fall at 0 HP)

**STEP 6: Add Lore Hooks**
Every encounter should hint at the bigger picture:
- "For Sky King!" → mitflit religion
- "Ghost Queen hungers!" → morlock worship
- "Cankerous flesh for the golem!" → Cult of Canker's goal
- "Jafaki needs specimens!" → seugathi experiments
- "Urevian's law is absolute!" → devil hierarchy
- "For Khurfel! For glory!" → urdefhan honor culture

**STEP 7: Named NPCs When Possible**
Use actual NPCs from the lore:
- Augrael (ghoulish morlock, tranquil reader)
- Szek (mischievous imp who locked Chafkhem)
- Cratonys (feral velstrac, lost her mind)
- Lallizanx (lazy drider bouncer, reads romance novels)
- Chafkhem (bossy Osirion wizard from ancient era)
- Cynemi (tiefling bounty hunter, history with Carman Rajani)
- Padli (alcoholic caligni, Dulac's second-in-command)
- Ryta (ratfolk vocalist from Shadow Malice band)

**STEP 8: Explicit Mechanics**
Never be vague about game mechanics:
- BAD: "They might surprise you"
- GOOD: "DC 19 Perception to spot them first, or they get surprise round"
- BAD: "Some enemies arrive"
- GOOD: "1d3+1 Morlocks arrive in 2 rounds"
- BAD: "They're dangerous"
- GOOD: "Paralytic claws: DC 15 Fort save or paralyzed 1 round"

**STEP 9: Dice Jar Integration**
For DILEMMA events, always specify:
- "REMOVE 1 DIE FROM JAR" (fast choice)
- "ADD 1 DIE TO JAR (takes 20 minutes)" (slow choice)
- "ADD 2 DICE TO JAR (takes 40 minutes)" (very slow choice)
- "NO DICE ADDED" (neutral choice)

**STEP 10: GM Notes Are Gold**
Every event needs GM notes with:
- Floor number
- Faction connections
- Tactical considerations
- Consequences of choices
- Lore implications

Example:
```
"gm_notes": "Floor 3 specific. Cult of Canker ghouls. Paralytic claws: DC 15 Fort. Ghoul fever: DC 15 Fort. Seeking flesh for golem in Temple of Canker (C34). If Nhimbaloth invoked, they pause - shows deep religious knowledge."
```

### The Formula That Works

**Generic Event:**
```json
{
  "title": "Enemies Attack!",
  "description": "Hostile creatures attack you",
  "creatures": "Some enemies"
}
```

**Specific Event:**
```json
{
  "title": "Ghoul Librarian Ambush!",
  "description": "Ghouls hidden among bookshelves suddenly attack! 'More flesh for the golem!' Claws extended!",
  "immediate_action": "DC 19 Perception to smell decay, or they attack with surprise",
  "success": "You smell rot! Roll initiative normally.",
  "failure": "Hidden attack! 1d3 Ghouls leap out! Paralysis risk!",
  "creatures": "1d3 Ghouls",
  "creature_reference": {
    "Ghoul": {
      "source": "creatures.json",
      "aon_url": "https://2e.aonprd.com/Monsters.aspx?ID=218",
      "level": 1,
      "hp": 20,
      "ac": 16,
      "key_abilities": ["Paralytic claws: DC 15 Fort", "Ghoul fever: DC 15 Fort"]
    }
  },
  "gm_notes": "Floor 3. Paralytic claws: DC 15 Fort or paralyzed 1 round. Ghoul fever: DC 15 Fort or contract disease. Cult of Canker seeks cankerous flesh for flesh golem in Temple (C34)."
}
```

### Why This Works
1. **GM can run it immediately** - all info is there
2. **Players feel the world** - factions, motivations, lore
3. **Combat is tactical** - specific abilities matter
4. **Choices have weight** - consequences are clear
5. **Lore is integrated** - every encounter teaches something
6. **Stats are accurate** - pulled from creatures.json
7. **Floors feel different** - each has unique ecology

### The Creative Process
1. Pick a generic event title
2. Ask: "What floor is this for?"
3. Ask: "What creatures live on that floor?"
4. Look up their stats in creatures.json
5. Ask: "What faction do they serve?"
6. Ask: "What are they doing RIGHT NOW?"
7. Ask: "What makes this encounter unique?"
8. Write it like you're describing a movie scene
9. Add all the mechanical details
10. Add GM notes connecting to larger story

### Red Flags (Don't Do This)
- ❌ "A creature" → ✓ "1d3 Ghouls (Level 1, HP 20, AC 16)"
- ❌ "Enemies" → ✓ "Morlocks from King Graulgust's pack"
- ❌ "They attack" → ✓ "Paralytic claws: DC 15 Fort or paralyzed"
- ❌ "Generic guards" → ✓ "Bearded devils enforcing Urevian's law"
- ❌ "Some danger" → ✓ "Psychic Crush: 4d6 mental, DC 24 Will"
- ❌ "Split the party" → ✓ "Rush vs Caution: REMOVE 1 DIE or ADD 1 DIE"

### Remember
The lore files are a GOLD MINE. Every generic event is a missed opportunity to make the dungeon feel alive, connected, and real. Use the lore. Use the stats. Make it specific. Make it sing.

---

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
