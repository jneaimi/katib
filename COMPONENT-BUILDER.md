# Katib — AI-assisted component builder

This is the playbook Claude follows when the user asks to **build a new
component**. Every step is a thin orchestration over deterministic tools
that already exist — the intelligence lives in the interview and
generation, not in any new executable.

## When to enter this mode

Invoke when:
- The user types `/katib component new` (with or without a name).
- The user describes a visual element they need and no existing
  component fits — check `capabilities.yaml` under `components.*` first.
- The user explicitly asks to "make a component", "create a new block",
  "I want a [X] that shows [Y]".

Do **not** enter this mode when:
- The user wants a new **recipe** (different flow — that's just editing
  YAML with `scripts/recipe.py`).
- The request can be satisfied by an existing component with recipe-level
  input shuffling. Prefer reuse over creation.

## The flow

```
1. Interview    ──▶  5 questions, one AskUserQuestion call
2. Scaffold     ──▶  scripts/component.py new <name> ...
3. Generate     ──▶  Edit component.yaml / en.html / ar.html / styles.css
4. Validate     ──▶  scripts/component.py validate <name>
5. Preview      ──▶  scripts/component.py test <name>  (renders EN + AR)
6. Iterate      ──▶  User sees PDF → feedback → edit → preview again
7. Register     ──▶  scripts/component.py register <name>  (on approval)
```

No new executables. Existing CLI surface handles every step.

---

## Step 1 — Interview

Ask these **in a single `AskUserQuestion` call** if possible. If the
user already gave some of the answers in their prompt, skip those.

| # | Question | Accepted values |
|---|---|---|
| 1 | **Name** (kebab-case) | `^[a-z][a-z0-9]*(-[a-z0-9]+)*$` — e.g. `testimonial`, `metric-block`, `price-grid` |
| 2 | **Tier** | `primitive` (small reusable part), `section` (whole content block), `cover` (full-page document opener) |
| 3 | **Languages** | `en` only, `ar` only, or `en + ar` (the default) |
| 4 | **Inputs** | One-line description of each — e.g. "quote (string, required), author (string, required), role (string, optional)" |
| 5 | **Closest existing component** | User picks from a short list of likely exemplars you suggest based on tier + purpose |

### Picking exemplar candidates

When you ask question 5, offer 3 concrete exemplars from the existing
library. Match on tier + purpose:

- **Primitive with text only** → `callout`, `pull-quote`, `tag`, `eyebrow`
- **Primitive with variants** → `signature-block`, `rule`
- **Primitive with structured list** → `clause-list`, `skill-bar-list`, `tag-chips`
- **Primitive with images** → `figure-with-caption`
- **Section — heading + body** → `module`, `front-matter`
- **Section with variants** → `letterhead`, `masthead-personal`, `cv-layout`
- **Section — layout/page-level** → `landscape-section`, `two-column-page`, `slide-frame`, `appendix-page`, `full-bleed-page`, `section-divider-page`
- **Section with images** → `two-column-image-text`, `sections-grid`
- **Section with tabular data** → `financial-summary`, `kv-list`
- **Cover** → `cover-page` (only cover shipped so far)

You tell the user: "Which existing component is closest in spirit — I'll
borrow its shape." Reading the exemplar's 4 files is the single best
shortcut to matching the house style.

---

## Step 2 — Scaffold

Run the scaffolder deterministically:

```bash
uv run scripts/component.py new <name> \
    --tier <primitive|section|cover> \
    --namespace user \
    --languages en,ar \
    --description "<one-sentence purpose>"
```

**Namespace** — use `user` for user-created components (lands in
`~/.katib/components/`). Use `katib` only if the user explicitly wants
to contribute the component back to the bundled library.

The scaffolder emits:
- `component.yaml` with TODO-marked description
- `en.html` (and `ar.html` if requested) with a stub body
- `README.md` stub
- `fixtures/test-inputs.yaml` for the preview renderer

It also writes an audit entry. Never touch the audit file by hand.

---

## Step 3 — Generate the real files

Read the exemplar first (`components/<tier>/<exemplar>/*`). Mirror its
patterns. Fill in the four files with content tailored to the interview.

When the component carries default prose (placeholders, README example
copy, `fixtures/test-inputs.yaml` strings), apply the content quality gate
in `references/writing.{lang}.md` to that prose — defaults set the tone
every recipe author inherits.

