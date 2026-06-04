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

```bash
uv run python aerobar-crossbar/aerobar_crossbar.py
# or, since mise auto-activates the venv:
python aerobar-crossbar/aerobar_crossbar.py
```
