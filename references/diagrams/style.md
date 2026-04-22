# Diagram Style — Semantic Role Map

**The single source of truth for diagram tokens.** Every `type-*.md` refers to roles by name (`accent`, `text`, `border`), never by hex. The hex values come from the active domain's `tokens.json`, optionally overridden by the `--brand` profile.

> **Why Jinja, not CSS vars?** WeasyPrint does *not* resolve `var(--accent)` inside SVG attributes or SVG-scoped stylesheets. Write `fill="{{ colors.accent }}"` instead. Outside SVG (regular CSS), `var()` still works.

---

## Katib color context → semantic role

Type references use these names — this table maps them to the `colors` dict injected by `build.py`.

| Role (in type specs) | Jinja | Semantic intent |
|---|---|---|
| `paper` | `{{ colors.page_bg }}` | Canvas background, mask rectangles |
| `paper-2` | `{{ colors.tag_bg }}` | Container/tray backgrounds, legend strip |
| `ink` | `{{ colors.text }}` | Primary text, primary stroke |
| `muted` | `{{ colors.text_secondary }}` | Secondary text, default arrows, sublabels |
| `soft` | `{{ colors.text_tertiary }}` | Tertiary text, boundary labels, fine detail |
| `rule` | `{{ colors.border }}` | Hairline borders, lane dividers |
| `rule-solid` | `{{ colors.border_strong }}` | Stronger dividers, axis baselines |
| `accent` | `{{ colors.accent }}` | Focal / 1–2 max per diagram |
| `accent-tint` | *see note* | Fill paired with accent stroke |
| `accent-on` | `{{ colors.accent_on }}` | Text sitting on an accent fill |
| `link` | `{{ colors.accent_2 }}` | HTTP/API/external edges — secondary accent |

### `accent-tint`: how to produce it

Brands don't typically ship a pre-mixed tint. Compose inline by layering an opacity-reduced accent over paper, or use `rgba()` if the brand's accent is known to be safe as a base color:

```html
<!-- Preferred: double-rect (opaque paper mask + translucent accent on top) -->
<rect x="X" y="Y" width="W" height="H" rx="6" fill="{{ colors.page_bg }}"/>
<rect x="X" y="Y" width="W" height="H" rx="6" fill="{{ colors.accent }}" opacity="0.08"/>
<rect x="X" y="Y" width="W" height="H" rx="6" fill="none"
      stroke="{{ colors.accent }}" stroke-width="1"/>
```

The triple-rect pattern (paper → accent@low-opacity → stroke-only outline) reads as "accent-tinted fill with accent border" without requiring a pre-mixed hex.

---

## Node type → treatment

Reference these by name in type specs. Each treatment = `fill` + `stroke` (plus optional `stroke-dasharray`).

| Type | Fill | Stroke | Use for |
|---|---|---|---|
| **focal** (1–2 max) | accent-tint (see above) | `accent` | The 1–2 elements the reader should look at first |
| **backend / API / step** | `paper` (white) | `ink` | Default — most nodes |
| **store / state** | `ink @ 0.05` opacity | `muted` | Databases, caches, state containers |
| **external / cloud** | `ink @ 0.03` opacity | `ink @ 0.30` | Third-party services, external APIs |
| **input / user** | `muted @ 0.10` opacity | `soft` | User actors, ingress points |
| **optional / async** | `ink @ 0.02` opacity | `ink @ 0.20` dashed `4,3` | Optional paths, async calls |
| **security / boundary** | `accent @ 0.05` opacity | `accent @ 0.50` dashed `4,4` | Trust zones, security group outlines |

Opacity values compose inline with `<rect fill="{{ colors.text }}" opacity="0.05"/>` rather than pre-mixed hex.

---

## Typography inside SVG

SVG text defaults to generic sans-serif. Katib inherits the template's brand font family via:

```html
<svg viewBox="..." font-family="inherit">
  <text x="..." y="...">label</text>
</svg>
```

That gives you the active domain's EN font (e.g. `Inter`, `Newsreader`, `Georgia`) — or the AR font if the template is `.ar.html` (`Cairo`, `Amiri`, `IBM Plex Arabic`).

### Register conventions

| Register | Font | Size | Use |
|---|---|---|---|
| Title (diagram headline) | brand display | 20–24px | Rare — most diagrams don't need a title, they sit inside a doc heading |
| Node name | brand body | 12–14px, weight 500–600 | Human-readable labels |
| Sublabel / technical | monospace (when available) | 8–10px | Ports, URLs, field types, commands |
| Eyebrow / tag | monospace, uppercase, tracked 0.08–0.14em | 7–9px | Type tags, axis labels |
| Arrow label | monospace | 8px | Annotation on arrows |
| Callout (editorial) | brand serif *italic* | 14px | Marginalia only — see `primitive-annotation.md` |

**Load-bearing:** mono is for *technical* content. Names go in the brand body sans. Don't use monospace as a blanket "looks like code" font.

When the brand doesn't declare a monospace in `tokens.json`, fall back to the CSS default:

```html
<text font-family="ui-monospace, 'SF Mono', Menlo, monospace">PORT</text>
```

---

## Stroke, radius, spacing

| Token | Value | Use |
|---|---|---|
| `stroke-thin` | 0.8 | Tag-box outlines, leaf nodes |
| `stroke-default` | 1 | Most strokes |
| `stroke-strong` | 1.2 | Emphasis / axis lines |
| `radius-sm` | 4 | Small tags |
| `radius-md` | 6 | Node boxes |
| `radius-lg` | 8 | Containers, rings |
| `grid` | 4 | Every coord, size, and gap divisible by 4 (hard rule) |

---

## Brand interaction

When the user passes `--brand jasem`, `colors.accent` becomes the brand's primary (e.g. amber `#F59E0B`). Every diagram in that render inherits the new focal color automatically. No edits to the SVG templates required.

Partial brand profiles are fine: a brand that sets `accent` but not `accent_2` falls back to the domain default for `colors.accent_2`. A brand that overrides fonts but not colors keeps the domain palette.

See `brands/example.yaml` for the brand schema; see the root `SKILL.md` for `--brand` CLI usage.

---

## Constraints (don't break these)

- **Never hardcode hex in SVG attributes.** Always `{{ colors.<name> }}`.
- **Never use CSS custom properties inside `<svg>`.** WeasyPrint won't resolve them.
- **Never set `width`/`height` on the `<svg>` root.** Use `viewBox` + CSS.
- **Accent on max 2 elements.** §8 of [index.md](index.md).
- **No Arabic inside `<text>`/`<tspan>`.** See [rtl-notes.md](rtl-notes.md). `build.py --check` fails the build.
