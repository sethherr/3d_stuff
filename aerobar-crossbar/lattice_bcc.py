"""BCC strut lattice.

Body-centered cubic: a node at every cube corner plus one at each cube center,
joined only along the body diagonals -- open rows of X / octahedral cells.

Run: python aerobar-crossbar/lattice_bcc.py
"""

from lattice_kit import build_part, write_exports

CELL = 9.0
H = CELL / 2
NODES = [(0, 0, 0), (H, H, H)]                      # corner + body center
OFFSETS = [(sx * H, sy * H, sz * H)                 # the 8 body diagonals
           for sx in (1, -1) for sy in (1, -1) for sz in (1, -1)]


def gen_step():
    return build_part(NODES, OFFSETS, CELL, strut_r=0.85, node_r=1.2,
                      label="aerobar_crossbar_bcc")


if __name__ == "__main__":
    write_exports(gen_step(), __file__)
