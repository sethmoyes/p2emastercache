#!/usr/bin/env python3
"""
Scrape creature stats from Archives of Nethys Elasticsearch API
Populates creatures.json with full creature data including attacks, abilities, etc.
"""
import json
import requests
import time
import re

AON_API_URL = "https://elasticsearch.aonprd.com"

def search_creatures(size=1000, from_offset=0):
    """Search for creatures using the AoN Elasticsearch API"""
    url = f"{AON_API_URL}/aon/_search"
    
    payload = {
        "query": {
            "bool": {
                "must": [
                    {"term": {"type": "creature"}}
                ],
                "must_not": [
                    {"term": {"exclude_from_search": True}}
                ]
            }
        },
        "size": size,
        "from": from_offset,
        "sort": [
            {"name.keyword": "asc"}
        ]
    }
    
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0'
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error searching creatures: {e}")
        return None

def parse_creature(hit):
    """Parse creature data from Elasticsearch hit"""
    source = hit.get('_source', {})
    
    creature = {
        'name': source.get('name', 'Unknown'),
        'level': source.get('level', 0),
        'hp': source.get('hp', 0),
        'ac': source.get('ac', 0),
        'fort': source.get('fortitude', ''),
        'reflex': source.get('reflex', ''),
        'will': source.get('will', ''),
        'perception': source.get('perception', ''),
        'traits': source.get('trait', []),
        'rarity': source.get('rarity', 'common'),
        'size': source.get('size', 'Medium'),
        'alignment': source.get('alignment', ''),
        'creature_type': source.get('creature_type', ''),
        'attacks': [],
        'abilities': [],
        'skills': {},
        'languages': source.get('language', []),
        'immunities': source.get('immunity', []),
        'resistances': source.get('resistance', []),
        'weaknesses': source.get('weakness', []),
        'url': source.get('url', '')
    }
    
    # Parse attacks from text
    text = source.get('text', '')
    
    # Extract attacks (look for Melee/Ranged patterns)
    attack_pattern = r'(Melee|Ranged)\s+([^,]+?)\s+([+-]\d+)(?:\s+\([^)]+\))?,?\s+(?:Damage\s+)?([^;]+)'
    attacks = re.findall(attack_pattern, text, re.IGNORECASE)
    for attack in attacks:
        attack_type, weapon, bonus, damage = attack
        creature['attacks'].append(f"{attack_type} {weapon} {bonus}, Damage {damage}".strip())
    
    # Extract abilities (look for ability names followed by descriptions)
    # This is harder - abilities are usually in their own sections
    ability_section = re.search(r'(Abilities|Special Abilities|Actions)(.*?)(?=Skills|Languages|Immunities|$)', text, re.DOTALL | re.IGNORECASE)
    if ability_section:
        ability_text = ability_section.group(2)
        # Split by ability names (usually capitalized words followed by description)
        ability_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+([^.]+\.)'
        abilities = re.findall(ability_pattern, ability_text)
        for ability_name, ability_desc in abilities[:10]:  # Limit to 10 abilities
            creature['abilities'].append(f"{ability_name}: {ability_desc}".strip())
    
    # Parse skills
    skills_text = source.get('skill', [])
    if isinstance(skills_text, list):
        for skill in skills_text:
            # Format: "Acrobatics +10" or "Acrobatics +10 (some note)"
            match = re.match(r'([A-Za-z\s]+)\s+([+-]\d+)', skill)
            if match:
                skill_name, bonus = match.groups()
                creature['skills'][skill_name.strip()] = bonus
    
    return creature

def scrape_all_creatures():
    """Scrape all creatures from AoN"""
    print("Scraping creatures from Archives of Nethys...")
    print("="*60)
    
    all_creatures = []
    offset = 0
    batch_size = 1000
    
    while True:
        print(f"\nFetching creatures {offset} to {offset + batch_size}...")
        
        result = search_creatures(size=batch_size, from_offset=offset)
        if not result:
            print("Failed to fetch creatures")
            break
        
        hits = result.get('hits', {}).get('hits', [])
        if not hits:
            print("No more creatures found")
            break
        
        print(f"  Processing {len(hits)} creatures...")
        for hit in hits:
            creature = parse_creature(hit)
            all_creatures.append(creature)
        
        print(f"  Total creatures so far: {len(all_creatures)}")
        
        # Check if we got all results
        total = result.get('hits', {}).get('total', {}).get('value', 0)
        if len(all_creatures) >= total:
            print(f"\nReached total of {total} creatures")
            break
        
        offset += batch_size
        time.sleep(0.5)  # Rate limiting
    
    # Save to file
    print(f"\nSaving {len(all_creatures)} creatures to etc/creatures.json...")
    with open('etc/creatures.json', 'w', encoding='utf-8') as f:
        json.dump(all_creatures, f, indent=2, ensure_ascii=False)
    
    # Statistics
    with_attacks = sum(1 for c in all_creatures if c['attacks'])
    with_abilities = sum(1 for c in all_creatures if c['abilities'])
    
    print("\n" + "="*60)
    print("Scraping complete!")
    print(f"  Total creatures: {len(all_creatures)}")
    print(f"  With attacks: {with_attacks} ({with_attacks/len(all_creatures)*100:.1f}%)")
    print(f"  With abilities: {with_abilities} ({with_abilities/len(all_creatures)*100:.1f}%)")
    print(f"  Output: etc/creatures.json")
    print("="*60)

if __name__ == "__main__":
    scrape_all_creatures()
