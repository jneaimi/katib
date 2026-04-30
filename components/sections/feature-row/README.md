# feature-row

Repeating row pattern with an icon (or thumbnail) on the leading side, a heading, and a body paragraph. Use for "what we do" / "key features" / "what's included" / "how it works" sections.

## When to use

Anywhere the same visual pattern repeats 3–6 times for parallel ideas — and you want each item to carry enough body text to stand on its own. Distinct from:

- `kv-list` — terms + values, no body
- `objectives-box` — bullets, no per-item heading
- `comparison-table` — features × options grid

## Inputs

| Field | Required | Description |
|---|---|---|
| `eyebrow` | no | Small uppercase label above the section heading. |
| `title` | no | Optional section heading. |
| `rows` | yes | Array of `{icon?, image?, heading, body}`. |
| `layout` | no | `"stacked"` (default) or `"two-up"` (2-col grid). |

## Per-row fields

- **`icon`** — 1–2 character glyph rendered in an accent-coloured circle (e.g. "1", "★", emoji)
- **`image`** — small thumbnail path (rendered as a 36×36 squared image instead of the icon)
- **`heading`** — bold one-line title
- **`body`** — one paragraph of supporting text

Provide either `icon` OR `image`, not both. If neither is provided, a muted dot is shown.

## Example

```yaml
- component: feature-row
  inputs:
    eyebrow: "WHAT'S INCLUDED"
    title: "How katib works"
    layout: stacked
    rows:
      - icon: "1"
        heading: "Install the engine"
        body: "One command — npx @jasemal/katib install — drops the engine into your local cache. No SaaS account, no dashboard."
      - icon: "2"
        heading: "Browse the marketplace"
        body: "44+ packs — templates and components — installable with a single command. Each pack is versioned and reproducible."
      - icon: "3"
        heading: "Render print-grade PDFs"
        body: "Bilingual EN+AR by default. WeasyPrint produces A4 with proper margins, page breaks, and OpenType ligatures."
```
