"""Variant B -- "Barley Twist".

Low-fidelity design exploration. The hex section is the same, but the whole bar
is LOFTED through rotating cross-sections so it corkscrews ~180 deg end to end
-- a twisted-column look. The saddle cups and tie slots are cut afterward so the
ends still mate the round bars; GoPro tab unchanged.

Run: python aerobar-crossbar/variant_b_twist.py
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
    loft,
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

TWIST_DEG = 180.0
SECTIONS = 17


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
    sections = []
    for i in range(SECTIONS):
        t = i / (SECTIONS - 1)
        x = -BAR_X + 2 * BAR_X * t
        ang = TWIST_DEG * t
        sections.append(Pos(x, 0, 0) * Rot(ang, 0, 0) * (Plane.YZ * RegularPolygon(HEX_R, 6)))
    body = loft(sections)
    return _saddles_and_ties(body)


def gen_step():
    part = _body() + _gopro_mount()
    part.label = "aerobar_crossbar_twist"
    return part


if __name__ == "__main__":
    p = gen_step()
    print("volume mm^3:", round(p.volume, 1))
    here = Path(__file__).with_suffix("")
    export_step(p, str(here) + ".step")
    export_stl(p, str(here) + ".stl")
    export_gltf(p, str(here) + ".glb", binary=True)
    print("wrote .step / .stl / .glb")
