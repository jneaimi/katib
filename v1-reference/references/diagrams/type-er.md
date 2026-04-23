# ER / Data Model

**Best for:** database schemas, API resource relationships, domain models.

## Layout conventions

Each entity is a two-section box:

- **Header:** type tag (`ENTITY`) + entity name in brand body sans.
- **Body:** field list in monospace, one per line. PK prefixed with `#`, FK prefixed with `→`.

Relationships are lines between entities with cardinality at each end:

- `1`, `N`, `0..1`, `1..*` in monospace 8px, placed 10–12px from the entity edge.
- Optional relationship label ("has", "belongs to") centered on the line.
- Group related entities close; lay out so most relationships are straight lines, not tangles.
- `colors.accent` on the aggregate root or central entity of the model.

## Entity primitive

```html
<!-- Mask -->
<rect x="X" y="Y" width="160" height="HEIGHT" rx="6" fill="{{ colors.page_bg }}"/>

<!-- Box -->
<rect x="X" y="Y" width="160" height="HEIGHT" rx="6"
      fill="{{ colors.page_bg }}" stroke="{{ colors.text }}" stroke-width="1"/>

<!-- Header divider -->
<line x1="X" y1="Y+28" x2="X+160" y2="Y+28"
      stroke="{{ colors.border }}" stroke-width="0.8"/>

<!-- Type tag -->
<text x="X+12" y="Y+18" fill="{{ colors.text_secondary }}" font-size="7"
      font-family="ui-monospace, monospace" letter-spacing="0.14em">ENTITY</text>

<!-- Entity name -->
<text x="X+60" y="Y+18" fill="{{ colors.text }}" font-size="12" font-weight="600"
      text-anchor="start" font-family="inherit">User</text>

<!-- Fields (one per row, monospace) -->
<text x="X+12" y="Y+46" fill="{{ colors.text_secondary }}" font-size="9"
      font-family="ui-monospace, monospace"># id · uuid</text>
<text x="X+12" y="Y+62" fill="{{ colors.text_secondary }}" font-size="9"
      font-family="ui-monospace, monospace">  email · string</text>
<text x="X+12" y="Y+78" fill="{{ colors.text_secondary }}" font-size="9"
      font-family="ui-monospace, monospace">→ team_id · uuid</text>
```

## Cardinality

```html
<!-- Line -->
<line x1="160" y1="Y" x2="280" y2="Y"
      stroke="{{ colors.text_secondary }}" stroke-width="1"/>

<!-- Left cardinality (near entity 1) -->
<text x="172" y="Y-4" fill="{{ colors.text_tertiary }}" font-size="8"
      font-family="ui-monospace, monospace">1</text>

<!-- Right cardinality (near entity 2) -->
<text x="268" y="Y-4" fill="{{ colors.text_tertiary }}" font-size="8"
      font-family="ui-monospace, monospace">N</text>

<!-- Optional label (middle) -->
<rect x="206" y="Y-10" width="28" height="12" rx="2" fill="{{ colors.page_bg }}"/>
<text x="220" y="Y-1" fill="{{ colors.text_secondary }}" font-size="8"
      font-family="inherit" text-anchor="middle">has</text>
```

## Bilingual

- Field names (`id`, `email`, `team_id`) stay in SVG — they're code.
- Entity *descriptions* (if any): overlay in `.diagram-label`.
- Cardinality symbols (`1`, `N`, `0..1`) stay in SVG — they're notation, not language.

## Anti-patterns

- Drawing an arrow for every FK on a model with dozens — lay out by cluster instead.
- Inconsistent cardinality notation between ends of the same relationship.
- Fields padded to equal-height boxes — natural height by content is fine.
- More than 8 entities — split by bounded context / subsystem.
- `colors.accent` on every entity that has a lot of fields — reserve it for the root.
