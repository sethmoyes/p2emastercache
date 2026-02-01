#!/usr/bin/env python3
"""
Test scraping from a specific AoN URL
This is useful for verifying the scraping logic works correctly
"""
import sys
import requests
from bs4 import BeautifulSoup
import re

def scrape_equipment_data(url):
    """Scrape equipment data from AoN page"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        data = {}
        
        # Get the main content
        main = soup.find('div', {'id': 'main'})
        if not main:
            return None
        
        text = main.get_text()
        
        # Extract level from "Item X" pattern
        level_match = re.search(r'Item\s+(\d+)', text, re.IGNORECASE)
        if level_match:
            data['level'] = int(level_match.group(1))
        
        # Extract price
        price_match = re.search(r'Price\s+(\d+\s*(?:gp|sp|cp))', text, re.IGNORECASE)
        if price_match:
            data['price'] = price_match.group(1).strip()
        elif re.search(r'Price\s+—', text):
            data['price'] = None
        
        # Extract rarity
        rarity_match = re.search(r'\b(Uncommon|Rare|Unique)\b', text, re.IGNORECASE)
        if rarity_match:
            data['rarity'] = rarity_match.group(1).lower()
        else:
            data['rarity'] = 'common'
        
        # Get item name from title
        title = soup.find('title')
        if title:
            name_match = re.search(r'^([^-]+)', title.get_text())
            if name_match:
                data['name'] = name_match.group(1).strip()
        
        return data
        
    except Exception as e:
        print(f"Error scraping: {e}")
        return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python test_aon_url.py <URL>")
        print("\nExamples:")
        print("  python test_aon_url.py https://2e.aonprd.com/Equipment.aspx?ID=186")
        print("  python test_aon_url.py https://2e.aonprd.com/Weapons.aspx?ID=1")
        print("  python test_aon_url.py https://2e.aonprd.com/Armor.aspx?ID=4")
        sys.exit(1)
    
    url = sys.argv[1]
    
    print(f"Testing URL: {url}\n")
    
    data = scrape_equipment_data(url)
    
    if data:
        print("Successfully scraped data:")
        print(f"  Name: {data.get('name', 'N/A')}")
        print(f"  Level: {data.get('level', 'N/A')}")
        print(f"  Price: {data.get('price', 'N/A')}")
        print(f"  Rarity: {data.get('rarity', 'N/A')}")
    else:
        print("Failed to scrape data")

if __name__ == "__main__":
    main()
