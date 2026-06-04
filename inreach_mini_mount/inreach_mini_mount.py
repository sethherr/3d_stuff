"""Secure pedestal cradle for a Garmin inReach Mini / Mini 2.

Design priorities (per request): security first, screen visibility second.

- 1" x 1" (25.4 mm) flat square foot at the bottom to epoxy onto a surface.
- Flared neck from the foot up to the cradle: widens the stance and beefs up
  the joint without enlarging the glued footprint.
- Deep wrap cradle: full back wall + full side walls + front retaining lips +
  a closed floor. Captures the lower ~72 mm of the device on all four sides.
- Strap slots through both side walls for a velcro / zip-tie strap across the
  front -> positive retention even with print flex.

Coordinates: Z up = device long axis. +Y = front (screen / open side).
Origin centered in X/Y, Z=0 at the flat epoxy foot.
"""

from build123d import (
    Box,
    Pos,
    Rectangle,
    RectangleRounded,
    extrude,
    loft,
)

# ---------------------------------------------------------------- parameters
# Garmin inReach Mini / Mini 2 body envelope (mm)
DEV_W, DEV_D, DEV_H = 51.5, 26.2, 99.6
DEV_R = 7.0                       # rounded long-edge radius (estimate)
CLEAR = 0.5                       # fit clearance per side (printed cradle)

POCKET_W = DEV_W + 2 * CLEAR
POCKET_D = DEV_D + 2 * CLEAR
POCKET_R = DEV_R + CLEAR

WALL = 3.0                        # cradle wall thickness
OUTER_W = POCKET_W + 2 * WALL
OUTER_D = POCKET_D + 2 * WALL
OUTER_R = POCKET_R + WALL

BASE_SQ = 25.4                    # 1" x 1" epoxy foot
BASE_T = 5.0                      # foot thickness (flat bonding pad)
NECK_T = 6.0                      # flared transition foot -> cradle
SHELF_T = 4.0                     # closed floor the device rests on
CHAN_H = 72.0                     # wrap-wall height above the floor
FRONT_LIP = 12.0                  # how far each front lip reaches inward

FLOOR_TOP = BASE_T + NECK_T + SHELF_T   # device sits here (Z)
TOP_Z = FLOOR_TOP + CHAN_H

# velcro / zip-tie strap slot (through each side wall)
SLOT_Z = 22.0                     # vertical opening
SLOT_Y = 4.0                      # front-back opening
SLOT_CZ = FLOOR_TOP + CHAN_H * 0.6


def gen_step():
    # --- flat 1" epoxy foot --------------------------------------------------
    foot = Pos(0, 0, BASE_T / 2) * Box(BASE_SQ, BASE_SQ, BASE_T)

    # --- flared neck: square foot -> cradle footprint ------------------------
    neck = loft(
        [
            Pos(0, 0, BASE_T) * Rectangle(BASE_SQ, BASE_SQ),
            Pos(0, 0, BASE_T + NECK_T) * RectangleRounded(OUTER_W, OUTER_D, OUTER_R),
        ]
    )

    # --- closed floor (device rests on this) ---------------------------------
    floor = Pos(0, 0, BASE_T + NECK_T) * extrude(
        RectangleRounded(OUTER_W, OUTER_D, OUTER_R), SHELF_T
    )

    # --- wrap walls: C-channel cross-section ---------------------------------
    ring = RectangleRounded(OUTER_W, OUTER_D, OUTER_R) - RectangleRounded(
        POCKET_W, POCKET_D, POCKET_R
    )
    # open the front center, leaving FRONT_LIP-wide retaining lips at each side
    front_gap = Pos(0, OUTER_D / 2) * Rectangle(POCKET_W - 2 * FRONT_LIP, OUTER_D)
    c_section = ring - front_gap
    walls = Pos(0, 0, FLOOR_TOP) * extrude(c_section, CHAN_H)

    part = foot + neck + floor + walls

    # --- strap slots through each side wall ----------------------------------
    inner_x = POCKET_W / 2 - 3.0
    outer_x = OUTER_W / 2 + 1.0
    slot_len = outer_x - inner_x
    slot_cx = (inner_x + outer_x) / 2
    slot_cy = POCKET_D / 2 - SLOT_Y / 2
    for sign in (-1, 1):
        part -= Pos(sign * slot_cx, slot_cy, SLOT_CZ) * Box(slot_len, SLOT_Y, SLOT_Z)

    part.label = "inreach_mini_mount"
    return part


if __name__ == "__main__":
    p = gen_step()
    bb = p.bounding_box()
    print(f"label:  {p.label}")
    print(f"bbox:   {bb.size.X:.1f} x {bb.size.Y:.1f} x {bb.size.Z:.1f} mm")
    print(f"volume: {p.volume / 1000:.1f} cm^3")
