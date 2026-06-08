"""Aerobar accessory crossbar (solid plate).

Nests in the gap between two Ø22.2 mm aerobar extensions and carries a
GoPro-mounted light underneath. A semicircular saddle cradles each bar (one zip
tie per side, grooved into the cup top/bottom) and the mid-span is a single solid
plate sized for durability.

Unlike the earlier lattice study, every feature here is fused with real booleans
into one watertight, printable solid.

Run: python aerobar-crossbar/aerobar_crossbar.py
"""

from pathlib import Path

from build123d import (
    Box,
    Cylinder,
    Plane,
    Pos,
    RegularPolygon,
    Rot,
    export_gltf,
    export_step,
    export_stl,
    extrude,
    mirror,
)

# ---- Bar / saddle geometry --------------------------------------------------
BAR_D = 22.2
BAR_R = BAR_D / 2
CLEAR = 0.3
GROOVE_R = BAR_R + CLEAR              # 11.4 mm half-circle cradle
SPAN_CC = 120.0
BAR_X = SPAN_CC / 2                   # 60: bar centers at +/-BAR_X
HEX_R = 16.0                          # cradle envelope radius (vertex)
HEX_FLAT_HALF = HEX_R * 3 ** 0.5 / 2  # hex flat half-height

SHELL_WALL = 2.4                      # cradle cup wall thickness
SEAT_CLEAR = 0.4                      # keep the plate this far clear of each seat
Y_R = 12.0                            # mid-span half-depth (Y)

# ---- Plate ------------------------------------------------------------------
# A single horizontal solid deck spanning the gap between the two cradles. Its
# top face is flush with the top of the cradle cups (z = GROOVE_R + SHELL_WALL),
# and it extends down by PLATE_T. 6 mm is plenty for PLA/PETG at this span.
PLATE_T = 6.0                         # plate thickness (Z)
PLATE_TOP_Z = GROOVE_R + SHELL_WALL   # 13.8: top flush with the cup tops
PLATE_BOT_Z = PLATE_TOP_Z - PLATE_T

# ---- GoPro 2-prong tab mount (male, underside) ------------------------------
GP_FINGER_T = 3.0
GP_GAP = 3.0
GP_OFFX = (GP_FINGER_T + GP_GAP) / 2
GP_WIDTH_Y = 15.0
GP_ROUND_R = GP_WIDTH_Y / 2
GP_HOLE_D = 5.0
GP_LEN = 17.0                         # straight prong length, root to pin-hole
GP_EMBED = 1.5                        # prong roots embed this far up into the plate
GP_TOP_Z = PLATE_BOT_Z               # prongs root straight into the plate underside
GP_ROUND_Z = GP_TOP_Z - GP_LEN       # rounded tip / pin-hole center

# ---- Zip-tie channel --------------------------------------------------------
TIE_W = 6.0                           # tie width grooved into the cup edges
RAMP_ANG = 22.0                       # taper: open at the outboard edge
TIE_FLOOR_Z = PLATE_BOT_Z            # channel floor flush with the deck underside
FLOOR_TILT = 15.0                     # shelf floor ramps up toward the bar (deg)
TIE_OPEN_ANG = 30.0                   # slope of the channel's inboard exit wall (deg)


def _gopro_mount():
    m = None
    top = GP_TOP_Z + GP_EMBED        # embed the prong roots up into the plate
    for fx in (-GP_OFFX, GP_OFFX):
        straight = Pos(fx, 0, (top + GP_ROUND_Z) / 2) * Box(
            GP_FINGER_T, GP_WIDTH_Y, top - GP_ROUND_Z
        )
        tip = Pos(fx, 0, GP_ROUND_Z) * (Rot(0, 90, 0) * Cylinder(GP_ROUND_R, GP_FINGER_T))
        finger = straight + tip
        hole = Pos(fx, 0, GP_ROUND_Z) * (
            Rot(0, 90, 0) * Cylinder(GP_HOLE_D / 2, GP_FINGER_T + 2)
        )
        finger = finger - hole
        m = finger if m is None else m + finger
    return m


def _tie_ramp(sign, top):
    """A wedge that grooves the zip-tie channel into the top (or bottom) of the
    cradle: open to the seat at the outboard edge, the floor tilting up so the
    wall thickens inboard. Centered in Y, TIE_W wide."""
    bx = sign * BAR_X
    s = 1 if top else -1
    box = Box(80, TIE_W, 80)
    return Pos(bx, 0, s * GROOVE_R) * Rot(0, sign * RAMP_ANG, 0) * Pos(0, 0, s * 40) * box


