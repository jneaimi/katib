# Katib — Bilingual PDF Document Generation

> **⚠️ v2 is in alpha.** User-content plumbing and the first round of
> recipes are shipped and tested, but APIs and recipe shapes can still
> change before `1.0.0`. If you need stability, stay on
> `npx @jasemal/katib@0`. If you want the v2 architecture (custom
> recipes and components under `~/.katib/`, bilingual EN+AR,
> auto-regenerating capabilities), `npx @jasemal/katib install` installs
> the current alpha.

[![CI](https://github.com/jneaimi/katib/actions/workflows/ci.yml/badge.svg)](https://github.com/jneaimi/katib/actions/workflows/ci.yml)
[![npm](https://img.shields.io/npm/v/%40jasemal%2Fkatib?color=1B2A4A&label=npm&style=flat-square)](https://www.npmjs.com/package/@jasemal/katib)
[![license](https://img.shields.io/badge/license-MIT-1B2A4A?style=flat-square)](LICENSE)
![status](https://img.shields.io/badge/v2-alpha-orange?style=flat-square)

**كاتب** (*kātib*, "the writer") — the one who shapes words onto paper.

One skill, bilingual (EN + AR) print-grade PDF generation for Claude Code.
HTML + CSS → WeasyPrint → PDF.

---

## Where things stand

| | |
|---|---|
| **Stable (v1):** | `@jasemal/katib@0.20.0` on npm — install with `npx @jasemal/katib@0 install` |
| **In development (v2):** | `1.0.0-alpha.0` — clean-canvas rebuild, component architecture |
| **Archived:** | Full v1 code under `v1-reference/` (read-only) |
| **Architecture notes:** | See [CHANGELOG.md](CHANGELOG.md) for phase-by-phase design decisions |

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

### Create a custom component

```bash
uv run scripts/component.py new client-hero --tier section \
    --namespace user --languages en,ar \
    --description "Full-width hero with brand lockup"
# edit ~/.katib/components/sections/client-hero/{en.html,ar.html,styles.css}
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

v2 ships in six phases over approximately six weeks:

| Phase | Scope |
|---|---|
| **0 — Archive + ADR** (3–5 days, **in progress**) | v1 frozen in `v1-reference/`, ADR approved, baseline measurements |
| **1 — Core engine + primitives** (1 week) | Composer, renderer, tokens, output routing, first 8 primitives |
| **2 — Sections + first recipe** (2 weeks) | First image-consuming sections, tutorial recipe, CLI subcommands, decision gate |
| **3 — Recipe migration** (3 weeks) | Port v1 doc-types to v2 recipes (triaged — not all doc-types migrate) |
| **4 — Self-improvement + sharing** (2 weeks) | Reflect, feedback, import/export |
| **5 — v1.0.0 release** (1 week) | CHANGELOG, migration guide, npm publish, GitHub release |

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
