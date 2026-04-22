# Changelog

All notable changes to Katib are documented here. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.13.0] — 2026-04-22

### Added
- **`scripts/feedback.py` — CLI for logging user corrections to `feedback.jsonl`.** Closes the signal-capture side of the reflect loop: v0.10.0 added reflect.py's `string-swap` detection, but the underlying `log_feedback()` helper was a Python API no one invoked mid-conversation. A `python3 scripts/feedback.py add …` one-liner makes it the natural step after "change X to Y" corrections.
  - **Three subcommands.** `add --before X --after Y --domain tutorial --lang en [--reason …] [--doc …]` writes a row. `list [--since 7d] [--domain …] [--lang …] [--limit N]` prints recent rows (most recent last). `search <term>` finds rows where the term appears in either the `before` or `after` field.
  - **Round-trip verified**: three identical `add` calls in a domain/lang make `reflect.py --json` emit a `string-swap` proposal with `count=3`; one-off corrections stay correctly below the threshold.
- **`scripts/test-feedback.sh`** — 8-step harness covering: add-flag validation, row shape, idempotent multi-add, list, list filters, search (hit + miss), reflect integration (string-swap fires at 3), single correction suppressed at threshold. Uses a scratch `.katib/config.yaml` to isolate memory.location so the live vault stays clean.

### Changed
- **`SKILL.md` — `Inline feedback capture` section rewritten.** The old guidance showed `from memory import log_feedback` — but Claude can't import Python modules interactively. Replaced with the bash one-liner + a list/search cheatsheet so Claude actually has a callable command after the user says "change X to Y" in a Katib conversation.

### Context
- reflect.py has always been able to surface `string-swap` proposals. The bottleneck was the input side: corrections happened in conversation, got applied to templates, but never reached `feedback.jsonl`. v0.13.0 removes that gap — Claude now runs one command after each correction, and the same `before → after` pair recurring ≥3 times in a domain/lang produces an actionable proposal in the next reflect run.

### Tests
- `test-feedback.sh`: 8/8 steps pass.
- No regressions: `test-add-domain.sh` 11/11, `test-ar-svg.sh` 8/8, `test-install-fonts.sh` 8/8.

### Philosophy
- v0.10.x built the diagnostic half of the self-improvement loop (capture, cluster, propose). v0.11.0 built the execution half (`add_domain.py`). v0.13.0 closes the input side that had silently starved the loop. Each correction the user makes is now a durable data point — the skill learns what it renders worse than the user wants, and reflect can finally surface it.

## [0.12.0] — 2026-04-22

