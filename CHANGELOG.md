# Changelog

All notable changes to Katib are documented here. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

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
