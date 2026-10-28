#!/usr/bin/env python3
"""
Build etc/item_details.json: each stockable item's and spell's Archives of
Nethys page and one-line summary, for the shop pages' item details.

Reads AoN's public search index (the one its own site searches) in a handful of
bulk requests; run it by hand when equipment.json or spells.json change. The
shop pages and restocks only read the file, so they never call AoN.

    python3 bin/data_management/fetch_item_details.py
"""

import json
import os
import re
import sys
import time
import unicodedata

import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from avtools.data import etc_path, read_json  # noqa: E402

INDEX = 'https://elasticsearch.aonprd.com/aon/_search'
CATEGORIES = ('equipment', 'weapon', 'armor', 'shield', 'spell')
FIELDS = ['name', 'url', 'summary', 'category', 'item_subcategory', 'remaster_id', 'exclude_from_search']
PAGE = 2000
SUMMARY_MAX = 240

ASCII_FIXES = {'‘': "'", '’': "'", '“': '"', '”': '"', '–': '-',
               '—': ' - ', '…': '...', '×': 'x', '−': '-', ' ': ' '}


def ascii_text(text):
    """Generated text stays ASCII (claude.md)."""
    for bad, good in ASCII_FIXES.items():
        text = text.replace(bad, good)
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    return re.sub(r'\s+', ' ', text).strip()


def short_summary(text):
    text = ascii_text(text or '')
    if len(text) <= SUMMARY_MAX:
        return text
    cut = text[:SUMMARY_MAX].rsplit(' ', 1)[0]
    return cut.rstrip(',;:') + '...'


def fetch(category):
    """Every document in one index category, paged with search_after."""
    docs, after = [], None
    while True:
        body = {'size': PAGE, '_source': FIELDS, 'sort': [{'id.keyword': 'asc'}],
                'query': {'bool': {'filter': [{'term': {'category': category}}]}}}
        if after:
            body['search_after'] = after
        response = requests.post(INDEX, json=body, timeout=60)
        response.raise_for_status()
        hits = response.json()['hits']['hits']
        docs += [hit['_source'] for hit in hits]
        print(f'  {category}: {len(docs)}')
        if len(hits) < PAGE:
            return docs
        after = hits[-1]['sort']
        time.sleep(1)


def best(docs):
    """Of documents sharing a name, the remaster one: legacy entries point at it with remaster_id."""
    return sorted(docs, key=lambda d: (bool(d.get('remaster_id')), d.get('exclude_from_search') in (True, 'True')))[0]


def build(wanted, docs):
    by_name = {}
    for doc in docs:
        if doc.get('name') and doc.get('url'):
            by_name.setdefault(doc['name'].lower(), []).append(doc)
    found = {}
    for name in sorted(wanted):
        matches = by_name.get(name.lower())
        if not matches:
            continue
        doc = best(matches)
        entry = {'url': doc['url']}
        if doc.get('summary'):
            entry['summary'] = short_summary(doc['summary'])
        if doc.get('item_subcategory'):
            entry['subcategory'] = ascii_text(doc['item_subcategory'])
        found[name] = entry
    return found


def main():
    equipment = {item['name'] for item in read_json(etc_path('equipment.json'))}
    spells = {spell['name'] for spell in read_json(etc_path('spells.json'))}
    print('Reading the Archives of Nethys search index...')
    docs = {category: fetch(category) for category in CATEGORIES}
    item_docs = [doc for category in CATEGORIES if category != 'spell' for doc in docs[category]]
    out = {
        '_about': 'AoN page and summary per item and spell name; built by '
                  'bin/data_management/fetch_item_details.py from the AoN search index',
        '_fetched': time.strftime('%Y-%m-%d'),
        'items': build(equipment, item_docs),
        'spells': build(spells, docs['spell']),
    }
    path = etc_path('item_details.json')
    with open(path + '.tmp', 'w', encoding='ascii') as f:
        json.dump(out, f, indent=1, sort_keys=True)
        f.write('\n')
    os.replace(path + '.tmp', path)
    print(f"OK {len(out['items'])}/{len(equipment)} items, {len(out['spells'])}/{len(spells)} spells -> {path}")


if __name__ == '__main__':
    main()
