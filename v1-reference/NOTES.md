# Katib v1 — Reference Archive

This directory preserves the Katib v1 architecture (v0.1.0 → v0.20.0, built
2026-04-21 → 2026-04-22) as a **read-only reference** while v2 is developed
at the repository root.

> **Do not edit files in this directory.** CI enforces this.
> Read it when you need to recall how v1 handled a specific problem, port a
> pattern forward, or understand why a v2 decision was made. Port changes
> into the v2 files at the repo root; never modify the archived v1 here.

---

## What v1 was

A bilingual (EN + AR) print-grade PDF generation skill for Claude Code:

- **10 domains** (business-proposal, tutorial, report, formal, personal,
  academic, financial, editorial, marketing-print, legal)
- **~40 doc-types** across the domains, each with its own monolithic HTML
  template plus per-language variant (`.en.html`, `.ar.html`)
- **Brand profile system** (jasem, triden, tridenits, example) overriding
  domain tokens at render time
- **Inline SVG diagrams** with brand-color interpolation via Jinja
- **Self-improvement loop** — `reflect.py` + `feedback.py` + `add_domain.py`
  with a three-stage graduation path (log → cluster → scaffold)
- **Vault integration** (v0.14.0–v0.18.0, five phases) — writes PDFs into
  Jasem's Obsidian-based Soul Hub vault with zone-governance pre-checks,
  manifest emission, and fallback reconciliation
- **WeasyPrint + Jinja** pipeline
- **UAE VAT invoice compliance** rules embedded in the `financial/invoice`
  template
- **Gemini Nano Banana 2** cover-image generation (`cover.py`, ~$0.12/image)
- **Playwright-based screenshots** (`shot.py`) for the tutorial domain
- **Font installer** (`install_fonts.py`) for the 7 OFL fonts v1 depended on

