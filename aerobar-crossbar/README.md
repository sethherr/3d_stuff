# Aerobar accessory crossbar

A parametric build123d part that nests in the gap between two aerobar extensions
and carries a GoPro-mounted light underneath.

It clips between the two Ø22.2 mm aerobars with a semicircular saddle on each
side, secures with one zip tie per side, and has a GoPro 2-prong tab underneath
to aim a light. The bar is a faceted (hex) section lightened with diamond
cutouts through the mid-span.

## Build

```sh
python aerobar-crossbar/aerobar_crossbar.py
```

Running the script self-exports `.step`, `.stl`, and `.glb` alongside it — no
skill launcher needed.

## Lattice explorations

Alternative versions that replace the solid mid-span with an open strut lattice
running the full length and wrapping around each saddle (only a thin cradle cup
stays solid; the tie channel is cut into the cup's top and bottom edges). Each is
its own self-exporting script; the three `lattice_*` ones share `lattice_kit.py`
and differ only by their unit cell. Their meshes are 100+ MB, so the `.stl` /
`.glb` / `.step` exports are git-ignored — regenerate by running the script.

| Variant | Lattice | What it's good for |
| --- | --- | --- |
| `aerobar_crossbar_foam.py` | Kelvin foam (truncated octahedron) | Near-isotropic — similar stiffness in every direction, no weak axis — and spreads stress smoothly, so it's a strong all-rounder per gram. The most organic look (matches the reference photo). |
| `lattice_bcc.py` | Body-centered cubic (body-diagonal struts) | The most open and lightest. Bending-dominated, so it's springy and soaks up shock and vibration well; the diagonal struts also self-support cleanly when printed. |
| `lattice_octet.py` | Octet truss (FCC nearest-neighbors) | Stretch-dominated, so it's the stiffest and strongest for its weight — the pick when rigidity matters most. The trade-off is more material and longer print time. |
| `lattice_diamond.py` | Diamond cubic (4-connected tetrahedral) | Near-isotropic and smooth like the foam but with only four struts per node, so it prints cleanly and stays springy — a good balance of stiffness and give. |

```sh
python aerobar-crossbar/lattice_bcc.py        # or _octet / _diamond / aerobar_crossbar_foam
```

These are visual studies (overlapping struts assembled as a compound, not yet a
watertight/printable solid).
