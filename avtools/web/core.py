"""
What every part of the web app shares: the GM login check, request parsing,
and reading and writing data files.
"""

import json
import os
from functools import wraps

from flask import jsonify, request, session
from werkzeug.exceptions import BadRequest

from avtools.data import DATA_DIR, ROOT as PROJECT_ROOT
from avtools.web.render import render_markdown

# ------------------------------------------------------------------- GM login
# Anything that changes shared state (restocks, map pins, the dice jar, roll
# history) needs the GM password, which lives in the GM_PASSWORD secret. Pages
# and read-only APIs stay open. Without a password set, writes are open too,
# which is what you want running locally, but never on Fly.
GM_PASSWORD = os.environ.get('GM_PASSWORD', '')
ON_FLY = bool(os.environ.get('FLY_APP_NAME'))



def gm_write(view):
    """Refuse a write unless the GM has logged in (or no password is set locally)."""
    @wraps(view)
    def guarded(*args, **kwargs):
        if not GM_PASSWORD:
            if ON_FLY:
                return jsonify({'error': 'GM_PASSWORD is not set on this server.'}), 503
        elif not session.get('gm'):
            return jsonify({'error': 'GM login required.', 'login': True}), 401
        return view(*args, **kwargs)
    return guarded


def is_gm():
    return session.get('gm') or (not GM_PASSWORD and not ON_FLY)


def json_body():
    """The request's JSON object. A form or text/plain post (the kind another
    site can send) is refused, and so is anything that isn't an object."""
    body = request.get_json(silent=False)
    if not isinstance(body, dict):
        raise BadRequest('Expected a JSON object.')
    return body


def int_field(data, key, low, high, default=None):
    """An integer from the request body, or a 400 if it's missing or out of range."""
    value = data.get(key, default)
    try:
        value = int(value)
    except (TypeError, ValueError):
        raise BadRequest(f'{key} must be a whole number')
    if not low <= value <= high:
        raise BadRequest(f'{key} must be between {low} and {high}')
    return value

# DATA_DIR is where anything the app writes goes: restocked merchants, map
# pins, the GM's session (dice jar, history). On Fly it's a mounted volume,
# because a machine's own disk resets to the image every time it stops;
# locally it's the repo itself, same as running the generator by hand.


def data_file(rel):
    """The newest copy of a data file, on the volume or baked into the image.

    Newest wins both ways: a restock on the server beats the copy in the image,
    and a copy you regenerated locally and deployed beats an older restock.
    """
    candidates = [os.path.join(root, rel) for root in (DATA_DIR, PROJECT_ROOT)]
    existing = [path for path in candidates if os.path.exists(path)]
    return max(existing, key=os.path.getmtime) if existing else None


def merchant_path(subdir, filename):
    return data_file(os.path.join(subdir, filename))


def write_json_atomic(path, data):
    """Write to a temp file and swap it in, so a reader never sees half a file."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = f'{path}.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)


def markdown_page(path):
    """(title, html) for a markdown file; the title is its first # heading."""
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    first = content.split('\n', 1)[0]
    if first.startswith('# '):
        content = content.split('\n', 1)[1] if '\n' in content else ''
        return first[2:].strip(), render_markdown(content)
    return None, render_markdown(content)
