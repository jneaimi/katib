---
name: katib
description: "Generate print-grade bilingual (EN + AR) PDF documents — proposals, tutorials, letters, one-pagers, how-to guides, onboarding docs, cheatsheets. Use when the user says /katib, asks to create a proposal, commercial offer, SOW, tutorial, how-to, onboarding guide, formal letter, cover letter, PDF deliverable, or bilingual document for GCC/UAE audiences. Also triggers on 'make a proposal', 'build a tutorial', 'write a formal letter', 'create a handoff doc', 'generate PDF', 'اكتب عرضاً', 'اصنع دليلاً', 'انشئ مستنداً', 'خطاب رسمي'. Produces PDF via HTML + WeasyPrint."
---

# katib · كاتب

**كاتب (Katib)** — the writer. Print-grade bilingual document production.

One skill across six planned domains (v0 ships two), two output formats, two languages, pluggable cover + layout styles. Kaku writes code, Kami is paper — Katib is the writer who shapes the words onto it.

---

## Step 1 · Detect language

**Match the user's language.** Arabic request → `.ar.html` templates + Arabic references. English request → `.en.html` templates + English references.

When ambiguous (e.g. one-word "proposal"), ask a one-liner rather than guess.

| User language | Templates | References |
|---|---|---|
| English | `*.en.html`, `*.en.js` | `references/design.en.md`, `writing.en.md` |
| Arabic (MSA + خليجي) | `*.ar.html`, `*.ar.js` | `references/design.ar.md`, `writing.ar.md` |

## Step 2 · Pick domain

| User signal | Domain | Tokens |
|---|---|---|
| "proposal / SOW / commercial offer / عرض تجاري" | `business-proposal` | Navy `#1B2A4A` + Gold `#C5A44E`, Arial |
| "how-to / tutorial / onboarding / handoff / cheatsheet / دليل / شرح" | `tutorial` | Teal/slate on warm off-white, mono for code |
| "report / research / annual / audit / progress / تقرير / دراسة / تدقيق" | `report` | Slate `#2E3A4B` + teal accent, Newsreader serif |
| "NOC / formal / government / ministry / circular / authority / خطاب رسمي / شهادة عدم ممانعة / تعميم / تفويض" | `formal` | Institutional navy `#0B3D66` on off-white, Georgia/Amiri serif |
| "CV / resume / cover letter / bio / سيرة ذاتية / خطاب تغطية / نبذة" | `personal` | Navy `#1E3A8A` sidebar on warm paper, Inter/Cairo sans-serif |
| "syllabus / assignment / lecture notes / research proposal / خطة مقرر / واجب / محاضرة / مقترح بحثي" | `academic` | Burgundy `#7E1D4A` + sage on cream, Newsreader/Amiri serif |
| "invoice / tax invoice / quote / quotation / statement / financial summary / فاتورة / فاتورة ضريبية / عرض سعر / كشف حساب / ملخّص مالي" | `financial` | Emerald `#0F5F4E` + slate on warm ivory, Inter/Cairo sans |
| "white paper / article / op-ed / opinion / thought leadership / case study / ورقة بيضاء / مقال / رأي / دراسة حالة" | `editorial` | Magazine red `#B91C1C` + ink on warm newsprint, Newsreader/Amiri serif |
| "sell sheet / product brief / capability statement / slide deck / pitch deck / ورقة بيع / موجز منتج / بيان قدرات / عرض تقديمي" | `marketing-print` | Orange `#EA580C` + ink on white, Inter/Cairo sans |
| "service agreement / MOU / memorandum of understanding / NDA / non-disclosure / engagement letter / اتفاقية خدمات / مذكّرة تفاهم / عدم إفصاح / خطاب تعاقد" | `legal` | Navy `#1E3A5F` + ink on white, Newsreader/Amiri serif |

All planned domains are live. Formal (v0.3.0), personal (v0.4.0), academic (v0.5.0), financial (v0.6.0), editorial (v0.7.0), marketing-print (v0.8.0), legal (v0.9.0).

