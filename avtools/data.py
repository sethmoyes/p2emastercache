"""
Where things live, and the data files every tool reads, loaded once.

Everything is resolved from the repo root, so tools work from any working
directory. DATA_DIR is where the web app writes (a Fly volume in production,
the repo itself locally).
"""

import json
import os
from functools import lru_cache

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ETC = os.path.join(ROOT, 'etc')
DATA_DIR = os.environ.get('DATA_DIR') or ROOT
AON_BASE = 'https://2e.aonprd.com'


def etc_path(name):
    return os.path.join(ETC, name)


def read_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


@lru_cache(maxsize=None)
def creatures():
    return read_json(etc_path('creatures.json'))


@lru_cache(maxsize=None)
def events():
    """Event templates by category: OPPORTUNITY, COMPLICATION, DILEMMA, ACTIVE_THREAT."""
    data = read_json(etc_path('dungeon_turn_events.json'))
    return {category: data.get(category, []) for category in
            ('OPPORTUNITY', 'COMPLICATION', 'DILEMMA', 'ACTIVE_THREAT')}


@lru_cache(maxsize=None)
def floor_ecology():
    """Each floor's name, ecology summary and entries, keyed by floor number."""
    return {int(floor): data for floor, data in read_json(etc_path('floor_ecology.json'))['floors'].items()}


@lru_cache(maxsize=None)
def shops():
    """Who runs each Otari shop, keyed by shop slug."""
    return {slug: people for slug, people in read_json(etc_path('otari_shops.json')).items()
            if not slug.startswith('_')}


# ---------------------------------------------------------------- creatures
# creatures.json holds legacy and remaster versions of many creatures under the
# same name. Legacy stat blocks carry an alignment trait; remaster ones don't.
# This campaign uses the remaster, so that one wins.
LEGACY_ALIGNMENTS = {'LG', 'NG', 'CG', 'LN', 'N', 'CN', 'LE', 'NE', 'CE'}
_by_name = {}


def aon_id(record):
    try:
        return int(record.get('url', '').rsplit('=', 1)[1])
    except (IndexError, ValueError):
        return 0


def preferred(records):
    """Of several stat blocks with one name, the remaster one (newest on AoN)."""
    return max(records, key=lambda c: (not LEGACY_ALIGNMENTS & set(c.get('traits', [])), aon_id(c)))


def find_creature(records, name):
    """The stat block for a creature name, from a list of creature records."""
    key = id(records)
    if key not in _by_name:
        grouped = {}
        for creature in records:
            grouped.setdefault(creature['name'], []).append(creature)
        _by_name.clear()
        _by_name[key] = {n: preferred(group) for n, group in grouped.items()}
    return _by_name[key].get(name)
