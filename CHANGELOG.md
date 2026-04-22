# Changelog

All notable changes to Katib are documented here. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.3.0] — 2026-04-22

### Added
- **New domain: `formal`.** GCC-aware institutional correspondence with four doc types:
  - `noc` — UAE No-Objection Certificate with pre-structured fields (name, Emirates ID, passport, position, join date, employment status), purpose block, validity period, stamp hint (1 page)
  - `government-letter` — addressed to ministries/authorities with Islamic greeting (`السلام عليكم ورحمة الله وبركاته`), honorific salutation (`سعادة/معالي + name + المحترم`), subject line, formal body, closing formula (`وتفضّلوا بقبول فائق الاحترام والتقدير،،`) (1–2 pp)
  - `circular` — internal company-wide announcement with TO/FROM/CC header, full-width colored banner, action items block, effective date (1–2 pp)
  - `authority-letter` — delegation of specific authority with Grantor/Grantee dual-column blocks, numbered scope list, validity period (1 page)
- Institutional palette: restrained navy `#0B3D66` on off-white `#FDFDFB`, Georgia (EN) / Amiri (AR) serif. No decorative covers — formal domain defaults to cover-less rendering.
- Bilingual structural conventions: Arabic passport numbers / Emirates IDs embedded as LTR (`direction: ltr; unicode-bidi: embed`) inside RTL cells for correct reading.
- SKILL.md router: added "NOC / formal / government / ministry / circular / authority / خطاب رسمي / شهادة عدم ممانعة / تعميم / تفويض" signal → `formal` domain. Doc-type picker table added.
- `references/writing.{en,ar}.md`: formal letter rules (honorific catalog, Islamic greeting use, Arabic opening/closing formulas, NOC purpose specificity, authority-letter scope precision).
- Reference-code formats: `NOC-{YYYY}-{NNN}`, `GOV-{YYYY}-{NNN}`, `CIR-{YYYY}-{NNN}`, `AUTH-{YYYY}-{NNN}`.

### Changed
- `scripts/build.py`: cover validation now skips when a domain declares no covers (`covers_allowed: []`). Previously raised `ValueError: cover_style None not allowed` on cover-less domains.
- Roadmap renumbered: `formal` is now **live** (was v0.3 deferred).

## [0.2.0] — 2026-04-22

### Added
- **New domain: `report`.** Long-form structured documents with four doc types:
  - `research-report` — abstract + methodology + findings + discussion + conclusion + references (10–30 pp)
  - `progress-report` — KPI cards + milestones + risks + next-period priorities (5–15 pp)
  - `annual-report` — chairman's letter + highlights + financial summary + outlook (20–60 pp)
  - `audit-report` — scope + severity matrix + detailed findings + recommendations + remediation plan (10–25 pp)
- Data-forward palette: slate `#2E3A4B` + teal accent `#0F766E` on warm off-white, Newsreader serif for EN and Amiri for AR. Distinct from business-proposal's navy+gold.
- **Bilingual RTL tables** with numeric cells forced LTR (`direction: ltr` on `.num`) so figures read correctly inside Arabic tables.
- **Severity matrix** (audit-report) — color-coded likelihood × impact grid, works in both EN and AR.
- **KPI cards with trend colors** (progress-report) — green/red/neutral trend badges.
- **Big-year title page** (annual-report) — 88pt year mark dominates the cover page.
- **Confidential stamp** (audit-report) — red-outlined corner stamp on the title page.
- SKILL.md router now recognizes "report / research / annual / audit / progress / تقرير / دراسة / تدقيق" and routes to the new domain.
- `references/writing.{en,ar}.md` gain a report-specific section on informational register, third-person voice, and finding structure (observation → risk → evidence → recommendation).
- Reference-code formats: `RPT-R-{YYYY}-{NNN}`, `RPT-P-{YYYY}-{NNN}`, `RPT-A-{YYYY}`, `RPT-AU-{YYYY}-{NNN}`.

### Changed
- Deferred-domain roadmap in SKILL.md renumbered: `formal` → v0.3, `personal` → v0.4, `academic` → v0.5 (new), `financial` → v0.6 (new), `editorial` → v0.7, `marketing-print` → v0.8 (renamed from marketing-pitch, slide-decks added as print-PDF), `legal` → v0.9 (new).

## [0.1.2] — 2026-04-22