Unknown domain → route to closest, flag as mismatch in `.katib-memory/domain-requests.jsonl`.

## Step 3 · Pick doc type (within domain)

| Domain | Doc types |
|---|---|
| `business-proposal` | `proposal`, `one-pager`, `letter` |
| `tutorial` | `how-to`, `cheatsheet`, `tutorial`, `onboarding`, `handoff` |
| `report` | `research-report`, `progress-report`, `annual-report`, `audit-report` |
| `formal` | `noc`, `government-letter`, `circular`, `authority-letter` |
| `personal` | `cv`, `cover-letter`, `bio` |
| `academic` | `syllabus`, `assignment-brief`, `lecture-notes`, `research-proposal` |
| `financial` | `invoice`, `quote`, `statement`, `financial-summary` |
| `editorial` | `white-paper`, `article`, `op-ed`, `case-study` |
| `marketing-print` | `sell-sheet`, `product-brief`, `capability-statement`, `slide-deck` |
| `legal` | `service-agreement`, `mou`, `nda`, `engagement-letter` |

### Legal doc-type picker

| Doc type | Shape | Target pages | RC prefix | When |
|---|---|---|---|---|
| `service-agreement` | Parties + recitals + 12 clauses (definitions, scope, fees, term, IP, warranties, confidentiality, liability, force majeure, governing law, general) + signature page with witness slot | 5–12 | `SA-*` | Full commercial services contract |
| `mou` | Parties + background + purpose + scope + responsibilities + **non-binding** clause + binding sub-clauses (confidentiality, governing law, costs) + signatures | 2–5 | `MOU-*` | Pre-contract statement of intent |
| `nda` | Inline parties block + purpose + definition + obligations + exceptions + term + return-of-materials + remedies + governing law + signatures. Mutual and one-way variants | 2–4 | `NDA-*` | Confidentiality before disclosure |
| `engagement-letter` | Letterhead + recipient block + subject box + scope + fee table + timeline + liability + closing + Client-acceptance box | 2–4 | `EL-*` | Professional-services engagement (consulting, advisory) |

**All legal templates include a standard template-notice disclaimer strip.** Templates, not legal advice — have counsel review before execution.

### Marketing-print doc-type picker

| Doc type | Shape | Target pages | RC prefix | When |
|---|---|---|---|---|
| `sell-sheet` | Dark hero + value-stripe (3 big numbers) + feature grid + value list + testimonial + CTA band | 1–2 | `SS-*` | Single-page sales one-pager, trade-show handout |
| `product-brief` | Masthead + problem/solution split + how-it-works + benefits grid + specs table + pricing tiers + CTA | 2–4 | `PB-*` | Product or service detailed spec with pricing |
| `capability-statement` | Band header + facts row + about/mission grid + competencies grid + differentiators + past-performance + contact strip | 1–2 | `CAP-*` | Gov-contracting / B2B capability pager |
| `slide-deck` | **Landscape A4** · title + section dividers + content (bullet/two-col/big-figure/quote/CTA) with footer bar | 8–25 | `DECK-*` | Pitch decks, keynote slides, executive briefings — PDF export only |

### Editorial doc-type picker

| Doc type | Shape | Target pages | RC prefix | When |
|---|---|---|---|---|
| `white-paper` | Title page + executive summary + drop-capped body with pull quotes + data tables + footnotes + author bio | 10–25 | `WP-*` | Research-grade thought leadership, funder-facing analysis |
| `article` | Magazine masthead + deck + byline + drop-cap body + blockquote + pull-quote + mini-headings + byline footer | 3–8 | `ART-*` | Long-form magazine piece or blog essay |
| `op-ed` | Centred kicker + bold title + deck + byline + drop-cap body with one pull-line + disclaimer | 1–3 | `OP-*` | Opinion piece, position column, editorial commentary |
| `case-study` | Kicker + outcome title + fact-box (industry/size/region) + result hero + challenge/approach/results/lessons/next | 3–8 | `CASE-*` | Client success story, engagement narrative |

