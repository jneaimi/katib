# objectives-box

Labeled bullet list — "What you'll learn", "Module objectives", "In scope".

## Variants

| Variant | Look |
|---|---|
| `boxed` (default) | Tinted background + accent rule on leading edge |
| `minimal` | No background, no border — just label + list |

## Inputs

| Name | Type | Required | Default |
|---|---|---|---|
| `label` | string | no | `"What you'll learn"` (EN) · `"ما ستتعلمه"` (AR) |
| `items` | array<string> | yes | — |

## Usage

```yaml
- component: objectives-box
  variant: boxed
  inputs:
    label: "In this module"
    items:
      - "Install and verify the core tool"
      - "Authenticate against the shared service"
      - "Run a smoke command that confirms everything is reachable"
```

## Composes

- No primitives — this is a self-contained section with its own list.

## Accessibility

- Label is a `<div>` not a `<h3>` — it's a visual hint, not a navigable heading. Use objectives-box alongside module headings, not as a substitute for them.
