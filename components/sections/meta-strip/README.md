# meta-strip

## Purpose

Horizontal row of small badges sitting directly under a title. Lets the reader triage a tutorial, recipe, or briefing before committing — `Time · Difficulty · Yield · Stack`.

## When to use

- Top of a tutorial, sitting under the cover or between cover and outcome-preview
- Top of a recipe-card spread (yield · active time · total time · difficulty)
- Top of a course module handout (level · units · time)
- Top of a procurement-ready briefing (when readers want to know "is this for me?" in 2 seconds)

## Inputs

```yaml
- component: meta-strip
  variant: outline   # outline (default) | solid | minimal
  inputs:
    align: start     # start (default) | center | space-between
    items:
      - label: "Time"
        value: "15 min"
      - label: "Difficulty"
        value: "Beginner"
      - label: "Yield"
        value: "1 working integration"
        icon: "→"    # optional short glyph
```

## Variants

- **outline** (default) — each item rendered as a small chip with a thin border. Best for procurement / formal contexts.
- **solid** — tag-tinted background, accent-coloured label. Best for editorial / hero contexts.
- **minimal** — no chip; items are inline, separated by a middle dot. Best for dense magazine-style headers.

## Bilingual notes

- AR removes the Latin uppercase + letter-spacing on `label` (Arabic doesn't shape well at small uppercase tracked sizes) and bumps font weight to 700 to compensate.
- The strip flows RTL automatically via `dir="rtl"` on the `<section>`. `align: space-between` honours logical (not physical) start/end.
- The `minimal` variant's middle-dot separator flows correctly in both directions because it uses adjacent-sibling positioning.

## Pedagogy

Source pattern: Microsoft Learn module headers ("Level: Beginner / 8 Units"), cookbook yield+time line, recipe schema structured data, merit-badge difficulty letter. Sits at the front of an instructional artifact to honour Mayer's pre-training principle — the reader knows what they're committing to before they invest attention.

## Companion components

- `outcome-preview` — the visual pair to this strip (text-meta + image-target sit together at the top of a tutorial)
- `objectives-box` — the bullet companion ("by the end you will…") that complements meta data with scope
- `prerequisites-grid` — the gating list that follows the meta strip and outcome preview

Part of the Tutorial Component Pack — Sprint 1 / Phase A.
