"""
Merchants on the GM side: traveling merchants, restocking Otari's shops in the
background, and the backup of everything the server has written.
"""

import io
import json
import os
import re
import subprocess
import sys
import threading
import time
import zipfile

from flask import Blueprint, Response, jsonify, request

from avtools.merchants import MERCHANT_CONFIGS, SETTINGS_SCHEMA, TRAVELING_FILE, merchant_slug, normalize_settings
from avtools.web.core import DATA_DIR, PROJECT_ROOT, gm_write, json_body, markdown_page

bp = Blueprint('restock', __name__)


def traveling_merchant_dir():
    """The gm/ folder holding the newest set of traveling merchants.

    A restock writes the whole set at once, so the set comes from whichever
    copy (volume or image) was written last, never a mix of the two.
    """
    newest, newest_time = None, -1
    for root in (DATA_DIR, PROJECT_ROOT):
        gm_dir = os.path.join(root, 'gm')
        if not os.path.isdir(gm_dir):
            continue
        times = [os.path.getmtime(os.path.join(gm_dir, name))
                 for name in os.listdir(gm_dir) if TRAVELING_FILE.match(name)]
        if times and max(times) > newest_time:
            newest, newest_time = gm_dir, max(times)
    return newest


@bp.route('/api/gm-merchants', methods=['GET'])
def get_gm_merchants():
    """The current traveling merchants, in slot order."""
    gm_dir = traveling_merchant_dir()
    merchants = []
    for name in os.listdir(gm_dir) if gm_dir else []:
        slot = TRAVELING_FILE.match(name)
        if not slot:
            continue
        path = os.path.join(gm_dir, name)
        with open(path, 'r', encoding='utf-8') as f:
            first = f.readline()
        merchants.append({
            'file': name[:-3],
            'slot': int(slot.group(1)),
            'name': first.lstrip('#').strip() or name[:-3],
            'updated': os.path.getmtime(path),
        })
    merchants.sort(key=lambda m: m['slot'])
    return jsonify({'merchants': merchants})


@bp.route('/api/gm-merchant/<merchant_file>', methods=['GET'])
def get_gm_merchant(merchant_file):
    """Load a traveling merchant and return it as HTML"""
    gm_dir = traveling_merchant_dir()
    if not gm_dir or not TRAVELING_FILE.match(f'{merchant_file}.md'):
        return jsonify({'error': 'Merchant not found'}), 404
    path = os.path.join(gm_dir, f'{merchant_file}.md')
    if not os.path.exists(path):
        return jsonify({'error': 'Merchant not found'}), 404

    title, html = markdown_page(path)
    return jsonify({'title': title or merchant_file.replace('_', ' ').title(), 'html': html})

# ------------------------------------------------------------------ Export
# What the server has written (restocks, pins, the session), zipped with the
# same layout as the repo, so `unzip -o export.zip` in the repo root brings it
# home to be committed.
EXPORT_GLOBS = [('players', '.md'), ('gm', '.md'), ('etc', '_locations.json'), ('state', '.json')]


@bp.route('/api/export', methods=['GET'])
@gm_write
def export_data():
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as archive:
        for folder, suffix in EXPORT_GLOBS:
            path = os.path.join(DATA_DIR, folder)
            if not os.path.isdir(path):
                continue
            for name in sorted(os.listdir(path)):
                if name.endswith(suffix):
                    archive.write(os.path.join(path, name), f'{folder}/{name}')
    stamp = time.strftime('%Y-%m-%d')
    return Response(buffer.getvalue(), mimetype='application/zip',
                    headers={'Content-Disposition': f'attachment; filename="p2e-export-{stamp}.zip"'})


# ---------------------------------------------------------- Merchant restocking

PROGRESS_LINE = re.compile(r'^\[(\d+)/(\d+)\] Generating (.+?)\.\.\.$')

# The latest restock run. Only one runs at a time, and it lives in this process,
# which is why gunicorn runs a single worker (see Dockerfile).
merchant_job = None
merchant_job_lock = threading.Lock()


def run_merchant_job(job):
    """Run the generator script, recording its output and progress on the job."""
    try:
        process = subprocess.Popen(
            [sys.executable, '-u', '-m', 'avtools.merchants',
             '--settings-json', json.dumps(job['settings']),
             '--output-root', DATA_DIR],
            cwd=PROJECT_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        for line in process.stdout:
            line = line.rstrip()
            job['log'].append(line)
            progress = PROGRESS_LINE.match(line)
            if progress:
                job['step'], job['total'] = int(progress.group(1)), int(progress.group(2))
                job['current'] = progress.group(3)
        process.wait()
        job['status'] = 'done' if process.returncode == 0 else 'failed'
    except Exception as e:
        job['log'].append(f'ERROR: {e}')
        job['status'] = 'failed'
    job['finished'] = time.time()


def merchant_job_view(job, since=0):
    """The job as the GM page sees it, with log lines from `since` onward."""
    return {
        'status': job['status'],
        'step': job['step'],
        'total': job['total'],
        'current': job['current'],
        'started': job['started'],
        'finished': job['finished'],
        'log': job['log'][since:],
        'next': len(job['log']),
    }


@bp.route('/api/merchant-generator', methods=['GET'])
def merchant_generator_config():
    """Everything the restock form needs: the settings schema and the shop list."""
    return jsonify({
        'schema': SETTINGS_SCHEMA,
        'merchants': [
            {'slug': merchant_slug(c['name']), 'name': c['name'], 'specialties': c['specialties']}
            for c in MERCHANT_CONFIGS
        ],
        'job': merchant_job_view(merchant_job) if merchant_job else None,
    })


@bp.route('/api/merchant-generator/run', methods=['POST'])
@gm_write
def start_merchant_job():
    """Start a restock in the background; the GM page polls the status endpoint."""
    global merchant_job
    settings = normalize_settings(json_body())
    if not settings['merchants'] and not settings['random_merchants']:
        return jsonify({'error': 'Pick at least one shop or traveling merchant.'}), 400

    with merchant_job_lock:
        if merchant_job and merchant_job['status'] == 'running':
            return jsonify({'error': 'A restock is already running.'}), 409
        job = {
            'status': 'running',
            'settings': settings,
            'step': 0,
            'total': len(settings['merchants']) + settings['random_merchants'],
            'current': None,
            'started': time.time(),
            'finished': None,
            'log': [],
        }
        merchant_job = job
        threading.Thread(target=run_merchant_job, args=(job,), daemon=True).start()

    return jsonify(merchant_job_view(job))


@bp.route('/api/merchant-generator/status', methods=['GET'])
def merchant_job_status():
    if not merchant_job:
        return jsonify({'status': 'idle'})
    return jsonify(merchant_job_view(merchant_job, request.args.get('since', 0, type=int)))
