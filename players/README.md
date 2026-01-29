# Otari Merchant Files

This directory contains individual merchant inventory files for the town of Otari, based on the Abomination Vaults Player's Guide.

## Merchant Files

Each merchant has their own file with complete inventory, proprietor information, and services:

### Magical & Specialty Shops
- **wrins_wonders.md** - Wrin Sivinxi's magical items, scrolls, wands, potions, and alchemical goods
- **odd_stories.md** - Morlibint's bookshop and scroll emporium
- **dawnflower_library.md** - Vandy Banderdash's temple library with religious texts and scrolls

### General Goods
- **otari_market.md** - Keeleno Lathenar's general goods market (all types)
- **blades_for_glades.md** - Jorsk Hinterclaw's weapons and armor shop

### Taverns & Inns
- **crows_casks.md** - Crow's tavern and general store
- **crooks_nook.md** - Crook's seedy tavern and flophouse
- **the_rowdy_rockfish.md** - Tamily Tanderveil's lively tavern and inn

### Specialty Services
- **gallentine_deliveries.md** - Gallentine's courier and delivery service
- **otari_fishery.md** - Lillia Dusklight's fresh fish and fishing supplies

## Generating New Merchants

To generate fresh merchant inventories:

```bash
python bin/generate_merchants.py
```

This will:
1. Create individual `.md` files for each merchant with randomized inventories
2. Include all equipment details (Name, Level, Price, Rarity, Category, Type)
3. Add direct search links to Archives of Nethys for each item
4. Include proprietor information and available services
5. Randomize common items (15-50 depending on shop type)
6. Randomize uncommon items (1-7 per shop)
7. 10% chance for rare items (level 4)

## Merchant Categories

Merchants are categorized by the types of items they sell:

- **All Types**: Otari Market
- **Magical/Alchemical/Adventuring**: Wrin's Wonders, Odd Stories, Dawnflower Library
- **Weapons/Armor Only**: Blades for Glades
- **Adventuring Gear Only**: Taverns (Crow's Casks, Crook's Nook, Rowdy Rockfish), Otari Fishery
- **Services Only**: Gallentine Deliveries

## Item Links

All items include direct search links to Archives of Nethys (2e.aonprd.com) for easy reference and image lookup.
