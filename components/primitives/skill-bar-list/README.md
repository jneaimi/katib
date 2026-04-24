# skill-bar-list

**Tier:** primitive

## Purpose

Skill/proficiency list with named items and visual level bars on a 1-5
scale. Each item renders as a name label + horizontal bar filled to a
level-driven percentage (l1=20% through l5=100%).

Used in CV sidebar Languages + Core Skills sections; future reuse for
portfolio skill displays and bio proficiency matrices.

## Variants

- default (the only shape — no variants needed; bar style is stable)

## Inputs

- `items` (array, required): Array of `{name, level}` mappings.
  - `name` (string, required): skill label
  - `level` (int 1-5, required): proficiency level driving the bar fill
    percentage

## Usage Example

```yaml
- component: skill-bar-list
  inputs:
    items:
      - {name: "English", level: 5}
      - {name: "Arabic", level: 5}
      - {name: "Python", level: 4}
      - {name: "TypeScript", level: 3}
```

## Rendering

- `<ul class="katib-skill-bar-list">` with `list-style: none`.
- Each `<li>` contains a name `<span>` + a level `<span>` with
  modifier class `--l1` through `--l5` controlling fill width.
- Fill is rendered via `::after` pseudo-element with
  `position: absolute` — language-scoped selectors flip `left: 0`
  under LTR and `right: 0` under RTL so bars fill from the leading
  edge.

## Accessibility Notes

- Root element is `<ul>` with `lang` and `dir` attributes.
- Level bars are visual-only (`::after` content); the skill name is
  the full readable content for screen readers.
- Each `<li>` declares `page-break-inside: avoid`.

## Token Contract

- `text` — skill name color
- `accent` — bar fill color
- `accent_on` — reserved for future inverted-sidebar rendering
- `border` — unfilled bar track color

## Related Components

- Used within `cv-layout` sidebar content for Languages + Core Skills.
- Complements `tag-chips` (Tools/tags) in personal-domain primitives.
