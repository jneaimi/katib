# citation

**Tier:** primitive

## Purpose

Inline numbered citation marker — superscript `[N]` that points at a
matching entry in the `references-list` section at the end of the
document. For academic, editorial, legal, and any doc where
attribution matters.

## Inputs

| Input | Type | Required | Notes |
|---|---|---|---|
| `number` | int | **yes** | The citation number. Matches the order in the references-list. |
| `ref` | string | no | Optional slug for future anchor/hyperlink support. Unused at render today. |

## Usage

Most often embedded inline in a `raw_body` string via literal `<sup>`
tags — but when you want token-driven styling consistent with the
rest of the document, use the component:

```yaml
- component: module
  inputs:
    title: "Findings"
    raw_body: |
      Early trials showed a 34% improvement in reading speed
      <sup class="katib-citation">[1]</sup> — a result later replicated
      in the 2025 multi-site study <sup class="katib-citation">[2]</sup>.
```

In practice, the `<sup class="katib-citation">[N]</sup>` markup is
inlined directly in `raw_body` strings since Jinja components can't
interpolate into arbitrary text positions. The component acts as the
canonical CSS source for the inline markup.

## Accessibility Notes

- Superscript rendering preserves baseline alignment with surrounding
  text.
- Arabic RTL context: the `[N]` marker keeps LTR semantics since
  numerals are rendered left-to-right inside Arabic sentences anyway.
