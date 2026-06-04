"""Aerobar accessory crossbar.

Nests in the gap *between* two round aerobar extensions and carries a
GoPro-mounted light underneath, like a tri/TT cockpit crossbar.

Form: a faceted "bone" -- a fat hexagonal saddle pod at each end joined by a
slimmer hexagonal spine. The flat facets give clean FDM bed contact and
self-supporting (~60deg) overhangs, a deeper section than a round bar (stiffer
in bending), and a more organic/crystalline look than a perfect cylinder. The
saddle cups stay circular so they mate the round bars.

Printing: lay it on a flat (the GoPro tab points up as a vertical fin). The
hex faces print without support; only the down-facing saddle cup wants a little.

- Bars: 22.2 mm OD, 120 mm center-to-center.
- The body sits between the bars. Each pod end is a semicircular saddle that
  opens *outward* (+/-X) and mates the inner half of the bar; the bar's outer
  half stays exposed for the tie to wrap.
- Each bar is secured with one zip tie: a vertical through-slot behind each
  saddle lets a tie pass through the pod and wrap the bar's exposed outer half,
  cinching the bar into the saddle.
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

# ---- Faceted "bone" body ----------------------------------------------------
# Hex radius = vertex radius; flat-to-flat height = 1.732 * radius. The pod must
# clear the cup (GROOVE_R) with material left for the saddle horns.
POD_R = 15.5                          # end-pod hex radius (flat-flat ~26.8)
POD_X = 22.0                          # pod length along X (covers cup + slot)
POD_CX = BAR_X - POD_X / 2            # 49, pod center in X
SPINE_R = 11.0                        # slim mid-span hex radius (flat-flat ~19)
SPINE_OVERLAP = 6.0                   # spine reaches into the pods to fuse

# Zip-tie vertical slot: one tie per side threads through and wraps the bar's
# outer half. Centered on the bar (y = 0).
TIE_SLOT_X = 3.0
TIE_SLOT_Y = 6.0
TIE_SLOT_OFFX = 16.0                  # inboard of each bar center, behind the cup

# ---- GoPro 2-prong tab mount (male, underside) -----------------------------
GP_FINGER_T = 3.0                     # finger thickness (X)
GP_GAP = 3.0                          # slot between fingers
GP_OFFX = (GP_FINGER_T + GP_GAP) / 2  # +/- 3.0
GP_WIDTH_Y = 15.0
GP_ROUND_R = GP_WIDTH_Y / 2           # 7.5
GP_HOLE_D = 5.0
GP_TOP_Z = -7.0                       # rooted up into the spine
GP_ROUND_Z = -24.0                    # rounded tip center / pin-hole center


def _hex_x(r, length):
    """A hexagonal prism centered at the origin, axis along X, flat top/bottom."""
    return extrude(Plane.YZ * RegularPolygon(r, 6), amount=length / 2, both=True)


def _body():
    # Slim faceted spine spanning the gap, fat faceted pods at each end.
    spine_len = 2 * (BAR_X - POD_X + SPINE_OVERLAP)
    body = _hex_x(SPINE_R, spine_len)
    for sign in (-1, 1):
        body = body + Pos(sign * POD_CX, 0, 0) * _hex_x(POD_R, POD_X)

    for sign in (-1, 1):
        cx = sign * BAR_X
        # Outward-facing semicircular saddle: remove the bar's inner half so the
        # cup opens toward the bar (+/-X) and seats against its inner surface.
        groove = Pos(cx, 0, 0) * (Rot(90, 0, 0) * Cylinder(GROOVE_R, 2 * POD_R + 6))
        body = body - groove
        # Zip-tie slot behind the saddle: one vertical through-hole so a tie can
        # pass through the pod and wrap the bar's exposed outer half.
        slot = Pos(cx - sign * TIE_SLOT_OFFX, 0, 0) * Box(
            TIE_SLOT_X, TIE_SLOT_Y, 2 * POD_R + 6
        )
        body = body - slot
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
