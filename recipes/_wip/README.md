# `_wip/` — work-in-progress recipes

Recipes here are **excluded** from:
- `capabilities.yaml` generation (`generate_capabilities.py` globs top-level only)
- build-time audit check (`scripts/build.py:_on_disk_recipes`)
- route.py staleness detection (`scripts/route.py:_ensure_capabilities_fresh`)

The `_` prefix is the contract — any directory starting with `_` is skipped
by the engine's recipe scanners.

**When to use:**
- A recipe whose content is known-stale and needs rewriting before it ships
- Prototype shapes being iterated on without polluting the registered set
- Recipes deferred to a future phase

**What does NOT belong here:**
- Recipes being actively debugged but ready to ship after a fix — those go
  back to `recipes/` the moment they're fixed. `_wip/` is for larger
  blockers, not intermittent test failures.

When a `_wip/` recipe is ready, move it to `recipes/` and re-register it
via `uv run scripts/recipe.py new` or by adding an audit entry in
`memory/recipe-audit.jsonl`.
