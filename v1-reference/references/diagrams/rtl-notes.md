# Bilingual Diagrams — RTL + Arabic overlay

Katib diagrams live in bilingual templates. Geometry is direction-neutral — Arabic and English templates share the same SVG shapes. **Only the labels differ**, and Arabic has one hard constraint: it can't live inside `<text>` or `<tspan>`.

---

## The rule

> **Never put Arabic text inside `<svg>`.** `scripts/build.py --check` will fail the build.

### Why

WeasyPrint's native SVG text renderer does *not* run HarfBuzz shaping. Arabic `<text>` elements render in their isolated Unicode presentation forms — the letters don't join, and the word is unreadable. `<foreignObject>` doesn't save you either: WeasyPrint's SVG path doesn't hand control to the HTML text engine for embedded content.

The HTML text path, however, shapes Arabic correctly. So the pattern is: **keep SVG for geometry, English labels, and numeric axes; put Arabic labels in HTML positioned absolutely on top.**

---

## The primitive: `.diagram-stage` + `.diagram-label`

Declare these once at the top of your AR template's `<style>` block:

```css
.diagram-stage {
  position: relative;
  direction: ltr;            /* keep positioning math sane */
  width: 100%;
  max-width: 170mm;
  margin: 0 auto;
}
.diagram-stage svg {
  display: block;
  width: 100%;
  height: auto;
}
.diagram-label {
  position: absolute;
  direction: rtl;            /* Arabic shaping via HTML text engine */
  transform: translate(-50%, -50%);
  white-space: nowrap;
  line-height: 1.1;
  font-family: var(--font-primary);   /* Cairo / Amiri / IBM Plex Arabic */
  color: var(--color-text);
}

/* Size modifiers — pick the one matching the hidden SVG font-size */
.diagram-label.dl-xs   { font-size: 7pt;  color: var(--color-text-tertiary); }
.diagram-label.dl-sm   { font-size: 8pt;  color: var(--color-text-secondary); }
.diagram-label.dl-md   { font-size: 9pt;  color: var(--color-text-secondary); }
.diagram-label.dl-lg   { font-size: 14pt; font-weight: 700; }
.diagram-label.dl-bold { font-weight: 700; }
.diagram-label.dl-muted { color: var(--color-text-tertiary); }
```

> CSS custom properties *do* work here — this block is outside `<svg>`, so `var()` resolves normally.

---

## Coordinate math

Inside SVG you'd write `<text x="260" y="156">...</text>`. With the overlay, place the HTML label at the **same point as a percent of the viewBox**:

```
left % = (svg_x / viewBox_width)  × 100
top  % = (svg_y / viewBox_height) × 100
```

So `x=260, y=156` inside `viewBox="0 0 520 300"` becomes `left: 50%; top: 52%;`. The `transform: translate(-50%, -50%)` on `.diagram-label` centers the text on that point — matching SVG's `text-anchor="middle"` behavior.

### Worked example

```html
<figure class="diagram">
  <div class="diagram-stage">
    <svg viewBox="0 0 520 300" xmlns="http://www.w3.org/2000/svg">
      <!-- geometry only — no Arabic text -->
      <rect x="220" y="130" width="80" height="40" rx="4" fill="{{ colors.accent }}"/>
      <line x1="220" y1="140" x2="90" y2="30"
            stroke="{{ colors.border }}" stroke-width="0.5"/>
      <rect x="10" y="18" width="150" height="24" rx="3"
            fill="{{ colors.page_bg }}" stroke="{{ colors.border }}" stroke-width="0.5"/>
    </svg>
    <!-- Arabic labels overlaid at viewBox-percentage coordinates -->
    <div class="diagram-label dl-lg"   style="left: 50%;   top: 52%;">كاتب</div>
    <div class="diagram-label dl-bold" style="left: 16.3%; top: 10%;">عرض تجاري</div>
  </div>
  <figcaption>الشكل 1: بنية كاتب</figcaption>
</figure>
```

---

## What about English labels?

English text, numeric axis labels, and monospace code names (`shot.py`, `build.py`, `npm run dev`) shape correctly inside SVG — **keep them there**. Only Arabic needs overlays.

Mixed-script labels (Arabic + English in the same span, e.g. `تثبيت npm install`) should go through HTML regardless, so direction and bidi are handled by the HTML engine.

---

## Flow direction mirroring (optional)

Most Katib diagrams don't need mirroring — the reader's eye accepts left→right flow in an Arabic doc because the diagram is a visual, not prose. But for process flows where direction carries semantic meaning ("first step → last step"), flip the SVG root group:

```html
<svg viewBox="0 0 600 80" role="img" aria-label="…">
  <g transform="{% if direction == 'rtl' %}translate(600,0) scale(-1,1){% endif %}">
    <!-- draw LTR — the transform flips it when direction='rtl' -->
  </g>
  <!-- text labels sit OUTSIDE that group, upright -->
  <text x="80" y="46" text-anchor="middle">Step 1</text>
</svg>
```

The `direction` variable is injected by `build.py` — `'rtl'` for `.ar.html`, `'ltr'` for `.en.html`.

**Don't mirror:** quadrants (axes have fixed directional meaning), sequence diagrams (time always flows top→down), state machines (mirror reads as confusing), trees (hierarchy is visual, not directional).

**Do mirror:** horizontal process flows, timelines, funnels read as progression.

---

## Bilingual alt text

Always provide `aria-label` in both languages via Jinja:

```html
<svg viewBox="0 0 600 80"
     role="img"
     aria-label="{{ 'Process flow: Plan → Build → Ship' if lang == 'en' else 'مخطط العملية: تخطيط ← بناء ← إطلاق' }}"
     style="max-width: 100%;">
```

The `lang` variable is injected by `build.py` — `'en'` or `'ar'`. `aria-label` feeds the PDF's accessibility tree + screen readers.

---

## Lint rule

`scripts/build.py --check` scans every `*.ar.html` template for Arabic characters inside `<text>` or `<tspan>` elements nested in `<svg>`. Any hit emits a violation with the file path, element, and snippet. Keeps the skill from silently shipping unreadable Arabic diagrams.

The check is cheap (regex over template source) and runs on every build. It is a *fail-the-build* rule, not a warning.

---

## Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| Arabic letters appear disconnected in PDF | Arabic sat in `<text>` | Move to `.diagram-label` HTML overlay |
| Label shifts position when switching AR ↔ EN | Hardcoded SVG coords in AR version | Switch to percent-positioned `.diagram-label` |
| Overlay label is in the wrong place | `viewBox` width ≠ rendered SVG width, or missing `transform: translate(-50%, -50%)` | Always set `.diagram-stage svg { width: 100%; }` + keep the transform |
| Mixed EN + AR in one label looks "wrong direction" | Went through SVG | Move the whole span to `.diagram-label` |
| Flow arrow points left-to-right in AR when the story reads right-to-left | No mirroring group | Wrap geometry in the `translate/scale(-1,1)` group above |
