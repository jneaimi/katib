# Katib — Design Language (Arabic)

The same eight iron rules as `design.en.md` apply, with Arabic-specific typography, direction, numeral, and punctuation rules layered on top. Read `design.en.md` first for color, spacing, and type scale; this file covers only what changes for Arabic.

---

## 1 · Direction is `rtl` everywhere

```css
html[lang="ar"] { direction: rtl; }
@page :first { direction: rtl; }
```

All templates set `<html lang="ar" dir="rtl">`. Mirrored layout follows automatically for text, tables, lists, and flex order — except for properties listed under **Don't mirror** below.

### Don't mirror

| Element | Why |
|---|---|
| Brand logo | Logos are proper nouns — flip only if the logo includes directional text |
| Signature image | Stays in original orientation |
| Charts, diagrams | Mirror the layout but **not the data axes** — dates still run oldest→newest left-to-right in a time series when that matches the data semantics. For Arabic reading flow, reverse only when the data is inherently sequential (steps, phases) |
| Code blocks | English syntax stays LTR inside an RTL document. Use `<pre dir="ltr">` on every code block |
| English technical terms within Arabic prose | Stay LTR (bidi mirroring handles this automatically) |

### Do mirror

- Page margins (e.g., larger gutter on right in `classic` layout)
- Section-title left-bar becomes right-bar
- Table header alignment flips from left to right
- Cover title placement: top-right instead of top-left
- Signature block: right-aligned instead of left

## 2 · Numerals — two systems, context-dependent

| Context | Use | Example |
|---|---|---|
| Formal documents (proposals, government, formal letters) | **Arabic-Indic** `٠١٢٣٤٥٦٧٨٩` | "٢٦ رمضان ١٤٤٧" |
| Body text in editorial / thought leadership | Arabic-Indic | "٨٠٪ من الشركات..." |
| Digital / casual / UI / code / metrics | **Western** `0123456789` | "80% من الشركات..." |
| Mixed (tables, charts, data) | **Western** — consistent across language variants | |
| Dates in headers/footers | Western (ISO-style: 2026-04-21) | |

Never mix both systems in the same paragraph. Pick per doc type and hold it throughout.

## 3 · Punctuation — proper Arabic marks

| Use | Not | Purpose |
|---|---|---|
| `،` | `,` | Comma |
| `؛` | `;` | Semicolon |
| `؟` | `?` | Question mark |
| `!` | — | Exclamation (same glyph, visual direction different) |
| `«»` | `""` or `''` | Quotation marks |
| `ـ` (tatweel) | — | Typographic extension only; **never use for emphasis** in body text |

## 4 · Font stacks

### business-proposal (formal corporate)

```css
--font-ar-primary: "IBM Plex Arabic", "Cairo", "Tahoma", sans-serif;
--font-ar-display: "IBM Plex Arabic", "Noto Naskh Arabic", serif;
```

- Body: IBM Plex Arabic weight 400
- Display/cover title: IBM Plex Arabic weight 500 (never 700+)
- Tables/metadata: IBM Plex Arabic weight 400 at 9.5pt

### tutorial (warm, approachable)

```css
--font-ar-primary: "Cairo", "IBM Plex Arabic", "Tahoma", sans-serif;
--font-ar-display: "Cairo", "Amiri", serif;
--font-mono: "JetBrains Mono", "Courier New", monospace;  /* code blocks stay LTR */
```

- Body: Cairo weight 400
- Step numbers: Cairo weight 600, Western numerals (for scannability)
- Callouts: Cairo weight 500 italic

### editorial (v0.2 — reference)

```css
--font-ar-primary: "Amiri", "Noto Naskh Arabic", serif;
--font-ar-display: "Amiri", serif;
```

All Arabic fonts are OFL; Amiri, Cairo, and IBM Plex Arabic bundled in `assets/fonts/core/`.

## 5 · Size adjustments for Arabic

Arabic characters typically read smaller than Latin at the same pt size. Size tokens bump up:

| Role | EN size | AR size |
|---|---|---|
| Body | 10 pt | 11 pt |
| Body Dense | 9 pt | 10 pt |
| H1 | 20 pt | 22 pt |
| H2 | 15 pt | 16 pt |
| Caption | 8.5 pt | 9 pt |
| Label | 7.5 pt | 8 pt |

Apply via CSS:

```css
html[lang="ar"] body { font-size: 11pt; }
html[lang="ar"] h1 { font-size: 22pt; }
```

## 6 · Line-height — slightly looser

Arabic diacritics and letter-height variation need more vertical breathing room.

| Role | EN | AR |
|---|---|---|
| Titles | 1.2 | 1.3 |
| Dense body | 1.4 | 1.5 |
| Reading body | 1.55 | 1.65 |
| Workbook body | 1.6 | 1.75 |

## 7 · Letter-spacing is forbidden

Arabic script is cursive. Letter-spacing breaks ligatures and destroys readability. **Never use `letter-spacing` on Arabic text** — not even 0.5pt. If a designer's eye wants more breathing, increase `line-height` or `word-spacing` instead.

## 8 · Text over cover images

Arabic covers use the same generated image as English — title/subtitle text sits in the HTML text layer on top.

- Title zone: **top-right** (not top-left — mirrors the EN placement)
- Subtitle zone: **bottom-left** (mirrors EN bottom-right)
- Reference code: **bottom-right** (mirrors EN bottom-left)
- Background image: identical to EN version (no flipping — image is content, not layout)

## 9 · Title register

Article and proposal titles should use **confident, elevated MSA**. Avoid:

- Casual verbs that sound like chat: `وصل` (arrived), `طلع` (came out)
- Direct English translations: `مهندس كبير` for "senior engineer" reads as "big engineer" — rephrase
- AI filler: `في عالمنا اليوم`, `نعيش في زمن`, `من المعلوم أن`

## 10 · RTL-specific landmines

| Landmine | Fix |
|---|---|
| Latin punctuation in AR text | Use Arabic marks (see §3) |
| Page numbers showing Western when body uses Arabic-Indic | Set `font-variant-numeric: tabular-nums` + explicit numeral system in `@page` counter |
| Tables breaking alignment in RTL | Use `direction: rtl` on `<table>` not on cells |
| Flex gap collapsing | Tested fine in WeasyPrint ≥ 60.0; downgrade trigger documented in `production.md` |
| Bidi in mixed EN/AR lines | Wrap EN tokens in `<span dir="ltr">` for explicit direction override |
| Code blocks rendering RTL | Every `<pre>` and `<code>` needs explicit `dir="ltr"` |

## 11 · Brand names and technical terms

- Brand names (e.g., "NemoClaw", "Amazon", "Claude") stay in Latin — do not transliterate
- Technical acronyms introduce once with Arabic meaning: "بروتوكول سياق النموذج (MCP)". Subsequent mentions can use "MCP" alone.
- Arabic terms with common non-tech meanings need qualification:
  - `وكيل` → `الوكيل الذكي` (AI agent, not business broker)
  - `إطار` → `الإطار التقني` (framework, not picture frame)
  - `نموذج` → `النموذج اللغوي` (language model, not form to fill)

## 12 · Enforcement via `build.py --check`

The `--check` mode scans Arabic templates for:

- Latin comma `,` inside Arabic text blocks → fail
- `letter-spacing` rule on any Arabic element → fail
- `<pre>` or `<code>` without `dir="ltr"` → fail
- `إذا` followed by a noun (nominal sentence) → warn (should use `إذا كان/كانت`)
- Unqualified `وكيل` / `وكلاء` without `الذكي/الأذكياء` within 3 words → warn
- `rgba()` in any color token → fail (applies to EN too)
