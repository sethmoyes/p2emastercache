"""The atlas: tiled maps and their points of interest."""

import json
import os
import threading

from flask import Blueprint, jsonify, render_template, request

from avtools.web.core import DATA_DIR, PROJECT_ROOT, data_file, gm_write, is_gm, json_body, write_json_atomic

bp = Blueprint('atlas', __name__)

MAPS_REGISTRY = os.path.join(PROJECT_ROOT, 'etc', 'maps.json')


def load_maps():
    """Map registry written by bin/maps/tile_map.py."""
    try:
        with open(MAPS_REGISTRY, 'r', encoding='utf-8') as f:
            return json.load(f).get('maps', [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def poi_file(filename):
    """A POI file's name, if it is a plain file name listed under etc/."""
    name = os.path.basename(filename or '')
    return name if name and name == filename and name.endswith('.json') else None


def poi_path(filename):
    """The newest copy of a POI file (pins saved on the server, or the repo's)."""
    name = poi_file(filename)
    return data_file(os.path.join('etc', name)) if name else None


@bp.route('/atlas')
def atlas():
    """Interactive tiled map atlas with clickable points of interest.

    ?embed=1 hides the page header so the viewer can be framed inside another
    page, such as the players' market square.
    """
    return render_template('atlas.html', embed=request.args.get('embed') == '1', can_place=is_gm())


@bp.route('/api/maps', methods=['GET'])
def api_maps():
    return jsonify({'maps': load_maps()})


@bp.route('/api/pois/<map_id>', methods=['GET'])
def api_pois(map_id):
    """Every POI for a map, including unplaced ones (x/y null).

    A POI file can back several maps (the whole city and one district, say), so
    coordinates are stored per map under "coords". Here we flatten this map's
    entry into plain x/y, which keeps the viewer's job simple.
    """
    entry = next((m for m in load_maps() if m['id'] == map_id), None)
    if not entry:
        return jsonify({'error': f'unknown map: {map_id}'}), 404

    path = poi_path(entry.get('pois'))
    if not path:
        return jsonify({'map': map_id, 'groups': [], 'locations': [], 'count': 0})

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # A district map shows only its own slice of a shared POI file.
    only_groups = entry.get('poi_groups')
    locations = []
    for loc in data.get('locations', []):
        if only_groups and loc.get('group') not in only_groups:
            continue
        here = (loc.get('coords') or {}).get(map_id) or {}
        flat = {k: v for k, v in loc.items() if k != 'coords'}
        flat['x'] = here.get('x')
        flat['y'] = here.get('y')
        flat['approx'] = bool(here.get('approx'))
        locations.append(flat)

    groups = data.get('groups', [])
    if only_groups:
        groups = [g for g in groups if g in only_groups]

    return jsonify({
        'map': map_id,
        'group_by': data.get('group_by', 'type'),
        'groups': groups,
        'count': len(locations),
        'locations': locations,
    })


poi_lock = threading.Lock()


@bp.route('/api/pois/<map_id>', methods=['POST'])
@gm_write
def api_save_pois(map_id):
    """Persist pin coordinates from the viewer's placement mode.

    Body: {"placements": {"<poi id>": {"x": 0.42, "y": 0.61} | null, ...}}
    Coordinates are 0-1 fractions of the image, so they survive swapping the
    underlying map image for a higher-resolution one, and are stored under
    coords[<map id>] so one POI file can back several maps.
    """
    entry = next((m for m in load_maps() if m['id'] == map_id), None)
    if not entry:
        return jsonify({'error': f'unknown map: {map_id}'}), 404

    path = poi_path(entry.get('pois'))
    if not path:
        return jsonify({'error': f'no POI file configured for {map_id}'}), 400

    placements = json_body().get('placements') or {}
    if not isinstance(placements, dict):
        return jsonify({'error': 'placements must be an object'}), 400

    with poi_lock:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        updated = 0
        cleared = 0
        for loc in data.get('locations', []):
            if loc.get('id') not in placements:
                continue
            coords = placements[loc['id']]
            store = loc.setdefault('coords', {})
            if coords is None:
                if store.pop(map_id, None) is not None:
                    cleared += 1
            else:
                try:
                    x = min(1.0, max(0.0, float(coords['x'])))
                    y = min(1.0, max(0.0, float(coords['y'])))
                except (TypeError, ValueError, KeyError):
                    continue
                # A hand placement is deliberate, so it is no longer approximate.
                store[map_id] = {'x': round(x, 6), 'y': round(y, 6)}
                updated += 1

        data['count'] = len(data.get('locations', []))
        write_json_atomic(os.path.join(DATA_DIR, 'etc', poi_file(entry.get('pois'))), data)

    only_groups = entry.get('poi_groups')
    scoped = [l for l in data.get('locations', [])
              if not only_groups or l.get('group') in only_groups]
    placed = sum(1 for l in scoped if (l.get('coords') or {}).get(map_id))
    return jsonify({
        'success': True, 'updated': updated, 'cleared': cleared,
        'placed': placed, 'total': len(scoped),
    })
