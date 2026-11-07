"""
Creature stat blocks from the Archives of Nethys, looked up live.

AoN's public search index (the one its own site searches) has every creature
with real numbers: saves, skills, speed, immunities, and the full stat block.
creatures.json lacks most of that (saves and skills are empty on every record),
so the combat tracker asks AoN each time and keeps what it found on disk, so a
creature already looked up still loads when AoN is slow or down. Without AoN
and without a saved copy, creatures.json fills in what it can.
"""

import copy
import json
import os
import re
import threading
import unicodedata

import requests

from avtools.data import AON_BASE, DATA_DIR, creatures, find_creature

INDEX = 'https://elasticsearch.aonprd.com/aon/_search'
TIMEOUT = 6
CACHE_DIR = os.path.join(DATA_DIR, 'cache', 'aon')
SEARCH_SIZE = 30
# The Abomination Vaults issues on AoN, so the campaign's own creatures rank first
AV_SOURCES = ('Pathfinder #163', 'Pathfinder #164', 'Pathfinder #165', 'Abomination Vaults')
SUMMARY_FIELDS = ['name', 'url', 'level', 'hp', 'ac', 'perception', 'rarity', 'size', 'trait',
                  'remaster_id', 'source', 'npc']

ASCII_FIXES = {'‘': "'", '’': "'", '“': '"', '”': '"', '–': '-',
               '—': ' - ', '…': '...', '×': 'x', '−': '-', ' ': ' '}
ACTIONS = {'Single Action': '[1]', 'Two Actions': '[2]', 'Three Actions': '[3]',
           'Reaction': '[R]', 'Free Action': '[F]'}
SAVE_NAMES = (('fort', 'fortitude_save'), ('ref', 'reflex_save'), ('will', 'will_save'))
LEGACY_ALIGNMENTS = {'LG', 'NG', 'CG', 'LN', 'N', 'CN', 'LE', 'NE', 'CE'}

_memory = {}
_lock = threading.Lock()


class AonUnavailable(Exception):
    """AoN didn't answer (network down, timeout, or an error page)."""


def ascii_text(text):
    """Generated text stays ASCII (claude.md)."""
    for bad, good in ASCII_FIXES.items():
        text = text.replace(bad, good)
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')


def _query(body):
    try:
        response = requests.post(INDEX, json=body, timeout=TIMEOUT)
        response.raise_for_status()
        return [hit['_source'] for hit in response.json()['hits']['hits']]
    except (requests.RequestException, ValueError, KeyError, RuntimeError) as error:
        raise AonUnavailable(str(error)) from error


def valid_key(key):
    """A creature's key is its AoN page path, e.g. /Monsters.aspx?ID=731."""
    return isinstance(key, str) and bool(re.fullmatch(r'/(Monsters|NPCs)\.aspx\?ID=\d+', key))


# ------------------------------------------------------------------- search

def _summary(doc, source='aon'):
    traits = [t for t in doc.get('trait') or doc.get('traits') or [] if t not in LEGACY_ALIGNMENTS]
    sources = doc.get('source') or []
    return {
        'key': doc['url'],
        'name': ascii_text(doc['name']),
        'level': doc.get('level'),
        'hp': doc.get('hp'),
        'ac': doc.get('ac'),
        'perception': doc.get('perception'),
        'rarity': doc.get('rarity', 'common'),
        'traits': [ascii_text(t) for t in traits],
        'legacy': bool(doc.get('remaster_id')) or bool(LEGACY_ALIGNMENTS & set(doc.get('traits') or [])),
        'book': ascii_text(sources[0]) if sources else '',
        'campaign': any(s.startswith(AV_SOURCES) for s in sources),
        'source': source,
    }


def rank(results, query, favored=()):
    """Exact name first, then names that start with the query, then the
    campaign's own creatures, then remaster over legacy."""
    q = query.lower().strip()
    favored = {f.lower() for f in favored}

    def key(r):
        name = r['name'].lower()
        return (name != q, not name.startswith(q),
                not (r['campaign'] or name in favored), r['legacy'], len(name))
    return sorted(results, key=key)


def _local_search(query):
    q = query.lower().strip()
    best = {}
    for record in creatures():
        if q in record['name'].lower() and record['name'] not in best:
            best[record['name']] = find_creature(creatures(), record['name'])
    return [_summary(dict(c, trait=c.get('traits')), source='local') for c in best.values() if c]


