#!/usr/bin/env python3
"""
Reset verification dates in equipment.json to force re-verification
This will allow check_data_integrity.py to re-check all items
"""
import json

print("Resetting verification dates in equipment.json...")

# Load equipment
with open('etc/equipment.json', 'r', encoding='utf-8') as f:
    equipment = json.load(f)

print(f"Loaded {len(equipment)} items")

# Remove verification dates
removed_count = 0
for item in equipment:
    if 'aon_verified_date' in item:
        del item['aon_verified_date']
        removed_count += 1

print(f"Removed {removed_count} verification dates")

# Save back
with open('etc/equipment.json', 'w', encoding='utf-8') as f:
    json.dump(equipment, f, indent=2, ensure_ascii=False)

print("Done! Now run: python bin/check_data_integrity.py all equipment --replace")