### `component.yaml` — the contract

Must contain at minimum:

```yaml
name: <name>
tier: <tier>
version: 0.1.0
namespace: user
description: <1-2 sentences, no more than 500 chars>
languages: [en, ar]
requires:
  tokens: [text, accent, ...]   # Only tokens you actually use in CSS.
  fonts: [display, primary]      # Only fonts you actually use.
accepts:
  inputs:
    - <input_name>:
        type: string|markdown|int|float|bool|date|image|array|object
        required: true|false
        description: <short explanation>
# Optional:
variants:
  - <variant_name>
page_behavior:
  mode: atomic|flowing|flowing-protect-items
  break_before: auto|always|avoid
  break_after: auto|always|avoid
```

**Rules:**
- `name`, `tier`, `version`, `namespace`, `languages` are all required.
- `requires.tokens` must list **only** tokens referenced in `styles.css`
  via `var(--token-name)`. Declaring unused tokens triggers a validator
  warning.
- `accepts.inputs[].name` **cannot be `description`** — it clashes with
  the schema's own description field and the component will fail
  validation. Use `overview`, `intro`, `blurb`, `note` instead.
- `page_behavior` is optional; omit for regular flowing primitives.

### `en.html` — Jinja template (and `ar.html` if bilingual)

Template context — variables you can read:

| Variable | Meaning |
|---|---|
| `input.<name>` | Any input from the recipe. Missing inputs render as empty. |
| `variant` | The variant name if the recipe picked one. `None` otherwise. |
| `colors.<token>` | Resolved color tokens (e.g. `{{ colors.accent }}`). |
| `fonts.<name>` | Resolved font stacks. Usually just inject via CSS `var(--font-X)`. |
| `logo.primary`, `logo.max_height_mm` | Brand logo (if declared in `requires.brand_fields`). |
| `identity.author_name`, `identity.company` | Brand identity fields. |

Structural rules:
- Root element must carry `class="katib-<component-name>"` and either
  `class="katib-section katib-<name>"` (for sections) or `class="katib-<name>"` (for primitives).
- Use BEM naming inside: `katib-<name>__element`, `katib-<name>--variant`.
- Set `lang="en"` on the EN root and `lang="ar" dir="rtl"` on the AR root.
- Use `{{ input.X | safe }}` for **trusted HTML** inputs (like `raw_body`).
  Never for untrusted inputs — escaping stays on by default.

### `ar.html` — RTL-aware variant

For bilingual components, copy `en.html` and adjust:
- Add `dir="rtl"` to the root element.
- Translate any inline English strings (labels, "Appendix", etc.).
- Leave the Jinja expressions untouched — the inputs are language-neutral.

Arabic typography conventions (apply in `styles.css` under
`.katib-<name>[lang="ar"]`):
- Larger font sizes (typically +1–2pt vs EN).
- Looser line-height (1.4–1.8 vs 1.2–1.5 for EN).
- No letter-spacing or uppercase transforms (they break Arabic glyph shaping).
- Reverse directional properties: `text-align: end`, `border-inline-start`, etc.
- `font-style: italic` has no meaning in Arabic — drop it.

### `styles.css` — scoped CSS

**Never hardcode colors or fonts.** Use `var(--accent)`, `var(--text)`,
`var(--font-display)`, `var(--font-primary)`, etc. Brand profiles flow
through the token system; hardcoded values ignore them.

Scope all selectors under `.katib-<name>` so they can't leak to other
components.

**WeasyPrint caveats** (learned the hard way):
- `inset: 0` is **not supported** — write `top: 0; right: 0; bottom: 0; left: 0`.
- CSS custom properties work inside `@page` rules with caveats — prefer
  hex colors or rgb() inside `@page` margin boxes.
- `break-inside: avoid` is preferred over the older `page-break-inside: avoid`
  (WeasyPrint supports both; the new syntax is forward-compatible).
- For page-level layouts (landscape, zero-margin, etc.), use named
  `@page foo { ... }` rules and opt in via `page: foo;` on the component root.

### `README.md` — one file, one shape

