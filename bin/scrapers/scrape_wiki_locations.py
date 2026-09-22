#!/usr/bin/env python3
"""
Build POI datasets for the atlas from PathfinderWiki.

One entry per place: name, layer group, type (drives the map icon), a short
summary, and a canonical wiki link. No online source carries map coordinates,
so everything starts unplaced and is positioned in the viewer's placement mode.

Coordinates live in "coords", keyed by map id, because one place can sit on
several maps at once (a district map and the whole-city map, say) at different
positions. Each value is a 0-1 fraction of that image.

    python3 bin/scrapers/scrape_wiki_locations.py            # every map
    python3 bin/scrapers/scrape_wiki_locations.py absalom    # just one

Coordinates already present in an existing file are preserved on re-run.
Wiki text is CC BY-SA 3.0. Pathfinder and Golarion are Paizo Inc. trademarks.
"""

import json
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

API = "https://pathfinderwiki.com/w/api.php"
UA = "p2emastercache-campaign-tool/1.0 (personal GM tool)"
ROOT = Path(__file__).resolve().parents[2]

ABSALOM_DISTRICTS = [
    "Ascendant Court", "The Coins", "The Docks", "Eastgate", "Foreign Quarter",
    "Ivy District", "Petal District", "Precipice Quarter", "The Puddles",
    "Westgate", "Wise Quarter", "Undercity",
]

DISTRICT_ALIASES = {
    "Coins": "The Coins", "Docks": "The Docks",
    "Puddles": "The Puddles", "Undercity (Absalom)": "Undercity",
}

MAPS = {
    "absalom": {
        "out": "absalom_locations.json",
        "categories": ["Category:Absalom/Locations"],
        "group_by": "district",
    },
    "otari": {
        "out": "otari_locations.json",
        "categories": ["Category:Otari/Locations"],
        "group_by": "type",
    },
    "kortos": {
        "out": "kortos_locations.json",
        "categories": ["Category:Isle of Kortos/Locations",
                       "Category:Isle of Kortos/Settlements"],
        "group_by": "type",
    },
    "inner-sea": {
        "out": "inner_sea_locations.json",
        "categories": ["Category:Nations of Avistan", "Category:Nations of Garund",
                       "Category:Avistan/Geography", "Category:Garund/Geography"],
        "group_by": "type",
    },
}

# Wiki type-categories mapped to an icon key; first match wins, so specific first.
TYPE_RULES = [
    ("tavern",        ["tavern", "inn locations", "alehouse", "bar locations", "brewer"]),
    ("restaurant",    ["restaurant", "bakeries", "bakery", "teahouse", "food"]),
    ("temple",        ["temple", "church", "shrine", "cathedral", "religious", "monaster"]),
    ("magic",         ["magic", "arcane", "alchemist", "enchant", "wizard", "occult"]),
    ("knowledge",     ["academy", "school", "librar", "archive", "university", "college", "museum"]),
    ("shop",          ["shop", "store", "merchant", "market", "bazaar", "trading", "smith",
                       "workshop", "armor", "weaponsmith", "jewel", "book"]),
    ("guild",         ["guild", "lodge", "organization", "society", "headquarters"]),
    ("military",      ["defence", "defense", "fortification", "garrison", "barrack", "prison",
                       "jail", "watch", "guard", "militar", "gate locations", "wall", "castle"]),
    ("civic",         ["civic", "municipal", "government", "court", "bank", "mint", "taxation",
                       "embassy", "administra"]),
    ("entertainment", ["theatre", "theater", "entertain", "gambling", "casino", "arena",
                       "amphitheat", "brothel", "bathhouse", "opera", "music"]),
    ("healing",       ["hospital", "heal", "infirmar", "chirurgeon", "asylum", "almshouse"]),
    ("maritime",      ["harbor", "harbour", "dock locations", "lighthouse", "shipyard", "pier",
                       "wharf", "ferry", "naval", "ocean", "sea", "strait", "bay"]),
    ("ruins",         ["ruin", "dungeon", "tomb", "graveyard", "cemeter", "crypt", "necropol",
                       "catacomb"]),
    ("nation",        ["nations of", "nation", "city-state", "countr", "kingdom", "empire"]),
    ("settlement",    ["settlement", "cities", "towns", "villages", "metropol"]),
    ("residence",     ["residence", "estate", "manor", "mansion", "apartment", "villa", "palace"]),
    ("geography",     ["geograph", "mountain", "forest", "river", "lake", "island", "desert",
                       "swamp", "plain", "valley", "hill", "road", "region", "street", "plaza",
                       "square", "bridge", "park", "garden"]),
]
DEFAULT_TYPE = "landmark"

