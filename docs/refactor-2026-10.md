# October 2026 Refactor: Notes for Agents

What changed in the October 2026 cleanup, why, and what to know before you
touch the code. Read this before working on anything older than the refactor:
paths, routes and data sources from before it are gone.

## Status

- Work is on branch `cleanup` (off `master`). It has not been merged, pushed or
  deployed as of 2026-10-21. Check `git log master..cleanup` before assuming
  either way.
- The test suite passes: `pip install -r requirements-dev.txt && pytest`
  (455 tests, a few seconds, no network).
- The Docker image build was not verified (no Docker daemon on the machine it
  was done on). The only Dockerfile change that matters is the gunicorn target,
  `avtools.web.app:app`.

## Layout: before and after

| Before | After |
|---|---|
| `bin/web/dungeon_turn_app.py` (one 1,400-line file) | `avtools/web/app.py` plus blueprints: `core.py`, `pages.py`, `table.py`, `atlas.py`, `restock.py` |
| `bin/web/templates/`, `bin/web/static/` | `avtools/web/templates/`, `avtools/web/static/` |
| `bin/generators/generate_dungeon_turn_v2.py` | `avtools/dungeon_turn.py` |
| `bin/generators/floor_ecology.py` | `avtools/ecology.py` |
| `bin/generators/template_selector.py`, `bin/event_loader.py` | `avtools/events.py` (selection) and `avtools/data.py` (loading) |
| `bin/event_validation.py` | `avtools/validation.py` |
| `bin/generators/generate_merchants.py` | `avtools/merchants.py` |
| `bin/generators/generate_npc_lore.py`, `generate_hazard.py` | `avtools/npcs.py`, `avtools/hazards.py` |
| `bin/scrapers/scrape_wiki_locations.py` | `bin/maps/scrape_wiki_locations.py` |
| `bin/web/build_css.sh`, `start.sh` | `bin/build_css.sh`, `bin/start.sh` |
| `bin/web/requirements.txt` | `requirements.txt` (pinned), `requirements-dev.txt`, `pyproject.toml` |
| no tests (13 markdown tests) | `tests/` |

Run things as modules from the repo root (or `pip install -e .` first):

```bash
python3 -m avtools.web.app                      # the app, http://localhost:5001
python3 -m avtools.merchants --level 4          # restock shops into players/ and gm/
python3 -m avtools.dungeon_turn --floors 3 --output table.md
pytest
```

There are no `sys.path` hacks left. Import from the package:
`from avtools.data import ...`, `from avtools.merchants import ...`.

## How the pieces fit

**`avtools/data.py`** is the only place that knows where things live:
- `ROOT`, `ETC`, and `DATA_DIR`, read from the environment at import; it defaults
  to the repo root locally and is `/data` (a Fly volume) in production.
- Cached loaders: `creatures()`, `events()`, `floor_ecology()`, `shops()`.
- `find_creature(records, name)`. `creatures.json` holds legacy and remaster
  stat blocks under the same name; this picks the remaster one (no alignment
  trait, newest AoN id). Always use it instead of matching names yourself.

**The web app** (`avtools/web/`):
- `core.py` has `gm_write` (the decorator every state-changing route needs),
  `json_body()` (rejects non-JSON bodies, which blocks cross-site form posts),
  `int_field()` (validated ints, a 400 otherwise), `data_file()` (newest copy wins
  between `DATA_DIR` and the repo), and `markdown_page()`.
- Auth: `GM_PASSWORD` env var. Without it, writes are open locally and refused
  (503) on Fly. Login is `POST /api/gm-login`, which sets a Flask session cookie
  (SameSite=Lax). Pages and read-only APIs are open.
- The GM session (floor, party level and size, dice jar, Prepared tokens, last
  20 full events) is one JSON file at `DATA_DIR/state/session.json`, changed only
  through `update_session()` under a lock. API: `GET/POST /api/session`.
- Everything the server writes goes under `DATA_DIR`: `players/*.md` (shops),
  `gm/traveling_merchant_N.md`, `etc/*_locations.json` (map pins), `state/`.
  `GET /api/export` (GM only) zips it in the repo's layout.
- Markdown is rendered by `avtools/web/render.py` (Python-Markdown plus a cleanup
  pass) and styled by the `.md` rules in `avtools/web/tailwind/input.css`.
- CSS is compiled Tailwind in `avtools/web/static/css/app.css`. After changing
  classes in templates, JS or the renderer, run `bin/build_css.sh` (needs Node;
  it pins the public npm registry because the user's npm config points at a
  private one). Leaflet is vendored in `static/vendor/`. No CDNs.
- Frontend JS lives in `static/js/`: `common.js` (`api()`, `esc()`, login
  prompt), `encounter_card.js`, `gm.js`, `admin.js`. Escape everything you
  interpolate into HTML with `esc()`.

**Routes** (the full list; anything else was removed on purpose):

