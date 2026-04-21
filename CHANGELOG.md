# Changelog

All notable changes to Katib are documented here. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

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