342 renders logged in `memory/` during the 30-day v1 lifespan. First public
release (v0.1.2) shipped 2026-04-22 at
[github.com/jneaimi/katib](https://github.com/jneaimi/katib) and
[`@jasemal/katib`](https://www.npmjs.com/package/@jasemal/katib) on npm.

---

## What worked and must survive into v2

1. **WeasyPrint + Jinja** is the right rendering pipeline. No reason to
   switch engines. v2 keeps it.
2. **Inline SVG with brand-color interpolation via `{{ colors.X }}`** —
   crisp vector output, brand-aware, zero external tooling. v2 keeps and
   extends this pattern.
3. **Twin-file bilingual model** — separate `<doc>.en.html` and
   `<doc>.ar.html` files beat `{% if lang == "ar" %}` conditionals for
   clarity, linting, and typography tuning. v2 keeps this for monolingual
   components and adds a third peer `<component>.bilingual.html` for
   side-by-side UAE contracts.
4. **Brand profiles as YAML data** — `jasem.yaml`, `triden.yaml`, etc., with
   colors/fonts/identity fields. Clean separation of brand from structure.
   v2 keeps this schema largely unchanged.
5. **Arabic HTML-overlay pattern for SVG labels** — WeasyPrint can't shape
   Arabic inside SVG `<text>`, so v1 positions HTML labels absolutely on top
   of SVG geometry. Hard-won learning. v2 keeps it.
6. **UAE VAT tax-invoice field requirements** — Federal Decree-Law No. 8 of
   2017 compliance (TRN, invoice number, supply date, separate VAT line,
   amount-in-words, etc.). Domain knowledge that must port forward.
7. **Self-improvement loop** (reflect / feedback / graduation). v2 keeps the
   pattern but generalises it from doc-types to components + recipes.
8. **`shot.py` screenshot caching** — content-hashing of URL + viewport +
   hide rules to skip Playwright when inputs match. Ported forward as the
   `screenshot` image provider in v2.
9. **Install-time font fetching** via `install_fonts.py` — 7 OFL fonts
   downloaded from Google Fonts GitHub mirrors, cached in `~/.katib/fonts/`.
   v2 reuses this.
10. **Quality gate** — the anti-slop checklist in `references/writing.en.md`
    and `writing.ar.md`, plus `content_lint.py` static checks. v2 ports
    these unchanged.

---

## What broke and informed v2

### The `framework-guide` incident (2026-04-23)

**What happened:** An agent (Claude) was asked to author an educational
document about Bloom's AI Collaboration framework using Jasem's brand, with
a cover and three diagrams. The correct routing per v1's rules was
`tutorial/tutorial` (multi-module, 5–15 pages). Instead, the agent added a
new doc-type `framework-guide` by hand-editing `domains/tutorial/styles.json`
and creating `domains/tutorial/templates/framework-guide.en.html` with the
body content baked into the template.

**Why it happened:** The agent did not ignore v1's `log_domain_request` rule.
v1's architecture offered no clean path to inject custom content into the
existing `tutorial.en.html` template without either corrupting the shared
template file (polluting the skill) or creating a new doc-type. The hardcoded
sample content in the template ("Install the tool", "Create your first item")
was designed to be *replaced* per project, but v1 provided no mechanism to do
that without forking the template.

**Root cause:** **Templates and content were the same file.** Every
customisation either corrupted the shared template or added a new doc-type.
Over time, both paths accumulate entropy. v1 reflect already showed the
symptom — 32 `unused-doc-type` flags in a 30-day window, with `academic/*`
and `report/*` fully unused.

**Compounding factor:** v1 had the right graduation flow in principle
(`log_domain_request` → reflect cluster → `add_domain.py` scaffold) but zero
enforcement. The `domain-requests.jsonl` log file had zero entries in 342
renders. The rule existed in prose in SKILL.md and was stated three times,
but no code path required it. Agents (and humans) could hand-edit
`styles.json` and the build would succeed.

**What v2 does differently:**
1. Templates and content fully separated. Components are Jinja partials with
   Jinja-declared input slots; content flows through via recipe YAML.
2. `build.py` at startup verifies every component and recipe has a matching
   audit-log entry. Hand-added files fail the startup check with a pointer
   to the scaffolder.
3. Doc-types replaced by recipes (YAML files). Adding a new recipe is a
   guided CLI operation (`katib recipe new`) with validator + tests.
4. Graduation is enforced, not advisory.

### Vault integration scope creep (v0.14.0 – v0.18.0)

**What happened:** Five phases of development wired Katib outputs into the
Obsidian vault with zone governance, manifest emission, API-first writing,
and a fallback reconciler. ~15 commits, significant surface area.

**Why it happened (in hindsight):** v1 was trying to solve "where do my
PDFs go and how do I find them later" at the Katib layer. That concern
belongs at a different layer — file navigation is infrastructure, not a
per-tool responsibility. `/media`, `/research`, `/diagram`, screenshots,
manual downloads all have the same problem; solving it for Katib only is
the wrong abstraction.

**Root cause:** Scope creep. Generation and navigation got conflated.

**What v2 does differently:**
1. No vault integration at all. PDFs write to OS-standard
   `~/Documents/katib/` via `platformdirs`. Same on every install.
2. File navigation becomes a Soul Hub responsibility (separate sibling ADR).
3. Public install = Jasem's install. Zero conditional paths.

### Template + sample content coupling

See framework-guide incident above — the generic symptom beyond one agent
incident. Every v1 template bundled a "starter example" of body content
inline, forcing users to either (a) edit the shared template and pollute it,
(b) add a new doc-type for trivial variations, or (c) manually rewrite the
rendered HTML output after the fact. Option (b) caused the `framework-guide`
incident; option (c) was never documented; option (a) was tempting under
time pressure.

**What v2 does differently:** Templates ship as **empty composable
components**. Body content flows in through recipe YAML + component input
slots. Sample content lives in separate `fixtures/` files used only by the
test harness — never shipped as the template itself.

### Governance without enforcement

Stated three times in SKILL.md, implemented as a Python function
(`log_domain_request`), surfaced via `reflect.py` as
`new-domain-candidate` proposals, and wired to a scaffolder
(`add_domain.py`). Every piece worked individually. Nothing enforced the
chain. Across 342 renders and the existence of many "this doesn't quite
fit" moments, zero `domain-requests.jsonl` entries were ever logged.

**What v2 does differently:** enforcement moves into `build.py` startup
checks that fail the skill load on unregistered components or recipes.
Prose rules remain in SKILL.md but they document what the code already
enforces, rather than asking agents to self-police.

---

## What to reach into this archive for (mostly)

- **Specific HTML patterns** that already work (cover-page CSS, signature
  block layout, page-break rules for bilingual signature pages, etc.). These
  port forward as components in v2.
- **Arabic typography tuning** in v1 templates — line-height, letter-spacing,
  RTL padding rules. Distilled into v2 component styles.
- **SVG diagram patterns** in `v1-reference/references/diagrams/` — 13 types
  catalogued. Become v2 chart + diagram components.
- **UAE VAT invoice structure** in `v1-reference/domains/financial/templates/`.
  Ports to the `uae-vat-invoice` recipe in v2 Phase 3.
- **Brand profile YAMLs** in `v1-reference/brands/`. Data, unchanged. Copied
  to root `brands/` in v2 Phase 1.
- **Font installer** in `v1-reference/scripts/install_fonts.py`. Logic ports
  unchanged.

---

## What to leave in this archive forever

- **Monolithic per-doc-type HTML templates** (`v1-reference/domains/*/templates/*.html`).
  Replaced by component composition. Do not port forward as templates.
- **`styles.json` doc-type matrix** (`v1-reference/domains/*/styles.json`).
  Replaced by recipe YAMLs. Do not port forward.
- **Vault integration code** (`v1-reference/scripts/vault_client.py`,
  `audit_vault.py`, `migrate_vault.py`, `recover_vault.py`,
  `reconcile_fallbacks.py`). v2 has no vault integration.
- **`add_domain.py`** — superseded by `katib recipe new`.
- **`log_domain_request` function** as invoked in v1 — superseded by
  `log_request.py` handling both recipe and component requests.

---

## Related documentation

- **v2 architecture:** `~/vault/knowledge/adr-katib-v2-component-architecture.md`
- **v1 original ADR:** `~/vault/knowledge/adr-katib-document-generation-skill.md`
  (superseded)
- **Git tag:** `v1-final` marks the last commit before this archival.
- **npm:** `@jasemal/katib@0.20.0` remains available as the stable v1 release.
  v1.0.0 (v2) will promote to `latest` when it ships.

---

**Read-only. Do not modify. Port lessons forward by implementing them in
the v2 files at the repository root.**
