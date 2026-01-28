#!/usr/bin/env python3
"""
Fix item images with known Archives of Nethys URLs
"""
import re

# Manual mapping of common items to their correct image URLs
ITEM_IMAGE_MAP = {
    # Weapons
    'longsword': 'https://2e.aonprd.com/Images/Weapons/Longsword.png',
    'shortsword': 'https://2e.aonprd.com/Images/Weapons/Shortsword.png',
    'battleaxe': 'https://2e.aonprd.com/Images/Weapons/BattleAxe.png',
    'warhammer': 'https://2e.aonprd.com/Images/Weapons/Warhammer.png',
    'spear': 'https://2e.aonprd.com/Images/Weapons/Spear.png',
    'shortbow': 'https://2e.aonprd.com/Images/Weapons/Shortbow.png',
    'crossbow': 'https://2e.aonprd.com/Images/Weapons/HeavyCrossbow.png',
    'dagger': 'https://2e.aonprd.com/Images/Weapons/Dagger.png',
    'club': 'https://2e.aonprd.com/Images/Weapons/Club.png',
    'staff': 'https://2e.aonprd.com/Images/Weapons/Staff.png',
    'arrows': 'https://2e.aonprd.com/Images/Weapons/Arrows.png',
    'bolts': 'https://2e.aonprd.com/Images/Weapons/Bolts.png',
    'dogslicer': 'https://2e.aonprd.com/Images/Weapons/Dogslicer.png',
    'spiked chain': 'https://2e.aonprd.com/Images/Weapons/SpikedChain.png',
    'bladed scarf': 'https://2e.aonprd.com/Images/Weapons/BladedScarf.png',
    
    # Armor
    'leather armor': 'https://2e.aonprd.com/Images/Armor/LeatherArmor.png',
    'studded leather armor': 'https://2e.aonprd.com/Images/Armor/StuddedLeatherArmor.png',
    'chain shirt': 'https://2e.aonprd.com/Images/Armor/ChainShirt.png',
    'hide armor': 'https://2e.aonprd.com/Images/Armor/HideArmor.png',
    'scale mail': 'https://2e.aonprd.com/Images/Armor/ScaleMail.png',
    'chain mail': 'https://2e.aonprd.com/Images/Armor/ChainMail.png',
    'breastplate': 'https://2e.aonprd.com/Images/Armor/Breastplate.png',
    'wooden shield': 'https://2e.aonprd.com/Images/Armor/WoodenShield.png',
    'steel shield': 'https://2e.aonprd.com/Images/Armor/SteelShield.png',
    'buckler': 'https://2e.aonprd.com/Images/Armor/Buckler.png',
    'padded armor': 'https://2e.aonprd.com/Images/Armor/PaddedArmor.png',
    'armored coat': 'https://2e.aonprd.com/Images/Armor/ArmoredCoat.png',
    'fortress shield': 'https://2e.aonprd.com/Images/Armor/FortressShield.png',
    'breastplate of command': 'https://2e.aonprd.com/Images/Armor/BreastplateOfCommand.png',
    
    # Alchemical Items
    "alchemist's fire": 'https://2e.aonprd.com/Images/Equipment/AlchemistsFire.png',
    'acid flask': 'https://2e.aonprd.com/Images/Equipment/AcidFlask.png',
    'tanglefoot bag': 'https://2e.aonprd.com/Images/Equipment/TanglefootBag.png',
    'smokestick': 'https://2e.aonprd.com/Images/Equipment/Smokestick.png',
    'thunderstone': 'https://2e.aonprd.com/Images/Equipment/Thunderstone.png',
    'antidote': 'https://2e.aonprd.com/Images/Equipment/Antidote.png',
    'antiplague': 'https://2e.aonprd.com/Images/Equipment/Antiplague.png',
    'elixir of life': 'https://2e.aonprd.com/Images/Equipment/ElixirOfLife.png',
    'healing potion': 'https://2e.aonprd.com/Images/Equipment/HealingPotion.png',
    'bottled lightning': 'https://2e.aonprd.com/Images/Equipment/BottledLightning.png',
    
    # Adventuring Gear
    'backpack': 'https://2e.aonprd.com/Images/Equipment/Backpack.png',
    'bedroll': 'https://2e.aonprd.com/Images/Equipment/Bedroll.png',
    'rope': 'https://2e.aonprd.com/Images/Equipment/Rope.png',
    'grappling hook': 'https://2e.aonprd.com/Images/Equipment/GrapplingHook.png',
    'torch': 'https://2e.aonprd.com/Images/Equipment/Torch.png',
    'waterskin': 'https://2e.aonprd.com/Images/Equipment/Waterskin.png',
    'rations': 'https://2e.aonprd.com/Images/Equipment/Rations.png',
    'flint and steel': 'https://2e.aonprd.com/Images/Equipment/FlintAndSteel.png',
    'chalk': 'https://2e.aonprd.com/Images/Equipment/Chalk.png',
    'piton': 'https://2e.aonprd.com/Images/Equipment/Piton.png',
    'climbing kit': 'https://2e.aonprd.com/Images/Equipment/ClimbingKit.png',
    'lantern': 'https://2e.aonprd.com/Images/Equipment/Lantern.png',
    'oil': 'https://2e.aonprd.com/Images/Equipment/Oil.png',
    'tent': 'https://2e.aonprd.com/Images/Equipment/Tent.png',
    'fishing tackle': 'https://2e.aonprd.com/Images/Equipment/FishingTackle.png',
    "healer's tools": 'https://2e.aonprd.com/Images/Equipment/HealersTools.png',
    "explorer's clothing": 'https://2e.aonprd.com/Images/Equipment/ExplorersClothing.png',
    'winter clothing': 'https://2e.aonprd.com/Images/Equipment/WinterClothing.png',
    
    # Scrolls and Magic Items
    'scroll': 'https://2e.aonprd.com/Images/Equipment/Scroll.png',
    'wand': 'https://2e.aonprd.com/Images/Equipment/Wand.png',
    'holy water': 'https://2e.aonprd.com/Images/Equipment/HolyWater.png',
    'silver weapon blanch': 'https://2e.aonprd.com/Images/Equipment/WeaponBlanch.png',
    'cold iron weapon blanch': 'https://2e.aonprd.com/Images/Equipment/WeaponBlanch.png',
    'religious symbol': 'https://2e.aonprd.com/Images/Equipment/ReligiousSymbol.png',
    'book': 'https://2e.aonprd.com/Images/Equipment/Book.png',
    'writing set': 'https://2e.aonprd.com/Images/Equipment/WritingSet.png',
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
    
    # Default fallback - try to construct a generic URL
    clean_name = normalized.replace(' ', '')
    clean_name = ''.join(c for c in clean_name if c.isalnum())
    
    # Guess category
    if any(word in normalized for word in ['sword', 'axe', 'hammer', 'spear', 'bow', 'dagger', 'weapon', 'arrow', 'bolt', 'chain', 'staff', 'club']):
        return f'https://2e.aonprd.com/Images/Weapons/{clean_name.title()}.png'
    elif any(word in normalized for word in ['armor', 'shield', 'mail', 'breastplate', 'leather', 'hide', 'scale', 'buckler']):
        return f'https://2e.aonprd.com/Images/Armor/{clean_name.title()}.png'
    else:
        return f'https://2e.aonprd.com/Images/Equipment/{clean_name.title()}.png'

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
