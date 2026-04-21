# Katib — Design Language (English)

One visual language across six domains. Eight iron rules are cross-domain; palettes, fonts, and proportions swap per `domains/<domain>/tokens.json`.

---

## Eight iron rules

1. **Page background is never pure white.** Use the domain's `page-bg` token — warm off-white, parchment, or cream. White `#FFFFFF` reads cold and unfinished in print.
2. **One accent per domain.** Brand color carries emphasis, CTAs, section indicators. No second chromatic hue. Coverage ≤ 5% of total surface.
3. **Neutrals track the accent.** Cool-accent brands → cool-gray neutrals. Warm-accent brands → warm-gray neutrals. Never mix.
4. **Serif for authority, sans for utility.** Body text uses serif in editorial/formal, sans in tutorial/marketing. UI elements (eyebrows, labels, metadata) always sans.
5. **Serif weight locked at 500.** Never `bold` on serif display. Single weight is the signature. Sans can use 400/500/600.
6. **Line-height bands (never 1.6+ except workbook layout):**
   - Tight titles: 1.1–1.3
   - Dense body / tables: 1.4–1.45
   - Reading body: 1.5–1.55
   - **Workbook/tutorial exception:** 1.6 for scannability
7. **Tag backgrounds are solid hex, never `rgba()`.** WeasyPrint renders rgba tags as a double-rectangle; use a flat color from the `rgba → hex` conversion table below.
8. **Shadows are `ring` or `whisper`, never hard drop shadows.** `box-shadow: 0 0 0 0.5pt var(--border)` for rings; `box-shadow: 0 1pt 2pt rgba(0,0,0,0.04)` for whispers.

## Color system per domain (v0)

| Token | business-proposal | tutorial |
|---|---|---|
| `--page-bg` | `#FAFAF8` (near-white warm) | `#F7F5F0` (warm off-white) |
| `--accent` | `#1B2A4A` (Navy) | `#2E7D6B` (Teal) |
| `--accent-2` | `#C5A44E` (Gold) | `#3D5A80` (Slate) |
| `--accent-on` | `#FFFFFF` | `#FFFFFF` |
| `--text` | `#1A1A1A` | `#1F2024` |
| `--text-secondary` | `#404040` | `#4A4D52` |
| `--text-tertiary` | `#6A6A6A` | `#7A7D82` |
| `--border` | `#D9D9D3` | `#D4CFC2` |
| `--border-strong` | `#BFBEB4` | `#B5B0A3` |
| `--code-bg` | `#F2F2F0` | `#1A1A1A` (dark for code contrast) |
| `--code-fg` | `#1A1A1A` | `#E8E8E8` |
| `--callout-note` | — | `#E8F0EE` |
| `--callout-warn` | — | `#F8E8D8` |
| `--callout-tip` | — | `#EDF4EC` |

## rgba → hex conversion (over page-bg)

When an rgba tag is needed, convert to flat hex using the page-bg as blend base. Tables for `business-proposal` (over `#FAFAF8`):

| Accent @ opacity | Hex equivalent |
|---|---|
| Navy @ 0.08 | `#EEF1F6` |
| Navy @ 0.14 | `#E1E6F0` |
| Navy @ 0.18 (default tag) | `#D8DEED` |
| Navy @ 0.30 | `#C3CCE0` |
| Gold @ 0.15 | `#F6EDDB` |

## Type scale (print pt)

| Role | Size | Weight | Line-height |
|---|---|---|---|
| Display (cover title) | 36–48 | 500 | 1.10 |
| H1 | 18–22 | 500 | 1.20 |
| H2 | 14–16 | 500 | 1.25 |
| H3 | 12–13 | 500 | 1.30 |
| Body Lead | 11 | 400 | 1.55 |
| Body | 9.5–10.5 | 400 | 1.55 |
| Body Dense (tables) | 9–9.5 | 400 | 1.40 |
| Caption | 8.5–9 | 400 | 1.45 |
| Label (UI) | 7.5–8 | 600 | 1.35 |
| Tiny (meta, page numbers) | 7 | 400 | 1.40 |

Screen (px) ≈ pt × 1.33. Don't mix pt and px within a template.

## Spacing (4pt base)

| Level | Value | Use |
|---|---|---|
| xs | 2–3 pt | In-line spacing |
| sm | 4–5 pt | Tag padding, list-item gaps |
| md | 8–10 pt | Component interior |
| lg | 16–20 pt | Between components |
| xl | 24–32 pt | Section title margins |
| 2xl | 40–60 pt | Between major sections |
| 3xl | 80–120 pt | Between chapters (long-doc only) |

## Page margins (A4, per doc type)

| Doc type | Top | Right | Bottom | Left |
|---|---|---|---|---|
| Proposal | 20 mm | 22 mm | 22 mm | 22 mm |
| One-Pager | 15 mm | 18 mm | 15 mm | 18 mm |
| Letter | 25 mm all sides | | | |
| How-To (tutorial) | 18 mm | 20 mm | 20 mm | 20 mm |
| Onboarding | 20 mm | 22 mm | 22 mm | 22 mm |
| Cheatsheet | 10 mm all sides | | | |

Cover pages: always **0 / 0 / 0 / 0** (full-bleed).

## Border radii

`4 pt → 6 pt → 8 pt (default) → 12 pt → 16 pt → 24 pt → 32 pt (hero only)`

## Cover section rules

- Cover is a `@page :first` section with zero margins
- Cover image is a `background-image` on the cover container OR a full-bleed `<img>` at `100vw × 100vh`
- Title/subtitle/reference code sit in absolutely-positioned `<div>` overlays — never baked into the image
- Cover height: exactly `297mm` for A4 portrait (no flex shrinking)
- Text over image: minimum contrast ratio 4.5:1 (WCAG AA)

## Signature section rules (business-proposal only)

- Standard margins, page numbering hidden (`start: 0`)
- Signer details: name, title, company, reference date
- Signature image: `100 × 35 mm` max, stroke inward padding `4pt`
- Extracted at build time from `assets/signature.png` if present

## Body section rules

- Standard margins per doc type
- Page numbers start at `3` for business-proposal (covers title + signature spreads); at `2` for tutorial
- Header: right-aligned `{reference_code}  |  CONFIDENTIAL` (when applicable)
- Footer: centered `{brand} | Page N of M` in tertiary text color

## Print contracts (page count limits)

| Doc type | Target | Hard limit |
|---|---|---|
| One-pager | 1 | 1 |
| Letter | 1 | 1 |
| Proposal | 8–15 | 20 |
| How-to | 2–5 | 8 |
| Onboarding | 4–8 | 12 |
| Cheatsheet | 1–2 | 2 |

`build.py --verify` checks page count against hard limits and fails the build if exceeded.

## Known WeasyPrint landmines (see `production.md` for fixes)

1. **Tag rgba double-rectangle** — use flat hex from the conversion table
2. **Thin border + radius double-ring** — borders < 1pt with `border-radius` trigger the bug
3. **break-inside in flex** — wrap flex children in a block container
4. **`height: 100vh` in `@page`** — use explicit mm values
5. **SVG marker orient="auto"** — WeasyPrint does not rotate markers; use fixed-orientation marker copies
