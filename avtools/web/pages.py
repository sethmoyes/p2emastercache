"""The site's pages: landing, players' market square and shops, the GM pages."""

import json
import os
import time

from flask import Blueprint, Response, abort, jsonify, render_template, request

from avtools import items
from avtools.merchants import MERCHANT_CONFIGS, merchant_slug
from avtools.pathbuilder import build_pack
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
    'the_knotted_charm': ('\U0001F9FF', ('#3b0764', '#0f766e')),
}
DEFAULT_ART = ('\U0001F3EA', ('#1f2937', '#4b5563'))


def shop_list():
    shops = []
    for config in MERCHANT_CONFIGS:
        slug = merchant_slug(config['name'])
        path = merchant_path('players', f'{slug}.md')
        if config.get('optional') and not path:
            continue  # closed (the GM hasn't opened it with a restock)
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


def _shop(slug):
    """(config, path, sections) for a shop with stock on file, else a 404."""
    config = next((c for c in MERCHANT_CONFIGS if merchant_slug(c['name']) == slug), None)
    path = merchant_path('players', f'{slug}.md') if config else None
    if not path:
        abort(404)
    with open(path, 'r', encoding='utf-8') as f:
        return config, path, parse_shop(f.read())


def _entries(sections):
    return [item for s in sections for g in s['groups'] for item in g['entries']]


@bp.route('/players/shop/<slug>')
def player_shop(slug):
    config, path, sections = _shop(slug)
    proprietor, _, role = config['proprietor'].partition('(')
    return render_template(
        'shop.html', shop=config, slug=slug, theme=theme(slug), css_vars=css_vars, sections=sections,
        proprietor=proprietor.strip(), role=role.rstrip(') ').strip(), items=_entries(sections),
        pick_key=pick_key, scroll_rules=(items.SCROLL_CASTING, items.SCROLL_LEARNING), stocked=time.strftime('%b %d', time.localtime(os.path.getmtime(path))))


def pick_key(item):
    """What the Pathbuilder form sends for an item: a spell and an item can share a name."""
    return ('scroll:' if item['scroll'] else 'item:') + item['name']


@bp.route('/players/shop/<slug>/pathbuilder.json', methods=['GET', 'POST'])
def player_shop_pathbuilder(slug):
    """The shop's items as a Pathbuilder 2e custom pack: all of them, or the ones the form picked.
    Read-only, so a plain form post is fine here."""
    _, _, sections = _shop(slug)
    entries = _entries(sections)
    if request.method == 'POST':
        picked = set(request.form.getlist('item'))
        entries = [item for item in entries if pick_key(item) in picked]
        if not entries:
            return jsonify({'error': 'Pick at least one item.'}), 400
    body = json.dumps(build_pack(entries), indent=1)
    return Response(body, mimetype='application/json', headers={
        'Content-Disposition': f'attachment; filename="otari-{slug}-pathbuilder.json"'})


@bp.route('/players/pathbuilder')
def player_pathbuilder_help():
    title, html = markdown_page(os.path.join(PROJECT_ROOT, 'docs', 'PATHBUILDER_GUIDE.md'))
    return render_template('doc.html', title=title or 'Pathbuilder', html=html)


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
