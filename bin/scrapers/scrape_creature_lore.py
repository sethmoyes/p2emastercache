#!/usr/bin/env python3
"""
Scrape creature lore from PathfinderWiki for encounter generation
"""
import json
import requests
import re
import time
from bs4 import BeautifulSoup
import urllib.parse

def clean_creature_name_for_url(name):
    """Convert creature name to PathfinderWiki URL format"""
    # Remove parentheses and contents
    name = re.sub(r'\([^)]*\)', '', name)
    # Remove level indicators
    name = re.sub(r'Level \d+', '', name)
    # Clean up
    name = name.strip()
    # Replace apostrophes with nothing (Will-o'-Wisp -> Will-o-Wisp)
    name = name.replace("'", "")
    # Replace spaces with underscores (but hyphens stay)
    name = name.replace(' ', '_')
    return name

def try_pathfinderwiki(creature_name):
    """Try to get lore from PathfinderWiki"""
    clean_name = clean_creature_name_for_url(creature_name)
    url = f"https://pathfinderwiki.com/wiki/{clean_name}"
    
    print(f"  Trying PathfinderWiki: {url}", end="... ")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 404:
            print("✗ (404)")
            return None
        
        if response.status_code != 200:
            print(f"✗ ({response.status_code})")
            return None
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Get the main content
        content_div = soup.find('div', {'id': 'mw-content-text'})
        if not content_div:
            print("✗ (no content)")
            return None
        
        # Get the parser-output div which contains the actual content
        parser_output = content_div.find('div', {'class': 'mw-parser-output'})
        if not parser_output:
            parser_output = content_div
        
        # Get first few paragraphs (skip infobox)
        paragraphs = []
        for element in parser_output.children:
            if element.name == 'p':
                text = element.get_text().strip()
                # Skip empty paragraphs, navigation text, and citation needed
                if text and len(text) > 50 and not text.startswith('This page is a stub'):
                    # Clean up citation markers
                    text = re.sub(r'\[\d+\]', '', text)
                    text = re.sub(r'citation needed', '', text)
                    text = ' '.join(text.split())  # Clean up whitespace
                    paragraphs.append(text)
                    if len(paragraphs) >= 3:  # Get first 3 substantial paragraphs
                        break
        
        if not paragraphs:
            print("✗ (no paragraphs)")
            return None
        
        lore = '\n\n'.join(paragraphs)
        
        # Limit to reasonable length
        if len(lore) > 1500:
            lore = lore[:1500] + "..."
        
        print(f"✓ ({len(lore)} chars)")
        return {
            'source': 'PathfinderWiki',
            'url': url,
            'lore': lore
        }
        
    except Exception as e:
        print(f"✗ (error: {e})")
        return None

def search_google_for_creature(creature_name):
    """Search Google for creature lore as fallback"""
    clean_name = re.sub(r'\([^)]*\)', '', creature_name).strip()
    search_query = f"{clean_name} pathfinder 2e creature lore"
    encoded_query = urllib.parse.quote_plus(search_query)
    
    print(f"  Searching Google for: {clean_name}", end="... ")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        search_url = f"https://www.google.com/search?q={encoded_query}"
        response = requests.get(search_url, headers=headers, timeout=10)
        
        # Look for PathfinderWiki or Archives of Nethys URLs
        wiki_pattern = r'https?://(?:pathfinderwiki\.com|2e\.aonprd\.com)/[^\s<>"]+?/([^/\s<>"]+)'
        matches = re.findall(wiki_pattern, response.text)
        
        if matches:
            # Try the first match
            for match in matches[:3]:
                result_url = f"https://pathfinderwiki.com/wiki/{match}"
                result = try_pathfinderwiki_direct_url(result_url)
                if result:
                    print(f"✓ (found via search)")
                    return result
        
        print("✗ (no results)")
        return None
        
    except Exception as e:
        print(f"✗ (error: {e})")
        return None

