#!/usr/bin/env python3
"""
Give every POI a sensible starting position from the region it belongs to.

Placing hundreds of pins by hand is the slow part of building an atlas. The
Absalom map prints its district names, so each district's POIs can be scattered
inside that district's footprint straight away, leaving only nudges to do.

Three sources feed it, best first. GEOREF projects PathfinderWiki's own latlong
coordinates onto the map image, which is exact. POINTS holds positions read off
labels printed on the map. REGIONS holds a district ellipse, whose remaining
POIs are spread by phyllotaxis (the sunflower-seed spiral), which fills the
shape evenly instead of clumping in the middle the way random points do.

    python3 bin/maps/autoplace.py absalom            # place them
    python3 bin/maps/autoplace.py absalom --force    # also move already-placed pins
    python3 bin/maps/autoplace.py absalom --clear    # undo, back to unplaced

Coordinates are 0-1 fractions of the image, matching the atlas POI format.
"""

import argparse
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "etc" / "maps.json"

GOLDEN_ANGLE = math.pi * (3 - math.sqrt(5))

# Ellipses eyeballed from the printed district labels and boundaries on the
# Absalom poster map, as fractions of the image (cx, cy, rx, ry).
REGIONS = {
    "absalom": {
        "Wise Quarter":      (0.452, 0.185, 0.082, 0.025),
        "Ivy District":      (0.317, 0.214, 0.058, 0.016),
        "Petal District":    (0.703, 0.209, 0.066, 0.028),
        "Ascendant Court":   (0.540, 0.264, 0.088, 0.037),
        "Westgate":          (0.228, 0.316, 0.050, 0.030),
        "Foreign Quarter":   (0.340, 0.368, 0.072, 0.034),
        "The Coins":         (0.537, 0.362, 0.082, 0.029),
        "Eastgate":          (0.795, 0.358, 0.072, 0.035),
        "The Docks":         (0.500, 0.452, 0.160, 0.023),
        "The Puddles":       (0.224, 0.484, 0.048, 0.023),
        "Precipice Quarter": (0.838, 0.524, 0.056, 0.026),
        # Sits beneath the city; anchored under the Coins.
        "Undercity":         (0.537, 0.398, 0.068, 0.026),
    },
}

# Exact positions, read off labels printed on the map itself. These win over
# the region scatter above, so a named place lands where the cartographer put it.
# Linear fit from PathfinderWiki's latlong space onto each map image, derived
# from district centroids and anchored on the Starstone Cathedral, whose pit is
# unmistakable on the Absalom map. fx = A*lon + B, fy = C*lat + D.
# Affine, so a map drawn at an angle still fits: fx = a*lon + b*lat + c.
GEOREF = {
    "absalom": {
        # Fitted on district centroids, anchored on the Starstone Cathedral pit.
        # Median error 0.4% of image width across 241 points.
        "x": (8.017801, 0.0, 2.429641),
        "y": (0.0, -5.519927, 170.804271),
        # Ignore Absalom-tagged pages describing places elsewhere in the world.
        "lat_range": (30.70, 31.00), "lon_range": (-0.35, -0.10),
    },
    "kortos": {
        # The Kortos map is stylised rather than projected, so this only gets a
        # pin to roughly the right part of the island (median error ~5%).
        # POINTS entries below are read straight off map labels and win over it.
        "x": (0.267785, 0.019594, -0.003558),
        "y": (0.006887, -0.496088, 16.039176),
        "lat_range": (30.30, 32.10), "lon_range": (-2.20, 1.00),
    },
}

POINTS = {
    "kortos": {
        # Settlements and landmarks, north to south.
        "high-harbor":    (0.796, 0.278),
        "pier-s-end":     (0.389, 0.327),
        "willowside":     (0.319, 0.342),
        "rovagug-s-hall": (0.585, 0.346),
        "hazrak":         (0.678, 0.414),
        "flesk":          (0.776, 0.426),
        "elyon":          (0.082, 0.525),
        "kerrick":        (0.140, 0.570),
        "tyrant-s-grasp": (0.664, 0.584),
        "bosco":          (0.707, 0.609),
        "meravon":        (0.304, 0.688),
        "otari":          (0.339, 0.744),
        "absalom":        (0.499, 0.793),
        "galizhur":       (0.284, 0.851),
        "diobel":         (0.165, 0.872),
    },
}


def load_map_entry(map_id):
    reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
    entry = next((m for m in reg.get("maps", []) if m["id"] == map_id), None)
    if not entry:
        sys.exit(f"ERROR: '{map_id}' is not in etc/maps.json")
    if not entry.get("pois"):
        sys.exit(f"ERROR: '{map_id}' has no POI file configured")
    return entry


def spread(cx, cy, rx, ry, n):
    """n points filling an ellipse at even density."""
    if n == 1:
        return [(cx, cy)]
    out = []
    for i in range(n):
        r = math.sqrt((i + 0.5) / n)
        theta = i * GOLDEN_ANGLE
        out.append((cx + rx * r * math.cos(theta),
                    cy + ry * r * math.sin(theta)))
    return out


