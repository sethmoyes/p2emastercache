#!/usr/bin/env python3
"""Test creature lore scraping"""
import sys
sys.path.insert(0, 'bin')
from scrape_creature_lore import get_creature_lore

# Test creatures
test_creatures = [
    "Will-o'-Wisp",
    "Ghoul",
    "Zombie",
    "Skeleton",
    "Mohrg"
]

for creature in test_creatures:
    print(f"\n{'='*60}")
    print(f"Testing: {creature}")
    print('='*60)
    result = get_creature_lore(creature)
    print(f"\nSource: {result['source']}")
    print(f"URL: {result['url']}")
    print(f"Lore preview: {result['lore'][:200]}...")
