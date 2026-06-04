"""Variant C -- "Cross-hatch".

Low-fidelity design exploration. The mid-span is a diagonal lattice NET: two
families of +/-45 deg slots cut clean through (Y) leave a rhombic cross-hatch of
ribs, framed by solid top/bottom flanges and solid end collars. Functional bits
(outward saddles, one tie slot per side, GoPro tab) unchanged.

Run: python aerobar-crossbar/variant_c_crosshatch.py
"""

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

MID_X = 38.0           # perforate |x| <= this
Z_BAND = 9.5           # perforate |z| <= this (flanges stay solid)
SLOT_W = 3.0           # diagonal slot width -> rib = PITCH - SLOT_W
PITCH = 12.0          # spacing between parallel diagonals (bigger, cleaner cells)
THRU = HEX_R + 5


def _diag_slots(sign):
    """Family of parallel SLOT_W slots at sign*45 deg, as one compound."""
    slots = None
    # parallel 45-deg lines z = sign*x + c ; sweep c across the window.
    c = -(MID_X + Z_BAND)
    while c <= (MID_X + Z_BAND):
        slab = Box(4 * BAR_X, 4 * HEX_R, SLOT_W)        # long thin slab
        slab = Pos(0, 0, c) * Rot(0, -sign * 45, 0) * slab
        slots = slab if slots is None else slots + slab
        c += PITCH
    return slots


def _net_holes():
    # Confine both diagonal families to the mid window so flanges/collars survive.
    window = Box(2 * MID_X, 4 * HEX_R, 2 * Z_BAND)
    return (_diag_slots(1) + _diag_slots(-1)) & window


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
    body = body - _net_holes()
    return _saddles_and_ties(body)


def gen_step():
    part = _body() + _gopro_mount()
    part.label = "aerobar_crossbar_crosshatch"
    return part


if __name__ == "__main__":
    p = gen_step()
    print("volume mm^3:", round(p.volume, 1))
    here = Path(__file__).with_suffix("")
    export_step(p, str(here) + ".step")
    export_stl(p, str(here) + ".stl")
    export_gltf(p, str(here) + ".glb", binary=True)
    print("wrote .step / .stl / .glb")