def try_pathfinderwiki_direct_url(url):
    """Try a specific PathfinderWiki URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        content_div = soup.find('div', {'id': 'mw-content-text'})
        if not content_div:
            return None
        
        parser_output = content_div.find('div', {'class': 'mw-parser-output'})
        if not parser_output:
            parser_output = content_div
        
        paragraphs = []
        for element in parser_output.children:
            if element.name == 'p':
                text = element.get_text().strip()
                if text and len(text) > 50 and not text.startswith('This page is a stub'):
                    text = re.sub(r'\[\d+\]', '', text)
                    text = re.sub(r'citation needed', '', text)
                    text = ' '.join(text.split())
                    paragraphs.append(text)
                    if len(paragraphs) >= 3:
                        break
        
        if not paragraphs:
            return None
        
        lore = '\n\n'.join(paragraphs)
        if len(lore) > 1500:
            lore = lore[:1500] + "..."
        
        return {
            'source': 'PathfinderWiki',
            'url': url,
            'lore': lore
        }
        
    except:
        return None

def get_creature_lore(creature_name):
    """Get lore for a creature, trying multiple methods"""
    # Try PathfinderWiki first
    result = try_pathfinderwiki(creature_name)
    if result:
        return result
    
    # Try Google search as fallback
    result = search_google_for_creature(creature_name)
    if result:
        return result
    
    # Return placeholder if nothing found
    return {
        'source': 'Not Found',
        'url': '',
        'lore': f'No lore found for {creature_name}. This creature may be from a newer source or have a different name on PathfinderWiki.'
    }

def load_creatures_from_json():
    """Load creature list from creatures.json"""
    with open('etc/creatures.json', 'r', encoding='utf-8') as f:
        creatures = json.load(f)
    return creatures

def scrape_all_creature_lore():
    """Scrape lore for all creatures"""
    print("Loading creatures from creatures.json...")
    creatures = load_creatures_from_json()
    print(f"  Loaded {len(creatures)} creatures\n")
    
    # Get unique creature names
    creature_names = sorted(set(c['name'] for c in creatures))
    print(f"  Found {len(creature_names)} unique creature names\n")
    
    # Limit to first 100 for testing (remove this for full run)
    # creature_names = creature_names[:100]
    
    creature_lore = {}
    
    for idx, name in enumerate(creature_names, 1):
        print(f"[{idx}/{len(creature_names)}] {name}")
        
        lore_data = get_creature_lore(name)
        creature_lore[name] = lore_data
        
        # Rate limiting
        time.sleep(0.5)
        
        # Save progress every 50 creatures
        if idx % 50 == 0:
            print(f"\n  Saving progress... ({idx} creatures)")
            with open('etc/creature_lore.json', 'w', encoding='utf-8') as f:
                json.dump(creature_lore, f, indent=2, ensure_ascii=False)
            print(f"  ✓ Saved\n")
    
    # Final save
    print("\nSaving final results...")
    with open('etc/creature_lore.json', 'w', encoding='utf-8') as f:
        json.dump(creature_lore, f, indent=2, ensure_ascii=False)
    
    # Statistics
    found = sum(1 for v in creature_lore.values() if v['source'] != 'Not Found')
    not_found = len(creature_lore) - found
    
    print(f"\n{'='*60}")
    print(f"Scraping complete!")
    print(f"  Total creatures: {len(creature_lore)}")
    print(f"  Lore found: {found}")
    print(f"  Not found: {not_found}")
    print(f"  Success rate: {found/len(creature_lore)*100:.1f}%")
    print(f"  Output: etc/creature_lore.json")
    print(f"{'='*60}")

if __name__ == "__main__":
    print("Creature Lore Scraper")
    print("="*60)
    print("This will scrape PathfinderWiki for creature lore")
    print("and create etc/creature_lore.json")
    print("="*60 + "\n")
    
    scrape_all_creature_lore()