TYPE_LABELS = {
    "tavern": "Taverns & Inns", "restaurant": "Food & Drink", "temple": "Temples & Shrines",
    "magic": "Magic & Alchemy", "knowledge": "Libraries & Schools", "shop": "Shops & Markets",
    "guild": "Guilds & Lodges", "military": "Defences & Prisons", "civic": "Civic & Government",
    "entertainment": "Entertainment", "healing": "Healers", "maritime": "Harbour & Sea",
    "ruins": "Ruins & Tombs", "nation": "Nations", "settlement": "Settlements",
    "residence": "Estates & Homes", "geography": "Geography", "landmark": "Landmarks",
}


def api_get(params):
    params = dict(params, format="json", formatversion="2")
    url = f"{API}?{urllib.parse.urlencode(params)}"
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=45) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as exc:
            if attempt == 3:
                raise
            print(f"   retry {attempt + 1}: {exc}")
            time.sleep(2 * (attempt + 1))


def fetch_category_members(category):
    titles, cont = [], {}
    while True:
        data = api_get({"action": "query", "list": "categorymembers", "cmtitle": category,
                        "cmtype": "page", "cmlimit": "500", **cont})
        titles.extend(m["title"] for m in data.get("query", {}).get("categorymembers", []))
        if "continue" not in data:
            return titles
        cont = data["continue"]


def fetch_page_meta(titles):
    """Read each page's raw wikitext for two things the rendered extract hides.

    `latlong` is PathfinderWiki's own georeference, which lets the atlas place a
    pin exactly rather than scattering it across a district. `locale` names the
    containing district, which rescues locations whose district category is
    missing.
    """
    out = {}
    for i in range(0, len(titles), 40):
        batch = titles[i:i + 40]
        data = api_get({"action": "query", "titles": "|".join(batch),
                        "prop": "revisions", "rvprop": "content", "rvslots": "main"})
        for page in data.get("query", {}).get("pages", []):
            if "revisions" not in page:
                continue
            text = page["revisions"][0]["slots"]["main"]["content"]
            meta = {}
            m = re.search(r"\|\s*latlong\s*=\s*(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)", text)
            if m:
                meta["latlong"] = [float(m.group(1)), float(m.group(2))]
            m = re.search(r"\|\s*locale\s*=\s*(.+)", text)
            if m:
                meta["locale"] = m.group(1).strip()
            # First paragraph often reads "... in Absalom's Foreign Quarter".
            meta["body"] = text[:4000]
            out[page["title"]] = meta
        print(f"   wikitext {min(i + 40, len(titles))}/{len(titles)}")
        time.sleep(0.15)
    return out


def district_from_text(*chunks):
    """Find a district named in a locale field or article prose."""
    for chunk in chunks:
        if not chunk:
            continue
        for name in ABSALOM_DISTRICTS:
            # Match the bare name too ("the Coins" -> "The Coins").
            bare = name[4:] if name.startswith("The ") else name
            if re.search(r"\b" + re.escape(bare) + r"\b", chunk, re.IGNORECASE):
                return name
    return None


def fetch_details(titles):
    out = {}
    for i in range(0, len(titles), 20):
        batch = titles[i:i + 20]
        data = api_get({"action": "query", "titles": "|".join(batch),
                        "prop": "categories|extracts", "cllimit": "500",
                        "exintro": "1", "explaintext": "1", "exlimit": "20"})
        for page in data.get("query", {}).get("pages", []):
            if "missing" in page:
                continue
            out[page["title"]] = {
                "categories": [c["title"].replace("Category:", "") for c in page.get("categories", [])],
                "extract": (page.get("extract") or "").strip(),
            }
        print(f"   {min(i + 20, len(titles))}/{len(titles)}")
        time.sleep(0.2)
    return out


def derive_district(categories):
    for cat in categories:
        if not cat.endswith("/Locations"):
            continue
        prefix = cat[: -len("/Locations")].strip()
        name = DISTRICT_ALIASES.get(prefix, prefix)
        if name in ABSALOM_DISTRICTS:
            return name
        if f"The {name}" in ABSALOM_DISTRICTS:
            return f"The {name}"
    return None


