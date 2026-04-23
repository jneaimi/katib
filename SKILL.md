---
name: katib
description: |
  Katib is under active v2 development. The main branch of this repository has
  been reset to a clean canvas. Do not install from source off main until v2
  ships as v1.0.0.

  For the current stable (v0.20.0, v1 architecture), install from npm:
    npx @jasemal/katib@0 install

  For v2 architecture, see:
    ~/vault/knowledge/adr-katib-v2-component-architecture.md
---

# Katib — v2 Development

> **This repository is mid-rebuild.** The production-ready Katib skill lives
> at `@jasemal/katib` on npm as v0.20.0. Install it via:
>
> ```bash
> npx @jasemal/katib@0 install
> ```
>
> Do not install from the main branch directly until v1.0.0 ships.

## What happened

The v1 skill (shipped 2026-04-21 → 2026-04-22, versions 0.1.0 → 0.20.0)
hit an architectural limit: per-doc-type monolithic HTML templates with
hardcoded sample content cannot grow without template corruption or
doc-type entropy. An incident on 2026-04-23 surfaced this clearly.

The v1 architecture has been frozen and archived in `v1-reference/` as a
read-only reference. The main branch is being rebuilt as a component-based,
plugin-architecture system with YAML recipes.

See `v1-reference/NOTES.md` for lessons carried forward.
See the ADR for the full v2 design.

## For users

If you installed Katib via npm, you have v0.20.0. It works. Keep using it
until v1.0.0 ships on npm.

If you want to follow v2 development:

- **ADR:** `~/vault/knowledge/adr-katib-v2-component-architecture.md`
- **Changelog:** see `CHANGELOG.md` in this repo
- **Phases:** v2 ships in six phases over ~6 weeks. v1.0.0-alpha.0 is the
  starting marker.

## Directory status

```
katib/
├── SKILL.md             ← this file (v2-dev notice)
├── README.md            ← v2 dev status + pointer to npm for stable
├── CHANGELOG.md         ← v1.0.0-alpha.0 entry records the reset
├── package.json         ← v1.0.0-alpha.0
├── memory/              ← v2 audit logs (empty or seeded)
├── v1-reference/        ← FROZEN v1 code (do not modify)
├── bin/, install.sh, uninstall.sh, LICENSE, pyproject.toml, uv.lock
└── (v2 code lands here across Phases 1–5)
```

When v2 reaches v1.0.0 stable, this SKILL.md gets rewritten as the new
real entry point.