def _cradle(sign):
    """Thin C-shaped cup hugging the inner half of the bar, with a tapered
    zip-tie channel cut into its top and bottom edges. Front and rear are
    flattened to single planes level with the plate edges."""
    bx = sign * BAR_X
    big = 2 * HEX_R + 6
    ring = Pos(bx, 0, 0) * (
        (Rot(90, 0, 0) * Cylinder(GROOVE_R + SHELL_WALL, big))
        - (Rot(90, 0, 0) * Cylinder(GROOVE_R, big))
    )
    env = Pos(bx - 8 * sign, 0, 0) * extrude(
        Plane.YZ * RegularPolygon(HEX_R, 6), amount=8, both=True
    )
    # Square both the front and rear of the env to full height so each cup
    # opening is one clean arc. Without this the hex vertex (at +/-Y) splits the
    # opening into three slanted-facet segments instead of a single edge.
    for fy in (-10, 10):
        env = env + Pos(bx - 8 * sign, fy, 0) * Box(16, 8, 2 * HEX_FLAT_HALF + 1)
    cradle = (ring & env) - _tie_ramp(sign, True) - _tie_ramp(sign, False)
    # Flatten the rear (+Y) and the front (-Y) to single planes level with the
    # plate edges (instead of the hex points).
    cradle = cradle - Pos(0, Y_R + 50, 0) * Box(400, 100, 400)        # rear (+Y)
    cradle = cradle - Pos(0, -(Y_R + 50), 0) * Box(400, 100, 400)     # front (-Y)
    return cradle


def _plate():
    """The solid horizontal mid-span deck. Spans cup to cup, full depth in Y,
    with its top flush at PLATE_TOP_Z. The bar seats are carved so it merges into
    each cup wall around the bar instead of intruding into it."""
    plate = Pos(0, 0, (PLATE_TOP_Z + PLATE_BOT_Z) / 2) * Box(
        2 * BAR_X, 2 * Y_R, PLATE_T
    )
    for bx in (-BAR_X, BAR_X):
        plate = plate - Pos(bx, 0, 0) * (
            Rot(90, 0, 0) * Cylinder(GROOVE_R + SEAT_CLEAR, 2 * HEX_R + 6)
        )
    return plate


def _tie_tunnel():
    """Open tie channel cutter for the +X cup (the -X one is its mirror). A
    TIE_W-wide (Y) slot follows the bar's curve over the top, down to the bar
    surface, with everything above removed. Its inboard exit wall through the deck
    is sloped (not vertical), leaning toward the bar so the tie passes cleanly."""
    bx = BAR_X
    big = 2 * HEX_R + 6
    bore = Pos(bx, 0, 0) * (Rot(90, 0, 0) * Cylinder(GROOVE_R, big + 2))
    # Strip from TIE_FLOOR_Z up, tilted so the shelf floor ramps up toward the bar.
    # Pivot on the outer-wall edge (where the floor meets the cup wall at z=floor),
    # so that edge stays put while the bore-side edge rises. The tilt is gentle
    # enough that the bore still controls the deep channel over the bar.
    e4x = bx - ((GROOVE_R + SHELL_WALL) ** 2 - TIE_FLOOR_Z ** 2) ** 0.5
    floor = (
        Pos(e4x, 0, TIE_FLOOR_Z)
        * Rot(0, -FLOOR_TILT, 0)
        * Pos(0, 0, big)
        * Box(2 * big, TIE_W, 2 * big)
    )
    # Bound it inboard with a sloped plane; keep the bar (outboard, +x) side. The
    # plane leans so its top is toward the bar, angling the deck exit wall.
    inboard_x = bx - (GROOVE_R + SHELL_WALL + 1)
    slant = (
        Pos(inboard_x, 0, PLATE_BOT_Z)
        * Rot(0, TIE_OPEN_ANG, 0)
        * Pos(1.5 * big, 0, 0)
        * Box(3 * big, TIE_W + 4, 4 * big)
    )
    return (floor & slant) - bore


def gen_step():
    part = (
        _cradle(-1)
        + _cradle(1)
        + _plate()
        + _gopro_mount()
    )
    cut = _tie_tunnel()
    part = part - cut - mirror(cut, Plane.YZ)
    part.label = "aerobar_crossbar"
    return part


def write_exports(part, pyfile):
    here = Path(pyfile).with_suffix("")
    print("solids:", len(part.solids()))
    print("volume (mm^3):", round(part.volume, 1))
    export_step(part, str(here) + ".step")
    export_stl(part, str(here) + ".stl")
    export_gltf(part, str(here) + ".glb", binary=True)
    print("wrote .step / .stl / .glb")


if __name__ == "__main__":
    write_exports(gen_step(), __file__)