def derive_type(categories):
    blob = " | ".join(categories).lower()
    for type_key, needles in TYPE_RULES:
        if any(n in blob for n in needles):
            return type_key
    return DEFAULT_TYPE


def summarize(extract, limit=320):
    text = re.sub(r"\s+", " ", extract).strip()
    if len(text) <= limit:
        return text
    cut = text[:limit]
    stop = max(cut.rfind(". "), cut.rfind("! "), cut.rfind("? "))
    return cut[: stop + 1] if stop > limit * 0.5 else cut.rstrip() + "..."


def slugify(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "location"


def scrape_map(map_id, config):
    print(f"\n=== {map_id} ===")
    out_path = ROOT / "etc" / config["out"]

    # Keep any coordinates already placed, and any hand-added custom POIs.
    placed, custom = {}, []
    if out_path.exists():
        old = json.loads(out_path.read_text(encoding="utf-8"))
        for loc in old.get("locations", []):
            if loc.get("coords"):
                placed[loc["id"]] = loc["coords"]
            if loc.get("custom"):
                custom.append(loc)
        if placed:
            print(f"   preserving {len(placed)} placed pins")

    titles = []
    for category in config["categories"]:
        found = fetch_category_members(category)
        print(f"   {len(found):>4} from {category}")
        titles.extend(found)
    titles = sorted(set(titles))
    print(f"   {len(titles)} unique pages")

    details = fetch_details(titles)
    meta_by_title = fetch_page_meta(titles)
    n_geo = sum(1 for m in meta_by_title.values() if m.get("latlong"))
    print(f"   {n_geo} pages carry map coordinates")

    locations, seen = [], set()
    for title in sorted(details):
        info = details[title]
        slug, base, n = slugify(title), slugify(title), 2
        while slug in seen:
            slug = f"{base}-{n}"
            n += 1
        seen.add(slug)

        poi_type = derive_type(info["categories"])
        meta = meta_by_title.get(title, {})
        if config["group_by"] == "district":
            # Category first, then the infobox locale, then the prose.
            group = (derive_district(info["categories"])
                     or district_from_text(meta.get("locale"), meta.get("body"))
                     or "Elsewhere in Absalom")
        else:
            group = TYPE_LABELS.get(poi_type, "Landmarks")

        locations.append({
            "id": slug, "name": title, "group": group, "type": poi_type,
            "summary": summarize(info["extract"]),
            "url": "https://pathfinderwiki.com/wiki/" + urllib.parse.quote(title.replace(" ", "_")),
            "latlong": meta.get("latlong"),
            "coords": placed.get(slug, {}),
        })

    locations.extend(custom)
    if custom:
        print(f"   kept {len(custom)} custom POIs")

    if config["group_by"] == "district":
        order = ABSALOM_DISTRICTS + ["Elsewhere in Absalom"]
    else:
        order = [TYPE_LABELS[k] for k, _ in TYPE_RULES] + ["Landmarks"]
    present = [g for g in order if any(l["group"] == g for l in locations)]
    present += sorted({l["group"] for l in locations} - set(present))

    payload = {
        "map": map_id,
        "source": "PathfinderWiki",
        "license": "Wiki text CC BY-SA 3.0. Pathfinder/Golarion are Paizo Inc. trademarks.",
        "scraped": date.today().isoformat(),
        "group_by": config["group_by"],
        "groups": present,
        "count": len(locations),
        "locations": locations,
    }
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    n_placed = sum(1 for l in locations if l.get("coords"))
    print(f"   OK {len(locations)} POIs -> etc/{config['out']}  ({n_placed} placed)")
    for g in present:
        print(f"      {g:<26} {sum(1 for l in locations if l['group'] == g):>4}")
    return len(locations)


def main():
    wanted = sys.argv[1:] or list(MAPS)
    unknown = [w for w in wanted if w not in MAPS]
    if unknown:
        print(f"ERROR: unknown map(s): {', '.join(unknown)}")
        print(f"       available: {', '.join(MAPS)}")
        return 1
    total = sum(scrape_map(m, MAPS[m]) for m in wanted)
    print(f"\nOK {total} POIs across {len(wanted)} map(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
