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
| *(v0.7)* white paper, article, thought leadership | `editorial` | *(deferred)* |
| *(v0.8)* sell-sheet, product-brief, slide-deck (print PDF) | `marketing-print` | *(deferred)* |
| *(v0.9)* service-agreement, MOU, NDA | `legal` | *(deferred)* |

Formal live as of v0.3.0, personal live as of v0.4.0, academic live as of v0.5.0, financial live as of v0.6.0.

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

## Inline feedback capture (v0 passive logging)

After every delivery, `build.py` appends one line to `.katib-memory/runs.jsonl`:

```json
{"ts": "...", "domain": "...", "doc": "...", "lang": "...", "tier": "...", "output": "..."}
```

When the user makes a correction (explicitly says "change X to Y", "this phrasing is off", "wrong color"), capture it to `.katib-memory/feedback.jsonl`:

```json
{"ts": "...", "domain": "...", "lang": "...", "before": "...", "after": "...", "reason": "..."}
```

These logs feed future `/katib reflect` in v0.2. No commands in v0 — just capture.

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
