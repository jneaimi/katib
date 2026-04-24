# appendix-page

## Purpose

Appendix content with a distinct running header. The `label` input
(e.g. "Appendix A") is repeated in the top-right margin of every page
the appendix spans, so the reader never loses track of which section
they're reading. Flows across as many pages as needed — appendix
material is usually long-form (raw data, transcripts, derivations,
references).

## How it works

Uses the CSS Generated Content for Paged Media pattern:

1. A `<div class="katib-appendix__running-label">Appendix A</div>` at
   the top of the section is promoted into the `@top-right` margin box
   via `position: running(appendix-label)`.
2. Every page inside the appendix inherits `page: appendix`, so every
   one of those pages shows the running label.
3. Pages outside the appendix go back to the default `@page` rule with
   no running header.

## Inputs

| Input | Type | Required | Notes |
|---|---|---|---|
| `label` | string | no | Running header text. Defaults to `"Appendix"` (EN) or `"ملحق"` (AR). Use `"Appendix A"`, `"Appendix B"` etc. for multi-appendix docs. |
| `eyebrow` | string | no | Small label above the appendix title on the opening page. |
| `title` | string | **yes** | The appendix title. |
| `intro` | string | no | Short paragraph under the title. |
| `raw_body` | string | **yes** | Trusted HTML — tables, code, long prose. Flows across pages. |

## Example — multiple appendices in one document

```yaml
- component: appendix-page
  inputs:
    label: "Appendix A"
    eyebrow: "SOURCE MATERIAL"
    title: "Raw Interview Transcripts"
    intro: |
      Full transcripts from the twelve interviews referenced in
      Chapter 3. Anonymized per consent protocol.
    raw_body: |
      <h3>Interview 01 · 2026-02-14</h3>
      <p>...</p>

- component: appendix-page
  inputs:
    label: "Appendix B"
    title: "Technical Derivations"
    raw_body: |
      <h3>B.1 — Shadow resolution algorithm</h3>
      <pre>...</pre>
```

## Notes

- Uses WeasyPrint's `position: running(name)` + `@top-right { content:
  element(name) }` pattern for the running header.
- The label is injected from the input, not hardcoded — one component,
  many appendices.
- `page_behavior: flowing` — the appendix can span multiple pages
  without forcing atomic page breaks inside.
- `break_before: always` — each appendix starts on a fresh page.
