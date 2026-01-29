#!/usr/bin/env python3
import requests

# Test URLs from the archived file
test_urls = [
    "https://2e.aonprd.com/Images/Weapons/Longsword.webp",
    "https://2e.aonprd.com/Images/Weapons/Heavy_Crossbow.webp",
    "https://2e.aonprd.com/Images/Armor/Leather_Armor.webp",
    "https://2e.aonprd.com/Images/Armor/Buckler.webp",
    "https://2e.aonprd.com/Images/Treasure/Healing_Potion.webp",
]

for url in test_urls:
    print(f"Testing: {url}", end="... ")
    try:
        response = requests.head(url, timeout=5)
        print(f"{response.status_code}")
    except Exception as e:
        print(f"Error: {e}")
