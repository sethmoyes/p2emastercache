#!/usr/bin/env python3
"""
Slice a large map image into Leaflet XYZ tiles and register it in etc/maps.json.

Only the visible tiles are ever downloaded, so a 12000px map costs a player the
same bandwidth as a small one. Uses ImageMagick, so no Python image deps needed.

    python3 bin/maps/tile_map.py etc/maps_src/absalom.png --id absalom \
        --name "Absalom" --subtitle "The City at the Center of the World"

Re-running for an existing id replaces its tiles and keeps its POI file, so you
can swap in a better scan later without losing placed pins (pins are stored as
0-1 fractions, not pixels).
"""

import argparse
import json
import math
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TILE_ROOT = ROOT / "bin" / "web" / "static" / "maps"
REGISTRY = ROOT / "etc" / "maps.json"

TILE_SIZE = 256
# Padding for partial edge tiles. Leaflet stretches every tile to a full square,
# so edge tiles must be padded or the map warps at the right/bottom margins.
PAD_COLOR = "#11161f"


def run(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("ERROR: " + " ".join(str(c) for c in cmd))
        print(result.stderr[:2000])
        sys.exit(1)
    return result.stdout


def magick_cmd():
    """ImageMagick 7 uses `magick`; 6 uses `convert`."""
    if shutil.which("magick"):
        return ["magick"]
    if shutil.which("convert"):
        return ["convert"]
    print("ERROR: ImageMagick not found. Install with: brew install imagemagick")
    sys.exit(1)


def identify(path):
    if shutil.which("magick"):
        out = run(["magick", "identify", "-format", "%w %h", f"{path}[0]"])
    else:
        out = run(["identify", "-format", "%w %h", f"{path}[0]"])
    w, h = out.strip().split()[:2]
    return int(w), int(h)


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def build_tiles(src, out_dir, width, height, max_zoom, quality):
    """Render one tile pyramid level per zoom, cropping each scaled image."""
    base = magick_cmd()
    total = 0

    for z in range(max_zoom + 1):
        scale = 2 ** (z - max_zoom)
        zw = max(1, int(math.ceil(width * scale)))
        zh = max(1, int(math.ceil(height * scale)))
        cols = int(math.ceil(zw / TILE_SIZE))
        rows = int(math.ceil(zh / TILE_SIZE))

        z_dir = out_dir / str(z)
        if z_dir.exists():
            shutil.rmtree(z_dir)
        z_dir.mkdir(parents=True)

        staging = out_dir / f".staging_{z}"
        if staging.exists():
            shutil.rmtree(staging)
        staging.mkdir(parents=True)

        run(base + [
            str(src),
            "-colorspace", "sRGB",
            "-resize", f"{zw}x{zh}!",
            "-background", PAD_COLOR,
            "-gravity", "NorthWest",
            "-extent", f"{cols * TILE_SIZE}x{rows * TILE_SIZE}",
            "-crop", f"{TILE_SIZE}x{TILE_SIZE}",
            "-set", "filename:tile", "%[fx:page.x/256]_%[fx:page.y/256]",
            "+repage", "+adjoin",
            "-quality", str(quality),
            str(staging / "t_%[filename:tile].jpg"),
        ])

        count = 0
        for tile in staging.glob("t_*.jpg"):
            x_str, y_str = tile.stem[2:].split("_")
            col_dir = z_dir / x_str
            col_dir.mkdir(exist_ok=True)
            tile.rename(col_dir / f"{y_str}.jpg")
            count += 1
        shutil.rmtree(staging)

        total += count
        print(f"    zoom {z}: {zw}x{zh}px  {cols}x{rows} grid  {count} tiles")

    return total


def build_thumbnail(src, out_dir, quality):
    run(magick_cmd() + [
        str(src), "-colorspace", "sRGB",
        "-resize", "480x480>", "-quality", str(quality),
        str(out_dir / "thumb.jpg"),
    ])


def load_registry():
    if REGISTRY.exists():
        return json.loads(REGISTRY.read_text(encoding="utf-8"))
    return {"maps": []}


def save_registry(reg):
    REGISTRY.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY.write_text(json.dumps(reg, indent=2, ensure_ascii=False), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description="Tile a map image for the atlas viewer.")
    ap.add_argument("image", help="source image (any format ImageMagick reads)")
    ap.add_argument("--id", help="map id / url slug (default: from --name)")
    ap.add_argument("--name", help="display name (default: from filename)")
    ap.add_argument("--subtitle", default="", help="one-line description")
    ap.add_argument("--pois", default="", help="POI json in etc/ (e.g. absalom_locations.json)")
    ap.add_argument("--attribution", default="", help="credit line shown on the map")
    ap.add_argument("--quality", type=int, default=82, help="jpeg quality (default 82)")
    ap.add_argument("--order", type=int, default=100, help="sort order in the map switcher")
    args = ap.parse_args()

    src = Path(args.image).expanduser().resolve()
    if not src.exists():
        print(f"ERROR: no such file: {src}")
        return 1

    name = args.name or src.stem.replace("_", " ").replace(".", " ").title()
    map_id = args.id or slugify(name)

    width, height = identify(src)
    # Max zoom is where the image is shown at 1:1 pixels.
    max_zoom = max(0, math.ceil(math.log2(max(width, height) / TILE_SIZE)))

    print(f"Tiling '{name}' (id: {map_id})")
    print(f"  source: {src}")
    print(f"  size:   {width} x {height}px")
    print(f"  zooms:  0 to {max_zoom}")

    out_dir = TILE_ROOT / map_id
    out_dir.mkdir(parents=True, exist_ok=True)

    total = build_tiles(src, out_dir, width, height, max_zoom, args.quality)
    build_thumbnail(src, out_dir, args.quality)

    tile_bytes = sum(f.stat().st_size for f in out_dir.rglob("*.jpg"))
    print(f"  OK {total} tiles, {tile_bytes / 1048576:.1f} MB total")

    reg = load_registry()
    entry = {
        "id": map_id,
        "name": name,
        "subtitle": args.subtitle,
        "width": width,
        "height": height,
        "tile_size": TILE_SIZE,
        "max_zoom": max_zoom,
        "tiles": f"/static/maps/{map_id}/{{z}}/{{x}}/{{y}}.jpg",
        "thumb": f"/static/maps/{map_id}/thumb.jpg",
        "pois": args.pois,
        "attribution": args.attribution,
        "order": args.order,
    }

    existing = next((m for m in reg["maps"] if m["id"] == map_id), None)
    if existing:
        # Keep fields the user may have hand-edited unless this run set them.
        for key in ("pois", "attribution", "subtitle"):
            if not entry[key] and existing.get(key):
                entry[key] = existing[key]
        reg["maps"][reg["maps"].index(existing)] = entry
        print(f"  OK updated '{map_id}' in etc/maps.json")
    else:
        reg["maps"].append(entry)
        print(f"  OK added '{map_id}' to etc/maps.json")

    reg["maps"].sort(key=lambda m: (m.get("order", 100), m["name"]))
    save_registry(reg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
