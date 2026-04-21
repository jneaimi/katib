# Katib — Diagrams (Inline SVG)

Print-grade diagrams in katib are inline SVG embedded directly in the template HTML. WeasyPrint renders SVG natively — no external tool, no build step, no new dependencies. SVGs stay crisp at any print DPI, text inside is selectable/searchable in the PDF, and colors can auto-adopt the active brand via Jinja template interpolation.

---

## How it works

SVGs go inside the `.html` template (where Jinja runs). Colors interpolate at render time from the `colors` context — the resolved domain tokens merged with any `--brand` override.

**Important:** WeasyPrint does NOT resolve CSS `var(--accent)` inside SVG attributes or SVG-scoped stylesheets. Write `fill="{{ colors.accent }}"` instead. Everything else (CSS outside SVG, token injection at `:root`) still uses `var()`.

Example — same template, two brands:

```bash
uv run scripts/build.py how-to --domain tutorial --lang en ...                    # domain default (teal)
uv run scripts/build.py how-to --domain tutorial --lang en --brand triden ...     # navy
uv run scripts/build.py how-to --domain tutorial --lang en --brand example ...    # example blue
```

## Brand color context available to Jinja

Reference these with `{{ colors.<name> }}` inside any SVG attribute or CSS:

| Key | Use for |
|---|---|
| `colors.accent` | Primary brand color — box fills, lines |
| `colors.accent_2` | Secondary brand color — emphasis, highlights |
| `colors.accent_on` | Text on accent fills |
| `colors.text`, `colors.text_secondary`, `colors.text_tertiary` | Body text, captions, labels |
| `colors.border`, `colors.border_strong` | Outlines, connector lines |
| `colors.page_bg` | Canvas background (rarely needed — SVG defaults to transparent) |
| `colors.tag_bg`, `colors.tag_fg` | Pill/badge backgrounds and labels |
| `colors.code_bg`, `colors.code_fg` | Code block colors |

Each value is a resolved hex (e.g. `#1B2A4A`). The `colors` dict mirrors `semantic_colors` from the domain's `tokens.json`, with `--` stripped and dashes replaced with underscores.

## Sizing and layout

- **Always set `viewBox`** — it's what makes the SVG scale crisply. `viewBox="0 0 <w> <h>"` defines the internal coordinate system.
- **Omit hardcoded `width`/`height`** on the `<svg>` root. Size via CSS on the container (`style="max-width: 100%;"` or a class).
- **Accessibility:** include `role="img"` and `aria-label="…"` so the PDF's accessibility tree has meaningful text for each diagram.

```html
<figure>
  <svg viewBox="0 0 600 80" role="img" aria-label="Process: Plan → Build → Ship" style="max-width: 100%;">
    <!-- ... -->
  </svg>
  <figcaption>Figure 1: Three-phase delivery</figcaption>
</figure>
```

## Patterns

### 1. Labeled box

```html
<svg viewBox="0 0 220 64" role="img" aria-label="Phase 1: Kickoff" style="max-width: 100%;">
  <rect x="1" y="1" width="218" height="62" rx="6" fill="{{ colors.accent }}"/>
  <text x="110" y="38" fill="{{ colors.accent_on }}"
        text-anchor="middle" font-size="14" font-weight="500">Phase 1: Kickoff</text>
</svg>
```

### 2. Arrow / connector

Define the arrowhead once per SVG via `<marker>`, then reuse on any `<line>` or `<path>`:

```html
<svg viewBox="0 0 80 20" role="img" aria-label="arrow" style="max-width: 100%;">
  <defs>
    <marker id="arr" viewBox="0 0 10 10" refX="8" refY="5"
            markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="{{ colors.text_tertiary }}"/>
    </marker>
  </defs>
  <line x1="0" y1="10" x2="72" y2="10"
        stroke="{{ colors.text_tertiary }}" stroke-width="1.5" marker-end="url(#arr)"/>
</svg>
```

### 3. Horizontal process flow (3 boxes)

```html
<svg viewBox="0 0 600 80" role="img" aria-label="Plan → Build → Ship" style="max-width: 100%;">
  <defs>
    <marker id="arr" viewBox="0 0 10 10" refX="8" refY="5"
            markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="{{ colors.text_tertiary }}"/>
    </marker>
  </defs>

  <rect x="0"   y="10" width="160" height="60" rx="6" fill="{{ colors.accent }}"/>
  <text x="80"  y="46" fill="{{ colors.accent_on }}" text-anchor="middle" font-size="14">Plan</text>

  <line x1="165" y1="40" x2="215" y2="40"
        stroke="{{ colors.text_tertiary }}" stroke-width="1.5" marker-end="url(#arr)"/>

  <rect x="220" y="10" width="160" height="60" rx="6" fill="{{ colors.accent }}"/>
  <text x="300" y="46" fill="{{ colors.accent_on }}" text-anchor="middle" font-size="14">Build</text>

  <line x1="385" y1="40" x2="435" y2="40"
        stroke="{{ colors.text_tertiary }}" stroke-width="1.5" marker-end="url(#arr)"/>

  <rect x="440" y="10" width="160" height="60" rx="6" fill="{{ colors.accent }}"/>
  <text x="520" y="46" fill="{{ colors.accent_on }}" text-anchor="middle" font-size="14">Ship</text>
</svg>
```

