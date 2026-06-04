"""Aerobar accessory crossbar.

Spans two round aerobar extensions and carries a bike computer + light between
them, like a tri/TT cockpit crossbar.

- Bars: 22.2 mm OD, 120 mm center-to-center.
- Each end is a half-circle (semicircular) saddle that cradles the bar from
  below and is secured with zip ties that pass through vertical slots and wrap
  over the top of the bar (two tie positions per saddle for anti-rotation).
- Top center: Garmin/Wahoo-compatible quarter-turn mount, raised above bar
  height so the computer clears the bars.
- Bottom center: GoPro 2-prong tab mount (3 mm fingers, 5 mm pin hole) for a
  light; hole axis is left-right so the light tilts up/down to aim.

Conventions: millimeters. X = crossbar span. Y = bar axis (fore/aft). Z = up.
Bar centers sit at (+/-60, 0, 0) with the bar centerline at z = 0.
"""

from build123d import Box, Cylinder, Pos, Rot

# ---- Bars / saddles ---------------------------------------------------------
BAR_D = 22.2
BAR_R = BAR_D / 2
CLEAR = 0.3
GROOVE_R = BAR_R + CLEAR              # 11.4 mm half-circle cradle

SPAN_CC = 120.0
BAR_X = SPAN_CC / 2                   # 60

SAD_W = 37.0                          # saddle width (X)
SAD_L = 28.0                          # saddle length along bar (Y)
SAD_TOP_Z = 0.0
SAD_BOT_Z = -17.0
SAD_H = SAD_TOP_Z - SAD_BOT_Z         # 17
SAD_MID_Z = (SAD_TOP_Z + SAD_BOT_Z) / 2

# Zip-tie vertical slots (over-the-bar wrap)
TIE_SLOT_X = 2.8
TIE_SLOT_Y = 5.0
TIE_SLOT_OFFX = 14.8                  # +/- from bar center, outside the groove
TIE_SLOT_OFFY = 8.0                   # +/- two tie lanes along the bar

# ---- Beam connecting the saddles -------------------------------------------
BEAM_W = 20.0                         # Y
BEAM_TOP_Z = -3.0
BEAM_BOT_Z = SAD_BOT_Z
BEAM_X_HALF = BAR_X + SAD_W / 2       # 78.5

# ---- Center riser -----------------------------------------------------------
RISER_W = 24.0                        # X
RISER_D = 24.0                        # Y
RISER_TOP_Z = 10.0

# ---- Garmin/Wahoo quarter-turn mount (male) --------------------------------
QT_DISC_R = 11.4                      # tab disc radius (Ø22.8)
QT_FLAT_W = 15.5                      # stem across-flats (Y) = computer slot
QT_GAP_H = 3.0                        # seat for computer shelf
QT_TAB_H = 2.6                        # locking tab thickness
QT_FLANGE_R = 12.5
QT_FLANGE_H = 2.0
QT_Z0 = 12.0                          # flange top / stem base (above bar top)
QT_STEM_H = QT_GAP_H + QT_TAB_H

# ---- GoPro 2-prong tab mount (male) ----------------------------------------
GP_FINGER_T = 3.0                     # finger thickness (X)
GP_GAP = 3.0                          # slot between fingers
GP_OFFX = (GP_FINGER_T + GP_GAP) / 2  # +/- 3.0
GP_WIDTH_Y = 15.0
GP_ROUND_R = GP_WIDTH_Y / 2           # 7.5
GP_HOLE_D = 5.0
GP_TOP_Z = -14.0                      # rooted up into the beam
GP_ROUND_Z = -29.0                    # rounded tip center / pin-hole center


def _saddle(sign):
    cx = sign * BAR_X
    block = Pos(cx, 0, SAD_MID_Z) * Box(SAD_W, SAD_L, SAD_H)
    groove = Pos(cx, 0, 0) * (Rot(90, 0, 0) * Cylinder(GROOVE_R, SAD_L + 10))
    s = block - groove
    for sx in (-TIE_SLOT_OFFX, TIE_SLOT_OFFX):
        for sy in (-TIE_SLOT_OFFY, TIE_SLOT_OFFY):
            slot = Pos(cx + sx, sy, SAD_MID_Z) * Box(
                TIE_SLOT_X, TIE_SLOT_Y, SAD_H + 6
            )
            s = s - slot
    return s


def _beam():
    h = BEAM_TOP_Z - BEAM_BOT_Z
    return Pos(0, 0, (BEAM_TOP_Z + BEAM_BOT_Z) / 2) * Box(2 * BEAM_X_HALF, BEAM_W, h)


def _riser():
    h = RISER_TOP_Z - BEAM_TOP_Z
    return Pos(0, 0, (RISER_TOP_Z + BEAM_TOP_Z) / 2) * Box(RISER_W, RISER_D, h)


def _garmin_mount():
    flange = Pos(0, 0, QT_Z0 - QT_FLANGE_H / 2) * Cylinder(QT_FLANGE_R, QT_FLANGE_H)
    stem_disc = Pos(0, 0, QT_Z0 + QT_STEM_H / 2) * Cylinder(QT_DISC_R, QT_STEM_H)
    clip = Pos(0, 0, QT_Z0 + QT_STEM_H / 2) * Box(2 * QT_DISC_R + 4, QT_FLAT_W, QT_STEM_H)
    stem = stem_disc & clip
    tabs = Pos(0, 0, QT_Z0 + QT_GAP_H + QT_TAB_H / 2) * Cylinder(QT_DISC_R, QT_TAB_H)
    return flange + stem + tabs


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
    part = (
        _saddle(+1)
        + _saddle(-1)
        + _beam()
        + _riser()
        + _garmin_mount()
        + _gopro_mount()
    )
    part.label = "aerobar_crossbar"
    return part


if __name__ == "__main__":
    p = gen_step()
    bb = p.bounding_box()
    print("bbox min:", bb.min)
    print("bbox max:", bb.max)
    print("volume mm^3:", round(p.volume, 1))
