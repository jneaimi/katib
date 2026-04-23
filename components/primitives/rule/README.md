# rule

Horizontal divider between content blocks.

## Variants

| Variant | Rendered as |
|---|---|
| `hairline` | 1px line in `--border` |
| `strong` (default) | 1px line in `--border-strong` |
| `double` | two 1px lines stacked (3px overall) |

## Inputs

None.

## Usage

```yaml
- component: rule
  variant: hairline
```

## Accessibility

Renders as a native `<hr>`, announced as "separator" by screen readers.
