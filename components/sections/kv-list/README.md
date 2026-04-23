# kv-list

**Tier:** section

## Purpose

Renders a list of `term` + `value` pairs as a two-column grid. Use for glossaries, quick-reference pairs, metadata summaries, definition blocks, legal-style defined terms, and cheat-sheet-style compact reference lists.

Not for tabular data with >2 columns — use a `module` with `raw_body` holding a `<table>` for that. kv-list is optimized for the case where the first column is a short fixed-width label (a term) and the second is a one-or-two-line explanation.

## Variants

- **default** — balanced row spacing, 10pt text, suitable for reference or meta lists
- **dense** — tight spacing, 9pt text, for cheat-sheets and quick-scan lookup
- **spacious** — generous spacing, 10.5pt text, for formal definitions and legal glossaries

## Inputs

- `items` (array, required): list of `{term, value}` mappings; both fields are plain strings
- `heading` (string, optional): heading above the grid
- `eyebrow` (string, optional): small preheader above the heading

## Usage Example

```yaml
- component: kv-list
  variant: spacious
  inputs:
    eyebrow: Defined Terms
    heading: Interpretation
    items:
      - term: "Agreement"
        value: "This Memorandum of Understanding and any schedules attached."
      - term: "Effective Date"
        value: "The date of the last signature below."
      - term: "Party"
        value: "Either signatory; together, the Parties."
```

Dense cheat-sheet example:

```yaml
- component: kv-list
  variant: dense
  inputs:
    heading: Git shortcuts
    items:
      - term: "git status"
        value: "Working tree + staged changes"
      - term: "git log --oneline"
        value: "Condensed commit history"
      - term: "git diff --cached"
        value: "Staged changes vs HEAD"
```

## Accessibility Notes

- Uses semantic `<dl>` / `<dt>` / `<dd>` — screen readers announce as a description list
- Root element carries `lang` / `dir` attributes; Arabic renders RTL automatically
- Border-bottom separates rows for visual scanning; trailing border stripped from last row
- All colors resolve via tokens (`--text`, `--text-secondary`, `--border`) — no hex in the stylesheet
