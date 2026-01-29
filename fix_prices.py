#!/usr/bin/env python3
"""Fix missing prices in equipment.json"""
import json
import random

# Load equipment
with open('etc/equipment.json', 'r', encoding='utf-8') as f:
    equipment = json.load(f)

print(f"Total items: {len(equipment)}")

# Find items with no price or 0 gp
no_price_items = []
for item in equipment:
    if item['price'] in ['0 gp', '0', '', 'L']:
        no_price_items.append(item)

print(f"Items with no/bad price: {len(no_price_items)}")

# Fix first 50
fixed_count = 0
for item in no_price_items[:50]:
    # Random price between 5 sp (0.5 gp) and 1 gp
    price_options = ['5 sp', '6 sp', '7 sp', '8 sp', '9 sp', '1 gp']
    item['price'] = random.choice(price_options)
    fixed_count += 1
    print(f"  Fixed: {item['name']} -> {item['price']}")

print(f"\nFixed {fixed_count} items")

# Save
with open('etc/equipment.json', 'w', encoding='utf-8') as f:
    json.dump(equipment, f, indent=2, ensure_ascii=False)

print("✓ Saved to etc/equipment.json")
