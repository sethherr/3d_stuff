---
name: pr
description: >-
  Create or update a pull request for the current branch. Trigger when the user
  asks to create/open/make a PR, or to edit/update/rewrite/fix the PR
  description, body, or summary — for both new PRs (`gh pr create`) and
  existing ones (`gh pr edit --body-file`). For CAD/geometry diffs, locates the
  part's snapshot renders (`snap_<view>_*.png`) and embeds them under a
  `## Snapshots` section via the `github-upload-image-to-pr` skill. Use for any
  verb that lands on a PR's text content: "open a PR", "make a PR", "update the
  PR description", "rewrite the PR body", "fix the description".
allowed-tools: Bash, Read, Glob, Grep
---

# Pull request workflow

Create or update a pull request for the current branch. This is a build123d CAD repo (Python parts managed by mise + uv; see the root `README.md`). If the diff changes geometry, embed the part's snapshot renders in the PR body under a `## Snapshots` section using the `github-upload-image-to-pr` skill.

The workflow is ordered so the always-runs phase (steps 1–3) happens first, then the snapshot phase (steps 4–7) runs only when the diff touches geometry. Each step ends with the conditions under which you stop and return.

## Workflow

### 1. Gather branch state

Run in parallel:
- `git status` (no `-uall`)
- `git diff main...HEAD --stat`
- `git diff main...HEAD --name-only`
- `git log main..HEAD --oneline`
- `EXISTING_PR=$(gh pr view --json number,url,title 2>/dev/null)` — capture for step 3.

If the branch has no commits ahead of `main`, stop and tell the user.

### 2. Classify the diff

A change is "CAD" if any changed path is a part script or exported geometry:
- `**/*.py` (a build123d part — anything that builds geometry, e.g. `aerobar-crossbar/aerobar_crossbar.py`)
- `**/*.step`, `**/*.stp`, `**/*.stl`, `**/*.glb`, `**/*.3mf`, `**/*.dxf`

Record this as `CAD=true|false` and note the set of **affected part directories** (the dirs containing the changed part scripts / exports) for the snapshot decision in step 4. A pure tooling/docs change (`README.md`, `pyproject.toml`, `mise.toml`, `uv.lock`, `.claude/**`) is `CAD=false`.

### 3. Build the summary body and create/update the PR

Write a summary of the change (2–5 bullets based on the diff and recent commits) to a temp file. Follow the repo's existing PR body style — look at the last few merged PRs (`gh pr list --state merged --limit 5 --json body,title`) to match tone and length. If there are none yet, keep it plain and factual. Keep the title under ~70 chars.

**Bias toward brevity.** Reviewers skim. A bullet that fits on one line beats one that wraps three times — push detail down to the diff or commit log, not the body. If a per-file bullet starts feeling like an essay, compress to a single sentence naming the *kind* of change (e.g., "raised the bar to 40mm, filleted the clamp, re-exported STEP/STL/GLB") rather than enumerating each edit. Aim for under ~6 bullets total across the whole body, including any nested ones; if you're past that, regroup by category until you fit.

**Describe the end state, not the journey.** Reviewers want to know what the PR does *now* — the diff that will land — not the order in which it was built. Avoid framings like "first pass" / "second pass", commit-hash references for stages of work that all merge into the same shipped diff, "originally we tried X then switched to Y", or play-by-play of how the conversation evolved. The git log preserves that. If a discarded approach is genuinely load-bearing context for the reviewer (e.g., explains why a dimension is what it is), one line is enough; otherwise omit. The same applies when *updating* an existing PR body: rewrite to describe the current diff, don't append a changelog of edits made since the last revision.

**No "Test plan" section unless the user asks.** Don't list routine regen/validation steps — `uv run python <part>.py`, re-exporting STEP/STL/GLB, opening the CAD Viewer, etc. Only add a Test plan when there's reviewer-facing manual verification a human needs to do (e.g. "confirm the clamp clears the 31.8mm bar"), and only when the user requests it.

