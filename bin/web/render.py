"""
Markdown to HTML for shop pages, traveling merchants and docs.

Python-Markdown does the conversion; a small pass over the result then fits it
to the site: tables scroll sideways on phones, an Image column that holds only
placeholders is dropped, and outside links open in a new tab. Styling comes
from the .md rules in tailwind/input.css, so the HTML carries no classes.
"""

import re

import markdown
from bs4 import BeautifulSoup

PLACEHOLDER = re.compile(r'^\s*(?:\U0001F5BC️?)?\s*$')  # empty, or the picture-frame emoji


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
