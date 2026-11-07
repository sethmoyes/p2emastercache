#!/usr/bin/env python3
"""
Build etc/pathbuilder_items.json: what a Pathbuilder 2e custom pack needs to
know about each item the shops can stock (rules text, traits, usage, and the
numbers Pathbuilder does math with: weapon damage and group, armor and shield
stats). equipment.json has few of those, so they come from the Archives of
Nethys' public search index in a handful of bulk requests. Run it by hand when
equipment.json or talismans.json change; the shop pages only read the file.

    python3 bin/data_management/fetch_pathbuilder_items.py
"""

import json
import os
import re
import sys
import time

import markdown
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from avtools.data import etc_path, read_json  # noqa: E402
from bin.data_management.fetch_item_details import INDEX, ascii_text, best  # noqa: E402

CATEGORIES = ('equipment', 'weapon', 'armor', 'shield')
FIELDS = ['name', 'url', 'category', 'level', 'price', 'rarity', 'trait', 'trait_raw', 'usage', 'bulk_raw',
          'hands', 'item_category', 'item_parent_id', 'remaster_id', 'exclude_from_search', 'markdown',
          'weapon_category', 'weapon_type', 'weapon_group', 'damage', 'damage_die', 'damage_type', 'range', 'reload',
          'armor_category', 'ac', 'dex_cap', 'strength', 'check_penalty', 'speed_penalty', 'hardness', 'hp']
PAGE = 1000
DESCRIPTION_MAX = 6000
ACTIONS = {'Single Action': '[one-action]', 'Two Actions': '[two-actions]', 'Three Actions': '[three-actions]',
           'Reaction': '[reaction]', 'Free Action': '[free-action]'}
# Stat lines the pack carries as fields, so the description leaves them out
FIELD_LABELS = ('Source', 'Price', 'Usage', 'Bulk', 'Hands', 'Damage', 'Range', 'Reload', 'Type', 'Category',
                'Group', 'Favored Weapon', 'Ammunition', 'Access', 'PFS Note', 'AC Bonus', 'Dex Cap',
                'Check Penalty', 'Speed Penalty', 'Strength', 'Hardness', 'HP', 'HP (BT)', 'BT')
BASE_LINK = re.compile(r'\*\*Base (?:Weapon|Armor|Shield)\*\*\s*\[[^\]]*\]\((/(?:Weapons|Armor|Shields)\.aspx\?ID=\d+)\)')
BASE_PAGES = {'Weapons': 'Weapons', 'Armor': 'Armor', 'Shields': 'Shields'}
LEVEL2 = re.compile(r'<title\s+level="2"[^>]*>(.*?)</title>', re.S)


def fetch(category):
    """Every document in one index category, paged with search_after."""
    docs, after = [], None
    while True:
        body = {'size': PAGE, '_source': FIELDS, 'sort': [{'id.keyword': 'asc'}],
                'query': {'bool': {'filter': [{'term': {'category': category}}]}}}
        if after:
            body['search_after'] = after
        response = requests.post(INDEX, json=body, timeout=120)
        response.raise_for_status()
        hits = response.json()['hits']['hits']
        docs += [hit['_source'] for hit in hits]
        print(f'  {category}: {len(docs)}')
        if len(hits) < PAGE:
            return docs
        after = hits[-1]['sort']
        time.sleep(1)