def search(query, favored=()):
    """Creatures whose name matches, best first: {"results": [...], "source": "aon"|"local"}."""
    query = query.strip()[:60]
    if len(query) < 2:
        return {'results': [], 'source': 'aon'}
    body = {'size': SEARCH_SIZE, '_source': SUMMARY_FIELDS,
            'query': {'bool': {'filter': [{'term': {'category': 'creature'}}],
                               'must_not': [{'term': {'exclude_from_search': True}}],
                               'should': [{'match_phrase_prefix': {'name': query}},
                                          {'match': {'name': {'query': query, 'fuzziness': 'AUTO'}}}],
                               'minimum_should_match': 1}}}
    try:
        results, source = [_summary(d) for d in _query(body) if d.get('url')], 'aon'
    except AonUnavailable:
        results, source = _local_search(query), 'local'
    return {'results': rank(results, query, favored)[:20], 'source': source}


# -------------------------------------------------------------- stat blocks

def _abs_links(text):
    return re.sub(r'\]\((/[^)\s]*)\)', lambda m: f']({AON_BASE}{m.group(1)})', text)


def statblock_markdown(md):
    """The stat block part of an AoN page as plain markdown: lore, sidebars and
    AoN's layout tags dropped, action icons as [1] [2] [3] [R] [F]."""
    start = re.search(r'<title level="2"[^>]*right="(Creature|NPC)', md) or re.search(r'<title level="2"', md)
    if start:
        md = md[start.start():]
        end = re.search(r'<title level="[12]"|<document ', md[1:])
        md = md[:end.start() + 1] if end else md
    md = re.sub(r'<aside>.*?</aside>', '', md, flags=re.S)
    md = re.sub(r'<title[^>]*>.*?</title>', '', md, flags=re.S)
    md = re.sub(r'<traits>.*?</traits>', '', md, flags=re.S)
    md = re.sub(r'<actions string="([^"]+)"\s*/>', lambda m: ACTIONS.get(m.group(1), ''), md)
    md = re.sub(r'<br\s*/?>', '\n\n', md)
    md = re.sub(r'<[^>]+>', '\n', md)               # row, column, document and anything else
    md = re.sub(r'^\*\*Source\*\*.*$', '', md, flags=re.M)
    # AoN puts a field's label and value on separate lines; join them
    md = re.sub(r'(\*\*[A-Za-z ]+\*\*)\n(?=\S)', r'\1 ', md)
    md = re.sub(r'(\[[123RF]\])\n', r'\1 ', md)
    md = re.sub(r',\n(\*\*Damage\*\*)', r', \1', md)
    md = re.sub(r'[ \t]+\n', '\n', md)
    # Ability scores, and AC with the saves, on one line each
    md = re.sub(r'(\*\*(?:Str|Dex|Con|Int|Wis)\*\* [+-]\d+)\n+(?=\*\*(?:Dex|Con|Int|Wis|Cha)\*\*)', r'\1, ', md)
    md = re.sub(r'(\*\*(?:AC|Fort|Ref)\*\* [+-]?\d+[^\n]*)\n+(?=\*\*(?:Fort|Ref|Will)\*\*)', r'\1; ', md)
    md = re.sub(r'\n{3,}', '\n\n', md)
    return _abs_links(ascii_text(md)).strip()


STRIKE = re.compile(r'\*\*(Melee|Ranged)\*\*\s*(?:<actions string="[^"]*"\s*/>)?\s*'
                    r'(?P<name>[^\n+]+?)\s+(?P<bonus>[+-]\d+)\s*(?:\((?P<traits>[^\n]*?)\))?\s*,\s*'
                    r'\*\*Damage\*\*\s*(?P<damage>[^\n]+)')


