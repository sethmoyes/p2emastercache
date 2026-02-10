# Scrapers Directory

Scripts for fetching and enhancing game data from Archives of Nethys.

## Active Scripts

### add_gauntlight_creatures.py
**Status:** ✅ Production Ready

Adds complete creature stats (attacks, abilities, defenses) for key Gauntlight Keep creatures.

**Usage:**
```bash
python3 bin/scrapers/add_gauntlight_creatures.py
```

**What it does:**
- Backs up `etc/creatures.json` to `etc/creatures_backup.json`
- Enhances 8 key creatures with full combat data:
  - Mitflit
  - Morlock
  - Ghoul
  - Skeleton Guard
  - Zombie Shambler
  - Giant Monitor Lizard
  - Wight
  - Shadow

**Data added:**
- Attacks (melee/ranged with damage)
- Special abilities
- Skills
- Languages
- Immunities/Resistances/Weaknesses

### scrape_creature_lore.py
**Status:** ✅ Working

Fetches creature lore/flavor text from Archives of Nethys.

### scrape_spells.py
**Status:** ✅ Working

Fetches spell data from Archives of Nethys.

## Archived/Removed Scripts

The following scripts were removed as they didn't work reliably:
- `scrape_creatures_enhanced.py` - SSL/API issues
- `apply_enhanced_creatures.py` - Superseded by add_gauntlight_creatures.py
- `enhance_creatures_v3.py` - API approach didn't work

## Future Enhancements

To add more creatures:

1. **Manual Curation (Recommended)**
   - Edit `add_gauntlight_creatures.py`
   - Add creature data to `GAUNTLIGHT_CREATURES` dict
   - Run script to apply

2. **API Scraping (Needs Work)**
   - Fix SSL certificate issues with Archives of Nethys
   - Implement proper HTML parsing with BeautifulSoup
   - Add rate limiting and error handling

## Data Sources

All data comes from [Archives of Nethys](https://2e.aonprd.com), the official Pathfinder 2E reference.

## Backup Policy

The `add_gauntlight_creatures.py` script automatically creates a backup before modifying the database:
- Original: `etc/creatures.json`
- Backup: `etc/creatures_backup.json`

Only one backup is kept (not overwritten on subsequent runs).
