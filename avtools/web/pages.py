"""The site's pages: landing, players' market square and shops, the GM pages."""

import os
import time

from flask import Blueprint, abort, jsonify, render_template

from avtools.merchants import MERCHANT_CONFIGS, merchant_slug
from avtools.web.atlas import load_maps
from avtools.web.core import PROJECT_ROOT, is_gm, markdown_page, merchant_path
from avtools.web.render import parse_shop
from avtools.web.themes import css_vars, theme

bp = Blueprint('pages', __name__)


@bp.route('/healthz')
def healthz():
    return jsonify({'ok': True, 'commit': os.environ.get('GIT_SHA', 'unknown')})

@bp.route('/')
def index():
    """Landing page with PLAYER and GM buttons"""
    return render_template('landing.html')

# Stand-in art for shops without a proprietor portrait: an icon for what the shop sells
SHOP_ART = {
    'otari_market': ('\U0001F6D2', ('#78350f', '#b45309')),
    'wrins_wonders': ('\U0001F52E', ('#4c1d95', '#7e22ce')),
    'odd_stories': ('\U0001F4DA', ('#1e3a8a', '#4338ca')),
    'gallentine_deliveries': ('\U0001F40E', ('#14532d', '#4d7c0f')),
    'blades_for_glades': ('\u2694\uFE0F', ('#374151', '#6b7280')),
    'crows_casks': ('\U0001F37A', ('#713f12', '#a16207')),
    'crooks_nook': ('\U0001F5DD\uFE0F', ('#111827', '#4b5563')),
    'the_rowdy_rockfish': ('\U0001F6CF\uFE0F', ('#7c2d12', '#c2410c')),
    'otari_fishery': ('\U0001F41F', ('#0c4a6e', '#0e7490')),
    'dawnflower_library': ('\u2600\uFE0F', ('#92400e', '#f59e0b')),
}
DEFAULT_ART = ('\U0001F3EA', ('#1f2937', '#4b5563'))


def shop_list():
    shops = []
    for config in MERCHANT_CONFIGS:
        slug = merchant_slug(config['name'])
        path = merchant_path('players', f'{slug}.md')
        shops.append({
            'slug': slug,
            'name': config['name'],
            'description': config['description'],
            'proprietor': config['proprietor'],
            'proprietor_name': config['proprietor'].split('(')[0].strip(),
            'portrait': config.get('portrait'),
            'icon': SHOP_ART.get(slug, DEFAULT_ART)[0],
            'tint': SHOP_ART.get(slug, DEFAULT_ART)[1],
            'specialties': config['specialties'],
            'updated': time.strftime('%b %d', time.localtime(os.path.getmtime(path))) if path else None,
        })
    return shops


@bp.route('/players')
def players():
    """Player-facing market square: Otari's shops, the town map, the guide"""
    return render_template('players.html', shops=shop_list(), otari=next(
        (m for m in load_maps() if m['id'] == 'otari'), None))


@bp.route('/players/shop/<slug>')
def player_shop(slug):
    config = next((c for c in MERCHANT_CONFIGS if merchant_slug(c['name']) == slug), None)
    path = merchant_path('players', f'{slug}.md') if config else None
    if not path:
        abort(404)
    with open(path, 'r', encoding='utf-8') as f:
        sections = parse_shop(f.read())
    proprietor, _, role = config['proprietor'].partition('(')
    return render_template(
        'shop.html', shop=config, slug=slug, theme=theme(slug), css_vars=css_vars, sections=sections,
        proprietor=proprietor.strip(), role=role.rstrip(') ').strip(),
        items=[item for s in sections for g in s['groups'] for item in g['entries']],
        stocked=time.strftime('%b %d', time.localtime(os.path.getmtime(path))))


@bp.route('/players/guide')
def player_guide():
    title, html = markdown_page(os.path.join(PROJECT_ROOT, 'docs', 'DUNGEON_EXPLORATION_GUIDE.md'))
    return render_template('doc.html', title=title or 'Exploration Guide', html=html)

@bp.route('/gm')
def gm():
    """The GM's table view: session bar, rolls, encounter card, quick tools"""
    return render_template('gm.html')


@bp.route('/gm/admin')
def gm_admin():
    """Restocking, backups and the test generator"""
    return render_template('gm_admin.html')