def _number(value):
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _section(md, name, child):
    """The part of an AoN page about this item: the whole page up to its first
    sub-heading, plus (for one grade of an item family) that grade's own entry."""
    first = LEVEL2.search(md)
    head = md[:first.start()] if first else md
    if not child:
        return head
    for m in LEVEL2.finditer(md):
        if ascii_text(re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', m.group(1))).lower() == name.lower():
            rest = md[m.end():]
            end = re.search(r'<title\s|<document\s', rest)
            return head + '\n\n' + (rest[:end.start()] if end else rest)
    return head


def description_html(md, name, child=False):
    """An AoN page's markdown as the simple HTML Pathbuilder shows: links as their text,
    action icons as Pathbuilder's own [one-action] tags, stat lines left out."""
    md = _section(md, name, child)
    md = re.sub(r'<aside>.*?</aside>', '', md, flags=re.S)
    md = re.sub(r'<title[^>]*>.*?</title>', '', md, flags=re.S)
    md = re.sub(r'<traits>.*?</traits>', '', md, flags=re.S)
    md = re.sub(r'<actions string="([^"]+)"\s*/>', lambda m: ' ' + ACTIONS.get(m.group(1), '') + ' ', md)
    md = re.sub(r'<br\s*/?>', '\n\n', md)
    md = re.sub(r'<[^>]+>', '\n', md)                       # row, column and AoN's other layout tags
    md = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', md)        # links to their text
    md = re.sub(r'^\s*-{3,}\s*$', '', md, flags=re.M)
    labels = '|'.join(re.escape(label) for label in FIELD_LABELS)
    md = re.sub(rf'^\s*\*\*(?:{labels})\*\*.*$', '', md, flags=re.M)
    md = re.sub(r'^\s*May contain spoilers from .*$', '', md, flags=re.M)
    md = re.sub(r'(\*\*[A-Za-z ]+\*\*)\s*\n+\s*(?=\S)', r'\1 ', md)  # label and value onto one line
    md = re.sub(r'\n\s*\n\s*(\[[a-z-]+\])', r' \1', md)
    md = re.sub(r'\n{3,}', '\n\n', ascii_text_lines(md)).strip()
    html = markdown.markdown(md)
    html = html.replace('<strong>', '<b>').replace('</strong>', '</b>')
    html = html.replace('<em>', '<i>').replace('</em>', '</i>')
    if len(html) > DESCRIPTION_MAX:
        html = html[:DESCRIPTION_MAX].rsplit(' ', 1)[0] + '...</p>'
    return html


def ascii_text_lines(text):
    """ascii_text, keeping line breaks (it folds all whitespace)."""
    return '\n'.join(ascii_text(line) for line in text.split('\n'))


def _traits(doc):
    raw = doc.get('trait_raw') or doc.get('trait') or []
    return [ascii_text(t) for t in raw if t]


def stats(doc):
    """The numbers Pathbuilder uses, by what the item is."""
    out = {}
    if doc.get('damage_die'):
        # damage is "1d8 S"; damage_type lists every type a versatile weapon can deal, alphabetically
        printed = re.search(r'\b([BPS])\b\s*$', doc.get('damage') or '')
        damage_types = [printed.group(1)] if printed else doc.get('damage_type') or []
        out['weapon'] = {
            'category': doc.get('weapon_category') or 'Simple',
            'ranged': doc.get('weapon_type') == 'Ranged',
            'group': ascii_text(doc.get('weapon_group') or ''),
            'die': _number(doc['damage_die']),
            'damage_type': damage_types[0][:1] if damage_types else '',
            'hands': ascii_text(str(doc.get('hands') or '1')),
            'range': _number(doc.get('range')),
            'reload': ascii_text(str(doc.get('reload'))) if doc.get('reload') not in (None, '') else None,
        }
    if doc.get('armor_category'):
        out['armor'] = {
            'category': doc['armor_category'],
            'ac': _number(doc.get('ac')) or 0,
            'dex_cap': _number(doc.get('dex_cap')),
            'strength': _number(doc.get('strength')),
            'check_penalty': _number(doc.get('check_penalty')) or 0,
            'speed_penalty': _number(re.sub(r'[^\d-]', '', str(doc.get('speed_penalty') or ''))) or 0,
        }
    if doc.get('hardness') or doc.get('category') == 'shield':
        out['shield'] = {'ac': _number(doc.get('ac')) or 0, 'hardness': _number(doc.get('hardness')) or 0,
                         'hp': _number(doc.get('hp')) or 0}
    return out


def entry(doc, by_url):
    md = doc.get('markdown') or ''
    item = {
        'url': doc['url'],
        'level': _number(doc.get('level')) or 0,
        'price_cp': _number(doc.get('price')),
        'rarity': (doc.get('rarity') or 'common').lower(),
        'traits': _traits(doc),
        'usage': ascii_text(doc.get('usage') or ''),
        'bulk': ascii_text(str(doc.get('bulk_raw') or '')),
        'category': ascii_text(doc.get('item_category') or ''),
        'description': description_html(md, doc['name'], child=bool(doc.get('item_parent_id'))),
        **stats(doc),
    }
    # A specific magic weapon, armor or shield is filed as equipment; its base item has the numbers.
    # Older pages name it as "Base Weapon"; remaster ones only link it in the text.
    own = _section(md, doc['name'], bool(doc.get('item_parent_id')))
    base = BASE_LINK.search(own)
    linked = re.search(r'\]\((/%s\.aspx\?ID=\d+)\)' % BASE_PAGES.get(item['category'], '-'), own)
    base_url = base.group(1) if base else linked.group(1) if linked else None
    if base_url in by_url:
        for kind, values in stats(by_url[base_url]).items():
            item.setdefault(kind, values)
        base_traits = _traits(by_url[base_url])
        item['traits'] += [t for t in base_traits if t not in item['traits']]
    # Precious-material shields give their numbers in a sentence
    numbers = re.search(r'Hardness (\d+), HP (\d+)', own)
    if item['category'] == 'Shields' and 'shield' not in item and numbers:
        item['shield'] = {'ac': 1 if 'buckler' in doc['name'].lower() else 2,
                          'hardness': int(numbers.group(1)), 'hp': int(numbers.group(2))}
    return item


def build(wanted, docs):
    by_name, by_url = {}, {}
    for doc in docs:
        if doc.get('name') and doc.get('url'):
            by_name.setdefault(doc['name'].lower(), []).append(doc)
            if not doc.get('item_parent_id'):
                by_url.setdefault(doc['url'], []).append(doc)
    by_url = {url: best(matches) for url, matches in by_url.items()}
    return {name: entry(best(by_name[name.lower()]), by_url)
            for name in sorted(wanted) if name.lower() in by_name}


def main():
    wanted = {item['name'] for item in read_json(etc_path('equipment.json'))}
    wanted |= {t['name'] for t in read_json(etc_path('talismans.json'))['talismans']}
    print('Reading the Archives of Nethys search index...')
    docs = [doc for category in CATEGORIES for doc in fetch(category)]
    items = build(wanted, docs)
    out = {
        '_about': 'Rules text, traits and stats per item name for Pathbuilder custom packs; built by '
                  'bin/data_management/fetch_pathbuilder_items.py from the AoN search index',
        '_fetched': time.strftime('%Y-%m-%d'),
        'items': items,
    }
    path = etc_path('pathbuilder_items.json')
    with open(path + '.tmp', 'w', encoding='ascii') as f:
        json.dump(out, f, indent=1, sort_keys=True)
        f.write('\n')
    os.replace(path + '.tmp', path)
    print(f'OK {len(items)}/{len(wanted)} items -> {path}')


if __name__ == '__main__':
    main()
