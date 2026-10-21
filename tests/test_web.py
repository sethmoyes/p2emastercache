"""The web app: pages, the GM login, the session, and the routes that are gone."""
import io
import zipfile

import pytest

from render import render_markdown


@pytest.mark.parametrize('url', ['/', '/players', '/players/shop/wrins_wonders', '/players/guide',
                                 '/gm', '/gm/admin', '/atlas', '/healthz', '/api/maps', '/api/session',
                                 '/api/gm-merchants', '/api/gm-doc/quick-reference', '/api/merchant-generator'])
def test_pages_load(client, url):
    assert client.get(url).status_code == 200


@pytest.mark.parametrize('method,url', [('POST', '/api/view-doc'), ('GET', '/api/download-doc?path=/etc/passwd'),
                                        ('POST', '/api/scrape-spells'), ('POST', '/api/run-data-integrity'),
                                        ('GET', '/api/gm-doc/..%2F..%2Fetc%2Fpasswd'), ('GET', '/players/shop/..')])
def test_unsafe_routes_are_gone(client, method, url):
    assert client.open(url, method=method).status_code in (404, 405)


@pytest.fixture
def password(app_module, monkeypatch):
    monkeypatch.setattr(app_module, 'GM_PASSWORD', 'sekrit')


@pytest.mark.parametrize('url,body', [('/api/session', {'add': {'dice_jar': 1}}),
                                      ('/api/encounter', {'sum': 50}),
                                      ('/api/pois/otari', {'placements': {}}),
                                      ('/api/merchant-generator/run', {})])
def test_writes_need_the_gm_password(client, password, url, body):
    assert client.post(url, json=body).status_code == 401


def test_login_unlocks_writes(client, password):
    assert client.post('/api/gm-login', json={'password': 'wrong'}).status_code == 401
    assert client.post('/api/gm-login', json={'password': 'sekrit'}).status_code == 200
    assert client.post('/api/session', json={'set': {'dice_jar': 2}}).status_code == 200


def test_writes_refused_on_fly_without_a_password(client, app_module, monkeypatch):
    monkeypatch.setattr(app_module, 'ON_FLY', True)
    assert client.post('/api/session', json={'add': {'dice_jar': 1}}).status_code == 503


def test_cross_site_form_posts_are_refused(client):
    r = client.post('/api/merchant-generator/run', data='{}', content_type='text/plain')
    assert r.status_code == 415


def test_session_jar_and_rolls(client):
    client.post('/api/session', json={'set': {'dice_jar': 0, 'floor': 3}, 'clear_history': True})
    client.post('/api/session', json={'add': {'dice_jar': 6}})  # a long rest
    assert client.get('/api/session').get_json()['dice_jar'] == 6
    event = client.post('/api/encounter', json={'sum': 50, 'use_jar': True}).get_json()
    state = client.get('/api/session').get_json()
    assert state['dice_jar'] == 1
    assert state['history'][-1]['event']['title'] == event['title']
    assert event['floor'] == 3


@pytest.mark.parametrize('body', [{'sum': 3}, {'sum': 'x'}, {}, {'sum': 50, 'floor': 11},
                                  {'sum': 50, 'party_level': 0}])
def test_bad_encounter_input_is_a_400(client, body):
    assert client.post('/api/encounter', json=body).status_code == 400


def test_export_is_a_zip_laid_out_like_the_repo(client):
    client.post('/api/session', json={'add': {'dice_jar': 1}})
    archive = zipfile.ZipFile(io.BytesIO(client.get('/api/export').data))
    assert 'state/session.json' in archive.namelist()


def test_markdown_drops_placeholder_image_columns_and_unsafe_links():
    html = render_markdown('| Image | Name |\n|---|---|\n| \U0001F5BC️ | Rope |\n\n[x](javascript:alert(1)) [y](https://a.example)')
    assert 'Image' not in html and 'Rope' in html
    assert 'javascript:' not in html
    assert 'target="_blank"' in html
    assert 'table-scroll' in html
