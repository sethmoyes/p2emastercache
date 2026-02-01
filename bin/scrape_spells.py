#!/usr/bin/env python3
"""
Scrape spells from Archives of Nethys Elasticsearch API
Creates spells.json with all spell data
"""
import requests
import json
import time

# Archives of Nethys Elasticsearch endpoint
AON_ELASTIC_URL = "https://elasticsearch.aonprd.com/aon/_search"

def search_spells(from_index=0, size=100):
    """Search for spells using Elasticsearch API"""
    
    payload = {
        "query": {
            "bool": {
                "must": [
                    {"match": {"category": "spell"}}
                ]
            }
        },
        "size": size,
        "from": from_index,
        "sort": [
            {"name.keyword": "asc"}
        ]
    }
    
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.post(AON_ELASTIC_URL, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error searching spells: {e}")
        return None

def extract_spell_data(hit):
    """Extract relevant spell data from Elasticsearch hit"""
    source = hit.get('_source', {})
    
    spell = {
        'name': source.get('name', 'Unknown'),
        'level': source.get('level', 0),
        'type': source.get('spell_type', 'Unknown'),  # spell, focus, ritual
        'traditions': source.get('tradition', []),
        'cast': source.get('cast', 'Unknown'),
        'range': source.get('range', 'Unknown'),
        'targets': source.get('targets', ''),
        'area': source.get('area', ''),
        'duration': source.get('duration', ''),
        'saving_throw': source.get('saving_throw', ''),
        'traits': source.get('trait', []),
        'rarity': source.get('rarity', 'common'),
        'school': source.get('school', 'Unknown'),
        'url': source.get('url', ''),
        'source': source.get('source', []),
        'text': source.get('text', ''),
    }
    
    return spell

def scrape_all_spells():
    """Scrape all spells from AoN"""
    print("Scraping spells from Archives of Nethys Elasticsearch API...")
    print("=" * 80)
    
    all_spells = []
    from_index = 0
    batch_size = 100
    
    while True:
        print(f"\nFetching spells {from_index} to {from_index + batch_size}...")
        
        result = search_spells(from_index=from_index, size=batch_size)
        
        if not result:
            print("Failed to fetch spells")
            break
        
        hits = result.get('hits', {}).get('hits', [])
        
        if not hits:
            print("No more spells found")
            break
        
        for hit in hits:
            spell = extract_spell_data(hit)
            all_spells.append(spell)
            print(f"  - {spell['name']} (Level {spell['level']}, {spell.get('type', 'spell')})")
        
        from_index += batch_size
        
        # Check if we've reached the end
        total_hits = result.get('hits', {}).get('total', {}).get('value', 0)
        if from_index >= total_hits:
            break
        
        time.sleep(0.5)  # Rate limiting
    
    return all_spells

if __name__ == "__main__":
    spells = scrape_all_spells()
    
    print(f"\n{'=' * 80}")
    print(f"SCRAPING COMPLETE")
    print(f"{'=' * 80}")
    print(f"Total spells scraped: {len(spells)}")
    
    # Save to JSON
    output_file = "etc/spells.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(spells, f, indent=2, ensure_ascii=False)
    
    print(f"\nSaved to: {output_file}")
    
    # Print some statistics
    by_level = {}
    by_tradition = {}
    by_type = {}
    
    for spell in spells:
        level = spell['level']
        by_level[level] = by_level.get(level, 0) + 1
        
        spell_type = spell.get('type', 'spell')
        by_type[spell_type] = by_type.get(spell_type, 0) + 1
        
        for tradition in spell.get('traditions', []):
            by_tradition[tradition] = by_tradition.get(tradition, 0) + 1
    
    print(f"\nSpells by Level:")
    for level in sorted(by_level.keys()):
        print(f"  Level {level}: {by_level[level]} spells")
    
    print(f"\nSpells by Type:")
    for spell_type in sorted(by_type.keys()):
        print(f"  {spell_type}: {by_type[spell_type]} spells")
    
    if by_tradition:
        print(f"\nSpells by Tradition:")
        for tradition in sorted(by_tradition.keys()):
            print(f"  {tradition}: {by_tradition[tradition]} spells")
    
    print(f"\nOK All spells scraped successfully!")
