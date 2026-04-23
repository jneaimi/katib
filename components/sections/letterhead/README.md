# letterhead

**Tier:** section

## Purpose

Two-column header strip that sits above body content on page 1 of a document. Brand/company on the leading side; meta stack (doc title + reference code + date + custom lines) on the trailing side. Bottom accent rule separates it from the body.

Use for **letters, NOCs, invoices, quotes, MoUs** and similar documents where page 1 needs organizational identity and a reference block, but not a full title page.

**Distinct from `front-matter`:** use `front-matter` when you need a full title page (it declares `break_after: always` and consumes the whole page). Use `letterhead` when you need a header strip that leaves room for body content on the same page.

## Variants

- **default** — business letter: 0.75pt accent bottom rule, company name in accent color
- **formal** — NOC, legal doc: 1.25pt text-color rule, uppercased austere company name, uppercased doc-title
- **commercial** — invoice, quote: large accent doc-title on trailing side, company name in body text color, top-aligned for taller meta blocks

## Inputs

- `company` (string, required): organization name shown on the leading side
- `reference_code` (string, optional): short document ref, rendered in monospace
- `date` (string, optional): free-form issue date (caller formats per locale)
- `meta_lines` (array of strings, optional): extra lines below date — e.g., "Strictly Confidential"
- `doc_title` (string, optional): document-class label — "INVOICE", "QUOTE", "NO OBJECTION CERTIFICATE". Used primarily by `commercial` and `formal` variants.

## Usage Example

Letter header:

```yaml
- component: letterhead
  inputs:
    company: "jasem | katib"
    reference_code: "KATIB-2026-001"
    date: "23 April 2026"
```

Invoice header:

```yaml
- component: letterhead
  variant: commercial
  inputs:
    company: "JNEAIMI CONSULTING"
    doc_title: "INVOICE"
    reference_code: "INV-2026-042"
    date: "23 April 2026"
    meta_lines:
      - "Due: 30 days from issue"
```

NOC header:

```yaml
- component: letterhead
  variant: formal
  inputs:
    company: "Arabian Holdings LLC"
    doc_title: "NO OBJECTION CERTIFICATE"
    reference_code: "NOC/2026/042"
    date: "23 April 2026"
```

## Accessibility Notes

- Semantic `<header>` inside the section wrapper
- Root element carries `lang` / `dir` attributes; RTL flips the flex direction so the leading side stays on the visual start
- `reference_code` is forced `dir="ltr"` in Arabic templates (codes are left-to-right even in Arabic documents)
- All colors resolve via tokens (`--accent`, `--text`, `--text-secondary`, `--text-tertiary`) — zero hex in the stylesheet

## Brand fields

- `logo.primary` → rendered above the bar if the active brand profile defines it, constrained to `logo.max_height_mm` (default 18mm)

## When NOT to use

- **Title pages** — use `front-matter` instead (full-page, `break_after: always`)
- **Centered document headers** (MoU-style) — this component is 2-column; centered openers may need a different section
- **Repeating body content** — use `module`