### Financial doc-type picker

| Doc type | Shape | Target pages | RC prefix | When |
|---|---|---|---|---|
| `invoice` | Masthead + parties (TRN) + meta strip + line items + VAT totals + amount-in-words + payment block | 1–2 | `INV-*` | UAE VAT tax invoice (Fed. Decree-Law No. 8 of 2017) |
| `quote` | Masthead + meta strip + scope (inclusions/exclusions) + pricing + totals + acceptance block | 1–3 | `QUO-*` | Commercial quotation / estimate before engagement |
| `statement` | Masthead + balance-summary hero + ledger + ageing buckets (current / 30 / 60 / 90+) | 1–3 | `STM-*` | Statement of account / receivables ageing |
| `financial-summary` | KPI cards + P&L table + revenue-mix bars + management commentary + outlook | 2–5 | `FIN-*` | Board / leadership financial review (quarterly, half-yearly, annual) |

### Academic doc-type picker

| Doc type | Shape | Target pages | RC prefix | When |
|---|---|---|---|---|
| `syllabus` | Masthead + meta + objectives + schedule table + grading + policies | 3–6 | `SYL-*` | Course overview for a semester or program |
| `assignment-brief` | Task heading + due banner + deliverables + rubric table | 2–4 | `AB-*` | Student-facing spec for a specific piece of assessment |
| `lecture-notes` | Main column + margin notes (prerequisite, common mistake, next lecture) + exercises | 4–12 | `LN-*` | Structured handout supporting a single lecture |
| `research-proposal` | Title page + abstract + questions + methodology + timeline + budget + references | 8–20 | `RP-*` | Funding application, thesis proposal, IRB submission |

### Personal doc-type picker

| Doc type | Shape | Target pages | RC prefix | When |
|---|---|---|---|---|
| `cv` | Two-column (navy sidebar + main) — contact, skills, languages, experience, education, projects | 1–2 | `CV-*` | Job application or professional profile |
| `cover-letter` | Masthead + date + recipient + subject + 3 paragraphs + signature | 1 | `CL-*` | Specific role application, tied to CV |
| `bio` | Hero (photo + name + tags) + long-form + short/medium variants + contact footer | 1 | `BIO-*` | Speaker intro, conference program, personal website, media kit |

### Formal doc-type picker

| Doc type | Shape | Target pages | RC prefix | When |
|---|---|---|---|---|
| `noc` | Pre-structured fields + purpose + validity + stamp block | 1 | `NOC-*` | UAE No-Objection Certificate for visa / school / bank / travel |
| `government-letter` | Islamic greeting + honorific + subject + formal body + closing formula | 1–2 | `GOV-*` | Submissions to ministries, authorities, regulators |
| `circular` | Distribution banner + TO/FROM/CC + subject + action items + effective date | 1–2 | `CIR-*` | Internal company-wide announcements and policy changes |
| `authority-letter` | Grantor/Grantee blocks + scope list + validity + stamp block | 1 | `AUTH-*` | Delegation of a specific act (not full POA) |

### Report doc-type picker

| Doc type | Shape | Target pages | RC prefix | When |
|---|---|---|---|---|
| `research-report` | Abstract + methodology + findings + discussion | 10–30 | `RPT-R-*` | Original research or analysis |
| `progress-report` | KPI cards + milestones + risks + next period | 5–15 | `RPT-P-*` | Periodic status update |
| `annual-report` | Letter + highlights + financials + outlook | 20–60 | `RPT-A-*` | Year-end institutional review |
| `audit-report` | Scope + severity matrix + findings + remediation | 10–25 | `RPT-AU-*` | Compliance, security, or process audit |

### Tutorial doc-type picker

