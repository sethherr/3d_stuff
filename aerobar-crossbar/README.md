# Aerobar accessory crossbar

A parametric build123d part that nests in the gap between two aerobar extensions
and carries a GoPro-mounted light underneath.

It clips between the two Ø22.2 mm aerobars with a semicircular saddle cup on each
side (secured with one zip tie per side, grooved into the cup top/bottom) and has
a GoPro 3-prong clevis (the female side) underneath to aim a light. The mid-span
is a single horizontal deck whose top face is flush with the top of the cradle
cups (z = 13.8 mm). The deck is a **fore-aft wedge**: the top stays flat, but the
underside is angled — the front edge holds at the deck bottom (z = 7.8 mm) while
the back edge drops to the cradle midpoint (z = 0, `PLATE_BACK_Z`), so the deck
thickens toward the back. At center it widens to a Ø34 mm disc (`HUB_D`) with a
3 mm-deep recess cut into the disc top (`HUB_RECESS`).

The clevis's three prongs root directly into the underside of the deck, centered
midway between the disc and the left cup and shifted back so its rear is flush
with the deck back. The cradle-side prong is tapped M5 (×0.8) and carries a
truncated cone on its outboard face (as on a real GoPro clevis) for extra thread
engagement; the other two prongs are Ø5.4 mm clearance holes for the screw.

Over each cup an open tie channel is cut concentric with the bar and down to its
surface, so a zip tie wraps the rounded back of the cup with no material capping
it above. The slot runs the whole way through the wedge deck — bounded at the
angled underside and stopped at the cup wall so it removes only deck material
without carving into the cradle. Its inboard exit wall through the deck is angled
(not vertical), mirroring the bar's curve so the tie passes through the opening
cleanly.

The wedge is plenty of wall for PLA/PETG at this span and prints fast.

## Build

```sh
python aerobar-crossbar/aerobar_crossbar.py
```

The script self-exports `.step`, `.stl`, and `.glb` alongside it. Everything is
fused with real booleans into **one watertight, printable solid**, so the exports
are small (a few hundred KB) and committed.

## Status

Printable. Every feature — the two cradle cups, the wedge deck (with its central
disc and the two zip-tie channels), and the GoPro clevis — is one fused manifold
solid (`solids: 1`).
