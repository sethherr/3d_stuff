"""Octet-truss strut lattice.

FCC nodes (cube corners + face centers) joined between all nearest neighbours --
the classic octet truss of alternating octahedra and tetrahedra. Densely
triangulated and stiff-looking.

Run: python aerobar-crossbar/lattice_octet.py
"""

from lattice_kit import build_part, write_exports

CELL = 11.0
H = CELL / 2
# corner + the three face centers owned by this cell
NODES = [(0, 0, 0), (H, H, 0), (H, 0, H), (0, H, H)]
# 12 FCC nearest-neighbour directions (distance CELL/sqrt(2))
OFFSETS = [(a * H, b * H, 0) for a in (1, -1) for b in (1, -1)] + \
          [(a * H, 0, b * H) for a in (1, -1) for b in (1, -1)] + \
          [(0, a * H, b * H) for a in (1, -1) for b in (1, -1)]


def gen_step():
    return build_part(NODES, OFFSETS, CELL, strut_r=0.7, node_r=1.0,
                      label="aerobar_crossbar_octet")


if __name__ == "__main__":
    write_exports(gen_step(), __file__)