**No Claude Code attribution footer.** Don't append the "🤖 Generated with [Claude Code](https://claude.com/claude-code)" line (or any variant of it) to the body. The PR body should read like the human author wrote it.

Push the branch: `git push -u origin HEAD`. **Never force-push** (it's blocked by policy anyway) — if the push is rejected as non-fast-forward, stop and tell the user rather than rewriting history.

- If `$EXISTING_PR` from step 1 was non-empty: `gh pr edit <num> --body-file <tmp-body-file>` (don't overwrite the title unless the user asks).
- Otherwise: `gh pr create --base main --title "..." --body-file <tmp-body-file>`. Capture the PR number from the output.

Always pass the body via `--body-file` (not inline `--body`) to preserve formatting.

**Stop here and return the PR URL** unless step 4's gate says snapshots are needed.

### 4. Decide whether snapshots are needed

Only continue past this step when the diff changes geometry. Otherwise return the PR URL.

- New PR + `CAD=false` → done.
- New PR + `CAD=true` → continue; embed snapshots for every affected part directory.
- Existing PR + `CAD=false` → done.
- Existing PR + `CAD=true` → continue only if the snapshots in the existing `## Snapshots` section are stale: a commit since the last embed changed a part already shown, or a newly affected part appears in the diff. Limit step 5 to those parts. If nothing moved, done.

### 5. Locate the part snapshots

For each affected part directory, find the most recent snapshot set. Snapshots follow the convention `snap_<view>_<UTC-timestamp>.png` (views: `iso`, `front`, `right`, `top`), written next to the part by the CAD Viewer. Glob `<part-dir>/snap_*_*.png` and pick the newest timestamp group (the four views sharing the latest `…Z` stamp; a part may have fewer than four).

**If a changed part has no snapshots, or its newest snapshots predate the latest change to its `.py` / geometry**, they're missing or stale. Do **not** silently skip or post old renders — regenerate first via the `cad` / `cad-viewer` skills (which render the part and write fresh `snap_*` PNGs), then commit them and re-push. If you can't regenerate, tell the user which parts lack current snapshots and let them decide; don't post an out-of-date render as if it were current.

Collect the chosen PNG paths keyed by `(part-dir, view)`.

### 6. Upload snapshots and get inline URLs

Invoke the `github-upload-image-to-pr` skill to upload each PNG from step 5 to the PR's comment textarea — GitHub mints persistent `user-attachments/assets/` URLs that render inline. The skill clears the textarea without submitting a comment.

Collect the returned URLs, keyed by `(part-dir, view)`.

### 7. Post the Snapshots section in the PR body

Embed the renders under a `## Snapshots` section in the PR body (one subsection per affected part). On an update, replace the existing `### <part-dir>` block for any part you recaptured and leave the others alone; if a `## Snapshots` section already exists, edit it in place rather than appending a duplicate.

```markdown
## Snapshots

### aerobar-crossbar

| Iso | Front | Right | Top |
| --- | --- | --- | --- |
| <img src="<iso-url>" width="320"> | <img src="<front-url>" width="320"> | <img src="<right-url>" width="320"> | <img src="<top-url>" width="320"> |
```

Rules:
- Each affected part gets a `### <part-dir>` subheading followed by its own table.
- Column headers are the view names (`Iso`, `Front`, `Right`, `Top`) — include only the views that exist for that part, in that order.
- Use `<img src=... width=...>` (not `![]()`) so widths render predictably in GitHub table cells; ~320 reads well in a four-up row.

Update the body with `gh pr edit <num> --body-file <tmp-body-file>` (regenerate the full body so the section lands in place). Return the PR URL.

## Notes

- If `github-upload-image-to-pr` fails, report the failure clearly and leave the PR without snapshots — don't block PR creation on the image tooling.
- Never force-push from this skill. If history has diverged, surface it and let the user resolve it.
