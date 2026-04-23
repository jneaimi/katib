# module

Repeating body unit — the backbone of a multi-section document. Shows an optional number, eyebrow category, heading, intro paragraph, and freeform body content.

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
| `title` | string | yes | The module heading |
| `intro` | string | no | Paragraph under the title |
| `body` | string | no | Freeform HTML/text content |

## Composition pattern

A `module` does **not** contain its own objectives — recipes compose `module` + `objectives-box` + other sections as siblings:

```yaml
- component: module
  variant: numbered
  inputs:
    number: 1
    eyebrow: "Module 1 · Foundations"
    title: "Get set up"
    intro: "Before you can do anything, you need a working environment."
- component: objectives-box
  inputs:
    label: "Module objectives"
    items:
      - "Install and verify the tool"
      - "Authenticate against the shared service"
- component: module
  variant: numbered
  inputs:
    number: 2
    eyebrow: "Module 2 · First task"
    title: "Complete a real workflow"
```

This pattern is idiomatic v2 — every section does one thing well.

## Composes

- `.katib-eyebrow` · `.katib-eyebrow--accent`
- Built-in `<h2>` + `<p>` page-shell styles

## Page behaviour

- `break_before: auto`, `break_inside: auto` — modules can span pages naturally. Add a `rule` primitive between modules if you want a visible divider.
