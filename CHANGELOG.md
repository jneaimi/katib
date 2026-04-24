# Changelog

All notable changes to Katib are documented here. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased] — v2 **Phase 3 COMPLETE** (close 2026-04-24, Day 21)

**Phase 3 closed.** 15 of 15 migrated recipes shipped. 11 new
components + 4 Phase-2 evolutions. 920 tests passing. Zero WeasyPrint
warnings across 25 render paths. Tutorial domain complete; business-
proposal + financial + personal domains complete; legal domain 25%
(3 recipes Deferred). Ready to tag as `v2.0.0-phase-3` and push to
origin/main.

### Added (Phase 3 Day 21 — `tutorial/katib-walkthrough` recipe ship; **PHASE 3 CLOSES AT 15/15**)

**FIFTEENTH AND FINAL Phase-3 recipe.** Largest by section count
(48 sections — beats mou's 25). Zero new components. Closes the
Phase-3 triage list.

- **`recipes/tutorial-katib-walkthrough.yaml`** (new) — comprehensive
  self-documenting katib walkthrough:
  - **Cover + preface**: cover-page minimalist-typographic (5th use) +
    lead paragraph + `objectives-box` ("What you'll learn") + inline
    checklist ("Before you begin").
  - **Module 1 — Install & first render**: 3 `tutorial-step` (3rd
    consumer) interleaved with inline code blocks for installer/
    config YAML/CLI sample + `callout tip` (KATIB_OUTPUT_ROOT tip).
  - **Module 2 — The ten domains**: inline SVG taxonomy diagram +
    `data-table` (**8TH production consumer** — domains quick-pick
    with 3 cols × 10 rows) + `callout info` ("How routing works").
  - **Module 3 — Brand profiles**: `objectives-box` + inline Jasem-
    brand palette swatches (5 colors) + brand YAML code + CLI usage
    + inline Do/Don't block.
  - **Module 4 — Covers/diagrams/screenshots**: `kv-list` (cover
    styles) + inline SVG screenshot pipeline + `callout info`
    ("When to use what").
  - **Module 5 — Reflect**: `objectives-box` + inline SVG reflect
    data-flow diagram + `kv-list` (3 proposal types) + inline CLI
    code + `pull-quote` (3RD PRODUCTION CONSUMER — "reflect.py is
    read-only" marker).
  - **Module 6 — Vault integration**: `objectives-box` + `kv-list`
    (project routing) + `kv-list` (mode matrix) + `callout info`
    ("Why this matters") + `kv-list` (5 admin scripts) + `kv-list`
    (exit codes) + `pull-quote` (CI strict-mode marker).
  - **Module 7 — Command cheatsheet**: `sections-grid` dense cols=2
    with **20 cheat-cards** (6TH sections-grid consumer, LARGEST
    items count ever) + `kv-list` (env vars) + `kv-list` (file
    layout).
  - **Closing**: Summary + What's next ul.
  Content adapted from `v1-reference/domains/tutorial/templates/
  katib-walkthrough.en.html`. Placeholder prose preserved (content
  references v1 CLI — Phase-4 task to rewrite for v2 architecture).
- **Rendered output: 14 pages, 0 WeasyPrint warnings.** `target_pages:
  [8, 16]`, `page_limit: 16`. Within target.
- **Validation clean at default + strict** — 0 content-lint warnings.
- **HEAVIEST kv-list deployment** — 8 uses (Modules 4/5/6/7). Prior
  max: 0 per recipe (kv-list wasn't used in legal/financial). Now
  the utility kv primitive is thoroughly validated.
- **3rd production consumer of pull-quote** (Phase-2 tutorial + white-
  paper Day 13 + walkthrough Day 21). 2 uses in this recipe alone.
- **5 inline density pattern groups** — SVG diagrams (3), code blocks
  (5+), palette swatches (1 group of 5), objectives-box (wait, that's
  a real component), Do/Don't block, checklists. Above NOC's 4 but
  acceptable given self-documenting nature — codified as the extreme
  density case.
- **Audit + capabilities:** recipe register entry +
  `capabilities.yaml` regenerated.

### Tests (Phase 3 Day 21)

- **`tests/test_tutorial_katib_walkthrough.py`** (new, 25 tests):
  schema-loads, en-only, page-targets [8, 16], large-section-count
  (regression: >=40), component-mix, **eighth-data-table-consumer**
  (regression: 3 cols × 10 rows domains table), third-tutorial-step-
  consumer, **heaviest-kv-list-deployment** (regression: >=8 uses),
  third-pull-quote-consumer (regression: 2 uses), cover-minimalist-
  typographic, sections-grid-dense-cheat-cards (regression: 20
  items), seven-module-headers (regression: Module 1-7 eyebrow
  pattern), uses-objectives-box, validates-clean, validates-strict-
  clean, renders-EN (7 marker classes), pdf-within-target-pages,
  renders-all-v1-content (40+ distinct phrases), has-three-inline-
  svg-diagrams (regression), has-multiple-code-blocks (regression
  >=5 <pre>), has-cheat-grid-twenty-cards (regression), has-palette-
  swatches (regression: 5 hex colors), in-capabilities, audit-
  entry-exists, **phase-3-close-marker-all-fifteen-recipes-in-
  capabilities** (gate test: all 15 Phase-3 recipes present).
- **Regression sweep:** 920/920 passing (was 895, +25). Zero
  WeasyPrint warnings across all 25 render paths.

### Phase 3 Summary

**Closed 2026-04-24 on Day 21** — matches original ~21-day estimate.

**Recipes migrated: 15/15 (100%)** via 15 ship days across 4 weeks.

Day-by-day:

| Day | Recipe | Component work | Commit |
|-----|--------|----------------|--------|
| 4 | business-proposal-letter | — | `8f4...` (first recipe) |
| 6 | personal-cover-letter | masthead-personal + callout 0.2.0 Day 5 | `1073839` |
| 8 | formal-noc | multi-party-signature-block + kv-list 0.2.0 Day 7 | `65b10a4` |
| 9 | tutorial-how-to | — | `ad26298` |
| 10 | tutorial-handoff (pivot day) | — | `23e55a7` |
| 11 | tutorial-cheatsheet | **sections-grid** (infra+recipe combo) | `6a92f8b` |
| 12 | business-proposal-one-pager | — | `e48aaba` |
| 13 | editorial-white-paper | **data-table** (infra+recipe combo) | `326c4c7` |
| 14 | business-proposal-proposal | — | `ca2baf1` |
| 15 | financial-invoice | **financial-summary** (infra+recipe combo) | `70dce46` |
| 16 | financial-quote | — | `19fdd54` |
| 17 | legal-mou | **clause-list** (infra+recipe combo) | `342acb3` |
| 18 | CV infra sprint day 1 | **cv-layout + skill-bar-list + tag-chips** (3 parallel) | `adcbe59` |
| 19 | personal-cv | — | `ccb8df1` |
| 20 | tutorial-onboarding | — | `66a1ba7` |
| 21 | tutorial-katib-walkthrough | — | (this commit) |

**Components delivered:**

Day-0 queue (original 7 slots → 8 after Day-2 queue revision):
1. ✅ `kv-list` Day 1 (now v0.2.0 after Day-7 boxed variant)
2. ✅ `letterhead` Day 2
3. ✅ `masthead-personal` Day 5 (honest-intent graduation)
4. ✅ `multi-party-signature-block` Day 7
5. ✅ `financial-summary` Day 15 (honest-intent graduation)
6. ❌ **`recitals-block` RETIRED Day 17** on v1 evidence (replaced
   by clause-list — legal domain uses numbered clauses, not WHEREAS
   preambles)
7. 🔄 **`legal-disclaimer-strip` ABSORBED Day 17** into callout
   neutral (Template Notice block)
8. ✅ `clause-list` Day 17 (replaces recitals-block)

Phase-3 post-queue additions (auto-graduated via request log):
9. ✅ `sections-grid` Day 11 (first auto-graduation — 3 deps)
10. ✅ `data-table` Day 13 (second auto-graduation — 4 deps; 7-day
    horizon prediction fulfilled Day 20)
11. ✅ `cv-layout` Day 18 (auto-graduated, 3 deps)
12. ✅ `skill-bar-list` Day 18 (auto-graduated, 3 deps)
13. ✅ `tag-chips` Day 18 (auto-graduated, 3 deps)

Phase-3 component evolutions (4):
- `signature-block` 0.1.0 → 0.2.0 (Day 3): organization + location +
  recipient variant
- `module` 0.2.0 → 0.3.0 (Day 3): title optional for continuous prose
- `callout` 0.1.0 → 0.2.0 (Day 5): neutral tone for non-status
  highlights
- `kv-list` 0.1.0 → 0.2.0 (Day 7): boxed variant for field-summary
  blocks

**Total engine state:**
- **31 components** (11 new Phase-3 + Phase-2 library; 4 at evolved
  versions)
- **22 recipes** (16 production; 6 dev showcases — unchanged from
  Phase-2 close)
- **920 tests** (+402 from Phase-2's 518 — 77% growth)
- **0 WeasyPrint warnings** across 25 render paths
- **49 commits ahead of `origin/main`** — ready to push + tag

**Phase-3 forecasts fulfilled:**

1. **Original 21-day estimate met** (Day 21 close).
2. **14-15 recipe triage list** (CHANGELOG said 14; enumerated 15).
   Actual: 15 shipped.
3. **Day-13 data-table triage prediction** (onboarding = 3-col
   text-only windows dependent) — fulfilled Day 20 at 7-day horizon.
4. **24-hour ship discipline** (infra day → recipe day +1) — 4
   consecutive applications validated the pattern as operational
   mode.
5. **Day-10 v1-read discipline** caught recitals-block plan
   mismatch on Day 17 before scaffolding. Architecture plans
   yielded to evidence.
6. **Day-15 ADR prediction** (legal-disclaimer-strip absorbed into
   callout neutral) — confirmed Day 17.
7. **Day-17 ADR prediction** (Days 20-21 zero-new-component) —
   confirmed Day 20 + Day 21.

**Phase-3 patterns codified:**

1. **Request-driven graduation** (≥3 verified dependents = auto-
   graduate; 2 = honest-intent --force + justification). 5 of 11
   Phase-3 components auto-graduated; 6 via honest-intent.
2. **24-hour ship discipline** for infra+recipe combos.
3. **v1-read before scaffolding** (Day-10 codification).
4. **Raw-HTML inputs abstraction** — scales from module's 1 density
   block (Phase 2) → legal-mou 3 (Day 17) → cv-layout hosting
   entire sidebar + main (Days 18-19).
5. **Primitive styles auto-load** (Phase-2 feature exercised for
   the first time Day 19).
6. **Section-divider via module eyebrow** (codified Day 20).
7. **Repeated-pattern density convention** — identical-pattern
   repeated blocks count as 1 semantic density block per group.
8. **Domain-completion pattern** — all recipes within a domain
   ship within 2-3 days of each other (business-proposal Day 14,
   financial Day 16, personal Day 19, tutorial Day 21).

**Phase-4 roster (deferred):**

- **`signature-field-block` primitive** — 3 verified dependents
  (proposal Day 14, quote Day 16, mou Day 17 inline signature
  grids). Meets auto-graduation threshold.
- **`code-block` primitive** — 10+ internal uses in walkthrough
  alone; tutorials will want it; deferred from Day 21.
- **`cv-layout` photo input evolution** — v0.2.0 adds `photo` input
  accepting registered brand image assets (brand_fields
  integration).
- **`inputs_by_lang` recipe schema** (Open Item #5) — first
  bilingual recipe unblocks NOC, MoU AR variants.
- **Legal domain backfill** — nda, service-agreement, engagement-
  letter (currently Deferred in v1-reference). 18 clause-list
  instances ready to graduate clause-list usage.
- **Content rewrite for katib-walkthrough** — v1 CLI references
  need v2-accurate content.
- **Phase-4 cover variants** — business-proposal, formal, editorial
  styles beyond minimalist-typographic.

### Architecture decisions (Phase 3 Day 21)

1. **Zero-new-component forecast held at Day 21** — 2nd consecutive
   zero-new-component day closes Phase 3 on original estimate.
2. **kv-list heaviest deployment ever** — 8 uses in one recipe.
   Validates kv-list as the workhorse primitive for reference-style
   documentation.
3. **pull-quote 3rd consumer after 13 days of silence** — Phase-2
   tutorial + white-paper Day 13 + walkthrough Day 21. Same pattern
   as tutorial-step's 2nd-consumer-after-11-days (Day 20) and
   letterhead commercial's 13-day-wait-before-invoice (Day 15).
   Patient primitives earn their keep.
4. **Phase-3 close gate test** — `test_phase_3_close_marker_all_
   fifteen_recipes_in_capabilities` asserts all 15 recipes present.
   Institutional memory captured in test form.
5. **Content-v1-accuracy vs structure-fidelity trade-off
   documented.** Walkthrough content references v1 CLI
   (build.py, scripts/, etc.) — placeholder-preservation
   convention applied consistently across Phase 3. Phase-4 rewrite
   to make content v2-accurate flagged.
6. **AR variant deferred fifteenth recipe in a row.** 15/15
   consistency. First bilingual pending `inputs_by_lang` schema
   (Open Item #5).



Fourteenth Phase-3 recipe migration. **Zero-new-component day** — composes the existing library into the densest tutorial recipe shipped. **The Day-13 data-table triage prediction materializes**: data-table was built Day 13 with onboarding listed as a verified dependent ("3-col text-only windows" — 30/60/90-day milestone table). 7-day build-to-consumer gap. Validates the Phase-3 "triage-driven graduation" pattern operating over week-long horizons.

- **`recipes/tutorial-onboarding.yaml`** (new) — 26-section new-hire
  onboarding handbook:
  1. `cover-page` **minimalist-typographic** — 4th production use of
     this variant (tutorial-how-to Day 9, editorial-white-paper Day
     13, inline variants, now onboarding). eyebrow "Onboarding" +
     title "Welcome to the team" + subtitle + reference_code.
  2. Inline TOC (density block #1) — 5-row custom grid layout with
     part labels + titles + dotted leaders + page numbers.
  3-7. **Part I — Welcome and company context**: section divider
     (module plain with eyebrow "Part I" + title + intro) + 3
     content modules (Who we are, How we work with 3-bullet ul, Our
     mission) + 1 `callout tip` ("Why this matters" async-first
     reinforcement — 2nd tip consumer after tutorial-how-to).
  8-13. **Part II — Your role**: section divider + Responsibilities
     ul + 30/60/90 header + **`data-table` 7TH PRODUCTION CONSUMER**
     (3-col Window/Focus/Signal text-only table) + Stakeholders
     header + `sections-grid` bordered cols=2 (4 stakeholder cards
     — 4th bordered consumer).
  14-20. **Part III — Tools and environment**: section divider +
     Accounts inline checklist (density block #2) + Software header
     + 3× `tutorial-step` (2nd production consumer — 11-day wait
     since Day 9; validates primitive's reuse value) + `callout
     warn` ("Security basics" 2FA — 2nd warn consumer).
  21-22. **Part IV — Your first week**: section divider + combined
     5-day checklists (density block #3 — single raw_body containing
     5 h3 + checklist ul combinations for Days 1-5).
  23-26. **Closing**: section divider + By topic header + `sections-
     grid` bordered cols=2 (4 who-to-ask cards — 5th bordered
     consumer) + final welcome prose.
  Content adapted from `v1-reference/domains/tutorial/templates/
  onboarding.en.html`. Placeholder prose preserved.
- **Rendered output: 5 pages, 0 WeasyPrint warnings.** `target_pages:
  [3, 6]`, `page_limit: 6`. Within target.
- **Validation clean at default + strict** — 0 content-lint warnings.
- **3 density-convention inline blocks** (TOC + accounts checklist +
  combined 5-day checklists) — under NOC's empirical ceiling of 4.
  Pattern: repeated identical-shape blocks (checklists) counted as 1
  pattern per semantic group, not N distinct density blocks.
- **3 tutorial-onboarding recipe-requests logged** (new-hire
  engineering + consultant + partner-team).
- **1 fix-pass during iteration**: dropped `meta_left` and
  `meta_right` inputs from cover-page (not in its schema; v2
  cover-page doesn't auto-render date like v1 did). Replaced with
  `reference_code` input which IS supported.
- **Audit + capabilities:** recipe register entry +
  `capabilities.yaml` regenerated.

### Tests (Phase 3 Day 20)

- **`tests/test_tutorial_onboarding.py`** (new, 23 tests): schema-
  loads, en-only, page-targets [3, 6], 26-section count,
  component-mix (17 module + 2 sections-grid + 3 tutorial-step +
  2 callout + 1 cover-page + 1 data-table), cover-uses-minimalist-
  typographic, **seventh-data-table-consumer** (regression guard:
  Day-13 triage prediction — 3 cols Window/Focus/Signal + 3 rows
  Days-1-30/31-60/61-90), uses-three-tutorial-steps (regression:
  numbers 1-2-3), uses-callout-tip (regression: "Why this matters"),
  uses-callout-warn (regression: "Security basics"), uses-two-
  sections-grid-bordered (regression: 2 instances, 4 items each,
  cols=2), section-divider-pattern (regression: 5 module plain
  dividers with eyebrows Part I/II/III/IV/Closing — validates
  module eyebrow as section-separator pattern), validates-clean,
  validates-strict-clean, renders-EN (5 marker classes), pdf-within-
  target-pages (3-6 accepted), renders-all-v1-content (30+ distinct
  phrases), regression guards for data-table (1 element), tutorial-
  step elements (3), sections-grid bordered elements (2), data-
  table 3-columns (regression), in-capabilities, audit-entry-exists.
- **Regression sweep:** 895/895 passing (was 872, +23). Zero
  WeasyPrint warnings across all 24 render paths.

### Architecture decisions (Phase 3 Day 20)

1. **Day-13 triage prediction fulfilled at 7-day horizon.** data-table
   was built Day 13 with 4 verified dependents: white-paper (Day 13),
   proposal (Day 14), invoice (Day 15), onboarding (Day 20). First
   three shipped within 3 days of build; onboarding arrives 7 days
   later. Validates the "triage-driven graduation" pattern operates
   cleanly over week-long horizons, not just same-day ships. Future
   Phase-4 components can be built against verified dependents
   without requiring immediate same-day consumption.
2. **tutorial-step's second consumer after 11 days.** Built Phase-2;
   first production use Day 9 (tutorial-how-to); second use Day 20
   (onboarding). 11-day gap. Proves Phase-2 primitives earn their
   keep over weeks, not just days. Same pattern as pull-quote
   (Phase-2 build → Day-13 white-paper consumer, 13-day gap).
3. **Zero-new-component forecast held.** Day-17 ADR predicted this;
   Day 20 delivers. Tutorial domain now at 80% complete (4 of 5:
   how-to + handoff + cheatsheet + onboarding; katib-walkthrough
   remaining for Day 21).
4. **Section-divider pattern via module plain eyebrow** — codified.
   5 Part dividers (Part I-IV + Closing) use `module plain` with
   `eyebrow + title + intro`. No new component; validates module's
   eyebrow input as a sub-document separator primitive. This
   pattern is reusable for any multi-part long-form document
   (white-paper already used 6 numbered modules; onboarding uses 5
   plain modules with eyebrows — same component serves both
   numbered and eyebrow-based section-separator shapes).
5. **sections-grid bordered cements as THE contact-card pattern.**
   Now at 5 production instances across 3 recipes (invoice 2 +
   quote 1 + onboarding 2). Every instance is 2x2 (cols=2, 4 items).
   The "bordered-grid for contact/stakeholder cards" pattern is
   stable — future portfolio/directory recipes can assume this.
6. **Repeated-shape density convention refined.** 6 checklist ul
   instances in onboarding (1 accounts + 5 days). Combined 5 daily
   checklists into 1 raw_body block + 1 accounts block = 2 density
   blocks total (plus TOC = 3). Under NOC's ceiling of 4. The
   refinement: identical-pattern repeated blocks count as 1
   semantic density block per group, not N distinct density
   decisions.
7. **WeasyPrint CSS strict-parsing continues to serve as lint-pass.**
   Day 19 caught `word-break: break-word`. Day 20 had no CSS issues
   — clean renders across all 7 primitive CSS files + 3 section CSS
   files + 26 recipe sections.
8. **14 of 15 Phase-3 recipes shipped (93%).** Original triage
   enumerated 15 (tutorial × 5 + business-proposal × 3 + formal/noc
   + personal × 2 + financial × 2 + editorial/white-paper +
   legal/mou = 15; CHANGELOG said "14" — arithmetic error).
   Day 21 ships `tutorial-katib-walkthrough` to close at 15/15.
9. **AR variant deferred (fourteenth recipe in a row).** Same
   discipline. First bilingual pending `inputs_by_lang` schema.



Thirteenth Phase-3 recipe migration. **CV 2-day sprint completes** —
Day 18 built cv-layout + skill-bar-list + tag-chips infrastructure;
Day 19 ships the recipe. **24-hour ship discipline: 4th consecutive
application** (sections-grid Day 11→12, data-table Day 13→14,
financial-summary Day 15→16, CV-infra Day 18→Day 19). The pattern is
operationally stable.

- **`recipes/personal-cv.yaml`** (new) — SINGLE-SECTION recipe; all
  content lives inside cv-layout's `sidebar_html` + `main_html` raw
  inputs. Fewest sections ever in Phase-3 (1 vs. mou's 25).
  - **Sidebar (7 content blocks)**: photo slot (styled circular
    placeholder) + name+headline block (centered) + Contact section
    (5 labeled fields: Email/Phone/Location/Portfolio/LinkedIn) +
    Personal section (3 labeled fields: Nationality/Visa/DOB) +
    Languages section with inline `<ul class="katib-skill-bar-list">`
    (2 items at level 5) + Core Skills section with same class (4
    items at levels 5/4/4/3) + Tools section with inline `<ul
    class="katib-tag-chips">` (4 chips).
  - **Main column (4 sections)**: Summary (prose) + Experience (3
    entries with role + dates + employer + location + ul achievements)
    + Education (2 entries with degree + institution + meta) +
    Selected Projects (1 entry).
- **FIRST production consumer of 3 Day-18 components** simultaneously:
  - `cv-layout` — 24-hour ship from infra day (4th consecutive
    application of the discipline).
  - `skill-bar-list` — 2 uses in one recipe (Languages + Core Skills).
  - `tag-chips` — 1 use (Tools).
- **Architecture discovery exercised: primitive styles auto-load.**
  `core/compose.py:_load_primitive_styles()` loads ALL primitive CSS
  globally into every rendered recipe. This enables writing inline
  `katib-skill-bar-list` + `katib-tag-chips` class usage in
  cv-layout's raw HTML — the primitive CSS applies without requiring
  the primitives to be referenced as separate sections. The
  abstraction is: primitives are library-level styles (available
  everywhere); sections are recipe-scoped styles (loaded on
  reference). Mirrors the tier semantics.
- **Sidebar-scoped CSS overrides pay off.** cv-layout's styles.css
  has `.katib-cv-layout__sidebar .katib-skill-bar-list__*` rules that
  invert primitive colors against the dark accent sidebar bg.
  Inline primitive usage in sidebar_html renders correctly without
  per-recipe color overrides.
- **Rendered output: 2 pages, 0 WeasyPrint warnings.** `target_pages:
  [1, 2]`, `page_limit: 2`. Within target.
- **1 fix pass: `word-break: break-word` → `overflow-wrap: break-word`**
  (invalid CSS property fixed; property is `word-break: break-all` or
  `overflow-wrap: break-word` in standard CSS).
- **Validation clean at default + strict** — 0 content-lint warnings.
- **3 personal-cv recipe-requests logged** (Senior AI Engineer CV +
  Consulting partnership pitch CV + Academic/research CV) —
  validates the recipe's reach across 3 CV types.
- **Audit + capabilities:** recipe register entry +
  `capabilities.yaml` regenerated.

### Tests (Phase 3 Day 19)

- **`tests/test_personal_cv.py`** (new, 24 tests): schema-loads,
  en-only, page-targets [1, 2], single-section (regression guard:
  1 cv-layout section — fewest ever), first-cv-layout-consumer,
  sidebar-has-skill-bar-list-inline (regression guard: 2 uls + 6
  items + level modifier classes l3/l4/l5), sidebar-has-tag-chips-
  inline (regression guard: 1 ul + 4 chips), sidebar-has-all-identity-
  sections (Contact + Personal + Languages + Core Skills + Tools),
  main-has-four-main-sections (Summary + Experience + Education +
  Selected Projects), main-has-three-experience-entries (regression
  guard: 4 cv-entry divs = 3 experience + 1 project),
  main-has-two-education-entries, validates-clean, validates-strict-
  clean, renders-EN (4 marker classes), pdf-within-target-pages (1-2
  accepted), renders-all-v1-content (25+ distinct phrases), regression
  guards for skill-bar-list uls (2), tag-chips uls (1), skill items
  (6), tag chips (4), grid-layout-in-html (regression guard:
  `grid-template-columns: 70mm 1fr`), sidebar-has-photo-slot
  (regression guard: circular photo placeholder), in-capabilities,
  audit-entry-exists.
- **Regression sweep:** 872/872 passing (was 848, +24). Zero
  WeasyPrint warnings across all 23 render paths.

### Architecture decisions (Phase 3 Day 19)

1. **Primitive styles auto-load — architectural discovery exercised
   for the first time.** `core/compose.py:_load_primitive_styles()`
   loads all primitive CSS globally into every recipe. This enables
   writing primitive-class inline HTML in raw_body inputs without
   referencing the primitives as sections. The design is:
   *primitives are library-level styles (available everywhere);
   sections are recipe-scoped styles (loaded per-reference)*. Mirrors
   the tier semantics. This was a Phase-2 feature newly exercised
   on Day 19 — cv-layout's raw-HTML approach relies on it.
2. **Single-section recipe pattern.** CV is the first single-section
   recipe in Phase-3 (1 section vs. mou's 25). All content lives
   inside cv-layout's sidebar_html + main_html raw inputs. This is
   the terminal case of the "raw-HTML inputs" abstraction that scaled
   from module (1 density block) → legal-mou (3 density blocks) →
   cv-layout (hosts ENTIRE recipe content).
3. **24-hour ship discipline: 4th consecutive application.** Prior
   applications: sections-grid Day 11→12, data-table Day 13→14,
   financial-summary Day 15→16. Now CV-infra Day 18→Day 19. The
   pattern is no longer a discipline to maintain — it's the operating
   mode for infra+recipe combo planning.
4. **Personal domain complete.** cover-letter (Day 6) + cv (Day 19).
   3rd complete Phase-3 domain after business-proposal (Day 14) and
   financial (Day 16). Legal remains 25% complete (mou only; other
   3 stay in v1-reference per Phase-3 triage).
5. **Photo slot as inline placeholder.** cv-layout has no `photo`
   input in v0.1.0 — the photo renders as a styled circular `<div>`.
   Future Phase-4 evolution: add a `photo` input accepting a
   registered brand image asset (brand_fields integration). For now,
   users add their photo via manual HTML edit post-generation.
6. **Invalid CSS property caught by WeasyPrint.** `word-break: break-word`
   is not a valid CSS value (standard is `word-break: break-all` OR
   `overflow-wrap: break-word`). WeasyPrint's warning caught it
   pre-commit. Fixed to `overflow-wrap: break-word`. Documents the
   value of WeasyPrint's strict CSS parsing as a lint-pass for
   recipe authors.
7. **13 of 14 recipes shipped (93%).** On pace for Day-21 Phase-3
   close. 1 recipe remaining technically (Day 20 OR 21 — the
   tutorial-onboarding + tutorial-katib-walkthrough pair). Both
   zero-new-component per Day-17 ADR prediction.
8. **AR variant deferred (thirteenth recipe in a row).** Same
   discipline. First bilingual pending `inputs_by_lang` schema.



Day 1 of the 2-day personal/cv infra+recipe sprint. **3 new components
built in parallel** — all three auto-graduated through the request log
(3 verified dependents each: personal-cv primary + 2 Deferred
recipes per component). First Phase-3 day to build 3 components
simultaneously.

**Key architectural novelty:** cv-layout introduces the first 2-column
page layout in v2. Every other recipe uses single-column linear flow
top-to-bottom; CV needs a full-page grid with 70mm dark-accent
sidebar + 1fr main column. Implementation keeps the single-section
composition model (the recipe still looks like a flat section list);
cv-layout just accepts `sidebar_html` + `main_html` raw inputs and
emits the grid wrapper.

- **`components/primitives/skill-bar-list/`** (new) — primitive-tier
  proficiency list. `items: [{name, level (1-5)}]` → `<ul>` with name
  + level-bar span. Level drives CSS modifier class
  (`--l1` through `--l5`) controlling fill width (20%→100% in 20%
  increments). RTL: bar fills from trailing edge via lang-scoped
  `::after` positioning (same pattern as clause-list Day 17).
  Token contract: `text, accent, border` (accent for bar fill; border
  for unfilled track). No variants.
- **`components/primitives/tag-chips/`** (new) — primitive-tier inline
  tag-pill list. `items: [string|{text}]` → `<ul>` with `font-size: 0`
  trick to eliminate inline-block whitespace gaps; each `<li>` is a
  rounded-corner pill with tag-bg background. RTL: chip trailing-margin
  flips so gaps appear on the correct side. Items accept strings or
  `{text}` mappings for primitive consistency with clause-list +
  data-table. Token contract: `text, tag_bg`. No variants.
- **`components/sections/cv-layout/`** (new) — section-tier 2-column
  page layout. `sidebar_html` + `main_html` raw-string inputs (trusted
  HTML via Jinja2 `| safe` filter — same pattern as module raw_body).
  CSS grid `70mm 1fr` with `min-height: 257mm` (A4 height minus
  default page margins) + `margin: -20mm` (pulls the layout to page
  edges under default @page margins — no recipe-level @page override
  needed). Sidebar uses accent bg + accent-on fg (inverts against
  dark accent); main uses transparent bg + text fg. Sidebar-scoped
  overrides for nested `skill-bar-list` + `tag-chips` primitives so
  their colors invert correctly against the dark sidebar background.
  Token contract: `text, accent, accent_on` (tight — no border or
  secondary text needed since content is raw-HTML callee-supplied).
- **9 component-requests logged** (3 per component) — all three
  components auto-graduated cleanly (threshold: 3 verified
  dependents). No `--force` needed; this is the second consecutive
  multi-request auto-graduation (data-table Day 13 had 4, now these
  three with 3 each). Request-driven graduation is operating as
  designed.
- **Validation: token contracts tightened pre-register.** Initial
  declarations included tokens that weren't referenced in the HTML
  or styles.css. Validator caught each, tightened to actual usage.
  Clean patterns reinforced.
- **Isolated-render harness: 6 PDFs clean.** Each component rendered
  EN + AR through `katib component test` with 0 WeasyPrint warnings.
- **Audit + capabilities:** 3 component register entries +
  `capabilities.yaml` regenerated (now 31 components).

### Tests (Phase 3 Day 18)

- **`tests/test_skill_bar_list.py`** (new, 10 tests): schema-loads,
  items-required, token-contract, no-variants, renders-EN (4 items),
  renders-AR (dir=rtl), renders-to-pdf, level-modifier-classes-
  emitted (regression guard for l1-l5 class-name contract), name-
  and-level-spans-present, wrap-section-has-lang-attr.
- **`tests/test_tag_chips.py`** (new, 10 tests): schema-loads,
  items-required, token-contract, no-variants, renders-EN (3 chips),
  renders-AR (dir=rtl), renders-to-pdf, accepts-mapping-form
  (regression guard for string OR {text} item support), wrap-section-
  has-lang-attr, ul-has-lang-attr (regression guard — inner `<ul>`
  also carries lang= so RTL CSS scoping applies).
- **`tests/test_cv_layout.py`** (new, 10 tests): schema-loads,
  inputs-required (sidebar_html + main_html), token-contract,
  no-variants, renders-EN (semantic aside + main tags), renders-AR
  (dir=rtl), renders-to-pdf, grid-in-styles (regression guard for
  `grid-template-columns: 70mm 1fr` + `min-height: 257mm` declarations
  surviving to rendered HTML), sidebar-styling-present (regression
  guard for `background: var(--accent)` + `color: var(--accent-on)`
  rules), html-passthrough-preserves-structure (regression guard:
  raw HTML flows through `{{ input.sidebar_html | safe }}` unchanged).
- **Regression sweep:** 848/848 passing (was 818, +30 from 3×10
  component tests). Zero WeasyPrint warnings across all 24 render
  paths (21 from prior recipes + 6 from Day-18 isolated component
  harnesses — actually 24 total after including Day-18 internal
  compose renders).

### Architecture decisions (Phase 3 Day 18)

1. **2-column layout kept as a single component, not a schema
   extension.** Alternative considered: add `layout: two-column-sidebar`
   field to recipe schema and have the compose engine wrap section
   subsets. Rejected — the engine extension would only benefit one
   recipe (CV); the single-component approach (cv-layout section with
   sidebar_html + main_html raw inputs) keeps the recipe schema
   stable and contains the novelty to one component. Phase-4 can
   promote layout to schema if demand emerges.
2. **Raw-HTML inputs over nested-component composition.** cv-layout's
   sidebar/main inputs accept raw HTML rather than nested component
   references. This matches module's `raw_body` precedent (Phase 2)
   and avoids the complexity of recursive component resolution that
   v2 compose doesn't currently support. Trade-off: sub-shape
   validation lost, but recipe authors can still use skill-bar-list
   and tag-chips primitives by rendering them inline via Jinja2
   templating at recipe level — Day 19 will show this pattern.
3. **Reuse accent + accent-on for sidebar colors, not new tokens.**
   v1 CV used dedicated `--sidebar-bg`, `--sidebar-fg`, `--sidebar-muted`
   tokens. v2 reuses `accent` (dark sidebar bg) + `accent-on` (light
   text on dark bg). Trade-off: brand palettes now drive both the
   accent color AND the sidebar color; if future CV-like recipes
   need a neutral-dark sidebar rather than brand-accent, revisit
   with dedicated tokens. For now, accent-driven sidebar is visually
   correct for personal-brand CVs.
4. **Negative-margin grid to handle page margins.** cv-layout emits
   `margin: -20mm` on the grid to pull content to page edges under
   default @page 20mm margins. Alternative was recipe-level
   `@page { margin: 0 }` override — would require extending recipe
   schema. Negative-margin approach keeps the schema stable and
   works across all brand templates.
5. **Request-driven auto-graduation holding at Day 18.** Third
   multi-request auto-graduation cluster (sections-grid Day 11 with
   3 deps, data-table Day 13 with 4 deps, Day 18 with 3×3=9 total
   requests across 3 components). 5 of 11 Phase-3 components have
   now auto-graduated via the request log (sections-grid, data-table,
   cv-layout, skill-bar-list, tag-chips). The 6 others used honest-
   intent `--force` with justification (kv-list, letterhead,
   masthead-personal, multi-party-signature-block, financial-summary,
   clause-list).
6. **Infra day #6 in Phase 3.** Prior infra days: Day 1 (kv-list),
   Day 2 (letterhead), Day 5 (masthead-personal), Day 7
   (multi-party-signature-block + kv-list 0.2.0), Day 11
   (sections-grid + infra+recipe combo), Day 13 (data-table +
   infra+recipe combo), Day 15 (financial-summary + infra+recipe
   combo), Day 17 (clause-list + infra+recipe combo). Day 18 is
   pure-infra (no recipe ship) — first since Day 7. The 2-day
   sprint pattern was validated on Day 7 (NOC infra Day 7 → NOC
   recipe Day 8).
7. **Phase-3 progress: 12/14 recipes shipped (86%), 11 of 11 Phase-3
   components built.** Day 19 forecast: ship personal-cv recipe
   (13/14, 93%). Day 20-21 forecast: tutorial-onboarding + tutorial-
   katib-walkthrough (both zero-new-component). Phase-3 close
   achievable by Day 20-21. On pace for the original 21-day estimate.
8. **AR variant deferred (thirteenth recipe coming up).** Same
   discipline — first bilingual still pending `inputs_by_lang`
   schema.



Twelfth Phase-3 recipe migration + 8th new Phase-3 component. **Closes
the original Day-0 component queue** with a v1-evidence-driven revision:
the planned `recitals-block` is retired (v1 legal domain uses numbered
clauses, not WHEREAS preambles); `clause-list` takes its place. The
planned `legal-disclaimer-strip` is formally absorbed into `callout
neutral` (Template Notice block).

- **`components/primitives/clause-list/`** (new) — primitive-tier
  ordered-list with counter-based decimal numbering in accent color.
  Inputs: `items: [string]` (array of clause strings; also accepts
  `{text}` mappings for primitive consistency with data-table) +
  optional `start` (counter continuation). No variants — shape is
  stable across all 4 legal-domain v1 templates. Token contract:
  `text, accent`. RTL handling: lang-scoped physical properties flip
  the `::before` number from left to right (no `padding-inline-start`
  reliance — WeasyPrint has gaps in logical-property support within
  `::before` pseudo-element contexts). Validator wrap pattern
  (`<section class="katib-clause-list-wrap" lang=...>`) reuses the
  data-table Day-13 precedent for primitives whose natural root
  element isn't accepted by the `_ROOT_LANG_RE` regex.
- **`recipes/legal-mou.yaml`** (new) — 25-section bilateral MoU:
  1. `module` raw_body — centered masthead (density block #1:
     kicker + title + subtitle + reference line).
  2. `callout` **neutral** — Template Notice (5th neutral consumer;
     **absorbs legal-disclaimer-strip** per Day-15 ADR prediction).
  3. `module` numbered (§1) — "The Parties" heading + intro.
  4. `callout` **info** — Party A (3rd info consumer).
  5. `callout` **info** — Party B (4th info consumer).
  6-23. Alternating `module numbered` + `clause-list` pairs for
     §2 Background (prose only), §3 Purpose, §4 Scope, §5
     Responsibilities (Party A then Party B — Party B continues §5
     via `module plain` without re-incrementing), §6 Non-Binding
     (with `callout neutral` emphasis block — 6th neutral consumer),
     §7 Confidentiality, §8 Term, §9 Governing Law, §10 Costs
     (prose only).
  24. `module` raw_body — Execution section header (density block #2).
  25. `module` raw_body — inline 2-col signatory grid with 4 blank
     fields per party (density block #3; 3rd consumer of the inline
     signature-field pattern after proposal Day 14 + quote Day 16
     — ripe for Phase-4 graduation to `signature-field-block`
     primitive, 3 dependents meets auto-threshold).
  Content adapted from `v1-reference/domains/legal/templates/
  mou.en.html`. Placeholder prose preserved.
- **HEAVIEST `module numbered` deployment ever** — 10 uses in one
  recipe (§1-§10). Prior records: white-paper Day 13 (6 consecutive
  chapters), proposal Day 14 (5 sections). Zero component revisions
  needed — the variant scales from 5-chapter to 10-section shapes.
- **clause-list: 7 uses, 20 total items** — `{3, 3, 3, 3, 3, 3, 2}`
  pattern across §3, §4, §5-A, §5-B, §7, §8, §9.
- **Rendered output: 4 pages, 0 WeasyPrint warnings.** `target_pages:
  [2, 4]`, `page_limit: 4`. Within target.
- **Validation clean at default + strict** — 0 content-lint warnings.
- **3 density-convention inline blocks** (masthead + Execution header +
  signature grid) — under NOC's ceiling of 4.
- **3 clause-list component-requests logged** (mou, nda,
  service-agreement — the 2 Deferred legal recipes provide
  future-graduation pressure). **3 legal-mou recipe-requests logged.**
- **Audit + capabilities:** component + recipe register entries +
  `capabilities.yaml` regenerated.

### Tests (Phase 3 Day 17)

- **`tests/test_clause_list.py`** (new, 13 tests): schema-loads,
  items-required, token-contract, no-variants, renders-EN (3 items),
  renders-AR (dir=rtl), renders-to-pdf-EN, renders-to-pdf-AR,
  start-attribute-when-set (regression guard for counter
  continuation), no-start-when-unset (regression guard — only the
  inline override style should be absent; the base CSS rule always
  applies), items-render-as-li-elements, wrap-section-has-lang-attr
  (data-table precedent), items-accept-mapping-form (primitive
  consistency with data-table).
- **`tests/test_legal_mou.py`** (new, 24 tests): schema-loads,
  en-only, page-targets [2, 4], 25-section count, component-mix
  (14 module + 7 clause-list + 4 callout), first-clause-list-
  consumer (regression guard for 7 uses + 20 total items),
  heaviest-module-numbered-deployment (regression guard for 10
  consecutive §-numbers 1-10), uses-two-callout-info-blocks
  (regression guard for Party A/B), uses-two-callout-neutral-blocks
  (regression guard for Template Notice + Non-Binding emphasis),
  costs-section-has-no-clause-list (§10 is prose-only per v1 —
  validates evidence-driven clause-list usage, not mechanical),
  validates-clean, validates-strict-clean, renders-EN (4 marker
  classes), pdf-within-target-pages (2-4 accepted), renders-all-v1-
  content (40+ distinct phrases), seven-clause-list-elements-in-html
  (regression), twenty-clause-list-items-in-html (regression),
  ten-numbered-modules-in-html (regression), two-info-callouts-in-html,
  two-neutral-callouts-in-html, in-capabilities, audit-entry-exists,
  clause-list-in-capabilities, clause-list-audit-entry-exists.
- **Regression sweep:** 818/818 passing (was 781, +37: 13 clause-list
  + 24 mou). Zero WeasyPrint warnings across all 22 render paths.

### Architecture decisions (Phase 3 Day 17)

1. **Day-0 component queue formally closed.** 8 components originally
   planned (kv-list, letterhead, masthead-personal,
   multi-party-signature-block, financial-summary, recitals-block,
   legal-disclaimer-strip, and later-added sections-grid + data-table).
   Final state: 7 built (kv-list, letterhead, masthead-personal,
   multi-party-signature-block, sections-grid, data-table,
   financial-summary, clause-list = 8 counting clause-list) + 1
   absorbed (legal-disclaimer-strip → callout neutral). recitals-block
   retired on v1 evidence. Plus 2 auto-graduated Phase-3 bonus
   components.
2. **recitals-block retired on v1 evidence.** v1 mou.en.html does NOT
   use WHEREAS preambles. It uses `<ol class="clauses">` numbered
   legal-clause lists — 7 instances in MoU alone. The Day-0 plan
   assumed a shape that wasn't actually in v1. v1-read discipline
   (codified Day 10) caught this before scaffolding the wrong
   component. Architecture plans must yield to evidence.
3. **legal-disclaimer-strip absorbed into callout neutral.**
   Day-15 ADR predicted this; Day 17 confirms. The Template Notice
   block uses `callout neutral` with `title: "Template Notice"` —
   no new component needed. Evolving callout 0.2.0 (neutral addition)
   proved to be the correct abstraction.
4. **clause-list chosen as primitive, not section.** Numbered-clause
   lists are atomic content primitives (like data-table), not
   page-level structural elements (like module or financial-summary).
   Tier matches the semantics.
5. **module numbered scales to 10-section deployment.** Prior records:
   white-paper Day 13 (6 consecutive chapters), proposal Day 14 (5).
   MoU Day 17 (10 sections — §1 through §10). The variant's design
   holds from chapter-prose to heading-only shapes without revision.
   This is the Phase-2 design investment paying off at scale.
6. **Signature-field pattern ripe for Phase-4 graduation.** 3 recipes
   now use the inline blank-field signature grid (proposal Day 14,
   quote Day 16, mou Day 17). 3 dependents meets the auto-graduation
   threshold. Semantically distinct from multi-party-signature-block
   v0.1.0 (which accepts pre-filled `{name, title, email}` data —
   the "these are the signatories" shape vs. the "fill these in when
   signing" shape). Phase-4 candidate: `signature-field-block`.
7. **First legal-domain recipe shipped.** 1 of 4 legal v1 templates
   migrated (mou). The other 3 (nda, service-agreement,
   engagement-letter) stay in v1-reference per Phase-3 triage —
   but clause-list is now ready to serve them when pulled into
   Phase 4+. 25 internal clause-list instances across the 4 legal
   templates = strong future graduation pressure.
8. **7th zero-new-variant day for existing components** — no callout
   tones, module variants, or sections-grid column counts added.
   The library is shape-stable at Day 17.
9. **Pace tracking.** 12 recipes / 17 days = 0.71/day. Holding.
   2 recipes remaining (CV 2-day sprint + 2 tutorial recipes = 4
   work-days). Tracking to Day 20-21 close with buffer.
10. **AR variant deferred (twelfth recipe in a row).** First
    bilingual remains deferred pending `inputs_by_lang` schema
    (Open Item #5). Not a discipline break — NOC was designated
    first bilingual, MoU could follow in Phase 4.



**Phase 3 kicked off.** Open Item #4 (migration triage) resolved
2026-04-23 — 14 recipes on the migrate list. Component queue revised
three times during Phase 3: 5 (Day 0) → 6 (Day 2, discovered
`letterhead`) → 7 (Day 5, discovered `masthead-personal` — personal
identity is semantically distinct from organizational identity).
Day 4 shipped the first Phase-3 recipe (`business-proposal/letter`),
proving the recipe-migration flow end-to-end. Bilingual NOC proven
to need no new component (CSS direction-flip only). See
`~/vault/projects/katib/project.md` and ADR §Phase 3 for the locked
plan.

**Phase 2 milestone complete.** All 14 days delivered, all 8 ADR exit
criteria green with automated proofs, 518 tests passing, zero
WeasyPrint warnings, grep-clean outside `v1-reference/`. Phase-2 gate
review lives in the vault at `projects/katib/phase-2-gate-review.md`.

**Post-close-out:** Open Item #2 (content-lint wiring) resolved;
Open Item #4 (Phase 3 triage) resolved 2026-04-23. Items #1 (push + tag —
HELD until Phase 3 close) and #3 (PNG goldens — pushed to Phase 4)
parked by decision.

Engine state: **31 components** (cv-layout + skill-bar-list + tag-chips
Day 18; clause-list Day 17; financial-summary Day 15, data-table
Day 13, sections-grid Day 11, multi-party-signature-block Day 7,
kv-list at 0.2.0, signature-block at 0.2.0, module at 0.3.0, callout
at 0.2.0). **22 recipes** (+1 tutorial-katib-walkthrough Day 21; 16 production:
tutorial + business-proposal-letter + personal-cover-letter +
formal-noc + tutorial-how-to + tutorial-handoff + tutorial-cheatsheet +
business-proposal-one-pager + editorial-white-paper +
business-proposal-proposal + financial-invoice + financial-quote +
legal-mou + personal-cv + tutorial-onboarding +
**tutorial-katib-walkthrough**; 6 dev showcases). 6 core library
modules, 5 CLIs, 4 memory streams, 4 image providers, 0 external
skill dependencies.

**Business-proposal domain complete** (Day 14) — all 3 recipes
shipped: letter (Day 4), one-pager (Day 12), proposal (Day 14).
**Financial domain complete** (Day 16) — both recipes shipped:
invoice (Day 15), quote (Day 16). **Legal domain 25% complete**
(Day 17) — mou shipped; nda, service-agreement, engagement-letter
stay in v1-reference per Phase-3 triage. **Personal domain complete**
(Day 19) — cover-letter (Day 6) + cv (Day 19).

**Day-0 component queue closed (Day 17)** — 8 originally-planned
components accounted for: 7 built (kv-list, letterhead,
masthead-personal, multi-party-signature-block, sections-grid,
data-table, financial-summary, clause-list) + 1 absorbed
(legal-disclaimer-strip → callout neutral). recitals-block retired
on v1 evidence (legal domain uses numbered clauses, not WHEREAS
preambles).

**Not shippable as a v1 replacement yet** — v2 has 13 production
recipes; Phase 3 ports 2 more over the next ~4 days. Keep v1
installed as the daily global skill until the cutover.

### Added (Phase 3 Day 16 — `financial/quote` recipe ship; financial domain complete)

Eleventh Phase-3 recipe migration. **Zero-new-component day** — pure
composition of the Day-15 financial stack. **24-hour ship discipline
validated**: `financial-summary` default variant shipped Day 15,
compact variant gets its first production consumer Day 16.

- **`recipes/financial-quote.yaml`** (new) — 9-section UAE commercial
  quotation:
  1. `letterhead` **commercial variant** — **second production use**
     (validates Day-2 variant beyond the invoice 1-off). Quotation
     eyebrow + ref code `QTE-2026-0042` + issue date.
  2. `kv-list` boxed — **fourth production consumer** (NOC +
     handoff + invoice + quote). 4 fields: Issued / Valid Until /
     Currency / Prepared By.
  3. `callout` **info tone** — **second production consumer** (after
     handoff Day-10). "Prepared For" client block — v1 quote used
     `--callout-border` color here; info tone is the right semantic.
  4. `module` **numbered** (§1 Scope) — intro prose + inline
     Inclusions ul + Exclusions ul (raw_body — content-specific
     sublists don't warrant a list component).
  5. `module` **numbered** (§2 Pricing) — section header only;
     data-table follows.
  6. `data-table` dense — **sixth production consumer + second
     production use of `{text, sub}` cell mapping**. 5 columns (# /
     Description / Qty / Unit Price / Total), 3 line items, each
     with title + timing sub-line in the description cell.
  7. `financial-summary` **compact variant** — **FIRST PRODUCTION
     CONSUMER** (Day-15 built → Day-16 shipped = 24-hour ship
     discipline). 3 rows (Subtotal / VAT / Total) fit the 60mm box
     well; currency "AED" appended to Total row label.
  8. `sections-grid` bordered — **third bordered consumer** (invoice
     had 2 instances; quote adds 1). 2x2 Terms grid: Payment
     Schedule / Timeline / Validity / T&C.
  9. `module` **numbered** (§3 Acceptance) — intro prose + inline
     2-col signature grid (raw_body — honest-intent inline pattern
     matching Day-14 proposal sign-row; 2 dependents below
     graduation threshold).
  Content adapted from `v1-reference/domains/financial/templates/
  quote.en.html`. Placeholder prose preserved.
- **Rendered output: 2 pages, 0 WeasyPrint warnings.** `target_pages:
  [1, 2]`, `page_limit: 2`. Within target.
- **Validation clean at default + strict** — 0 content-lint warnings.
- **1 density-convention inline block** (acceptance signature grid)
  — well below NOC's ceiling of 4.
- **Heaviest single-recipe deployment of `module numbered`** (3
  uses in one recipe — Scope/Pricing/Acceptance). Prior max was
  6 consecutive in white-paper Day 13 (different recipe).
- **3 quote recipe-requests logged** (Triden training / consulting
  engagement / workshop facilitation).
- **Audit + capabilities:** recipe register entry +
  `capabilities.yaml` regenerated.

### Tests (Phase 3 Day 16)

- **`tests/test_financial_quote.py`** (new, 22 tests): schema-
  loads, en-only, page-targets [1, 2], nine-section-ordering,
  uses-letterhead-commercial (regression guard for the Day-2
  variant's second production use), first-financial-summary-
  compact-consumer (regression guard for 3 rows + variant: total
  on last + "50,400.00" value + "AED" currency), data-table-uses-
  text-sub-cells (regression guard for 5-col + 3-row shape with
  all 3 descriptions using {text, sub} mapping), uses-callout-info
  (regression guard for info tone + "Prepared For" title),
  uses-kv-list-boxed (regression guard for 4 meta terms),
  sections-grid-bordered-third-consumer (regression guard for
  single 2x2 instance), uses-three-numbered-modules (regression
  guard for Scope/Pricing/Acceptance numbers 1-2-3), validates-
  clean, validates-strict-clean, renders-EN (6 marker classes),
  pdf-within-target-pages (1-2 accepted), renders-all-v1-content
  (30+ distinct phrases including all totals 48,000/2,400/50,400),
  line-items-three-rows-with-sub-cells (regression guard: 3
  cell-sub spans), totals-has-accent-total-row, compact-variant-
  class-emitted, three-numbered-modules-in-html (regression guard
  at element level), in-capabilities, audit-entry-exists.
- **Regression sweep:** 781/781 passing (was 759, +22 quote tests).
  Zero WeasyPrint warnings across all 21 render paths.

### Architecture decisions (Phase 3 Day 16)

1. **24-hour ship discipline validated for financial-summary compact.**
   Built Day 15 with two variants (default 70mm, compact 60mm). Default
   shipped Day 15 (invoice — 4 rows). Compact shipped Day 16 (quote —
   3 rows). Both variants have production consumers within 24 hours
   of each other. Same pattern as sections-grid Day 11→12 (dense then
   default) and data-table Day 13→14 (white-paper then proposal). The
   discipline holds: build with dependents already confirmed, ship
   the second dependent the next day.
2. **Financial domain complete in 2 days.** Invoice Day 15 + quote
   Day 16. Both rely on letterhead commercial + kv-list boxed +
   data-table dense with {text, sub} + financial-summary (both
   variants) + sections-grid bordered + callout. Common-denominator
   infra — both recipes compose from the same 6 components with
   different section orderings and variant choices.
3. **letterhead commercial variant is now a validated production
   variant.** Day-2 build spent 13 days with zero consumers, then
   got 2 consumers in 2 days. The Phase-2 "build variants
   speculatively IF v1 triage locked them in" pattern is validated
   retroactively — the ~13-day wait was just reaching the recipes,
   not a signal of overbuilding.
4. **callout info tone graduates.** Built during callout 0.2.0
   (neutral addition). Handoff Day-10 was the 1st info consumer.
   Quote Day-16 is the 2nd. Below the 3-consumer auto-graduation
   threshold but demonstrates the tone's semantic fit across
   working-doc (handoff status block) and commercial-doc (quote
   client block) shapes.
5. **module numbered scales to 3-use single-recipe deployment.**
   Quote uses numbered module 3 times (Scope/Pricing/Acceptance).
   Prior records: white-paper Day 13 used 6 consecutive, proposal
   Day 14 used 5. The 3-use pattern here is a section-header shape
   (numbered heading + optional raw_body) rather than the chapter-
   like shape of white-paper/proposal. Same component serves both
   shapes cleanly.
6. **Zero-new-component forecast held for the 3rd time in Phase 3.**
   Day 4 (letter), Day 8 (NOC AR), Day 9 (how-to), Day 10 (handoff),
   Day 12 (one-pager), Day 14 (proposal), Day 16 (quote) — 7
   zero-new-component days on a 14-recipe migrate list. The queue
   is composing well.
7. **Phase-3 progress: 11/14 recipes (79%) in 16 days.** On pace.
   Remaining: CV (2-day sprint), MoU (Day 17+ w/ recitals-block —
   last Day-0 queue item), plus 2 tutorial recipes (onboarding,
   katib-walkthrough). Reachable by Day 20 with buffer.
8. **AR variant deferred (eleventh recipe in a row).** Consistent
   since Day 4. MoU may break the streak depending on recitals-
   block bilingual support; NOC remains the designated first
   bilingual recipe.

### Added (Phase 3 Day 15 — `financial-summary` component + `financial/invoice` recipe ship)

Tenth Phase-3 recipe migration. **Seventh new Phase-3 component built** —
`financial-summary` closes the Day-0 queue's totals-box requirement.
Infra+recipe combo day. Honest-intent graduation (2 verified dependents,
below auto-threshold of 3 — --force with justification, matching Day-5
masthead-personal pattern).

- **`components/sections/financial-summary/`** (new) — section-tier
  totals box for invoices and quotes. Right-aligned numeric rows with
  labels on the leading side; one emphasized Total row with accent
  background. Container is `flex-end` positioned (70mm wide) so it
  naturally aligns to the trailing edge of the page. Optional
  `currency` input appends currency code to the Total row label
  ("TOTAL AED"). Variants: `default` (70mm), `compact` (60mm, slimmer
  for quotes). Row data is simple: `{label, value, variant?}` where
  `variant: "total"` triggers the accent-bg emphasis. Token contract:
  `text, text_secondary, accent, accent_on, border` — all existing.
  RTL handling: flex auto-flips; numeric values forced `direction: ltr`
  (standard Arabic-document convention for currency figures).

- **`recipes/financial-invoice.yaml`** (new) — 8-section UAE tax
  invoice:
  1. `letterhead` **commercial variant** — **FIRST PRODUCTION
     CONSUMER** (Day-2 variant waited 13 days for first real use;
     NOC Day-8 used formal). Tax Invoice eyebrow + ref code + date.
  2. `sections-grid` **bordered variant** — **FIRST PRODUCTION
     CONSUMER** of bordered. Bill From / Bill To 2-col with TRN
     per party.
  3. `kv-list` boxed — **third production consumer** (NOC field-
     summary, handoff status-grid, now invoice meta strip). 4 fields:
     Invoice Date / Supply Date / Due Date / Currency.
  4. `data-table` dense — **FIFTH production consumer + FIRST use
     of `{text, sub}` cell mapping** that was built Day 13
     specifically for invoice's description column. 7 columns (# /
     Description / Qty / Unit / VAT% / VAT / Total), 3 line items,
     each with a title + scope-note sub-line in the description cell.
  5. `financial-summary` default — **FIRST PRODUCTION CONSUMER**.
     4 rows (Subtotal / Discount / VAT / Total) with currency "AED".
  6. `callout` neutral — **fourth production consumer**.
     "Amount in Words" block.
  7. `sections-grid` bordered (2nd instance in recipe) — Payment
     Terms + Bank Details 2-col with inline-styled `<dl>` for bank
     kv fields.
  8. `module` raw_body — inline footer (density block #1): VAT Law
     citation + thank-you + signature line.
  Content adapted from `v1-reference/domains/financial/templates/
  invoice.en.html`. Placeholder prose preserved.
- **Rendered output: 2 pages, 0 WeasyPrint warnings.** `target_pages:
  [1, 2]`, `page_limit: 2`. Within target.
- **Validation clean at default + strict** — 0 content-lint warnings.
- **1 density-convention inline block** (footer) — well below NOC's
  ceiling of 4. The recipe composes primarily from existing
  components; inline styling is minimal.
- **2 financial-summary component-requests logged** (invoice + quote).
  **3 invoice recipe-requests logged.**
- **Audit + capabilities:** component + recipe register entries +
  `capabilities.yaml` regenerated.

### Tests (Phase 3 Day 15)

- **`tests/test_financial_summary.py`** (new, 11 tests): schema-
  loads, compact-variant-declared, rows-required, token-contract,
  renders-EN (2 non-total rows + 1 total row), renders-AR
  (dir=rtl), renders-to-pdf, compact-variant-class-emitted,
  default-variant-class, currency-appended-to-total-label,
  currency-absent-when-unset, total-row-emphasis-class (regression
  guard for the `--total` modifier).
- **`tests/test_financial_invoice.py`** (new, 20 tests): schema-
  loads, en-only, page-targets [1, 2], eight-section-ordering,
  uses-letterhead-commercial-variant (regression guard for the
  Day-2 commercial variant's first real use),
  first-financial-summary-consumer (regression guard for 4 rows +
  variant: total on last row + AED currency), data-table-uses-
  text-sub-cells (regression guard for the 7-col + 3-row shape
  with all 3 descriptions using {text, sub} mapping), kv-list-
  boxed-for-meta-strip, sections-grid-bordered-first-consumer
  (regression guard for 2 bordered instances), fourth-callout-
  neutral-consumer, validates-clean, validates-strict-clean,
  renders-EN (5 marker classes), pdf-within-target-pages (1-2
  accepted), renders-all-v1-content (30+ distinct phrases),
  line-items-three-rows-with-sub-cells (regression guard: 3
  cell-sub spans inside the data-table), totals-has-accent-
  total-row, in-capabilities, audit-entry-exists.
- **Regression sweep:** 759/759 passing (was 728, +11 financial-
  summary +20 invoice tests). Zero WeasyPrint warnings across
  all 20 render paths.

### Architecture decisions (Phase 3 Day 15)

1. **financial-summary closes the Day-0 component queue (original 7).**
   Phase 3 started with a 7-component plan: kv-list (Day 1), letterhead
   (Day 2), masthead-personal (Day 5), multi-party-signature-block
   (Day 7), financial-summary (Day 15), recitals-block (still pending
   for mou), legal-disclaimer-strip (probably absorbed into callout
   neutral). 6 of 7 built. Plus 2 auto-graduated bonus components
   (sections-grid Day 11, data-table Day 13). Component library is
   now more complete than originally planned.
2. **letterhead commercial variant graduates after 13 days.** Built
   Day 2 with three variants (default, formal, commercial). NOC used
   formal; nothing used commercial until invoice. This validates the
   Phase-2 + early-Phase-3 "build variants speculatively IF the v1
   triage locked them in" pattern — commercial was always going to
   serve invoice and quote; the wait was just about reaching those
   recipes.
3. **data-table `{text, sub}` cell feature used where it was
   designed.** The feature was built Day 13 specifically for invoice's
   description column (v1 template review highlighted it). Day 15
   exercises it. No component revisions needed. This is a tight
   design-use loop — build for a specific future need, use it when
   that need arrives, validate in production.
4. **sections-grid bordered graduates.** Built Day 11 with 3 variants
   (default, dense, bordered). Dense shipped Day 11 (cheatsheet).
   Default shipped Day 12 (one-pager). Bordered shipped Day 15
   (invoice Bill From/To + Payment block). All three variants now
   have production consumers within 4 days.
5. **Honest-intent graduation pattern holding.** financial-summary
   has 2 verified dependents (invoice + quote), below the threshold
   of 3. Used `--force` + justification citing both recipes on the
   migrate list. Same pattern as Day 5's masthead-personal. Both
   decisions look cleaner in retrospect than forcing more dependents
   or deferring the component until an artificial third consumer.
6. **Financial domain 50% migrated.** Day 15 ships invoice; Day 16
   plan is quote (same infra, different variant). Financial domain
   completes after Day 16.
7. **Phase-3 progress: 10/14 recipes (71%) in 15 days.** Ahead of
   1-per-day pace. Remaining: quote (Day 16), MoU (Day 17 w/
   recitals-block), plus 2 tutorial recipes (onboarding,
   katib-walkthrough) + CV. Reachable by Day 20 with buffer.
8. **AR variant deferred (tenth recipe in a row).** Consistent
   since Day 4.

### Added (Phase 3 Day 14 — `business-proposal/proposal` recipe ships — business-proposal domain complete)

Ninth Phase-3 recipe migration. **Completes the business-proposal
domain** — all 3 recipes shipped (letter Day 4, one-pager Day 12,
proposal Day 14). First Phase-3 domain fully migrated. Zero new
components (streak = 2). data-table second-consumer validation
within 24 hours of Day-13 ship: 3 more production uses in one
recipe across distinct column shapes.

- **`recipes/business-proposal-proposal.yaml`** (new) — 11-section
  long-form commercial proposal:
  1. Inline `module` raw_body — **title page** with eyebrow +
     36pt h1 + subtitle + 4-item meta-block (Reference / Issued /
     Prepared by / For). Density block #1. `page-break-after:
     always` inline.
  2. Inline `module` raw_body — **Table of Contents** with 5
     numbered rows (number + title + page). Density block #2.
     TOC graduation deferred: only 2 verified dependents (proposal
     + onboarding) — below auto-graduation threshold of 3.
  3. `module` variant=numbered, number=1, title="Executive Summary"
     with lead paragraph (inline-styled 12pt) + 2 body paragraphs.
  4. `module` variant=numbered, number=2, title="Program Scope"
     — intro paragraph only.
  5. `data-table` — **Program Scope deliverables** (4 columns:
     # / Module / Focus / Outcome; 4 rows). **Second production
     consumer of data-table.**
  6. `module` variant=numbered, number=3, title="Delivery Timeline"
     — intro paragraph.
  7. `data-table` — **Delivery Timeline schedule** (4 columns:
     Week / Theme / Group A / Group B; 6 rows). **Third production
     consumer.**
  8. `module` variant=numbered, number=4, title="Investment &
     Terms" — intro + lead paragraph.
  9. `data-table` — **Investment milestones** (3 columns:
     Milestone / Trigger / Amount; 4 rows including Total).
     **Fourth production consumer.** Total row workaround:
     colspan not supported, so "Total" in col 1, blank col 2,
     value in col 3.
  10. `module` plain — Section 4 closing paragraph (VAT,
      materials, MSA reference).
  11. `module` variant=numbered, number=5, title="Acceptance" —
      body paragraph + inline acceptance block with 3-box
      sign-row (Name & Title / Signature / Date). Density block #3.
      sign-row graduation deferred: 1 verified dependent
      (proposal only).
  Content adapted from `v1-reference/domains/business-proposal/
  templates/proposal.en.html`. Placeholder prose preserved
  (e.g., `[PROP/2026/001]`, `[Client Organization]`).
- **Rendered output: 5 pages, 0 WeasyPrint warnings.** Placeholder
  prose renders shorter than v1's ~10-page template-with-content;
  `target_pages: [5, 10]`, `page_limit: 12` accepts both.
- **Validation clean at default + strict** — 0 content-lint warnings.
- **3 density-convention inline blocks** (title page, TOC,
  sign-row-in-acceptance) — below NOC's ceiling of 4.
- **module numbered variant validated at scale again.** White-paper
  Day 13 used 6 instances; proposal Day 14 uses 5. Two data points
  from two recipe families — the Phase-2 design holds.
- **3 proposal recipe-requests logged.**
- **Audit + capabilities:** register entry + `capabilities.yaml`
  regenerated.

### Tests (Phase 3 Day 14)

- **`tests/test_business_proposal_proposal.py`** (new, 18 tests):
  schema-loads, en-only, page-targets [5, 10], eleven-section-
  ordering, three-data-table-consumers (regression guard for
  4/4/6/4/3/4 shapes + captions + Total row workaround),
  five-numbered-module-sections (regression guard for [1,2,3,4,5]),
  title-page-has-meta-block (regression guard for 4 meta pairs +
  page-break-after), toc-has-five-numbered-rows (HTML-entity-aware
  content check), acceptance-has-inline-sign-row (entity-aware
  check for 3-box layout + flex), validates-clean,
  validates-strict-clean, renders-EN (3 data-table-wrap count +
  5 module-numbered count), pdf-within-target-pages (5-10),
  renders-all-v1-content (22+ distinct phrases across all 11
  sections + 3 tables), three-captions-rendered (accessibility
  regression guard), completes-business-proposal-domain (sentinel
  test asserting the 3 recipe filenames exist), in-capabilities,
  audit-entry-exists.
- **Regression sweep:** 728/728 passing (was 710, +18 proposal
  tests). Zero WeasyPrint warnings across all 19 render paths.

### Architecture decisions (Phase 3 Day 14)

1. **data-table validated at scale within 24 hours.** Day 13
   shipped with 1 production consumer (white-paper, 5-col numeric).
   Day 14 adds 3 more (4-col text, 4-col matrix, 3-col numeric
   with custom total row) in a single recipe. **Zero component
   changes needed.** Same discipline as Day 11→12 for sections-grid:
   ship the component, then exercise it immediately across shape
   variations.
2. **TOC deferred on evidence.** 2 verified dependents (proposal
   + onboarding) below the threshold of 3. Inline-style proposal's
   TOC; defer graduation until a third recipe introduces the same
   shape. Matches metrics-grid's Day-12 decision. A `toc` component
   may graduate when onboarding ships if no third dependent has
   appeared by then (honest-intent pattern for essential shapes).
3. **sign-row deferred on evidence.** 1 verified dependent
   (proposal). Inline-style. If MoU's acceptance section or a
   future service-agreement recipe introduces a similar 3-box
   sign-row, graduation triggers.
4. **colspan workaround in data-table.** Invoice and proposal
   both have "Total" rows that v1 renders with
   `<td colspan="2">`. v2's data-table doesn't support per-row
   colspan hints. Workaround: put "Total" in col 1, blank col 2,
   value in col 3. Visually matches 95% of intent; semantically
   clearer (column count stays consistent). If invoice needs a
   fancier total row later, extend data-table with a
   `row_type: "summary"` or a `colspan` cell attribute — but
   only when a second recipe requires it.
5. **Business-proposal domain fully migrated — first domain
   complete.** Phase 3 started with 14 recipes across 7 domains.
   Day 14 closes business-proposal cleanly: letter (Day 4, 4
   sections), one-pager (Day 12, 5 sections, zero-new-component),
   proposal (Day 14, 11 sections, zero-new-component). All three
   compose primarily from `letterhead` (letter) + `sections-grid`
   (one-pager) + `data-table` + `module numbered` (proposal).
6. **Phase-3 pace summary through Day 14:**
   - 9 recipes shipped in 14 days (0.64/day — slightly below the
     0.69 Day-13 pace due to Day-14 being a longer recipe)
   - 6 new components built (kv-list, letterhead, masthead-personal,
     multi-party-signature-block, sections-grid, data-table)
   - 4 component evolutions complete (100% of original plan)
   - 2 auto-graduated components (sections-grid, data-table) beyond
     the original 7-component plan
   - 0 pivot days lost (CV-pivot Day 10, metrics-grid Day 12, TOC
     Day 14 — all happened during planning, not execution)
7. **AR variant deferred (ninth recipe in a row).** Consistent
   since Day 4.

### Added (Phase 3 Day 13 — `data-table` primitive + `editorial/white-paper` recipe ship)

Fifth infra+recipe combo day. **Second Phase-3 component to
auto-graduate** via the request log (4 verified dependents logged
before scaffold: white-paper, proposal, invoice, onboarding — no
--force). Eighth Phase-3 recipe migration.

- **`components/primitives/data-table/`** (new) — primitive-tier
  accessible tabular data component. Supports per-column numeric
  alignment (`align: num` → right-aligned + tabular-nums), optional
  column widths, optional caption, and cells that are either plain
  strings OR `{text, sub?}` mappings (for invoice-style description
  cells with muted sub-lines). Variants: `default` (zebra alt rows
  via `tag_bg`), `bordered` (per-cell borders, no alt), `dense`
  (tighter padding for high-column-count tables). Token contract:
  `text, text_secondary, text_tertiary, accent, accent_on, border,
  tag_bg` — all existing tokens, no new ones needed. Accessibility:
  `<caption>` preferred over sibling heading; `<th scope="col">`
  on every column header. Root wrapped in `<section lang="...">`
  because the validator's a11y regex doesn't accept `<table>` as
  a lang-carrying root (out-of-scope for today; hygiene workaround).

- **`recipes/editorial-white-paper.yaml`** (new) — 12-section
  white-paper recipe:
  1. Inline `module` raw_body — **title page** with 36pt h1 + 14pt
     italic subtitle + byline/date (density block #1, `page-break-
     after: always` via inline style)
  2. `callout` tone=neutral — **Executive Summary abstract**.
     Third production consumer of neutral tone (cover-letter subject,
     NOC purpose, now white-paper abstract — neutral is the primary
     non-status highlight tone).
  3. `module` variant=numbered, number=1 — **Introduction** with
     inline-styled drop cap (`<span style="font-size: 28pt; color:
     accent; ...">T</span>` on the opening letter).
  4. `module` variant=numbered, number=2 — **The State of the
     Problem** with inline h3 sub-sections (2.1, 2.2) and footnote
     ref.
  5. `data-table` — **Indicator trends, 2020-2026**: 5 columns
     (Indicator + 4 years), 3 rows, 4 numeric-aligned columns.
     **First production consumer of data-table.**
  6. `module` variant=numbered, number=3 — **The Argument** with
     footnote ref.
  7. `pull-quote` variant=rule-leading — central claim quote with
     attribution. **First Phase-3 consumer of pull-quote**
     (was used in tutorial.yaml Phase-2 but this is the first
     Phase-3 use — the primitive's been waiting in the wings).
  8. `module` variant=numbered, number=4 — **Counterarguments &
     Limits** with inline h3 + ul.
  9. `module` variant=numbered, number=5 — **Implications &
     Recommendations** with inline h3 per-stakeholder + ol.
  10. `module` variant=numbered, number=6 — **Conclusion**.
  11. Inline `module` raw_body — **Notes (footnotes)** ordered
      list with top border (density block #2).
  12. Inline `module` raw_body — **About the Author** box with
      bordered background, author name + bio + contact (density
      block #3).
  Content adapted verbatim from `v1-reference/domains/editorial/
  templates/white-paper.en.html`. Placeholder prose preserved.
- **Rendered output: 4 pages, 0 WeasyPrint warnings.** Squarely
  within `target_pages: [4, 8]` with `page_limit: 10`. Title page
  takes 1 full page; body fills 3 more under placeholder prose
  (real content would push to 5-8).
- **Validation clean at default + strict** — 0 content-lint warnings.
- **3 density-convention inline blocks** (title page, footnotes,
  about-author) — below NOC's ceiling of 4. The 6 numbered body
  sections use module's native `numbered` variant — no inline
  styling needed for the section-num markers.
- **4 data-table component-requests logged** (white-paper,
  proposal, invoice, onboarding). **3 white-paper recipe-requests
  logged**.
- **Audit + capabilities:** component + recipe register entries +
  `capabilities.yaml` regenerated.

### Tests (Phase 3 Day 13)

- **`tests/test_data_table.py`** (new, 15 tests): schema-loads,
  variants-declared (bordered + dense), columns-and-rows-required,
  token-contract (text/accent/accent_on/border/tag_bg),
  renders-EN (semantic `<table>`/`<thead>`/`<tbody>`, 3 `<th>`s,
  num class on align:num columns), renders-AR (dir=rtl),
  renders-to-pdf, bordered-variant-class, dense-variant-class,
  default-variant-class-when-unset, caption-rendered-when-set,
  caption-absent-when-unset, cell-with-sub-text (invoice-style
  regression guard), column-width-hint-applied (inline style),
  th-scope-attribute-for-a11y (3 `scope="col"` count).
- **`tests/test_editorial_white_paper.py`** (new, 18 tests):
  schema-loads, en-only, page-targets [4, 8], twelve-section-
  ordering, first-data-table-consumer (regression guard for 5
  cols, 4 numeric, 3 rows, caption), third-callout-neutral-
  consumer (pairs-with regression guard), uses-pull-quote-rule-
  leading (first Phase-3 use), six-numbered-module-sections
  (regression guard for [1,2,3,4,5,6] numbers + section titles),
  validates-clean, validates-strict-clean, renders-EN (4 marker
  classes), pdf-within-target-pages (4-8 accepted),
  renders-all-v1-content (25+ distinct phrases spanning title
  page / abstract / 6 numbered sections / data-table / pull-quote /
  footnotes / about-author), data-table-has-five-columns-rendered
  (scope="col" count inside the data-table wrap), three-data-rows-
  rendered, drop-cap-inline-styled, in-capabilities,
  audit-entry-exists.
- **Regression sweep:** 710/710 passing (was 677, +15 data-table
  +18 white-paper tests). Zero WeasyPrint warnings across all 18
  render paths.

### Architecture decisions (Phase 3 Day 13)

1. **Second Phase-3 auto-graduation — the request-driven flow is
   now the default path.** sections-grid Day 11 was the first;
   data-table Day 13 is the second. Both logged 3+ real requests
   tied to verified v1 templates *before* scaffolding. Neither
   needed `--force`. The pattern is now: (a) 4-template verification
   scan, (b) log request per verified dependent, (c) scaffold +
   build. Days 1/2/5/7 components used `--force` by necessity
   because the request log was either stale or the threshold
   hadn't been reached — that's the old normal. Day 11/13 is the
   new normal.
2. **Primitive tier for data-table.** Tables live inline in body
   prose (white-paper, proposal body, invoice line items) — they're
   not top-level sections. `pull-quote` and `callout` are similar
   in-body primitives. This matches the tier taxonomy.
3. **Cell flexibility via `{text, sub}` mapping.** The invoice
   requirement (description cell with muted sub-line) could have
   forced a variant-per-recipe split. Instead, allowing each cell
   to be string OR mapping keeps one component serving all 4
   dependents with no forking. The cost is `<span>` wrapping on
   every cell — acceptable for accessibility clarity.
4. **module's `numbered` variant carried white-paper's 6 sections.**
   Phase-2 module 0.2.0 introduced the variant; Day-3 0.3.0 made
   title optional. White-paper is the first production recipe to
   exercise `numbered` at scale (6 consecutive instances). Zero
   component changes needed — the Phase-2 design holds. Same
   pattern as Day 11's sections-grid validation within 24 hours.
5. **Drop cap via inline span, not CSS `::first-letter`.** v1
   used `.body-start::first-letter` pseudo-element. WeasyPrint
   supports `::first-letter` but the effect is fragile with
   `float: left` (which WeasyPrint's float model handles poorly
   in paged media). Inline-spanning the first letter with explicit
   styles (`font-size: 28pt; color: accent; float: left`) is less
   elegant but renders predictably. The inline approach is also
   user-editable in the recipe YAML.
6. **Validator regex limitation — workaround, not fix.** The a11y
   validator's `_ROOT_LANG_RE` accepts only section/div/article/main
   as lang-carrying roots. data-table's root is `<table>` which
   would trigger a false warning. Wrapped in `<section lang="...">`.
   A proper fix (patch the regex to include `<table>`) is out of
   scope for a recipe day; logged mentally for a future maintenance
   pass.
7. **AR variant deferred (eighth recipe in a row).** Consistent
   since Day 4.
8. **Day-14 plan:** Continue evidence-driven path. Remaining 6
   recipes: proposal (4-section business proposal, similar to
   one-pager but longer + deliverables-table using Day-13's data-
   table), cv (2-day infra+recipe sprint), invoice + quote (need
   financial-summary + data-table), mou (needs recitals-block),
   onboarding (needs section-divider + contact-card grid +
   Day-13's data-table), katib-walkthrough (pure composition?).
   Instinct: proposal Day 14 as pure composition + data-table
   reuse. Will verify before committing.

### Added (Phase 3 Day 12 — `business-proposal/one-pager` recipe ships)

Seventh Phase-3 recipe migration. **Resumes the zero-new-component
streak** (broken intentionally on Day 11 for sections-grid; streak
now 1 again after validation-driven decision to defer metrics-grid).
Second production consumer of sections-grid (default variant
validates the component beyond Day-11 cheatsheet's dense variant).

Day 12 started with a deferred-graduation decision. Pre-day scan of
v1 proposal.en.html (401 lines) confirmed it does NOT reuse the
`metrics-grid` 4-col big-number shape — proposal uses title-page +
TOC + deliverables-table + sign-row. This means metrics-grid has
only 1 verified dependent (one-pager itself), below the auto-
graduation threshold of 3. **Decision: inline-style the metrics
block in one-pager; defer metrics-grid graduation until a second
recipe introduces the same shape.** Matches the density convention.

- **`recipes/business-proposal-one-pager.yaml`** (new) — 5-section
  recipe:
  1. `module` raw_body — **eyebrow row**: company left + ref·date
     right in a hairline-bordered strip (inline-styled density
     block #1)
  2. `module` raw_body — **hero**: 26pt accent title + 11pt
     subtitle lead paragraph (inline-styled density block #2)
  3. `module` raw_body — **metrics block**: 4-col inline grid
     (Participants / Duration / Training days / Investment) with
     20pt accent numbers + 8pt tertiary labels, bordered top +
     bottom hairlines (inline-styled density block #3).
     **Deferred metrics-grid graduation — 1 verified dependent
     below threshold of 3.**
  4. `sections-grid` default variant, columns=2 — **SECOND
     PRODUCTION CONSUMER of sections-grid**. 2x2 body grid
     (Program scope / Delivery model / Outcomes / Next step).
     Last card (`Next step`) uses inline `raw_body` with `<a>`
     CTA styled as accent-bg button.
  5. `module` raw_body — **footer strip**: company·author left +
     ref right with top hairline (inline-styled density block #4).
  Content adapted from `v1-reference/domains/business-proposal/
  templates/one-pager.en.html`. Placeholder-style prose preserved
  (`[Proposal title…]`, `[PROP/2026/001]`, etc.).
- **Rendered output: 1 page, 0 WeasyPrint warnings.** `target_pages:
  [1, 1]`, `page_limit: 1` — one-pager's whole point is single-page,
  and the render holds.
- **Validation clean at default + strict** — 0 content-lint warnings
  on the proposal prose + placeholders.
- **4 density-convention inline blocks** (eyebrow-row, hero,
  metrics, footer) — at NOC's ceiling but within it. If a future
  recipe introduces a second eyebrow-row, second hero, or second
  4-metrics shape, those become component candidates.
- **3 one-pager recipe-requests logged**.
- **Audit + capabilities:** register entry + `capabilities.yaml`
  regenerated.

### Tests (Phase 3 Day 12)

- **`tests/test_business_proposal_one_pager.py`** (new, 17 tests):
  schema-loads, en-only, single-page-target (exactly [1, 1]),
  has-no-cover-page, five-section-ordering, second-sections-grid-
  consumer (regression guard for default variant + columns=2 +
  4 cards), metrics-block-inline-styled (regression guard for the
  deferred-graduation decision — asserts `repeat(4, 1fr)` inline),
  validates-clean, validates-strict-clean, renders-EN (asserts
  `katib-sections-grid--default` present, no cover), pdf-fits-
  one-page (strict 1-page assertion), renders-all-v1-content
  (15 distinct phrases spanning eyebrow/hero/4-metrics/4-sections/
  CTA/footer), four-metric-blocks-rendered (counts inline accent
  20pt markers), sections-grid-four-cards (card count regression
  guard), cta-rendered-in-last-card (asserts Accept proposal +
  accent-bg token), in-capabilities, audit-entry-exists.
- **Regression sweep:** 677/677 passing (was 660, +17 one-pager
  tests). Zero WeasyPrint warnings across all 17 render paths.

### Architecture decisions (Phase 3 Day 12)

1. **metrics-grid deferred on evidence, not instinct.** The
   Day-10 lesson ("read the v1 template before committing") kept
   paying dividends today. Proposal's body was read end-to-end
   before Day 12 started; metrics-grid was revealed as a 1-recipe
   shape. Matches the density convention: *build abstractions when
   a second recipe needs the same shape, not speculatively.*
2. **sections-grid validated across two variants.** Day 11 shipped
   with cheatsheet (dense, 6 cards with raw_body). Day 12 exercises
   default (2 cards per row, 4 cards total, mix of plain `body` and
   `raw_body`). Zero component revisions needed — the Day-11 design
   held. This is the *"find component issues within 24 hours"*
   discipline from Day-12 planning paying off.
3. **One-pager is the first single-page Phase-3 recipe.** Prior
   recipes targeted [1, 2] (letter, cover-letter, NOC) or [2, 3]
   (how-to, handoff, cheatsheet=1-2). One-pager's `target_pages:
   [1, 1]` with `page_limit: 1` enforces the single-page constraint.
   Render met it on first try — good signal that component margins
   are tuned for compact compositions.
4. **Four inline blocks = NOC's ceiling tested.** NOC (Day 8)
   introduced 4 inline-styled module raw_body blocks as "density
   permitted for structurally dense recipes." One-pager matches
   that count. Both recipes landed clean. If Day-13's white-paper
   pushes past 4, we revisit the ceiling. Until then, 4 remains
   the informal cap.
5. **CTA as inline `<a>` inside sections-grid card.** `Next step`
   card uses `raw_body` with an `<a>` styled as accent-bg button.
   This is inside-card styling (like cheatsheet's kbd chips) —
   distinct from recipe-level inline. If a second recipe needs
   a CTA button, a `cta-button` primitive graduates.
6. **AR variant deferred (seventh recipe in a row).** Consistent
   since Day 4.

### Added (Phase 3 Day 11 — `sections-grid` component + `tutorial/cheatsheet` recipe ship)

Fourth "component infra + recipe same-day" combo (after Days 1+2 kv-list
and letterhead, Day 5 masthead-personal + callout, Day 7 kv-list 0.2.0 +
multi-party-signature-block). Breaks the zero-new-component streak at 5
— but **intentionally**, because sections-grid has 3 verified Phase-3
dependents (cheatsheet, one-pager, possibly handoff retrofit) which
passed the auto-graduation threshold for the first time in Phase 3.

- **`components/sections/sections-grid/`** (new) — section-tier component
  for titled-card grids. Supports 2/3/4 column layouts via explicit
  `columns` input (avoids WeasyPrint's lack of `auto-fit` support).
  Cards accept `title` (required) + optional `body` (plain text) or
  `raw_body` (trusted HTML); optional per-card `eyebrow` for role-style
  labels (contact-card role). Variants: `default` (loose gap),
  `dense` (tight gap + smaller typography for cheatsheet),
  `bordered` (each card gets 0.5pt border + padding for contact-card
  visual separation). Token contract: `text, text_tertiary, accent,
  border` (no speculative tokens — lint-clean on first pass). No
  WeasyPrint warnings; no RTL-specific CSS needed (grid layout works
  across directions without physical-property overrides).

- **`recipes/tutorial-cheatsheet.yaml`** (new) — 3-section recipe:
  1. `module` with eyebrow="Cheatsheet" + title + intro — compact
     header (second no-cover module-with-eyebrow header after Day 10's
     handoff)
  2. `sections-grid` dense variant — **first production consumer**.
     6 cards in 2-col grid: Quick actions, Navigation, Vault, Terminal,
     Common flags, Troubleshooting. Each card uses `raw_body` with
     inline-styled `<dl>`/`<ul>` content for keyboard shortcuts +
     commands + troubleshooting notes. Demonstrates sections-grid's
     "card as container for arbitrary structured content" design.
  3. `module` raw_body — inline-styled footer strip (ref + date with
     top border, monospace, muted text)
  Content adapted from `v1-reference/domains/tutorial/templates/
  cheatsheet.en.html`. Placeholder-style tool name preserved.
- **Rendered output: 1 page, 0 WeasyPrint warnings.** Cheatsheet fits
  on a single A4 at v2 defaults — matches v1 design intent.
  `target_pages: [1, 2]`, `page_limit: 2`.
- **Validation clean at default + strict** — 0 content-lint warnings.
- **3 sections-grid component-requests logged** (cheatsheet, one-pager,
  handoff-retrofit). **3 cheatsheet recipe-requests logged**
  (katib-recipe-cheatsheet, git-shortcuts-cheatsheet,
  vim-commands-cheatsheet).
- **Audit + capabilities:** component + recipe register entries +
  `capabilities.yaml` regenerated.

### Tests (Phase 3 Day 11)

- **`tests/test_sections_grid.py`** (new, 14 tests): schema-loads,
  variants-declared (dense + bordered), items-required, token-contract
  (text/accent/border referenced), renders-EN, renders-AR (dir=rtl),
  renders-to-pdf, dense-variant-class-emitted, bordered-variant-class-
  emitted, default-variant-class-when-unset, column-count-emitted
  (2/3/4), default-columns-is-2, raw-body-takes-precedence-over-body,
  optional-eyebrow-and-heading-and-card-eyebrow (regression guard for
  opt-in behaviour), page-break-inside-avoid-styles-present.
- **`tests/test_tutorial_cheatsheet.py`** (new, 16 tests): schema-
  loads, en-only, page-targets [1, 2], has-no-cover-page,
  three-section-ordering, first-sections-grid-consumer (regression
  guard for dense variant + columns=2 + 6 cards with correct titles),
  module-header-uses-eyebrow-pattern, validates-clean,
  validates-strict-clean, renders-EN (2 component marker classes +
  negative cover assertion), pdf-within-target-pages,
  six-cards-rendered (regression guard for `<article>` count),
  renders-all-v1-content (18 distinct phrases spanning 6 cards),
  in-capabilities, audit-entry-exists.
- **Regression sweep:** 660/660 passing (was 630, +14 sections-grid
  +16 cheatsheet tests). Zero WeasyPrint warnings across all 16
  render paths.

### Architecture decisions (Phase 3 Day 11)

1. **sections-grid is the first Phase-3 component built to
   *auto-graduate*.** Prior Phase-3 components (kv-list Day 1,
   letterhead Day 2, masthead-personal Day 5, multi-party-
   signature-block Day 7) were built with --force + justification
   because request logging was either stale or below threshold.
   Day 11 logged 3 real requests tied to verified v1 templates
   (cheatsheet, one-pager, handoff retrofit) *before* scaffolding.
   The graduation threshold (3) passed cleanly; no --force needed.
   This is the request-driven graduation flow working as designed.
2. **Explicit `columns` input over `auto-fit`.** WeasyPrint doesn't
   support `grid-template-columns: repeat(auto-fit, ...)` (codified
   Day 7 after the multi-party-signature-block warning). sections-grid
   requires consumers to declare column count up-front (2, 3, or 4).
   This is a small UX tax but a reliability win — no silent layout
   breakage under WeasyPrint.
3. **`raw_body` takes precedence over `body` in cards, matching
   module's convention.** Cheatsheet's cards need complex HTML (dl
   for kv shortcuts, ul with kbd chips for commands, div with strong
   + code for troubleshooting). Simple text cards (one-pager bodies)
   use `body`. The precedence rule (raw_body wins when both set)
   avoids ambiguity.
4. **Cheatsheet uses heavy inline styling inside raw_body cards.**
   Every card has inline-styled `<dl>`/`<ul>`/`<div>` with font-mono
   keyboard shortcut styling, tag-bg chips, accent labels. This is
   *inside-card* inline styling — distinct from recipe-level inline
   styling. sections-grid provides the card skeleton; the card
   *content* is consumer territory. If multiple recipes end up with
   the same kv-shortcut + kbd-chip styling, a `shortcut-list`
   primitive becomes the next candidate for graduation.
5. **No-cover compact-header pattern now has 2 consumers** (handoff
   Day 10, cheatsheet Day 11). Template convention codifying: working
   docs and reference docs don't need covers; use `module` with
   `eyebrow: "[Document type]"` + `title` + `intro` as a compact
   opener. Matches v1 design intent for both document types.
6. **AR variant deferred (sixth recipe in a row).** Consistent since
   Day 4.
7. **One-pager queued for Day 12.** sections-grid's second consumer.
   `metrics-grid` is the only verified-new component needed for
   one-pager (4-metric row with big accent number + small label).
   Day 12 will be another infra+recipe combo if metrics-grid has ≥3
   verified dependents; otherwise inline-style the metrics and ship
   one-pager as pure composition (hybrid approach to evaluate on
   Day 12 planning).

### Added (Phase 3 Day 10 — `tutorial/handoff` recipe ships)

Fifth Phase-3 recipe migration. **Fifth zero-new-component recipe
in a row** (Days 4, 6, 8, 9, 10). First Phase-3 recipe to validate
the *headerless* pattern — no cover page, no title page, content
starts directly with a compact module header.

Day 10 was preceded by a plan pivot: `personal/cv` was scoped as the
Day 10 target but investigation of the v1 template revealed a
2-column sidebar layout with 4-5 genuinely new component shapes
(sidebar grid, skill-bar-list, tag chips, experience-entry,
education-entry). CV deferred to a proper 2-day infra+recipe sprint
later in Phase 3. `tutorial/handoff` picked instead after verifying
its v1 template composes from existing components + density-convention
inline styles only.

- **`recipes/tutorial-handoff.yaml`** (new) — 11-section recipe:
  1. `module` with eyebrow="Handoff" + title + intro — compact
     header (no cover page by design — handoff is a working doc)
  2. `kv-list` boxed — **4-field status meta**: Status / Reference /
     Handoff date / Owner. **Second production consumer of kv-list
     boxed** — validates the component serves status-grid shape as
     well as NOC's field-summary shape (both 4-7 item KV grids with
     identical styling; the Day-7 boxed variant handles both).
  3. `module` plain — Summary
  4. `module` raw_body — What shipped bullet list (release, docs,
     monitoring, runbook, follow-ups)
  5. `module` plain — Architecture in 30 seconds
  6. `callout` tone=info — **first production consumer of info
     tone** (prior consumers: NOC+cover-letter used neutral;
     how-to used tip+warn). "Key decision" box for ADR-adjacent
     context.
  7. `module` raw_body — Runbook with 3 `<h3>` sub-sections +
     `<pre><code>` code blocks (inline-styled tag-bg code styling)
  8. `module` raw_body — Known issues: 3 inline-styled severity
     cards (Medium / Low / Low) with warn-bg + info-bg token
     backgrounds and left accent borders. Density-convention block.
  9. `module` raw_body — Contacts: 4 inline-styled contact cards
     in a 2x2 flex grid (Handing off / Taking over / Escalation /
     On-call). Density-convention block.
  10. `module` raw_body — Next steps ordered list
  11. `callout` tone=tip — **second production consumer of tip
      tone** after how-to. "One last note" closing message.
  Content adapted from `v1-reference/domains/tutorial/templates/
  handoff.en.html`. Placeholder-style prose preserved
  (`[Feature / service / area being handed off]`,
  `[Outgoing owner]`, `[Incoming owner]`, etc.).
- **Rendered output: 3 pages, 0 WeasyPrint warnings.** No cover
  page — content starts at page 1 with the compact module header.
  3-page split: ~page 1 (header + status meta + summary + what
  shipped), ~page 2 (architecture + key decision + runbook),
  ~page 3 (known issues + contacts + next steps + closing).
  `target_pages: [2, 3]` with `page_limit: 3`.
- **Validation clean at default + strict** — 0 content-lint warnings
  on the handoff prose + placeholders.
- **3 recipe-requests logged** — soul-hub-feature-handoff,
  on-call-rotation-handoff, signal-forge-pipeline-handoff
  (stand-in signals for future handoff consumers).
- **Audit + capabilities:** register entry + `capabilities.yaml`
  regenerated.

### Tests (Phase 3 Day 10)

- **`tests/test_tutorial_handoff.py`** (new, 18 tests): schema-
  loads, en-only, page-targets [2, 3], has-no-cover-page (regression
  guard for the headerless pattern), eleven-section-ordering,
  uses-kv-list-boxed-status-grid (second production consumer
  regression guard, 4 terms: Status/Reference/Handoff date/Owner),
  first-callout-info-consumer (regression guard for tone=info's
  debut), second-callout-tip-consumer (pairs-with-how-to regression
  guard), module-header-uses-eyebrow-pattern (validates the
  no-cover compact-header pattern), validates-clean,
  validates-strict-clean, renders-EN (3 component marker classes +
  negative assertion for cover), pdf-within-target-pages (2-3
  accepted), renders-all-v1-content (22 distinct phrases spanning
  header/meta/summary/what-shipped/architecture/key-decision/runbook/
  known-issues/contacts/next-steps/closing), known-issues-inline-
  block-present (regression guard for density-block severity
  counts + token bg refs), contacts-inline-block-present (regression
  guard for 4 labels), in-capabilities, audit-entry-exists.
- **Regression sweep:** 630/630 passing (was 612, +18 handoff
  tests). Zero WeasyPrint warnings across all 15 render paths.

### Architecture decisions (Phase 3 Day 10)

1. **Day 10 pivot proved honest estimation matters.** The original
   CV plan fell over on contact with the v1 template. Lesson: read
   the v1 template *before* committing to a "pure composition" day
   — instincts about recipe complexity can't substitute for
   validation. Zero velocity lost by the pivot because handoff
   shipped cleanly the same day; the recovery was fast precisely
   because the pivot happened during planning, not during execution.
2. **Zero-new-component streak = 5.** Business-letter → cover-letter
   → NOC → how-to → handoff. The component library is handling
   composition at a rate that was hard to predict. 6 of 14 Phase-3
   recipes now shipped (43%) using 4 of the 7 planned Phase-3
   components. Remaining 8 recipes will likely split: 4-5 pure
   composition (handoff-like), 3-4 needing 1-2 new components
   (CV, white-paper, invoice, one-pager, cheatsheet, mou).
3. **kv-list boxed is now validated as dual-purpose.** First used
   Day 7 for NOC's 7-field employee details (field-summary shape);
   Day 10 used for handoff's 4-field status grid (status-meta shape).
   Same variant, same styling, two distinct editorial roles. This
   is the component library working — *one variant, multiple
   document-scoped semantics*.
4. **"Headerless" composition is a first-class pattern.** Handoff
   intentionally has no cover page or front-matter — content starts
   at the compact module header. This is the right shape for
   working docs (runbooks, handoffs, internal memos) where a full
   cover would be overkill. Documents *without* covers are as
   legitimate as documents *with* covers.
5. **Inline-styled "card grid" pattern used twice but not
   graduated.** Known-issues (3 severity cards) and Contacts (4
   info cards) are structurally similar: flex container of N
   similar cards with accent/border + label + title + detail.
   *Same recipe, not a second recipe.* The density convention
   says: build a `card-grid` component when a *second recipe*
   introduces the same shape. Onboarding.en.html uses contact-cards
   too — when onboarding ships (Day 11+), we'll see if graduation
   is justified.
6. **Code-block styling as inline style.** The runbook's
   `<pre><code>` blocks use inline tag-bg token + padding styling.
   This is a candidate for a `code-block` primitive if multiple
   recipes need it (cheatsheet and katib-walkthrough likely will).
   Deferred to the point of consumer-count signal.
7. **AR variant deferred (fifth recipe in a row).** Consistent
   since Day 4; NOC remains the designated first-bilingual recipe
   that triggers `inputs_by_lang` schema design.

### Added (Phase 3 Day 9 — `tutorial/how-to` recipe ships)

Fourth Phase-3 recipe migration. **Fourth zero-new-component
recipe in a row** — confirms the component library has reached the
size where most tutorial and procedural docs compose from existing
primitives + sections. First Phase-3 recipe to use the covers tier.

- **`recipes/tutorial-how-to.yaml`** (new) — 12-section recipe:
  1. `cover-page` minimalist-typographic (CSS-only, zero cost,
     factual tone) — **first Phase-3 recipe to use the covers tier**
  2. `module` raw_body — lead paragraph (inline-styled `.lead`
     class via p tag)
  3. `objectives-box` boxed — "Before you start" preconditions
     (3 items); second production consumer after tutorial.yaml
  4-7. `tutorial-step` × 4 — **first production consumer**
     (previously only used in phase-2-day5-showcase). Numbered
     1-4, each with title + body.
  8. `callout` tone=tip — **first production consumer of tip
     tone** (cover-letter and noc both used neutral).
  9. `callout` tone=warn — **first production consumer of warn
     tone**.
  10. `module` raw_body — Do/Don't 2-col inline-styled compare
      box (flex layout, tip-bg/danger-bg halves). Single-recipe
      use per density convention — we wait for a second consumer
      before graduating a `compare-box` section.
  11. `module` raw_body — "If it doesn't work" h2 + 3-item
      troubleshooting bullet list (inline-styled).
  12. `whats-next` bullet — 3-item forward CTA; second consumer
      after tutorial.yaml.
  Content adapted from `v1-reference/domains/tutorial/templates/
  how-to.en.html`. Placeholder-style title preserved
  ("[Primary action the reader will accomplish]") since how-to
  is a template, not an instance.
- **Rendered output: 3 pages, 0 WeasyPrint warnings.** Cover is
  always 1 full page under `page_behavior.break_after: always`.
  Body fits in 2 pages given component-level whitespace.
  `target_pages: [2, 3]` with `page_limit: 3` — within bounds.
- **Validation clean at default + strict** — 0 content-lint
  warnings on the procedural prose.
- **3 recipe-requests logged** — how-to-soul-hub-vault, how-to-
  claude-skill-install, how-to-katib-ci-setup (stand-in signals
  for future how-to consumers).
- **Audit + capabilities:** register entry + `capabilities.yaml`
  regenerated.

### Tests (Phase 3 Day 9)

- **`tests/test_tutorial_how_to.py`** (new, 18 tests): schema-
  loads, en-only, page-targets [2, 3], twelve-section-ordering,
  uses-cover-page-minimalist (first Phase-3 covers-tier use),
  uses-objectives-box-boxed (second production consumer),
  first-tutorial-step-production-consumer (regression guard —
  4 numbered steps, 1-4, each with title + body),
  first-callout-tip-and-warn-consumers (regression guard —
  both tones in the `[tip, warn]` order),
  uses-whats-next-bullet (second production consumer),
  validates-clean, validates-strict-clean, renders-EN (6
  component marker classes), pdf-within-target-pages (2-3
  accepted), renders-all-v1-content (17 distinct phrases
  spanning cover/lead/prereqs/4-steps/tip/warn/do-dont/
  troubleshooting/whats-next), four-tutorial-steps-rendered
  (counts `<div class="katib-tutorial-step__circle">`),
  do-dont-inline-block-present (asserts Do/Don't halves +
  callout-tip-bg/callout-danger-bg token references),
  in-capabilities, audit-entry-exists.
- **Regression sweep:** 612/612 passing (was 594, +18 how-to
  tests). Zero WeasyPrint warnings across all 14 render paths.

### Architecture decisions (Phase 3 Day 9)

1. **Zero-new-component streak hits 4.** Business-letter (Day 4)
   → cover-letter (Day 6) → NOC (Day 8) → how-to (Day 9) all
   shipped without building a new component. The v2 component
   library has reached a size where template-style procedural
   docs compose from primitives + sections + carefully-scoped
   inline style. This reshapes the Phase-3 remaining queue:
   financial-summary and recitals-block may still be needed for
   invoice/quote and legal/mou, but the remaining tutorial and
   editorial recipes (cheatsheet, white-paper, how-to, onboarding,
   handoff, katib-walkthrough) look like pure composition OR
   +1 component at most.
2. **Do/Don't as inline-styled module — not a new component.**
   Used exactly once in how-to; no other migrate-list recipe in
   the scan has a 2-col compare layout (cheatsheet has a
   section-grid, different shape). Matches the density
   convention: *build abstractions when a second recipe needs
   the same shape, not speculatively.* If onboarding or any
   other recipe later introduces the same compare pattern,
   THAT's when `compare-box` graduates.
3. **`tutorial-step` promoted from showcase-only to production
   without change.** The component was built in Phase 2 (Day 5
   showcase) and never needed revisions to serve how-to. Clean
   proof that the Phase-2 component design held up.
4. **Cover variant choice: minimalist-typographic.** CSS-only,
   no Gemini cost, no external assets, matches the factual
   procedural tone. Image covers would be decorative noise for
   a how-to.
5. **AR variant deferred (fourth recipe in a row).** Consistent
   pattern since Day 4; `inputs_by_lang` schema design remains
   tied to NOC's bilingual port, not triggered by template-style
   procedural recipes.
6. **Placeholder-style content over realistic content.** Like
   NOC, how-to is a *template* — users fill in action,
   screenshots, tip text. The v1 template style is preserved
   (`[Primary action…]`). Realistic-content exemplars are a
   separate deliverable; not in scope for Phase 3 recipe migration.

### Added (Phase 3 Day 8 — `formal/noc` recipe ships)

Third Phase-3 recipe migration. Densest recipe yet (10 sections vs
cover-letter's 8 vs letter's 4) and first real test of the
"inline-style budget scales with recipe density" convention from
Day 6 ADR. Zero new components built.

- **`recipes/formal-noc.yaml`** (new) — 10-section recipe:
  1. `letterhead` formal variant (Day 2) — austere uppercased
     company, 1.25pt text-color rule
  2-3. `module` raw_body × 2 — inline-styled banner labels
     (doc-marker "NO OBJECTION CERTIFICATE" with top+bottom hairlines;
     opener "TO WHOM IT MAY CONCERN" centered larger letter-spaced)
  4. `module` raw_body — opening body paragraph (justified)
  5. `kv-list` boxed variant (Day 7) — 7-field employee details
     (Name/Nationality/Passport No./Emirates ID/Position/Date of
     Joining/Employment Status)
  6. `callout` neutral tone (Day 5) — purpose block with label
     "Purpose of this letter"
  7. `module` raw_body — validity-line (centered dashed-border
     box with inline `<strong>` for the day count)
  8. `module` raw_body — closing paragraph
  9. `multi-party-signature-block` (Day 7) — 2-party signature grid
     (HR signatory with email + Authorised signatory box for stamp)
  10. `module` raw_body — footer note (bordered, small, muted,
      centered)
  Content ported verbatim from `v1-reference/domains/formal/
  templates/noc.en.html`. Placeholder-prose template style preserved
  (v1's `[Full name as per passport]`, `[Nationality]`, etc.).
  Stamp-hint decorative circle intentionally dropped (position:
  absolute under WeasyPrint paged media is finicky; stamp placement
  is a post-print physical act).
- **Rendered output: 2 pages, 200KB PDF, 0 WeasyPrint warnings.** v1
  NOC fit 1 page with 30mm/25mm margins; v2 renders to 2 pages under
  20mm defaults because component-level whitespace (kv-list boxed
  padding, multi-party-signature-block 34pt padding-top for signing
  line, etc.) adds ~25mm of structural space v1 didn't have. Page 1
  = letter content (letterhead → closing paragraph). Page 2 =
  signatures + footer. Architecturally acceptable — components
  provide semantic spacing; target_pages [1, 2] permits this.
- **Validation clean at default + strict** — 0 content-lint warnings
  on formal NOC prose + placeholders.
- **3 recipe-requests logged** — visa-application, bank-account-
  opening, school-enrolment (stand-in for "dependent registration")
  signals.
- **Audit + capabilities:** register entry + `capabilities.yaml`
  regenerated.

### Tests (Phase 3 Day 8)

- **`tests/test_formal_noc.py`** (new, 16 tests): schema-loads,
  en-only, page-targets, ten-sections-in-order,
  uses-letterhead-formal-variant, uses-kv-list-boxed-variant
  (Day 7 first production consumer), uses-multi-party-signature-
  block (Day 7 first production consumer),
  uses-callout-neutral-tone (Day 5 second production consumer),
  validates-clean, validates-strict-clean, renders-EN (4 component
  marker classes), pdf-within-target-pages (1 or 2 accepted),
  renders-all-v1-content (14 distinct phrases + 7 field labels),
  employee-details-has-seven-fields (kv-list boxed regression
  guard), in-capabilities, audit-entry-exists.
- **Regression sweep:** 594/594 passing (was 578, +16 NOC tests).
  Zero WeasyPrint warnings across all 13 render paths.

### Architecture decisions (Phase 3 Day 8)

1. **Inline-style density convention validated.** NOC has 4 distinct
   inline-styled `module raw_body` blocks (doc-marker, opener,
   validity-line, footer-note) — more than any prior recipe. Each
   is NOC-specific (no other migrate-list recipe has centered-
   formal-notice shapes per Day 8 planning scan). Accepting these
   as inline styles rather than building a speculative
   `banner-label` primitive matches the Phase-3 rule:
   *build abstractions when a second recipe needs the same shape,
   not speculatively.* The inline styles all use token vars
   (`var(--accent)`, `var(--text)`, `var(--border)`,
   `var(--border-strong)`, `var(--text-secondary)`,
   `var(--text-tertiary)`) and supported WeasyPrint CSS properties
   — zero warnings in render.
2. **v2 page-count divergence is acceptable.** v1 NOC was 1 page;
   v2 renders to 2. This isn't a bug — it's the honest outcome of
   richer component-level whitespace. A recipe-level
   `page_margins` schema override was considered and deferred:
   *"don't design for hypothetical future requirements."* If a
   stakeholder later requires strict 1-page NOC, we add the
   schema then (~30 min feature).
3. **Stamp-hint intentionally dropped.** v1 had a decorative
   "COMPANY STAMP" circle positioned bottom-right via
   `position: absolute`. Under WeasyPrint paged media, absolute
   positioning across pages is finicky. The stamp is also a
   physical placement hint, not legal substance. Dropping it
   keeps the recipe focused on legal structure.
4. **Callout neutral for purpose block — minor v1 divergence
   accepted.** v1's purpose div had no left border; v2's callout
   neutral adds a 3pt accent left border. Visual improvement
   (accent emphasis) trumps pixel-perfect v1 fidelity. v2 is a
   thoughtful port, not a copy.
5. **Letterhead formal variant's ref-block missing label
   prefixes.** v1 has "Ref: X / Date: Y" (labeled rows); v2
   renders ref_code + date as plain stacked lines. Minor visual
   divergence; content clarity preserved since ref format
   (`NOC/2026/042`) and date format are self-descriptive. Not
   worth extending letterhead schema for this one recipe.

### Added (Phase 3 Day 7 — component infra for `formal/noc`)

Third "component infra day" (after Days 3 + 5). Builds the two additions
the NOC recipe needs before it can ship on Day 8.

- **`components/sections/multi-party-signature-block/`** (new) — Day-0
  queue item #3 of 6, section-tier component that lays out 2+ parties
  in a responsive side-by-side signature grid. Each party has
  `name` (required) + `title` + `email` (optional). Variants:
  `line-over` (default, top border as signing line) and `minimal` (no
  borders). Heading optional. Flexbox layout with
  `flex: 1 1 200pt` for auto-flow across 2-N parties (WeasyPrint
  doesn't support `grid-template-columns: repeat(auto-fit, ...)`,
  documented in the Day-7 ADR entry as the primary workaround
  convention). Email field forced `dir="ltr"` inside AR templates
  (continues the letterhead/masthead pattern). Tokens: `text`,
  `text_secondary`, `text_tertiary`. Zero hex in stylesheet.
- **`components/sections/kv-list/`** — v0.1.0 → v0.2.0 — added
  `boxed` variant for field-summary use (NOC employee details,
  future invoice/quote meta). Inverts emphasis relative to default:
  term renders as small-uppercase label-style (`text_secondary`,
  9pt, letter-spaced, normal weight); value renders as emphasized
  data (`text`, 10.5pt, 600 weight). Container adds background
  (`tag_bg`), leading accent border (3pt `accent`), 14pt × 18pt
  padding. Dotted row separators replace the default solid ones.
  RTL override flips the leading border to the trailing side
  (WeasyPrint doesn't support `border-inline-start` — hence the
  physical-property pattern with `[dir="rtl"]` override).
  `requires.tokens` gains `tag_bg` + `accent`. Existing default/
  dense/spacious variants unchanged.
- **Graduation reality for multi-party-signature-block:** 2 firm
  Phase-3 dependents (NOC Day 8 + mou later), below the automated
  threshold. Same honest-intent pattern as masthead-personal (Day 5):
  scaffold past the soft-warning, log 2 real requests, document
  intent in the ADR audit trail.
- **Audit + capabilities:** register entries for both components in
  `memory/component-audit.jsonl`; `capabilities.yaml` regenerated.

### Tests (Phase 3 Day 7)

- **`tests/test_multi_party_signature_block.py`** (new, 12 tests):
  schema-loads, parties-required, variants-declared, heading-
  optional, renders-EN-two-party, renders-AR, email-forced-ltr-in-
  arabic, renders-three-party-grid (flex auto-flow regression guard),
  line-over-top-border, minimal-variant, heading-rendered-when-set,
  heading-omitted-when-unset, styles-tokens-only, EN/AR-share-
  semantic-structure.
- **`tests/test_kv_list_v02.py`** (new, 8 tests): version-bumped,
  boxed-variant-declared, requires-added-tokens, boxed-renders-EN,
  boxed-renders-to-PDF, boxed-AR-flips-accent-border-to-right,
  styles-tokens-only, boxed-emphasis-inverted (stylesheet contract
  guards the term/value emphasis inversion).
- **`tests/test_kv_list.py`** — `test_kv_list_loads_against_schema`
  updated (0.1.0 → 0.2.0 version assertion).
- **Regression sweep:** 578/578 passing (was 556, +22 Day-7 tests +
  1 version-assertion update). Zero WeasyPrint warnings.

### Architecture decisions (Phase 3 Day 7)

1. **WeasyPrint constraints on modern CSS.** Two CSS logical/modern
   properties tripped during Day 7 render tests:
   (a) `grid-template-columns: repeat(auto-fit, minmax(200pt, 1fr))`
       — unsupported; switched to `flex` with `flex: 1 1 200pt` for
       auto-flow.
   (b) `border-inline-start` — unsupported; switched to `border-left`
       with explicit `[dir="rtl"]` override flipping to `border-right`.
   Phase-3 convention going forward: **prefer flex over grid for
   flexible column counts**; **use physical border properties with
   direction overrides instead of logical properties**. The
   `text-align: end` logical property DOES work in WeasyPrint
   (confirmed on cover-letter), so it's the exception.
2. **kv-list variant widens component scope without splitting.**
   `boxed` variant serves NOC's field-summary use case, which could
   have justified a separate `field-summary-box` primitive (Day-0
   scan initially proposed this). Chose to extend kv-list because
   semantically both are "term + value pairs" — boxed is a
   presentation variant, not a distinct shape. This parallels the
   Day-5 call to extend `callout` with `neutral` rather than build
   a separate primitive for non-status highlights. The rule-of-thumb:
   if the shape is the same and only styling differs, it's a variant.
3. **Emphasis inversion via variant is legitimate.** `kv-list` boxed
   variant inverts term/value emphasis (default: term bold+dark,
   value lighter; boxed: term lighter+uppercase-label, value bold+
   dark+emphasized). This is an aesthetic decision — the field-
   summary idiom reverses the scanning emphasis (field labels recede,
   data advances). Stylesheet contract tested via
   `test_kv_list_boxed_emphasis_inverted`.
4. **Day-0 scan `field-summary-box` component eliminated.** By
   extending kv-list with boxed variant, the Day-0 queue item (one
   of 17 proposed NEW components) is absorbed into kv-list. Running
   Day-0-queue-resolution tally: `kv-list` (Day 1 base) +
   `letterhead` (Day 2) + `masthead-personal` (Day 5 —
   not-in-day-0-list, queue-revision) + `multi-party-signature-block`
   (Day 7) = 4 of original queue items resolved; `field-summary-box`
   absorbed into kv-list as variant.

### Added (Phase 3 Day 6 — `personal/cover-letter` recipe ships)

Second Phase-3 recipe migration. Richer than the business letter (8
sections vs 4) but still zero new components — Day 5's infrastructure
carried the whole recipe.

- **`recipes/personal-cover-letter.yaml`** (new) — 8-section recipe:
  1. `masthead-personal` (Day 5) — personal identity header
  2. `module` heading-less (Day 3) — date line (right-end-aligned via inline style)
  3. `signature-block` recipient variant (Day 3) — addressee
  4. `callout` neutral tone (Day 5) — subject line
  5. `module` heading-less (Day 3) — salutation + 3 body paragraphs + closing
  6. `signature-block` default line-over — closing signature
  7. `rule` hairline variant — enclosure separator
  8. `module` heading-less — enclosure line
  Content ported verbatim from `v1-reference/domains/personal/templates/
  cover-letter.en.html`. Placeholder-prose style preserved — the v1
  cover-letter is a template-for-editing (instructional prose in
  square brackets for the author to replace). EN-only per the
  `inputs_by_lang` deferral established Day 4.
- **Inline-style compromise.** Date-line and enclosure-line modules use
  `<p style="...">` in their `raw_body` with token-driven colors
  (`var(--text-tertiary)`) and logical-property alignment
  (`text-align: end`). Considered dedicated `date-line` and
  `enclosure` primitives and rejected both as one-use entropy; recipe-
  local inline styling is the right scope when two short lines would
  otherwise force two one-off components.
- **Rendered output:** 1-page PDF (12KB), 0 WeasyPrint warnings.
- **Validation clean at default + strict** — 0 content-lint warnings
  on instructional placeholder prose. Pre-scan prediction confirmed.
- **3 recipe-requests logged** — job-application, portfolio-submission,
  formal-introduction signals.
- **Audit + capabilities:** register entry in `memory/recipe-audit.jsonl`;
  `capabilities.yaml` lists the new recipe.

### Tests (Phase 3 Day 6)

- **`tests/test_personal_cover_letter.py`** (new, 16 tests):
  schema-loads, en-only, page-targets, eight-sections-in-order,
  uses-masthead-personal (Day 5 first production consumer),
  uses-callout-neutral-tone (Day 5 first production consumer),
  uses-recipient-variant (Day 3 second production consumer),
  uses-rule-hairline, body-module-has-no-title (Day 3 third production
  consumer), validates-clean, validates-strict-clean, renders-EN
  (all 8 component marker classes present), pdf-within-target-pages,
  renders-all-v1-placeholder-content, in-capabilities, audit-entry-
  exists.
- **Regression sweep:** 556/556 passing (was 540, +16 cover-letter
  tests). Zero WeasyPrint warnings.

### Architecture decisions (Phase 3 Day 6)

1. **Placeholder-prose template style preserved.** Unlike Day 4's
   business-letter (realistic sample content), cover-letter ships
   with v1's instructional placeholders (`[Opening paragraph — the
   why]`, `[Hiring Manager Name]`). This is a recipe-style decision
   worth noting: letter-class recipes can be **exemplar** (realistic
   sample, user substitutes identifiers) or **template** (placeholder
   prose, user rewrites). Business-letter is exemplar; cover-letter
   is template. Both patterns are valid; the v1 author already made
   the correct call per recipe type, and Day-6 honors it.
2. **Recipe-local inline styling is acceptable scope.** Two short
   lines (date + enclosure) with minor typographic distinctness
   (right-aligned small muted for date; small muted for enclosure).
   Rejected: dedicated `date-line` and `enclosure` primitives
   (one-use entropy); stretching `signature-block` to cover date
   (wrong semantic); no styling (visually off from v1). Chose: inline
   `<p style="...">` with token vars (`var(--text-tertiary)`) and
   logical property (`text-align: end` for locale safety). Phase-3
   convention: inline-style is OK for 1-2 line recipe-specific tweaks
   that would otherwise force a one-use component.
3. **8 sections is not too many.** Day 4's business letter was 4
   sections; Day 6 is 8. Each section serves a distinct role (header,
   date, addressee, subject, body, signature, separator, enclosure).
   A denser recipe is still readable and structural — the per-section
   YAML is small.

### Added (Phase 3 Day 5 — component infra for cover-letter)

Second "component infra day" (after Day 3). Builds the two components
cover-letter (Day 6) needs before it can ship thin.

- **`components/sections/masthead-personal/`** (new) — personal-identity
  masthead for personal-brand documents. Sibling to `letterhead` but
  semantically distinct: organizational identity (company + ref + date)
  vs personal identity (name + tagline + contact stack). Forecast on
  Day 2 when the letterhead `personal` variant was explicitly rejected
  in favor of this separate component. Two-column flex with RTL
  cascade, 1.5pt bottom accent rule, optional brand-identity fallback
  (`email`/`phone` inputs fall back to `brand.identity.email`/
  `identity.phone` when unset). Forced LTR on email + phone inside AR
  templates (same pattern as letterhead's `reference_code` — addresses
  + phone numbers are structurally LTR inside RTL documents).
  Scoped tight: no variants. Tokens: `accent`, `text_secondary`,
  `text_tertiary`. Zero hex in stylesheet.
- **`components/primitives/callout/` — v0.1.0 → v0.2.0** — added
  `neutral` tone for non-status highlighted boxes (cover-letter
  subject lines, legal non-binding notices, inline emphasis
  paragraphs). The existing `info | warn | danger | tip` tones carry
  status semantics (pale blue/amber/red/green bg + matched accent);
  `neutral` uses `tag_bg` + `accent` for cases where colored status
  would be semantically wrong. `requires.tokens` gains `tag_bg` +
  `accent`; existing tones unchanged. README rewritten with full
  tone table and use-case guidance. Previously missing test fixture
  created.
- **Graduation reality for masthead-personal:** 2 firm Phase-3
  dependents (cover-letter Day 6 + cv later in Phase 3), below the
  automated threshold of 3. Scaffolded past the soft-gate warning
  (scaffold doesn't hard-block); 2 real requests logged in
  `memory/component-requests.jsonl`. Intent-verified via ADR Day 5
  entry — load-bearing shared component for personal-brand documents
  (cover-letter + cv + bio-deferred). First Phase-3 component that
  clears a threshold-below situation honestly rather than
  speculatively padding the request count to 3.

### Tests (Phase 3 Day 5)

- **`tests/test_masthead_personal.py`** (new, 14 tests): schema-loads,
  name-required, contact-fields-optional, identity-brand-fields-
  declared, token-contract, no-variants (scope-lock), renders-EN,
  renders-AR, ar-contact-rows-forced-ltr, tagline-optional,
  contact-fields-skip-when-all-missing, brand-identity-fallback
  (renders without crashing when inputs unset and brand supplies),
  styles-tokens-only, EN/AR-share-semantic-structure.
- **`tests/test_callout_v02.py`** (new, 8 tests): version-bumped,
  requires-tokens-added-for-neutral, neutral-renders-class, neutral-
  renders-to-PDF, neutral-bilingual, existing-4-tones-still-render
  (regression), stylesheet-has-neutral-rules, stylesheet-preserves-
  all-five-tones.
- **Regression sweep:** 540/540 passing (was 518, +22). Zero
  WeasyPrint warnings across 10 new render paths (masthead EN/AR +
  5 callout tones × EN/AR sampled).

### Architecture decisions (Phase 3 Day 5)

1. **Semantic-distinct primitives over vague unification.** Chose to
   build `masthead-personal` as a separate component rather than
   stretch `letterhead` with a `personal` variant. Rationale: the
   schema shapes differ too much — letterhead has
   `company + reference_code + date + doc_title` for organizational
   identity; masthead-personal has `name + tagline + email + phone +
   location` for personal identity. Unifying would force conditional
   schema (`company OR name`, `meta OR contact`) which vagues the
   contract for downstream authors. Day 2's explicit scoping decision
   ("build cover-letter later, see what its real header needs, add a
   variant or sibling component") pointed exactly here; Day 5 honors
   that decision.
2. **`callout` scope widens to non-status highlights.** The existing
   4 tones all carry status semantics (info/warn/danger/tip). The
   `neutral` tone extends callout's role to "any boxed highlight with
   accent border" — cover-letter subject lines + legal non-binding
   notices + future inline-emphasis paragraphs. Stays inside one
   primitive's semantic umbrella (boxed message with accent border);
   doesn't create a second highlight-box primitive.
3. **Brand-identity fallback is a template-level concern, not schema-
   level.** `masthead-personal` inputs `email` + `phone` are "optional
   with brand fallback" — the template uses `input.email or
   identity.email` to pick recipe value over brand value. Recipe stays
   clean when brand supplies identity; brand profile stays unchanged
   when recipe overrides. The same pattern can extend to other
   components that consume brand identity fields; Phase-3 components
   using this pattern: masthead-personal (Day 5), letterhead (Day 2,
   via `logo.primary`).
4. **Graduation threshold is intent, not a gate.** `masthead-personal`
   shipped with 2 real requests (below threshold of 3). Honest
   documentation of intent in the ADR + audit trail beats padding the
   count to hit the automated gate. The graduation mechanism is a
   soft-gate on scaffold; registration doesn't enforce it. Lesson:
   when genuine intent is below 3 firm dependents + ≥1 planned
   deferred, document the decision and proceed.

### Added (Phase 3 Day 4 — first Phase-3 recipe ships)

First real recipe migration. `business-proposal/letter` (v1 monolithic
template) → `business-proposal-letter.yaml` (v2 thin composition of 4
sections, zero new components).

- **`recipes/business-proposal-letter.yaml`** (new) — 4-section recipe:
  1. `letterhead` (default variant) — company + reference + date
  2. `signature-block` (recipient variant, Day 3) — addressee block
  3. `module` (no title, Day 3) — continuous-prose body with
     salutation + 3 paragraphs + closing
  4. `signature-block` (default line-over) — closing signature
  Content ported verbatim from `v1-reference/domains/business-proposal/
  templates/letter.en.html`. EN-only for now; AR variant deferred
  pending `inputs_by_lang` schema design (see Architecture decisions
  below).
- **Recipe metadata:** `languages: [en]`, `target_pages: [1, 2]`,
  `page_limit: 3`, keywords `letter,business,proposal,formal,
  correspondence,cover`.
- **Rendered output:** 1-page PDF (11KB), 0 WeasyPrint warnings.
  Matches v1 letter's 1-page behavior.
- **3 recipe-requests logged** — cover-letter-for-training-proposal,
  meeting-request, partnership-introduction signals. First real
  entries in `memory/recipe-requests.jsonl`.
- **Validation clean at default + strict** — 0 content-lint warnings
  on v1 body prose (pre-scan hit rate confirmed: no banned-openers,
  emphasis-crutches, vague-declaratives, or meta-commentary in the
  ported content).
- **Audit + capabilities:** register entry in `memory/recipe-audit.jsonl`;
  `capabilities.yaml` lists the new recipe.

### Tests (Phase 3 Day 4)

- **`tests/test_business_proposal_letter.py`** (new, 15 tests):
  schema-loads, en-only, page-targets, four-sections-in-order,
  recipient-variant-used (Day-3 component in production), body-module-
  has-no-title (module v0.3.0 in production), closing-signature-default
  variant, keywords-present, validates-clean, validates-strict-clean,
  renders-EN (4-section marker classes present), pdf-one-page,
  renders-all-v1-content (line-wrap tolerant whitespace collapse),
  in-capabilities (registration regression guard), audit-entry-exists
  (build.py gate regression guard).
- **`tests/test_recipe_ops.py:test_scaffold_graduation_warning_when_log_missing`**
  regression-fixed — same pattern as Day-1 component-ops sibling fix.
  Monkey-patches `ops.REQUESTS_FILE` to tmp_path because the real
  `memory/recipe-requests.jsonl` is now populated.
- **Regression sweep:** 518/518 passing (was 503, +15 letter-recipe
  tests). Zero WeasyPrint warnings.

### Architecture decisions (Phase 3 Day 4)

1. **`inputs_by_lang` recipe-schema feature deferred to NOC-day.**
   The v2 recipe schema has no per-language content pattern today.
   Existing bilingual showcases declare `languages: [en, ar]` but
   ship English-only content — the AR render is "English text in RTL
   direction," not culturally-adapted content. For a production letter
   with different prose per language (v1 ports), this is inadequate.
   Rather than design the schema extension today, deferred to the
   NOC day: NOC is the first truly bilingual recipe in the migrate
   list, and its scan proved the content differs per language. Day 4
   ships EN-only letter honestly declaring `languages: [en]`; matches
   tutorial.yaml's pattern.
2. **Content-lint didn't trip — recipe ships content-clean.** The
   v1 letter's business prose was written to sharp-prose standards
   already; no rewriting needed. This is the first production recipe
   validated under the Day-13 content-lint contract; the wiring
   proved unobtrusive for well-written content.
3. **4-section thin recipe validates the composition model.** The
   letter is 13 non-whitespace lines of YAML composing 4 sections
   — no template authoring, no custom HTML in the recipe (except the
   `raw_body` wrapper `<p>` tags around the prose). Proves that the
   Phase-2 architectural investment (primitives + sections + thin
   recipes) pays off for real doc-types, not just tutorials. The
   Day-3 component extensions (signature-block recipient + module
   no-title) were the load-bearing infrastructure.

### Added (Phase 3 Day 3 — component infra for letter-class recipes)

Two component evolutions enabling the business-letter recipe shape.
Day 3 invested in components first, per the Phase-3 discipline of
"build new components before the recipes that depend on them."

- **`signature-block` 0.1.0 → 0.2.0** — added two optional inputs
  (`organization`, `location`) and one variant (`recipient`) that
  widens the primitive's role from "signatory only" to "named party
  in a document's context." Existing `line-over` and `label-prefix`
  variants unchanged; backwards-compatible for all pre-0.2.0 recipes.
  The `recipient` variant strips the top border and adjusts spacing
  for use as an addressee block at the top of a letter. README
  rewritten with explicit signatory-vs-addressee role table.
- **`module` 0.2.0 → 0.3.0** — `title` relaxed from required to
  optional. A module with only `raw_body` (or `body`) now renders as
  pure continuous prose with no head region emitted. Template
  pre-computes `has_head = number or eyebrow or title or intro`;
  when false, the `<div class="katib-module__head">` collapses
  entirely — not an empty div. Enables letter bodies, legal recitals,
  abstract paragraphs, and any section where a heading is not
  appropriate. Backwards-compatible — existing recipes providing
  `title` continue to emit `<h2>` unchanged.
- **Bug fix (pre-existing, caught by new tests):**
  `signature-block` templates had a latent bug where `variant=None`
  would wrongly render a "Signed" label under the default `line-over`
  variant (because the `variant or 'line-over'` fallback only applied
  in the class attribute, not in the `{% if variant != 'line-over' %}`
  condition). Both EN + AR templates now set
  `effective_variant = variant or 'line-over'` once and reuse it
  consistently. No previous recipe tripped this because every existing
  consumer passed an explicit variant; the new v0.2.0 tests
  (`test_signature_block_renders_default_signatory`) caught it.
- **Cleanup:** `module` component dropped unused `accent_2` +
  `text_tertiary` tokens from `requires.tokens` (validator flagged as
  declared-but-unreferenced). `signature-block` + `module` both gained
  test fixtures + restructured READMEs (Purpose/Inputs/Variants/
  Accessibility sections per the validator's doc contract).
- **Audit trail:** register entries in `memory/component-audit.jsonl`
  for both components; `capabilities.yaml` regenerated.

### Tests (Phase 3 Day 3)

- **`tests/test_signature_block.py`** (new, 8 tests): schema-loads,
  new-fields-present, recipient-variant-declared, new-fields-optional
  (backwards-compat guard), renders-default-signatory (variant=None
  path — regression-proof), renders-recipient-with-full-fields,
  label-prefix-still-works (regression), recipient-bilingual,
  without-optional-fields-still-renders.
- **`tests/test_module_v03.py`** (new, 8 tests): version-bumped,
  title-optional, renders-without-title-raw-body, renders-without-
  title-plain-body, without-title-bilingual, with-title-still-emits-h2
  (regression), tutorial-recipe-still-renders (production regression),
  eyebrow-only-still-renders-head.
- **Regression sweep:** 503/503 passing (was 486, +9 signature-block,
  +8 module-v03, which match the file counts). Zero WeasyPrint
  warnings on all render paths. Tutorial.yaml (9 modules) continues
  to render unchanged — validated structurally by
  `test_module_tutorial_recipe_still_renders`.

### Architecture decisions (Phase 3 Day 3)

1. **Primitive widens semantic rather than fragment.** Chose to
   extend `signature-block` with a `recipient` variant + two fields
   over building a new `recipient-block` primitive. Rationale: the
   primitive's true role is "named party in a document's context" —
   signatories and addressees both fit. Adding a new primitive would
   have fragmented what is semantically one concept across two
   components. Tests enforce the split via variant-specific
   structural checks.
2. **`module` schema aligned with its description.** The component
   description said "optional numbered eyebrow, heading, intro, and
   body content" since inception, but the schema declared
   `title: required: true`. Relaxing this is schema-catches-up-to-
   description, not an expansion of scope. Module remains a flexible
   body unit; continuous-prose sections are now a first-class use
   case rather than needing a new `prose-block` component
   (considered and rejected as entropy).
3. **Pre-existing latent bugs count as regressions too.** The
   signature-block label-under-line-over bug existed from day one
   but was masked by every consumer passing an explicit variant.
   The Day-3 test added exercised the default path and exposed it.
   Fix committed in the same change as the feature extension — good
   hygiene, but worth the ADR note: Phase 3 tests should continue to
   exercise default paths even when the affected variants weren't
   the day's focus.

### Added (Phase 3 Day 2 — `letterhead` section component)

Second Phase-3 component. Dependents: `business-proposal/letter`,
`business-proposal/one-pager`, `formal/noc`, `financial/invoice`,
`financial/quote` (5 recipes).

- **`components/sections/letterhead/`** (new) — 2-column header strip
  for letters, NOCs, invoices, quotes. Leading side: brand/company.
  Trailing side: doc title + reference code + date + custom meta lines.
  Bottom accent rule. Optional leading brand logo from
  `brand.logo.primary`. Does NOT force a page break (that's
  `front-matter`'s distinct role — see scope note below).
- **Variants:** `default` (business letter, 0.75pt accent rule,
  accent-color company), `formal` (NOC/legal, 1.25pt text-color rule,
  uppercased austere company, uppercased doc-title), `commercial`
  (invoice/quote, large accent doc-title, body-text-color company,
  top-aligned for tall meta blocks).
- **Tokens:** `accent`, `text`, `text_secondary`, `text_tertiary`.
  Zero hex in stylesheet (tested).
- **Bilingual:** EN + AR share semantic `<header>` skeleton. RTL
  cascade flips flex direction so leading side stays on visual start.
  `reference_code` is forced `dir="ltr"` in AR templates (codes are
  LTR inside RTL documents).
- **5 graduation requests logged** — letter, one-pager, noc, invoice,
  quote signals.
- **Audit + capabilities:** scaffold + register entries in
  `memory/component-audit.jsonl`; `capabilities.yaml` regenerated.

### Tests (Phase 3 Day 2)

- **`tests/test_letterhead.py`** (new, 16 tests): schema-loads,
  variants-declared, company-required, token-contract,
  does-not-force-page-break (regression guard for scope),
  declares-logo-brand-field, renders-EN, renders-AR (ref-code
  dir=ltr inside RTL asserted), renders-to-PDF, formal-variant,
  commercial-variant, meta-lines-order-preserved, doc-title-optional,
  logo-omitted-without-brand, styles-tokens-only,
  EN/AR-share-semantic-structure.
- **Regression sweep:** 486/486 passing (was 470, +16 letterhead
  tests). Zero WeasyPrint warnings on 6 render paths (EN/AR ×
  default/formal/commercial).

### Architecture decisions (Phase 3 Day 2)

1. **`letterhead` is distinct from `front-matter`.** Both are
   "document opener" sections but serve different page roles:
   `letterhead` is a header strip (<40pt) above body content on page
   1; `front-matter` is a title section that consumes the whole page
   via `break_after: always`. A regression test
   (`test_letterhead_does_not_force_page_break`) guards the boundary.
2. **Scoped tight to prevent entropy.** Rejected the `personal`
   variant during scoping — cover-letter's masthead (name+tagline |
   contact block) is structurally different enough that stretching
   `letterhead` to cover both would vague the schema. Cover-letter
   will either add a variant later (once its real shape is known) or
   get a sibling `masthead-personal` component. Don't pre-unify.
3. **Phase 3 component queue revised to 6 (was 5).** Day-2 scoping
   surfaced that the Day-0 structural scan over-counted dependents on
   existing components — the letterhead shape doesn't compose from
   `eyebrow` + `reference-strip`. Queue is now a living estimate, not
   a Day-0 contract; may grow again as Phase 3 progresses and more
   recipes are read critically.
4. **`reference_code` forced LTR inside Arabic.** Codes like
   `NOC/2026/042` are structurally LTR even when embedded in RTL
   documents. The AR template explicitly declares `dir="ltr"` on the
   ref div to prevent visual reversal. Asserted in
   `test_letterhead_renders_ar`.

### Added (Phase 3 Day 1 — `kv-list` section component)

First of 5 genuinely-new Phase-3 components. Dependents:
`tutorial/cheatsheet`, `tutorial/katib-walkthrough`, `legal/mou`,
`editorial/white-paper`, `financial/quote`.

- **`components/sections/kv-list/`** (new) — term + value pairs as a
  two-column `<dl>` grid. Variants: `default`, `dense` (cheatsheet),
  `spacious` (glossaries, legal defined-terms). Tokens: `text`,
  `text_secondary`, `border`. Fully bilingual (EN + AR) with RTL
  cascade; both language templates share the semantic skeleton
  (dt/dd) and differ only in `dir="rtl"` attribute.
- **3 graduation requests logged** (`memory/component-requests.jsonl`):
  cheatsheet-signal, white-paper-signal, quote-signal. Real requests,
  not retroactive — Phase-3 gate active from Day 1.
- **Audit trail:** scaffold + register entries in
  `memory/component-audit.jsonl`. Build-time gate (`scripts/build.py`)
  refuses orphans.
- **`capabilities.yaml`** regenerated — `kv-list` now discoverable by
  recipe composition + the content-aware router.

### Tests (Phase 3 Day 1)

- **`tests/test_kv_list.py`** (new, 13 tests):
  schema-loads, variants-declared, items-required, token-contract,
  renders-EN, renders-AR, renders-to-PDF, dense-variant-class,
  spacious-variant-class, default-variant-class, eyebrow+heading-optional,
  styles-use-tokens-only, EN/AR-share-semantic-structure.
- **`tests/test_component_ops.py:test_scaffold_graduation_warning_when_log_missing`**
  regression-fixed: previously assumed `memory/component-requests.jsonl`
  does not exist (Phase-2 transitional state); now monkey-patches
  `ops.REQUESTS_FILE` to an ephemeral path so the first-install
  soft-pass contract stays proven as the real log grows.
- **Regression sweep:** 470/470 passing (was 457, +13 kv-list tests).
  Zero WeasyPrint warnings on 6 render paths (EN/AR × default/dense/spacious).

### Architecture decisions (Phase 3 Day 1)

1. **Migrate list locked at 14 recipes.** Dropped legal/service-agreement
   in favor of legal/mou (simpler, no counsel review needed to validate
   the new components). Full list in ADR §Phase 3 and
   `~/vault/projects/katib/project.md`.
2. **Deferred v1 doc-types called out in CHANGELOG.** Academic,
   marketing-print, report domains plus ~7 on-demand variants (formal
   circular/authority-letter/government-letter, personal bio, financial
   summary/statement, editorial article/case-study/op-ed, legal
   nda/engagement-letter). Available in `v1-reference/`, not migrated.
3. **Open Item #3 (PNG goldens) pushed to Phase 4.** Phase 3 is recipe
   migration; visual regression harness is orthogonal scope.
4. **Bilingual NOC scoped as cheap.** Scan of
   `v1-reference/domains/formal/templates/noc.{en,ar}.html` confirmed
   both share identical semantic structure — RTL handled by CSS
   cascade + swapped borders, not structural mirroring. No new
   `bilingual-paired-section` component needed.
5. **`kv-list` uses semantic `<dl>` / `<dt>` / `<dd>`.** Chosen over
   `<table>` because the content is paired-definitions, not tabular
   data — screen readers announce as a description list.

### Added (post-close-out — content_lint wired into recipe validate/register)

Closes Open Item #2 from the Phase-2 gate review (Day-13 deferral).

- **`core/recipe_ops.py:validate_recipe_full()`** gains two keyword
  args:
  - `content_lint: bool = True` — run `core.content_lint.lint()` over
    the recipe's extracted prose.
  - `strict: bool = False` — promote warnings to errors (CI-friendly).
    Honors `KATIB_STRICT_LINT=1` env var as a synonym.
  - New check #7: `content_lint` violations emitted as
    `RecipeIssue(category="content")`. All findings surface as
    warnings by default; `--strict` promotes to errors.
  - `register_recipe`, `bundle_share_recipe`, `lint_all_recipes`
    forward both flags consistently.

- **`scripts/recipe.py`** — `validate`, `register`, `lint`
  subcommands each gain:
  - `--strict` — promote content-lint warnings to errors (blocks
    register when strict)
  - `--no-content-lint` — skip the content-lint pass entirely
    (legacy-content escape hatch)
  - `KATIB_STRICT_LINT=1` env var — CI-friendly synonym for `--strict`

### Design: three-mode gating contract

| Mode | Findings → | Blocks register? | Use case |
|---|---|---|---|
| default | all → warnings | no | daily authoring |
| `--strict` / env var | all → errors | yes | CI, production gate |
| `--no-content-lint` | skipped | no | legacy override |

Content-lint's internal `error`/`warn` severity is preserved in the
message text (`[banned-opener/error]`) but collapsed at the wiring
boundary — in default mode, ALL findings surface as warnings,
regardless of content_lint's own grading. This prevents aggressive
rules (like `banned-opener`) from silently blocking the first author
who tries the feature.

### Pre-wiring audit

Ran `content_lint` against all shipped artifacts before any code
change:
- **7/7 recipes clean** (including `tutorial.yaml` — 111KB production
  prose)
- **20/20 components × EN clean**
- **20/20 components × AR clean**

Zero pre-existing errors. Zero pre-existing warnings. Safe to wire at
warning-default.

### Tests

- **`tests/test_recipe_content_lint.py`** — 17 new tests covering
  all three modes, env-var synonym, CLI subprocess paths,
  `lint --all --strict` green on the full shipped tree (regression
  guard against future rule additions).

**457 tests pass** (440 → 457, +17).

### Scope discipline

- **Only `recipe_ops` wired** — component HTML templates are mostly
  Jinja placeholders (low signal); audit decision was to skip them.
- **`scripts/lint.py` standalone behavior unchanged** — Day 13's
  file-level linter still works the same way.
- **Zero regressions** in the 440 pre-wiring tests.

### Added (Day 14 — integration tests + exit-criteria suite)

- **`tests/test_phase2_integration.py`** — 6 cross-module integration
  tests:
  - T1 graduation workflow: log 3 requests → scaffold silent →
    validate → register → audit updated
  - T2 bare `/katib` happy path: transcript → infer HIGH → build.py →
    PDF written
  - T3 gate-fire full loop: resolve yes-fits/one-off → render action
  - T4 log-and-wait contract: resolve no-fit/recurring → wait action
    + recipe-request + gate-decision persisted, no PDF
  - T5 content-lint on `tutorial.yaml`: 0 errors (intentional
    production prose passes)
  - T6 audit-gate breakage: strip audit entry → `build.py` refuses
    with clean error

- **`tests/test_exit_criteria.py`** — 8 automated exit-criteria
  proofs, one per ADR §Phase 2 exit criterion. CI fails if any
  regresses:
  - EC1 Bloom framework guide renders via v2 tutorial recipe
  - EC2 `two-column-image-text` accepts user-file + gemini + url
  - EC3 `tutorial-step` supports optional screenshot
  - EC4 `chart-donut` accepts only inline-svg
  - EC5 Gemini-missing-key fails loud
  - EC6 SKILL.md describes v2 flow
  - EC7 `/katib` context-aware mode infers recipe + brand + lang
  - EC8 fresh-install flow renders tutorial cleanly

### Phase 2 — 14-day arc summary

| Day | Deliverable |
|---|---|
| 1 | Image providers wired into compose |
| 2 | Five Tier-2 scaffolding sections |
| 3 | module + cover-page minimalist variant |
| 4 | Cover image-background + neural-cartography |
| 5 | two-column-image-text + tutorial-step |
| 6 | chart-donut + chart-bar + chart-sparkline |
| 7 | tutorial.yaml (Bloom framework guide) |
| 8 | capabilities.py + gate.py |
| 9 | context_sensor.py |
| 10 | route.py + SKILL.md rewrite |
| 11 | katib component CLI |
| 12 | katib recipe CLI + unicode-bidi fix |
| 13 | request_log + content_lint + auto-persist |
| 14 | Integration + exit-criteria suites + gate review |

### Architectural properties proven in Phase 2

1. Composability — every visible element is a component
2. Self-contained — no sibling-skill dependencies
3. Trilingual — EN / AR / bilingual first-class
4. Four image providers with sources_accepted whitelist
5. Enforced graduation — build-time audit gate for components + recipes
6. Auto-persistence — gate decisions + inferences + request signals
7. Observable routing — summary + reasons + log_entry on every response
8. JSON-contract discipline — parseable JSON on every --json exit path

### Open items (Jasem's post-close-out decisions)

Tracked in `projects/katib/phase-2-gate-review.md`:
1. Push branch to GitHub + tag `v1.0.0-alpha.2`
2. Wire content-lint into `register`/`validate` (Day 13 deferral)
3. Add PNG golden-diff tooling (Day 11 deferral)
4. Phase 3 triage — which v1 doc-types migrate

### Added (Day 13 — request-log writer + content_lint port)

- **`core/request_log.py`** — JSONL writer + reader library for four
  memory files:
  - `memory/component-requests.jsonl` (Day-11 gate input)
  - `memory/recipe-requests.jsonl` (Day-12 gate input)
  - `memory/gate-decisions.jsonl` (every `route.py resolve` decision)
  - `memory/context-inferences.jsonl` (every `route.py infer` signal
    extraction)
  - Schema locked at `REQUEST_SCHEMA_VERSION = 1`. Writer populates
    both `requested` and `closest_existing` so either-key reader
    match (the Day-11/12 contract) always succeeds.
  - `KATIB_MEMORY_DIR` env var redirects all four paths — tests use
    `tmp_path`, production uses the repo default.
  - POSIX atomic-append (single `write()` per line <4KB) — verified
    by a 20-thread concurrent-append smoke test.
  - Reader API: `read_requests(kind, since=timedelta)`,
    `count_requests(kind, name)`, `search_requests(kind, needle)`,
    `read_gate_decisions`, `read_context_inferences`. `parse_since`
    understands `"7d" | "2w" | "12h"`.

- **`core/content_lint.py`** — v1's 421-line content linter ported as
  a library. All rules preserved (AR banned-openers, emphasis
  crutches, jargon, vague declaratives, meta commentary,
  untranslated abbreviations, ambiguous tech terms, واو chains; EN
  equivalents). `extract_text()` strips HTML + Jinja + `<style>` +
  `<script>`. `guess_language()` suffix-first, then char-ratio
  fallback. `lint(text, lang)` dispatcher. Pure Python, no vault or
  config imports.

- **`scripts/log_request.py`** — CLI with six subcommands:
  - `component [--requested X] [--closest Y] --intent "…" --reason "…"`
  - `recipe [--requested X] [--closest Y] --intent "…" --reason "…"`
  - `list {component|recipe} [--since 30d]`
  - `count {component|recipe} <name>`
  - `search {component|recipe} <term>`
  - `--json` global flag; identical error contract to Days 10/11/12.

- **`scripts/lint.py`** — content-lint CLI:
  - `<file>` or `--stdin` input modes
  - `--lang` force override
  - `--json` machine output
  - Exit codes: 0 (clean) / 1 (errors found) / 2 (bad input)

- **`scripts/route.py`** — auto-persistence wired:
  - `infer` persists the context inference (unless `--no-persist`)
  - `resolve` persists the gate decision AND drops a recipe-request
    entry on `log-and-fill` / `log-and-wait` / `request-graduation`
    (these are the signals that accumulate for recipe graduation)
  - Log writes wrapped in `try: except OSError/ValueError: pass` so
    a logging failure never breaks routing
  - `--no-persist` flag opts out (tests only)

### Changed (Day 13)

- **`tests/test_route.py`** — `_inject_no_persist()` helper appends
  `--no-persist` to every `infer`/`resolve` invocation so the 19
  existing tests preserve their no-disk-side-effect contract. Route
  tests assert routing decisions; persistence gets its own test file.

### Tests (Day 13)

81 new tests (345 → 426 total):
- **`tests/test_request_log.py`** (23 unit tests): memory-dir
  resolution, component/recipe append, read/count/search, `since`
  filtering, schema-version locks, 20-thread concurrent-append smoke,
  gate-decisions + context-inferences writers.
- **`tests/test_content_lint.py`** (29 unit tests): `extract_text`
  (tags / Jinja / style / script), `guess_language` (suffix + char
  ratio), every English rule, every Arabic rule (including
  translated-abbrev pass), `lint` dispatcher, `lint_file`.
- **`tests/test_log_request_cli.py`** (12 subprocess tests): every
  verb in both human and `--json` mode, JSON-contract regression
  guard.
- **`tests/test_lint_cli.py`** (11 subprocess tests): file + stdin
  modes, lang force, JSON output shape, real recipe render + lint.
- **`tests/test_graduation_activation.py`** (6 end-to-end tests):
  proves the Day-11 and Day-12 graduation gates go silent once the
  Day-13 writer has logged ≥ 3 matching requests, with counts
  matching either `requested` or `closest_existing` fields.

### Architecture decisions taken (Day 13 — per Jasem's approval during validation)

1. **Separate library + CLI** (`core/request_log.py` +
   `scripts/log_request.py`) — matches the Days 8–12 pattern.
2. **`route.py` auto-persists by default**; `--no-persist` opts out.
   Production contract is that log writes happen; tests explicitly
   override.
3. **`KATIB_MEMORY_DIR` env var** for memory path redirection — clean
   test isolation; no monkeypatching of module-level paths.
4. **Content-lint stays standalone** for Day 13 — not wired into
   `register` or `validate`. Avoids false-positive flood on existing
   intentional prose; Day 14 can optionally wire it as a warning-
   level check.
5. **Full CLI set** on `log_request.py` including `list` / `count` /
   `search`. Phase-4 reflect will shell out to these rather than
   reimplementing JSONL parsing.
6. **Schema locked at `schema_version: 1`** with `requested` +
   `closest_existing` both written on every entry. Any future field
   additions are purely additive with defaults.
7. **Day-11/12 readers unchanged.** Writer populates both match
   keys; readers already check either — symmetry proves the
   contract without touching Phase-2 code.

### Added (Day 12 — katib recipe CLI)

- **`scripts/recipe.py`** — dispatcher mirroring `scripts/component.py`
  with recipe-specific semantics. Six subcommands + `--json` global
  flag + identical error contract (`{action: "error", message, type}`
  in JSON mode; `ERROR: …` to stderr in human mode; exit 0/1/2).
  - `new <name> [--languages … --keywords … --target-pages lo,hi
    --page-limit N --domain-hint X --when "one-liner"]` — scaffolder
  - `validate <name>` — schema + component-ref + variant + lang +
    keywords + pages
  - `test <name> [--lang X,Y | --all-langs] [--brand Z]` — render to
    PDF in throwaway `dist/recipe-tests/<name>/`
  - `register <name>` — re-validate + regen `capabilities.yaml` + audit
  - `share <name>` — bundle to `dist/recipe-<name>-<version>.tar.gz`
  - `lint --all` — validate every recipe

- **`core/recipe_ops.py`** — library behind the CLI:
  - `scaffold_recipe()` — writes a sensible-default skeleton (cover-
    page + module + summary + whats-next) that renders cleanly out
    of the box. Audit entry.
  - `validate_recipe_full()` — schema + component-ref existence with
    `difflib.get_close_matches` fuzzy suggestions on typos + every
    declared recipe language supported by every referenced component
    + variant validity + `keywords` populated warning +
    `target_pages`/`page_limit` sanity.
  - `render_recipe()` — delegates to `compose()` + `render_to_pdf()`.
    Defaults to the fastest path (first declared language only);
    explicit `langs=[…]` param opts into the full matrix.
  - `register_recipe()` — validate → regen → audit chain.
  - `bundle_share_recipe()` — validate → tar.gz with YAML +
    `MANIFEST.json` listing referenced components.
  - `lint_all_recipes()` — iterates `recipes/*.yaml`.

- **`memory/recipe-audit.jsonl`** — seeded with 7 bootstrap entries
  (phase-1-trivial + 5 showcases + tutorial). Mirrors the Phase 1
  component bootstrap.

- **`scripts/build.py`** — `check_audit` extended to gate recipes too.
  Hand-added recipes without an audit entry now fail the startup check
  with a clean error pointing at `scripts/recipe.py new`. Bootstrap
  entries seeded in the same commit so no existing recipe gets caught
  by surprise.

- **Graduation gate (soft-pass)** — core-namespace recipe scaffolds
  check `memory/recipe-requests.jsonl` for ≥3 matching entries. Until
  Day 13 writes that log, emits a structured warning and permits
  scaffold. `--force --justification "<reason>"` is the audited
  override path; `--force` without `--justification` raises.

### Fixed (Day 12)

- **WeasyPrint warning elimination** — removed `unicode-bidi: isolate`
  from `components/sections/module/styles.css:137`. WeasyPrint 68
  doesn't support the property; it was emitting a single warning per
  rich-body render since Day 7 as a silent no-op. The `direction: ltr`
  on the same rule already handles the monolingual-LTR `<pre>` case.
  Engine is now truly zero-WeasyPrint-warning across every recipe.
  Surfaced by Day 12's `recipe test` command.

### Tests (Day 12)

- **`tests/test_recipe_ops.py`** — 28 unit tests. Scaffold happy + sad
  paths (existing name, bad kebab-case, bad lang, force-without-
  justification). Validator detects unknown component refs (with
  `difflib.get_close_matches` suggestions), bad variants, unsupported
  languages, missing keywords (warning), inverted `target_pages`. Full
  render round-trip proves the scaffold skeleton renders clean.
  Register refuses broken recipes; writes audit. Share validates
  first; includes manifest; excludes machine-local state.

- **`tests/test_recipe_cli.py`** — 20 subprocess tests. Every verb in
  both human and `--json` mode. Exit-code contract (0/1/2), stderr
  messages, parseable JSON on every exit path. `--target-pages 3,8`
  parsing. `--all-langs` flag exercised. JSON-contract regression
  guard (mirrors `test_route.py` and `test_component_cli.py`).

### End-to-end smoke test (Day 12)

Full lifecycle exercised live during development:
1. `recipe new smoke-recipe --languages en --keywords smoke,test` —
   YAML written, audit entry logged, graduation warning printed.
2. `recipe validate smoke-recipe` — 0 errors, 0 warnings.
3. `recipe test smoke-recipe` — rendered 9245-byte PDF; exposed the
   pre-existing `unicode-bidi` WP warning, fixed opportunistically.
4. `recipe test smoke-recipe` (re-run after fix) — clean, 0 warnings.
5. `recipe lint --all` — all 7 existing recipes pass with 0 errors,
   0 warnings.

345 tests pass (297 → 345, +48 for Day 12). Engine state: both
lifecycle CLIs are in place; Day 13 activates the graduation gates by
landing the request writers.

### Architecture decisions taken (Day 12 — per Jasem's approval during validation)

1. **Separate `memory/recipe-audit.jsonl`** (not unified with component
   audit) — clean mental model, ~4 lines added to `build.py` to gate
   both.
2. **`recipe test` defaults to first declared language** for fast
   authoring; `--all-langs` opts into the full matrix.
3. **Share bundle is YAML + `MANIFEST.json` only** — no transitive
   component bundling (shadcn-style). Phase 4's `--with-components`
   flag will handle deployable-bundle case.
4. **Scaffolder skeleton renders out of the box** — cover-page + module
   + summary + whats-next is immediately `test`-able.
5. **Validator ships 5 of 6 proposed checks.** `required_brand_fields`
   existence deferred to Phase 4 (needs brand registry).
6. **Graduation gate** wired identical to Day 11 — soft-pass reads
   `memory/recipe-requests.jsonl`; activates silently when Day 13's
   writer lands.

### Added (Day 11 — katib component CLI)

- **`scripts/component.py`** — unified dispatcher for the component
  authoring lifecycle. Six subcommands, one argparse tree, `--json`
  global flag for machine-parseable output:
  - `new <name> --tier <t> [--languages …] [--requires-tokens …]
    [--description …] [--force --justification …]` — scaffolder
  - `validate <name>` — full validation (9 ADR checks, 6 implemented
    now)
  - `test <name> [--lang …] [--variant …]` — isolated render harness
  - `register <name>` — re-validate + regen `capabilities.yaml` + audit
  - `share <name>` — produce `dist/<name>-<version>.tar.gz`
  - `lint --all` — validate every component across every tier

- **`core/component_ops.py`** — library module behind the CLI. Every
  function returns a structured result dict (no printing); the CLI
  formats for either human or JSON consumers.
  - `scaffold()` — writes `component.yaml` (schema-conformant),
    language-appropriate HTML stubs, README skeleton, test-input
    fixture stub. Writes `action: scaffold` audit entry.
  - `validate_full()` — schema + lang completeness + token hygiene
    (both HTML `{{ colors.X }}` refs and CSS `var(--X)` refs against
    `requires.tokens`) + brand hygiene + input parity + root-element
    a11y lang attribute + README section headers + test-fixture
    presence. Returns `ValidationResult` with severity-tagged issues.
  - `render_isolated()` — composes a synthetic single-section recipe
    on the fly, renders to PDF via WeasyPrint, counts logger warnings.
    Uses the component's test fixture file when present; auto-
    synthesizes placeholder inputs from the declared schema otherwise.
  - `register()` — chains `validate_full` (must pass) → regenerates
    `capabilities.yaml` → writes `action: register` audit entry.
  - `bundle_share()` — tar.gz bundle with a strict allowlist
    (component.yaml, HTML variants, styles.css, README, fixture). No
    audit, no capabilities, no goldens. Embeds a `MANIFEST.json`
    header.
  - `lint_all()` — iterates every component directory under every tier
    and returns a list of `ValidationResult` objects.

- **Graduation gate (soft-pass)** — core-namespace scaffolds check
  `memory/component-requests.jsonl` for ≥3 matching entries. Until
  Day 13 writes that log, the check emits a structured warning and
  permits scaffold. `--force --justification "<reason>"` is the audited
  override path; `--force` without `--justification` raises.

- **CLI error contract** — `--json` mode wraps every operational error
  in `{action: "error", message, type}`. Human mode prints `ERROR: …`
  to stderr. Never leaks a raw traceback (catch-all at
  `scripts/component.py:main`). Exit codes: `0` success, `1`
  operational error, `2` bad CLI usage.

### Tests (Day 11)

- **`tests/test_component_ops.py`** — 27 unit tests covering the
  library API. Scaffold happy path + sad path (existing name, bad
  kebab-case, bad tier, `--force` without justification, bilingual
  mode). Validator detects undeclared input, undeclared HTML token
  reference, missing lang HTML file, missing README, missing root-
  element `lang=`. Isolated render produces non-empty PDF with zero
  WeasyPrint warnings. Register refuses broken component; writes
  audit. Share excludes audit/capabilities; includes manifest.
  Lint-all covers every existing component.

- **`tests/test_component_cli.py`** — 19 subprocess tests covering
  every CLI verb in both human and `--json` mode. Exit-code contract
  (0/1/2), stderr message content, JSON-parseable stdout on every
  exit path (regression guard modeled on `test_route.py`). Verifies
  the full `new → validate → test → register → share` round-trip runs
  cleanly end-to-end.

### End-to-end smoke test (Day 11)

Full lifecycle exercised live during development:
1. `component new test-widget --tier primitive --languages en
   --requires-tokens accent` — 4 files written, audit entry logged,
   graduation warning printed (as designed for soft-pass mode).
2. `component validate test-widget` — 0 errors, 1 warning (declared
   `accent` token not yet referenced in the HTML stub — correct
   finding).
3. `component test test-widget` — rendered isolated PDF (3171 bytes,
   0 WeasyPrint warnings).
4. `component register test-widget` — capabilities.yaml regenerated,
   audit entry appended.
5. `component share test-widget` — `dist/test-widget-0.1.0.tar.gz`
   (992 bytes, 5 files including MANIFEST.json, no audit/capabilities).

### Architecture decisions taken (Day 11 — per Jasem's approval during validation)

1. **All 6 subcommands ship today** (not split across Days 11/12) —
   each is small once the dispatcher exists; Day 12 gets recipe CLI
   to itself.
2. **PNG goldens deferred to Phase 3.** `test` asserts clean PDF
   render (non-empty + zero WeasyPrint warnings). Avoids adding
   pdf2image/poppler as a hard dependency.
3. **Graduation gate soft-passes until Day 13's requests log
   exists.** The check is wired; activates silently when the log
   file appears (zero code churn at Day 13).
4. **Python-only entry point for Phase 2.** `bin/katib.js` (npx
   wrapper) stays install-focused. Public-facing CLI verb routing
   can land later once the verbs are stable.
5. **Validator at 6/9 ADR checks.** Schema, lang completeness, token
   hygiene (HTML+CSS), brand hygiene, input parity, a11y root lang
   attribute, README section headers, test fixture presence.
   Deferred: full HTML5 validity (html5lib dep), contrast check,
   page-break warning.
6. **Fixture + auto-synth fallback for `test`.** Authors provide
   realistic inputs at `tests/fixtures/components/<name>/test-inputs.yaml`;
   auto-synthesized placeholders generated from the declared schema
   when the fixture is missing.

All 9 flagged risks mitigated before shipping — the JSON-contract
regression guard (modeled on `route.py`'s) is the most important;
catches any exit path that ever emits non-JSON to stdout in `--json`
mode.

297 tests pass (251 → 297, +46 for Day 11). Zero WeasyPrint warnings.
Grep clean. Engine state: component authoring lifecycle is now
enforceable end-to-end; Day 12 is the parallel lifecycle for recipes.

### Added (Day 10 — /katib runner + SKILL.md rewrite)

- **`scripts/route.py`** — unified JSON-emitting CLI router. Two
  subcommands:
  - `infer` — reads transcript (via `--transcript-file` or
    `--transcript`), chains `context_sensor.infer_signals` →
    `gate.evaluate`, emits one of 5 action types as JSON:
    `render` / `present_candidates` / `ask_questions` /
    `ask_intent` / `error`.
  - `resolve` — consumes Q1/Q2 answer labels from the agent's
    `AskUserQuestion` call on a fired gate; emits final action
    (`render` / `wait` / `graduate`) plus the `log_entry` dict
    for Day 13's writer.
  - **Subprocess JSON contract**: every exit path emits exactly
    one valid JSON document on stdout. Exceptions wrapped at
    `main()` — raw tracebacks never leak to stdout (would break
    the agent's JSON parse).
  - **Stale capabilities auto-regen**: if any recipe or component
    source file is newer than the cached `capabilities.yaml`, the
    router regenerates it via subprocess before routing. Notes
    the regen in the response's `capability_notes` field.

- **`SKILL.md`** — full rewrite replacing the v2-dev placeholder. A
  thin interpreter on top of `route.py`:
  - 4 invocation modes (bare / prose / explicit / mixed)
  - Single dispatch loop with ASCII flow diagram
  - 5 per-branch pseudocode blocks (including concrete
    `AskUserQuestion(questions=response["questions"])` calls for
    `present_candidates` and `ask_questions`)
  - Non-negotiable rules (always show signals, no registry hand-
    edits, no path bypasses the log, explicit flags win)
  - Fresh-install sanity check
  - Troubleshooting table (audit gate, missing image input,
    Gemini key)
  - Explicit out-of-scope boundaries (no vault integration, no
    file navigation, no external skill dependencies)

### Tests (Day 10)

- **`tests/test_route.py`** — 19 tests:
  - All 5 action branches (`render`, `present_candidates`,
    `ask_questions`, `ask_intent`, `error`)
  - Explicit-override merge (lang/brand override inferred,
    recorded in `reasons[]`)
  - AUQ payload shape on both `present_candidates` and
    `ask_questions` (matches `AskUserQuestion` tool contract 1:1)
  - Parametrized Q1×Q2 matrix through `resolve` subcommand
  - Force-graduation requires non-empty justification
  - Subprocess JSON contract regression guard — asserts every
    invocation produces parseable JSON stdout (guards against
    any future exception leak)

### End-to-end smoke test (Day 10)

Manual smoke test passed during the commit:

    transcript → scripts/route.py infer → HIGH confidence → scripts/build.py
    → tutorial.en.pdf (111KB, Jasem Warm-Ember brand)

---


### Added (Day 9 — context sensor)

- **`core/context_sensor.py`** — session-context reader that extracts
  routing `Signals` from a plain-text transcript + filesystem brand
  state. Pure Python, deterministic, no LLM. Public API:
  - `infer_signals(transcript, *, known_brands=None, max_chars=4000)`
    → `ContextInference` (signals + summary + reasons +
    transcript_sample + log_entry draft for Day 13).
  - `enumerate_brands(user_dir=None, repo_dir=None)` — lists brand
    names from `$KATIB_BRANDS_DIR` / `~/.katib/brands/` + repo
    `brands/`; user dir dedups over repo.
  - `from_messages(messages: list[dict])` — joins role-tagged
    messages into a transcript string; caps at last 10.
  - `extract_intent` / `extract_brand` / `extract_lang_marker` —
    helpers exposed for testability.

- **Brand extraction with indicator-verb guard**: word-boundary match
  against enumerated brands, requires an indicator verb (`use`,
  `with`, `apply`, `for`, `in`, `as`, `brand`, `using`) within ±3
  tokens OR quoted/backtick context. Bare word mentions are rejected.
  Most-recent-position wins among multiple candidates; earlier
  candidate count reported in the reason.

- **Explicit language markers**: regex-based detection of `in
  Arabic/English`, `ar/en only`, and Arabic variants (`باللغة
  العربية`, `بالعربية`, `بالإنجليزية`, `بالإنكليزية`). Latest
  match wins. Explicit marker always overrides script inference;
  conflict is logged in `reasons`.

- **Observability + privacy**:
  - `transcript_sample` = first 200 + `...` + last 200 chars. Middle
    redacted.
  - `summary` is ONE sentence joined by `;` (not `.`) so runners can
    splice it into observability text without re-parsing.
  - `log_entry.schema_version: 1`; fields `{transcript_sample,
    transcript_length, inferred: {intent_preview (120 chars), brand,
    lang, lang_source}, known_brands}`.
  - Full intent text stays in-memory only; never written to log.

### Changed (Day 9)

- **`core/gate.py`**: promoted `_infer_lang` to public
  `infer_script(text, threshold=0.7)`. Back-compat alias preserved so
  internal callers don't churn.

### Risk mitigations (Day 9, 8 flagged risks)

- **Transcript format ambiguity** — plain-text contract documented;
  `from_messages()` adapter provided.
- **Intent recency heuristic** — `max_chars` kwarg bounds the extracted
  window (default 4000).
- **False brand matches** — indicator-verb proximity + quoting guard.
- **Signal staleness** — last-N-chars only for intent; `from_messages`
  keeps last 10 messages.
- **Marker-vs-script conflict** — explicit marker always wins; conflict
  explicitly logged.
- **Privacy** — transcript middle redacted in `log_entry`; full text
  never persisted.
- **Brand-dir caching** — `enumerate_brands` reads fresh every call; no
  caching.
- **Multi-candidate brand** — most-recent-by-position wins;
  earlier-candidate count reported.

---


### Added (Day 8 — decision gate + capabilities loader)

- **`core/capabilities.py`** — in-process loader for
  `capabilities.yaml` + deterministic keyword-based recipe ranker. No
  LLM. Returns `RecipeMatch` objects with `{name, score, reasons, data}`
  so callers can explain their routing decisions. Public API:
  `load_capabilities`, `rank_recipes(top_k=3)`, `find_closest_recipe`.
  Weights: 40% name-match, 30% keyword overlap, 20% when/description,
  10% section-shape hints — tunable via `weights` kwarg on
  `rank_recipes`.

- **`core/gate.py`** — self-contained three-question flow for
  LOW-confidence recipe routing, per ADR §Built-in decision gate. Pure
  Python, zero Claude-Code coupling beyond the `Question` dataclass
  shape (which matches the `AskUserQuestion` tool schema 1:1 so the
  Day 10 runner can pass-through via `question.to_ask_user_question()`).
  Three moving parts:
  - `score_confidence(signals, caps)` — 0–100 score + HIGH/MEDIUM/LOW
    verdict. Thresholds 90/50 per ADR. Topic 50 / brand 25 / lang 25.
    All sub-weights + thresholds tunable via kwargs.
  - `evaluate(signals, caps)` — routes to one of four outcomes:
    `proceed` (HIGH + `ResolvedPlan`), `choose` (MEDIUM + top-3
    candidates), `fire` (LOW + 2 questions: FIT + FREQUENCY),
    `needs-intent` (empty intent or zero recipe match).
  - `resolve(q1, q2, closest)` — computes Q3 action from the ADR's
    Q1×Q2 matrix. Emits log-entry drafts with `schema_version: 1` +
    v1-parity fields (`{ts, request, routed_to, reason}`) plus gate
    fields (`{recipe_closest, closest_score, fit, frequency, action,
    force_graduation_justification}`) for Day 13's
    `log_recipe_request`.

- **57 new tests** — 12 for capabilities (loading, tokenization,
  ranking edge cases, reasons array) + 45 for gate (confidence scoring,
  language inference, evaluate outcomes, AskUserQuestion payload shape,
  Q1×Q2 matrix parametrized, force_graduation flow, log schema, 7-row
  snapshot corpus).

### Risk mitigations (Day 8, documented for the gate)

Eleven mitigations applied across seven pre-flagged risks:

- **Margin guard** — HIGH requires top recipe score to beat #2 by
  ≥1.3×; tied rankings cap topic credit at moderate.
- **Belt-and-suspenders HIGH** — score ≥90 AND strong topic credit
  both required; future weight tweaks can't green-light weak-topic
  renders via brand+lang alone.
- **AskUserQuestion schema match** — field names, option shape (no
  `value` leakage), `header` ≤12 chars, 2–4 options, all verified
  against the live tool schema loaded via `ToolSearch`.
- **Label→value adapter** — `answer_to_value(question_id, label)`
  maps user-selected labels back to internal routing values
  (`yes-fits`, `partial`, etc.).
- **Log schema version** — `schema_version: 1` + v1-parity fields
  make Day 13's consumer contract explicit.
- **Strict language inference** — ≥70% script dominance required
  (configurable); mixed-script returns `lang=None`.
- **Mandatory justification** — `force_graduation=True` requires a
  non-empty `force_graduation_justification` string.
- **`needs-intent` outcome** — empty intent or zero recipe match
  skips the gate entirely and returns an instructional message.
- **Tunable kwargs** — `weights`, `thresholds`,
  `inference_threshold`, `topic_strong`, `topic_moderate`,
  `high_margin` all overridable.
- **Snapshot corpus** — 7 canonical `(intent, expected_top_recipe)`
  pairs catch ranking regressions.

---

### Added (Day 7 — tutorial.yaml production recipe)

- **`recipes/tutorial.yaml`** — full production port of the v1
  `framework-guide` output. Cover (minimalist-typographic, Jasem brand,
  logo on cover) + objectives-box + 8 modules with rich body content
  (3 inline SVG diagrams, 2 tables, 1 tip callout, 2 pull-quotes,
  1 ordered step list) + summary + whats-next + reference-strip. 7-page,
  111KB EN PDF. No lorem, no placeholder — shippable document.
- **`components/sections/module` 0.1.0 → 0.2.0**:
  - New `raw_body` input — Jinja `| safe`, opt-in for trusted
    recipe-authored HTML (tables, inline SVG, callouts, pull-quotes).
    Preserves the autoescape contract on the existing `body` input.
  - `.katib-module__body--rich` CSS for embedded `<table>` (with
    `thead`/`th`/`td` styling matching v1 conventions), `<pre>`,
    `<blockquote>` (with RTL-aware border-side), `<figure>` + `<svg>`
    + `<figcaption>`, and `<ol class="steps">`.

### Fixed (Day 7)

- **Jinja `getattr` override — dict-method fallthrough.** When a
  template accessed `input.<missing_key>` (e.g., the summary template's
  `{% if input.items %}` when a recipe supplied `body` only), the
  override was falling through to the dict's bound method — returning
  `dict.items` (truthy) instead of `Undefined`. The `{% for %}` then
  raised `'builtin_function_or_method' object is not iterable`. Fix:
  explicit `isinstance(obj, dict)` branch returns `env.undefined()` on
  `KeyError`, so missing keys evaluate falsy consistently.
- **`scripts/check_no_vault_refs.sh`** — tightened pattern from bare
  `vault` to path-like refs (`vault/`, `/vault`, `~vault`, `.obsidian`).
  The English word "vault" is legitimate in prose (e.g., "knowledge
  vault"); only path-style references indicate a v1-integration leak.

### Port

- **Jasem brand profile** (`~/.katib/brands/jasem.yaml`) — v1 → v2:
  `accent_secondary` renamed to `accent_2` (matches v2 base-token
  key). `identity_ar: {author_name: ...}` top-level dict collapsed
  into `identity.author_name_ar` sibling (matches v2
  `render_context()` bilingual fallback convention). Logo path
  unchanged.


---

### Added (Day 6 — chart sections)

- **`core/tokens.base.yaml`** — new top-level `charts:` block:
  - `palette` — 8-color hex array, mirrors accent + callout accents by
    convention. Brands override the whole array to restyle all charts
    in one sweep.
  - `axis_color`, `gridline_color` — chart chrome colors.
- **`core/image/inline_svg.py`** — extended:
  - `render_bar()` — horizontal bars, language-aware growth direction
    (EN: grow right from left axis; AR: grow left from right axis).
    Rejects negative values, all-zero data, empty data.
  - `render_sparkline()` — flat trendline. Always LTR (chronological
    data-vis convention, not a text convention). Handles single-point
    (dot), flat-line (mid-height), and negative values. Area fill +
    polyline stroke, both drawn from palette[0..1].
  - Removed hardcoded `DEFAULT_PALETTE` — provider is now strict and
    refuses to render without an explicit `colors` array in the spec.
    Forces `compose()` to be the single injection point.
- **`core/compose.py:_resolve_image_slots`** — when source is
  `inline-svg`, auto-injects `colors` + `lang` + `axis_color` from
  merged tokens before handing the spec to the provider. Resolved
  image dict now persists the original `spec` so templates can access
  `data` + `colors` for legend rendering + the sr-only data table.
- **3 new Tier-2 sections** (`components/sections/`):
  - `chart-donut` — proportional breakdown, legend to the side (or
    centered-stat variant). Accepts `sources_accepted: [inline-svg]`
    only.
  - `chart-bar` — horizontal bar chart, axis flips for AR.
  - `chart-sparkline` — trendline with optional headline stat + delta
    badge (`with-delta-badge` variant).
  - Each emits a visually-hidden `<table class="katib-sr-only">` data
    alternative with localized headers (EN: Category/Value, AR:
    الفئة/القيمة) alongside the SVG.
- **Recipe** — `phase-2-day6-showcase.yaml` exercises all three charts
  with realistic data (signal sources, revenue by channel, MAU growth).
- **Tests** — `tests/test_chart_sections.py` (27 tests): palette in
  tokens, schema source gate, renderer edge cases, RTL axis flip,
  sparkline LTR invariance, brand override precedence, sr-only table
  presence, end-to-end PDF.
- **Audit** — 3 new bootstrap entries in `memory/component-audit.jsonl`.

### Added (Day 5 — image-consuming sections)

- `components/sections/two-column-image-text/` — 3 variants (image-left,
  image-right, image-top). Accepts all four image sources: user-file,
  url, gemini, screenshot. RTL flips image-text order via flex-direction
  with `[lang="ar"]` override. Fallback to gemini if image missing.
- `components/sections/tutorial-step/` — numbered step with optional
  screenshot. Declares `sources_accepted: [screenshot, user-file]` for
  the screenshot input — deliberately excludes gemini because tutorial
  screenshots are factual, not illustrative.
- `recipes/phase-2-day5-showcase.yaml` — exercises both sections EN + AR
  with 4 embedded images (3 fixture images + 1 tutorial screenshot).

### Added (Day 4 — cover variants)

- `components/covers/cover-page/` bumps `0.1.0 → 0.2.0`:
  - `image-background` variant — full-bleed image + scrim + foreground.
  - `neural-cartography` variant — generative inline-SVG cover
    (continues to work without Gemini API key).
  - Variant branching via Jinja `{%- set is_image = ... %}` +
    `katib-cover--has-image` class modifier.

### Added (Day 3 — module + first cover)

- `components/sections/module/` — repeating body unit for
  tutorial/guide documents. Variants: `plain`, `workbook`.
- `components/covers/cover-page/` — first cover with
  `minimalist-typographic` variant. Establishes the cover tier
  in `components/covers/`.

### Added (Day 2 — scaffolding sections)

- Five Tier-2 sections land: `front-matter`, `objectives-box`,
  `summary`, `whats-next`, `reference-strip`. All compose primitives by
  CSS class name (primitive styles are always-loaded globally via
  `_load_primitive_styles()`); no Jinja include/macro layer needed.

### Added (Day 1 — image providers wired into compose)

- `_image_input_specs()` — extracts `type: image` inputs from
  `accepts.inputs` (handles both schema dict-forms).
- `_resolve_image_slots()` — routes each slot through `resolve_image()`
  with the component's `sources_accepted` gate enforced; replaces the
  raw spec with `{resolved_path, resolved_svg, content_hash, alt,
  source, spec}` in template context.
- Four providers online: `user-file`, `screenshot`, `gemini`,
  `inline-svg`. Fallback policy documented per component.

### Fixed

- Jinja `input.items` collision with `dict.items()` method — overrode
  `env.getattr` to prefer item-lookup for mapping access (Day 2).
- WeasyPrint 68 doesn't support `*-inline-*` logical properties —
  switched affected components to physical properties with
  `[lang="ar"]` overrides (Day 2).
- WeasyPrint 68 doesn't support `color-mix()` — switched to rgba()
  for the sparkline delta badge background (Day 6).
- Input name `description` collided with schema `inputDef.description`
  property — renamed `tutorial-step.description` → `body` (Day 5).
- Test assertions on class-name strings in HTML were false-positive on
  stylesheet selectors — moved to regex-extracted class attributes
  (Day 4).

### Changed

- `core/image/inline_svg.py` no longer holds any default palette.
  Provider fails loud if `colors` missing; `compose()` is the single
  injection point for token-driven colors (Day 6).
- Component tier directory layout now firmly three-way:
  `components/{primitives,sections,covers}/` (Day 3).

## v2 Phase 1 — Core engine + primitives (2026-04-23)

The render pipeline works end-to-end. A recipe YAML composes through an
8-primitive library to a WeasyPrint PDF at OS-standard `~/Documents/katib/`,
in EN or AR, with or without a brand override. Four image providers are
online (user-file, screenshot, gemini, inline-svg) with the sources-accepted
gate enforced and fail-loud on missing prerequisites.

### Added

- **Core engine** (`core/`):
  - `core/output.py` — two-level output resolver: `KATIB_OUTPUT_ROOT` env
    override → `platformdirs.user_documents_path() / "katib"`. Cache +
    user-config + user-components helpers.
  - `core/tokens.py` + `core/tokens.base.yaml` — three-layer token merge
    (base → brand → overrides), CSS-injection whitelist (ported from v1
    `brand.py`), per-language identity fallback for `name_ar` /
    `identity.<field>_ar` siblings, `tokens_css()` emits a single `:root`
    block with every color + font var.
  - `core/compose.py` — recipe YAML → HTML. Validates against schema,
    resolves components (core namespace only in Phase 1 — brand/user
    resolution arrives Phase 2), per-lang template selection, Jinja
    autoescape ON for input fields.
  - `core/render.py` — thin WeasyPrint wrapper.
  - `core/image/` provider layer — 4 providers with common `Provider`
    protocol and `ResolvedImage` dataclass:
    - `user_file.py` — local path + URL, copy-on-reference caching
    - `screenshot.py` — Playwright + Chromium at 2x density, content-hash
      cache (ported from v1 `shot.py`)
    - `gemini.py` — Gemini Nano Banana 2, fail-loud on missing
      `GEMINI_API_KEY` with actionable guidance, no silent placeholder
    - `inline_svg.py` — donut chart generator (bar + sparkline arrive
      Phase 2); deterministic output keyed on spec
- **Schemas** (`schemas/`):
  - `component.yaml.schema.json` — tier/version/namespace/languages
    (`en | ar | bilingual` enum), image inputs with `sources_accepted`
    whitelist, variants, page_behavior
  - `recipe.yaml.schema.json` — ordered sections, language mode, namespace
- **8 seed primitives** (`components/primitives/`):
  - `eyebrow`, `rule`, `tag`, `callout`, `step-circle`, `pull-quote`,
    `figure-with-caption`, `signature-block`
  - Each ships `component.yaml` + EN/AR Jinja templates + `styles.css` +
    `README.md`. All 8 validate against the component schema.
- **CLI entries** (`scripts/`):
  - `build.py` — `uv run scripts/build.py <recipe> --lang en [--brand <name>] [--slug <s>]`;
    runs a startup audit-presence check before rendering
  - `generate_capabilities.py` — auto-generates `capabilities.yaml` from
    components + recipes
  - `validate_component.py` — standalone schema validator (`katib component
    validate` lands Phase 2)
  - `check_no_vault_refs.sh` — CI grep check for vault/obsidian/soul-hub
    references outside `v1-reference/`
- **Audit bootstrap** (`memory/component-audit.jsonl`) — 8 seed entries for
  the Phase 1 primitives. Hand-added components without an audit entry fail
  the skill load.
- **Capability index** (`capabilities.yaml`) — auto-generated flat index
  (8 components, 1 recipe in Phase 1); agents read this before routing.
- **Brand profiles** (`brands/`) — `example.yaml`, `README.md`, and
  `fixtures/placeholder-logo.svg` ported from `v1-reference/brands/`.
  User brands stay at `~/.katib/brands/` (loader reads both paths).
- **Test suite** (`tests/`) — 61 pytest cases across 5 modules:
  - `test_output_routing.py` (6 tests) — env override, OS fallback,
    nested-folder creation
  - `test_tokens.py` (28 tests) — base/brand/override merge, bilingual
    fallback, CSS injection whitelist (11 parametrized cases)
  - `test_image_providers.py` (13 tests) — registry, happy paths, fail-loud
    paths, `sources_accepted` gate, deterministic cache keys
  - `test_compose.py` (12 tests) — schema gates, lang gates, brand override,
    Jinja auto-escape on inputs
  - `test_render_trivial.py` (4 tests) — end-to-end compose → PDF for EN
    and AR, invariants via `pypdf` text extraction
- **Smoke recipe** (`recipes/phase-1-trivial.yaml`) — exercises 7 of 8
  primitives (figure-with-caption joins once Day 5 providers wire into
  compose.py; Phase 2 work).

### Changed

- `pyproject.toml`:
  - Python floor `>=3.10` → `>=3.11`
  - Version `0.20.0` → `1.0.0-alpha.0`
  - Added `platformdirs`, `jsonschema` as hard deps
  - Added `[dependency-groups] dev` for pytest + Playwright + google-genai
  - Removed `[tool.katib]` section (v2 has no install-wide config defaults)
  - Added `[build-system]` + `[tool.hatch.build]` for a proper Python
    package layout
  - Added `[tool.pytest.ini_options]`
- Recipe / component pattern: moved from per-doc-type monolithic HTML
  templates with hardcoded content (v1) to component composition with
  Jinja partials + YAML recipes (v2). Templates and content are now in
  different files — the root-cause fix for the `framework-guide` incident.

### Phase 1 exit-criteria verification

- [x] Trivial recipe using primitives only renders in EN and AR
- [x] Default output lands in `~/Documents/katib/` (macOS) / platform
      equivalent; `KATIB_OUTPUT_ROOT` overrides for tests
- [x] `capabilities.yaml` generates from the current component set
      (8 components, 1 recipe)
- [x] Brand inheritance works (`example.yaml` tokens override base; tested
      end-to-end)
- [x] Golden-level invariants pass (text-extract diff; pixel-level goldens
      defer to Phase 2 when we have deterministic test fonts)
- [x] Grep clean for `vault | obsidian | soul-hub` outside `v1-reference/`
      (enforced by `scripts/check_no_vault_refs.sh`)
- [x] Gemini-missing-key path produces actionable error, no silent
      placeholder (covered in `test_image_providers.py`)
- [x] 61/61 tests pass; zero WeasyPrint warnings at render time

### Known limitations deferred past Phase 1

- Per-component CSS uses physical properties (`border-left` / `border-right`
  with `[lang="ar"]` overrides) instead of logical properties (`*-inline-*`)
  because WeasyPrint 68 does not support the logical shorthand forms.
  Confirmed via direct test; documented in component styles.
- Pixel-level golden images not shipped — Phase 2 ships when we commit to
  pinned test fonts.
- `figure-with-caption` authored but unwired in the smoke recipe; Phase 2
  wires image-provider resolution into `core/compose.py`.
- `core/fonts.py` (font installer) not ported from v1. Phase 1 relies on
  system fonts. Port-forward scheduled when we need deterministic
  cross-platform renders.

## [1.0.0-alpha.0] — 2026-04-23 — v2 architecture reset (Phase 0)

v1 (v0.1.0 → v0.20.0) hit an architectural limit surfaced by the
`framework-guide` incident on 2026-04-23: per-doc-type monolithic HTML
templates with hardcoded sample content cannot grow without template
corruption or doc-type entropy. v2 begins as a clean-canvas rebuild around
a component-first architecture with YAML recipes.

**This alpha release ships an empty repo root** — the intended state during
the v2 build-out. Functional code lands progressively across Phases 1–5.
Do **not** install from source off `main` during alpha. For v1 stable
(still fully functional), continue using `@jasemal/katib@0.20.0` from npm.

### Architecture direction (planned across v2 roadmap)

- **Components replace templates.** Three-tier model: primitives (atomic
  layout shapes), sections (composed units like `cover-page`, `module`),
  covers (variants like `minimalist-typographic`, `neural-cartography`).
- **YAML recipes replace doc-types.** A doc-type becomes an ordered list of
  components plus metadata (target pages, brand field requirements,
  language mode). No more per-doc-type HTML files.
- **Trilingual contract.** EN / AR / **bilingual** (third state) for
  side-by-side UAE contracts in a single PDF.
- **Vault integration removed.** Every install writes to
  `~/Documents/katib/` via `platformdirs`. Public install equals Jasem's
  install, byte-for-byte.
- **Self-contained skill.** No external skill dependencies. Decision gate,
  content lint, context sensor all ship inside `@jasemal/katib`.
- **Four image-source providers.** `user-file`, `screenshot`, `gemini`,
  `inline-svg` — components declare which sources they accept; recipes
  pick per invocation.
- **Component authoring workflow.** Five CLI subcommands
  (`katib component new | validate | test | register | share`). Hand-edits
  to the component registry fail the skill load.
- **Graduation flow enforced.** New components and recipes go through
  `log_request` → reflect clustering (≥ 3 requests) → scaffold.
  Enforcement lives in `build.py` startup checks, not just in SKILL.md
  prose.

### Phase 0 changes (this release)

- Tagged `v1-final` on v0.20.0 HEAD as the v1 archival marker.
- Moved v1 code into `v1-reference/` as a read-only reference:
  `SKILL.md`, `domains/`, `scripts/`, `references/`, `styles/`, `assets/`,
  `brands/`, `tests/`, `config.example.yaml`.
- Created `v1-reference/NOTES.md` documenting what worked, what broke
  (the `framework-guide` incident and its root cause), and what ports
  forward to v2.
- Seeded `memory/domain-requests.jsonl` with the retroactive
  `framework-guide` request as the first logged entry, turning a v1
  rule-bypass into the proof-of-concept data point for v2's enforced
  graduation flow.
- Reverted the v1-violating `framework-guide` doc-type drift from the
  installed skill at `~/.claude/skills/katib/`.
- Updated `SKILL.md`, `README.md`, `package.json` to signal v2 dev status.

### What still works

- `@jasemal/katib@0.20.0` on npm remains the stable v1 release.
  `npx @jasemal/katib@0 install` gets the last v1 tarball.
- v0.x tags continue to be accessible via git
  (`git checkout v0.20.0`).
- `v1-final` tag marks the archival point.

### What does not work (yet)

- Installing from `main` branch directly during Phases 0–4.
  `install.sh` at `main` will deploy the v2-dev stub skill with a
  read-only `v1-reference/` directory. Use npm instead.

### Reference

- v2 ADR: `~/vault/knowledge/adr-katib-v2-component-architecture.md`
  (R6, approved 2026-04-23)
- v1-reference notes: `v1-reference/NOTES.md`

---

## [0.20.0] — 2026-04-22 — Diagram catalog (13 types + editorial primitives)

Replaces the monolithic `references/diagrams.md` (278 lines, 5 patterns)
with a progressive-disclosure catalog of **13 diagram types**, **2 editorial
primitives**, and **5 reusable Jinja snippets**. Structure, complexity budget,
and anti-pattern taxonomy adapted from Cathryn Lavery's
[`diagram-design`](https://github.com/cathrynlavery/diagram-design) (MIT).

### Added

- **`references/diagrams/index.md`** — catalog entry point with philosophy
  (restraint + deletion), type selection guide, universal anti-patterns, and
  the complexity budget (max 9 nodes, max 12 arrows, max 2 accent elements,
  4px grid, per-type limits).
- **`references/diagrams/style.md`** — maps Katib's `colors.*` context to
  semantic roles (`accent`, `ink`, `paper`, `muted`, etc.) used across all
  type specs. Includes the node-type → treatment table (focal / backend /
  store / external / input / optional / security) and the accent-tint
  composition pattern.
- **`references/diagrams/primitives.md`** — shared SVG building blocks:
  arrow markers (default / accent / link), masked node box, arrow labels,
  legend strip, optional dotted-paper background.
- **`references/diagrams/rtl-notes.md`** — consolidates the bilingual /
  Arabic overlay pattern (`.diagram-stage` + `.diagram-label`), coordinate
  math, flow-direction mirroring rules, and the `build.py --check` lint.
- **13 type-specific references** — each 40–120 lines covering layout
  conventions, primitives, anti-patterns, and bilingual notes:
  `type-architecture.md`, `type-flowchart.md`, `type-sequence.md`,
  `type-state.md`, `type-er.md`, `type-timeline.md`, `type-swimlane.md`,
  `type-quadrant.md` (including the consultant 2×2 scenario variant),
  `type-nested.md`, `type-tree.md`, `type-layers.md`, `type-venn.md`,
  `type-pyramid.md`.
- **2 editorial primitives** — `primitive-annotation.md` (italic-serif
  marginalia callouts with dashed Bézier leader + landing dot) and
  `primitive-sketchy.md` (optional hand-drawn SVG displacement filter for
  essays / editorial-domain diagrams).
- **5 Jinja snippets** under `references/diagrams/snippets/` — ready to
  `{% include %}` inside diagram SVGs: `arrow-markers.svg.j2`,
  `node-box.svg.j2`, `annotation-callout.svg.j2`, `legend-strip.svg.j2`,
  `timeline-axis.svg.j2`. Each reads from `{{ colors.* }}` so the active
  brand applies automatically.

### Changed

- **`SKILL.md`** Step 5 tier table now points at
  `diagrams/index.md → diagrams/type-<name>.md` instead of the single file.
- **`scripts/build.py`** Arabic-in-SVG lint error message now references
  `references/diagrams/rtl-notes.md` (the new home of that rule).
- **`references/diagrams.md`** retained as a compat stub with quick-jump
  table to the new catalog — keeps older wikilinks from breaking.

### Philosophy

> "The highest-quality move is usually deletion."

Every node earns its place. Every connection carries information. `colors.accent`
is editorial, not a flag — 1–2 focal elements per diagram. Target density 4/10.
Above 9 nodes it's probably two diagrams.

### Attribution

Catalog taxonomy © 2024–2026 Cathryn Lavery,
[`diagram-design`](https://github.com/cathrynlavery/diagram-design) (MIT).
Katib-specific additions: Jinja color interpolation instead of CSS custom
properties (WeasyPrint can't resolve `var()` in SVG attributes), bilingual
EN + AR overlay patterns, per-domain font inheritance, per-type RTL notes,
compat stub for existing references.

## [0.19.0] — 2026-04-22 — Self-sustained Arabic quality (anti-slop + fact-integrity + content lint)

Prompted by a concrete failure: a rendered Arabic article in this session
included a fabricated Bruce Schneier quote and two untranslated English
abbreviations that Katib's `writing.ar.md` wouldn't have caught because the
catalog was a "condensed snapshot" pointing back at `/arabic`. This release
makes Katib self-sufficient for Arabic writing quality — no external skill
dependency, mandatory gates, and a mechanical linter for CI.

### Added
- **`scripts/content_lint.py`** — static catch for mechanical anti-slop
  violations. Auto-detects language from filename or character content.
  Catches banned openers (§1), emphasis crutches (§2), jargon inflation (§3),
  vague declaratives (§7), meta-commentary (§6c), untranslated English
  abbreviations, unqualified ambiguous tech terms (وكيل without الذكي),
  and واو-chain runaways (3+ conjunctions per sentence). Word-boundary-aware
  so "API" doesn't false-positive inside `GEMINI_API_KEY`. Output modes:
  default text, `--json` for tooling. Exit 1 on errors.
- **Fact-integrity section** in `references/writing.ar.md` — explicit rules
  against fabricated quotes, unverified stats, invented institutional
  attributions. Includes a verification-tiers table and a pre-commit grep
  protocol for blockquotes and numeric claims.
- **Quality-gate workflow** in `writing.ar.md` — four-sub-step protocol:
  pre-write (read doc-type rules), while writing (apply grammar + qualify
  terms + translate abbrevs + no fabrication), post-write 5-dimension
  score (threshold 35/50), fact-integrity sweep.
- **SKILL.md Step 6.5 · Quality gate** — new mandatory step in the render
  workflow. Explicit pointer to `writing.{lang}.md` as the complete contract
  for quality. Notes the automation via `content_lint.py`.

### Changed
- **`references/writing.ar.md` is now self-contained.** Previously a
  "condensed snapshot" that deferred to `/arabic`'s `anti-slop.md`,
  `brand-voice.md`, and `writing-examples.md`. Now contains the full
  8-section anti-slop catalog (throat-clearing openers, emphasis crutches,
  jargon inflation, structural anti-patterns with sub-rules, rhythm rules,
  trust-the-reader, vague declaratives, 5 full before/after examples)
  inlined verbatim from upstream. Size: 295 → ~680 lines.
- **"Translate abbreviations on first mention" rule clarified** — explicit
  list of common offenders (B2B, CEO, CTO, DevSecOps, MFA, 2FA, SSO, OAuth,
  PDPL, GDPR, SOC 2, CI/CD, MCP, etc.) to remove any "assumed well-known"
  loophole. Content lint's abbreviation list matches.

### Why
Concrete failures that prompted this:
- **Fabricated quote** — a blockquote attributed to "Bruce Schneier, RSA 2023"
  that was generated rather than sourced. Would have ended up in the user's
  vault under their byline. Caught only by the user's audit.
- **Untranslated B2B + DevSecOps** — rule #3 in core rules says "Translate
  every English abbreviation on first mention," but these slipped through
  because the author skipped the quality gate (the gate existed in upstream
  `/arabic` but Katib's version lacked the teeth to make it mandatory).
- **Condensed-snapshot dependency** — `writing.ar.md` pointed back at the
  upstream `/arabic` skill for the full catalog. That's a fine documentation
  pattern for small patterns but creates a drift risk: if someone renders
  Arabic without loading `/arabic` (which is Katib's stated mode of operation —
  "self-sustained"), the full rules aren't available.

All three are fixed by this release.

### Verification
- `content_lint.py` on the v0.18.2 walkthrough: 0 errors, 6 warnings (all
  واو-chain style suggestions — legitimate stylistic choices).
- `content_lint.py` on the better-auth article from this session:
  **2 errors caught** — exactly B2B and DevSecOps, as identified in the
  audit. This was the baseline test.
- `content_lint.py` on a synthetic slop sample: 4 errors + 2 warnings
  — every category fires correctly.

## [0.18.2] — 2026-04-22 — Fix stale rebuild paths + broken index wikilinks

Bug caught post-migration when reviewing the vault through Soul Hub's
note viewer — the migration left two classes of broken links that the
Phase 4 frontmatter-only audit missed.

### Fixed
- **`manifest.py` hardcoded the rebuild path as `~/vault/content/katib/...`**
  in every manifest body, ignoring project routing. New rendered
  manifests now derive the rebuild path from the folder's actual
  location (falls back to project-aware reconstruction when no folder
  is passed).
- **30 existing manifests** with stale rebuild paths rewritten via
  atomic temp-file-then-replace. Every `--project=<other>` render +
  every Phase-4 relocated folder was affected.
- **10 broken wikilinks in `content/index.md`** pointing at the old
  pre-migration `content/katib/...` paths. `repair_manifest_links.py`
  walked each one, located where the folder landed in the `projects/`
  tree, and repointed the link.

### Added
- **`scripts/repair_manifest_links.py`** — idempotent repair script.
  Scans every katib manifest, rewrites the rebuild block if it doesn't
  match the folder's current location, plus sweeps `content/index.md`
  for broken `[[content/katib/.../manifest]]` wikilinks. Dry-run
  default, `--execute` to write.

### Why this escaped the Phase 4 audit
`audit_vault.py` only validated frontmatter against the schema + zone
governance. The body (including the rebuild block) wasn't in scope.
The hardcoded path was technically frontmatter-independent — every
render wrote it, even before the migration. Phase 4 surfaced it
because relocating folders made the already-wrong path newly visible.

### Tests
- `test-all.sh`, `test-tutorial.sh`, `test-meta-validator.sh` all green
  with the new `manifest.py`. Fresh renders write the correct rebuild
  path derived from the output folder.
- Post-repair audit: 79/79 clean, repair script reports 0 candidates
  on a second run (idempotent).

## [0.18.1] — 2026-04-22 — Housekeeping (CI gate + fallback reconciler)

Two small utilities flagged as worth-having in ADR §22's retrospective.
No changes to render path or governance contract.

### Added
- **`audit_vault.py --summary`** — one-line counts (`total=N clean=N
  errors=N warnings=N fallbacks=N`) suitable for CI gates. Returns
  exit 1 if any manifest has an error; other output modes always
  return 0. Also adds `fallbacks` counter (manifests tagged
  `katib-fallback` from an API-unreachable render).
- **`scripts/reconcile_fallbacks.py`** — walks the vault for manifests
  tagged `katib-fallback`, re-POSTs each one through Soul Hub, strips
  the tag on success. Dry-run default, `--execute` to apply, `--yes`
  to skip the confirmation prompt (for CI). Forces `KATIB_VAULT_MODE=strict`
  internally so a second API failure fails loud instead of silently
  re-writing the same file.

### Why now
After Phase 5 closed the migration, two items remained in §22's
retrospective as "latent risk / nice-to-have":
1. No CI-friendly audit output — `--verbose` and `--json` are both
   too much for a pipeline gate; `--summary` is the missing primitive.
2. No reconciliation path for the `katib-fallback` tag — if Soul Hub
   is ever down during a batch render, fallbacks accumulate and
   nothing cleans them up automatically. The tag is visible in
   `audit_vault.py --json` output, but no tool acted on it.

## [0.18.0] — 2026-04-22 — Phase 5 of vault-integration migration (integration polish — migration complete)

Final phase of the vault-integration migration (ADR §20). No behaviour
change — all-docs, all-cleanup. Vault-first mode becomes the documented
default, test-harness wording gets modernised, the ADR closes out with
lessons learned. With v0.18.0, every one of the five phases is shipped,
tagged, and regression-covered.

### Added
- **`references/vault.md`** — new 10-section reference doc covering the
  vault-integration contract end-to-end: routing (`--project` behaviour),
  mode matrix (`KATIB_VAULT_MODE=api|strict|fs`), pre-render governance
  check, manifest contract, fallback semantics + `katib-fallback` tag,
  incident recovery (`recover_vault.py`), audit + migration tooling,
  exit-code contract, configuration, related files.
- **`SKILL.md` Step 8 — Vault integration** — concise routing + mode
  table for Claude Code users, pointer to `references/vault.md` for the
  full story.
- **`README.md` vault integration callout** — "Generated folders land in"
  section now shows the project-routing matrix; new paragraph explains
  `KATIB_VAULT_MODE` defaults.

### Changed
- **`references/output-structure.md`** — updated "Default output roots"
  table with project-routing matrix; added vault-mode note to
  "Destination modes (config)".
- **Test harness comments cleaned up.** `test-all.sh`, `test-tutorial.sh`,
  and `test-brand.sh` previously had "Phase 2 regression: pin render
  tests to fs mode" — reframed as "render harness defaults to fs mode,
  override with `KATIB_VAULT_MODE=api` in CI to exercise the full API
  write path." The `${KATIB_VAULT_MODE:-fs}` override pattern stays —
  that's the contract.

### Docs / infrastructure
- Skill + dev-repo `pyproject.toml` and `package.json` bumped to 0.18.0.
- **ADR §20 Phase 5 marked ✓ DONE** with an outcome paragraph recording
  two deviations from the original plan (kept `KATIB_VAULT_MODE` env var
  instead of adding `--vault-mode` CLI flag; named reference doc
  `vault.md` for naming-convention consistency).
- **ADR §22 added — "Vault integration complete — lessons learned"** —
  retrospective covering what worked (phase shape, env-var as three-way
  switch, graceful fallback with marker tag, pre-render check, atomic
  FS writes), what hurt (pyyaml date parsing, duplicate-content detector
  on rewrites, delete-before-write, hardcoded test paths), what would
  have saved time (`recover_vault.py` from day one, contract tests for
  the API client earlier, YAML coercion as default), and metrics at
  close (5 tagged releases, 11 regression harnesses, 79/79 clean, 1
  incident, 0 data lost).

### Tests
- All 11 regression harnesses green:
  `test-meta-validator` (11), `test-all` (6 renders), `test-tutorial`
  (10 renders + merge), `test-alt-bundles` (18), `test-brand` (70+),
  `test-images` (8 goldens), `test-feedback` (8), `test-add-domain`
  (11), `test-vault-client` (16), `test-strict-governance` (12),
  `test-migration` (11). `test-install-fonts` (live network, 8).
- Final vault audit: **79/79 clean, 0 errors, 0 warnings**.

### Migration closed
With this release, ADR §20's five-phase migration is complete. Katib is
a vault-API-first client — no more writing directly to disk without
governance validation, no more tag-pollution, no more silent failures
when the vault rejects a write. The API path is the default for every
render; graceful FS fallback with a `katib-fallback` marker tag covers
the "Soul Hub is temporarily down" case; `KATIB_VAULT_MODE=strict` is
available for CI; `KATIB_VAULT_MODE=fs` is available for offline render
tests. All five migration versions (v0.14.0 → v0.18.0) shipped with
their own test harnesses and committed independently.

## [0.17.0] — 2026-04-22 — Phase 4 of vault-integration migration (audit + migration + recovery)

Fourth of five phases (ADR §20). Retroactively cleans the 78 legacy
Katib manifests in the vault so they match the v0.14.0+ contract and
live in the right zone. Also ships an incident-recovery tool because
the first attempt at the migration shipped a date-serialisation bug
that orphaned 77 manifests — recovering them produced a dedicated
script that now guards against re-occurrence.

### Added
- **`scripts/audit_vault.py`** — read-only walker. Scans every Katib
  manifest under `content/katib/` and `projects/*/outputs/`, validates
  against meta_validator + zone governance, reports drift. Outputs:
  text summary (default), `--verbose` per-manifest breakdown, `--json`
  for tooling, or `--report` for a markdown note in `vault/knowledge/`.
- **`scripts/migrate_vault.py`** — proposes and (with `--execute`)
  applies fixes:
  - Rebuilds `tags` to the clean `[katib, <project>, auto-generated]`
    shape, stripping domain/doc_type/language pollution
  - Updates `katib_version` to current, `source_agent` to
    `katib-migration-v0.17.0`, preserves original as `source_agent_original`
  - Adds `migrated_at` audit stamp
  - Relocates folders where `project` ≠ `katib` but location is under
    `content/katib/` → `projects/<slug>/outputs/<domain>/<slug>/`
  - `--dry-run` is default; `--execute` requires typing `yes` (or `--yes`)
  - `--report` writes the plan as markdown to the vault
  - Writes via filesystem (not the API) — avoids date-serialisation and
    duplicate-content-detector issues that blocked the first attempt
- **`scripts/recover_vault.py`** — disaster-recovery tool. Finds
  folders with `.katib/run.json` but no `manifest.md`, reconstructs the
  manifest from surviving run-log + HTML source (extracts title from
  `<h1>` or `<title>`). Applies the v0.17.0 contract while rebuilding.
  Idempotent on a healthy vault. Saved the current vault after the
  migration incident (77 manifests rebuilt in one run).
- **`scripts/test-migration.sh`** — 11-assertion harness covering the
  full audit → dry-run → execute → re-audit flow on a scratch vault.
  Also exercises `recover_vault` against a simulated incident.

### Changed
- **`migrate_vault.execute_plan()` rewritten** after the incident.
  The first implementation POSTed to the API for the manifest write
  and deleted the old file before confirmation — a pyyaml-parsed
  `datetime.date` crashed `json.dumps` and left 77 manifests unreachable.
  New implementation:
  - Writes via FS using atomic temp-file + `Path.replace` (no
    delete-before-write)
  - Coerces all date/datetime scalars to ISO strings before emit
  - Uses the Katib-standard inline-list YAML writer for tag consistency
  - Idempotent: re-runs are safe
- **`vault/content/katib/`** — migrated: 58 manifests in-place rewritten,
  21 relocated to `projects/<slug>/outputs/`. Final audit: 79/79 clean,
  0 errors, 0 warnings.
- **`test-all.sh` and `test-tutorial.sh` path globs** updated to match
  Phase 2's project-routing. Tests now look at
  `projects/<slug>/outputs/<domain>/<today>-*/` instead of the legacy
  `content/katib/<domain>/2026-04-21-*/`. Use `nullglob` + date-aware
  glob construction so they survive future date changes.
- **8 duplicate legacy folders** cleaned up manually before migration:
  when Phase 2 test renders landed in `projects/<slug>/outputs/`, the
  pre-Phase-2 counterparts stayed in `content/katib/` as duplicates.
  Deleted those; nothing important lost.
- **4 manifests with `project: Test`** renamed to `project: test`
  before migration so the new zone follows kebab-case convention.

### Docs / infrastructure
- Skill + dev-repo `pyproject.toml` and `package.json` bumped to 0.17.0.
- ADR §20 Phase 4 marked ✓ DONE with a detailed outcome paragraph
  including the incident post-mortem.
- Two vault reports produced:
  `vault/knowledge/katib-audit-2026-04-22.md`,
  `vault/knowledge/katib-migration-plan-2026-04-22.md`.

### Tests
- `test-migration.sh`: 11/11 pass (audit → dry-run → execute →
  re-audit → recovery idempotent → recovery-after-incident).
- Regression: all 10 prior harnesses green — `test-meta-validator` (11),
  `test-all` (fixed globs, 6 renders), `test-tutorial` (fixed globs,
  10 renders + merge), `test-alt-bundles` (18), `test-brand` (70+
  assertions), `test-images` (8 goldens), `test-feedback` (8),
  `test-add-domain` (11), `test-vault-client` (16),
  `test-strict-governance` (12). `test-install-fonts` (live network, 8).
- Post-migration vault audit: **79/79 clean, 0 errors, 0 warnings**.

### Incident post-mortem (see `migrate_vault.execute_plan()` docstring)
The first run of `--execute` on the live vault failed catastrophically
on two separate issues:

1. **pyyaml date parsing**: `created: 2026-04-21` came back as
   `datetime.date` which `json.dumps` cannot serialise. The manifest
   POST body threw, but the script had already deleted the old
   manifest to make room for the POST — leaving 77 folders with no
   `manifest.md`.
2. **Soul Hub duplicate-content detector**: even for manifests that
   parsed, 5 rewrite-in-place writes tripped the 90% similarity
   check because proposal/letter/one-pager of the same deliverable
   share boilerplate.

`recover_vault.py` reconstructed all 77 from `.katib/run.json` +
HTML source in ~1 second. `migrate_vault.py` was then rewritten to
(a) coerce dates to strings, (b) write via FS instead of API, and
(c) use atomic temp-file-then-replace instead of delete-then-write.

## [0.16.0] — 2026-04-22 — Phase 3 of vault-integration migration

Third of five phases (ADR §20). Adds **pre-render governance checking**:
Katib fetches the target zone's governance via a new Soul Hub endpoint
(`GET /api/vault/zones/<path>`) and validates the proposed manifest against
it *before* starting the expensive PDF render. If the zone would reject
the write, the build fails fast with a readable error. No more rendering
12 pages of PDF only to discover the target zone disallows `type: output`.

### Added
- **`GET /api/vault/zones/<path>`** (Soul Hub) — new read-only endpoint
  returning `{zone, resolvedFrom, allowedTypes, requiredFields, namingPattern, requireTemplate}`
  for any zone path, resolving the governance hierarchy walk automatically.
  Wraps the existing `GovernanceResolver.resolve()` (previously private).
  Path validation mirrors the `POST /api/vault/notes` handler (no `..`, no
  null bytes, regex allow-list). Implemented via a new public
  `VaultEngine.resolveZone()` method.
- **`vault_client.get_zone_governance(zone)`** — Python client. Returns
  a `ZoneGovernance` dict (camelCase + snake_case accessors) with a 60s
  in-memory cache (keyed on zone + base URL). Graceful fallback: network
  failures, 404 (old Soul Hub), or non-JSON responses all return None with
  a stderr warning — pre-check is advisory, not load-bearing.
- **`vault_client.validate_against_zone_governance()`** — runs a proposed
  `(meta, filename)` against the fetched governance dict. Mirrors the
  server's `createNote()` validation so whatever passes locally passes
  the POST. Returns a list of violation strings.
- **`ZonePreCheckError` exception** + **`clear_zone_cache()` helper** for
  test harnesses.
- **`build.py --strict-governance` / `--no-strict-governance` CLI flags**
  — default: on when `KATIB_VAULT_MODE` is `api`/`strict`, off for `fs`.
  The check fires *before* cover generation + HTML render, so a bad zone
  aborts the build in ~50ms instead of after the full render pipeline.
  Empty slug_dir cleanup on pre-check failure so the vault stays tidy.
- **`scripts/test-strict-governance.sh`** — 12-step harness covering
  import + exports, fs-mode short-circuit, network failure graceful
  degrade, violation detection (type, required fields, naming pattern),
  cache behaviour (measured 1100× speedup), CLI flag gating, and two
  live-API assertions against the running Soul Hub.

### Changed
- **`render_template()`** signature gains `strict_governance: bool | None`.
  When the target slug_dir lives under the vault root and a non-fs mode is
  active, it fetches zone governance and validates. `ZonePreCheckError` is
  caught at the CLI top level and maps to exit 4 — same code as governance
  rejections from Phase 2, so callers see uniform behaviour.
- **`test-brand.sh` — `--project` values simplified** from
  `katib-shadow-test`, `katib-brand-smoke`, etc. to plain `katib`. Phase 2's
  routing change meant those `katib-*` slugs landed in
  `projects/<slug>/outputs/` but the shell script's hardcoded file-checks
  still looked in `content/katib/`. Using `--project katib` + unique
  `--slug` values keeps test output in the legacy path the script expects.
  Purely a test-side fix — no production behaviour change.

### Docs / infrastructure
- Skill + dev-repo `pyproject.toml` and `package.json` bumped to 0.16.0.
- ADR §20 Phase 3 marked ✓ DONE with outcome paragraph.
- Soul Hub's governance scan runs at init; zone CLAUDE.md changes take
  effect after a server restart (or an out-of-band zone creation that
  triggers `governance.scan()` as a side effect — see index.ts:743).

### Tests
- `test-strict-governance.sh`: 12/12 pass (10 offline + 2 live-API).
- Regression: all 10 prior harnesses green — `test-meta-validator` (11),
  `test-all` (6 renders), `test-tutorial` (10 + merge), `test-alt-bundles`
  (18), `test-brand` (fixed + 70+ assertions across 5 steps),
  `test-images` (8 goldens), `test-feedback` (8), `test-add-domain` (11),
  `test-vault-client` (16). `test-install-fonts` (live network, 8).

## [0.15.0] — 2026-04-22 — Phase 2 of vault-integration migration

Second of five phases (ADR §20). Wires Katib's first-writes through Soul Hub's
`POST /api/vault/notes` endpoint — the governance gate — with an FS fallback
when the API is unreachable. Also introduces project-scoped output routing:
`--project <slug>` (for any slug other than `katib`) now lands outputs in
`projects/<slug>/outputs/` instead of `content/katib/`. Closes category (A)
governance-bypass and category (B) zone-misrouting from the breach audit.

### Added
- **`scripts/vault_client.py` (~320 lines)** — HTTP client for Soul Hub's
  `POST /api/vault/notes`. Uses stdlib urllib only (no new deps). Three modes
  selectable via `KATIB_VAULT_MODE`:
  - `api` (default): prefer API, fall back to FS with `katib-fallback` tag
  - `strict`: API only, raise `VaultNetworkError` on any connection failure
  - `fs`: skip API entirely (legacy path, used by regression harnesses)

  Exceptions: `VaultGovernanceError` (4xx reject — caller must fix metadata),
  `VaultConflictError` (409 duplicate path or content), `VaultNetworkError`
  (connection refused / timeout), `VaultWriteResult` dataclass reports the
  backend taken (`api`, `fallback`, `fs`).
- **`config.py — resolve_vault_root()`** — derives the Obsidian vault root
  from `output.vault_path` (convention: `<root>/content/katib`). Overridable
  via `KATIB_VAULT_ROOT` env var or `cfg.output.vault_root`.
- **`config.py — resolve_project_outputs_root()`** — new routing helper.
  `project=katib` → legacy `content/katib/` tree; `project=<other>` →
  `<vault>/projects/<slug>/outputs/`. Governed by `projects/CLAUDE.md`
  (inherits the `output` type + `type, created, tags, project` requirements
  that Phase 1's validator already enforces locally).
- **`scripts/test-vault-client.sh`** — 16-step harness covering: import +
  public API, FS fallback path + `katib-fallback` tag injection, strict-mode
  network failure, fs-mode skip-API, zone/filename derivation, project
  routing (katib vs. other), fs-mode build.py smoke, and two live-API
  assertions against Soul Hub (happy path + governance reject).

### Changed
- **`manifest.py — write_manifest(..., vault_root=Path)`** — first-writes
  route through `vault_client.create_note()` when `vault_root` is supplied
  and the folder lives under it. Updates (second-language render merging
  into an existing manifest) stay on FS; `katib-fallback` tag is preserved
  through the merge so the reconcile job (Phase 4) can still find them.
  PUT-based governed updates deferred to Phase 5.
- **`build.py — render_template()`** — `--project` CLI flag now drives
  real output routing, not just a metadata field. Default (`katib`) keeps
  the legacy `content/katib/` path; other values route to
  `projects/<slug>/outputs/`. Also wires `vault_root` through to
  `write_manifest` for the governance gate.
- **Regression harnesses pinned to `KATIB_VAULT_MODE=fs`** — `test-all.sh`,
  `test-tutorial.sh`, `test-brand.sh`. Keeps render tests offline-friendly
  and avoids Soul Hub's duplicate-content detector flagging repeat runs.
  `test-vault-client.sh` is the one harness that exercises the live API.
- **`vault/content/katib/CLAUDE.md — Allowed Types` rewritten** from
  markdown prose (`` `output` (every manifest), `index` (zone index) ``)
  to clean bullets (`- output` / `- index`). The governance parser
  splits on commas and couldn't extract type names from the decorated
  form, so previously the zone's allowed-types list parsed as garbage
  and the API blocked all Katib writes.

### Docs / infrastructure
- Skill + dev-repo `pyproject.toml` and `package.json` bumped to 0.15.0.
- ADR §20 Phase 2 marked ✓ DONE with outcome paragraph.

### Tests
- `test-vault-client.sh`: 16/16 pass.
- Regression: all 9 existing harnesses green — `test-meta-validator` (11),
  `test-all` (business-proposal 6 renders), `test-tutorial` (10 renders +
  manifest merge), `test-alt-bundles` (18), `test-brand` (14),
  `test-images` (8 goldens), `test-feedback` (8), `test-add-domain` (11),
  `test-install-fonts` (live-network, 8).

## [0.14.0] — 2026-04-22 — Phase 1 of vault-integration migration

First of five phases (ADR §20) to bring Katib's vault writes into line with the Soul Hub vault engine's governance. This phase is **schema-only** — no network calls, no routing changes, fully reversible. Builds the metadata contract that Phase 2 will post to `/api/vault/notes`. Closes all of category (C) from the breach audit (metadata drift) and the `auto-generated` tag portion of (A).

### Added
- **`scripts/meta_validator.py` (295 lines)** — schema gate that mirrors the vault engine's governance exactly. Encodes `GLOBAL_REQUIRED_FIELDS`, `MAX_NOTE_SIZE`, content/katib/projects/knowledge zone allowed-types + required-fields. Validates a proposed frontmatter dict against a target zone and returns a list of `SchemaViolation` objects (error or warn). Catches: global missing fields, zone-specific missing fields, disallowed types, missing `katib` tag, missing `auto-generated` tag, tag pollution (domain/doc_type/lang in tags when those are already structured fields), project-path mismatch, size over 1 MB.
  - CLI: `--manifest <path>` (validates an on-disk manifest.md, infers zone from path), `--describe-schema` (dumps full schema as JSON).
  - Python API: `from meta_validator import validate; violations = validate(meta, zone=...)`.
  - Drift prevention note: kept in lockstep with `soul-hub/src/lib/vault/types.ts` and `vault/*/CLAUDE.md` so Phase 2 API writes don't hit surprises.
- **`scripts/test-meta-validator.sh`** — 11-step harness covering every violation path plus an integration check that live `manifest.py` output validates clean for both `content/katib/tutorial` and `projects/<slug>/outputs`.
- **`--agent` CLI flag** on `build.py` — explicit `source_agent` override for write audit log. Precedence: `--agent` → `$KATIB_AGENT_ID` → default `katib-cli`. Previously hardcoded `claude-opus-4-7` which poisoned the write log.
- **`source_context` frontmatter field** — 8-char BLAKE2s hash of the slug directory name. Stable across EN/AR co-located renders (both use the same folder). Traces each manifest back to a specific Katib run.

### Changed
- **`manifest.py` — `katib_version` auto-read from `pyproject.toml`** via `importlib.metadata.version("katib")`, with fallback to parsing `pyproject.toml` directly for dev installs. Previously hardcoded `"0.1.0"` at module scope and drifted 13 versions. Both `manifest.md` frontmatter and `.katib/run.json` now carry the correct version.
- **`manifest.py` — tag builder rewritten.** New shape: `["katib", <project>, "auto-generated"]`. Prunes `domain`, `doc_type`, `languages` from tags (those are already structured fields; tagging them polluted the vault's tag taxonomy and collided with project tags like `personal`). `auto-generated` is pre-added to match the auto-tag the vault engine applies when `source_agent` is present — keeps tag shape stable across FS and API writes.
- **`manifest.py` — `source_agent` default changed** from literal `"claude-opus-4-7"` to the env-resolved `katib-cli`. Both `manifest.md` and `.katib/run.json` use the new `_resolve_source_agent()` helper.
- **`manifest.py` — `source_context` field threaded through** both `build_frontmatter()` and `write_run_json()`.
- **`build.py`** — `render_template()` signature gains `agent` and `source_context`; generates the BLAKE2s run-id when caller doesn't supply one.
- **Skill's `pyproject.toml`** — bumped to 0.14.0 (was stale at 0.1.0 from before v0.2.0 due to the install script not syncing it). Needed for `importlib.metadata.version()` to return a truthful number in dev mode.

### Tests
- `test-meta-validator.sh`: 11/11 pass.
- Regression: all 9 existing harnesses green — `test-ar-svg` (8), `test-add-domain` (11), `test-feedback` (8), `test-install-fonts` (8), `test-all` (business-proposal 6 renders), `test-tutorial` (tutorial 10 renders + manifest merge), `test-brand` (14), `test-alt-bundles` (18).

### Philosophy
- Phase 1 is explicitly schema-first. No network, no routing change, no user-visible behaviour change except the cleaner frontmatter. This is the foundation Phase 2 depends on: once validator and engine schemas agree, Phase 2's API POST is just plumbing. Drift detection is the point — if either side changes without the other, the validator will start rejecting manifests and we'll catch it before the API does in Phase 2.

### What's next (ADR §20)
- **Phase 2 (v0.15.0)** — `scripts/vault_client.py` + `manifest.py` POST to `/api/vault/notes`, with FS fallback. `--project <slug>` routing to `projects/<slug>/outputs/`.
- **Phase 3 (v0.16.0)** — Zone governance learning (pre-render fetch of `CLAUDE.md` rules).
- **Phase 4 (v0.17.0)** — `audit_vault.py` + `migrate_vault.py` (one-shot, dry-run default).
- **Phase 5 (v0.18.0)** — Integration polish; vault-first mode becomes default.

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
