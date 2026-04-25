# Migrating from v0.x to v1.0.0

`@jasemal/katib@1.0.0` is a **breaking redesign** of the v0.x line. This
guide covers what changed, how to upgrade, and what to do if you have
custom v0.x content you want to preserve.

> **TL;DR.** v0.x had per-doc-type monolithic templates. v1.0.0 has
> reusable components composed into YAML recipes, plus a user-tier at
> `~/.katib/` that survives reinstall, plus a `.katib-pack` share format
> for cross-machine portability. Same `npx @jasemal/katib install`
> install path; everything else is new.

---

## Should I migrate?

| You are | Action |
|---|---|
| A v0.x user with no customisations | Just upgrade. `npx @jasemal/katib@1` install replaces v0 cleanly. |
| A v0.x user with edited templates under the skill folder | Read [Custom v0.x content](#custom-v0x-content) below. |
| A v0.x user with shipped brand profiles you copied locally | Read [Brand profile changes](#brand-profile-changes). |
| Brand-new user | Skip this guide; read [README.md](README.md) and [TUTORIAL.md](TUTORIAL.md). |

**Pre-distribution status:** v1.0.0 is the first stable v2 release.
v0.20.0 was on `@latest` for ~3 days before v1.0.0 ships. If you got
lucky and tried v0.x in that window, this guide is for you.

---

## What changed at the architecture level

### Components, not templates

**v0.x:** Each doc-type was a single `.html` template per language under
`domains/<area>/<doc>.{en,ar}.html`. Customisation meant editing the
monolith.

**v1.0.0:** Every visible element is a reusable component (primitive,
section, or cover). Doc-types are YAML recipes that reference components
by name. Recipes never embed HTML — they only declare structure.

```yaml
# v1.0.0 recipe
name: my-proposal
languages: [en]
sections:
  - component: letterhead
    inputs: { company: "Acme", date: "2026-04-25" }
  - component: module
    inputs: { title: "Scope", body: "..." }
  - component: signature-block
```

### User tier under `~/.katib/`

**v0.x:** Custom content lived inside the installed skill folder
(`~/.claude/skills/katib/`), which `npx install` would overwrite.

**v1.0.0:** Custom recipes, components, and brand profiles live under
`~/.katib/` and **survive every reinstall**. The skill folder ships
templates; your customisations stack on top via shadow semantics
(user-tier wins on collision).

```
~/.katib/recipes/<your-recipe>.yaml
~/.katib/components/{primitives,sections,covers}/<your-component>/
~/.katib/brands/<your-brand>.yaml + <your-brand>-assets/
~/.katib/memory/                                   # audit + log streams
```

### Output to `~/Documents/katib/`

**v0.x:** Could write to a vault or a custom path.
**v1.0.0:** Always writes to `~/Documents/katib/` (or `$KATIB_OUTPUT_ROOT`).
File navigation belongs at a different layer (Finder, Soul Hub, etc.) —
v1 deliberately doesn't own this concern.

### `.katib-pack` share format

New in v1.0.0. Custom recipes / components / brand profiles can be
packaged into a `.katib-pack` tarball and imported into another install.
See [PACK-FORMAT.md](PACK-FORMAT.md). The same artifact format will be
served from a curated marketplace at `katib.jneaimi.com` post-v1.0.0
(Phase 6).

---

## How to upgrade

### Step 1 — uninstall v0.x

```bash
# Optional: back up v0.x customisations
cp -r ~/.claude/skills/katib ~/katib-v0-backup

# Remove v0.x
npx @jasemal/katib@0 uninstall
# (or just rm -rf ~/.claude/skills/katib)
```

### Step 2 — install v1.0.0

```bash
npx @jasemal/katib install
```

This will:

- Install the v1.0.0 skill into `~/.claude/skills/katib/`
- Create `~/.katib/{recipes,components,brands,memory}/`
- Seed 21 starter recipes into `~/.katib/recipes/` on first run
  (only when the directory is empty — opt-in via `scripts/seed.py`
  for refresh)

### Step 3 — render a test document

```bash
# Smoke-test using a starter recipe
uv run scripts/build.py tutorial --lang en
```

PDF lands at `~/Documents/katib/tutorial/<slug>/tutorial.en.pdf`.

---

## Custom v0.x content

If you edited templates, brands, or scripts inside the v0.x skill folder,
they don't migrate automatically — v1.0.0's architecture has no place for
a monolithic `domains/<area>/<doc>.en.html` to land. You have three
options:

### Option A — manual port to v1.0.0 components (recommended for active customisation)

Identify the v0.x doc-type you customised; map it to the closest
v1.0.0 starter recipe; copy your custom content into the recipe's
`inputs` blocks. The starter library covers business / editorial /
financial / formal / legal / personal / report / tutorial domains.

If you need a custom layout that no starter expresses, build it as
a v1.0.0 recipe with the AI-assisted builder:

```bash
# In Claude Code:
/katib component new <name>
```

See [TUTORIAL.md](TUTORIAL.md) for a 20-minute walkthrough.

### Option B — keep v0.x running on a separate install

Pin a project to v0.20.0:

```bash
# In a project dir
npx @jasemal/katib@0.20.0 install --target ./katib-v0
```

v0 reads from its own folder, v1 reads from `~/.claude/skills/katib/`.
They don't conflict.

### Option C — preserve as a reference

Move your v0.x backup to `~/katib-v0-backup` and treat it as
documentation. Re-implement only the doc-types you actively use.
Most v0.x doc-types are covered by the v1 starters; only bespoke
customisation needs porting.

---

## Brand profile changes

### Schema additions

v1.0.0 brand profiles add (all optional):

- `covers:` — map of named cover presets (image source + path) bound
  to the brand. Lets you save a generated cover and reuse it in any
  recipe via `source: brand-preset`.
- `<brand>-assets/` sibling directory — for storing per-brand images
  outside the YAML.

The v0.x fields (`name`, `name_ar`, `legal_name`, `identity.*`,
`colors.*`, `logo`) all carry over unchanged.

### Where they live

**v0.x:** `~/.katib/brands/` (already user-tier in v0.20.0).
**v1.0.0:** Same path. Direct copy works.

```bash
# Move brand profiles forward
cp -r ~/katib-v0-backup/.katib/brands/* ~/.katib/brands/
```

### Validation

Run `katib validate-brand <name>` (new in v1.0.0) to catch any
schema drift:

```bash
uv run scripts/build.py tutorial --lang en --brand <your-brand>
# Brand validation runs as part of build; misconfigs fail loud.
```

---

## CLI changes

### Renamed / removed

| v0.x | v1.0.0 | Note |
|---|---|---|
| `katib build` | `uv run scripts/build.py` | Direct invocation; the `katib` binary will rewire to this in a future patch release. |
| `katib generate-cover` | (removed) | Use `--save-cover-preset` on a build to capture a cover into the brand's preset map. |
| `katib reflect` | (removed) | Reflect/feedback loops are folded into the audit stream + `request_log` in v1. |

### New

| Command | Purpose |
|---|---|
| `uv run scripts/component.py new <name>` | Scaffold a new component |
| `uv run scripts/component.py validate <name>` | Validate a component |
| `uv run scripts/recipe.py new <name>` | Scaffold a new recipe |
| `uv run scripts/recipe.py validate <name>` | Validate a recipe |
| `uv run scripts/pack.py export --component <name>` | Export to `.katib-pack` |
| `uv run scripts/pack.py export --recipe <name>` | Export a recipe pack |
| `uv run scripts/pack.py export --bundle <recipe>` | Export a recipe + its custom deps |
| `uv run scripts/pack.py inspect <pack>` | Read manifest of a pack |
| `uv run scripts/pack.py verify <pack>` | CI-grade pack validation |
| `uv run scripts/pack.py import <pack>` | Install a pack into `~/.katib/` |
| `uv run scripts/seed.py refresh <name>` | Pull in a starter recipe |

### Deprecated (still works)

| Command | Replacement |
|---|---|
| `uv run scripts/component.py share <name>` | `uv run scripts/pack.py export --component <name>` |

The legacy `share` command emits a stderr deprecation note pointing at
`pack export`. It will be removed in a future v1.x release.

---

## What's gone

| v0.x feature | Status in v1.0.0 |
|---|---|
| Vault integration (zone-governance, manifest emission, fallback reconciliation) | **Removed.** v1 writes to `~/Documents/katib/`. File-navigation belongs at the Soul Hub layer. |
| `add_domain.py` graduation path | Replaced by component+recipe authoring CLIs with audit gate. |
| `install_fonts.py` | Removed. Fonts ship as system-install instructions in README. |
| `report/<doc>` templates with hardcoded sample content | Replaced by `report-progress` starter recipe + composable sections. |
| `marketing-print/<doc>` templates | Deferred. Build via composable sections if needed. |
| `academic/<doc>` templates | Deferred. Use `editorial-white-paper` as a baseline; build a custom recipe for academic shapes. |

---

## Frequently asked questions

### Q: Can I keep using v0.x?

Yes. `npx @jasemal/katib@0.20.0 install` always pulls v0.x. v0
remains on the `0` dist-tag indefinitely. We won't auto-update you to
v1 unless you ask for `@latest`.

### Q: Will my custom recipes / components / brands break on v1.x patch releases?

No. The pack format is frozen at `pack_format: 1` for the entire v1.x
line. Your `~/.katib/` content is owned by you and never overwritten
by `npx install`. Patch / minor releases of v1 only modify the bundled
tier under `~/.claude/skills/katib/`.

### Q: When does the marketplace launch?

Phase 6 (post-v1.0.0). The same `.katib-pack` artifact you create
locally will be importable from `katib.jneaimi.com` once the
marketplace MVP ships. The pack format is the contract; only the
distribution mechanism changes.

### Q: Where do I report a v0 → v1 issue?

[github.com/jneaimi/katib/issues](https://github.com/jneaimi/katib/issues).
Tag the issue `migration-v1` so it's easy to triage.

---

## See also

- [README.md](README.md) — install + usage overview for v1
- [TUTORIAL.md](TUTORIAL.md) — 20-minute walkthrough building your first custom component
- [COMPONENT-BUILDER.md](COMPONENT-BUILDER.md) — AI-assisted component-builder playbook
- [PACK-FORMAT.md](PACK-FORMAT.md) — `.katib-pack` spec
- [CHANGELOG.md](CHANGELOG.md) — full history from v0.1.0 through v1.0.0
