"""Aerobar accessory crossbar.

Nests in the gap *between* two round aerobar extensions and carries a
GoPro-mounted light underneath, like a tri/TT cockpit crossbar.

Form: one uniform faceted (hexagonal) bar the whole length -- no step, solid
through the middle. A single crystalline diamond cutout sits behind each saddle
and passes straight through top-to-bottom (Z): it both lightens the part and
serves as the zip-tie pass-through. Flat top/bottom faces print cleanly on FDM
and the vertical cutouts are plain through-holes (no overhang). The saddle cups
stay circular so they mate the round bars.

- Bars: 22.2 mm OD, 120 mm center-to-center.
- The body sits between the bars. Each end is a semicircular saddle that opens
  *outward* (+/-X) and mates the inner half of the bar; the bar's outer half
  stays exposed for the tie to wrap.
- Each bar is secured with one zip tie threaded down through the diamond cutout
  behind its saddle and wrapped over the bar's exposed outer half, cinching the
  bar into the saddle.
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

# One diamond cutout behind each saddle, cut through top-to-bottom (Z). Doubles
# as the lightening window and the zip-tie pass-through, so the tie threads down
# through it and wraps the bar's outer half. Half-Y stays within the top flat
# (= HEX_R/2 = 8); the outboard edge keeps a solid wall to the cup.
CUT_HALF_X = 8.0                      # half-length along the bar
CUT_HALF_Y = 7.0                      # half-length across the bar (Y)
CUT_OFFX = 23.0                       # inboard of each bar center (-> center +/-37)

# ---- GoPro 2-prong tab mount (male, underside) -----------------------------
GP_FINGER_T = 3.0                     # finger thickness (X)
GP_GAP = 3.0                          # slot between fingers
GP_OFFX = (GP_FINGER_T + GP_GAP) / 2  # +/- 3.0
GP_WIDTH_Y = 15.0
GP_ROUND_R = GP_WIDTH_Y / 2           # 7.5
GP_HOLE_D = 5.0
GP_TOP_Z = -11.0                      # rooted up into the bar
GP_ROUND_Z = -28.0                    # rounded tip center / pin-hole center


def _diamond_prism(plane, ha, hb, length):
    """A diamond, ``ha`` half-wide and ``hb`` half-tall in ``plane``, extruded
    ``length`` along that plane's normal (centered)."""
    profile = plane * Polygon((-ha, 0), (0, hb), (ha, 0), (0, -hb))
    return extrude(profile, amount=length / 2, both=True)


def _body():
    # One uniform hexagonal bar, flat top/bottom, spanning bar center to center.
    bar_len = 2 * BAR_X
    body = extrude(Plane.YZ * RegularPolygon(HEX_R, 6), amount=bar_len / 2, both=True)

    for sign in (-1, 1):
        cx = sign * BAR_X
        # Outward-facing semicircular saddle: remove the bar's inner half so the
        # cup opens toward the bar (+/-X) and seats against its inner surface.
        groove = Pos(cx, 0, 0) * (Rot(90, 0, 0) * Cylinder(GROOVE_R, 2 * HEX_R + 6))
        body = body - groove
        # Diamond cutout behind the saddle, through Z: lightening + tie pass.
        cut = _diamond_prism(Plane.XY, CUT_HALF_X, CUT_HALF_Y, 2 * HEX_R + 6)
        body = body - Pos(cx - sign * CUT_OFFX, 0, 0) * cut
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
