"""Shared setup: import paths, a scratch DATA_DIR, and no network."""
import os
import socket
import sys
import tempfile

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)

# The app reads DATA_DIR at import: point it somewhere disposable first
os.environ['DATA_DIR'] = tempfile.mkdtemp(prefix='p2e-test-data-')
os.environ.pop('GM_PASSWORD', None)
os.environ.pop('FLY_APP_NAME', None)


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def refuse(*args, **kwargs):
        raise RuntimeError('tests must not touch the network')
    monkeypatch.setattr(socket.socket, 'connect', refuse)


@pytest.fixture(scope='session')
def app_module():
    from avtools.web import app
    return app


@pytest.fixture
def client(app_module):
    return app_module.app.test_client()