def _plain(text):
    """Markdown links to their text."""
    return ascii_text(re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', text)).strip()


def parse_strikes(md):
    strikes = []
    for m in STRIKE.finditer(md):
        traits = _plain(m.group('traits') or '')
        strikes.append({
            'kind': m.group(1).lower(),
            'name': _plain(m.group('name')),
            'bonus': int(m.group('bonus')),
            'traits': traits,
            'agile': 'agile' in traits.lower(),
            'damage': _plain(m.group('damage')),
        })
    return strikes


SPELLS = re.compile(r'\*\*([A-Za-z ]*Spells|[A-Za-z ]*Rituals)\*\*\s*DC (\d+)(?:,\s*attack ([+-]\d+))?')


def parse_spells(md):
    return [{'name': ascii_text(m.group(1)), 'dc': int(m.group(2)),
             'attack': int(m.group(3)) if m.group(3) else None} for m in SPELLS.finditer(md)]


def _amounts(values):
    """{type: n}; AoN spells "resistance all 10" out to every damage type."""
    values = {k: v for k, v in (values or {}).items() if isinstance(v, (int, float))}
    if 'all' in values:
        values = {'all': values['all'], **{k: v for k, v in values.items() if v != values['all']}}
    return values


def normalize(doc):
    """An AoN creature document as the tracker's stat record."""
    md = doc.get('markdown') or ''
    traits = [ascii_text(t) for t in doc.get('trait') or [] if t not in LEGACY_ALIGNMENTS]
    saves = {short: doc.get(field) for short, field in SAVE_NAMES}
    return {
        'key': doc['url'],
        'name': ascii_text(doc['name']),
        'level': doc.get('level', 0),
        'hp': doc.get('hp') or 1,
        'hp_note': ascii_text(doc.get('hp_raw', '')).partition('(')[2].rstrip(') ').strip(),
        'ac': doc.get('ac'),
        'saves': saves,
        'perception': doc.get('perception'),
        'senses': ascii_text(doc.get('sense', '')),
        'skills': {k: v for k, v in (doc.get('skill_mod') or {}).items() if isinstance(v, int)},
        'speed': ascii_text(doc.get('speed_raw') or doc.get('speed_markdown') or ''),
        'immunities': [ascii_text(i) for i in doc.get('immunity') or []],
        'resistances': _amounts(doc.get('resistance')),
        'weaknesses': _amounts(doc.get('weakness')),
        'traits': traits,
        'rarity': doc.get('rarity', 'common'),
        'size': (doc.get('size') or [''])[0],
        'strikes': parse_strikes(md),
        'spells': parse_spells(md),
        'statblock': statblock_markdown(md),
        'url': AON_BASE + doc['url'],
        'legacy': bool(doc.get('remaster_id')),
        'source': 'aon',
    }


def from_local(record):
    """creatures.json as a stat record, for when AoN can't be reached."""
    return {
        'key': record['url'],
        'name': record['name'],
        'level': record['level'],
        'hp': record.get('hp') or 1,
        'hp_note': '',
        'ac': record.get('ac'),
        'saves': {'fort': None, 'ref': None, 'will': None},
        'perception': record.get('perception'),
        'senses': '',
        'skills': {},
        'speed': '',
        'immunities': record.get('immunities', []),
        'resistances': record.get('resistances', {}),
        'weaknesses': record.get('weaknesses', {}),
        'traits': [t for t in record.get('traits', []) if t not in LEGACY_ALIGNMENTS],
        'rarity': record.get('rarity', 'common'),
        'size': (record.get('size') or [''])[0],
        'strikes': [],
        'spells': [],
        'statblock': '\n\n'.join(record.get('attacks', []) + record.get('abilities', [])),
        'url': AON_BASE + record['url'],
        'legacy': False,
        'source': 'local',
    }


def _cache_path(key):
    kind, _, number = key.strip('/').partition('.aspx?ID=')
    return os.path.join(CACHE_DIR, f'{kind.lower()}-{number}.json')


def _read_cache(key):
    try:
        with open(_cache_path(key), 'r', encoding='utf-8') as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def _write_cache(key, stats):
    path = _cache_path(key)
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(path + '.tmp', 'w', encoding='utf-8') as f:
        json.dump(stats, f)
    os.replace(path + '.tmp', path)


def creature(key):
    """The stat record for an AoN page path, or None if there's no such creature.

    Asks AoN (once per process per creature), then falls back to the copy saved
    on disk, then to creatures.json.
    """
    if not valid_key(key):
        return None
    with _lock:
        if key in _memory:
            return copy.deepcopy(_memory[key])
    try:
        docs = _query({'size': 1, 'query': {'bool': {'filter': [{'term': {'category': 'creature'}},
                                                                 {'term': {'url': key}}]}}})
        stats = normalize(docs[0]) if docs else None
        if stats:
            _write_cache(key, stats)
    except AonUnavailable:
        stats = _read_cache(key)
        if stats is None:
            local = next((c for c in creatures() if c.get('url') == key), None)
            stats = from_local(local) if local else None
    if stats and stats['source'] == 'aon':
        with _lock:
            _memory[key] = copy.deepcopy(stats)
    return stats


def key_for_name(name):
    """The AoN page of a creature by name, from creatures.json (remaster preferred)."""
    record = find_creature(creatures(), name)
    return record['url'] if record else None