def main():
    ap = argparse.ArgumentParser(description="Seed POI positions from their region.")
    ap.add_argument("map_id")
    ap.add_argument("--force", action="store_true", help="reposition pins that are already placed")
    ap.add_argument("--clear", action="store_true", help="remove this map's coordinates instead")
    args = ap.parse_args()

    entry = load_map_entry(args.map_id)
    path = ROOT / "etc" / Path(entry["pois"]).name
    data = json.loads(path.read_text(encoding="utf-8"))
    locations = data.get("locations", [])

    if args.clear:
        n = sum(1 for l in locations if (l.get("coords") or {}).pop(args.map_id, None) is not None)
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"OK cleared {n} placement(s) for '{args.map_id}'")
        return 0

    regions = REGIONS.get(args.map_id, {})
    points = POINTS.get(args.map_id, {})
    if not regions and not points:
        sys.exit(f"ERROR: nothing defined for '{args.map_id}'. Add REGIONS or POINTS.")

    by_id = {l["id"]: l for l in locations}
    placed = skipped = exact = geo = offmap = 0
    precise = set()   # ids fixed by a better source than the region scatter

    # Map labels first: on a stylised map they beat the georeference fit.
    for poi_id, (x, y) in points.items():
        loc = by_id.get(poi_id)
        if loc is None:
            print(f"   WARNING: no POI '{poi_id}' to place")
            continue
        if not args.force and (loc.get("coords") or {}).get(args.map_id):
            skipped += 1
            continue
        loc.setdefault("coords", {})[args.map_id] = {"x": round(x, 6), "y": round(y, 6)}
        precise.add(loc["id"])
        exact += 1
    if exact:
        print(f"   {'exact map labels':<20} {exact:>4} placed")

    # Then the wiki's own coordinates, for anything a label did not cover.
    ref = GEOREF.get(args.map_id)
    if ref:
        lo_lat, hi_lat = ref["lat_range"]
        lo_lon, hi_lon = ref["lon_range"]
        for loc in locations:
            ll = loc.get("latlong")
            if not ll or loc["id"] in precise:
                continue
            lat, lon = ll
            if not (lo_lat <= lat <= hi_lat and lo_lon <= lon <= hi_lon):
                continue
            if not args.force and (loc.get("coords") or {}).get(args.map_id):
                precise.add(loc["id"])   # already positioned; hands off
                skipped += 1
                continue
            ax, bx, cx = ref["x"]
            ay, by, cy = ref["y"]
            fx = ax * lon + bx * lat + cx
            fy = ay * lon + by * lat + cy
            # Some locations sit beyond the edge of the map (the Spire of Nex is
            # north of Absalom's walls). Leave those unplaced rather than clamp
            # them onto the border, where they would read as a real position.
            if not (0.0 <= fx <= 1.0 and 0.0 <= fy <= 1.0):
                offmap += 1
                continue
            loc.setdefault("coords", {})[args.map_id] = {
                "x": round(fx, 6), "y": round(fy, 6),
            }
            precise.add(loc["id"])
            geo += 1
        if geo:
            print(f"   {'wiki coordinates':<20} {geo:>4} placed")
        if offmap:
            print(f"   {'off the map edge':<20} {offmap:>4} skipped")

    by_group = {}
    for loc in locations:
        by_group.setdefault(loc.get("group"), []).append(loc)

    placed = 0
    for group, ellipse in regions.items():
        members = by_group.get(group, [])
        if not members:
            continue
        # Keep a stable order so re-running lands pins in the same spots.
        members.sort(key=lambda l: l["id"])
        candidates = [m for m in members if m["id"] not in precise]
        targets = [m for m in candidates
                   if args.force or not (m.get("coords") or {}).get(args.map_id)]
        # Only count pins that were already positioned before this run.
        skipped += len(candidates) - len(targets)
        if not targets:
            continue

        for loc, (x, y) in zip(targets, spread(*ellipse, len(targets))):
            # Flagged approximate: we know the district, not the spot. The atlas
            # renders these faded so nobody reads them as surveyed positions.
            loc.setdefault("coords", {})[args.map_id] = {
                "x": round(min(1.0, max(0.0, x)), 6),
                "y": round(min(1.0, max(0.0, y)), 6),
                "approx": True,
            }
            placed += 1
        print(f"   {group:<20} {len(targets):>4} placed")

    unmatched = sorted(g for g in by_group if g not in regions and g)
    if not regions:
        unmatched = []
    for g in unmatched:
        print(f"   {g:<20} {len(by_group[g]):>4} left unplaced (no region defined)")

    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    total = sum(1 for l in locations if (l.get("coords") or {}).get(args.map_id))
    print(f"\nOK placed {placed + exact + geo}" + (f", kept {skipped} existing" if skipped else ""))
    print(f"   {total}/{len(locations)} now on '{args.map_id}'")
    return 0


if __name__ == "__main__":
    sys.exit(main())