```markdown
# <name>

## Purpose

<1-3 sentences on what the component shows and when to use it.>

## Variants  (omit if no variants)

| Variant | When to use |
|---|---|
| `<name>` | <one-line> |

## Inputs

| Input | Type | Required | Notes |
|---|---|---|---|
| `<name>` | `string` | yes/no | <notes> |

## Example usage

\`\`\`yaml
- component: <name>
  inputs:
    <realistic example>
\`\`\`

## Notes  (optional)

<Any gotchas, RTL behavior, WeasyPrint quirks.>
```

Validator requires a `## Purpose` heading. Nothing else is structurally
checked, but the table shape is convention.

---

## Step 4 — Validate

```bash
uv run scripts/component.py validate <name>
```

Reads the YAML, checks every input name matches a use in the Jinja
templates (and vice-versa), checks declared tokens are referenced in CSS,
and runs structural checks on README.md.

Exit codes:
- `0` + possibly warnings → proceed
- `1` → real errors. Fix before rendering.

Common fixes:
- **"token X declared in requires.tokens but not referenced"** → Remove
  the token from `requires.tokens` (trim to only what's used).
- **"input X used in HTML but not declared"** → Add the input to
  `accepts.inputs`.
- **"component.yaml schema validation failed"** → Read the error; most
  often a required field is missing or has the wrong type.

---

## Step 5 — Preview

```bash
uv run scripts/component.py test <name>
```

Renders the component standalone to `dist/component-tests/<name>/<name>.{en,ar}.pdf`.
Uses auto-synthesized test inputs unless `fixtures/test-inputs.yaml`
supplies real ones. Zero WeasyPrint warnings = clean render.

**Always show the user the PDF path and a count of WeasyPrint warnings
after rendering.** If warnings > 0, investigate — they often indicate
invalid CSS that WeasyPrint silently ignored.

---

## Step 6 — Iterate

Ask the user to open the PDF and confirm. If changes are needed:
- "Make the title smaller" → edit styles.css
- "Add a byline line" → edit component.yaml (new input) + en.html + ar.html + styles.css
- "Use a different color" → check brand tokens — the user probably
  wants to use `var(--accent_2)` instead of `var(--accent)`

Re-run validate + test after every change. Never skip the validate step.

---

## Step 7 — Register

On user approval:

```bash
uv run scripts/component.py register <name>
```

This updates the audit trail and regenerates `capabilities.yaml` so the
router and future recipes can find the component.

Then tell the user how to use the new component in a recipe:

```yaml
sections:
  - component: <name>
    inputs:
      <input>: "value"
```

---

## Common pitfalls (cheat sheet)

| Pitfall | Symptom | Fix |
|---|---|---|
| Input named `description` | Schema validation fails | Use `overview`, `blurb`, `intro`, `note` |
| `inset: 0` in CSS | WeasyPrint warning "Ignored `inset: 0`" | Use `top: 0; right: 0; bottom: 0; left: 0` |
| Hardcoded colors | Brand profiles don't flow through | Use `var(--accent)` etc. |
| Missing `## Purpose` in README | Validator warning | Add the section |
| Unused tokens in `requires.tokens` | Validator warning | Trim to what's actually used |
| `font-style: italic` in Arabic | Visual: no effect | Drop from `[lang="ar"]` selectors |
| `letter-spacing` / `text-transform: uppercase` on Arabic | Broken glyph shaping | Drop from `[lang="ar"]` selectors |
| Quotes in YAML description | YAML parse error | Use folded-block style: `description: \|` + newline + indented text |

---

## Bilingual authoring

Designing a component that survives both languages cleanly:

- **Every text-bearing input is wrappable in `inputs_by_lang`.** The recipe
  decides per language; the component just declares the input once. No
  per-lang inputs in `component.yaml`.
- **SVG with text → see the next section.** WeasyPrint cannot shape
  Arabic in SVG `<text>`. Use the HTML-overlay pattern.
- **RTL** — the renderer sets `direction: rtl` on `<html>` when
  `--lang ar`, plus `dir="rtl"` on the component root. Logical CSS
  properties (`text-align: end`, `border-inline-start`, `margin-inline-start`)
  flip automatically. Hardcoded `text-align: left` does not — gate it
  behind `[lang="ar"]` if you need a per-language override.
- **Numerals** — Western (`123`) vs. Arabic-Indic (`١٢٣`) is a
  recipe-author choice, not a component decision. Default behavior keeps
  source numerals as authored. Don't transform them in CSS.

---

## Arabic in SVG diagrams

WeasyPrint's SVG renderer has no bidi or HarfBuzz path. Putting Arabic
inside `<svg><text>...</text></svg>` produces disjoined, mis-ordered
glyphs. The fix: **SVG holds geometry only; labels render as
absolutely-positioned HTML `<div>` elements layered over the SVG.**

### Container scope: keep `<figcaption>` OUT of the relative parent

The percentages on overlay `<div>`s resolve against the **total height of
their `position: relative` ancestor**. If you put `position: relative` on
the `<figure>` and the figure also contains a `<figcaption>`, the
ancestor height becomes `svg_height + figcaption_height` — every overlay
drifts upward, and the drift gets worse the further up the SVG you go.

The relative-positioning context must be **the SVG aspect ratio alone —
caption goes outside.**

❌ **Wrong** — `position: relative` on `<figure>`, caption inside it:

```html
<figure style="position: relative; ...">
  <svg ...>...</svg>
  <div style="position: absolute; top: 18.75%; ...">الأول</div>
  <figcaption>...</figcaption>   <!-- inflates the relative parent -->
</figure>
```

✓ **Right** — wrap SVG + overlays in their own `<div style="position: relative;">`, leave the `<figcaption>` outside that div as a sibling:

```html
<figure style="margin: 0; break-inside: avoid; page-break-inside: avoid;">
  <div style="position: relative;">
    <svg ...>...</svg>
    <div style="position: absolute; top: 18.75%; ...">الأول</div>
  </div>
  <figcaption>...</figcaption>
</figure>
```

### The pattern

Inside a `<figure>`, wrap the SVG + overlay labels in a
`<div style="position: relative;">`. Put a geometry-only SVG (`<rect>`,
`<line>`, `<circle>`, `<path>`) inside, then layer HTML `<div>` labels
on top, anchored on shape centers. Place any `<figcaption>` **outside**
the relative `<div>` but inside the `<figure>`.

```html
<figure style="margin: 0; break-inside: avoid; page-break-inside: avoid;">
  <div style="position: relative;">
    <svg viewBox="0 0 560 240" width="100%" style="display: block;" role="img" aria-label="Three stacked rows">
      <rect x="40" y="20"  width="480" height="50" fill="#E8F4FD" rx="4"/>
      <rect x="40" y="90"  width="480" height="50" fill="#FFF3E0" rx="4"/>
      <rect x="40" y="160" width="480" height="50" fill="#F3E5F5" rx="4"/>
      <!-- EN can keep <text> in SVG -->
      <text x="280" y="50"  text-anchor="middle" font-size="14" fill="#141414">First</text>
      <text x="280" y="120" text-anchor="middle" font-size="14" fill="#141414">Second</text>
      <text x="280" y="190" text-anchor="middle" font-size="14" fill="#141414">Third</text>
    </svg>
  </div>
  <figcaption>Figure: three stacked rows.</figcaption>
</figure>
```

Same geometry for Arabic, but labels are HTML overlays inside the same
`position: relative` `<div>`:

```html
<figure style="margin: 0; break-inside: avoid; page-break-inside: avoid;">
  <div style="position: relative;">
    <svg viewBox="0 0 560 240" width="100%" style="display: block;" role="img" aria-label="ثلاثة صفوف مكدسة">
      <rect x="40" y="20"  width="480" height="50" fill="#E8F4FD" rx="4"/>
      <rect x="40" y="90"  width="480" height="50" fill="#FFF3E0" rx="4"/>
      <rect x="40" y="160" width="480" height="50" fill="#F3E5F5" rx="4"/>
    </svg>
    <div style="position: absolute; top: 18.75%; left: 50%; transform: translate(-50%, -50%); direction: rtl; unicode-bidi: isolate; font-family: Cairo, sans-serif; font-size: 14px; color: #141414; white-space: nowrap; text-align: center;">الأول</div>
    <div style="position: absolute; top: 47.92%; left: 50%; transform: translate(-50%, -50%); direction: rtl; unicode-bidi: isolate; font-family: Cairo, sans-serif; font-size: 14px; color: #141414; white-space: nowrap; text-align: center;">الثاني</div>
    <div style="position: absolute; top: 77.08%; left: 50%; transform: translate(-50%, -50%); direction: rtl; unicode-bidi: isolate; font-family: Cairo, sans-serif; font-size: 14px; color: #141414; white-space: nowrap; text-align: center;">الثالث</div>
  </div>
  <figcaption>الشكل: ثلاثة صفوف مكدسة.</figcaption>
</figure>
```

### Positioning math

Anchor each label on the center of its shape, expressed as percentages
of the SVG viewBox:

```
top:  cy / VH * 100%
left: cx / VW * 100%
transform: translate(-50%, -50%);
```

For `viewBox="0 0 560 240"` (VW=560, VH=240), a `<rect>` centered at
`(280, 45)` becomes `top: 18.75%; left: 50%`.

### Required CSS on each label

```
direction: rtl;
unicode-bidi: isolate;
font-family: Cairo, sans-serif;
white-space: nowrap;
```

`unicode-bidi: isolate` prevents adjacent labels from cross-contaminating
bidi runs. `white-space: nowrap` keeps the label on one line so the
center-translate stays accurate.

### Pitfalls

| Pitfall | Why it bites | Fix |
|---|---|---|
| Using `bottom:` for vertical anchor | WeasyPrint anchoring quirk inside `position: relative` | Always use `top:` (compute from `cy/VH`) |
| Missing `width="100%"` on `<svg>` | SVG renders at intrinsic size; HTML overlay drifts off the geometry | Always set explicit `width="100%"` |
| `<figure>` splits across pages | `module` is `mode: flowing`; raw HTML inherits | Add `break-inside: avoid; page-break-inside: avoid;` (or use `class="katib-atomic"`) |
| Arabic inside `<svg><text>` | WeasyPrint produces broken glyphs | Refactor to HTML overlay |
| `<figcaption>` inside the `position: relative` parent | Caption height inflates the parent; overlay `top: %` drifts upward (worst on upper rows) | Wrap only `<svg>` + overlays in `<div style="position: relative;">`; put `<figcaption>` outside that div, inside `<figure>` |

### Lint enforcement

The `ARABIC_IN_SVG_TEXT` lint rule blocks Arabic codepoints inside SVG
`<text>` elements at recipe-validation time. If you see this error,
refactor the offending diagram using the HTML-overlay pattern above.

See `recipes/bilingual-svg-diagram.yaml` for a working example.

---

## Atomic blocks inside flowing modules

`module` is `mode: flowing` — its body can split across pages. Raw HTML
in `module.raw_body` inherits this behavior, so a callout box, install
snippet, repository card, framed quote, or styled code block can split
mid-element and look broken.

Apply the **`katib-atomic` utility class** to any wrapper element you
don't want to split:

```html
<div class="katib-atomic" style="border: 1pt solid var(--border); padding: 12pt; border-radius: 4pt;">
  ...content that must stay together...
</div>
```

The class is opt-in and ships in katib's base CSS. Internally it sets
`break-inside: avoid; page-break-inside: avoid;` — equivalent to
hand-writing both, but with a stable name.

**Common targets:**
- Callout boxes built inline in `raw_body`
- Install snippets / `<pre>` blocks with custom framing
- Repository cards, contact cards, framed quotes
- Any inline figure with a caption that must travel with it

**Bundled named components (`callout`, `pull-quote`, `data-table`,
`executive-summary`) already declare `mode: atomic` in their
`page_behavior` — only raw HTML in `module.raw_body` needs the utility
class.**

---

## Scope of this mode

**In scope:** Creating a single new component from interview → register.

**Out of scope** (handled elsewhere):
- Creating a new recipe that uses the component (`scripts/recipe.py new`)
- Migrating an existing v1 template (`v1-reference/domains/*`) — same as
  building from scratch, but use the v1 HTML as the exemplar
- Editing the bundled tier (namespace=katib) — requires explicit user
  intent + `--force --justification` flag
- Graduation gate workflow — a separate machinery for promoting
  recipe-inlined patterns to components

## What the skill guarantees

- No executable outside `scripts/component.py` is required.
- No new Python helpers — `scripts/component.py test` already renders a
  preview PDF with synthesized inputs.
- The audit trail is updated atomically by `register`; the user never
  touches `memory/*.jsonl` files.
- User components land in `~/.katib/components/` by default — survive
  skill reinstalls, editable, shareable (Phase 4).
