# signoff-block

**Tier:** section

## Purpose

Fill-in sign-off block for proposals and contracts. Renders one or more party cards, each with a label and a list of fields that are either printed (label plus value) or blank ruled lines to write on; an optional company-stamp box. Use for a Prepared-by sign-off and for Client and Provider acceptance grids.

## Variants

- default

## Inputs

- `title` (string, required): …

## Usage Example

```yaml
- component: signoff-block
  inputs:
    title: "Example title"
```

## Accessibility Notes

- Root element carries `lang` / `dir` attributes
