"""
The campaign web app: the GM's table view, the players' market square, and
the atlas.

    python3 -m avtools.web.app        # http://localhost:5001
"""

import hashlib
import hmac
import os
import secrets

from flask import Flask, jsonify, session

from avtools.web import atlas, core, pages, restock, table
from avtools.web.core import json_body

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024
app.secret_key = (os.environ.get('SECRET_KEY')
                  or (hashlib.sha256(b'p2e-session:' + core.GM_PASSWORD.encode()).hexdigest() if core.GM_PASSWORD
                      else secrets.token_hex(32)))
app.config.update(
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=core.ON_FLY,
    PERMANENT_SESSION_LIFETIME=60 * 60 * 24 * 30,
)

for module in (pages, table, atlas, restock):
    app.register_blueprint(module.bp)


@app.route('/api/gm-login', methods=['POST'])
def gm_login():
    password = str(json_body().get('password', ''))
    if core.GM_PASSWORD and not hmac.compare_digest(password, core.GM_PASSWORD):
        return jsonify({'error': 'Incorrect password'}), 401
    session.permanent = True
    session['gm'] = True
    return jsonify({'success': True})


@app.errorhandler(400)
@app.errorhandler(413)
@app.errorhandler(415)
def bad_request(error):
    return jsonify({'error': getattr(error, 'description', str(error))}), error.code


@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'The server hit an error. Check the logs.'}), 500


if __name__ == '__main__':
    # FLASK_DEBUG=1 for the reloader and debugger; it stays on this machine only.
    print('Open http://localhost:5001  (Ctrl+C to stop)')
    app.run(debug=os.environ.get('FLASK_DEBUG') == '1', host='127.0.0.1', port=5001)
