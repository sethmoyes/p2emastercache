#!/usr/bin/env python3
"""
Verify image URLs and fix broken ones with web search
"""
import re
import requests
import time
from urllib.parse import quote_plus

def check_image_exists(url):
    """Check if an image URL is valid"""
    try:
        response = requests.head(url, timeout=5, allow_redirects=True)
        return response.status_code == 200
    except:
        return False

def search_google_images(item_name):
    """Search Google Images for item and return first result URL"""
    # Add p2e and dnd to search query
    search_query = f"{item_name} p2e dnd pathfinder 2e"
    encoded_query = quote_plus(search_query)
    
    # Use Google Images search
    search_url = f"https://www.google.com/search?q={encoded_query}&tbm=isch"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        
        # Extract first image URL from response
        # Look for image URLs in the HTML
        img_pattern = r'"ou":"(https?://[^"]+)"'
        matches = re.findall(img_pattern, response.text)
        
        if matches:
            # Return first match
            return matches[0]
        
        # Fallback: try to find any image URL
        img_pattern2 = r'https?://[^\s<>"]+?\.(?:jpg|jpeg|png|webp|gif)'
        matches2 = re.findall(img_pattern2, response.text)
        
        if matches2:
            return matches2[0]
            
    except Exception as e:
        print(f"  Error searching for {item_name}: {e}")
    
    return None

def try_alternative_aon_urls(item_name):
    """Try different Archives of Nethys URL patterns"""
    clean_name = re.sub(r'\([^)]*\)', '', item_name).strip()
    url_name = clean_name.replace(' ', '_')
    url_name = re.sub(r'[^a-zA-Z0-9_]', '', url_name)
    
    base_url = "https://2e.aonprd.com/Images/"
    
    # Try different category paths
    categories = [
        "Treasure/",
        "Weapons/",
        "Armor/",
        "Equipment/",
        "Items/",
        "Adventuring_Gear/",
    ]
    
    for category in categories:
        url = f"{base_url}{category}{url_name}.webp"
        if check_image_exists(url):
            return url
    
    return None

def verify_and_fix_images(input_file, output_file):
    """Verify all image URLs and fix broken ones"""
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    output_lines = []
    fixed_count = 0
    failed_count = 0
    
    for i, line in enumerate(lines):
        # Check if line contains an image
        if '![' in line and '](https://' in line:
            # Extract item name and current URL
            match = re.search(r'\| ([^|]+) \| ([^|]+) \| ([^|]+) \| !\[([^\]]+)\]\(([^)]+)\)', line)
            
            if match:
                item_name = match.group(1).strip()
                level = match.group(2).strip()
                price = match.group(3).strip()
                current_url = match.group(5).strip()
                
                print(f"Checking: {item_name}...", end=' ')
                
                # Check if current URL works
                if check_image_exists(current_url):
                    print("✓ OK")
                    output_lines.append(line)
                else:
                    print("✗ Broken, searching for alternative...")
                    
                    # Try alternative AoN URLs first
                    new_url = try_alternative_aon_urls(item_name)
                    
                    # If still not found, try Google Images
                    if not new_url:
                        print(f"  Searching Google Images for: {item_name}")
                        new_url = search_google_images(item_name)
                        time.sleep(1)  # Be nice to Google
                    
                    if new_url:
                        print(f"  ✓ Found: {new_url}")
                        new_line = f"| {item_name} | {level} | {price} | ![{item_name}]({new_url}) |\n"
                        output_lines.append(new_line)
                        fixed_count += 1
                    else:
                        print(f"  ✗ No image found, keeping original")
                        output_lines.append(line)
                        failed_count += 1
            else:
                output_lines.append(line)
        else:
            output_lines.append(line)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(output_lines)
    
    print(f"\n{'='*60}")
    print(f"Verification complete!")
    print(f"Fixed: {fixed_count} images")
    print(f"Failed: {failed_count} images")
    print(f"Output: {output_file}")
    print(f"{'='*60}")

if __name__ == "__main__":
    print("Verifying and fixing image URLs...")
    print("This may take a few minutes...\n")
    
    verify_and_fix_images("merchant_inventories.md", "merchant_inventories_verified.md")
    
    print("\nDone! Review merchant_inventories_verified.md")
    print("If satisfied, rename it to merchant_inventories.md")
