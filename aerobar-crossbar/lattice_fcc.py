"""FCC close-packed strut lattice (dense).

FCC nodes (cube corners + face centers) joined to both their 12 nearest
neighbours (the octet diagonals) and their 6 next-nearest neighbours (along the
cube axes) -- a high-connectivity, densely triangulated lattice. Its {111}
close-packed layers face roughly toward the iso camera, so it reads as the
hexagon + 6-spoke + Star-of-David pattern of a triangular net.

Run: python aerobar-crossbar/lattice_fcc.py
"""

from lattice_kit import build_part, write_exports

CELL = 10.0
H = CELL / 2
# FCC sites: corner + the three face centers owned by this cell
NODES = [(0, 0, 0), (H, H, 0), (H, 0, H), (0, H, H)]
# 12 nearest-neighbour (octet) directions, distance CELL/sqrt(2)...
OFFSETS = [(a * H, b * H, 0) for a in (1, -1) for b in (1, -1)] + \
          [(a * H, 0, b * H) for a in (1, -1) for b in (1, -1)] + \
          [(0, a * H, b * H) for a in (1, -1) for b in (1, -1)] + \
          [(CELL, 0, 0), (-CELL, 0, 0),        # ...plus the 6 cube-axis
           (0, CELL, 0), (0, -CELL, 0),        #   next-nearest neighbours
           (0, 0, CELL), (0, 0, -CELL)]


def gen_step():
    return build_part(NODES, OFFSETS, CELL, strut_r=0.7, node_r=1.0,
                      label="aerobar_crossbar_fcc", strict_bounds=True)


if __name__ == "__main__":
    write_exports(gen_step(), __file__)
