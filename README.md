# Seth 3d stuff

build123d CAD parts (with Playwright for snapshots), managed by [mise](https://mise.jdx.dev/) + [uv](https://docs.astral.sh/uv/).

## Setup

```bash
mise install        # installs Python 3.12.13 + uv (pinned in mise.toml)
mise run setup      # uv sync (deps) + Playwright Chromium for snapshots
```

`mise` auto-activates the uv-managed `.venv` when you `cd` into the project, so
`python` and `uv run` resolve to it. The first `cd` in creates `.venv`; the two
commands above install the toolchain and the dependencies. That's the whole
setup — no manual `uv venv` / `source .venv/bin/activate` dance.

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
uv run python <part>/<part>.py
# or, since mise auto-activates the venv:
python <part>/<part>.py
```

## `bin/cad`

Thin wrapper around the `cad` skill's launchers so the versioned plugin path
isn't hard-coded. Resolves `~/.claude/plugins/cache/text-to-cad/.../skills/cad/scripts/<tool>`
and runs it:

```bash
bin/cad snapshot --input <part>/<part>.step --output out.png --camera iso
bin/cad inspect refs --facts <part>/<part>.step
bin/cad step <part>/<part>.py     # (generators self-export, so rarely needed)
```

## CAD Viewer

The CAD skills (`cad:*`) and `bin/cad` come from the [`cad@text-to-cad`](https://github.com/earthtojake/text-to-cad) Claude Code plugin, declared in `.claude/settings.json` so it installs on clone (Claude Code prompts to trust the marketplace on first use).

To view a part, use the `cad:cad-viewer` skill (in Claude Code:
`/cad:cad-viewer <part>/<part>.step`) — it starts/reuses the local viewer server
and hands back a ready-to-open link.

## 3D printing (Bambu Lab)

Parts export a print-ready `.stl` (the `.glb` is viewer-only). Slice it to
`.gcode` with the `cad:gcode` skill (drives OrcaSlicer; `brew install --cask
orcaslicer` on macOS), then print over LAN with the `cad:bambu-labs` skill.

Store each printer's IP, access code, and model in a `bambu-printers.json` at
the repo root — **git-ignored** because it holds the LAN access code:

```json
{
  "printers": {
    "a1-mini": { "host": "192.168.1.34", "access_code": "12345678", "model": "a1-mini" }
  }
}
```

The printer must be in **LAN Only + Developer Mode** (set on its touchscreen).
`cad:bambu-labs` defaults to dry-run — see the skill for the flags that enable
real printer traffic and start a print.
