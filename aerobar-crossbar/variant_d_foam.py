"""Variant D -- "Foam" (3D strut lattice).

Low-fidelity design exploration matching a reference photo of an open-cell strut
lattice: the mid-span is filled with a 3D node-and-strut network based on the
Kelvin cell (truncated octahedron) tiled through the volume, with beaded nodes --
an open metallic-foam look. Solid hex collars at each end still host the saddles
+ tie slots; the GoPro tab hangs off a small center hub.

The lattice is assembled as a Compound of cylinders + spheres (no booleans) so it
stays fast; it's a visual exploration, not a watertight/printable solid yet.

Run: python aerobar-crossbar/variant_d_foam.py
"""

import itertools
from pathlib import Path

from build123d import (
    Box,
    Compound,
    Cylinder,
    Plane,
    Pos,
    RegularPolygon,
    Rot,
    Solid,
    Sphere,
    Vector,
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

S = 2.3                # Kelvin cell scale (cell period = 4*S)
STRUT_R = 0.8          # strut radius
NODE_R = 1.15          # beaded node radius
MID_X = 40.0           # lattice fills |x| <= ~this; collars solid beyond
Y_R = 12.0             # lattice half-extent in Y (within the hex flats)
Z_R = 12.0             # lattice half-extent in Z


def _kelvin_verts():
    # Truncated-octahedron vertices: all signed permutations of (0, 1, 2).
    verts = set()
    for perm in itertools.permutations((0, 1, 2)):
        for sx, sy, sz in itertools.product((1, -1), repeat=3):
            v = (perm[0] * sx, perm[1] * sy, perm[2] * sz)
            verts.add(v)
    return sorted(verts)


def _kelvin_edges():
    verts = _kelvin_verts()
    edges = []
    for a, b in itertools.combinations(verts, 2):
        d2 = sum((a[i] - b[i]) ** 2 for i in range(3))
        if d2 == 2:                       # nearest neighbours -> the 36 edges
            edges.append((a, b))
    return verts, edges


def _strut(p0, p1):
    d = Vector(*p1) - Vector(*p0)
    length = d.length
    return Solid.make_cylinder(
        STRUT_R, length, Plane(origin=Vector(*p0), z_dir=d)
    )


def _lattice():
    verts, edges = _kelvin_edges()
    # BCC tiling: simple-cubic origins of period 4S, plus body-centred copies.
    reach = MID_X + 2 * S
    n = int(reach / (4 * S)) + 1
    rng = range(-n, n + 1)
    origins = []
    for i, j, k in itertools.product(rng, repeat=3):
        base = (i * 4 * S, j * 4 * S, k * 4 * S)
        origins.append(base)
        origins.append((base[0] + 2 * S, base[1] + 2 * S, base[2] + 2 * S))

    def inside(p):
        return abs(p[0]) <= MID_X + 1.5 and abs(p[1]) <= Y_R and abs(p[2]) <= Z_R

    seen_edges, seen_nodes = set(), set()
    parts = []
    for o in origins:
        scaled = {v: (o[0] + v[0] * S, o[1] + v[1] * S, o[2] + v[2] * S) for v in verts}
        for a, b in edges:
            pa, pb = scaled[a], scaled[b]
            mid = tuple((pa[i] + pb[i]) / 2 for i in range(3))
            if not inside(mid):
                continue
            key = tuple(sorted((tuple(round(c, 2) for c in pa),
                                tuple(round(c, 2) for c in pb))))
            if key in seen_edges:
                continue
            seen_edges.add(key)
            parts.append(_strut(pa, pb))
            for p in (pa, pb):
                nk = tuple(round(c, 2) for c in p)
                if nk not in seen_nodes and inside(p):
                    seen_nodes.add(nk)
                    parts.append(Pos(*p) * Sphere(NODE_R))
    return parts


def _collar(sign):
    cx = sign * (MID_X - 1 + BAR_X) / 2
    block = Pos(cx, 0, 0) * extrude(
        Plane.YZ * RegularPolygon(HEX_R, 6), amount=(BAR_X - MID_X + 1) / 2, both=True
    )
    # saddle cup + tie slot
    bar_x = sign * BAR_X
    block = block - Pos(bar_x, 0, 0) * (Rot(90, 0, 0) * Cylinder(GROOVE_R, 2 * HEX_R + 6))
    block = block - Pos(bar_x - sign * TIE_SLOT_OFFX, 0, 0) * Box(
        TIE_SLOT_X, TIE_SLOT_Y, 2 * HEX_R + 6
    )
    return block


def _center_hub():
    # Small solid block at center-bottom so the GoPro tab has something to root in.
    return Pos(0, 0, -10.5) * Box(14, 15, 6)


def gen_step():
    shapes = _lattice() + [_collar(-1), _collar(1), _center_hub(), _gopro_mount()]
    # Flatten everything to individual solids so the Compound is well-formed.
    solids = []
    for sh in shapes:
        solids.extend(sh.solids())
    part = Compound(solids)
    part.label = "aerobar_crossbar_foam"
    return part


if __name__ == "__main__":
    p = gen_step()
    print("struts+nodes+solids:", len(p.solids()))
    here = Path(__file__).with_suffix("")
    export_step(p, str(here) + ".step")
    export_stl(p, str(here) + ".stl")
    export_gltf(p, str(here) + ".glb", binary=True)
    print("wrote .step / .stl / .glb")
