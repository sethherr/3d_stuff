"""Variant B -- "Truss".

Low-fidelity design exploration. The mid-span is an OPEN space-frame, not a
solid bar: a top and bottom chord tied together by a zig-zag of diagonal struts
(a Warren/X truss) -- fully see-through. Solid hex collars at each end host the
saddles + tie slots; the GoPro tab hangs off the bottom chord at center.

Run: python aerobar-crossbar/variant_b_truss.py
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

MID_X = 40.0           # truss spans |x| <= this; collars solid beyond
CHORD_Z = 10.0         # top/bottom chord centerline height
STRUT = 3.2            # square strut thickness (in X and Z)
WIDTH_Y = 12.0         # truss thickness in Y
BAYS = 7               # number of triangular bays across the span


def _strut(x0, z0, x1, z1):
    """Square-section bar between two points in the X-Z plane (full WIDTH_Y)."""
    dx, dz = x1 - x0, z1 - z0
    length = math.hypot(dx, dz) + STRUT      # overlap a touch at the nodes
    ang = math.degrees(math.atan2(dz, dx))
    bar = Box(length, WIDTH_Y, STRUT)
    return Pos((x0 + x1) / 2, 0, (z0 + z1) / 2) * Rot(0, -ang, 0) * bar


def _collar(sign):
    cx = sign * (MID_X + BAR_X) / 2
    return Pos(cx, 0, 0) * extrude(
        Plane.YZ * RegularPolygon(HEX_R, 6), amount=(BAR_X - MID_X) / 2, both=True
    )


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
    # Chords run the whole span and lap into the collars so it's one piece.
    body = Box(2 * BAR_X, WIDTH_Y, STRUT)
    body = Pos(0, 0, CHORD_Z) * body + Pos(0, 0, -CHORD_Z) * Box(
        2 * BAR_X, WIDTH_Y, STRUT
    )

    # Zig-zag web between the chords.
    xs = [-MID_X + 2 * MID_X * i / BAYS for i in range(BAYS + 1)]
    for i in range(BAYS):
        x0, x1 = xs[i], xs[i + 1]
        # alternate the diagonal direction -> Warren truss of triangles
        if i % 2 == 0:
            body += _strut(x0, -CHORD_Z, x1, CHORD_Z)
        else:
            body += _strut(x0, CHORD_Z, x1, -CHORD_Z)
    # verticals at the ends close the frame
    for xv in (-MID_X, MID_X):
        body += _strut(xv, -CHORD_Z, xv, CHORD_Z)

    body += _collar(-1) + _collar(1)
    return _saddles_and_ties(body)


def gen_step():
    part = _body() + _gopro_mount()
    part.label = "aerobar_crossbar_truss"
    return part


if __name__ == "__main__":
    p = gen_step()
    print("volume mm^3:", round(p.volume, 1))
    here = Path(__file__).with_suffix("")
    export_step(p, str(here) + ".step")
    export_stl(p, str(here) + ".stl")
    export_gltf(p, str(here) + ".glb", binary=True)
    print("wrote .step / .stl / .glb")