| Area | Routes |
|---|---|
| Pages | `/`, `/players`, `/players/shop/<slug>`, `/players/guide`, `/gm`, `/gm/admin`, `/atlas`, `/healthz` |
| Login | `POST /api/gm-login` |
| Table | `GET/POST /api/session`, `POST /api/encounter`, `GET /api/generate-npc`, `POST /api/generate-hazard`, `GET /api/gm-doc/<id>` |
| Atlas | `GET /api/maps`, `GET/POST /api/pois/<map_id>` |
| Merchants | `GET /api/gm-merchants`, `GET /api/gm-merchant/<file>`, `GET /api/merchant-generator`, `POST /api/merchant-generator/run`, `GET /api/merchant-generator/status`, `GET /api/export` |

## Sources of truth

1. `common/campaign-reference/floors/` (the book, floor by floor) beats
   everything else in the repo.
2. `etc/floor_ecology.json` is the only source of floor names and of what lives
   on each floor. Nothing else in the code restates floor data.
3. `etc/otari_shops.json` says who runs each shop; `MERCHANT_CONFIGS` in
   `avtools/merchants.py` says what each one stocks.
4. Merchant numbers live in `SETTINGS_SCHEMA`; the dice bands live in
   `get_category_from_sum`. `claude.md` points at them rather than repeating them.

## Data notes

- `equipment.json` files about 94% of items under `type: "adventuring"`. The
  merchant generator derives a real `kind` from `item_category` at load time
  (`prepare_equipment`) and skips priceless, duplicate and unsellable entries.
  The JSON file itself was not rewritten.
- `spells.json` has about 570 legacy and remaster duplicate pairs;
  `prepare_spells` keeps one per name and only the four traditions.
- `creatures.json` saves, creature types and skills are empty for every record.
  Fixing that needs a re-scrape through the user's integrity tools, which agents
  must not run (see `claude.md`).
- `etc/dungeon_turn_events.json`: OPPORTUNITY, COMPLICATION and DILEMMA were
  rewritten from the floor docs just before this refactor; ACTIVE_THREAT was
  rewritten during it (99 events). Every creature reference is copied from
  `creatures.json`. The field format is in `etc/dungeon_turn_events_schema.md`.
  `tests/test_data.py` enforces fields, validation, ASCII and stat accuracy:
  run it after editing events.

## Removed on purpose (don't bring back)

- `/api/view-doc` and `/api/download-doc` (they served any file on the machine)
  and the six admin routes that ran scrapers and data rewrites as subprocesses.
- Dungeon Turn V1, the 4d20 overland generator and `expanded_pools.json` (built
  from a corrupt backup), the scrapers, `creatures_backup.json`, the
  "context" system (space type, recent combat: no event used it), the toy
  merchant, 4d20 and V1 routes, `/api/roll`, `/api/events`, `/api/test-ghoul`.
- The V2 generator's fallback combat table and per-floor flavor strings (they
  contradicted the floor docs).
- `etc/gauntlight_keep_levels.md`, `inner_sea_region.md` and `players_guide.md`
  were byte-identical copies of the files in `common/campaign-reference/etc/`;
  only those remain.
- `gm/random_merchant_N:_name.md` files (colons break Windows); restocks write
  `gm/traveling_merchant_N.md` and replace the whole set.

## Gotchas

- When you overwrite an existing file, the editor tool keeps that file's
  encoding. The old README was UTF-16 and the rewrite silently stayed UTF-16.
  Delete a file before rewriting it if its encoding is suspect, and check with
  `file`.
- Locally, `DATA_DIR` is the repo, so running the app or a restock writes into
  `players/`, `gm/`, `etc/` and `state/` (`state/` is gitignored).
- Newest wins between the volume and the image. A freshly committed shop file
  will replace the stock on the live volume at the next deploy, so export the
  volume (`/gm/admin`, "Download backup") before committing regenerated shops.
- Named enemies (Cratonys, Khurfel, Urthagul and the like) never appear as
  incidental encounters; see `claude.md`.

## Not done

- Merchants are still written and served as markdown; moving them to JSON with
  templates was in the plan but skipped as low value.
- Randomness isn't injectable; tests seed `random` instead.

## Deployment TODO (needs the user)

1. Decide whether to merge `cleanup` into `master`.
2. Pick which Fly app's volume holds the real shop stock, export it, and commit
   it. Then fix the old (wrong) shopkeeper names in those `players/*.md`
   headers; doing it before the export would replace the live stock.
3. The user sets `fly secrets set GM_PASSWORD=...`. Never handle the password.
4. Consolidate the two Fly apps into one, then deploy with
   `fly deploy -a <app> --ha=false --build-arg GIT_SHA=$(git rev-parse --short HEAD)`.
   Keep one machine per app.
5. The traveling merchants on the live volume still use the old file names, so
   the GM list will be empty until the first restock after deploying.
