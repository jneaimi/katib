# cv-layout

**Tier:** section

## Purpose

2-column sidebar+main page layout for CV / profile / portfolio recipes.
Emits a full-page CSS grid with 70mm dark-accent sidebar + 1fr main
column. Content is supplied as raw HTML via `sidebar_html` and
`main_html` inputs — callers compose sidebar primitives
(`skill-bar-list`, `tag-chips`) and main sections inline.

Fundamental structural departure from the single-column linear-flow
pattern used by every other Phase-3 recipe.

## Variants

- default (the only shape; 70mm sidebar width is stable for A4)

## Inputs

- `sidebar_html` (string, required): Trusted HTML for the sidebar
  column. Typically: photo slot + name block + contact list +
  skill-bar-list sections + tag-chips section.
- `main_html` (string, required): Trusted HTML for the main column.
  Typically: Summary + Experience + Education + Selected Projects
  sections.

## Usage Example

```yaml
- component: cv-layout
  inputs:
    sidebar_html: |
      <div class="photo"></div>
      <div class="name-block">
        <div class="name">Alex Acme</div>
        <div class="headline">Senior AI Engineer · GCC</div>
      </div>
      <section>
        <h3>Contact</h3>
        ...
      </section>
    main_html: |
      <section>
        <h2>Summary</h2>
        <p>...</p>
      </section>
      <section>
        <h2>Experience</h2>
        ...
      </section>
```

## Rendering

- `<section class="katib-cv-layout">` is the CSS grid container.
- `.katib-cv-layout__sidebar` = accent-bg column (`<aside>`).
- `.katib-cv-layout__main` = transparent-bg column (`<main>`).
- Grid uses `grid-template-columns: 70mm 1fr` with a negative
  20mm margin to pull content to page edges under default @page
  margins (20mm).
- Sidebar typography helpers (h3 styling) are scoped to
  `.katib-cv-layout__sidebar` so consumer HTML can use plain `<h3>`
  and `<section>` tags.
- Nested `skill-bar-list` and `tag-chips` primitives get sidebar-
  scoped color overrides so their colors invert against the dark bg.

## Page Margin Handling

CV expects a full-page 2-column layout with the sidebar edge-to-edge.
This component uses `margin: -20mm` on the grid to negate the default
page margins. Recipe authors can also set `@page { margin: 0 }` at
the recipe level for complete control — but the negative-margin
approach keeps the recipe schema stable.

## Accessibility Notes

- Root element is `<section>` with `lang` and `dir` attributes.
- Sidebar is semantic `<aside>` (secondary content).
- Main is semantic `<main>` (primary document content).
- Content in both slots is caller-supplied raw HTML — caller is
  responsible for semantic heading hierarchy and accessibility of
  nested content.

## Token Contract

- `text`, `text_secondary`, `text_tertiary` — main-column text hierarchy
- `accent` — sidebar background
- `accent_on` — sidebar foreground (inverts against accent bg)
- `border` — dividers and rules

## Related Components

- Hosts `skill-bar-list` and `tag-chips` primitives in the sidebar.
- Designed specifically for `personal-cv` recipe; future reuse
  expected for portfolio + profile page templates (both Deferred in
  Phase 3).