| Doc type | Shape | Target pages | RC prefix | When |
|---|---|---|---|---|
| `how-to` | Linear steps + callouts | 2–6 | `HT-*` | Single task, one sitting |
| `cheatsheet` | Dense 2-column grid, no cover | 1–2 | `CS-*` | Reference card, keyboard shortcuts |
| `tutorial` | Multi-module w/ objectives + summary | 5–15 | `TUT-*` | Multi-session learning path |
| `onboarding` | Cover + TOC + parts + checklists | 10–25 | `ON-*` | New-hire / new-role orientation |
| `handoff` | Status banner + runbook + issues + contacts | 3–12 | `HT-*-###` | Transferring ownership |

Page-limit guardrails fire automatically from `styles.json`. Going over the `page_limit` fails the build (exit 3); going below the `target_pages` floor prints a warning but still ships.

## Step 4 · Output format

Katib produces PDF only. HTML + CSS → WeasyPrint. For editable Word deliverables, edit the source `.md` / HTML content in the output folder and re-render.

## Step 4.5 · Cover style

Read `domains/<domain>/styles.json` for whitelisted covers + default.

| Style | Engine | Cost | Good for |
|---|---|---|---|
| `neural-cartography` | Gemini (Nano Banana 2) | ~$0.12/image | business-proposal, formal — institutional weight |
| `minimalist-typographic` | CSS + SVG | free, deterministic | editorial, formal, personal, tutorial |
| `friendly-illustration` | Gemini (Nano Banana 2) | ~$0.12/image | tutorial — warm, approachable |

Override with `--cover <style>` if user asks.

**Cover text layer:** Arabic or English title/subtitle sit in HTML on top of the cover image. Never baked into the PNG. Covers are decorative only.

## Step 4.6 · Interior layout

Read `domains/<domain>/styles.json` for whitelisted layouts + default.

| Layout | Rhythm | Use |
|---|---|---|
| `classic` | Standard, per-domain tuning | Default for most |
| `workbook` | Numbered steps, callouts, code blocks, screenshots | Tutorial domain |

Override with `--layout <variant>`.

## Step 5 · Load spec tier

Pick the tier that matches the task. Default to the lowest that covers the work.

| Tier | When | Read |
|---|---|---|
| **Content-only** | Updating text in existing doc, translating, swapping bullets | `CHEATSHEET.{lang}.md` only |
| **Layout tweak** | Adjusting spacing, section order, font size within spec | `CHEATSHEET` + `design.{lang}.md` |
| **New document** | Building from scratch or from raw content | `design` + `writing` + `production.md` |
| **Diagram** | Embedding SVG in a doc | `diagrams.md` only |
| **Screenshot** | Tutorial with screenshots | `screenshots.md` + `tutorial-primitives.md` |
| **Troubleshoot** | Render bug, font issue, page overflow | `production.md` first |

Escalate mid-task if work turns out to need more.

## Step 6 · Distill raw content (if applicable)

Skip if the user hands over already-structured content.

When the user hands over **raw material** (meeting notes, brain dump, existing doc in a different format):

1. **Extract:** every factual claim, number, date, name, action item
2. **Classify:** map each extract to the target template's sections (see `references/writing.{lang}.md`)
3. **Gap-check:** list what the template needs but the raw content doesn't have — compact table
4. **Ask once:** share gap table. Do not guess to fill gaps.

Example gap-check:

| Template needs | Found | Missing |
|---|---|---|
| 4 metric cards | "8 years", "50-person team" | 2 more quantifiable results |
| 3-5 core projects | 2 mentioned | at least 1 more with outcome |

## Step 7 · Build & verify

```bash
python3 scripts/build.py --verify                       # build all + page count + font + placeholder check
python3 scripts/build.py --verify <target>              # single target
python3 scripts/build.py --check                        # CSS rule violations only (fast, no build)
python3 scripts/build.py --sync                         # cross-template token drift
```

For Gemini covers:

```bash
python3 scripts/cover.py --domain <d> --style <s> --lang <l> --out <path>
```

For screenshots (tutorial domain):

```bash
python3 scripts/shot.py web <url> --out <path> --device-scale 2
python3 scripts/annotate.py <path> --arrow x,y --label "..." --blur x,y,w,h
python3 scripts/frame.py <path> --style browser-safari
```

