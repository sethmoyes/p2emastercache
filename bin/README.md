# Pathfinder 2e Campaign Tools - Scripts

This directory contains all the scripts for generating and managing campaign content.

## Directory Structure

### `/generators/` - Content Generation Scripts
Scripts that create game content for the campaign:

- **`generate_dungeon_turn_v2.py`** - NEW! Generates fun, engaging 5d20 dice jar encounters
  - Usage: `python3 bin/generators/generate_dungeon_turn_v2.py --level 4 --floors 3`
  - Creates: `gm/dungeon_turn_encounters_v2.md`
  - Features: 50/50 combat split, rewards creativity, living dungeon ecology
  - See: `gm/DUNGEON_TURN_V2_QUICK_REFERENCE.md` for GM guide

- **`generate_dungeon_turn.py`** - LEGACY - Original 5d20 dice jar encounters
  - Usage: `python3 bin/generators/generate_dungeon_turn.py --level 4 --floors 3 --generate-all`
  - Creates: `gm/dungeon_turn_encounters.md`

- **`generate_merchants.py`** - Generates merchant inventories for Otari shops
  - Usage: `python bin/generators/generate_merchants.py`
  - Creates: Files in `players/` directory

- **`generate_4d20_encounters.py`** - Generates overland/Fogfen encounters
  - Usage: `python bin/generators/generate_4d20_encounters.py`
  - Creates: `gm/4d20_fogfen_otari_encounters.md`

- **`generate_npc_lore.py`** - Generates detailed NPC backgrounds
  - Used by other generators, can also run standalone for testing

### `/data_management/` - Data Maintenance Scripts
Scripts for managing and maintaining data files:

- **`check_data_integrity.py`** - Validates data against Archives of Nethys
  - Usage: `python bin/data_management/check_data_integrity.py all equipment --replace`
  - Checks: `etc/equipment.json`, `etc/creatures.json`, `etc/dieties.json`

- **`expand_encounter_pools.py`** - Expands encounter pools from creatures.json
  - Usage: `python bin/data_management/expand_encounter_pools.py`
  - Creates: `etc/expanded_pools.json`

- **`encounter_pools.py`** - Loads encounter pools (imported by generators)

- **`complete_flavor_events.py`** - Completes dungeon flavor events
  - Usage: `python bin/data_management/complete_flavor_events.py`
  - Updates: `etc/dungeon_flavor_events.json`

- **`reset_verification_dates.py`** - Resets verification dates for re-checking
  - Usage: `python bin/data_management/reset_verification_dates.py`

### `/scrapers/` - Data Collection Scripts
Scripts that scrape data from external sources:

- **`scrape_spells.py`** - Scrapes spells from Archives of Nethys
  - Usage: `python bin/scrapers/scrape_spells.py`
  - Creates: `etc/spells.json`

- **`scrape_creature_lore.py`** - Scrapes creature lore from PathfinderWiki
  - Usage: `python bin/scrapers/scrape_creature_lore.py`
  - Creates: `etc/creature_lore.json`

## Quick Reference

### Generate Dungeon Encounters
```bash
python bin/generators/generate_dungeon_turn.py --level 4 --floors 3 --generate-all
```

### Generate Merchants
```bash
python bin/generators/generate_merchants.py
```

### Generate Overland Encounters
```bash
python bin/generators/generate_4d20_encounters.py
```

### Check Data Integrity
```bash
python bin/data_management/check_data_integrity.py 10 equipment
```

### Update All Data
```bash
python bin/scrapers/scrape_spells.py
python bin/scrapers/scrape_creature_lore.py
python bin/data_management/expand_encounter_pools.py
```

## Notes

- All scripts reference data files in `/etc/` directory
- Generated content goes to `/gm/` or `/players/` directories
- See `kiro.md` for detailed generation rules and guidelines
