# toc

**Tier:** section

## Purpose

Table of contents — entry label + dotted leader + page number. The
recipe provides explicit entries rather than auto-generating from
headings in the document, because recipes know their own structure
(part numbers, appendix labels, non-heading milestones) better than
any introspection pass could.

Supports up to 3 nesting levels via `level` — level 1 is bold, level 2
is indented, level 3 is further indented and muted.

## Variants

| Variant | When to use |
|---|---|
| `default` | Clean — title with underline, entries below. |
| `bordered` | Full box around the TOC — good for presentation docs, executive summaries. |

## Inputs

| Input | Type | Required | Notes |
|---|---|---|---|
| `title` | string | no | Section heading. Defaults to `"Contents"` (EN) / `"المحتويات"` (AR). |
| `entries` | array | **yes** | Each entry is `{label, page, level}`. `level` is 1/2/3 (default 1). `page` is string or int. |

## Usage Example

```yaml
- component: toc
  variant: default
  inputs:
    entries:
      - label: "Executive Summary"
        page: 1
        level: 1
      - label: "Part I — Context"
        page: 3
        level: 1
      - label: "Market overview"
        page: 4
        level: 2
      - label: "Competitive landscape"
        page: 8
        level: 2
      - label: "Part II — Approach"
        page: 12
        level: 1
      - label: "Methodology"
        page: 13
        level: 2
      - label: "Appendix A — Raw data"
        page: "A-1"
        level: 1
```

## Accessibility Notes

- Semantic `<ul>` for the entry list.
- Dotted leader is pure CSS border — doesn't appear in screen-reader
  output.
- Arabic variant: title-underline flips across to Arabic-glyph-safe
  typography; level indentation flips to right side.
- `page-break-inside: avoid` on each entry keeps lines atomic across
  page breaks (important when the TOC spans >1 page).
