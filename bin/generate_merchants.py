#!/usr/bin/env python3
"""
Unified Otari Merchant Generator
Generates merchant inventories with links to Archives of Nethys
"""
import random
import re
import os
import urllib.parse
import json

def load_equipment_json(filename):
    """Load equipment from JSON file"""
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def clean_item_name(name):
    """Clean item name for search - remove everything after special chars/numbers"""
    # Remove parentheses and everything inside
    name = re.sub(r'\([^)]*\)', '', name)
    # Remove everything after first digit
    name = re.split(r'\d', name)[0]
    # Remove special characters except spaces, hyphens, apostrophes
    name = re.sub(r'[^a-zA-Z\s\'-]', '', name)
    # Clean up extra spaces
    name = ' '.join(name.split())
    return name.strip()

def get_image_from_aon(item_name):
    """Generate Archives of Nethys image URL for the item"""
    # Create direct image URL to AoN using Google Images site search
    clean_name = clean_item_name(item_name)
    # Use Google Images with site filter for 2e.aonprd.com
    search_query = f"site:2e.aonprd.com {clean_name}"
    image_url = f"https://www.google.com/search?q={urllib.parse.quote(search_query)}&tbm=isch"
    return image_url

def fix_price(price):
    """Fix malformed prices from source data"""
    if not price or price == 'L':
        return "5 sp"  # Default for 'L' (likely means "Light" bulk, but used as price)
    
    # If it's just a number, assume gp
    if price.isdigit():
        return f"{price} gp"
    
    return price

def capitalize_field(text):
    """Capitalize first letter of text, handle N/A"""
    if not text or text == 'N/A' or text == '':
        return 'N/A'
    return text[0].upper() + text[1:] if len(text) > 0 else text

def generate_merchant_inventory(equipment, categories, num_common, num_uncommon):
    """Generate random inventory from equipment"""
    inventory = {'common': [], 'uncommon': [], 'rare': []}
    
    # Filter by categories and rarity
    common_pool = [e for e in equipment if e['type'] in categories and e['rarity'] == 'common']
    uncommon_pool = [e for e in equipment if e['type'] in categories and e['rarity'] == 'uncommon']
    rare_pool = [e for e in equipment if e['type'] in categories and e['rarity'] == 'rare']
    
    # Select items
    if common_pool:
        inventory['common'] = random.sample(common_pool, min(num_common, len(common_pool)))
    
    if uncommon_pool:
        inventory['uncommon'] = random.sample(uncommon_pool, min(num_uncommon, len(uncommon_pool)))
    
    # 10% chance for 1 rare item
    if random.random() < 0.1 and rare_pool:
        inventory['rare'] = [random.choice(rare_pool)]
    
    return inventory

def write_merchant_with_header(merchant_name, description, proprietor, specialties, inventory, services=None, output_dir='players'):
    """Write merchant file with header, proprietor image, and full item details"""
    filename = merchant_name.lower().replace(' ', '_').replace("'", '') + '.md'
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        # Header with proprietor image
        f.write(f"# {merchant_name}\n\n")
        f.write(f"<div align=\"center\">\n\n")
        f.write(f"![Proprietor](IMAGE_PLACEHOLDER)\n\n")
        f.write(f"</div>\n\n")
        f.write(f"*{description}*\n\n")
        f.write(f"**Proprietor:** {proprietor}\n\n")
        f.write(f"**Specialties:** {specialties}\n\n")
        
        # Common items
        if inventory['common']:
            f.write(f"## Common Items ({len(inventory['common'])})\n\n")
            
            for item in inventory['common']:
                # Get image URL
                image_url = get_image_from_aon(item['name'])
                
                # Fix and capitalize fields
                name = item['name']
                level = item['level']
                price = fix_price(item['price'])
                rarity = capitalize_field(item['rarity'])
                category = capitalize_field(item.get('category', 'N/A'))
                item_type = capitalize_field(item['type'])
                
                # Write item with image
                f.write(f"### {name}\n\n")
                f.write(f"![{name}]({image_url})\n\n")
                f.write(f"**Level:** {level} | **Price:** {price} | **Rarity:** {rarity}\n\n")
                f.write(f"**Category:** {category} | **Type:** {item_type}\n\n")
                f.write(f"[View on Archives of Nethys](https://2e.aonprd.com/Search.aspx?query={urllib.parse.quote(clean_item_name(name))})\n\n")
                f.write("---\n\n")
            
            f.write("\n")
        
        # Uncommon items
        if inventory['uncommon']:
            f.write(f"## Uncommon Items ({len(inventory['uncommon'])})\n\n")
            
            for item in inventory['uncommon']:
                # Get image URL
                image_url = get_image_from_aon(item['name'])
                
                # Fix and capitalize fields
                name = item['name']
                level = item['level']
                price = fix_price(item['price'])
                rarity = capitalize_field(item['rarity'])
                category = capitalize_field(item.get('category', 'N/A'))
                item_type = capitalize_field(item['type'])
                
                # Write item with image
                f.write(f"### {name}\n\n")
                f.write(f"![{name}]({image_url})\n\n")
                f.write(f"**Level:** {level} | **Price:** {price} | **Rarity:** {rarity}\n\n")
                f.write(f"**Category:** {category} | **Type:** {item_type}\n\n")
                f.write(f"[View on Archives of Nethys](https://2e.aonprd.com/Search.aspx?query={urllib.parse.quote(clean_item_name(name))})\n\n")
                f.write("---\n\n")
            
            f.write("\n")
        
        # Rare items
        if inventory['rare']:
            f.write(f"## Rare Items ({len(inventory['rare'])})\n\n")
            
            for item in inventory['rare']:
                # Get image URL
                image_url = get_image_from_aon(item['name'])
                
                # Fix and capitalize fields
                name = item['name']
                level = item['level']
                price = fix_price(item['price'])
                rarity = capitalize_field(item['rarity'])
                category = capitalize_field(item.get('category', 'N/A'))
                item_type = capitalize_field(item['type'])
                
                # Write item with image
                f.write(f"### {name}\n\n")
                f.write(f"![{name}]({image_url})\n\n")
                f.write(f"**Level:** {level} | **Price:** {price} | **Rarity:** {rarity}\n\n")
                f.write(f"**Category:** {category} | **Type:** {item_type}\n\n")
                f.write(f"[View on Archives of Nethys](https://2e.aonprd.com/Search.aspx?query={urllib.parse.quote(clean_item_name(name))})\n\n")
                f.write("---\n\n")
            
            f.write("\n")
        
        # Services section
        if services:
            f.write("## Services\n\n")
            for service in services:
                f.write(f"- {service}\n")
            f.write("\n")
    
    print(f"✓ Created: {filepath}")

