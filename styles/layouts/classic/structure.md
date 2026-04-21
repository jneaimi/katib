# Classic Layout — Structure Contract

The `classic` layout is the default interior rhythm for business-proposal, formal, and personal domains. Used for proposals, letters, and standard one-pagers.

## Section order (required)

1. **Cover** — full-bleed, zero margins, cover style fragment injected
2. **Signature** — signer details + optional signature image, standard margins (business-proposal only)
3. **Body** — content with standard margins, header + footer with page numbers

Omit sections not in the domain's `sections_required` (see `domains/<domain>/styles.json`).

## Required CSS tokens (from domain `tokens.json` → injected as `:root` custom properties)

| Token | Semantic role |
|---|---|
| `--page-bg` | Page background color |
| `--accent` | Primary brand color (headings, H1 bar, table headers, links) |
| `--accent-2` | Secondary accent (optional highlights, tags) |
| `--accent-on` | Readable text color on accent background |
| `--text` | Main body text |
| `--text-secondary` | H3 / captions / secondary text |
| `--text-tertiary` | Page numbers, meta, footer |
| `--border` | Table borders, dividers |
| `--border-strong` | Strong dividers, strong borders |
| `--tag-bg`, `--tag-fg` | Inline tags / callout chips |
| `--font-primary` | Body font stack |
| `--font-display` | Heading / display font stack (can equal primary) |

## Page configuration

```css
@page {
  size: A4;
  margin: {domain.page.margins_mm.{doc-type}};
  @top-right { content: "{reference_code}  |  CONFIDENTIAL"; font-size: 8pt; color: var(--text-tertiary); }
  @bottom-center { content: "{brand} | Page " counter(page) " of " counter(pages); font-size: 8pt; color: var(--text-tertiary); }
}

@page :first {
  margin: 0;
  @top-right { content: none; }
  @bottom-center { content: none; }
}
```

## Page numbering

| Section | Rule |
|---|---|
| Cover | Hidden (no page number) |
| Signature | Hidden (start counter at 0) |
| Body | Start at 3 for business-proposal (covers title + signature spreads); overridable via `domain.tokens.json → page_numbering.body_start_at` |

## RTL handling

- `<html lang="ar" dir="rtl">` flips all inline flow automatically
- H1 left-bar → right-bar (handled in `body.css`)
- Page `@top-right` stays top-right in both directions — it's a physical corner, not a reading-order position
- For AR docs, `@top-right` may contain the EN reference code; the **content** reads AR but the **corner metadata** stays in EN for archival consistency

## Typography contracts

- Base body: 10.5pt EN / 11pt AR, line-height 1.55 EN / 1.65 AR
- H1: 22pt, line-height 1.2 EN / 1.3 AR, margin-top 32pt
- Consecutive headings collapse margins (H1 → H2 uses H2's margin-top, not sum)
- Page break before H1 only when explicitly requested (`.page-break` class or `page-break-before: always` on the H1)

## Widows & orphans

- All paragraphs: `orphans: 2; widows: 2;`
- Tables: `page-break-inside: auto` with `thead { display: table-header-group }` for header repeat on break
- Rows: `page-break-inside: avoid`
- Code blocks: `page-break-inside: avoid`
- Figures: `page-break-inside: avoid`

## Forbidden patterns

- **No `rgba()` on tag or callout backgrounds** — WeasyPrint bug, use flat hex from `design.{lang}.md` conversion table
- **No `letter-spacing` on Arabic** — breaks cursive ligatures
- **No `height: 100vh`** in `@page` — use explicit mm
- **No `break-inside: avoid` directly inside flex** — wrap in a block container first
- **No hard drop shadows** — rings or whispers only

## Composition — how covers plug in

1. Build reads `styles/covers/<cover-style>/cover.html` — an HTML fragment with title/subtitle/reference-code placeholder `{{title}}`, `{{subtitle}}`, `{{ref_code}}`
2. Cover fragment is injected as the first child of `<body>` and wrapped in a cover-specific `@page :first` rule
3. Cover CSS comes from `styles/covers/<cover-style>/cover.css` (or inline `<style>` inside cover.html)
4. Body content starts after the cover's explicit `page-break-after: always`

## Testing contract

`build.py --verify <target>` checks:

- Generated PDF page count ≤ `doc_type.page_limit`
- Required sections present (per `styles.json`)
- No `rgba()` in compiled CSS
- No `letter-spacing` on `[lang="ar"]` selectors
- Every `<pre>` / `<code>` has `dir="ltr"`
- All `{{placeholder}}` tokens have been substituted
