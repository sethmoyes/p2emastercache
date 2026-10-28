#!/usr/bin/env python3
"""
Rebuild avtools/web/static/icons/icons.svg, the icon sprite the shop pages use
(item kinds on the grid tiles, each shop's crest), from game-icons.net.

Add an icon by adding a line to ICONS and running this; it needs the network.
Pages use an icon as <svg><use href="/static/icons/icons.svg#i-NAME"></use></svg>,
coloured by CSS (fill: currentColor). The icons are CC BY 3.0; CREDITS.md lists
the authors, and the shop pages credit game-icons.net in their footer.

    python3 bin/build_icons.py
"""

import os
import re

import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'avtools', 'web', 'static', 'icons')
SOURCE = 'https://raw.githubusercontent.com/game-icons/icons/master/{}.svg'

# sprite id -> game-icons author/name
ICONS = {
    # item kinds
    'potion': 'lorc/standing-potion',
    'elixir': 'lorc/round-bottom-flask',
    'alchemy': 'lorc/bubbling-flask',
    'bomb': 'lorc/fire-bomb',
    'poison': 'lorc/poison-bottle',
    'herb': 'delapouite/herbs-bundle',
    'scroll': 'lorc/scroll-unfurled',
    'rune': 'lorc/rune-stone',
    'wand': 'lorc/fairy-wand',
    'staff': 'lorc/wizard-staff',
    'sword': 'lorc/broadsword',
    'axe': 'delapouite/war-axe',
    'hammer': 'delapouite/warhammer',
    'dagger': 'lorc/plain-dagger',
    'spear': 'lorc/spears',
    'bow': 'delapouite/bow-arrow',
    'gun': 'john-colburn/pistol-gun',
    'ammo': 'delapouite/quiver',
    'armor': 'lorc/breastplate',
    'shield': 'lorc/checked-shield',
    'ring': 'delapouite/diamond-ring',
    'neck': 'lorc/gem-pendant',
    'boots': 'lorc/boots',
    'cloak': 'lucasms/cloak',
    'hat': 'lorc/pointy-hat',
    'gloves': 'delapouite/gauntlet',
    'bracers': 'delapouite/bracer',
    'belt': 'lucasms/belt',
    'eyes': 'delapouite/steampunk-goggles',
    'held': 'lorc/crystal-ball',
    'talisman': 'delapouite/tribal-pendant',
    'gem': 'lorc/gems',
    'tattoo': 'lorc/ink-swirl',
    'book': 'delapouite/spell-book',
    'animal': 'delapouite/horse-head',
    'snare': 'lorc/wolf-trap',
    'gadget': 'lorc/gears',
    'tools': 'delapouite/toolbox',
    'gear': 'delapouite/backpack',
    'food': 'delapouite/bread',
    'drink': 'lorc/beer-stein',
    'light': 'lorc/lantern',
    'item': 'lorc/swap-bag',
    # shop crests
    'coins': 'delapouite/coins-pile',
    'star': 'delapouite/falling-star',
    'open-book': 'lorc/open-book',
    'horseshoe': 'delapouite/horseshoe',
    'crossed-swords': 'lorc/crossed-swords',
    'barrel': 'delapouite/barrel',
    'key': 'lorc/skeleton-key',
    'candle': 'lorc/candle-holder',
    'hook': 'lorc/fishing-hook',
    'sunrise': 'lorc/sunrise',
}

BACKGROUND = re.compile(r'<path d="M0 0h512v512H0z"\s*/>')


def symbol(name, svg):
    svg = BACKGROUND.sub('', svg)
    paths = re.findall(r'<path\b[^>]*\bd="([^"]+)"', svg)
    if not paths:
        raise ValueError(f'{name}: no paths')
    return f'<symbol id="i-{name}" viewBox="0 0 512 512"><path d="{" ".join(paths)}"/></symbol>'


def main():
    symbols, authors = [], {}
    for name, source in ICONS.items():
        response = requests.get(SOURCE.format(source), timeout=30)
        response.raise_for_status()
        symbols.append(symbol(name, response.text))
        authors.setdefault(source.split('/')[0], []).append(source)
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, 'icons.svg'), 'w', encoding='ascii') as f:
        f.write('<svg xmlns="http://www.w3.org/2000/svg" style="display:none">\n')
        f.write('\n'.join(symbols) + '\n</svg>\n')
    with open(os.path.join(OUT, 'CREDITS.md'), 'w', encoding='ascii') as f:
        f.write('# Icon credits\n\nIcons from [game-icons.net](https://game-icons.net), '
                'licensed [CC BY 3.0](https://creativecommons.org/licenses/by/3.0/). '
                'Built into `icons.svg` by `bin/build_icons.py` (backgrounds removed, '
                'recoloured by CSS).\n\n')
        for author, sources in sorted(authors.items()):
            f.write(f"- **{author}**: {', '.join(s.split('/')[1] for s in sources)}\n")
    print(f'OK {len(symbols)} icons -> {OUT}/icons.svg')


if __name__ == '__main__':
    main()