if __name__ == "__main__":
    print("Loading equipment...")
    equipment = load_equipment_json("etc/equipment.json")
    print(f"  Loaded {len(equipment)} items")
    
    # Create output directory
    os.makedirs('players', exist_ok=True)
    
    # 1. Otari Market - All types
    print("\n[1/10] Generating Otari Market...")
    inventory = generate_merchant_inventory(
        equipment,
        categories=['weapon', 'armor', 'adventuring', 'alchemical', 'magical'],
        num_common=50,
        num_uncommon=random.randint(1, 7)
    )
    write_merchant_with_header(
        "Otari Market",
        "One-stop shop for basic goods",
        "Keeleno Lathenar (dour, humorless human merchant)",
        "All adventuring gear, light armor, and simple weapons",
        inventory
    )
    
    # 2. Wrin's Wonders - Magical items, scrolls, wands, potions, alchemical, adventuring
    print("\n[2/10] Generating Wrin's Wonders...")
    inventory = generate_merchant_inventory(
        equipment,
        categories=['magical', 'alchemical', 'adventuring'],
        num_common=30,
        num_uncommon=random.randint(1, 7)
    )
    write_merchant_with_header(
        "Wrin's Wonders",
        "Eccentric tiefling-elf oddities merchant and stargazer",
        "Wrin Sivinxi (CG female tiefling elf oddities merchant 5)",
        "Scrolls, wands, potions, alchemical items, and adventuring gear",
        inventory,
        services=[
            "Spellcasting Services: Price varies by spell level (GM discretion)",
            "Spell Learning/Training: Price negotiable (GM discretion)",
            "Magical item identification: 1-10 gp depending on complexity",
            "Astrological readings: 5 sp - 5 gp"
        ]
    )
    
    # 3. Odd Stories - Scrolls and adventuring gear
    print("\n[3/10] Generating Odd Stories...")
    inventory = generate_merchant_inventory(
        equipment,
        categories=['magical', 'adventuring'],
        num_common=25,
        num_uncommon=random.randint(1, 7)
    )
    write_merchant_with_header(
        "Odd Stories",
        "Bookshop and scroll emporium",
        "Morlibint (NG male gnome bookseller 3)",
        "Books, scrolls, and writing supplies",
        inventory,
        services=[
            "Spellcasting Services: Price varies by spell level (GM discretion)",
            "Spell Learning/Training: Price negotiable (GM discretion)",
            "Book copying and restoration: 1-5 gp per page",
            "Research assistance: 5 gp per day"
        ]
    )
    
    # 4. Gallentine Deliveries - Service only (no inventory)
    print("\n[4/10] Generating Gallentine Deliveries...")
    write_merchant_with_header(
        "Gallentine Deliveries",
        "Courier and delivery service",
        "Gallentine (N female human courier 2)",
        "Package delivery, message running, and escort services",
        {'common': [], 'uncommon': [], 'rare': []},
        services=[
            "Local delivery (within Otari): 1 sp per package",
            "Regional delivery (to nearby towns): 5 sp - 2 gp depending on distance",
            "Long-distance delivery: Price negotiable (GM discretion)",
            "Escort services: 5 gp per day",
            "Rush delivery: Double normal price"
        ]
    )
    
    # 5. Blades for Glades - Weapons and armor only
    print("\n[5/10] Generating Blades for Glades...")
    inventory = generate_merchant_inventory(
        equipment,
        categories=['weapon', 'armor'],
        num_common=40,
        num_uncommon=random.randint(1, 7)
    )
    write_merchant_with_header(
        "Blades for Glades",
        "Weaponsmith and armorer",
        "Jorsk Hinterclaw (LN male dwarf weaponsmith 4)",
        "Weapons and armor of all types",
        inventory,
        services=[
            "Weapon sharpening: 5 sp",
            "Armor repair: 1-5 gp depending on damage",
            "Custom weapon crafting: Price negotiable (GM discretion)",
            "Weapon engraving: 1 gp"
        ]
    )
    
    # 6. Crow's Casks - Adventuring gear only (tavern)
    print("\n[6/10] Generating Crow's Casks...")
    inventory = generate_merchant_inventory(
        equipment,
        categories=['adventuring'],
        num_common=20,
        num_uncommon=random.randint(1, 7)
    )
    write_merchant_with_header(
        "Crow's Casks",
        "Tavern and general store",
        "Crow (CN female human tavernkeeper 2)",
        "Food, drink, and basic adventuring supplies",
        inventory,
        services=[
            "Meals: 1 cp (poor) to 1 gp (fine)",
            "Lodging: 3 cp (floor space) to 5 sp (private room)",
            "Ale/Wine: 1 cp (mug) to 1 sp (bottle)",
            "Rumors and information: Free with purchase"
        ]
    )
    
    # 7. Crook's Nook - Adventuring gear only (tavern)
    print("\n[7/10] Generating Crook's Nook...")
    inventory = generate_merchant_inventory(
        equipment,
        categories=['adventuring'],
        num_common=20,
        num_uncommon=random.randint(1, 7)
    )
    write_merchant_with_header(
        "Crook's Nook",
        "Seedy tavern and flophouse",
        "Crook (NE male half-orc tavernkeeper 3)",
        "Cheap lodging and questionable goods",
        inventory,
        services=[
            "Meals: 1 cp (poor quality)",
            "Lodging: 3 cp (floor space) to 3 sp (shared room)",
            "Ale: 1 cp (watered down)",
            "Black market contacts: 5-50 gp (GM discretion)"
        ]
    )
    
    # 8. The Rowdy Rockfish - Adventuring gear only (tavern)
    print("\n[8/10] Generating The Rowdy Rockfish...")
    inventory = generate_merchant_inventory(
        equipment,
        categories=['adventuring'],
        num_common=25,
        num_uncommon=random.randint(1, 7)
    )
    write_merchant_with_header(
        "The Rowdy Rockfish",
        "Lively tavern and inn",
        "Tamily Tanderveil (CG female halfling innkeeper 4)",
        "Quality food, drink, and lodging",
        inventory,
        services=[
            "Meals: 5 cp (square) to 2 gp (fine)",
            "Lodging: 5 cp (bed) to 1 gp (private room with bath)",
            "Ale/Wine: 1 cp (mug) to 5 sp (fine bottle)",
            "Entertainment: Free nightly performances",
            "Hot bath: 2 cp"
        ]
    )
    
    # 9. Otari Fishery - Adventuring gear only
    print("\n[9/10] Generating Otari Fishery...")
    inventory = generate_merchant_inventory(
        equipment,
        categories=['adventuring'],
        num_common=15,
        num_uncommon=random.randint(1, 7)
    )
    write_merchant_with_header(
        "Otari Fishery",
        "Fresh fish and fishing supplies",
        "Lillia Dusklight (NG female human fisher 2)",
        "Fresh fish, fishing gear, and rope",
        inventory,
        services=[
            "Fresh fish: 1 cp - 5 sp depending on type",
            "Fishing lessons: 5 sp per hour",
            "Boat rental: 5 sp per day",
            "Net repair: 1 sp"
        ]
    )
    
    # 10. Dawnflower Library - Scrolls and magical items
    print("\n[10/10] Generating Dawnflower Library...")
    inventory = generate_merchant_inventory(
        equipment,
        categories=['magical', 'adventuring'],
        num_common=20,
        num_uncommon=random.randint(1, 7)
    )
    write_merchant_with_header(
        "Dawnflower Library",
        "Temple library and scriptorium",
        "Vandy Banderdash (LG female halfling cleric of Sarenrae 5)",
        "Religious texts, scrolls, and holy items",
        inventory,
        services=[
            "Spellcasting Services: Price varies by spell level (GM discretion)",
            "Healing: 1-20 gp depending on severity",
            "Remove curse/disease: 10-50 gp (GM discretion)",
            "Research assistance: Free for worshippers, 2 gp per day for others",
            "Blessings: Donation-based"
        ]
    )
    
    print("\n✓ All merchants generated!")
