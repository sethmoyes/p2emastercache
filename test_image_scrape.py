#!/usr/bin/env python3
import requests
import re
import urllib.parse

def test_image_scrape(item_name):
    """Test image scraping for a single item"""
    # Clean name
    clean_name = re.sub(r'\([^)]*\)', '', item_name)
    clean_name = re.split(r'\d', clean_name)[0]
    clean_name = re.sub(r'[^a-zA-Z\s\'-]', '', clean_name)
    clean_name = ' '.join(clean_name.split()).strip()
    
    print(f"Original: {item_name}")
    print(f"Cleaned: {clean_name}")
    
    # Build search query
    search_query = f"2e.aonprd.com: {clean_name}"
    encoded_query = urllib.parse.quote_plus(search_query)
    search_url = f"https://www.google.com/search?q={encoded_query}&tbm=isch"
    
    print(f"Search URL: {search_url}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        print(f"Response status: {response.status_code}")
        
        # Look for "ou" pattern
        img_pattern = r'"ou":"(https?://[^"]+)"'
        matches = re.findall(img_pattern, response.text)
        
        print(f"Found {len(matches)} image URLs")
        
        if matches:
            # Filter for AoN images
            aon_matches = [m for m in matches if '2e.aonprd.com' in m.lower()]
            print(f"Found {len(aon_matches)} AoN images")
            
            if aon_matches:
                print(f"First AoN image: {aon_matches[0]}")
                return aon_matches[0]
            else:
                print(f"First image (any): {matches[0]}")
                return matches[0]
        
        # Try fallback pattern
        img_pattern2 = r'https?://2e\.aonprd\.com/[^\s<>"]+?\.(?:jpg|jpeg|png|webp|gif)'
        matches2 = re.findall(img_pattern2, response.text, re.IGNORECASE)
        
        if matches2:
            print(f"Fallback found: {matches2[0]}")
            return matches2[0]
        
        print("No images found")
        return None
        
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    # Test with a few items
    test_items = [
        "Crossbow",
        "Leather Armor",
        "Longsword",
        "Healing Potion (Lesser)"
    ]
    
    for item in test_items:
        print("\n" + "="*60)
        result = test_image_scrape(item)
        print(f"Result: {result}")
