#!/usr/bin/env python3
import sys
sys.path.append('bin')
from generate_otari_merchants import parse_equipment_md

items = parse_equipment_md('etc/equipment.md')

print(f'Weapons uncommon: {len(items["weapons"]["uncommon"])}')
print(f'Armor uncommon: {len(items["armor"]["uncommon"])}')
print(f'Adventuring uncommon: {len(items["adventuring"]["uncommon"])}')
print(f'Alchemical uncommon: {len(items["alchemical"]["uncommon"])}')
print(f'Magical uncommon: {len(items["magical"]["uncommon"])}')

print('\nSample uncommon weapons:')
for item in items["weapons"]["uncommon"][:5]:
    print(f'  {item["name"]} - Level {item["level"]} - {item["price"]}')

print('\nSample uncommon adventuring:')
for item in items["adventuring"]["uncommon"][:5]:
    print(f'  {item["name"]} - Level {item["level"]} - {item["price"]}')
