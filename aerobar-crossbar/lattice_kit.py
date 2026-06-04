"""Shared builder for strut-lattice crossbar explorations.

Each lattice variant just defines a unit cell -- a list of base node positions
and the neighbour offsets that become struts -- and calls `build_part`. This kit
handles the rest, identically to `aerobar_crossbar_foam.py`: tile the cell across
the volume, draw struts (cylinders) + beaded nodes (spheres), run the lattice the
full length and wrap it around each saddle (only a thin C-shaped cradle cup stays
solid), keep the bar seats + tie channels clear, and hang the GoPro tab off a
small center hub.

Parts are assembled as a Compound of cylinders + spheres (no booleans) so they
stay fast; these are visual studies, not watertight/printable solids yet.
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

EDGE_X = BAR_X - 1.0   # lattice fills out to here -- just shy of the bar centers
Y_R = 12.0             # lattice half-extent in Y (within the hex flats)
Z_R = 12.0             # lattice half-extent in Z
SHELL_WALL = 2.4       # cradle cup wall thickness (the only solid at the ends)
SEAT_CLEAR = 0.4       # keep struts this far clear of each bar's seat
TIE_W = TIE_SLOT_Y     # zip-tie channel width (matches the tie slot)
TIE_DEPTH = 1.4        # recess so the tie sits flush with the rest of the saddle


def _strut(p0, p1, r):
    d = Vector(*p1) - Vector(*p0)
    return Solid.make_cylinder(r, d.length, Plane(origin=Vector(*p0), z_dir=d))


def _in_bounds(p):
    return abs(p[0]) <= EDGE_X and abs(p[1]) <= Y_R and abs(p[2]) <= Z_R


def _excluded(p):
    """Regions the lattice must stay out of: each bar's seat and each tie slot."""
    for s in (-1, 1):
        bx = s * BAR_X
        if (p[0] - bx) ** 2 + p[2] ** 2 <= (GROOVE_R + SEAT_CLEAR) ** 2:
            return True
        sx = bx - s * TIE_SLOT_OFFX
        if abs(p[0] - sx) <= TIE_SLOT_X / 2 + 0.8 and abs(p[1]) <= TIE_SLOT_Y / 2 + 0.8:
            return True
    return False


def _tie_channel(bx):
    """A shallow groove across the cradle (centered in Y) so the zip tie wrapping
    the bar sits recessed -- flush with the rest of the saddle, not proud."""
    big = 2 * HEX_R + 6
    reach = GROOVE_R + SHELL_WALL + 2
    slab = Pos(bx, 0, 0) * Box(2 * reach, TIE_W, 2 * reach)
    keep = Pos(bx, 0, 0) * (Rot(90, 0, 0) * Cylinder(GROOVE_R + SHELL_WALL - TIE_DEPTH, big))
    return slab - keep


def _cradle(sign):
    """Thin C-shaped cup shell hugging the inner half of the bar, with a flush
    zip-tie channel grooved across its top and bottom."""
    bx = sign * BAR_X
    big = 2 * HEX_R + 6
    ring = Pos(bx, 0, 0) * (
        (Rot(90, 0, 0) * Cylinder(GROOVE_R + SHELL_WALL, big))
        - (Rot(90, 0, 0) * Cylinder(GROOVE_R, big))
    )
    env = Pos(bx - 8 * sign, 0, 0) * extrude(
        Plane.YZ * RegularPolygon(HEX_R, 6), amount=8, both=True
    )
    return (ring & env) - _tie_channel(bx)


def _center_hub():
    return Pos(0, 0, -10.5) * Box(14, 15, 6)


def build_part(base_nodes, neighbor_offsets, cell, strut_r=0.8, node_r=1.15, label="lattice"):
    """Tile `base_nodes` (positions within one `cell`-sized cube) on a cubic grid,
    connect each node to existing neighbours at `neighbor_offsets`, and assemble
    the struts + nodes + end cradles + GoPro hub into one Compound."""
    nx = int(EDGE_X / cell) + 2
    ny = int(Y_R / cell) + 2
    nz = int(Z_R / cell) + 2

    nodes = {}                       # rounded key -> world position
    for i, j, k in itertools.product(
        range(-nx, nx + 1), range(-ny, ny + 1), range(-nz, nz + 1)
    ):
        origin = (i * cell, j * cell, k * cell)
        for bn in base_nodes:
            p = (origin[0] + bn[0], origin[1] + bn[1], origin[2] + bn[2])
            nodes[(round(p[0], 2), round(p[1], 2), round(p[2], 2))] = p

    parts, seen_edges, used_nodes = [], set(), set()
    for key, p in nodes.items():
        for off in neighbor_offsets:
            qk = (round(p[0] + off[0], 2), round(p[1] + off[1], 2), round(p[2] + off[2], 2))
            if qk not in nodes:
                continue
            ek = tuple(sorted((key, qk)))
            if ek in seen_edges:
                continue
            seen_edges.add(ek)
            pa, pb = p, nodes[qk]
            mid = tuple((pa[i] + pb[i]) / 2 for i in range(3))
            if not _in_bounds(mid) or _excluded(pa) or _excluded(pb):
                continue
            parts.append(_strut(pa, pb, strut_r))
            for nd, ndk in ((pa, key), (pb, qk)):
                if ndk not in used_nodes and _in_bounds(nd) and not _excluded(nd):
                    used_nodes.add(ndk)
                    parts.append(Pos(*nd) * Sphere(node_r))

    parts += [_cradle(-1), _cradle(1), _center_hub(), _gopro_mount()]
    solids = []
    for sh in parts:
        solids.extend(sh.solids())
    part = Compound(solids)
    part.label = label
    return part


def write_exports(part, pyfile):
    here = Path(pyfile).with_suffix("")
    print("solids:", len(part.solids()))
    export_step(part, str(here) + ".step")
    export_stl(part, str(here) + ".stl")
    export_gltf(part, str(here) + ".glb", binary=True)
    print("wrote .step / .stl / .glb")
