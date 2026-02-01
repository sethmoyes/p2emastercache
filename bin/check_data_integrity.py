#!/usr/bin/env python3
"""
Data Integrity Checker for Pathfinder 2e JSON files
Validates equipment, creatures, and deities against Archives of Nethys using their Elasticsearch API
"""
import json
import random
import requests
import time
import re
import sys
from bs4 import BeautifulSoup
import urllib.parse

# Archives of Nethys Elasticsearch endpoint
AON_ELASTIC_URL = "https://elasticsearch.aonprd.com/aon/_search"

def load_json(filename):
    """Load JSON file"""
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def search_aon_elasticsearch(item_name, category='equipment'):
    """
    Search Archives of Nethys using their Elasticsearch API.
    This is the official way AoN loads data - much more reliable than scraping!
    """
    # Clean the name for search
    clean_name = re.sub(r'\([^)]*\)', '', item_name).strip()
    
    # Build Elasticsearch query
    query = {
        "size": 5,  # Get top 5 results
        "query": {
            "bool": {
                "must": [
                    {"match": {"category": category}},
                    {"match": {"name": clean_name}}
                ]
            }
        }
    }
    
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.post(AON_ELASTIC_URL, json=query, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return None
        
        data = response.json()
        hits = data.get('hits', {}).get('hits', [])
        
        if not hits:
            return None
        
        # Return the first (best) match
        return hits[0]['_source']
        
    except Exception as e:
        print(f"    Error searching Elasticsearch: {e}")
        return None

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
        
        # Extract level from "Item X" pattern (usually in h2 or span)
        level_match = re.search(r'Item\s+(\d+)', text, re.IGNORECASE)
        if level_match:
            data['level'] = int(level_match.group(1))
        
        # Extract price - look for "Price" followed by amount
        # Pattern: Price\n4 gp or Price 4 gp
        price_match = re.search(r'Price\s+(\d+\s*(?:gp|sp|cp))', text, re.IGNORECASE)
        if price_match:
            data['price'] = price_match.group(1).strip()
        elif re.search(r'Price\s+—', text):
            # Some items (like weapons) don't have prices on AoN
            data['price'] = None
        
        # Extract rarity from traits
        # Rarity traits are: Common, Uncommon, Rare, Unique
        # If no rarity is listed, it's Common
        rarity_match = re.search(r'\b(Uncommon|Rare|Unique)\b', text, re.IGNORECASE)
        if rarity_match:
            data['rarity'] = rarity_match.group(1).lower()
        else:
            # If no rarity trait found, assume common
            data['rarity'] = 'common'
        
        return data
        
    except Exception as e:
        print(f"    Error scraping: {e}")
        return None

def scrape_creature_data(url):
    """Scrape creature data from AoN page"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        data = {}
        
        content = soup.find('div', {'id': 'main'})
        if not content:
            return None
        
        # Extract level (usually "Creature X")
        level_match = re.search(r'Creature (\d+)', content.text)
        if level_match:
            data['level'] = int(level_match.group(1))
        
        # Extract HP
        hp_match = re.search(r'HP\s+(\d+)', content.text)
        if hp_match:
            data['hp'] = hp_match.group(1)
        
        # Extract AC
        ac_match = re.search(r'AC\s+(\d+)', content.text)
        if ac_match:
            data['ac'] = ac_match.group(1)
        
        return data
        
    except Exception as e:
        print(f"    Error scraping: {e}")
        return None

def check_equipment_item(item, verbose=True, replace=False):
    """Check a single equipment item against AoN using Elasticsearch API"""
    if verbose:
        print(f"\nChecking: {item['name']}")
        print(f"  Our data: Level {item['level']}, Price {item['price']}, Rarity {item['rarity']}")
    
    # Search AoN using Elasticsearch API
    aon_data = search_aon_elasticsearch(item['name'], 'equipment')
    if not aon_data:
        # Try weapon category
        aon_data = search_aon_elasticsearch(item['name'], 'weapon')
    if not aon_data:
        # Try armor category
        aon_data = search_aon_elasticsearch(item['name'], 'armor')
    
    if not aon_data:
        if verbose:
            print(f"  X Not found on AoN")
        return {'status': 'not_found', 'item': item['name'], 'updated': False}
    
    if verbose:
        print(f"  Found: {aon_data.get('name', 'Unknown')}")
    
    # Extract data from Elasticsearch response - use price_raw for proper formatting!
    aon_level = aon_data.get('level', 0)
    aon_price = aon_data.get('price_raw', '0 gp')  # Use price_raw instead of price!
    aon_rarity = aon_data.get('rarity', 'common').lower()
    aon_category = aon_data.get('category', 'equipment')
    aon_item_category = aon_data.get('item_category', '')
    aon_bulk = aon_data.get('bulk', 0)
    
    # Compare
    mismatches = []
    
    if aon_level != item['level']:
        mismatches.append(f"Level: ours={item['level']}, AoN={aon_level}")
    
    if aon_price and aon_price != item['price']:
        mismatches.append(f"Price: ours={item['price']}, AoN={aon_price}")
    
    if aon_rarity != item['rarity']:
        mismatches.append(f"Rarity: ours={item['rarity']}, AoN={aon_rarity}")
    
    if mismatches:
        if verbose:
            print(f"  ! Mismatches found:")
            for m in mismatches:
                print(f"    - {m}")
        
        # Update the item if replace flag is set
        updated = False
        if replace:
            item['level'] = aon_level
            item['price'] = aon_price
            item['rarity'] = aon_rarity
            item['category'] = aon_category
            item['item_category'] = aon_item_category
            item['bulk'] = aon_bulk
            
            # Add weapon-specific fields if it's a weapon
            if aon_category == 'weapon':
                item['damage'] = aon_data.get('damage', '')
                item['weapon_type'] = aon_data.get('weapon_type', '')
                item['weapon_category'] = aon_data.get('weapon_category', '')
                item['hands'] = aon_data.get('hands', '')
            
            # Add armor-specific fields if it's armor
            if aon_category == 'armor':
                item['ac'] = aon_data.get('ac', 0)
                item['armor_category'] = aon_data.get('armor_category', '')
                item['dex_cap'] = aon_data.get('dex_cap', 0)
            
            updated = True
            if verbose:
                print(f"  >> Updated with AoN data")
        
        return {'status': 'mismatch', 'item': item['name'], 'mismatches': mismatches, 'aon_data': aon_data, 'updated': updated}
    else:
        if verbose:
            print(f"  OK Data matches!")
        return {'status': 'match', 'item': item['name'], 'updated': False}

def check_creature_item(item, verbose=True, replace=False):
    """Check a single creature against AoN using Elasticsearch API"""
    if verbose:
        print(f"\nChecking: {item['name']}")
        print(f"  Our data: Level {item['level']}, HP {item['hp']}, AC {item['ac']}")
    
    aon_data = search_aon_elasticsearch(item['name'], 'creature')
    if not aon_data:
        if verbose:
            print(f"  X Not found on AoN")
        return {'status': 'not_found', 'item': item['name'], 'updated': False}
    
    if verbose:
        print(f"  Found: {aon_data.get('name', 'Unknown')}")
    
    # Extract data from Elasticsearch response
    aon_level = aon_data.get('level', 0)
    aon_hp = aon_data.get('hp', 0)
    aon_ac = aon_data.get('ac', 0)
    
    mismatches = []
    
    if str(aon_level) != str(item['level']):
        mismatches.append(f"Level: ours={item['level']}, AoN={aon_level}")
    
    if str(aon_hp) != str(item['hp']):
        mismatches.append(f"HP: ours={item['hp']}, AoN={aon_hp}")
    
    if str(aon_ac) != str(item['ac']):
        mismatches.append(f"AC: ours={item['ac']}, AoN={aon_ac}")
    
    if mismatches:
        if verbose:
            print(f"  ! Mismatches found:")
            for m in mismatches:
                print(f"    - {m}")
        
        # Update the item if replace flag is set
        updated = False
        if replace:
            item['level'] = aon_level
            item['hp'] = aon_hp
            item['ac'] = aon_ac
            updated = True
            if verbose:
                print(f"  >> Updated with AoN data")
        
        return {'status': 'mismatch', 'item': item['name'], 'mismatches': mismatches, 'aon_data': aon_data, 'updated': updated}
    else:
        if verbose:
            print(f"  OK Data matches!")
        return {'status': 'match', 'item': item['name'], 'updated': False}

def main(num_checks=10, data_type='equipment', replace=False):
    """Main integrity check function"""
    print(f"Data Integrity Checker")
    print(f"=" * 60)
    
    # Handle "all" option
    check_all = False
    if isinstance(num_checks, str) and num_checks.lower() == 'all':
        check_all = True
        print(f"Checking ALL {data_type} items")
    else:
        print(f"Checking {num_checks} random {data_type} items")
    
    if replace:
        print(f"REPLACE MODE: Will update mismatched items with AoN data")
        print(f"CLEANUP MODE: Will delete items not found on AoN")
    
    print()
    
    # Load data
    if data_type == 'equipment':
        filename = 'etc/equipment.json'
        data = load_json(filename)
        check_func = check_equipment_item
    elif data_type == 'creatures':
        filename = 'etc/creatures.json'
        data = load_json(filename)
        check_func = check_creature_item
    else:
        print(f"Unknown data type: {data_type}")
        return
    
    print(f"Loaded {len(data)} items from JSON\n")
    
    # Select items to check
    if check_all:
        sample = data
        num_checks = len(data)
    else:
        sample = random.sample(data, min(num_checks, len(data)))
    
    results = []
    junk_items = []  # Track items to delete
    
    for idx, item in enumerate(sample, 1):
        print(f"\n[{idx}/{num_checks}]", end=" ")
        result = check_func(item, verbose=True, replace=replace)
        results.append(result)
        
        # Mark items not found for deletion
        if result['status'] == 'not_found' and replace:
            junk_items.append(item)
        
        # Small delay to be respectful to the API
        time.sleep(0.5)
    
    # Remove junk items from data if in replace mode
    if replace and junk_items:
        print(f"\n\nRemoving {len(junk_items)} junk items not found on AoN...")
        for junk in junk_items:
            if junk in data:
                data.remove(junk)
        
        # Log junk items
        with open('junk_items.log', 'w', encoding='utf-8') as f:
            f.write(f"Junk Items Removed - {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"=" * 60 + "\n\n")
            for item in junk_items:
                f.write(f"Name: {item.get('name', 'Unknown')}\n")
                f.write(f"  Level: {item.get('level', 'N/A')}\n")
                f.write(f"  Price: {item.get('price', 'N/A')}\n")
                f.write(f"  Rarity: {item.get('rarity', 'N/A')}\n")
                f.write(f"  Category: {item.get('category', 'N/A')}\n")
                f.write("\n")
        print(f"Logged junk items to junk_items.log")
    
    # Summary
    print(f"\n\n{'=' * 60}")
    print("SUMMARY")
    print(f"{'=' * 60}")
    
    matches = sum(1 for r in results if r['status'] == 'match')
    mismatches = sum(1 for r in results if r['status'] == 'mismatch')
    not_found = sum(1 for r in results if r['status'] == 'not_found')
    scrape_failed = sum(1 for r in results if r['status'] == 'scrape_failed')
    updated = sum(1 for r in results if r.get('updated', False))
    
    print(f"Total checked: {len(results)}")
    print(f"  OK Matches: {matches}")
    print(f"  ! Mismatches: {mismatches}")
    print(f"  X Not found: {not_found}")
    print(f"  ! Scrape failed: {scrape_failed}")
    
    if replace and updated > 0:
        print(f"  >> Updated: {updated}")
    
    if replace and junk_items:
        print(f"  >> Deleted: {len(junk_items)}")
    
    if mismatches > 0 and not replace:
        print(f"\nItems with mismatches:")
        for r in results:
            if r['status'] == 'mismatch':
                print(f"  - {r['item']}")
                for m in r['mismatches']:
                    print(f"      {m}")
    
    accuracy = (matches / len(results) * 100) if results else 0
    print(f"\nAccuracy: {accuracy:.1f}%")
    
    if replace:
        print(f"Final item count: {len(data)} (removed {len(junk_items)} junk items)")
    
    print(f"{'=' * 60}")
    
    # Save updated data if replace mode
    if replace and (updated > 0 or junk_items):
        print(f"\nSaving updated data to {filename}...")
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Saved! {updated} items updated, {len(junk_items)} items removed.")
    elif replace and updated == 0 and not junk_items:
        print(f"\nNo items needed updating or removal.")

if __name__ == "__main__":
    # Parse command line arguments
    num_checks = 10
    data_type = 'equipment'
    replace = False
    
    if len(sys.argv) > 1:
        # Check for "all" option
        if sys.argv[1].lower() == 'all':
            num_checks = 'all'
        else:
            try:
                num_checks = int(sys.argv[1])
            except:
                print("Usage: python check_data_integrity.py [num_checks|all] [data_type] [--replace]")
                print("  num_checks: number of items to check or 'all' (default: 10)")
                print("  data_type: 'equipment' or 'creatures' (default: equipment)")
                print("  --replace: update mismatched items with AoN data")
                print("\nExamples:")
                print("  python check_data_integrity.py 10 equipment")
                print("  python check_data_integrity.py all equipment --replace")
                print("  python check_data_integrity.py 50 creatures")
                sys.exit(1)
    
    if len(sys.argv) > 2:
        data_type = sys.argv[2]
    
    # Check for --replace flag
    if '--replace' in sys.argv:
        replace = True
    
    main(num_checks, data_type, replace)
