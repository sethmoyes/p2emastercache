# Pathfinder 2e Campaign Tools - Project Guidelines

## Project Overview
Campaign tools for the Abomination Vaults adventure path, set in Otari: a Flask
app (`bin/web/dungeon_turn_app.py`) with GM, player and atlas pages, plus the
generators behind it. See `README.md` for running, deploying and the CLI tools.

## Sources of Truth

When two files disagree, this is the order that wins:

1. **`common/campaign-reference/floors/`** - room-by-room reference for every
   floor of Gauntlight Keep (rooms, creatures, DCs, NPCs, cross-floor links),
   from the book. It beats anything else in the repo, including
   `etc/gauntlight_keep_levels.md`.
2. **`etc/floor_ecology.json`** - what actually wanders each floor (creatures,
   hazards, events), each entry citing its floor doc. The dungeon turn draws
   COMBAT and most ACTIVE_THREAT events from it. Don't restate floor ecology
   anywhere else; read it from here.
3. **Code defaults** - merchant rules live in `SETTINGS_SCHEMA` in
   `bin/generators/generate_merchants.py`; the dice distribution lives in
   `get_category_from_sum` in `bin/generators/generate_dungeon_turn_v2.py`.
   This file describes them but the code is authoritative.

Data the tools read, in `etc/`:
- **`creatures.json`** - creature stats (level, HP, AC, attacks, abilities, AoN url).
  Names repeat across legacy and remaster entries; prefer looking a creature up
  by its AoN url.
- **`equipment.json`**, **`spells.json`** - shop stock
- **`dungeon_turn_events.json`** - OPPORTUNITY, COMPLICATION, DILEMMA and
  ACTIVE_THREAT templates. Templates with `"retired"` stay on file but never roll.
- **`floor_ecology.json`** - see above
- **`gauntlight_keep_levels.md`** - floor names and themes (narrative only)
- **`dieties.json`**, **`inner_sea_region.md`**, **`players_guide.md`** - lore
- **`maps.json`**, **`*_locations.json`** - the atlas

## Generation Rules

### Merchants (`bin/generators/generate_merchants.py`)
Defaults (all adjustable from the GM page's Restock panel):
- Shops: 3-15 common, 1-3 uncommon; 2 random shops get a rare item
- Otari Market: 20-50 common, 5-15 uncommon, 1-3 rare
- Equipment max level: party level + `item_level_offset` (default 0)
- Spell max rank: party level
- Potions: 3-6 per shop at party level - 3 or higher (min level 1), at least
  one Spell Slot Restoration Potion
- Traveling merchants: written to `gm/traveling_merchant_N.md`; a restock
  replaces the whole set

### Dungeon Turn (`bin/generators/generate_dungeon_turn_v2.py`)
- 5d20. Extreme rolls (5-15, 90-100) are always combat at a Severe or Extreme
  budget; they come up about once in 530 rolls.
- Any other roll: 50% quiet passage; otherwise 5-44 and 63-89 are COMBAT or
  ACTIVE_THREAT, 45-62 are OPPORTUNITY, COMPLICATION or DILEMMA.
- Combat comes from `floor_ecology.json`, scaled with the PF2e XP budget (Low on
  normal rolls) by party level and party size.
- Boss NPCs and unique named entities never appear as random encounters.
- Hazards vs creatures: sinkholes, traps, wards, manifestations, effects = hazards.

## Important Rules

### Character Encoding
- ASCII only in generated text and script output: use OK/X, not check marks, and
  `<=`/`>=`, not their Unicode forms. Unicode breaks Windows consoles.

### Data Integrity
- DO NOT run data integrity scripts - the user has them running in other windows.
  Check before rewriting `equipment.json`, `creatures.json` or `dieties.json`.
- Use JSON parsing instead of markdown parsing when possible.

### Documents
- **NEVER create summary documents** - summarize work in chat only.
- No SUMMARY.md, STATUS.md, CHANGES.md, or similar files.

### Named Enemies
- Don't use named enemies (Cratonys, Khurfel, Urthagul, and the like) as
  incidental encounters. They are either already dead from earlier play or need
  to be met through the adventure's own story. Use them in lore, flavor and GM
  notes, or when an event specifically leads to meeting them as a designed
  encounter.

### Creature Encounters
- Use exact creature names from `creatures.json`, with counts and level:
  "1d3 Ghouls (Level 1)" not "some ghouls".
- Every creature reference carries stats copied from `creatures.json` and its
  AoN url; never invent abilities or stats.

## Dungeon Turn Mechanics

### Time and Movement
- **Moving between floors**: 10 minutes (ADD 1 DIE TO JAR)
- **Exploring within a floor**: varies by action (see each event's time cost)
- **Resting**: short rest (10 min) = 1 die, long rest (1 hour) = 6 dice

### Dice Jar
- Each die in the jar is 10 minutes of dungeon time.
- Roll 5d20 to see what happens.

### Prepared Tokens
Some events grant "Prepared" tokens for efficient preparation:
- **Cost**: ADD 1 DIE TO JAR (10 minutes to prepare)
- **Benefit**: the next time you would add dice, spend the token to add 1 fewer
  (minimum 0)

## Event Writing Philosophy

Generic events ("A creature attacks", "You find supplies") are useless at the
table: the GM has to improvise everything. Every event should be something the
GM can run straight off the card.

1. **Know the floor.** Read its floor doc in `common/campaign-reference/floors/`
   and its entries in `floor_ecology.json`: who lives there, who they serve, what
   they're doing right now.
2. **Use real creatures** with stats and AoN links from `creatures.json`.
3. **Give it faction context.** Every creature serves someone (mitflits and the
   "Sky King", morlocks and the "Ghost Queen", Jafaki's seugathi, Urevian's
   devils, Khurfel's urdefhan).
4. **Make mechanics explicit.** "DC 19 Perception or they get a surprise round",
   not "they might surprise you". "1d3+1 morlocks arrive in 2 rounds", not "some
   enemies arrive".
5. **Make choices cost time.** DILEMMA options say what they do to the jar:
   "REMOVE 1 DIE", "ADD 1 DIE (20 minutes)", "NO DICE ADDED".
6. **Write GM notes** with the floor, faction ties, tactics, consequences, and
   what it hints at.
7. **Respect the fixed map.** Don't teleport the party into a keyed room; events
   happen in passing, between rooms.

### Flavor
- Small discoveries: a single cushion, a tool, a stain, a sound.
- Not full rooms or major plot points. Prompt questions, don't answer them.
- GOOD: "A single leech crawls across the floor. Where did it come from?"
- BAD: "A ritual vat filled with thousands of leeches for transformation"

## File Structure

```
bin/web/            Flask app, templates, static assets
bin/generators/     dungeon turn, floor ecology, merchants, NPCs, hazards
bin/maps/           atlas tooling
bin/data_management/ AoN integrity checker
etc/                data the tools read
players/            Otari shop inventories
gm/                 traveling merchants, GM quick reference, 2d20 overland table
docs/               player-facing exploration guide
common/             reference from the GM's campaign repo (floor docs win)
```
