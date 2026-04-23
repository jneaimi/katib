# whats-next

Forward-pointing call-to-action list. Lives at the end of a document, just before `reference-strip`.

## Variants

| Variant | Look |
|---|---|
| `bullet` (default) | Unordered list with standard bullets |
| `numbered` | Accent-filled numbered circles (reuses `--step-circle-*` tokens) |

## Inputs

| Name | Type | Required | Default |
|---|---|---|---|
| `eyebrow` | string | no | `"Next"` (EN) · `"التالي"` (AR) |
| `heading` | string | no | `"What's next"` (EN) · `"الخطوات التالية"` (AR) |
| `items` | array | yes | — |

`items` accepts either:
- plain strings → rendered as bullets
- objects `{title, description}` → bolded title + em-dash + description

## Usage

```yaml
- component: whats-next
  variant: numbered
  inputs:
    items:
      - title: "Review the cheatsheet"
        description: "Keyboard-first shortcuts"
      - title: "Pair with a teammate"
        description: "Solidify your mental model on a real task"
      - "Skim the reference docs"
```

## Composes

- `.katib-eyebrow` · `.katib-eyebrow--accent`
- `--step-circle-bg` / `--step-circle-fg` tokens (via numbered variant)

## Accessibility

- `<h2>` heading for navigation
- Proper `<ol>` / `<ul>` semantics preserved — numbered markers are CSS pseudo-elements, not content
