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
    Edge,
    Face,
    Plane,
    Pos,
    RegularPolygon,
    Rot,
    Solid,
    Sphere,
    Vector,
    Vertex,
    Wire,
    export_gltf,
    export_step,
    export_stl,
    extrude,
    loft,
)

from aerobar_crossbar import (
    BAR_X,
    GROOVE_R,
    HEX_R,
    _gopro_mount,
)

# Tie geometry the lattice keeps clear and grooves into the cradle. The base part
# redesigned its own tie routing (through-saddle X-holes); the lattice variants
# keep their own cradle-channel approach, so these live here rather than imported.
TIE_SLOT_OFFX = 16.0   # inboard channel offset from each bar center
TIE_SLOT_X = 3.0       # channel width (X)
TIE_SLOT_Y = 6.0       # channel / tie width (Y)

EDGE_X = BAR_X - 1.0   # lattice fills out to here -- just shy of the bar centers
Y_R = 12.0             # lattice half-extent in Y (within the hex flats)
Z_R = 12.0             # lattice half-extent in Z
SHELL_WALL = 2.4       # cradle cup wall thickness (the only solid at the ends)
SEAT_CLEAR = 0.4       # keep struts this far clear of each bar's seat
TIE_W = TIE_SLOT_Y     # zip-tie channel width (matches the tie slot)
RAMP_ANG = 22.0        # tie channel taper: open at the outboard edge, the floor
                       # thickening inboard over ~(GROOVE_R*tan) mm


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


def _tie_ramp(sign, top):
    """A wedge that grooves the zip-tie channel into just the top (or bottom) of
    the cradle: open to the seat (no wall) at the outboard edge, the floor tilting
    up so the wall thickens inboard. Centered in Y, TIE_W wide."""
    bx = sign * BAR_X
    s = 1 if top else -1
    box = Box(80, TIE_W, 80)
    # bottom face -> ramp plane through the apex (bx, 0, +/-GROOVE_R), tilted so it
    # rises away from the outboard edge; the box removes everything past it.
    return Pos(bx, 0, s * GROOVE_R) * Rot(0, sign * RAMP_ANG, 0) * Pos(0, 0, s * 40) * box


def _cradle(sign):
    """Thin C-shaped cup shell hugging the inner half of the bar, with a tapered
    zip-tie channel cut into its top and bottom edges. The rear (+Y) is flattened
    to a single plane at the lattice back edge instead of the hex's rear point."""
    bx = sign * BAR_X
    big = 2 * HEX_R + 6
    ring = Pos(bx, 0, 0) * (
        (Rot(90, 0, 0) * Cylinder(GROOVE_R + SHELL_WALL, big))
        - (Rot(90, 0, 0) * Cylinder(GROOVE_R, big))
    )
    env = Pos(bx - 8 * sign, 0, 0) * extrude(
        Plane.YZ * RegularPolygon(HEX_R, 6), amount=8, both=True
    )
    cradle = (ring & env) - _tie_ramp(sign, True) - _tie_ramp(sign, False)
    # Flatten the rear to a single plane level with the lattice's back edge.
    cradle = cradle - Pos(0, Y_R + 50, 0) * Box(400, 100, 400)
    return cradle


def _center_hub():
    return Pos(0, 0, -10.5) * Box(14, 15, 6)


# ---- Aero nose fairing ------------------------------------------------------
# A faceted prow on the FRONT (-Y) face that continues the bar's hex faceting: its
# back is the two front facets of the saddle horns (@cad f2035/f2036 left,
# f2051/f2052 right) -- an upper facet and a lower facet meeting at the hex front
# vertex -- and each side folds along that vertex into the apex. Built as an upper
# and a lower half-pyramid (each coplanar with a facet) unioned together.
FAIR_HALF_SPAN = BAR_X               # half-width = out to the bar centers / cups
FAIR_NOSE = 18.0                      # apex this far forward of the hex front vertex


def _front_fairing():
    hf = HEX_R * 3 ** 0.5 / 2          # hex flat half-height (~13.86)
    fv = -HEX_R                        # hex front vertex y (-16): facets meet here
    fe = -HEX_R / 2                    # where the facets meet the flats (y=-8, z=+/-hf)
    half = FAIR_HALF_SPAN
    Lt, Rt = (-half, fe, hf), (half, fe, hf)
    Lb, Rb = (-half, fe, -hf), (half, fe, -hf)
    Lv, Rv = (-half, fv, 0), (half, fv, 0)
    apex = Vertex(0, fv - FAIR_NOSE, 0)

    def quad(pts):
        edges = [Edge.make_line(Vector(*pts[i]), Vector(*pts[(i + 1) % 4])) for i in range(4)]
        return Face(Wire(edges))

    upper = loft([quad([Lt, Rt, Rv, Lv]), apex])   # coplanar with the upper facets
    lower = loft([quad([Lb, Rb, Rv, Lv]), apex])   # coplanar with the lower facets
    prow = upper + lower
    # Don't cover the bar seats: carve the cup cylinders at the seat radius so the
    # prow's cup opening matches the cradle and the fairing touches the bar (prow +
    # cradle form one continuous cup). (A ~1 mm^2 sliver face remains at the
    # ridge-tangent point -- a boolean artifact that fuses out when the part is
    # made watertight; cutting it away would lift the prow off the bar.)
    for bx in (-BAR_X, BAR_X):
        prow = prow - Pos(bx, 0, 0) * (Rot(90, 0, 0) * Cylinder(GROOVE_R, 2 * HEX_R + 6))
    return prow


def build_part(base_nodes, neighbor_offsets, cell, strut_r=0.8, node_r=1.15,
               label="lattice", strict_bounds=False, fairing=False, trim_back_corners=False):
    """Tile `base_nodes` (positions within one `cell`-sized cube) on a cubic grid,
    connect each node to existing neighbours at `neighbor_offsets`, and assemble
    the struts + nodes + end cradles + GoPro hub into one Compound.

    By default a strut is kept when its midpoint is in bounds (struts may poke a
    little past the edge). `strict_bounds=True` keeps a strut only when *both*
    endpoints are in bounds -- needed for longer struts that would otherwise
    leave stubs sticking out (e.g. the dense FCC variant)."""
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
            # Drop the back-top and back-bottom corner rows (and their struts).
            if trim_back_corners and p[1] > Y_R - 1.5 and abs(p[2]) > Z_R - 1.5:
                continue
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
            in_region = (_in_bounds(pa) and _in_bounds(pb)) if strict_bounds else _in_bounds(mid)
            if not in_region or _excluded(pa) or _excluded(pb):
                continue
            parts.append(_strut(pa, pb, strut_r))
            for nd, ndk in ((pa, key), (pb, qk)):
                if ndk not in used_nodes and _in_bounds(nd) and not _excluded(nd):
                    used_nodes.add(ndk)
                    parts.append(Pos(*nd) * Sphere(node_r))

    parts += [_cradle(-1), _cradle(1), _center_hub(), _gopro_mount()]
    if fairing:
        parts.append(_front_fairing())
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
