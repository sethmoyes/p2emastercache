#!/usr/bin/env python3
"""
Add image links to merchant inventories
"""
import re

def item_name_to_image_url(item_name):
    """Convert item name to likely Archives of Nethys image URL"""
    # Remove parentheses content and clean up
    clean_name = re.sub(r'\([^)]*\)', '', item_name).strip()
    
    # Replace spaces with underscores
    url_name = clean_name.replace(' ', '_')
    
    # Remove special characters except underscores
    url_name = re.sub(r'[^a-zA-Z0-9_]', '', url_name)
    
    # Construct URL
    base_url = "https://2e.aonprd.com/Images/"
    
    # Determine category based on item name
    if any(word in item_name.lower() for word in ['sword', 'axe', 'hammer', 'spear', 'bow', 'crossbow', 'dagger', 'weapon', 'arrow', 'bolt', 'scarf', 'chain']):
        category = "Weapons/"
    elif any(word in item_name.lower() for word in ['armor', 'shield', 'mail', 'breastplate', 'leather', 'hide', 'scale', 'buckler']):
        category = "Armor/"
    elif any(word in item_name.lower() for word in ['potion', 'elixir', 'flask', 'alchemist', 'acid', 'fire', 'lightning', 'smoke', 'thunder', 'antidote', 'antiplague', 'tanglefoot']):
        category = "Treasure/"
    elif any(word in item_name.lower() for word in ['scroll', 'wand', 'holy water', 'blanch', 'symbol']):
        category = "Treasure/"
    else:
        category = "Equipment/"
    
    return f"{base_url}{category}{url_name}.webp"

def add_images_to_markdown(input_file, output_file):
    """Add image URLs to merchant inventory markdown"""
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    output_lines = []
    in_table = False
    
    for line in lines:
        # Check if we're in a table
        if '|------|-------|-------|' in line:
            # Add Image column to header separator
            output_lines.append('|------|-------|-------|-------|\n')
            in_table = True
            continue
        
        # Check for table header
        if '| Item | Level | Price |' in line:
            output_lines.append('| Item | Level | Price | Image |\n')
            continue
        
        # Process table rows
        if in_table and line.startswith('|') and not line.startswith('|---'):
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 4 and parts[1]:  # Has item name
                item_name = parts[1]
                level = parts[2]
                price = parts[3]
                
                # Generate image URL
                image_url = item_name_to_image_url(item_name)
                
                # Reconstruct line with image
                output_lines.append(f"| {item_name} | {level} | {price} | ![{item_name}]({image_url}) |\n")
                continue
        
        # Check if we're leaving a table
        if in_table and (line.startswith('#') or line.startswith('*') or line.strip() == '---'):
            in_table = False
        
        output_lines.append(line)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(output_lines)
    
    print(f"Updated merchant inventories with images: {output_file}")

if __name__ == "__main__":
    add_images_to_markdown("merchant_inventories.md", "merchant_inventories_with_images.md")
    print("\nNote: Image URLs are constructed based on Archives of Nethys naming conventions.")
    print("Some images may not exist. You can manually verify and update URLs as needed.")
