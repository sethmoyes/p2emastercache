#!/usr/bin/env python3
import requests
import re

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

def try_direct_aon_image(item_name):
    """Try to construct direct AoN image URL"""
    clean_name = clean_item_name(item_name)
    
    # Try common AoN image paths
    base_url = "https://2e.aonprd.com/Images/"
    
    # Create URL-safe name: replace spaces with underscores, remove apostrophes, capitalize words
    url_name = clean_name.replace("'", "").replace(" ", "_")
    # Capitalize each word
    url_name = "_".join(word.capitalize() for word in url_name.split("_"))
    
    print(f"  Clean name: {clean_name}")
    print(f"  URL name: {url_name}")
    
    # Try different category paths
    categories = [
        f"Weapons/{url_name}.webp",
        f"Armor/{url_name}.webp",
        f"Equipment/{url_name}.webp",
        f"Items/{url_name}.webp",
        f"Treasure/{url_name}.webp",
    ]
    
    for category in categories:
        url = base_url + category
        print(f"  Trying: {url}", end="... ")
        try:
            response = requests.head(url, timeout=2)
            if response.status_code == 200:
                print("✓ FOUND!")
                return url
            else:
                print(f"✗ ({response.status_code})")
        except Exception as e:
            print(f"✗ (error)")
    
    return None

# Test items
test_items = [
    "Crossbow",
    "Leather Armor",
    "Longsword",
    "Healing Potion (Lesser)",
    "Buckler"
]

for item in test_items:
    print(f"\nTesting: {item}")
    result = try_direct_aon_image(item)
    if result:
        print(f"SUCCESS: {result}")
    else:
        print(f"FAILED: No image found")
