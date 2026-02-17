# Otari Merchant Files

This directory contains individual merchant inventory files for the town of Otari, based on the Abomination Vaults Player's Guide.

## Merchant Files (10 Total)

Each merchant has their own file with complete inventory, proprietor portrait, and services:

### Magical & Specialty Shops
- **wrins_wonders.md** - Wrin Sivinxi's magical items, spell scrolls, runes, staffs, and potions
- **odd_stories.md** - Morlibint's bookshop with spell scrolls, runes, and magical items
- **dawnflower_library.md** - Vandy Banderdash's temple library with religious texts, scrolls, and runes

### General Goods
- **otari_market.md** - Keeleno Lathenar's large open-air market (DOUBLE inventory, all types)
- **blades_for_glades.md** - Jorsk Hinterclaw's weapons, armor, and shields

### Taverns & Specialty Shops
- **crows_casks.md** - Crow's tavern specializing in tea, oils, food, and alchemical potions
- **crooks_nook.md** - Crook's seedy tavern selling snares, tattoos, and consumables
- **the_rowdy_rockfish.md** - Tamily Tanderveil's lively tavern (all items EXCEPT weapons/armor)
- **otari_fishery.md** - Lillia Dusklight's fresh fish and fishing supplies

### Services
- **gallentine_deliveries.md** - Gallentine's courier and delivery service (no inventory)

## Merchant Features

Each merchant file includes:

### Proprietor Section
- **Portrait** (250px width) from PathfinderWiki or default merchant images
- **Description** of the shop and its atmosphere
- **Proprietor name** with ancestry, class, and level
- **Specialties** listing what the shop focuses on

### Spell Scrolls (Wrin's Wonders & Odd Stories)
- **Common scrolls** (5-15): Level 1-4 spells for learning
- **Uncommon scrolls** (3-5): Harder to find spells
- **Rare scrolls** (1): Only one of the two merchants has a rare spell
- **Study time**: 1 hour (common), 5 hours (uncommon), 1 day (rare)
- **Prices & DCs**: Based on spell level (2 gp @ DC 15 for level 1, up to 7,000 gp @ DC 41 for level 10)
- **Full details**: Traditions, cast time, range, traits, and Archives of Nethys links

### Runes (Wrin's, Odd Stories, Dawnflower)
- **Fundamental runes** (always available, 2-3 of each):
  - Weapon Potency (+1, +2, +3)
  - Striking (regular, Greater, Major)
  - Armor Potency (+1, +2, +3)
  - Resilient (regular, Greater, Major)
  - Reinforcing (regular, Greater, Major)
- **Property runes** (1-3 random): Level-appropriate runes for customization

### Regular Items
- **Common items** (3-15, or 6-30 for Otari Market)
- **Uncommon items** (1-3, or 2-6 for Otari Market)
- **Rare items** (2 random merchants get 1 each)
- **Item details**: Image, name, level, price, rarity, category, type
- **Archives of Nethys links** for each item

### Services
- Spellcasting, healing, repairs, information, etc.
- Prices listed or marked as GM discretion

## Generating New Merchants

To generate fresh merchant inventories:

```bash
# Generate all 10 merchants
python bin/generate_merchants.py --level 4

# Test a single merchant (fast)
python bin/generate_merchants.py --level 4 -tm wrins_wonders
python bin/generate_merchants.py --level 4 -tm otari_market
```

This will:
1. Create individual `.md` files for each merchant with randomized inventories
2. Generate spell scrolls for Wrin's Wonders and Odd Stories
3. Generate rune tables for Wrin's, Odd Stories, and Dawnflower Library
4. Include proprietor portraits (250px width)
5. Add item images from Archives of Nethys
6. Include direct links to Archives of Nethys for all items and spells
7. Randomize inventory quantities based on merchant type
8. Generate 2 random traveling merchants in `gm/` directory

## Merchant Inventory Rules

### Item Quantities
- **Common items**: 3-15 (6-30 for Otari Market)
- **Uncommon items**: 1-3 (2-6 for Otari Market)
- **Rare items**: 2 random merchants get 1 each
- **Spell scrolls**: 5-15 common, 3-5 uncommon, 1 rare (only 1 of 2 spell merchants)
- **Property runes**: 1-3 random runes per merchant

### Item Levels
- **Equipment**: Player level + 2 maximum
- **Spells**: Player level maximum (NOT +2)
- **Runes**: Player level maximum

### Merchant Specialties
- **Otari Market**: No restrictions, DOUBLE items
- **Wrin's Wonders**: Magical items, scrolls, staffs, runes, potions only
- **Odd Stories**: Books, scrolls, magical items, runes only
- **Blades for Glades**: Weapons, armor, shields only
- **Crow's Casks**: Tea, oils, food, beverages, alchemical potions only
- **Crook's Nook**: Snares, tattoos, consumables only
- **Rowdy Rockfish**: All items EXCEPT weapons/armor/shields
- **Otari Fishery**: Food and beverages only
- **Dawnflower Library**: Books, scrolls, runes only
- **Gallentine Deliveries**: Services only (no inventory)

## Item Links & Images

- All items include direct links to Archives of Nethys (2e.aonprd.com)
- Item images are scraped from Archives of Nethys during generation
- Spell scrolls link to spell pages with full details
- Runes link to rune pages with etching rules
- Merchant portraits are 250px width for consistency

## Notes

- Inventories are randomized each generation
- Spell scrolls are for learning (not casting)
- Fundamental runes are always available (2-3 of each in stock)
- Property runes are randomized (1-3 per merchant)
- Prices are verified against Archives of Nethys
- Generation takes ~10-15 minutes due to image scraping
- Use `-tm` flag to test individual merchants quickly