Site-config defaults (`~/.katib/sites/<name>.json`) let `shot.py --site <name>` inherit `hide`, `cookies`, `theme`, and `viewport` without re-typing. CLI flags always win.

`shot.py` content-addresses captures in `~/.katib/cache/screenshots/<hash>.png` — hash keys include url, resolved viewport, scale, theme, full-page/clip, wait-for/ms/until, hide selectors, and cookies-file SHA. Repeat captures with matching inputs skip Playwright (~50× faster). Opt out with `--no-cache`; `--force` re-captures and refreshes the cache entry. Override the cache dir with `--cache-dir` or `$KATIB_CACHE_DIR`. Inspect a planned key with `--dry-run`.

For bilingual captions and alt text, pass `--alt-en/--alt-ar/--caption-en/--caption-ar` — the sidecar stores a `{en, ar}` dict and `build.py` picks the right string per render language. Legacy `--alt/--caption` still work (applied to both languages). Missing-language falls back to EN with a `⚠ caption missing for lang='ar'` stderr warning. Sidecars are written with `ensure_ascii=False` so Arabic is readable in JSON.

For bilingual EN+AR co-location, pass the same `--slug` to both renders — `manifest.md` and `.katib/run.json` merge `languages`, `formats`, and `page_counts` across calls (instead of last-write-wins overwriting).

**Brand profiles.** Colors, fonts, identity, and logo swap per-project via `--brand <name>` (loads `~/.katib/brands/<name>.yaml` or `<skill>/brands/<name>.yaml`) or `--brand-file <path>`. Precedence: domain tokens → brand profile → CLI flags. A brand omitting a field falls back to the domain default, so partial brands are fine. See `brands/example.yaml` for the full schema. Bilingual: `name_ar` picks up automatically on AR renders. Logo (`logo: path.svg` or `logo: {primary, max_height_mm}`) renders on tutorial covers and business-proposal letterheads (proposal title page, one-pager, letter) — paths resolve relative to the brand file. List available profiles with `python3 scripts/build.py --list-brands`.

Test harnesses:

```bash
bash scripts/test-all.sh          # 3 business-proposal doc types × 2 langs = 6
bash scripts/test-tutorial.sh     # 5 tutorial doc types × 2 langs = 10
bash scripts/test-alt-bundles.sh  # alt/caption bundle resolution (18 assertions)
bash scripts/test-brand.sh        # brand profile loader + end-to-end render (14 assertions)
bash scripts/test-images.sh       # annotate + frame golden-image regression (8 goldens)
```

`test-images.sh` goldens are machine-local (captured with current Pillow + system fonts). On a Pillow upgrade or machine move, regenerate with `bash scripts/test-images.sh --regenerate` after reviewing the diff.

Visual anomalies → `references/production.md`.

Self-improvement & template evolution → see **Reflect** below.

## Step 8 · Vault integration

Katib is **vault-first by default**: every successful render lands as a governed
note in the Soul Hub vault. Outputs route based on `--project`:

| `--project <slug>` | Output lands under | Governed by |
|---|---|---|
| `katib` (default) | `<vault>/content/katib/<domain>/<slug>/` | `content/katib/CLAUDE.md` |
| anything else | `<vault>/projects/<slug>/outputs/<domain>/<slug>/` | `projects/CLAUDE.md` + `projects/<slug>/CLAUDE.md` |

Before rendering, Katib fetches the target zone's governance via
`GET /api/vault/zones/<path>` and validates the proposed manifest. If the zone
would reject the write, the build fails fast with exit code 4 — no PDF render
happens, no orphan folders get left behind.

Switch modes with `KATIB_VAULT_MODE`:

| Mode | Behaviour |
|---|---|
| `api` (default) | POST manifest to Soul Hub; pre-check governance; fall back to FS if the API is unreachable (adds a `katib-fallback` tag) |
| `strict` | Same as `api`, but fail hard on network errors — never fall back |
| `fs` | Skip the API entirely; write directly to the filesystem (offline-friendly for render tests) |

