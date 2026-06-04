"""Aerobar accessory crossbar.

Nests in the gap *between* two round aerobar extensions and carries a
GoPro-mounted light underneath, like a tri/TT cockpit crossbar.

Form: a round "bone" -- a fat circular saddle pod at each end joined by a slim
round spine. Circular cross-section throughout (no slab faces) for an organic
look that stays strong and light.

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
    Axis,
    Box,
    Cylinder,
    GeomType,
    Pos,
    Rot,
    export_gltf,
    export_step,
    export_stl,
    fillet,
)

# ---- Bars / saddles ---------------------------------------------------------
BAR_D = 22.2
BAR_R = BAR_D / 2
CLEAR = 0.3
GROOVE_R = BAR_R + CLEAR              # 11.4 mm half-circle cradle

SPAN_CC = 120.0
BAR_X = SPAN_CC / 2                   # 60

# ---- Round "bone" body ------------------------------------------------------
POD_R = 13.5                          # end-pod radius (round saddle section)
POD_X = 22.0                          # pod length along X (covers cup + slot)
POD_CX = BAR_X - POD_X / 2            # 49, pod center in X
SPINE_R = 10.5                        # slim mid-span spine radius
SPINE_OVERLAP = 6.0                   # spine reaches into the pods to fuse
SHOULDER_FILLET = 2.0                 # blend the pod -> spine step

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
GP_TOP_Z = -5.0                       # rooted up into the spine
GP_ROUND_Z = -22.0                    # rounded tip center / pin-hole center


def _body():
    # Slim round spine spanning the gap, fat round pods at each end.
    spine_len = 2 * (BAR_X - POD_X + SPINE_OVERLAP)
    body = Rot(0, 90, 0) * Cylinder(SPINE_R, spine_len)
    for sign in (-1, 1):
        pod = Pos(sign * POD_CX, 0, 0) * (Rot(0, 90, 0) * Cylinder(POD_R, POD_X))
        body = body + pod

    # Blend the pod->spine shoulder so the section flows (and to ease the riser).
    # Only the inner (spine-radius) ring takes the concave fillet cleanly.
    shoulders = [
        e
        for e in body.edges().filter_by(GeomType.CIRCLE)
        if abs(e.radius - SPINE_R) < 1e-6 and abs(abs(e.center().X) - (BAR_X - POD_X)) < 1e-3
    ]
    for r in (SHOULDER_FILLET, 1.5, 1.0):
        try:
            body = fillet(shoulders, r)
            break
        except ValueError:
            continue

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
