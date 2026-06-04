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
WIN_HALF_X = 8.0                      # half-length along the bar
WIN_HALF_Z = 9.0                      # half-height (leaves top/bottom flanges)
WIN_CX = 22.0                         # +/- mid-span window centers

# Zip-tie anchor: a *convex* ridge just inboard of each cup that the tie wraps --
# same curvature as the bar in the saddle, so the tie lies flat. A pocket behind
# the ridge gives the tie room to wrap it; two tunnels run out to the cup so the
# tie passes over the bar's crown. Cinching pulls the bar against the cup.
PKT_IN = 31.0                         # pocket inboard x (gives the tie room)
RIDGE_CX = 43.0                       # ridge center x (pocket's outboard wall)
RIDGE_R = 5.0                         # convex ridge radius (tie wraps this)
PKT_HZ = 8.0                          # pocket half-height (z)
TUN_W = 6.5                           # tunnel width (Y) = tie width + slack
TUN_H = 3.0                           # tunnel height (Z); rectangular so the flat
TUN_Z = 5.0                           # tie lies flat. z offset (tangent to ridge)
TUN_OUT = 60.0                        # tunnel reaches the cup/end

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
    env = extrude(Plane.YZ * RegularPolygon(HEX_R, 6), amount=bar_len / 2, both=True)
    body = env

    # Lighten the mid-span with crystalline diamond windows (no step-down).
    for cx in (-WIN_CX, WIN_CX):
        body = body - _diamond_window(cx, WIN_HALF_X, WIN_HALF_Z)

    for sign in (-1, 1):
        cx = sign * BAR_X
        # Outward-facing semicircular saddle: remove the bar's inner half so the
        # cup opens toward the bar (+/-X) and seats against its inner surface.
        groove = Pos(cx, 0, 0) * (Rot(90, 0, 0) * Cylinder(GROOVE_R, 2 * HEX_R + 6))
        body = body - groove
        # Pocket inboard of the cup -> room for the tie to wrap the ridge.
        body = body - Pos(sign * (PKT_IN + RIDGE_CX) / 2, 0, 0) * Box(
            abs(RIDGE_CX - PKT_IN), 2 * HEX_R + 10, 2 * PKT_HZ
        )
        # Convex ridge on the pocket's outboard wall (added back): the tie wraps
        # it like it wraps the bar -- same curvature -- so it lies flat. Clipped
        # to the bar envelope so it can't poke out the sides.
        ridge = Pos(sign * RIDGE_CX, 0, 0) * (
            Rot(90, 0, 0) * Cylinder(RIDGE_R, 2 * HEX_R + 10)
        )
        body = body + (ridge & env)
        # Two rectangular tunnels from the ridge top/bottom out to the cup over
        # the bar -- rectangular (not round) so the flat zip tie lies flat.
        for off in (TUN_Z, -TUN_Z):
            body = body - Pos(sign * (RIDGE_CX + TUN_OUT) / 2, 0, off) * Box(
                abs(TUN_OUT - RIDGE_CX), TUN_W, TUN_H
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
