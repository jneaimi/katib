# landscape-diagram

**Tier:** section · **Namespace:** user

## Purpose

Single-page landscape A4 canvas for complex diagrams. Guarantees the diagram
fits on **exactly one** landscape page — never splits, never spills. Built
for entity-relationship diagrams, end-to-end process flows, architecture
maps, and other visuals too dense for the portrait content area.

## How it works

- Declares a named `@page landscape-diagram` rule (A4 landscape, 20mm
  margin) and opts in via `page: landscape-diagram` on the section root.
- Section is `page-break-inside: avoid` and has `height: 170mm` (the
  available content height after margins).
- Inside, a flex column distributes space: header (if any) at the top,
  caption (if any) at the bottom, and the **canvas** flex-grows to fill
  the remainder.
- The canvas has `overflow: hidden` so any oversize content is clipped
  rather than pushed onto a second page. Inline SVGs with `viewBox` and
  the default `preserveAspectRatio="xMidYMid meet"` automatically scale
  down to fit, so they never get clipped — they just shrink to the box.

## Inputs

| Input | Type | Required | Notes |
|---|---|---|---|
| `eyebrow` | string | no | Small label above the title (e.g. `"FIGURE 1"`). |
| `title` | string | no | Heading at the top. Omit for a diagram-only page. |
| `caption` | string | no | One-line description placed below the diagram. |
| `raw_body` | string | **yes** | Trusted HTML — typically inline SVG with `viewBox`. Not auto-escaped. |

## Recommended pattern for SVGs

Author the SVG with a `viewBox` and let it fill the canvas:

```html
<svg viewBox="0 0 1000 600" xmlns="http://www.w3.org/2000/svg">
  <!-- diagram content in viewBox coordinates -->
</svg>
```

The component will give the SVG `width: 100%; height: 100%`, and the
`viewBox` + default `preserveAspectRatio` make it scale uniformly into
the canvas. Aspect ratios near `5:3` (landscape, slightly wide) work
best — they fill the canvas with minimal whitespace.

## Example usage in a recipe

```yaml
- component: landscape-diagram
  inputs:
    eyebrow: "FIGURE A"
    title: "End-to-end procurement flow"
    caption: "All boxes below approval-gated; arrows annotate trigger names."
    raw_body: |
      <svg viewBox="0 0 1000 560" xmlns="http://www.w3.org/2000/svg">
        <!-- ... -->
      </svg>
```

## Notes

- **Don't pair with content larger than the canvas** — the canvas clips,
  it doesn't paginate. If a diagram won't fit at any zoom, split it into
  two diagrams or use `landscape-section` (which paginates) instead.
- **Hardcode colors** in the SVG `style="..."` attributes. WeasyPrint
  doesn't resolve `var(--*)` inside SVG element style attributes — fills
  fall back to black.
- **One diagram per page**, by design. The component forces a page break
  before and after.

## Accessibility

- Root element carries `lang` / `dir` attributes for LTR/RTL switching.
- Caption element uses `<figcaption>` semantics.
