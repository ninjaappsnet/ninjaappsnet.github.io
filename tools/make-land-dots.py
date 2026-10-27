#!/usr/bin/env python3
"""Write assets/land.js: the world's land as a grid of dots, for the map in
FlectoBI's opening (assets/flecto.js).

The source is Natural Earth's 1:110m land (public domain), downloaded once by
hand; the page never fetches it:

    curl -sSfL -o land.json https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_land.geojson
    python3 tools/make-land-dots.py land.json

A dot sits at the centre of every cell of a 2.5-degree grid that falls on land,
from 75 north to 57.5 south (no Antarctica: a bubble map has no business there).
Each row is stored as a hex string, one bit per cell, west to east.
"""
import json
import sys
from pathlib import Path

STEP = 2.5
NORTH, SOUTH = 75.0, -57.5
COLS = int(360 / STEP)
ROWS = int((NORTH - SOUTH) / STEP)
OUT = Path(__file__).resolve().parent.parent / "assets" / "land.js"


def inside(x, y, ring):
    hit = False
    j = len(ring) - 1
    for i in range(len(ring)):
        xi, yi = ring[i]
        xj, yj = ring[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            hit = not hit
        j = i
    return hit


def polygons(geojson):
    for f in geojson["features"]:
        g = f["geometry"]
        if g["type"] == "Polygon":
            yield g["coordinates"]
        elif g["type"] == "MultiPolygon":
            yield from g["coordinates"]


def main(src):
    polys = [(p, (min(c[0] for c in p[0]), min(c[1] for c in p[0]), max(c[0] for c in p[0]), max(c[1] for c in p[0])))
             for p in polygons(json.loads(Path(src).read_text()))]
    rows = []
    for r in range(ROWS):
        lat = NORTH - (r + 0.5) * STEP
        bits = []
        for c in range(COLS):
            lon = -180 + (c + 0.5) * STEP
            on = any(box[0] <= lon <= box[2] and box[1] <= lat <= box[3]
                     and inside(lon, lat, p[0]) and not any(inside(lon, lat, h) for h in p[1:])
                     for p, box in polys)
            bits.append("1" if on else "0")
        rows.append(f"{int(''.join(bits), 2):0{COLS // 4}x}")
    body = ",\n    ".join(f"'{r}'" for r in rows)
    OUT.write_text(
        "// The world's land as dots on a 2.5-degree grid, 75N to 57.5S, one hex\n"
        "// string per row, one bit per cell, west to east. Made by\n"
        "// tools/make-land-dots.py from Natural Earth 1:110m land (public domain).\n"
        "(function (root) {\n"
        f"  root.NinjaLand = {{ step: {STEP}, north: {NORTH}, cols: {COLS}, rows: [\n    {body},\n  ] }};\n"
        "})(typeof globalThis !== 'undefined' ? globalThis : this);\n")
    print(f"{OUT}: {ROWS} rows, {sum(bin(int(r, 16)).count('1') for r in rows)} dots")


if __name__ == "__main__":
    main(sys.argv[1])
