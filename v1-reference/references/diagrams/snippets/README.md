# Diagram Snippets (Jinja partials)

Reusable SVG partials. Each snippet uses `{{ colors.* }}` from the brand/domain color context, so they inherit the active brand automatically.

## Usage

Include inside a diagram template:

```jinja
<svg viewBox="0 0 960 320" role="img" aria-label="…" style="max-width:100%;">
  <defs>
    {% include 'references/diagrams/snippets/arrow-markers.svg.j2' %}
  </defs>

  {# a node #}
  {% set node = {
    'x': 40, 'y': 80, 'w': 160, 'h': 48,
    'fill': colors.page_bg, 'stroke': colors.text,
    'name': 'API Gateway', 'tag': 'API', 'sublabel': 'nginx:443'
  } %}
  {% include 'references/diagrams/snippets/node-box.svg.j2' %}

  {# a callout #}
  {% set callout = {
    'text_x': 904, 'text_y': 36,
    'target_x': 520, 'target_y': 216,
    'control_x': 700, 'control_y': 84,
    'text': 'no imports, no configuration'
  } %}
  {% include 'references/diagrams/snippets/annotation-callout.svg.j2' %}

  {# legend at the bottom #}
  {% set legend = {
    'y': 280, 'viewbox_w': 960,
    'items': [
      {'kind': 'swatch', 'color': colors.accent,        'label': 'Focal',         'x': 110},
      {'kind': 'line',   'color': colors.text_secondary,'label': 'Default arrow', 'x': 240},
      {'kind': 'dashed', 'color': colors.text_secondary,'label': 'Async / return','x': 400}
    ]
  } %}
  {% include 'references/diagrams/snippets/legend-strip.svg.j2' %}
</svg>
```

## Snippets

| File | Context variable | Produces |
|---|---|---|
| `arrow-markers.svg.j2` | none (uses `colors`) | 3 `<marker>` definitions — default, accent, link |
| `node-box.svg.j2` | `node` dict | Masked node box + optional type tag + optional sublabel |
| `annotation-callout.svg.j2` | `callout` dict | Italic text + dashed Bézier leader + landing dot |
| `legend-strip.svg.j2` | `legend` dict | Horizontal legend strip with hairline separator |
| `timeline-axis.svg.j2` | `axis` dict | Horizontal baseline with tick marks + date labels |

## Bilingual (AR)

On `.ar.html` templates, `aria-label` goes via Jinja:

```jinja
<svg aria-label="{{ 'Architecture' if lang == 'en' else 'البنية المعمارية' }}" ...>
```

Any Arabic label text should NOT sit inside SVG — use the `.diagram-stage` + `.diagram-label` overlay pattern (see `../rtl-notes.md`). Snippets that include English/numeric labels (like `timeline-axis` tick dates) still work in AR templates; only the *geometry + numbers* go through SVG.
