# Otari Merchant Files

This directory contains individual merchant inventory files for the town of Otari, based on the Abomination Vaults Player's Guide.

## Individual Merchant Files

Each merchant has their own file with complete inventory, personality, and special services:

- **wrins_wonders.md** - Wrin Sivinxi's magical items and scrolls shop
- **otari_market.md** - Keeleno Lathenar's general goods market
- **odd_stories.md** - Morlibint's bookshop and scroll emporium
- **gallentine_deliveries.md** - Oloria Gallentine's delivery and special order service

## Legacy Combined Files

These files contain all merchants in one document (older format):

- **otari_merchant_inventories.md** - All Otari merchants combined
- **merchant_inventories.md** - Generic merchants (non-Otari)

## Generating New Merchants

To generate fresh merchant inventories with separate files:

```bash
python bin/generate_otari_merchants.py
python bin/fix_item_images.py --dir players
```

This will:
1. Create individual `.md` files for each merchant
2. Add proper image URLs from Archives of Nethys

## Image URLs

All items include image links in `.webp` format from Archives of Nethys:
- Weapons: `https://2e.aonprd.com/Images/Weapons/[Item_Name].webp`
- Armor: `https://2e.aonprd.com/Images/Armor/[Item_Name].webp`
- Treasure/Items: `https://2e.aonprd.com/Images/Treasure/[Item_Name].webp`
