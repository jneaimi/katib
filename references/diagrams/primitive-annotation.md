# Annotation Callout (italic-serif editorial aside)

Use for editorial asides — the "italic pointer" that marks a detail without competing with the primary diagram grammar. Think marginalia: *"structure IS the index"*, *"no imports, no configuration"*, *"handoff happens here"*.

---

## Grammar

Three elements, in this z-order:

```html
<!-- 1. Italic serif text (right-aligned, sits in the margin) -->
<text x="904" y="36" fill="{{ colors.text }}" font-size="14" font-style="italic"
      text-anchor="end" font-family="inherit">no imports, no configuration</text>

<!-- 2. Dashed Bézier leader from text to target -->
<path d="M 820 44 Q 700 84 520 216"
      fill="none" stroke="{{ colors.text_secondary }}" stroke-width="1"
      stroke-dasharray="4,3" opacity="0.70"/>

<!-- 3. Landing dot at the target point -->
<circle cx="520" cy="216" r="2" fill="{{ colors.text }}"/>
```

The `font-family="inherit"` picks up the active template's brand serif — on EN domains, something like `Newsreader` or `Georgia`; on AR, `Amiri` or `Markazi Text`. Since the brand body font is usually already serif in editorial/report/academic domains, *italic* does the work without needing a distinct font.

In domains where the body font is sans-serif (business-proposal, marketing-print), swap to an explicit serif fallback:

```html
<text font-family="'Newsreader', Georgia, serif" font-style="italic">…</text>
```

---

## Rules

- **Italic + serif together signal "editorial voice"** against the diagram's sans/mono body. Don't substitute italic sans or italic mono — the combination is load-bearing.
- **Dashed leader** (`stroke-dasharray="4,3"`) distinguishes the callout from primary arrows (which are solid).
- **Place callouts in margins** (top-right, bottom-left). Never inside the active diagram area.
- **Max 2 callouts per diagram.** More becomes commentary, not signal.
- **Never a solid leader** — reads as a flow arrow.

---

## Colors

| Intent | Text | Leader | Landing dot |
|---|---|---|---|
| Neutral aside | `colors.text` | `colors.text_secondary` @ 0.70 | `colors.text` |
| Focal / accent | `colors.accent` | `colors.accent` @ 0.50 | `colors.accent` |
| Tertiary (muted) | `colors.text_secondary` | `colors.border` | `colors.text_secondary` |

Pick neutral by default. Use accent only when the callout reinforces the 1–2 focal elements that already carry accent — never to *add* a third accent.

---

## Bilingual

On `.ar.html` templates, the callout moves to the HTML overlay pattern (see [rtl-notes.md](rtl-notes.md)):

```html
<div class="diagram-stage">
  <svg viewBox="0 0 1000 280" ...>
    <!-- geometry + leader + landing dot -->
    <path d="M 820 44 Q 700 84 520 216" ... stroke-dasharray="4,3"/>
    <circle cx="520" cy="216" r="2" fill="{{ colors.text }}"/>
  </svg>
  <!-- Arabic text in HTML, positioned at the leader's start point -->
  <div class="diagram-label dl-md" style="left: 90.4%; top: 12.9%;">
    <em>بلا استيرادات، بلا إعدادات</em>
  </div>
</div>
```

The `<em>` tag + the template's CSS (`em { font-style: italic; font-family: var(--font-serif); }`) keeps the italic-serif signature for AR too. On AR domains where the primary font is Cairo (sans), the brand's `font-serif` (usually Amiri or Markazi Text) provides the contrasting register.

---

## Anti-patterns

| Anti-pattern | Why it fails |
|---|---|
| Solid arrow leader | Reads as a flow arrow, not an aside |
| Italic sans or italic mono | The serif combination is load-bearing |
| Callouts crossing primary arrows / lifelines | Visual collision — offset to a clear margin |
| Using a callout to label something the diagram should label directly | Put the label on the element |
| More than 2 callouts per diagram | Becomes running commentary, not marginalia |
| Callout on the same element that already carries accent | Redundant — pick one signal |
