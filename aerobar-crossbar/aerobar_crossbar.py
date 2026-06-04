"""Aerobar accessory crossbar.

Nests in the gap *between* two round aerobar extensions and carries a
GoPro-mounted light underneath, like a tri/TT cockpit crossbar.

Form: one uniform faceted (hexagonal) bar the whole length -- no step between
ends and middle. Two crystalline diamond windows lighten the mid-span; a round
cutout sits just inboard of each saddle. The saddle cups stay circular so they
mate the round bars. Flat top/bottom faces print cleanly on FDM.

Tie routing: instead of wrapping the bulky saddle, the zip tie threads *through*
the part on rounded walls so it lies flat. A round tunnel runs in X through the
top of each saddle into the cup, and another through the bottom; the tie passes
in through the round inboard cutout, out the top tunnel over the bar's exposed
crown, back in the bottom tunnel, and cinches -- hugging the bar, not the saddle.

- Bars: 22.2 mm OD, 120 mm center-to-center.
- The body sits between the bars. Each end is a semicircular saddle that opens
  *outward* (+/-X) and mates the inner half of the bar; the bar's outer half
  stays exposed for the tie to wrap.
- Each bar is secured with one zip tie threaded through the saddle: in via the
  round inboard cutout, out the top tunnel over the bar's exposed crown, back in
  the bottom tunnel, and cinched -- pulling the bar down into the cup.
- Bottom center: GoPro 2-prong tab mount (3 mm fingers, 5 mm pin hole) for a
  light; hole axis is left-right so the light tilts up/down to aim.

Conventions: millimeters. X = crossbar span. Y = bar axis (fore/aft). Z = up.
Bar centers sit at (+/-60, 0, 0) with the bar centerline at z = 0.
"""

from pathlib import Path

from build123d import (
    Box,
    Cylinder,
    Plane,
    Polygon,
    Pos,
    RegularPolygon,
    Rot,
    export_gltf,
    export_step,
    export_stl,
    extrude,
)

# ---- Bars / saddles ---------------------------------------------------------
BAR_D = 22.2
BAR_R = BAR_D / 2
CLEAR = 0.3
GROOVE_R = BAR_R + CLEAR              # 11.4 mm half-circle cradle

SPAN_CC = 120.0
BAR_X = SPAN_CC / 2                   # 60

# ---- Uniform faceted bar ----------------------------------------------------
# Hex radius = vertex radius; flat-to-flat height = 1.732 * radius. Sized so the
# saddle cup leaves solid "horn" material above/below it.
HEX_R = 16.0                          # one section the whole length (no step)
HEX_FLAT = HEX_R * 3 ** 0.5 / 2       # ~13.86, half-height of the flats

# Crystalline diamond windows that lighten the mid-span (cut through in Y).
WIN_HALF_X = 10.0                     # half-length along the bar
WIN_HALF_Z = 9.0                      # half-height (leaves top/bottom flanges)
WIN_CX = 22.0                         # +/- mid-span window centers

# Round inboard cutout next to each saddle (the tie's entry/return pocket). Round
# -- not a diamond -- so the tie lies flat, like it does in the saddle cup.
NEAR_CX = 36.0                        # +/- cutout centers
NEAR_R = 8.0                          # cutout radius (cut through Y)

# Zip-tie X-holes: a round tunnel runs in X through the top of each saddle into
# the cup, and another through the bottom. Round walls so the tie lies flat. The
# tie threads in via the round cutout, out the top tunnel over the bar's crown,
# back the bottom tunnel, and cinches.
XH_CX = 48.0                          # +/- tunnel center in X (NEAR cutout -> cup)
XH_LEN = 24.0                         # length along X
XH_R = 3.5                            # tunnel radius (tie cross-section + slack)
XH_OFFZ = 7.0                         # +/- above/below center, near the cup edges

# ---- GoPro 2-prong tab mount (male, underside) -----------------------------
GP_FINGER_T = 3.0                     # finger thickness (X)
GP_GAP = 3.0                          # slot between fingers
GP_OFFX = (GP_FINGER_T + GP_GAP) / 2  # +/- 3.0
GP_WIDTH_Y = 15.0
GP_ROUND_R = GP_WIDTH_Y / 2           # 7.5
GP_HOLE_D = 5.0
GP_TOP_Z = -11.0                      # rooted up into the bar
GP_ROUND_Z = -28.0                    # rounded tip center / pin-hole center


def _diamond_window(cx, hx, hz):
    """A point-up diamond prism through Y (self-supporting window when printed)."""
    profile = Plane.XZ * Polygon((-hx, 0), (0, hz), (hx, 0), (0, -hz))
    win = extrude(profile, amount=HEX_R + 5, both=True)  # all the way through Y
    return Pos(cx, 0, 0) * win


def _body():
    # One uniform hexagonal bar, flat top/bottom, spanning bar center to center.
    bar_len = 2 * BAR_X
    body = extrude(Plane.YZ * RegularPolygon(HEX_R, 6), amount=bar_len / 2, both=True)

    # Lighten the mid-span with crystalline diamond windows (no step-down).
    for cx in (-WIN_CX, WIN_CX):
        body = body - _diamond_window(cx, WIN_HALF_X, WIN_HALF_Z)

    for sign in (-1, 1):
        cx = sign * BAR_X
        # Outward-facing semicircular saddle: remove the bar's inner half so the
        # cup opens toward the bar (+/-X) and seats against its inner surface.
        groove = Pos(cx, 0, 0) * (Rot(90, 0, 0) * Cylinder(GROOVE_R, 2 * HEX_R + 6))
        body = body - groove
        # Round cutout just inboard of the saddle (the tie's entry/return pocket)
        # -- rounded, not a diamond, so the tie lies flat against it.
        body = body - Pos(sign * NEAR_CX, 0, 0) * (
            Rot(90, 0, 0) * Cylinder(NEAR_R, 2 * HEX_R + 10)
        )
        # Top & bottom round tunnels from that cutout into the cup, so the tie
        # rides on rounded walls (like the saddle) instead of sharp edges.
        for off in (XH_OFFZ, -XH_OFFZ):
            body = body - Pos(sign * XH_CX, 0, off) * (
                Rot(0, 90, 0) * Cylinder(XH_R, XH_LEN)
            )
    return body


def _gopro_mount():
    m = None
    for fx in (-GP_OFFX, GP_OFFX):
        straight = Pos(fx, 0, (GP_TOP_Z + GP_ROUND_Z) / 2) * Box(
            GP_FINGER_T, GP_WIDTH_Y, GP_TOP_Z - GP_ROUND_Z
        )
        tip = Pos(fx, 0, GP_ROUND_Z) * (Rot(0, 90, 0) * Cylinder(GP_ROUND_R, GP_FINGER_T))
        finger = straight + tip
        hole = Pos(fx, 0, GP_ROUND_Z) * (
            Rot(0, 90, 0) * Cylinder(GP_HOLE_D / 2, GP_FINGER_T + 2)
        )
        finger = finger - hole
        m = finger if m is None else m + finger
    return m


def gen_step():
    part = _body() + _gopro_mount()
    part.label = "aerobar_crossbar"
    return part


if __name__ == "__main__":
    p = gen_step()
    bb = p.bounding_box()
    print("bbox min:", bb.min)
    print("bbox max:", bb.max)
    print("volume mm^3:", round(p.volume, 1))

    here = Path(__file__).with_suffix("")
    export_step(p, str(here) + ".step")
    export_stl(p, str(here) + ".stl")
    export_gltf(p, str(here) + ".glb", binary=True)
    print("wrote .step / .stl / .glb")