### Changed
- npm package renamed from `katib` to **`@jasemal/katib`**. The npm registry
  rejected the unscoped name as too similar to existing packages (`katex`,
  `kasir`, `atob`). Scoped install:
  ```bash
  npx @jasemal/katib
  ```
  The CLI binary is still `katib` — no change to day-to-day usage after
  install. GitHub repo stays at `github.com/jneaimi/katib`.
- README install one-liner + `bin/katib.js` help text updated to the scoped
  form. Pre-v0.1.2 docs that say `npx katib` are stale.

## [0.1.1] — 2026-04-22

Three rendering bugs reported against the `workbook` and `classic` layouts.

### Fixed
- **Page background now covers the full page, including margins.** The
  previous `html { background }` rule only filled the content box in
  WeasyPrint — margins stayed white, making every page look like a framed
  card. Added `@page { background: var(--page-bg) }` to both layouts.
- **Cover no longer looks detached from the body.** Same root cause as
  above — the cover content sat on the page background but the margins
  were white, making page 1 read as a separate sheet. Fixed by the @page
  background change.
- **RTL bullets and ordered-list numbers now render on the right side.**
  Lists previously used `margin-left`/`margin-right` for the indent,
  which left markers on the left in Arabic documents (WeasyPrint doesn't
  auto-flip marker position from `dir="rtl"` alone). Switched to
  `padding` for the indent and added explicit `::before` pseudo-markers
  for RTL, scoped to avoid interfering with `.steps` counters.

## [0.1.0] — 2026-04-22

First public release. Extracted from a private working copy; scrubbed and
packaged with an installer.

### Added
- **Domains:** `business-proposal`, `tutorial`.
- **Doc types:** proposal, one-pager, letter (business-proposal); how-to,
  onboarding, cheatsheet, tutorial, handoff (tutorial).
- **Languages:** English + Arabic (peer templates, not machine translation).
- **Output:** PDF via WeasyPrint (HTML + CSS).
- **Cover styles:** `neural-cartography` (Gemini), `minimalist-typographic`
  (CSS only, no API key required), `friendly-illustration` (Gemini).
- **Interior layouts:** `classic`, `workbook`.
- **Brand profile system (v1.4):** per-project YAML configs at
  `~/.katib/brands/<name>.yaml`. CSS injection defense (positive regex
  whitelist), `max_height_mm` bounds, bilingual fallback (`name_ar`,
  `legal_name_ar`, `identity_ar`), logo format whitelist, `.yml` parity,
  warnings for unknown color keys and `--brand-file` shadowing.
- **Logos:** Tutorial covers + business-proposal letterheads.
- **Inline SVG diagrams:** `references/diagrams.md` + `{{ colors.<name> }}`
  Jinja context — works around WeasyPrint's inability to resolve CSS `var()`
  inside SVG attributes.
- **Screenshots:** Playwright capture + Pillow annotate + CSS frames
  (`browser-safari`, `macos-window`, `shadow-only`), content-addressed cache,
  bilingual alt/caption bundles.
- **Fonts:** 4 OFL families bundled — Newsreader, Inter, Amiri, Cairo.
- **Feedback loop:** Inline passive capture to
  `~/.local/share/katib/memory/*.jsonl`.
- **Installers:**
  - `npx katib` — Node wrapper (primary, cross-shell, version-pinnable via npm)
  - `install.sh` — bash installer (curl-friendly, no Node required)
  - Both perform: prereq checks, auto git-clone to `~/.claude/skills/katib/`,
    Playwright setup, vault-aware config bootstrap, optional Gemini API key prompt.
- **Logo + brand marks** in `assets/` (`logo.png`, `logo-horizontal.png`,
  `logo-square-bilingual.png`, `favicon.png`, `logo.svg`).

### Known limitations
- Native Windows unsupported; use WSL2.
- DOCX output not supported (drop by design — edit source and re-render).
- Only two domains ship in v0 (`business-proposal`, `tutorial`).
  `formal`, `personal`, `marketing-pitch`, `editorial` are deferred.
- **Fonts not bundled** — install Newsreader, Inter, Amiri, Cairo
  separately (see README Fonts section). A later release may bundle them.

[0.1.0]: https://github.com/jneaimi/katib/releases/tag/v0.1.0
[0.1.1]: https://github.com/jneaimi/katib/releases/tag/v0.1.1
[0.1.2]: https://github.com/jneaimi/katib/releases/tag/v0.1.2
[0.2.0]: https://github.com/jneaimi/katib/releases/tag/v0.2.0
[0.3.0]: https://github.com/jneaimi/katib/releases/tag/v0.3.0
