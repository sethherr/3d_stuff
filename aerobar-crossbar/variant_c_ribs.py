"""Variant C -- "Vertebrae".

Low-fidelity design exploration. Instead of a solid bar, a skeletal spine: solid
hex blocks at each end (to host the saddles + tie slots) and a solid hub in the
middle (to host the GoPro tab), strung together by a thin central rod with a row
of full-height hex "rib" plates floating along it. Open, bony, see-through.

Run: python aerobar-crossbar/variant_c_ribs.py
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

END_LEN = 18.0          # solid hex block at each end
HUB_LEN = 16.0          # solid hex hub in the middle (carries the GoPro tab)
SPINE_R = 4.0           # thin connecting rod radius
RIB_T = 3.0             # rib plate thickness
RIBS_PER_GAP = 3        # ribs strung in each gap between hub and an end block


def _hex_block(cx, length):
    return Pos(cx, 0, 0) * extrude(
        Plane.YZ * RegularPolygon(HEX_R, 6), amount=length / 2, both=True
    )


def _rib(cx):
    return Pos(cx, 0, 0) * extrude(
        Plane.YZ * RegularPolygon(HEX_R, 6), amount=RIB_T / 2, both=True
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
    # Central rod the whole span, plus solid masses at the two ends and middle.
    body = Rot(0, 90, 0) * Cylinder(SPINE_R, 2 * BAR_X)
    body += _hex_block(-BAR_X + END_LEN / 2, END_LEN)
    body += _hex_block(BAR_X - END_LEN / 2, END_LEN)
    body += _hex_block(0, HUB_LEN)

    # Floating rib plates in each gap between the hub edge and an end block.
    for sign in (-1, 1):
        inner = HUB_LEN / 2
        outer = BAR_X - END_LEN
        for k in range(1, RIBS_PER_GAP + 1):
            t = k / (RIBS_PER_GAP + 1)
            body += _rib(sign * (inner + (outer - inner) * t))

    return _saddles_and_ties(body)


def gen_step():
    part = _body() + _gopro_mount()
    part.label = "aerobar_crossbar_ribs"
    return part


if __name__ == "__main__":
    p = gen_step()
    print("volume mm^3:", round(p.volume, 1))
    here = Path(__file__).with_suffix("")
    export_step(p, str(here) + ".step")
    export_stl(p, str(here) + ".stl")
    export_gltf(p, str(here) + ".glb", binary=True)
    print("wrote .step / .stl / .glb")
