# Pathfinder 2e Campaign Tools - Abomination Vaults

A small Flask app and a few scripts for running Abomination Vaults out of Otari:

- **GM page** (`/gm`): the dice-jar dungeon turn for Gauntlight Keep, traveling
  merchants, NPC and hazard generators. Restocking and backups are at `/gm/admin`.
- **Combat tracker** (`/gm/combat`): the party (saved on the server), initiative
  with fair digital d20s for the monsters, monster HP and conditions. Monsters come
  from a room code (`A10`), a name search on the Archives of Nethys, or a
  dungeon-turn roll's "Fight" button.
- **Players page** (`/players`): Otari's shops and the exploration guide.
- **Atlas** (`/atlas`): tiled maps of Otari, Absalom, Kortos and the Inner Sea with
  clickable places.

## Running it locally

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements-dev.txt
python3 -m avtools.web.app        # http://localhost:5001
pytest                            # the test suite, a few seconds
```

`bin/start.sh` starts the app too. With no `GM_PASSWORD` set, anything that
changes state (rolls, the dice jar, restocks, map pins) is open, and those
writes land in the repo itself, so a local restock or pin edit can be committed.
`FLASK_DEBUG=1` turns on the reloader and debugger.

## Deploying (Fly.io)

The app runs under gunicorn with one worker (the restock job and the session
file lock live in that process) on one machine with a volume mounted at `/data`
(`DATA_DIR`). Everything the server writes goes to the volume: restocked shops,
traveling merchants, map pins, the GM session (dice jar, roll history), the party
and the current fight (`state/heroes.json`, `state/combat.json`), and stat blocks
already fetched from AoN (`cache/aon/`, so a creature loads when AoN is down). When
a file exists on the volume and in the image, the newer copy wins.

```bash
fly secrets set GM_PASSWORD=... -a <app>     # required: writes are refused without it
fly deploy -a <app> --ha=false --build-arg GIT_SHA=$(git rev-parse --short HEAD)
```

`/healthz` reports the commit that is live. Keep the app at one machine: a volume
belongs to one machine, and a second one would see different shop stock.

**Backups.** "Download backup" on `/gm/admin` zips what the server has written,
laid out like the repo. `unzip -o` it in the repo root and commit it.

## Command-line tools

Run these from the repo root.

```bash
# Restock Otari's shops and roll traveling merchants (writes players/ and gm/)
python3 -m avtools.merchants --level 4
python3 -m avtools.merchants --settings-json '{"merchants": ["wrins_wonders"], "random_merchants": 0}'

# Print a full dungeon-turn table (every sum, every floor) to a markdown file
python3 -m avtools.dungeon_turn --level 4 --floors 3 --party-size 4 --output turn_table.md

# Atlas: slice a map into tiles, pull places from PathfinderWiki, rough-place pins
python3 bin/maps/tile_map.py etc/maps_src/absalom.png --id absalom --name "Absalom"
python3 bin/maps/scrape_wiki_locations.py absalom
python3 bin/maps/autoplace.py absalom

# Check equipment/creatures/deities against Archives of Nethys
python3 bin/data_management/check_data_integrity.py 10 equipment [--replace]

# Rebuild the CSS after changing Tailwind classes (needs Node)
bin/build_css.sh
```

## How the dungeon turn works

Every 10 minutes in the dungeon adds a die to the jar. When it holds five, roll
5d20 (the GM page can roll for you) and the roll spends those five dice.

- **Extreme rolls (5-15 or 90-100)** are always combat at a Severe or Extreme
  budget. They come up about once in 530 rolls.
- **Any other roll** is a quiet passage half the time. Otherwise:
  - 5-44 and 63-89: combat or an active threat
  - 45-62: an opportunity, complication or dilemma

Combat and most active threats are drawn from what actually lives on the floor
(`etc/floor_ecology.json`), scaled to the party's level and size. The rest come
from the event templates in `etc/dungeon_turn_events.json`.

## Where things live

| Path | What it is |
|---|---|
| `avtools/` | The package: dungeon turn, floor ecology, merchants, NPCs, hazards, and `data.py`, which loads everything in `etc/` |
| `avtools/web/` | The Flask app, its templates, and static assets (map tiles, CSS, JS) |
| `tests/` | The pytest suite |
| `bin/maps/` | Atlas tooling (tiling, PathfinderWiki places, pin placement) |
| `bin/data_management/` | The AoN data-integrity checker |
| `etc/` | Data the tools read: creatures, equipment, spells, events, floor ecology, shops, maps, the creatures in each keyed room (`room_encounters.json`) and PF2e conditions (`conditions.json`) |
| `players/` | Otari shop inventories, as players see them |
| `gm/` | Traveling merchants, the GM quick reference, the 2d20 overland table |
| `docs/` | The player-facing exploration guide |
| `common/` | Reference copied from the GM's campaign repo. `common/campaign-reference/floors/` is the room-by-room source for every floor; when it disagrees with anything else, it wins |
