# references-list

**Tier:** section

## Purpose

Numbered bibliography section at the end of a document. Pairs with the
`citation` primitive — each entry corresponds to a `[N]` marker in the
document body. Supports multiple reference shapes (authors, year,
title, source, URL) rendered in a minimal-common style.

## Variants

| Variant | When to use |
|---|---|
| `default` | Standard density — good for most docs. |
| `compact` | Tighter leading + smaller font — for long reference lists (>20 entries). |

## Inputs

| Input | Type | Required | Notes |
|---|---|---|---|
| `title` | string | no | Section heading. Defaults to `"References"` (EN) / `"المراجع"` (AR). |
| `entries` | array | **yes** | Ordered list of references. Each entry is `{authors, year, title, source, url}` — all fields optional per entry. Order here defines the `[N]` number in citations. |

## Usage Example

```yaml
- component: references-list
  inputs:
    title: "References"
    entries:
      - authors: "Al Neaimi, J."
        year: 2026
        title: "Bilingual print for the AI era"
        source: "Katib internal notes"
      - authors: "W3C"
        year: 2024
        title: "CSS Paged Media Module Level 3"
        source: "w3.org/TR/css-page-3"
        url: "https://www.w3.org/TR/css-page-3/"
      - authors: "CourtBouillon"
        year: 2025
        title: "WeasyPrint documentation"
        source: "doc.courtbouillon.org"
        url: "https://doc.courtbouillon.org/weasyprint/"
```

Corresponding citation in the body:

```yaml
- component: module
  inputs:
    title: "Method"
    raw_body: |
      We use CSS Paged Media Level 3 <sup class="katib-citation">[2]</sup>
      via WeasyPrint <sup class="katib-citation">[3]</sup>.
```

## Accessibility Notes

- Uses semantic `<ol>` for the numbered list — screen readers read the
  entry numbers correctly.
- Entries carry `page-break-inside: avoid` so they don't split across
  pages.
- Arabic variant shifts list markers and padding to the right edge,
  switches italic title-text to bold (italic is meaningless in Arabic).
