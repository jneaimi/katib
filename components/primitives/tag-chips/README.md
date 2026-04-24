# tag-chips

**Tier:** primitive

## Purpose

Inline tag-pill list — rounded rectangular chips for tags, tools,
technologies, keywords, or topics. Items render as inline-block pills
with accent-muted background and small-font semi-bold text.

Used in CV Tools section; future reuse for bio/portfolio skill lists,
blog post keywords, editorial metadata tags.

## Variants

- default (the only shape — no variants needed; chip style is stable)

## Inputs

- `items` (array, required): Array of tag strings. Items can be strings
  or `{text}` mappings for primitive consistency with clause-list and
  data-table.

## Usage Example

```yaml
- component: tag-chips
  inputs:
    items:
      - "Python"
      - "TypeScript"
      - "PostgreSQL"
      - "Docker"
```

## Rendering

- `<ul class="katib-tag-chips">` with `list-style: none` and
  `font-size: 0` to eliminate inline-block whitespace gaps.
- Each `<li class="katib-tag-chips__chip">` is inline-block with
  rounded corners, tag-bg background, accent-weighted font.
- RTL: chip trailing-margin flips so gaps appear on the correct side.

## Accessibility Notes

- Root element is `<ul>` with `lang` and `dir` attributes.
- Each chip is a semantic `<li>` — screen readers read the tag list as
  an ordered collection.
- Chips declare `page-break-inside: avoid`.

## Token Contract

- `text` — chip text color
- `accent` — reserved for future accent-variant chips
- `accent_on` — reserved for accent-variant rendering
- `tag_bg` — chip background color

## Related Components

- Used within `cv-layout` sidebar for the Tools section.
- Complements `skill-bar-list` (Languages/Core Skills) in
  personal-domain primitives.
