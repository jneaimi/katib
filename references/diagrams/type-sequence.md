# Sequence

**Best for:** request/response flows, protocol exchanges, multi-actor interactions over time, API call traces, incident reconstructions.

## Layout conventions

- Actors as rectangular boxes in a horizontal row at the top.
- **Lifelines:** dashed vertical lines descending from each actor to the bottom.
- Messages: horizontal arrows between lifelines. **Time flows top→down** (never mirrored for AR).
- **Activation bar:** narrow rectangle (`w=8`, muted fill, 0.8 hairline stroke) on a lifeline spanning the interval that actor holds control. Stack for nested calls.
- **Self-messages:** short U-shaped loop returning to the same lifeline; label right of the loop.
- **Return messages:** dashed line in the same color as the originating call.
- `colors.accent` on the primary success response or headline message — one, maybe two.

## Lifeline primitive

```html
<line x1="CX" y1="TOP" x2="CX" y2="BOTTOM"
      stroke="{{ colors.text_secondary }}" stroke-width="1"
      stroke-dasharray="3,3" opacity="0.5"/>
```

## Activation bar primitive

```html
<rect x="CX-4" y="TOP" width="8" height="H"
      fill="{{ colors.text }}" opacity="0.06"
      stroke="{{ colors.text_secondary }}" stroke-width="0.8"/>
```

## Actor box

Standard node-box pattern from [primitives.md](primitives.md), placed at the top of each lifeline:

```html
<rect x="X" y="16" width="120" height="40" rx="6"
      fill="{{ colors.page_bg }}"
      stroke="{{ colors.text }}" stroke-width="1"/>
<text x="X+60" y="40" fill="{{ colors.text }}" font-size="12" font-weight="600"
      text-anchor="middle" font-family="inherit">Client</text>
```

## Message arrow

```html
<!-- Request -->
<line x1="120" y1="Y" x2="280" y2="Y"
      stroke="{{ colors.text_secondary }}" stroke-width="1"
      marker-end="url(#arrow)"/>
<rect x="182" y="Y-12" width="36" height="12" rx="2" fill="{{ colors.page_bg }}"/>
<text x="200" y="Y-3" fill="{{ colors.text_tertiary }}" font-size="8"
      font-family="ui-monospace, monospace" text-anchor="middle"
      letter-spacing="0.06em">POST /login</text>

<!-- Return (dashed) -->
<line x1="280" y1="Y+40" x2="120" y2="Y+40"
      stroke="{{ colors.text_secondary }}" stroke-width="1"
      stroke-dasharray="5,4" marker-end="url(#arrow)"/>
```

## Bilingual

- Actor names (user/api/database) can stay in SVG if they're English identifiers.
- Descriptive Arabic actor names (`المستخدم`, `الخادم`) go in `.diagram-label` overlays.
- Message labels (`POST /login`, `200 OK`) stay in SVG — they're technical protocol text.
- **Don't mirror** sequence diagrams for AR — time flows top→down universally and actors align left-to-right regardless of reading direction.

## Anti-patterns

- Message arrow pointing **upward** (reverses time — never).
- Activation bars that never close.
- Labels sitting over another lifeline — shorten or shift y into a gap.
- Swimlane-style lanes instead of lifelines (different grammar — see [type-swimlane.md](type-swimlane.md)).
- More than 5 lifelines — split into "login flow" + "checkout flow" etc.
