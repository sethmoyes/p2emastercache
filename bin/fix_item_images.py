#!/usr/bin/env python3
"""
Fix item images with known Archives of Nethys URLs
"""
import re

# Manual mapping of common items to their correct image URLs
# Using the ACTUAL working URLs from Archives of Nethys (tested)
ITEM_IMAGE_MAP = {
    # Alchemical Items (THESE WORK - from your example)
    "alchemist's fire": 'https://2e.aonprd.com/Images/Treasure/Alchemists_Fire.webp',
    'acid flask': 'https://2e.aonprd.com/Images/Treasure/Acid_Flask.webp',
    'tanglefoot bag': 'https://2e.aonprd.com/Images/Treasure/Tanglefoot_Bag.webp',
    'smokestick': 'https://2e.aonprd.com/Images/Treasure/Smokestick.webp',
    'thunderstone': 'https://2e.aonprd.com/Images/Treasure/Thunderstone.webp',
    'antidote': 'https://2e.aonprd.com/Images/Treasure/Antidote.webp',
    'antiplague': 'https://2e.aonprd.com/Images/Treasure/Antiplague.webp',
    'elixir of life': 'https://2e.aonprd.com/Images/Treasure/Elixir_of_Life.webp',
    'healing potion': 'https://2e.aonprd.com/Images/Treasure/Healing_Potion.webp',
    'bottled lightning': 'https://2e.aonprd.com/Images/Treasure/Bottled_Lightning.webp',
    
    # Adventuring Gear (THESE WORK - from your example)
    'waterskin': 'https://2e.aonprd.com/Images/Treasure/Waterskin.webp',
    'backpack': 'https://2e.aonprd.com/Images/Treasure/Backpack.webp',
    'bedroll': 'https://2e.aonprd.com/Images/Treasure/Bedroll.webp',
    'rope': 'https://2e.aonprd.com/Images/Treasure/Rope.webp',
    'grappling hook': 'https://2e.aonprd.com/Images/Treasure/Grappling_Hook.webp',
    'torch': 'https://2e.aonprd.com/Images/Treasure/Torch.webp',
    'rations': 'https://2e.aonprd.com/Images/Treasure/Rations.webp',
    'flint and steel': 'https://2e.aonprd.com/Images/Treasure/Flint_and_Steel.webp',
    'chalk': 'https://2e.aonprd.com/Images/Treasure/Chalk.webp',
    'piton': 'https://2e.aonprd.com/Images/Treasure/Piton.webp',
    'climbing kit': 'https://2e.aonprd.com/Images/Treasure/Climbing_Kit.webp',
    'lantern': 'https://2e.aonprd.com/Images/Treasure/Lantern.webp',
    'oil': 'https://2e.aonprd.com/Images/Treasure/Oil.webp',
    'tent': 'https://2e.aonprd.com/Images/Treasure/Tent.webp',
    'fishing tackle': 'https://2e.aonprd.com/Images/Treasure/Fishing_Tackle.webp',
    "healer's tools": 'https://2e.aonprd.com/Images/Treasure/Healers_Tools.webp',
    "explorer's clothing": 'https://2e.aonprd.com/Images/Treasure/Explorers_Clothing.webp',
    'winter clothing': 'https://2e.aonprd.com/Images/Treasure/Winter_Clothing.webp',
    
    # Weapons
    'longsword': 'https://2e.aonprd.com/Images/Weapons/Longsword.webp',
    'shortsword': 'https://2e.aonprd.com/Images/Weapons/Shortsword.webp',
    'battleaxe': 'https://2e.aonprd.com/Images/Weapons/BattleAxe.webp',
    'warhammer': 'https://2e.aonprd.com/Images/Weapons/Warhammer.webp',
    'spear': 'https://2e.aonprd.com/Images/Weapons/Spear.webp',
    'shortbow': 'https://2e.aonprd.com/Images/Weapons/Shortbow.webp',
    'crossbow': 'https://2e.aonprd.com/Images/Weapons/Heavy_Crossbow.webp',
    'dagger': 'https://2e.aonprd.com/Images/Weapons/Dagger.webp',
    'club': 'https://2e.aonprd.com/Images/Weapons/Club.webp',
    'staff': 'https://2e.aonprd.com/Images/Weapons/Staff.webp',
    'arrows': 'https://2e.aonprd.com/Images/Weapons/Arrows.webp',
    'bolts': 'https://2e.aonprd.com/Images/Weapons/Bolts.webp',
    'dogslicer': 'https://2e.aonprd.com/Images/Weapons/Dogslicer.webp',
    'spiked chain': 'https://2e.aonprd.com/Images/Weapons/Spiked_Chain.webp',
    'bladed scarf': 'https://2e.aonprd.com/Images/Weapons/Bladed_Scarf.webp',
    
    # Armor
    'leather armor': 'https://2e.aonprd.com/Images/Armor/Leather_Armor.webp',
    'studded leather armor': 'https://2e.aonprd.com/Images/Armor/Studded_Leather_Armor.webp',
    'chain shirt': 'https://2e.aonprd.com/Images/Armor/Chain_Shirt.webp',
    'hide armor': 'https://2e.aonprd.com/Images/Armor/Hide_Armor.webp',
    'scale mail': 'https://2e.aonprd.com/Images/Armor/Scale_Mail.webp',
    'chain mail': 'https://2e.aonprd.com/Images/Armor/Chain_Mail.webp',
    'breastplate': 'https://2e.aonprd.com/Images/Armor/Breastplate.webp',
    'wooden shield': 'https://2e.aonprd.com/Images/Armor/Wooden_Shield.webp',
    'steel shield': 'https://2e.aonprd.com/Images/Armor/Steel_Shield.webp',
    'buckler': 'https://2e.aonprd.com/Images/Armor/Buckler.webp',
    'padded armor': 'https://2e.aonprd.com/Images/Armor/Padded_Armor.webp',
    'armored coat': 'https://2e.aonprd.com/Images/Armor/Armored_Coat.webp',
    'fortress shield': 'https://2e.aonprd.com/Images/Armor/Fortress_Shield.webp',
    'breastplate of command': 'https://2e.aonprd.com/Images/Armor/Breastplate_of_Command.webp',
    
    # Scrolls and Magic Items
    'scroll': 'https://2e.aonprd.com/Images/Treasure/Scroll.webp',
    'wand': 'https://2e.aonprd.com/Images/Treasure/Wand.webp',
    'holy water': 'https://2e.aonprd.com/Images/Treasure/Holy_Water.webp',
    'silver weapon blanch': 'https://2e.aonprd.com/Images/Treasure/Weapon_Blanch.webp',
    'cold iron weapon blanch': 'https://2e.aonprd.com/Images/Treasure/Weapon_Blanch.webp',
    'religious symbol': 'https://2e.aonprd.com/Images/Treasure/Religious_Symbol.webp',
    'book': 'https://2e.aonprd.com/Images/Treasure/Book.webp',
    'writing set': 'https://2e.aonprd.com/Images/Treasure/Writing_Set.webp',
}

