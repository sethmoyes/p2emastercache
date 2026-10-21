"""The site's pages: landing, players' market square and shops, the GM pages."""

import os
import time

from flask import Blueprint, abort, jsonify, render_template

from avtools.merchants import MERCHANT_CONFIGS, merchant_slug
from avtools.web.atlas import load_maps
from avtools.web.core import PROJECT_ROOT, is_gm, markdown_page, merchant_path

bp = Blueprint('pages', __name__)


@bp.route('/healthz')
def healthz():
    return jsonify({'ok': True, 'commit': os.environ.get('GIT_SHA', 'unknown')})

@bp.route('/')
def index():
    """Landing page with PLAYER and GM buttons"""
    return render_template('landing.html')

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
    title, html = markdown_page(path)
    return render_template('shop.html', title=title or config['name'], html=html)


@bp.route('/players/guide')
def player_guide():
    title, html = markdown_page(os.path.join(PROJECT_ROOT, 'docs', 'DUNGEON_EXPLORATION_GUIDE.md'))
    return render_template('shop.html', title=title or 'Exploration Guide', html=html)

@bp.route('/gm')
def gm():
    """The GM's table view: session bar, rolls, encounter card, quick tools"""
    return render_template('gm.html')


@bp.route('/gm/admin')
def gm_admin():
    """Restocking, backups and the test generator"""
    return render_template('gm_admin.html')
