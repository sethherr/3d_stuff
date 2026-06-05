"""Aerobar accessory crossbar.

Nests in the gap between two Ø22.2 mm aerobar extensions and carries a
GoPro-mounted light underneath. A semicircular saddle cradles each bar (one zip
tie per side); the mid-span is an open diamond-cubic strut lattice, and a faceted
aero prow (oblique pyramid, flat top) sits on the front.

The lattice is a carbon-diamond structure -- two interpenetrating FCC lattices,
every node joined to four tetrahedral neighbours -- open, springy, and organic.
Assembled as a Compound of cylinders + spheres (no booleans) so it stays fast;
it's a visual study, not yet a watertight/printable solid.

Run: python aerobar-crossbar/aerobar_crossbar.py
"""

from lattice_kit import build_part, write_exports

CELL = 11.0
Q = CELL / 4
# 8 atoms per conventional cell, in quarter-cell units:
#   FCC sublattice + the same shifted by (1,1,1)
NODES = [(x * Q, y * Q, z * Q) for (x, y, z) in (
    (0, 0, 0), (0, 2, 2), (2, 0, 2), (2, 2, 0),
    (1, 1, 1), (1, 3, 3), (3, 1, 3), (3, 3, 1),
)]
# tetrahedral bonds: (+-1,+-1,+-1) quarter-cells; only real bonds find a node
OFFSETS = [(sx * Q, sy * Q, sz * Q)
           for sx in (1, -1) for sy in (1, -1) for sz in (1, -1)]


def gen_step():
    return build_part(NODES, OFFSETS, CELL, strut_r=0.85, node_r=1.2,
                      label="aerobar_crossbar", fairing=True, trim_back_corners=True)


if __name__ == "__main__":
    write_exports(gen_step(), __file__)