Disable pre-render governance checking with `--no-strict-governance` (useful
when developing against a zone whose `CLAUDE.md` is known-stale). For the full
story — endpoint contract, caching, fallback semantics, migration tooling — see
`references/vault.md`.

## Feedback protocol

When the user gives **vague feedback** ("looks off", "not elegant", "spacing weird", "غير لائق"):

Do not guess. Ask back using Katib vocabulary, with current values included.

| User says | Ask about |
|---|---|
| "too cramped" / "متضيّق" | Which element? Line-height (current X)? Padding (current Y)? Page margin? |
| "too loose" / "فضفاض" | Same direction, reversed |
| "colors feel off" / "الألوان غلط" | Which element? Accent overused? Neutral reading cool when it should be warm? |
| "not polished" / "ما يبيّن احترافي" | Font rendering? Alignment? Whitespace distribution? Hierarchy unclear? |

Template response: **"X is currently set to Y. Would you like (a) [specific alternative within spec] or (b) [another option]?"**

Never say "I'll adjust the spacing" without naming the exact property and its new value.

## Inline feedback capture

Every successful `build.py` render appends one line to `{memory.location}/runs.jsonl` (default `~/.local/share/katib/memory/`):

```json
{"ts": "...", "domain": "...", "doc": "...", "lang": "...", "layout": "...", "pages": N, "output": "..."}
```

When the user makes a correction (explicitly says "change X to Y", "this phrasing is off", "wrong color"), capture it via the `feedback.py` CLI **after** applying the edit. Reflect then receives real signal and surfaces a `string-swap` proposal once the same `before → after` pair recurs ≥3 times in one domain/lang.

```bash
python3 scripts/feedback.py add \
    --before "click" --after "select" \
    --domain tutorial --lang en \
    --reason "UI consistency"
```

Browse what's been logged:

```bash
python3 scripts/feedback.py list                 # last 20 rows
python3 scripts/feedback.py list --since 30d     # filter window
python3 scripts/feedback.py list --domain report # filter domain
python3 scripts/feedback.py search "click"       # rows where "click" appears in before or after
```

When the user requests a doc type that doesn't fit any existing domain, route to the closest and call `log_domain_request` so reflect can flag a candidate new domain.

## Reflect — surface self-improvement leads

```bash
python3 scripts/reflect.py                       # summary of last 30 days
python3 scripts/reflect.py --since 7d            # Nd | Nw | all
python3 scripts/reflect.py --domain tutorial     # filter to one domain
python3 scripts/reflect.py --stats               # counts only, skip proposals
python3 scripts/reflect.py --propose             # also write Markdown proposal to memory/proposals/
python3 scripts/reflect.py --json                # machine-readable
```

`reflect.py` reads the three jsonl logs and surfaces three proposal types — each fires only when a pattern recurs **≥3 times** in the window:

| Proposal | Trigger | Suggested action |
|---|---|---|
| `string-swap` | Same `before → after` correction ≥3× in one domain/lang | Audit `domains/<d>/templates/` + `references/writing.<lang>.md`; replace where universally correct |
| `new-domain-candidate` | ≥3 requests routed to the same closest-match domain | Review samples; add a doc_type to that domain or a new domain |
| `unused-doc-type` | A doc type in `styles.json` rendered 0 times in the window | Flag for possible deprecation; confirm before removing |

**reflect.py is read-only by design.** It does not edit templates, tokens, or references. Apply changes manually after reviewing the proposal — this keeps the skill from drifting on weak signal. When in doubt, widen the window (`--since 90d`) before acting.

---

## When not to use this skill

- User wants Material / Tailwind default UI — different design language entirely
- User wants dark / cyberpunk / futurist aesthetic — this is deliberately editorial
- Need cartoon / animation / illustration — this is for print/static documents
- User wants web dynamic app UI — this is for print deliverables

---

## Next steps

Apply Step 5's tier table to decide what to read. Then copy the matching template and start filling.

For new document types not in the current domain table, note it in `.katib-memory/domain-requests.jsonl` and route to the closest existing match.
