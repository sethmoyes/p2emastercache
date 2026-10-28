"""
Markdown to HTML for shop pages, traveling merchants and docs.

Python-Markdown does the conversion; a small pass over the result then fits it
to the site: tables scroll sideways on phones, an Image column that holds only
placeholders is dropped, and outside links open in a new tab. Styling comes
from the .md rules in tailwind/input.css, so the HTML carries no classes.
"""

import re
from functools import lru_cache

import markdown
from bs4 import BeautifulSoup

from avtools import items

PLACEHOLDER = re.compile('^\\s*(?:\U0001F5BC\uFE0F?)?\\s*$')  # empty, or the picture-frame emoji


def _drop_placeholder_image_column(table):
    headers = [th.get_text(strip=True).lower() for th in table.select('thead th')]
    if 'image' not in headers:
        return
    col = headers.index('image')
    rows = table.select('tbody tr')
    cells = [row.find_all('td')[col] for row in rows if len(row.find_all('td')) > col]
    if any(cell.find('img') or not PLACEHOLDER.match(cell.get_text()) for cell in cells):
        return
    table.select('thead th')[col].decompose()
    for row in rows:
        tds = row.find_all('td')
        if len(tds) > col:
            tds[col].decompose()


def render_markdown(text):
    html = markdown.markdown(text, extensions=['tables', 'fenced_code', 'sane_lists'])
    soup = BeautifulSoup(html, 'html.parser')

    for table in soup.find_all('table'):
        _drop_placeholder_image_column(table)
        wrapper = soup.new_tag('div', attrs={'class': 'table-scroll'})
        table.wrap(wrapper)

    for link in soup.find_all('a', href=True):
        href = link['href'].strip()
        if re.match(r'^https?://', href, re.I):
            link['target'] = '_blank'
            link['rel'] = 'noopener'
        elif not (href.startswith('#') or href.startswith('/')):
            del link['href']  # javascript:, data: and other schemes

    return str(soup)


# ---------------------------------------------------------------- shop pages
# A shop file is a header, then # sections (potions, scrolls, runes, items),
# each with ## groups holding one table. parse_shop turns the tables into item
# records so the page can show them as tiles or a list and open any of them in
# a details sheet. It reads old files (with an Image column) and new ones alike.

SECTION_KINDS = [('potion', 'potion', 'Potions'), ('scroll', 'scroll', 'Scrolls'),
                 ('rune', 'rune', 'Runes')]
RARITIES = ('common', 'uncommon', 'rare', 'unique')
FACT_COLUMNS = [('dc', 'DC'), ('traditions', 'Traditions'),
                ('range', 'Range'), ('traits', 'Traits')]
EMPTY = {'', 'n/a', '-'}
# Item art older restocks linked on AoN, which no longer serves it (all 404 since 2026-10)
DEAD_IMAGES = re.compile(r'^https://2e\.aonprd\.com/Images/', re.I)


def _section_kind(title):
    lowered = title.lower()
    for word, kind, label in SECTION_KINDS:
        if word in lowered:
            return kind, label
    return 'item', 'Items'


def _clean(text):
    return ' '.join(text.split())


def _spell_name(cell):
    """'SCROLL OF FIREBALL' -> 'Fireball', in the spell's own capitalisation."""
    name = re.sub(r'^scroll of\s+', '', cell, flags=re.I)
    known = _spell_names()
    return known.get(name.lower(), name.title())


@lru_cache(maxsize=None)
def _spell_names():
    return {name.lower(): name for name in items.details()['spells']}


def _table_items(table, kind, group_title, start):
    headers = [_clean(th.get_text()).lower() for th in table.select('thead th')]
    group_rarity = next((r for r in RARITIES if r in group_title.lower()), None)
    records, by_name = [], {}
    for row in table.select('tbody tr'):
        cells = row.find_all('td')
        cols = {h: cells[i] for i, h in enumerate(headers) if i < len(cells)}
        text = {h: _clean(cell.get_text()) for h, cell in cols.items()}
        spell = 'spell name' in text
        name = _spell_name(text['spell name']) if spell else text.get('name', '')
        if not name:
            continue
        if name in by_name:  # older files list each copy of a potion on its own row
            twin = by_name[name]
            twin['qty'] = (twin['qty'] or 1) + 1
            continue
        detail = items.item_detail(name, spell)
        link = cols.get('link').find('a', href=True) if cols.get('link') else None
        img = cols.get('image').find('img', src=True) if cols.get('image') else None
        rarity = (text.get('rarity') or group_rarity or 'common').lower()
        qty = text.get('qty') or text.get('quantity')
        facts = [(label, text[key]) for key, label in FACT_COLUMNS
                 if text.get(key, '').lower() not in EMPTY]
        if detail.get('subcategory'):
            facts.append(('Kind', detail['subcategory']))
        effect = text.get('effect', '')
        record = {
            'i': start + len(records),
            'name': name,
            'scroll': spell,
            'kind': 'scroll' if spell else items.item_kind(name, kind),
            'level': text.get('level', ''),
            'price': text.get('price', ''),
            'qty': int(qty) if qty and qty.isdigit() and int(qty) > 1 else None,
            'rarity': rarity if rarity in RARITIES else 'common',
            'facts': facts,
            'summary': effect if effect.lower() not in EMPTY else detail.get('summary', ''),
            'url': (items.aon_url(name, spell) if detail.get('url') or not link else link['href']),
            'image': items.image_overrides().get(name) or (
                img['src'] if img and re.match(r'^https://', img['src']) and not DEAD_IMAGES.match(img['src'])
                else None),
        }
        level = record['level']
        record['search'] = ' '.join([name, record['rarity'], record['kind'], *(value for _, value in facts),
                                     f'scroll rank {level}' if spell else f'level {level} lv {level}']).lower()
        records.append(record)
        by_name[name] = record
    return records


def parse_shop(text):
    """[{id, title, label, kind, intro, groups: [{title, intro, entries}]}] for a shop's markdown.

    Everything before the first # section (the shop's header) is left out: the
    page builds its header from the shop's config instead.
    """
    if text.startswith('# '):
        text = text.split('\n', 1)[1] if '\n' in text else ''  # the shop's name
    soup = BeautifulSoup(render_markdown(text), 'html.parser')
    sections, seen_ids, count = [], set(), 0
    section = group = None
    for node in soup.children:
        if not getattr(node, 'name', None) or node.name == 'hr':
            continue
        if node.name == 'h1':
            title = _clean(node.get_text())
            kind, label = _section_kind(title)
            sid = label.lower()
            while sid in seen_ids:
                sid += '-more'
            seen_ids.add(sid)
            section = {'id': sid, 'title': title.title(), 'label': label, 'kind': kind,
                       'intro': '', 'groups': []}
            sections.append(section)
            group = None
        elif section is None:
            continue
        elif node.name == 'h2':
            group = {'title': re.sub(r'\s*\(\d+\)\s*$', '', _clean(node.get_text())), 'intro': '', 'entries': []}
            section['groups'].append(group)
        elif node.name == 'div' and 'table-scroll' in node.get('class', []):
            if group is None:
                group = {'title': '', 'intro': '', 'entries': []}
                section['groups'].append(group)
            records = _table_items(node.find('table'), section['kind'], group['title'], count)
            group['entries'] += records
            count += len(records)
        elif group is not None:
            group['intro'] += str(node)
        else:
            section['intro'] += str(node)
    for section in sections:
        section['count'] = sum(len(g['entries']) for g in section['groups'])
    return [s for s in sections if s['count'] or s['groups']]
