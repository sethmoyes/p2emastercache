#!/usr/bin/env python3
"""
Test price fetching for Greater/Lesser items
"""
import json
import requests

AON_ELASTIC_URL = "https://elasticsearch.aonprd.com/aon/_search"

def search_item(item_name):
    """Search for an item and return its data"""
    query = {
        "size": 1,
        "query": {
            "bool": {
                "must": [
                    {"match": {"category": "equipment"}},
                    {"match": {"name": item_name}}
                ]
            }
        }
    }
    
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0'
    }
    
    response = requests.post(AON_ELASTIC_URL, json=query, headers=headers, timeout=10)
    
    if response.status_code != 200:
        return None
    
    data = response.json()
    hits = data.get('hits', {}).get('hits', [])
    
    if not hits:
        return None
    
    return hits[0]['_source']

# Test items
test_items = [
    "Healing Potion (Lesser)",
    "Healing Potion (Greater)",
    "Striking Rune",
    "Greater Striking Rune",
    "Elixir of Life (Minor)",
    "Elixir of Life (Major)"
]

print("Testing item price fetching from Archives of Nethys")
print("=" * 70)

for item_name in test_items:
    print(f"\nSearching: {item_name}")
    result = search_item(item_name)
    
    if result:
        print(f"  Found: {result.get('name', 'Unknown')}")
        print(f"  Level: {result.get('level', 'N/A')}")
        print(f"  Price (raw): {result.get('price_raw', 'N/A')}")
        print(f"  Price (regular): {result.get('price', 'N/A')}")
        print(f"  Rarity: {result.get('rarity', 'N/A')}")
    else:
        print(f"  NOT FOUND")

print("\n" + "=" * 70)
print("Key observation: Use 'price_raw' field for proper formatting!")