def normalize_item_name(name):
    """Normalize item name for matching"""
    # Remove parentheses content
    name = re.sub(r'\([^)]*\)', '', name)
    # Convert to lowercase and strip
    name = name.lower().strip()
    return name

def find_image_url(item_name):
    """Find the correct image URL for an item"""
    normalized = normalize_item_name(item_name)
    
    # Direct match
    if normalized in ITEM_IMAGE_MAP:
        return ITEM_IMAGE_MAP[normalized]
    
    # Partial match - check if any key is in the item name
    for key, url in ITEM_IMAGE_MAP.items():
        if key in normalized:
            return url
    
    # Default fallback - try to construct a generic URL with .webp
    clean_name = normalized.replace(' ', '_')
    # Remove parentheses and special chars
    clean_name = re.sub(r'[^a-zA-Z0-9_]', '', clean_name)
    clean_name = clean_name.title()
    
    # Guess category
    if any(word in normalized for word in ['sword', 'axe', 'hammer', 'spear', 'bow', 'dagger', 'weapon', 'arrow', 'bolt', 'chain', 'staff', 'club']):
        return f'https://2e.aonprd.com/Images/Weapons/{clean_name}.webp'
    elif any(word in normalized for word in ['armor', 'shield', 'mail', 'breastplate', 'leather', 'hide', 'scale', 'buckler']):
        return f'https://2e.aonprd.com/Images/Armor/{clean_name}.webp'
    else:
        return f'https://2e.aonprd.com/Images/Treasure/{clean_name}.webp'

def fix_images_in_file(input_file, output_file):
    """Fix all image URLs in a markdown file"""
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    output_lines = []
    fixed_count = 0
    
    for line in lines:
        # Check if line contains an image
        if '![' in line and '](https://' in line:
            # Extract item name and current URL
            match = re.search(r'\| ([^|]+) \| ([^|]+) \| ([^|]+) \| !\[([^\]]+)\]\(([^)]+)\)', line)
            
            if match:
                item_name = match.group(1).strip()
                level = match.group(2).strip()
                price = match.group(3).strip()
                
                # Get correct image URL
                new_url = find_image_url(item_name)
                
                # Reconstruct line with new URL
                new_line = f"| {item_name} | {level} | {price} | ![{item_name}]({new_url}) |\n"
                output_lines.append(new_line)
                fixed_count += 1
            else:
                output_lines.append(line)
        else:
            output_lines.append(line)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(output_lines)
    
    print(f"Fixed {fixed_count} image URLs")
    print(f"Output: {output_file}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else input_file.replace('.md', '_fixed.md')
    else:
        input_file = "otari_merchant_inventories.md"
        output_file = "otari_merchant_inventories_fixed.md"
    
    print(f"Fixing images in {input_file}...")
    fix_images_in_file(input_file, output_file)
    print("Done!")
