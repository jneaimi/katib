# sections-grid

**Tier:** section

## Purpose

Titled-card grid — N cards in 2, 3, or 4 columns. Each card has a title and either plain-text body or trusted HTML. Serves:

- Cheatsheet sections (6 cards with kv lists or keyboard-shortcut ul's)
- One-pager body grids (2x2 peer sections)
- Contact-card grids (role + name + contact-line, bordered variant)
- Any "group of peer sections" layout

## Variants

- `default` — 2-col (or N-col via `columns`), no borders, loose gap
- `dense` — tighter gap + smaller typography, fits 6+ cards per page (cheatsheet)
- `bordered` — each card has a thin border + padding (contact-card-style visual separation)

## Inputs

- `eyebrow` (string, optional) — grid-level category label above the heading
- `heading` (string, optional) — grid-level h2/h3 (many grids have none; cards carry the structure)
- `columns` (int, optional) — 2 (default), 3, or 4
- `items` (array, required) — card objects:
  - `title` (string, required) — card h3
  - `body` (string, optional) — plain-text body (auto-escaped)
  - `raw_body` (string, optional) — trusted HTML body (takes precedence over `body`)
  - `eyebrow` (string, optional) — small uppercase label above the card title (role labels on contact cards)

## Usage Examples

### Cheatsheet — 6 cards, dense, `<dl>` / `<ul>` in raw_body

```yaml
- component: sections-grid
  variant: dense
  inputs:
    columns: 2
    items:
      - title: "Quick actions"
        raw_body: |
          <dl class="kv"><dt>⌘K</dt><dd>Quick-create</dd>
          <dt>⌘/</dt><dd>Global search</dd></dl>
      - title: "Navigation"
        raw_body: |
          <dl class="kv"><dt>g h</dt><dd>Go home</dd></dl>
```

### One-pager — 2x2 body grid, plain-text bodies

```yaml
- component: sections-grid
  inputs:
    columns: 2
    items:
      - title: "Program scope"
        body: "Full-stack AI engineering curriculum..."
      - title: "Delivery model"
        body: "Hybrid split — 2 groups of 9..."
```

### Contacts — bordered cards with role eyebrows

```yaml
- component: sections-grid
  variant: bordered
  inputs:
    columns: 2
    items:
      - eyebrow: "Handing off"
        title: "Outgoing owner"
        body: "Available for 30 days"
```

## Accessibility Notes

- Root `<section>` carries `lang` / `dir` attributes
- Each card is an `<article>` with an `<h3>` title — readable linear order under screen readers even when visually gridded
- Cards are `page-break-inside: avoid` so they don't split across pages

## WeasyPrint constraints

- Column count is explicit (`repeat(2, 1fr)`, not `auto-fit`) — WeasyPrint doesn't support `auto-fit`/`auto-fill` in `repeat()` (see Day 7 ADR).
- No logical-property shortcuts (`border-inline-start` unsupported) — the component has no directional borders so RTL works without CSS overrides.
