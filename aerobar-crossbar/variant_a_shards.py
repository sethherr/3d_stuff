"""Variant A -- "Shardstorm".

Low-fidelity design exploration. Same uniform hex bar, but instead of two tidy
diamond windows the whole mid-span is shot through with a SWARM of diamond
shards at varying sizes and angles -- a chaotic crystalline lattice. Functional
bits (outward saddles, one tie slot per side, GoPro tab) are unchanged.

Run: python aerobar-crossbar/variant_a_shards.py
"""

from pathlib import Path

from build123d import (
    Box,
    Cylinder,
    Plane,
    Polygon,
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

# A scattered field of diamond shards: (center_x, tilt_deg, half_x, half_z).
# Hand-picked to overlap and tilt every which way for a shattered-glass look,
# kept clear of the tie slots at x = +/-44.
SHARDS = [
    (-38, 18, 6, 7),
    (-30, -35, 9, 5),
    (-22, 50, 5, 8),
    (-14, -12, 8, 6),
    (-6, 40, 7, 7),
    (2, -28, 6, 8),
    (10, 22, 9, 5),
    (18, -48, 5, 7),
    (26, 14, 8, 6),
    (34, -20, 6, 7),
]


def _shard(cx, tilt, half_x, half_z):
    profile = Plane.XZ * Polygon(
        (-half_x, 0), (0, half_z), (half_x, 0), (0, -half_z)
    )
    win = extrude(profile, amount=HEX_R + 5, both=True)  # through Y
    return Pos(cx, 0, 0) * Rot(0, tilt, 0) * win


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
    for cx, tilt, hx, hz in SHARDS:
        body = body - _shard(cx, tilt, hx, hz)
    return _saddles_and_ties(body)


def gen_step():
    part = _body() + _gopro_mount()
    part.label = "aerobar_crossbar_shards"
    return part


if __name__ == "__main__":
    p = gen_step()
    print("volume mm^3:", round(p.volume, 1))
    here = Path(__file__).with_suffix("")
    export_step(p, str(here) + ".step")
    export_stl(p, str(here) + ".stl")
    export_gltf(p, str(here) + ".glb", binary=True)
    print("wrote .step / .stl / .glb")
