#!/usr/bin/env python3
"""
Build etc/talismans.json: every talisman (and fulu) on the Archives of Nethys,
for the talisman shop. equipment.json has none, so they come straight from
AoN's public search index in one request. Run it by hand to refresh; restocks
only read the file.

    python3 bin/data_management/fetch_talismans.py
"""

import json
import os
import sys
import time

import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from avtools.data import etc_path  # noqa: E402
from bin.data_management.fetch_item_details import INDEX, ascii_text, short_summary  # noqa: E402

FIELDS = ['name', 'level', 'price_raw', 'rarity', 'item_subcategory', 'usage', 'summary', 'url',
          'remaster_id', 'exclude_from_search', 'source']


def fetch():
    body = {'size': 1000, '_source': FIELDS, 'sort': [{'id.keyword': 'asc'}],
            'query': {'bool': {'filter': [{'term': {'category': 'equipment'}},
                                          {'term': {'trait_raw': 'talisman'}}]}}}
    response = requests.post(INDEX, json=body, timeout=60)
    response.raise_for_status()
    return [hit['_source'] for hit in response.json()['hits']['hits']]


def build(docs):
    """One entry per name: the remaster one (legacy entries point at it with remaster_id)."""
    talismans = {}
    for doc in docs:
        if doc.get('remaster_id') or doc.get('exclude_from_search') in (True, 'True'):
            continue
        if not (doc.get('name') and doc.get('url') and doc.get('price_raw')):
            continue
        talismans[doc['name']] = {
            'name': ascii_text(doc['name']),
            'level': int(doc.get('level') or 0),
            'price': ascii_text(doc['price_raw']),
            'rarity': (doc.get('rarity') or 'common').lower(),
            'kind': ascii_text(doc.get('item_subcategory') or 'Talismans'),
            'usage': ascii_text(doc.get('usage') or ''),
            'summary': short_summary(doc.get('summary')),
            'url': doc['url'],
            'source': ascii_text(', '.join(doc.get('source') or [])),
        }
    return sorted(talismans.values(), key=lambda t: (t['level'], t['name']))


def main():
    print('Reading the Archives of Nethys search index...')
    talismans = build(fetch())
    out = {
        '_about': 'Talismans and fulu for the talisman shop; built by '
                  'bin/data_management/fetch_talismans.py from the AoN search index',
        '_fetched': time.strftime('%Y-%m-%d'),
        'talismans': talismans,
    }
    path = etc_path('talismans.json')
    with open(path + '.tmp', 'w', encoding='ascii') as f:
        json.dump(out, f, indent=1)
        f.write('\n')
    os.replace(path + '.tmp', path)
    print(f'OK {len(talismans)} talismans -> {path}')


if __name__ == '__main__':
    main()
