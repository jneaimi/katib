# Katib — Diagrams (compatibility stub)

> **This file was split into a catalog in v0.20.0.** See [`references/diagrams/`](diagrams/index.md) — 13 type-specific specs, 2 editorial primitives, reusable Jinja snippets.

## Quick-jump

| You want… | Read |
|---|---|
| **Catalog entry point** — philosophy, selection guide, complexity budget | [`diagrams/index.md`](diagrams/index.md) |
| **Color context → semantic role mapping** (`colors.accent` → `accent` etc.) | [`diagrams/style.md`](diagrams/style.md) |
| **Universal primitives** (arrow markers, node box, arrow labels, legend) | [`diagrams/primitives.md`](diagrams/primitives.md) |
| **Arabic / RTL** — overlay pattern, mirroring, lint rule | [`diagrams/rtl-notes.md`](diagrams/rtl-notes.md) |
| **Editorial callouts** (italic-serif marginalia) | [`diagrams/primitive-annotation.md`](diagrams/primitive-annotation.md) |
| **Hand-drawn variant** (SVG filter) | [`diagrams/primitive-sketchy.md`](diagrams/primitive-sketchy.md) |

## 13 diagram types

Architecture · Flowchart · Sequence · State · ER · Timeline · Swimlane · Quadrant · Nested · Tree · Layers · Venn · Pyramid

See `diagrams/type-<name>.md` for each. Load only the one you need.

## Why the rename matters

`build.py --check` still references `diagrams.md` in error messages for the Arabic-in-SVG rule. That rule now lives at [`diagrams/rtl-notes.md`](diagrams/rtl-notes.md); this stub keeps the error string's link target resolvable.

## Attribution

The catalog structure, complexity budget, and anti-pattern taxonomy are adapted from Cathryn Lavery's [`diagram-design`](https://github.com/cathrynlavery/diagram-design) (MIT). Katib adds Jinja color interpolation, WeasyPrint constraints, bilingual EN+AR overlay patterns, and per-domain font inheritance.
