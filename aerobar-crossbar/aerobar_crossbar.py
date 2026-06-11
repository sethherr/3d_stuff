"""Aerobar accessory crossbar (solid plate).

Nests in the gap between two Ø22.2 mm aerobar extensions and carries a
GoPro-mounted light underneath. A semicircular saddle cradles each bar (one zip
tie per side, grooved into the cup top/bottom) and the mid-span is a single solid
plate sized for durability.

Unlike the earlier lattice study, every feature here is fused with real booleans
into one watertight, printable solid.

Run: python aerobar-crossbar/aerobar_crossbar.py
"""

from math import atan2, degrees
from pathlib import Path

from build123d import (
    Box,
    Cone,
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
from bd_warehouse.thread import IsoThread

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
HUB_D = 34.0                          # deck widens to this Ø disc at mid-span
HUB_RECESS = 3.0                      # depth of the recess cut into the disc top

# ---- GoPro 3-prong clevis mount (female, underside) -------------------------
GP_FINGER_T = 3.0
GP_GAP = 3.0
GP_PITCH = GP_FINGER_T + GP_GAP       # center-to-center spacing of the prongs
GP_WIDTH_Y = 15.0
GP_ROUND_R = GP_WIDTH_Y / 2
GP_HOLE_D = 5.0                       # tapped prong: M5 major diameter
GP_CLEAR_D = 5.4                      # other two prongs: M5 clearance (a touch loose)
GP_THREAD_PITCH = 0.8                 # M5 coarse: one prong is tapped for the screw
GP_CONE_H = 2.5                       # outboard cone on the tapped prong (more thread)
GP_CONE_R_BASE = 5.25                 # cone base radius (at the prong face)
GP_CONE_R_TOP = 3.75                  # cone tip radius
GP_LEN = 17.0                         # straight prong length, root to pin-hole
GP_EMBED = 1.5                        # prong roots embed this far up into the plate
GP_TOP_Z = PLATE_BOT_Z               # prongs root straight into the plate underside
GP_ROUND_Z = GP_TOP_Z - GP_LEN       # rounded tip / pin-hole center
GP_X = -BAR_X / 2                     # mount center: midway between disc and left cup
GP_Y = Y_R - GP_WIDTH_Y / 2           # shift mount back so its rear is flush with the deck back

# ---- Zip-tie channel --------------------------------------------------------
TIE_W = 6.0                           # tie width grooved into the cup edges
RAMP_ANG = 22.0                       # taper: open at the outboard edge
TIE_FLOOR_Z = PLATE_BOT_Z            # channel floor flush with the deck underside
FLOOR_TILT = 17.0                     # shelf floor ramps up toward the bar (deg)
TIE_OPEN_ANG = 30.0                   # slope of the channel's inboard exit wall (deg)


def _prong(fx, top, threaded=False):
    """One clevis prong: a flat finger with a rounded, drilled tip. The threaded
    prong also gets an outboard cone (more thread depth) and an M5 internal thread
    through prong + cone, like a real GoPro female clevis."""
    straight = Pos(fx, 0, (top + GP_ROUND_Z) / 2) * Box(
        GP_FINGER_T, GP_WIDTH_Y, top - GP_ROUND_Z
    )
    tip = Pos(fx, 0, GP_ROUND_Z) * (Rot(0, 90, 0) * Cylinder(GP_ROUND_R, GP_FINGER_T))
    finger = straight + tip
    if not threaded:
        return finger - Pos(fx, 0, GP_ROUND_Z) * (
            Rot(0, 90, 0) * Cylinder(GP_CLEAR_D / 2, GP_FINGER_T + 2)
        )
    base_x = fx - GP_FINGER_T / 2 + 0.5        # cone base (large), overlapping the prong
    cone_tip = base_x - GP_CONE_H              # outboard tip (small) of the cone
    inboard_face = fx + GP_FINGER_T / 2        # inboard face of the prong
    # Cone is centroid-centered; place its center so the base sits at base_x and it
    # tapers outboard. Rot(0,-90) sends the large bottom toward +x (the prong).
    finger = finger + Pos(base_x - GP_CONE_H / 2, 0, GP_ROUND_Z) * (
        Rot(0, -90, 0) * Cone(GP_CONE_R_BASE, GP_CONE_R_TOP, GP_CONE_H)
    )
    finger = finger - Pos((inboard_face + cone_tip) / 2, 0, GP_ROUND_Z) * (
        Rot(0, 90, 0) * Cylinder(GP_HOLE_D / 2, inboard_face - cone_tip + 2)
    )
    thread = IsoThread(
        major_diameter=GP_HOLE_D, pitch=GP_THREAD_PITCH, length=inboard_face - cone_tip,
        external=False, end_finishes=("fade", "fade"),
    )
    return finger + Pos(cone_tip, 0, GP_ROUND_Z) * (Rot(0, 90, 0) * thread)


def _gopro_mount():
    top = GP_TOP_Z + GP_EMBED        # embed the prong roots up into the plate
    back = Pos(0, GP_Y, 0)           # shift back so the rear is flush with the deck
    m = back * _prong(GP_X - GP_PITCH, top, threaded=True)   # cradle-side, tapped
    m = m + back * _prong(GP_X, top)
    m = m + back * _prong(GP_X + GP_PITCH, top)
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


PLATE_BACK_Z = 0.0                    # angled underside drops to the cradle midpoint at the back


def _underside_cutter():
    """Half-space below the angled deck underside: a plane through the front edge
    (y=-Y_R, z=PLATE_BOT_Z) dropping to PLATE_BACK_Z at the back (y=+Y_R)."""
    ang = degrees(atan2(PLATE_BOT_Z - PLATE_BACK_Z, 2 * Y_R))
    big = 400
    return Pos(0, -Y_R, PLATE_BOT_Z) * Rot(-ang, 0, 0) * Pos(0, 0, -big / 2) * Box(big, big, big)


def _plate():
    """Wedge mid-span deck: top stays flat at PLATE_TOP_Z, the underside is angled
    so the front edge stays at PLATE_BOT_Z and the back edge drops to the cradle
    midpoint (PLATE_BACK_Z). Widens to a Ø HUB_D disc, recessed on top. Bar seats
    are carved so it merges into each cup wall rather than intruding into the bar."""
    z_low = -3.0
    h = PLATE_TOP_Z - z_low
    cz = (PLATE_TOP_Z + z_low) / 2
    body = Pos(0, 0, cz) * Box(2 * BAR_X, 2 * Y_R, h)
    body = body + Pos(0, 0, cz) * Cylinder(HUB_D / 2, h)
    # Angle the underside about the front edge, dropping to PLATE_BACK_Z at the back.
    body = body - _underside_cutter()
    # Recess the disc top by HUB_RECESS, leaving a floor below.
    body = body - Pos(0, 0, PLATE_TOP_Z - HUB_RECESS + 10) * Cylinder(HUB_D / 2, 20)
    for bx in (-BAR_X, BAR_X):
        body = body - Pos(bx, 0, 0) * (
            Rot(90, 0, 0) * Cylinder(GROOVE_R + SEAT_CLEAR, 2 * HEX_R + 6)
        )
    return body


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
    # Extend the slot down to the angled deck underside so it passes the whole way
    # through the (thicker) deck. Bound it by the underside plane AND subtract the
    # cradle, so the slot stops where it meets the cup wall instead of carving into
    # it -- the deck-only material gets removed, the cradle is left intact.
    ext = Pos(e4x, 0, (TIE_FLOOR_Z - 4) / 2) * Box(2 * big, TIE_W, TIE_FLOOR_Z + 4)
    ext = ext - _underside_cutter() - _cradle(1)
    return ((floor + ext) & slant) - bore


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
