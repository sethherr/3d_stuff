# Aerobar accessory crossbar

A parametric build123d part that nests in the gap between two aerobar extensions
and carries a GoPro-mounted light underneath.

It clips between the two Ø22.2 mm aerobars with a semicircular saddle cup on each
side (secured with one zip tie per side) and has a GoPro 2-prong tab underneath
to aim a light. The mid-span is an open **diamond-cubic strut lattice**, and a
faceted **aero prow** — an oblique pyramid with a flat top, level with the bar —
sits on the front.

The diamond lattice (two interpenetrating FCC lattices, every node joined to four
tetrahedral neighbours) is near-isotropic and springy with a clean, organic look,
and prints relatively cleanly (only four struts meet at each node).

## Build

```sh
python aerobar-crossbar/aerobar_crossbar.py
```

The script self-exports `.step`, `.stl`, and `.glb` alongside it — no skill
launcher needed. The lattice is thousands of separate solids, so the meshes are
100+ MB; the `.stl` / `.glb` / `.step` exports are git-ignored — regenerate them
by running the script.

`aerobar_crossbar.py` just defines the lattice unit cell and calls into
`lattice_kit.py`, the shared builder that tiles the cell, carves the saddle cups
and tie channels, hangs the GoPro tab, and adds the front prow.

## Status

This is a visual study — the struts are overlapping solids in a Compound, not yet
fused into a watertight, printable solid. The remaining step before printing is a
fuse/fillet pass to make it manifold.
