# module

**Tier:** section

## Purpose

Flexible body unit — the backbone of a multi-section document. Shows an optional number, eyebrow category, heading, intro paragraph, and freeform body content.

**Since 0.3.0:** the title is optional. A module with only `raw_body` (no eyebrow/title/intro) renders as pure continuous prose — use this for letter bodies, abstract paragraphs, legal recitals, or any section where a heading is not appropriate.

## Variants

| Variant | Look |
|---|---|
| `plain` (default) | Eyebrow + h2 + intro + body |
| `numbered` | Large accent-colored digit to the leading side of the heading block |

## Inputs

| Name | Type | Required | Notes |
|---|---|---|---|
| `number` | int | no | Rendered prominently in `numbered` variant only |
| `eyebrow` | string | no | Category label like "Module 1 · Foundations" |
| `title` | string | no | Module heading. Optional since 0.3.0 — omit for continuous prose |
| `intro` | string | no | Paragraph under the title |
| `body` | string | no | Auto-escaped plain-text body — safe for any source |
| `raw_body` | string | no | Trusted HTML body (tables, SVG, callouts) — takes precedence over `body` |

## Usage Example

With heading (most common — tutorials, guides, reports):

```yaml
- component: module
  variant: numbered
  inputs:
    number: 1
    eyebrow: "Module 1 · Foundations"
    title: "Get set up"
    intro: "Before you can do anything, you need a working environment."
    body: "Instructions here..."
```

Without heading (continuous prose — letter bodies, abstracts, recitals):

```yaml
- component: module
  inputs:
    raw_body: |
      <p>Dear Ms. Al-Hashimi,</p>
      <p>Thank you for the opportunity to present our proposal...</p>
      <p>Kind regards,</p>
```

## Composition pattern

A `module` does **not** contain its own objectives — recipes compose `module` + `objectives-box` + other sections as siblings:

```yaml
- component: module
  variant: numbered
  inputs:
    number: 1
    title: "Get set up"
    intro: "Before you can do anything, you need a working environment."
- component: objectives-box
  inputs:
    items:
      - "Install and verify the tool"
      - "Authenticate against the shared service"
```

## Composes

- `.katib-eyebrow` · `.katib-eyebrow--accent`
- Built-in `<h2>` + `<p>` page-shell styles

## Accessibility Notes

- When `title` is set, it emits a semantic `<h2>` — screen readers announce section structure
- When `title` is unset (continuous prose mode), only `<p>` elements emit — appropriate for body prose
- All colors resolve via tokens (`--text`, `--text-secondary`, `--accent`, `--border`)

## Page behaviour

- `break_before: auto`, `break_inside: auto` — modules can span pages naturally. Add a `rule` primitive between modules if you want a visible divider.
