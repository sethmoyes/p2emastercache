#!/usr/bin/env python3
"""Scrape lore for creatures used in encounter pools"""
import json
import sys
sys.path.insert(0, '.')
from bin.scrape_creature_lore import get_creature_lore
import time

# Get creatures from encounter_pools.py
creatures_in_encounters = [
    "Wight",
    "Ghoul",
    "Zombie",
    "Skeleton",
    "Will-o'-Wisp",
    "Mohrg",
    "Shadow",
    "Wraith",
    "Spectre",
    "Giant Spider",
    "Dire Wolf",
    "Owlbear",
    "Ogre",
    "Troll",
    "Ettercap",
    "Ankhrav",
    "Basilisk",
    "Cockatrice",
    "Manticore",
    "Wyvern",
    "Young Dragon",
    "Bandit",
    "Cultist",
    "Brigand",
    "Mercenary",
    "Assassin",
    "Goblin",
    "Hobgoblin",
    "Orc",
    "Kobold",
    "Gnoll"
]

print(f"Scraping lore for {len(creatures_in_encounters)} creatures...")
print("="*60 + "\n")

creature_lore = {}

for idx, creature in enumerate(creatures_in_encounters, 1):
    print(f"[{idx}/{len(creatures_in_encounters)}] {creature}")
    result = get_creature_lore(creature)
    creature_lore[creature] = result
    time.sleep(0.5)  # Rate limiting

print("\nSaving to etc/creature_lore.json...")
with open('etc/creature_lore.json', 'w', encoding='utf-8') as f:
    json.dump(creature_lore, f, indent=2, ensure_ascii=False)

found = sum(1 for v in creature_lore.values() if v['source'] != 'Not Found')
print(f"\n{'='*60}")
print(f"Complete!")
print(f"  Total: {len(creature_lore)}")
print(f"  Found: {found}")
print(f"  Not found: {len(creature_lore) - found}")
print(f"  Success rate: {found/len(creature_lore)*100:.1f}%")
print(f"{'='*60}")
