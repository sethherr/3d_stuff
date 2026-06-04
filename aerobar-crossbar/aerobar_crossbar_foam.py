"""Aerobar crossbar -- "Foam" (3D strut lattice).

An open-cell strut lattice (after a reference photo): a node-and-strut network
based on the Kelvin cell (truncated octahedron) tiled through the whole volume
with beaded nodes -- a metallic-foam look. The lattice runs the full length and
wraps around each saddle; the only solid left at the ends is a thin C-shaped
cradle cup on the bar's seat face, and a small center hub carries the GoPro tab.

The lattice is assembled as a Compound of cylinders + spheres (no booleans) so it
stays fast; it's a visual exploration, not a watertight/printable solid yet.

Run: python aerobar-crossbar/aerobar_crossbar_foam.py
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
    _gopro_mount,
)

# Tie geometry the lattice keeps clear and grooves into the cradle. The base part
# redesigned its own tie routing (through-saddle X-holes); the foam variant keeps
# its own cradle-channel approach, so these live here rather than imported.
TIE_SLOT_OFFX = 16.0   # inboard channel offset from each bar center
TIE_SLOT_X = 3.0       # channel width (X)
TIE_SLOT_Y = 6.0       # channel / tie width (Y)

S = 2.3                # Kelvin cell scale (cell period = 4*S)
STRUT_R = 0.8          # strut radius
NODE_R = 1.15          # beaded node radius
EDGE_X = BAR_X - 1.0   # lattice fills out to here -- just shy of the bar centers
Y_R = 12.0             # lattice half-extent in Y (within the hex flats)
Z_R = 12.0             # lattice half-extent in Z
SHELL_WALL = 2.4       # cradle cup wall thickness (the only solid at the ends)
SEAT_CLEAR = 0.4       # keep struts this far clear of each bar's seat
TIE_W = TIE_SLOT_Y     # zip-tie channel width (matches the tie slot)
RAMP_ANG = 22.0        # tie channel taper: open at the outboard edge, thickening inboard


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


def _in_bounds(p):
    return abs(p[0]) <= EDGE_X and abs(p[1]) <= Y_R and abs(p[2]) <= Z_R


def _excluded(p):
    """Regions the lattice must stay out of: each bar's seat and each tie slot."""
    for s in (-1, 1):
        bx = s * BAR_X
        # keep the cup clear so the bar can seat against the cradle shell
        if (p[0] - bx) ** 2 + p[2] ** 2 <= (GROOVE_R + SEAT_CLEAR) ** 2:
            return True
        # keep a clean vertical channel for the zip tie behind the saddle
        sx = bx - s * TIE_SLOT_OFFX
        if abs(p[0] - sx) <= TIE_SLOT_X / 2 + 0.8 and abs(p[1]) <= TIE_SLOT_Y / 2 + 0.8:
            return True
    return False


def _lattice():
    verts, edges = _kelvin_edges()
    # BCC tiling: simple-cubic origins of period 4S, plus body-centred copies.
    n = int(BAR_X / (4 * S)) + 1
    rng = range(-n, n + 1)
    origins = []
    for i, j, k in itertools.product(rng, repeat=3):
        base = (i * 4 * S, j * 4 * S, k * 4 * S)
        origins.append(base)
        origins.append((base[0] + 2 * S, base[1] + 2 * S, base[2] + 2 * S))

    seen_edges, seen_nodes = set(), set()
    parts = []
    for o in origins:
        scaled = {v: (o[0] + v[0] * S, o[1] + v[1] * S, o[2] + v[2] * S) for v in verts}
        for a, b in edges:
            pa, pb = scaled[a], scaled[b]
            mid = tuple((pa[i] + pb[i]) / 2 for i in range(3))
            # fill the whole length, but skip struts that intrude on a bar seat
            # or tie slot -- so the foam wraps right up to (and around) each saddle
            if not _in_bounds(mid) or _excluded(pa) or _excluded(pb):
                continue
            key = tuple(sorted((tuple(round(c, 2) for c in pa),
                                tuple(round(c, 2) for c in pb))))
            if key in seen_edges:
                continue
            seen_edges.add(key)
            parts.append(_strut(pa, pb))
            for p in (pa, pb):
                nk = tuple(round(c, 2) for c in p)
                if nk not in seen_nodes and _in_bounds(p) and not _excluded(p):
                    seen_nodes.add(nk)
                    parts.append(Pos(*p) * Sphere(NODE_R))
    return parts


def _tie_ramp(sign, top):
    """A wedge that grooves the zip-tie channel into just the top (or bottom) of
    the cradle: open to the seat (no wall) at the outboard edge, the floor tilting
    up so the wall thickens inboard. Centered in Y, TIE_W wide."""
    bx = sign * BAR_X
    s = 1 if top else -1
    box = Box(80, TIE_W, 80)
    return Pos(bx, 0, s * GROOVE_R) * Rot(0, sign * RAMP_ANG, 0) * Pos(0, 0, s * 40) * box


def _cradle(sign):
    """Thin C-shaped cup shell hugging the inner half of the bar -- the only solid
    left at the ends. The foam laps right up against its outer face. A tapered
    zip-tie channel is cut into its top and bottom edges."""
    bx = sign * BAR_X
    big = 2 * HEX_R + 6
    ring = Pos(bx, 0, 0) * (
        (Rot(90, 0, 0) * Cylinder(GROOVE_R + SHELL_WALL, big))
        - (Rot(90, 0, 0) * Cylinder(GROOVE_R, big))
    )
    # Clip the annulus to the hex profile and to the inboard half (x toward
    # center), leaving a half-pipe trough that opens outward to take the bar.
    env = Pos(bx - 8 * sign, 0, 0) * extrude(
        Plane.YZ * RegularPolygon(HEX_R, 6), amount=8, both=True
    )
    return (ring & env) - _tie_ramp(sign, True) - _tie_ramp(sign, False)


def _center_hub():
    # Small solid block at center-bottom so the GoPro tab has something to root in.
    return Pos(0, 0, -10.5) * Box(14, 15, 6)


def gen_step():
    shapes = _lattice() + [_cradle(-1), _cradle(1), _center_hub(), _gopro_mount()]
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
