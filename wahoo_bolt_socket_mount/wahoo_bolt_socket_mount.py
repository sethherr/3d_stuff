"""Wahoo ELEMNT BOLT quarter-turn socket mount (female).

The Wahoo system is inverted from Garmin: the *computer* carries the male
quarter-turn tabs, and the *mount* is the female socket the tabs drop into and
twist-lock. This is that female socket (like the round puck in the reference
photo / the PostMelvin "Socket"), as a standalone puck meant to be grafted
(boolean union) onto your own prints.

How it works: the Bolt's two ears drop straight down through the insertion
slots (the open channels), then a 90 deg twist sweeps them under the two
retaining ledges that overhang the rotation relief at the bottom of the cavity.

Engagement is the standard Wahoo/Garmin quarter-turn (Oe24.9 hub, Oe28.6 ears
over an 11 mm band) — cross-checked against the supplied PostMelvin socket STL
and the chadkirby/quarter-turn-mount source — with print clearances added so
the mating tab actually fits.

Coordinate system:
    Origin: center of the puck, on the underside.
    XY: base/print-bed plane.
    +Z: up; the socket opens upward and the Bolt inserts from the top.
"""

from build123d import (
    Align,
    Axis,
    BuildPart,
    BuildSketch,
    Circle,
    Cylinder,
    GeomType,
    Locations,
    Mode,
    Plane,
    Rectangle,
    chamfer,
    extrude,
)

# --- Mating tab (the Bolt's male quarter-turn; standard Wahoo/Garmin) ---------
TAB_HUB_DIA = 24.9     # central hub the ears protrude from
TAB_EAR_DIA = 28.6     # ear outer diameter
TAB_BAND = 11.0        # width of the band the two ears occupy
TAB_EAR_THICK = 1.5    # ear (lip) thickness

# --- Print clearances (tune these if the fit is tight/loose) -----------------
RADIAL_CL = 0.35       # added to each radius of the bore / slot
BAND_CL = 0.4          # added to each side of the insertion-slot band
TWIST_CL = 0.4         # vertical clearance under the ledge for the ear to rotate

# --- Socket body (shroud puck; tune freely for your print) -------------------
PUCK_DIA = 38.0        # outer diameter (matches the original PostMelvin socket)
SOCKET_DEPTH = 4.6     # cavity depth (how far the Bolt tab sinks in)
FLOOR = 2.0            # solid floor under the cavity
TOP_CHAMFER = 0.5      # lead-in chamfer around the socket opening

# --- Derived ------------------------------------------------------------------
BORE_DIA = TAB_HUB_DIA + 2 * RADIAL_CL      # hub clearance bore
SLOT_DIA = TAB_EAR_DIA + 2 * RADIAL_CL      # ear insertion / rotation diameter
SLOT_BAND = TAB_BAND + 2 * BAND_CL          # insertion-slot band width
RELIEF_H = TAB_EAR_THICK + TWIST_CL         # height of the rotation relief
H = FLOOR + SOCKET_DEPTH                     # overall puck height
BASE = (Align.CENTER, Align.CENTER, Align.MIN)


def gen_step():
    with BuildPart() as mount:
        # Solid puck
        Cylinder(radius=PUCK_DIA / 2, height=H, align=BASE)

        # (A) Central bore: hub clearance, full cavity depth. Leaves the
        #     retaining ledges as the wall material at r > BORE_DIA/2.
        with Locations((0, 0, FLOOR)):
            Cylinder(radius=BORE_DIA / 2, height=SOCKET_DEPTH + 0.1,
                     align=BASE, mode=Mode.SUBTRACT)

        # (B) Insertion slots: the ear channel (Oe SLOT_DIA trimmed to an
        #     11 mm band), open the full cavity depth so the ears drop straight in.
        with BuildSketch(Plane.XY.offset(FLOOR)):
            Circle(SLOT_DIA / 2)
            Rectangle(SLOT_DIA, SLOT_BAND, mode=Mode.INTERSECT)
        extrude(amount=SOCKET_DEPTH + 0.1, mode=Mode.SUBTRACT)

        # (C) Rotation relief: a full Oe SLOT_DIA disc at the bottom of the
        #     cavity so the ears can sweep 90 deg under the ledges. The material
        #     above it (in the non-slot quadrants) is the retaining overhang.
        with Locations((0, 0, FLOOR)):
            Cylinder(radius=SLOT_DIA / 2, height=RELIEF_H,
                     align=BASE, mode=Mode.SUBTRACT)

        # Lead-in chamfer around the top opening for easy insertion.
        if TOP_CHAMFER > 0:
            top_inner = (
                mount.edges()
                .filter_by(GeomType.CIRCLE)
                .group_by(Axis.Z)[-1]
                .filter_by(lambda e: e.radius < PUCK_DIA / 2 - 0.1)
            )
            if top_inner:
                try:
                    chamfer(top_inner, length=TOP_CHAMFER)
                except Exception:
                    pass

    solid = mount.part
    solid.label = "wahoo_bolt_socket_mount"
    return solid


if __name__ == "__main__":
    part = gen_step()
    bb = part.bounding_box()
    print(f"label: {part.label}")
    print(f"bbox size (mm): {bb.size.X:.2f} x {bb.size.Y:.2f} x {bb.size.Z:.2f}")
    print(f"volume (mm^3): {part.volume:.1f}")
    print(f"bore Oe{BORE_DIA:.1f}  slot Oe{SLOT_DIA:.1f}  band {SLOT_BAND:.1f}  "
          f"relief {RELIEF_H:.1f}  depth {SOCKET_DEPTH}")
