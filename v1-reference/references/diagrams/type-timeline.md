# Timeline

**Best for:** release history, project milestones, incident timelines, roadmaps, changelog visualizations.

## Layout conventions

- Horizontal hairline baseline across the middle (`stroke-width="1"`, `colors.text_secondary`).
- **Tick marks** at time boundaries (quarters, months, sprints) with date labels below in monospace.
- **Events:** small filled circles (`r=4`) on the baseline. Labels alternate above and below to prevent collision, connected to the circle with a 1px hairline drop.
- **Major milestones:** `colors.accent` circle (`r=6`) + bold brand-body label.
- **Time scale must be honest:** if intervals are non-equal, space the circles non-equally. Don't fake linear spacing for aesthetics. Break the axis visibly if a region is too dense.

## Baseline

```html
<line x1="40" y1="160" x2="960" y2="160"
      stroke="{{ colors.text_secondary }}" stroke-width="1"/>

<!-- Tick marks -->
<line x1="120" y1="156" x2="120" y2="164"
      stroke="{{ colors.text_secondary }}" stroke-width="1"/>
<text x="120" y="182" fill="{{ colors.text_tertiary }}" font-size="8"
      font-family="ui-monospace, monospace" text-anchor="middle"
      letter-spacing="0.14em">Q1 2026</text>
```

## Event (below-the-line label)

```html
<circle cx="240" cy="160" r="4" fill="{{ colors.text }}"/>

<!-- Leader to label -->
<line x1="240" y1="164" x2="240" y2="200"
      stroke="{{ colors.border }}" stroke-width="0.8"/>

<text x="240" y="214" fill="{{ colors.text }}" font-size="11" font-weight="500"
      text-anchor="middle" font-family="inherit">v0.17 ships</text>
```

## Major milestone (above the line, accent)

```html
<circle cx="480" cy="160" r="6" fill="{{ colors.accent }}"/>

<line x1="480" y1="156" x2="480" y2="120"
      stroke="{{ colors.accent }}" stroke-width="0.8"/>

<text x="480" y="110" fill="{{ colors.accent }}" font-size="12" font-weight="700"
      text-anchor="middle" font-family="inherit">v1.0 Launch</text>
```

## Bilingual

- Date labels (`Q1 2026`, `Mar 2026`) stay in SVG — numeric.
- Arabic date labels (`الربع الأول`, `مارس 2026`) go in `.diagram-label` overlays.
- Mirror the baseline direction? **Yes** for AR — time in Arabic reads right→left. Use the `direction` transform from [rtl-notes.md](rtl-notes.md). Labels in overlays position correctly regardless.
- Event descriptions (e.g. "v0.17 ships" → "إصدار v0.17"): overlay.

## Anti-patterns

- Equal-spacing events that aren't equally spaced in time — dishonest.
- Missing axis labels ("what unit is this?").
- Crowded labels without vertical offset — illegible.
- `colors.accent` on every milestone — defeats the signal.
- More than 12 events on one page — split by year or quarter.
