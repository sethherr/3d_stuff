# Seth 3d stuff

build123d CAD parts (with Playwright for snapshots), managed by [mise](https://mise.jdx.dev/) + [uv](https://docs.astral.sh/uv/).

## Setup

```bash
mise install        # installs Python 3.12.13 + uv (pinned in mise.toml)
mise run setup      # uv sync (deps) + Playwright Chromium for snapshots
```

`mise` auto-activates the uv-managed `.venv` when you `cd` into the project, so
`python` and `uv run` resolve to it.

## Toolchain notes

- **Deps live in `pyproject.toml`**; `uv.lock` pins exact versions (commit it).
  Use `uv add <pkg>` / `uv remove <pkg>` to change them, then commit the updated
  lockfile.
- **Python is pinned to 3.12.13** — 3.14 has no build123d/OCP wheels yet.
- **`.venv/` is disposable and git-ignored.** It's rebuilt anytime from
  `pyproject.toml` + `uv.lock` via `uv sync` (or `mise run setup`). Safe to
  `rm -rf .venv` whenever.

## Running a part

Each generator prints its bounding box / volume and writes its CAD artifacts
(`.step`, `.stl`, `.glb`) next to itself:

```bash
uv run python aerobar-crossbar/aerobar_crossbar.py
# or, since mise auto-activates the venv:
python aerobar-crossbar/aerobar_crossbar.py
```

## CAD Viewer

Use the `cad:cad-viewer` skill (in Claude Code: `/cad:cad-viewer aerobar-crossbar/aerobar_crossbar.step`) — it starts/reuses the local viewer server and hands back a ready-to-open link.

To start the server directly instead, run its `backend/server.mjs` from the
installed skill (the path is versioned, so locate it dynamically):

```bash
VIEWER=$(dirname "$(find ~/.claude/plugins/cache/text-to-cad -path '*/cad-viewer/scripts/viewer/backend/server.mjs' | sort | tail -1)")
node "$VIEWER/server.mjs" --host 127.0.0.1 --shutdown-after 12h
```

It prints a base URL (e.g. `http://127.0.0.1:4178/`). Open a model by appending
an absolute `?dir=` (the model folder) and a `?file=` relative to it:

```
http://127.0.0.1:4178/?dir=/Users/seth/Sites/3d/aerobar-crossbar&file=aerobar_crossbar.step
```

Swap `file=` for `.aerobar_crossbar.step.glb` or `aerobar_crossbar.stl` to load
the lighter tessellated mesh. The server self-stops after 12h
(`--shutdown-after`).
