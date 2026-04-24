# clause-list

**Tier:** primitive

## Purpose

Numbered legal-clause list — an ordered list with counter-based decimal
numbering rendered prominently in the accent color. Serves MoU clauses,
NDA provisions, service-agreement sections, and any legal-body structure
where clause references must be visually distinct.

Replaces the Day-0 `recitals-block` plan. The original plan assumed a
WHEREAS-clause preamble shape, but v1 evidence across the legal domain
(mou 7×, nda 7×, service-agreement 10×, engagement-letter 1×) shows the
actual shape is numbered-clause ordered lists.

## Variants

- default (the only shape — no variants needed; list density is stable across legal docs)

## Inputs

- `items` (array, required): Array of clause strings. Each item becomes a
  numbered `<li>` with the counter rendered in the accent color on the
  leading side (left under LTR, right under RTL). Items can be strings or
  `{text}` mappings for consistency with other primitives.
- `start` (int, optional): Starting counter value (default 1). Use to
  continue numbering across split clause-lists (rare — most sections
  reset the counter).

## Usage Example

```yaml
- component: clause-list
  inputs:
    items:
      - "Any non-public information exchanged shall be treated as confidential."
      - "Neither Party shall disclose such information to any third party without prior written consent."
      - "Confidentiality obligations survive termination for a period of two (2) years."
```

## Rendering

- `<ol class="katib-clause-list">` with `list-style: none` and custom
  CSS counter (`counter-increment: clause`).
- Numbers render via `::before` with `position: absolute`, decimal format,
  accent color, bold weight.
- RTL: lang-scoped physical properties flip the number position from the
  left padding to the right. No logical-property reliance (WeasyPrint
  has known gaps with `padding-inline-start` in `::before` contexts).

## Accessibility Notes

- Root element is `<ol>` with `lang` and `dir` attributes.
- Numbers are visual-only (`::before` content); screen readers read the
  `<ol>` natively as an ordered list.
- Each `<li>` declares `page-break-inside: avoid` to prevent clause
  splitting across pages.

## Token Contract

- `text` — clause body color
- `accent` — counter number color

## Related Components

- Used alongside `module numbered` (provides the §N heading + intro) in
  MoU-style legal documents.
- Part of the legal domain primitive set (data-table for tabular data,
  clause-list for numbered clauses, callout for notices).
