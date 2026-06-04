"""Variant A -- "Honeycomb".

Low-fidelity design exploration. The mid-span is a honeycomb MESH instead of
solid: a staggered grid of hexagonal cells cut clean through (Y), leaving thin
walls plus solid top/bottom flanges and solid end collars. Functional bits
(outward saddles, one tie slot per side, GoPro tab) unchanged.

Run: python aerobar-crossbar/variant_a_honeycomb.py
"""

import math
from pathlib import Path

from build123d import (
    Box,
    Cylinder,
    Plane,
    Pos,
    RegularPolygon,
    Rot,
    export_gltf,
    export_step,
    export_stl,
    extrude,
)

from aerobar_crossbar import (
    BAR_X,
    GROOVE_R,
    HEX_R,
    TIE_SLOT_OFFX,
    TIE_SLOT_X,
    TIE_SLOT_Y,
    _gopro_mount,
)

CELL_R = 5.0            # hex cell circumradius (the hole)
PITCH = 6.2            # tiling radius -> wall ~ PITCH-CELL_R between cells
MID_X = 38.0           # perforate |x| <= this (collars stay solid beyond)
Z_BAND = 9.5           # perforate |z| <= this (top/bottom flanges stay solid)
THRU = HEX_R + 5       # cut all the way through Y


def _cell(cx, cz):
    # Pointy-top hex prism through Y.
    poly = Plane.XZ * RegularPolygon(CELL_R, 6, rotation=90)
    return Pos(cx, 0, cz) * extrude(poly, amount=THRU, both=True)


def _honeycomb():
    hpitch = math.sqrt(3) * PITCH       # column spacing
    vpitch = 1.5 * PITCH                # row spacing
    holes = None
    row = 0
    z = 0.0
    while z <= Z_BAND:
        for zc in {z, -z}:
            offset = (hpitch / 2) if (row % 2) else 0.0
            x = -MID_X + offset
            while x <= MID_X:
                cell = _cell(x, zc)
                holes = cell if holes is None else holes + cell
                x += hpitch
        row += 1
        z = row * vpitch
    return holes


def _saddles_and_ties(body):
    for sign in (-1, 1):
        cx = sign * BAR_X
        groove = Pos(cx, 0, 0) * (Rot(90, 0, 0) * Cylinder(GROOVE_R, 2 * HEX_R + 6))
        body = body - groove
        slot = Pos(cx - sign * TIE_SLOT_OFFX, 0, 0) * Box(
            TIE_SLOT_X, TIE_SLOT_Y, 2 * HEX_R + 6
        )
        body = body - slot
    return body


def _body():
    body = extrude(Plane.YZ * RegularPolygon(HEX_R, 6), amount=BAR_X, both=True)
    body = body - _honeycomb()
    return _saddles_and_ties(body)


def gen_step():
    part = _body() + _gopro_mount()
    part.label = "aerobar_crossbar_honeycomb"
    return part


if __name__ == "__main__":
    p = gen_step()
    print("volume mm^3:", round(p.volume, 1))
    here = Path(__file__).with_suffix("")
    export_step(p, str(here) + ".step")
    export_stl(p, str(here) + ".stl")
    export_gltf(p, str(here) + ".glb", binary=True)
    print("wrote .step / .stl / .glb")