### Added
- **`scripts/install_fonts.py` — fetch the 7 OFL fonts Katib depends on** and drop them in the OS-standard user font directory (`~/Library/Fonts/Katib/` on macOS, `~/.local/share/fonts/Katib/` on Linux). Previously, a fresh machine produced technically-valid PDFs where Amiri silently rendered as Times, Cairo as Arial, Inter as Helvetica — the templates compiled but the typography was wrong. Installer closes that silent-failure path.
  - **7 families, 18 files**: Cairo (variable AR sans), Amiri (AR serif, 4 statics), Tajawal (AR corporate sans, 3 statics), IBM Plex Sans Arabic (AR fallback, 4 statics), Inter (variable EN sans + italic), Newsreader (variable EN serif + italic), JetBrains Mono (variable EN mono + italic). Total fetch: ~5 MB over the wire.
  - **Source**: `github.com/google/fonts` raw files (OFL-1.1 collection, tracked from upstream).
  - **Five modes**: `--list` (manifest, no network), `--verify` (check what's installed vs the manifest), default install (fetch missing), `--force` (re-download all), `--dry-run` (preview only). `--only "Cairo,Amiri"` limits to a subset.
  - **Safety**: small-response guard (<1 KB = 404 HTML disguised as OK), percent-encodes variable-font names like `Cairo[slnt,wght].ttf`, logs SHA-256 of every download for future pinning, skips files already present unless `--force`, calls `fc-cache` on Linux to refresh fontconfig.
  - **Windows**: not supported in v0.12.0 — exits with guidance to install manually from the same URLs.
- **`scripts/test-install-fonts.sh`** — 8-step harness with live-network tests that auto-skip when offline. Asserts: `--list` offline, unknown `--only` family rejected, `--dry-run` pure, JetBrains Mono variable-font fetched (187 KB), re-run idempotent (skipped=2), `--force` re-fetches and refreshes mtime, `--verify` distinguishes 2 installed vs 16 missing, Amiri family (4 static files) fetched.

### Context
- WeasyPrint resolves font families through fontconfig (macOS/Linux). If a family name in `tokens.json` isn't in the OS font cache, WeasyPrint falls back silently without a warning — templates compile, PDFs ship, but a document meant to render in Amiri ships in the system serif.
- Bundling fonts in the npm package was considered and rejected: the npm distribution would carry ~5 MB of binaries for a skill that many users won't even render AR content with. Fetch-on-install keeps the package lean and makes font presence explicit/opt-in.

### Tests
- `test-install-fonts.sh`: 8/8 steps pass (live network).
- No regressions: `test-add-domain.sh` 11/11, `test-ar-svg.sh` 8/8.

### Philosophy
- v0.12.0 fixes a failure mode that was invisible before: renders looked "fine" without the required fonts because the system fonts are adequate *as fallbacks* — they just aren't what the domain declared. The installer makes font state explicit, and `--verify` gives a one-command answer to "why doesn't my AR Amiri render look right."

## [0.11.0] — 2026-04-22

### Added
- **`scripts/add_domain.py` — one-command domain scaffolder.** Closes the self-improvement loop: `reflect.py`'s `new-domain-candidate` proposals are now actionable with a single command. Given a slug, generates `domains/<name>/tokens.json` + `styles.json` + skeleton templates (one per doc-type × lang) and patches the two router tables in `SKILL.md`. After writing, runs `build.py --check` automatically to verify the scaffold is valid.
  - **Three operating modes:** interactive Q&A (`python3 scripts/add_domain.py <name>`), non-interactive from JSON (`--from-json <file>`), and dry-run (`--dry-run` — prints plan, writes nothing).
  - **Eight palette presets**: `warm`, `cool`, `emerald`, `burgundy`, `navy-gold`, `editorial-red`, `slate`, `neutral`. Each defines all 13 semantic-color tokens that domains rely on (`--page-bg`, `--accent`, `--border`, `--tag-bg`, etc.) — inspect with `--list-presets`.
  - **Four font presets**: `sans-modern` (Inter/Cairo), `serif-editorial` (Newsreader/Amiri), `serif-formal` (Georgia/Amiri), `corporate` (Arial/Tajawal). EN + AR pair correctly for each.
  - **Safety rails**: refuses to overwrite existing domains without `--force`; rejects invalid slugs (must match `^[a-z][a-z0-9-]*[a-z0-9]$`); `SKILL.md` patching is idempotent (re-scaffolding with `--force` does not duplicate router/doc-type rows).
  - **Skeleton templates** are minimal but valid — include cover page (minimalist-typographic), one heading, a "skeleton note" callout explaining what to edit, and two section stubs. Render successfully out of the box; authors replace the content with real structure.
- **`scripts/test-add-domain.sh`** — 11-step test harness with scratch-copy isolation: asserts dry-run is pure, six files land correctly, tokens/styles JSON is well-formed, `build.py --check` passes, EN + AR renders produce non-empty PDFs, `SKILL.md` has exactly one router + one doc-type row placed in the right tables, overwrite protection works, `--force` is idempotent, invalid names rejected.

### Context
- Before v0.11.0, `reflect.py` could surface `new-domain-candidate` proposals but adding a domain was a 30-minute manual scaffold (copy tutorial, rewrite tokens, fix 10 fields, update SKILL.md twice, debug broken templates). This patch collapses that to one command.
- Skeleton templates explicitly reference `references/design.<lang>.md` + `references/writing.<lang>.md` in their body copy so authors see exactly which spec files to read before filling in content.

### Tests
- `test-add-domain.sh`: 11/11 steps pass.
- `test-ar-svg.sh`: 8/8 pass (no regression on the v0.10.2 AR-in-SVG lint).
- Confirmed the scaffold produces valid PDFs in both EN (2 pp) and AR (2 pp) for the `slate`/`sans-modern` preset.

### Philosophy
- v0.10.x closed the *diagnostic* side of the self-improvement loop (capture runs, surface clusters, flag candidates). v0.11.0 closes the *execution* side — reflect's output becomes input to a generator. The skill now grows by running.

## [0.10.2] — 2026-04-22

### Added
- **CSS-lint rule: Arabic text inside `<svg>`** — `build.py --check` now fails the build if any `*.ar.html` template embeds Arabic characters in a `<text>` or `<tspan>` element nested in `<svg>`. WeasyPrint's SVG renderer does not shape Arabic, so this catches the class of silent-failure bugs that shipped the walkthrough's first AR render broken. Violation message names the offending file and points at the `.diagram-stage` overlay pattern in `references/diagrams.md`.
- **`references/diagrams.md`: "Bilingual diagrams (Arabic labels)" section** — documents the `.diagram-stage` + `.diagram-label` primitive, the viewBox-percentage coordinate math, a copy-paste worked example, and the when-to-reach-for-English-vs-Arabic split. Canonical path for RTL diagrams going forward.
- **`scripts/test-ar-svg.sh`** — test harness with 4 cases, 8 assertions: clean skill passes, bad AR template is rejected with a helpful violation, overlay-pattern template passes, and English SVG text in an AR template is allowed (no false positive).

### Changed
- **`reflect.py`: bootstrap-noise suppression** for the `unused-doc-type` proposal. When fewer than 20 runs have been logged in the active window, the check is suppressed entirely and replaced with a one-line suppression note (`_\`unused-doc-type\` proposals suppressed (N runs < 20 minimum)_`). Above 20 runs, behaviour is unchanged. Rationale: day-two installs were flagging every template as a deprecation candidate, producing ~40 false positives per report.

### Tests
- `test-ar-svg.sh` passes: 8/8 assertions.
- Existing harnesses (`test-all`, `test-tutorial`, `test-brand`, `test-alt-bundles`, `test-images`) — all still pass. Batch render of all 34 doc types × 2 langs: 80/80 pass.

### Philosophy
- The Arabic-in-SVG fix is now a shape *and* a guard. v0.10.1 shipped the `.diagram-stage` primitive as a one-off workaround; v0.10.2 promotes it to the canonical path documented in `diagrams.md` with a lint rule behind it. Future AR templates can't regress this silently.

## [0.10.1] — 2026-04-22

### Added
- **`katib-walkthrough` doc type** (tutorial domain) — a full self-documenting Katib tutorial, rendered bilingually (EN + AR) as the first real dogfood of the ADR's complete scope: jasem brand cascade, Gemini `friendly-illustration` cover, four inline SVG diagrams, colour-swatch palette, cheatsheet grid, 13 pages per language. Target 8–18 pp, limit 25 pp. Reference prefix `TUT-KATIB-*`.
- **`.diagram-stage` / `.diagram-label` CSS primitive** for Arabic-safe SVG diagrams. Positions Arabic text as HTML overlays at viewBox-percentage coordinates on top of an SVG that carries only geometry, English labels, and numeric axes.

### Fixed
- **Arabic-in-SVG shaping.** WeasyPrint's native SVG text renderer does not run Arabic shaping via HarfBuzz — letters render in isolated presentation forms and do not join. Verified with a minimal test (`كاتب — الدليل` → `بتاك — ليلدلا` in extracted text). `foreignObject` does not fall back to the HTML text path either. Workaround: move Arabic `<text>` out of SVG into positioned HTML divs inside a `.diagram-stage` wrapper. Verified end-to-end — all 14 distinct Arabic diagram labels in `katib-walkthrough.ar.html` now extract as properly-shaped strings from the rendered PDF.

### Changed
- Tutorial domain `styles.json`: `katib-walkthrough` doc_type registered.

### Philosophy
- The Arabic-in-SVG fix is a shape, not just a one-off patch. Any future AR template embedding Arabic text in SVG will hit the same bug; using the `.diagram-stage` overlay pattern as the canonical path keeps RTL diagrams renderable indefinitely. To be captured in `references/diagrams.md` + a CSS-lint rule in a follow-up.

## [0.10.0] — 2026-04-22

### Added
- **Self-improvement loop (`reflect.py`) — the ADR's deferred v0.2 command lands.** Reads the three passive-capture logs (`runs.jsonl`, `feedback.jsonl`, `domain-requests.jsonl`) under the configured `memory.location` and surfaces three proposal types when a pattern recurs ≥3 times: `string-swap` (repeated before→after corrections → audit `references/writing.<lang>.md` + templates), `new-domain-candidate` (repeated routes to the same closest-match domain → consider a new domain or doc_type), `unused-doc-type` (zero renders in the window → flag for possible deprecation).
- `scripts/reflect.py` CLI: `--since Nd|Nw|all` (default 30d), `--domain <d>`, `--stats`, `--propose` (write Markdown proposal to `<memory>/proposals/<ts>-reflect.md`), `--json` (machine-readable output). Read-only by design — applying proposals stays manual.
- `scripts/memory.py` — shared helper module with `log_run`, `log_feedback`, `log_domain_request`, `read_jsonl`, `filter_since`. Ensures every log row carries a UTC ISO timestamp and non-ASCII-safe Arabic fields.
- Passive capture is **now actually wired.** `build.py` calls `log_run()` at the end of every successful render, writing one line per PDF to `runs.jsonl` (domain, doc, lang, layout, cover_style, pages, brand, output path).

### Changed
- `SKILL.md`: "Inline feedback capture (v0 passive logging)" section rewritten to reflect that (a) `build.py` genuinely writes to `{memory.location}/runs.jsonl` now, and (b) there is a live Reflect command to read those logs. Added the proposal-trigger table and the read-only-by-design note.
- `SKILL.md` Step 7 build block closes with a pointer to Reflect for template evolution.

### Philosophy
- Thresholds stay conservative: 3-count minimum across a 30-day window. Proposals surface leads; humans decide. No auto-edits in v0 — drift risk on weak signal outweighs convenience.

## [0.9.0] — 2026-04-22

### Added
- **New domain: `legal` — the final planned domain.** Contract-grade bilingual templates for UAE commercial instruments. Four doc types:
  - `service-agreement` — full commercial services contract with 12 clauses (parties, recitals with WHEREAS/IT IS AGREED, definitions, scope, fees + UAE VAT, term/termination, IP with Background/Foreground split, warranties, confidentiality, liability cap, force majeure, governing law, general provisions), and a dedicated execution page with witness slot. 5–12 pp.
  - `mou` — memorandum of understanding with explicit binding/non-binding clause flags (binding: confidentiality, governing law, costs; non-binding: the rest). Parties, background, purpose, scope, responsibilities, term, signatures. 2–5 pp.
  - `nda` — mutual NDA (one-way variant ready by removing reciprocal phrasing). Inline parties block, purpose, definition, obligations, exceptions, 2/5-year term (general/trade-secret), return-of-materials, remedies (injunctive relief), governing law. 2–4 pp.
  - `engagement-letter` — professional-services engagement for consultants/advisors. Letterhead + recipient block + subject box + scope box + fee table (fixed vs T&M) + timeline + liability cap + closing + Client-acceptance box with signature fields. 2–4 pp.
- Classic legal palette: navy `#1E3A5F` on white, Newsreader (EN) + Amiri (AR) serif. Conservative, enforceable, scannable.
- **Auto-numbered nested clauses** via CSS counter (`ol.clauses` primitive) — parties reference clauses by number during negotiation; inserting a clause renumbers automatically.
- **Defined-term capitalisation pattern:** `"Services"`, `"Confidential Information"`, `"Effective Date"` — capitalised and styled with `.defined-term` class.
- **Recitals block** with stylised `WHEREAS` / `حيث إنّ` clauses and a framed "Now, therefore" / «عليه، وبناءً على...» operative transition to signal the commercial-to-legal pivot.
- **Signature grid with witness slot** on service-agreement; 2-column acceptance on engagement-letter.
- **Template-notice disclaimer strip** on every legal doc — amber tinted — directing parties to counsel before execution. Not removable; only editable.
- SKILL.md router: "service agreement / MOU / NDA / non-disclosure / engagement letter / اتفاقية خدمات / مذكّرة تفاهم / عدم إفصاح / خطاب تعاقد" → `legal` domain. Doc-type picker table added.
- `references/writing.{en,ar}.md`: legal section covering the templates-are-not-advice top rule, defined-terms capitalisation discipline, nested-clause numbering, governing-law-is-non-negotiable, WHEREAS semantic weight, MOU binding-vs-non-binding signalling, page-break-before signature blocks, mutual-vs-one-way NDA discipline, numbers-and-words double-writing for fees/terms, Arabic legal phrasing conventions.
- Reference-code formats: `SA-{YYYY}-{NNN}`, `MOU-{YYYY}-{NNN}`, `NDA-{YYYY}-{NNN}`, `EL-{YYYY}-{NNN}`.

### Changed
- Roadmap complete: **all 9 planned domains are live.** `business-proposal` (v0.1.0), `tutorial` (v0.1.0), `report` (v0.2.0), `formal` (v0.3.0), `personal` (v0.4.0), `academic` (v0.5.0), `financial` (v0.6.0), `editorial` (v0.7.0), `marketing-print` (v0.8.0), `legal` (v0.9.0). **9 domains · 33 doc types · 66 bilingual templates.**

## [0.8.0] — 2026-04-22

### Added
- **New domain: `marketing-print`.** Print-grade sales and pitch materials. Four bilingual doc types:
  - `sell-sheet` — full-bleed dark hero + value-stripe (3 big numbers) + numbered feature grid + value-list + testimonial strip + orange CTA band. Single dense page. 1–2 pp.
  - `product-brief` — masthead + problem/solution split (grey vs orange tint) + how-it-works + 2×2 benefits grid + specs table + 3-tier pricing (with featured tier) + contact footer. 2–4 pp.
  - `capability-statement` — ink band + quick-facts row + about/mission grid + 4×2 competencies grid + differentiators list + past-performance ledger (client · scope · year) + orange contact strip (license, TRN, contact). 1–2 pp.
  - `slide-deck` — **landscape A4** · title slide with dark hero + section dividers (large faded chapter numbers) + content slides (bullets, two-col, big-figure, quote, CTA) with consistent footer bar (brand + page counter). 8–25 slides.
- Orange `#EA580C` accent on ink + white — high-contrast sales palette. Inter (EN) + Cairo (AR) sans-serif.
- **Slide-deck primitives:** `A4 landscape` page rule, 8mm accent stripe on title and quote slides, 180pt big-number slide, 140pt faded chapter number on dividers, CTA slide with inverted colour treatment. RTL decks mirror the accent stripe and chapter number side.
- **Sell-sheet hero band** bleeds to page edge via negative margins — full-bleed without manual page-box hacks.
- **Pricing tier featured card** — 2pt accent border + tint background to visually elevate the middle tier.
- **Capability-statement past-performance ledger** — client · scope · year grid optimised for 30-second procurement scan.
- SKILL.md router: "sell sheet / product brief / capability statement / slide deck / pitch deck / ورقة بيع / موجز منتج / بيان قدرات / عرض تقديمي" → `marketing-print` domain. Doc-type picker table added.
- `references/writing.{en,ar}.md`: marketing-print section on outcome-over-activity opens, one-claim-per-page discipline, big-numbers need provenance, capability-statement procurement scannability, slide-from-the-back-of-the-room type rules, section-dividers-as-rest-stops, one-CTA-per-artifact rule, testimonial specificity, Arabic slide mirroring.
- Reference-code formats: `SS-{YYYY}-{NNN}`, `PB-{YYYY}-{NNN}`, `CAP-{YYYY}`, `DECK-{YYYY}-{NNN}`.

### Changed
- Roadmap renumbered: `marketing-print` is now **live** (was v0.8 deferred).

## [0.7.0] — 2026-04-22

### Added
- **New domain: `editorial`.** Long-form thought leadership. Four bilingual doc types:
  - `white-paper` — dedicated title page + executive-summary block + drop-capped body + pull quotes + data tables + footnotes + author bio. Covers allowed (minimalist + neural-cartography). 10–25 pp.
  - `article` — magazine masthead + deck + byline + rising-cap body + blockquote with attribution + section § glyphs + mini-headings + byline footer. 3–8 pp.
  - `op-ed` — centred kicker + bold title + italicised deck + byline with role + indented-paragraph body + single pull-line + disclaimer. 1–3 pp.
  - `case-study` — kicker + outcome-led title + fact-box (industry/size/region/engagement) + result hero (+42%) + challenge / approach / results metrics / testimonial / lessons / next. 3–8 pp.
- Magazine-red accent `#B91C1C` + ink on warm newsprint `#FAFAF5`. Newsreader serif (EN) + Amiri (AR) with generous leading for long-form reading.
- **Editorial primitives:** rising cap (`::first-letter` styled but WeasyPrint-safe — no `float`), center-aligned pull quotes bracketed by thin accent rules, left-ruled blockquotes with attribution, § section glyphs on article headings, result-hero stripe on case-study.
- **Indented paragraphs on op-ed** — traditional editorial typography with second-and-later paragraphs indented (`p + p { text-indent: 14pt }`).
- **Timeline + metric-card primitives on case-study** — reusable phase rail with dot markers, 3-up metric cards with tabular-nums.
- SKILL.md router: "white paper / article / op-ed / opinion / thought leadership / case study / ورقة بيضاء / مقال / رأي / دراسة حالة" → `editorial` domain. Doc-type picker table added.
- `references/writing.{en,ar}.md`: editorial section covering lead-with-the-reader discipline, white-paper thesis commitment, earned-quote rule, op-ed opinion-vs-analysis line, case-study outcome-over-activity rule, drop-caps as editorial gesture, pull-quote-as-editing, footnote weight discipline, steel-man the opposition.
- Reference-code formats: `WP-{YYYY}-{NNN}`, `ART-{YYYY}-{NNN}`, `OP-{YYYY}-{NNN}`, `CASE-{YYYY}-{NNN}`.

### Changed
- Roadmap renumbered: `editorial` is now **live** (was v0.7 deferred).

### Fixed
- Editorial drop caps avoid `::first-letter { float }` due to a WeasyPrint `BlockReplacedBox` assertion. Rising-cap styling is used instead — larger first letter, no float, no layout crash.

## [0.6.0] — 2026-04-22

### Added
- **New domain: `financial`.** UAE-aware financial documents. Four bilingual doc types:
  - `invoice` — UAE VAT-compliant tax invoice. Masthead + parties (Bill From / Bill To) with TRN blocks + meta strip (invoice date / supply date / due date / currency) + line items with VAT column + subtotal/VAT/total + amount-in-words block + payment terms + bank details + authorised signature. Ready for Federal Tax Authority. 1–2 pp.
  - `quote` — Commercial quotation with scope (inclusions + explicit exclusions), pricing table, VAT totals, payment schedule, timeline, validity, and dual-signature acceptance block. 1–3 pp.
  - `statement` — Statement of account with balance-summary hero (opening / invoiced / received / closing), transactional ledger with debit/credit/balance columns, and colour-coded ageing buckets (current / 1–30 / 31–60 / 61–90 / 90+ days). 1–3 pp.
  - `financial-summary` — Executive review with 4-KPI hero cards (revenue / gross profit / operating margin / cash), P&L variance table, revenue-mix bars, and management commentary (what's working / what's at risk / outlook). 2–5 pp.
- Emerald `#0F5F4E` + slate palette on warm ivory `#FBFAF5`. Inter (EN) + Cairo (AR) for numeric clarity. Distinct from report (slate+teal) and formal (institutional navy).
- **UAE VAT compliance primitives:** TRN field rendered LTR inside RTL cells via `direction: ltr; unicode-bidi: embed`, VAT column separated from unit price, zero-rated row example, full UAE tax-law footer citation (Fed. Decree-Law No. 8 of 2017).
- **Numeric hygiene:** all amounts force LTR embedding so `AED 17,600.00` reads identically in both languages. 15-digit TRN stays Latin-numeric in both languages (tax-authority requirement).
- **Ageing-bucket colour coding:** green for current, amber for 31–60 / 61–90, red for 90+ — the receivables clerk scans this in under a second.
- **KPI delta colour trio** on financial-summary: `.up` success-green, `.down` danger-red, `.flat` muted-grey — consistent across metrics.
- SKILL.md router: "invoice / tax invoice / quote / quotation / statement / financial summary / فاتورة / فاتورة ضريبية / عرض سعر / كشف حساب / ملخّص مالي" → `financial` domain. Doc-type picker table added.
- `references/writing.{en,ar}.md`: financial section covering UAE VAT invoice mandatory fields, TRN formatting, currency LTR embedding, amount-in-words as legal cross-check, quote inclusions/exclusions discipline, ageing-bucket conventions, financial-summary commit-to-a-number rule, and zero-rated vs exempt distinction.
- Reference-code formats: `INV-{YYYY}-{NNN}`, `QUO-{YYYY}-{NNN}`, `STM-{YYYY}-{MM}`, `FIN-{YYYY}-Q{Q}`.

### Changed
- Roadmap renumbered: `financial` is now **live** (was v0.6 deferred).

## [0.5.0] — 2026-04-22

### Added
- **New domain: `academic`.** Course-facing and research-facing documents for educators, students, and researchers. Four bilingual doc types:
  - `syllabus` — masthead + instructor meta grid + course description + learning objectives + weekly schedule table + grading-weights table + policies (attendance, late work, integrity, accommodations). 3–6 pp.
  - `assignment-brief` — eyebrow masthead + due-date banner with weight % + task required elements + deliverables box + rubric table with criteria/weights + submission instructions + integrity callout. 2–4 pp.
  - `lecture-notes` — course/lecture header + learning-objectives box + two-column layout (main content + margin notes: prerequisite, common mistake, historical note, why-it-matters, next-lecture teaser) + definitions + formula block + worked-example box + exercises + further reading. 4–12 pp.
  - `research-proposal` — dedicated title page + abstract with keywords + research questions + hypotheses + literature review with explicit gap paragraph + methodology (design, sample, analysis, ethics) + phased timeline table + expected outcomes + itemised budget table + references. 8–20 pp.
- Editorial-academic palette: burgundy `#7E1D4A` + sage `#5F6B3C` on cream `#FBF8F2`. Newsreader serif (EN) + Amiri (AR) — distinct from report (slate+teal) and formal (institutional navy).
- Two-column `content-grid` on lecture-notes places sticky-note-style margin rail that mirrors correctly in RTL (no flip needed — grid handles it).
- Margin-note labels use Arabic terms in AR (`متطلّب سابق`, `خطأ شائع`, `لمحة تاريخية`, `لماذا يهمّ`, `المحاضرة القادمة`) — not literal translations.
- Pre-structured rubric rows and budget rows ready-to-fill for typical patterns (5-criterion rubric + 5-category budget).
- SKILL.md router: "syllabus / assignment / lecture notes / research proposal / خطة مقرر / واجب / محاضرة / مقترح بحثي" → `academic` domain. Doc-type picker table added.
- `references/writing.{en,ar}.md`: academic section covering measurable objectives (Bloom's verbs), syllabus-as-contract discipline, rubric-first assignment briefs, lecture-notes compression, proposal commitment language (no hedge), gap-paragraph centrality, citation-style consistency, and Arabic numeral-convention in running text vs equations/years.
- Reference-code formats: `SYL-{YYYY}-{NNN}`, `AB-{YYYY}-{NNN}`, `LN-{YYYY}-{NNN}`, `RP-{YYYY}-{NNN}`.

### Changed
- Roadmap renumbered: `academic` is now **live** (was v0.5 deferred).

## [0.4.0] — 2026-04-22

### Added
- **New domain: `personal`.** Career documents for GCC job seekers. Three bilingual doc types:
  - `cv` — two-column layout (navy sidebar + main) with pre-structured GCC-aware fields: photo slot, nationality, visa status, date of birth, languages with proficiency bars, core skills with level bars, tools tags. Main column covers summary, experience (role + dates + employer + achievements), education, and selected projects. 1–2 pp.
  - `cover-letter` — personal masthead, date, recipient block, subject line, three-paragraph body, signature, enclosure note. 1 page.
  - `bio` — hero row (photo + name + headline + specialty tags) plus long-form About plus Short/Medium variants side-by-side plus contact footer. 1 page.
- Clean recruiter-friendly palette: navy `#1E3A8A` sidebar on warm `#FDFCF8` paper. Inter (EN) + Cairo (AR) sans-serif.
- Skill level bars: 5-tier system (`l2` through `l5`) rendered as horizontal fills; mirror correctly in AR (fill starts from the right).
- LTR-embedded contact values (email, phone, LinkedIn handles, dates) inside RTL Arabic CV cells.
- SKILL.md router: "CV / resume / cover letter / bio / سيرة ذاتية / خطاب تغطية / نبذة" → `personal` domain. Doc-type picker table added.
- `references/writing.{en,ar}.md`: personal-domain section covering STAR/CAR bullet structure, verb-first openings, numeric achievements, GCC CV fields (photo, nationality, visa), and three-variant bios.
- Reference-code formats: `CV-{YYYY}`, `CL-{YYYY}-{NNN}`, `BIO-{YYYY}`.

### Changed
- Roadmap renumbered: `personal` is now **live** (was v0.4 deferred).

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
[0.4.0]: https://github.com/jneaimi/katib/releases/tag/v0.4.0
[0.5.0]: https://github.com/jneaimi/katib/releases/tag/v0.5.0
[0.6.0]: https://github.com/jneaimi/katib/releases/tag/v0.6.0
[0.7.0]: https://github.com/jneaimi/katib/releases/tag/v0.7.0
[0.8.0]: https://github.com/jneaimi/katib/releases/tag/v0.8.0
[0.9.0]: https://github.com/jneaimi/katib/releases/tag/v0.9.0
