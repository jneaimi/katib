# Katib — Bilingual PDF Document Generation

[![CI](https://github.com/jneaimi/katib/actions/workflows/ci.yml/badge.svg)](https://github.com/jneaimi/katib/actions/workflows/ci.yml)
[![npm](https://img.shields.io/npm/v/%40jasemal%2Fkatib?color=1B2A4A&label=npm&style=flat-square)](https://www.npmjs.com/package/@jasemal/katib)
[![license](https://img.shields.io/badge/license-MIT-1B2A4A?style=flat-square)](LICENSE)
![status](https://img.shields.io/badge/v2-alpha-orange?style=flat-square)

**كاتب** (*kātib*, "the writer") — the one who shapes words onto paper.

One skill, bilingual (EN + AR) print-grade PDF generation for Claude Code.
HTML + CSS → WeasyPrint → PDF.

## Install

```bash
# v1 stable — safe default, no v2 architecture changes
npx @jasemal/katib install

# v2 alpha — new component architecture, custom recipes under ~/.katib/
npx @jasemal/katib@alpha install
```

> **⚠️ v2 is in alpha.** Phase 3 (layout + content primitives, AI-assisted
> component builder, recipe migration) is shipped and tested. APIs and
> recipe shapes can still change before `1.0.0`. `@latest` on npm stays
> pointed at v1 (`0.20.0`); v2 ships under the `alpha` dist-tag.

---

## Where things stand

| | |
|---|---|
| **Stable (v1):** | `@jasemal/katib@0.20.0` on npm — `npx @jasemal/katib install` (the `@latest` tag) |
| **In development (v2):** | `1.0.0-alpha.3` on npm under the `alpha` tag — `npx @jasemal/katib@alpha install` |
| **Archived:** | Full v1 code under `v1-reference/` (read-only) |
| **Architecture notes:** | See [CHANGELOG.md](CHANGELOG.md) for phase-by-phase design decisions |
| **Component library** | 45 components · 16 primitives, 28 sections, 1 cover |
| **Starter recipes** | 21 bilingual (EN + AR) across business, editorial, financial, formal, legal, personal, report, and tutorial domains |
| **Extending** | Build new components with `/katib component new` — see [COMPONENT-BUILDER.md](COMPONENT-BUILDER.md) or the [tutorial](TUTORIAL.md) |

## Why v2 exists

An incident on 2026-04-23 surfaced an architectural limit in v1: per-doc-type
monolithic HTML templates with hardcoded sample content couldn't grow without
either corrupting the skill or adding doc-type entropy. v2 addresses this by
separating templates from content entirely — components become the atomic
unit of reuse, and doc-types become YAML recipes.

v2 key changes from v1:

1. **Component-first composition.** Every visible element is a reusable
   component (primitives, sections, covers). Doc-types are YAML recipes
   that reference components by name.
2. **OS-standard output routing.** v2 writes to the OS user-documents
   directory (`~/Documents/katib/` or `$KATIB_OUTPUT_ROOT`) on every
   install. File navigation belongs at a different layer.
3. **Trilingual contract.** EN / AR / **bilingual** — the third state
   supports side-by-side UAE contracts in a single PDF.
4. **Self-contained.** No dependency on sibling Claude Code skills. The
   decision gate, content lint, context sensor all ship inside Katib.
5. **Four image sources.** Components declare image slots; recipes pick from
   `user-file`, `screenshot`, `gemini`, or `inline-svg` per invocation.
6. **Enforced graduation.** Adding new components and recipes goes through
   a CLI-driven workflow with build-time audit checks. Hand-editing the
   registry fails the skill load.
7. **User content survives reinstall.** Your custom recipes, components,
   and brand cover presets live under `~/.katib/`, not in the skill dir.
   `npx install` never overwrites them.

## Starter recipes on fresh install

Fresh installs seed a curated set of starter recipes into
`~/.katib/recipes/` — they're yours from that moment on. Edit them freely;
future `npx install` runs will never overwrite your edits.

- **Fresh install** (`~/.katib/recipes/` is empty) → **21 starter recipes**
  are copied in, covering business, editorial, financial, formal, legal,
  personal, report, and tutorial domains. You can edit, delete, or fork
  them at will.
- **Returning install** (any recipe already in `~/.katib/recipes/`) → the
  seed step is skipped entirely. Your changes survive.
- **Bundled fallback** — if you delete a starter, the bundled version in the
  skill folder takes over at resolve time. Nothing breaks.
- **Opt-in refresh** — to pull a new starter after the manifest grows, or
  to restore a file you deleted:

  ```bash
  uv run scripts/seed.py list                     # see what's available
  uv run scripts/seed.py refresh personal-cv      # copy bundled → user if absent
  uv run scripts/seed.py refresh --all            # every missing starter
  uv run scripts/seed.py refresh tutorial \
      --force --justification "reset to ship defaults"
  ```

The manifest (`seed-manifest.yaml` at the repo root) is the single source of
truth for what gets seeded. This is the foundation for the Phase-4 share/import
flow — recipes that live under `~/.katib/` are the ones you'll be able to
package up and share with other Katib users.

### What's in the starter library

| Domain | Starter recipes |
|---|---|
| Business | `business-proposal-letter`, `business-proposal-one-pager`, `business-proposal-proposal` |
| Editorial | `editorial-article`, `editorial-white-paper` |
| Financial | `financial-invoice`, `financial-quote` |
| Formal | `formal-authority-letter`, `formal-noc` |
| Legal | `legal-mou`, `legal-nda`, `legal-service-agreement` |
| Personal | `personal-bio`, `personal-cover-letter`, `personal-cv` |
| Report | `report-progress` |
| Tutorial | `tutorial`, `tutorial-cheatsheet`, `tutorial-handoff`, `tutorial-how-to`, `tutorial-onboarding` |

Need something we don't ship? **Build it yourself with the AI-assisted
builder** — see [TUTORIAL.md](TUTORIAL.md) for a 20-minute walkthrough.

### Layout primitives

Wide tables, slide decks, full-bleed covers, multi-column essays, part
dividers, and appendices all compose from dedicated layout components
that handle the page-geometry work for you:

| Component | Use case |
|---|---|
| `landscape-section` | Wide data tables, horizontal timelines, wide charts |
| `slide-frame` | 16:9 slide-deck pages with 4 variants (title / content / two-column / image-bg) |
| `full-bleed-page` | Edge-to-edge covers and hero images with optional overlay text |
| `two-column-page` | Newspaper / magazine editorial flow |
| `section-divider-page` | "Part II" style atomic dividers between major sections |
| `appendix-page` | Flowing appendix content with a running header in the top margin |

## Custom recipes & components

Katib separates bundled content (shipped with the skill) from user
content (yours, kept under `~/.katib/`). Both tiers are searched at
resolve time, with user content silently shadowing bundled content of
the same name.

| Tier | Path | Written by |
|---|---|---|
| Bundled recipes | `~/.claude/skills/katib/recipes/` | Skill install |
| Bundled components | `~/.claude/skills/katib/components/` | Skill install |
| User recipes | `~/.katib/recipes/` | `katib recipe new` |
| User components | `~/.katib/components/` | `katib component new --namespace user` |
| Brand profiles + cover presets | `~/.katib/brands/` | `katib brand new`, `--save-cover-preset` |
| Audit + gate logs | `~/.katib/memory/` | Runtime |

### Create a custom recipe

```bash
uv run scripts/recipe.py new my-proposal --namespace user \
    --description "Client proposal template"
# edit ~/.katib/recipes/my-proposal.yaml (sections, inputs, languages)

# render via /katib in Claude Code, or directly:
uv run scripts/build.py my-proposal --lang en
```

### Create a custom component — two paths

**Path A — AI-assisted builder (recommended).** Invoke `/katib component new`
in Claude Code and Claude walks you through an interview, generates the
files, validates, renders a preview, and iterates on feedback. See
[TUTORIAL.md](TUTORIAL.md) for a full walkthrough or the
[COMPONENT-BUILDER.md playbook](COMPONENT-BUILDER.md) for reference.

**Path B — manual scaffold.** If you'd rather hand-edit:

```bash
uv run scripts/component.py new client-hero --tier section \
    --namespace user --languages en,ar \
    --description "Full-width hero with brand lockup"
# edit ~/.katib/components/sections/client-hero/{en.html,ar.html,styles.css}
uv run scripts/component.py validate client-hero
uv run scripts/component.py test client-hero        # renders EN + AR preview
uv run scripts/component.py register client-hero    # update audit + capabilities
```

Reference it from a recipe exactly like a bundled component:

```yaml
sections:
  - component: client-hero    # resolves user-tier first, bundled second
    inputs:
      headline: "Proposal for ACME"
```

### Shadow semantics

A user component or recipe with the same name as a bundled one silently
wins at resolve time — same pattern as local `.env` overriding shell
env vars. But **scaffolding** a user item that collides with a bundled
name is refused without `--force --justification '<why>'`, so you can't
accidentally mask a shipped template.

### Env var overrides

For testing and CI isolation: `KATIB_RECIPES_DIR`, `KATIB_COMPONENTS_DIR`,
`KATIB_BRANDS_DIR`, `KATIB_MEMORY_DIR` redirect each user-tier path.

## v1 users

Your install still works. No action needed. v2 is a breaking change and will
ship as `1.0.0` with a migration guide. Until then:

- `@jasemal/katib@0.20.0` on npm remains the stable release
- v0.x receives no further releases; all new work targets v2
- When v1.0.0 stable ships, `@latest` moves off v0.x

## Development phases

| Phase | Status | Scope |
|---|---|---|
| **0 — Archive + ADR** | ✅ shipped | v1 frozen in `v1-reference/`, ADRs approved, baseline measurements |
| **1 — Core engine + primitives** | ✅ shipped | Composer, renderer, tokens, output routing, first 8 primitives |
| **2 — Sections + first recipe** | ✅ shipped | Image-consuming sections, tutorial recipe, CLI subcommands, decision gate |
| **3a — Layout primitives** | ✅ shipped | `landscape-section`, `slide-frame`, `full-bleed-page`, `two-column-page`, `section-divider-page`, `appendix-page` |
| **3b — AI-assisted component builder** | ✅ shipped | `COMPONENT-BUILDER.md` playbook + `/katib component new` entry point |
| **3c — Content primitives** | ✅ shipped | `executive-summary`, `timeline`, `citation`, `references-list`, `toc`, `metric-block` |
| **3d — Recipe migration** | ✅ shipped | 6 new bilingual starters (legal-nda, legal-service-agreement, personal-bio, formal-authority-letter, report-progress, editorial-article) |
| **3e — Docs + tutorial** | ✅ shipped | README polish, TUTORIAL.md, CHANGELOG, seed manifest expansion |
| **4 — Self-improvement + sharing** | next | Reflect, feedback, import/export — `~/.katib/` content becomes shareable |
| **5 — v1.0.0 release** | planned | Migration guide, final CHANGELOG, `@latest` moves off v0.x |

## Contributing

Not accepting external contributions during Phases 0–4. After v1.0.0 stable
ships, Tier 2 (sections) and Tier 3 (recipes) will accept community PRs.
Tier 1 primitives stay curated until v2.0.

## License

MIT — see [LICENSE](LICENSE).

## Links

- **npm:** [`@jasemal/katib`](https://www.npmjs.com/package/@jasemal/katib)
- **Issues:** [github.com/jneaimi/katib/issues](https://github.com/jneaimi/katib/issues)
- **Author:** [Jasem Al Neaimi](mailto:jneaimi@gmail.com)