### 4. Layered architecture (stacked)

Three labeled tiers with subtle hierarchy — good for system diagrams.

```html
<svg viewBox="0 0 400 240" role="img" aria-label="System layers" style="max-width: 100%;">
  <rect x="0"   y="0"   width="400" height="70" rx="6" fill="{{ colors.accent }}"/>
  <text x="200" y="42" fill="{{ colors.accent_on }}" text-anchor="middle" font-size="16" font-weight="500">Presentation</text>

  <rect x="0"   y="85"  width="400" height="70" rx="6" fill="{{ colors.tag_bg }}" stroke="{{ colors.border }}" stroke-width="1"/>
  <text x="200" y="127" fill="{{ colors.tag_fg }}" text-anchor="middle" font-size="16" font-weight="500">Application</text>

  <rect x="0"   y="170" width="400" height="70" rx="6" fill="{{ colors.page_bg }}" stroke="{{ colors.border_strong }}" stroke-width="1"/>
  <text x="200" y="212" fill="{{ colors.text }}" text-anchor="middle" font-size="16" font-weight="500">Data</text>
</svg>
```

### 5. Numbered step sequence

A compact list-style diagram useful in tutorials and onboarding docs.

```html
<svg viewBox="0 0 480 80" role="img" aria-label="Steps: 1, 2, 3" style="max-width: 100%;">
  <!-- step 1 -->
  <circle cx="40"  cy="40" r="22" fill="{{ colors.accent }}"/>
  <text   x="40"   y="46" fill="{{ colors.accent_on }}" text-anchor="middle" font-size="16" font-weight="600">1</text>
  <text   x="80"   y="46" fill="{{ colors.text }}"      font-size="14">Install</text>

  <!-- step 2 -->
  <circle cx="200" cy="40" r="22" fill="{{ colors.accent }}"/>
  <text   x="200"  y="46" fill="{{ colors.accent_on }}" text-anchor="middle" font-size="16" font-weight="600">2</text>
  <text   x="240"  y="46" fill="{{ colors.text }}"      font-size="14">Configure</text>

  <!-- step 3 -->
  <circle cx="360" cy="40" r="22" fill="{{ colors.accent }}"/>
  <text   x="360"  y="46" fill="{{ colors.accent_on }}" text-anchor="middle" font-size="16" font-weight="600">3</text>
  <text   x="400"  y="46" fill="{{ colors.text }}"      font-size="14">Run</text>
</svg>
```

## Bilingual notes

Arabic documents render the same SVG — the canvas is direction-neutral. Apply these adjustments when needed:

- **Labels:** swap the `<text>` content for the AR string. If you have both variants, use Jinja: `{{ "Kickoff" if lang == "en" else "بدء" }}`.
- **Mirrored layout:** for left-to-right process flows in AR documents, mirror with a transform on the root group:
  ```html
  <svg viewBox="0 0 600 80" ...>
    <g transform="{% if direction == 'rtl' %}translate(600,0) scale(-1,1){% endif %}">
      <!-- draw LTR, the transform flips it when needed -->
    </g>
  </svg>
  ```
  Place `<text>` elements outside that group (or apply a counter-transform) to keep them upright.
- **Alt text:** provide `aria-label` in both languages: `aria-label="{{ 'Process flow' if lang == 'en' else 'مخطط العملية' }}"`.

## Fonts inside SVG

SVG text defaults to a generic sans-serif. To inherit the document's brand font, set `font-family="inherit"` on the `<text>` or a parent `<g>`:

```html
<svg viewBox="0 0 220 64" style="max-width: 100%;" font-family="inherit">
  <text x="110" y="38" ...>label</text>
</svg>
```

This picks up the active brand's EN or AR primary font (e.g. `IBM Plex Arabic` for AR, `Inter` for EN) based on the rendering template.

## Tips

- **Don't embed PNGs inside SVG.** Defeats the vector advantage. Use a plain `<img>` tag at native resolution instead.
- **Keep text larger than 9pt.** Anything smaller won't print cleanly.
- **Leave 4–6 pt padding inside boxes** (use `x`/`y` offsets from the edge). Text tight against a border reads poorly.
- **Use `rx` on rectangles** (e.g. `rx="6"`) to match the rest of the design system's rounded corners.
- **Round connector coordinates to integers** to avoid WeasyPrint sub-pixel rendering artifacts.

## Authoring outside a template

If you draft a diagram in Figma/Excalidraw and export raw SVG, the file will have hardcoded colors. Two options:

1. **Leave hardcoded** — fine for one-off diagrams where brand-switching isn't needed.
2. **Rewrite to `{{ colors.X }}`** — find/replace the hex codes with the matching token reference, then paste the SVG into the template.

## When to reach for something else

- **Complex flowcharts / sequence diagrams** → consider a Mermaid-to-SVG build step (not wired today; ask and we'll add it).
- **Hand-sketched / expressive diagrams** → the `/diagram` skill produces Excalidraw PNGs, but they pixelate in print; use sparingly.
- **Data viz with many points** → render via Python (matplotlib → SVG export), then paste the SVG source and optionally rewrite colors.
