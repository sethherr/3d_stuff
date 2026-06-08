# Aerobar accessory crossbar

A parametric build123d part that nests in the gap between two aerobar extensions
and carries a GoPro-mounted light underneath.

It clips between the two Ø22.2 mm aerobars with a semicircular saddle cup on each
side (secured with one zip tie per side, grooved into the cup top/bottom) and has
a GoPro 2-prong tab underneath to aim a light. The mid-span is a single **bare
horizontal plate** — a 6 mm-thick deck whose top face is flush with the top of
the cradle cups (z = 13.8 mm). The GoPro tab's two prongs root directly into the
underside of the plate at center. Over each cup an open tie channel is cut
through the deck and cup top, concentric with the bar and down to its surface, so
a zip tie wraps the rounded back of the cup with no material capping it above.
Its inboard exit wall through the deck is angled (not vertical), mirroring the
bar's curve so the tie passes through the opening cleanly.

6 mm of wall is plenty for PLA/PETG at this span and prints fast.

## Build

```sh
python aerobar-crossbar/aerobar_crossbar.py
```

The script self-exports `.step`, `.stl`, and `.glb` alongside it. Everything is
fused with real booleans into **one watertight, printable solid**, so the exports
are small (a few hundred KB) and committed.

## Status

Printable. Every feature — the two cradle cups, the plate (with its two zip-tie
tunnels), and the GoPro tab — is one fused manifold solid (`solids: 1`).
