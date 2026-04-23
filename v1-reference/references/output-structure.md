# Katib — Output Structure & Vault Integration

Every generation produces a single self-contained folder under the configured
output root. The folder IS the atomic unit — artifact, manifest, source,
metadata, and assets all live together for trivial re-render and archival.

**Default output roots** — chosen at render time based on `--project <slug>`:

| Situation | Root |
|---|---|
| `~/vault/` exists + `--project katib` (default) | `~/vault/content/katib/` |
| `~/vault/` exists + `--project <other>` | `~/vault/projects/<slug>/outputs/` |
| No vault | `~/Documents/katib/` |
| Override anywhere | `$KATIB_OUTPUT_ROOT` |

Project-routed outputs inherit governance from `projects/CLAUDE.md` and any
`projects/<slug>/CLAUDE.md` override. Katib-zone outputs are governed by
`content/katib/CLAUDE.md`. The pre-render governance check validates against
whichever zone the output is destined for. See `references/vault.md` for the
full story.

Examples below use `$OUT` as a stand-in for whichever root is active.

---

## Folder anatomy

```
$OUT/business-proposal/2026-04-25-sample-proposal/
├── manifest.md                      # Vault-compliant hub note (type: output)
├── proposal.en.pdf                  # Rendered artifact — English
├── proposal.ar.pdf                  # Rendered artifact — Arabic
├── assets/
│   └── cover.png                    # Gemini-generated cover (reused across EN + AR)
├── source/
│   ├── proposal.en.html             # Rendered HTML — re-render source of truth
│   ├── proposal.ar.html
│   └── tokens-snapshot.json         # Domain tokens at render time (stable)
└── .katib/
    └── run.json                     # Full render metadata for re-render + audit
```

For tutorials (add `screenshots/`):

```
$OUT/tutorial/2026-04-28-how-to-setup-katib/
├── manifest.md
├── how-to.en.pdf
├── screenshots/
│   ├── step-1.png                   # Raw screenshots
│   ├── step-2.png
│   └── annotated/                   # Post-annotate versions (arrows, frames, blur)
│       ├── step-1.png
│       └── step-2.png
└── source/
    └── how-to.en.html
```

## Slug convention

`<date>-<slug>` where:
- `date`: `YYYY-MM-DD` of first generation
- `slug`: kebab-case derived from the primary document title (max 60 chars)
- Ties go to increment suffix: `2026-04-25-sample-proposal-2/`

## Manifest format

```yaml
---
type: output
created: 2026-04-25
updated: 2026-04-25
tags: [katib, business-proposal, proposal, en, ar]
project: example-project
domain: business-proposal
doc_type: proposal
languages: [en, ar]
formats: [pdf]
cover_style: neural-cartography
layout: classic
katib_version: 0.1.0
source_agent: claude-opus-4-7
reference_code: PROP-2026-001
---

# <Document Title>

## Artifacts

- [proposal.en.pdf](./proposal.en.pdf)
- [proposal.ar.pdf](./proposal.ar.pdf)

## Source

- HTML: [source/proposal.en.html](./source/proposal.en.html)
- Cover: [assets/cover.png](./assets/cover.png)
- Tokens snapshot: [source/tokens-snapshot.json](./source/tokens-snapshot.json)

## Context

Part of [[projects/<project>/index|<project>]]. Generated <date> for <brief purpose>.

## Re-render

```bash
/katib rebuild <this-folder-path>
```
```

## `run.json` format

Machine-readable record of the generation. Structure:

```json
{
  "katib_version": "0.1.0",
  "generated_at": "2026-04-25T14:32:11Z",
  "updated_at": "2026-04-25T14:32:11Z",
  "domain": "business-proposal",
  "doc_type": "proposal",
  "languages": ["en", "ar"],
  "formats": ["pdf"],
  "cover": {
    "style": "neural-cartography",
    "engine": "gemini",
    "model": "nano-banana-2",
    "prompt_hash": "sha256:...",
    "generated_at": "2026-04-25T14:28:00Z"
  },
  "layout": "classic",
  "page_counts": {
    "proposal.en.pdf": 12,
    "proposal.ar.pdf": 12
  },
  "verify": {
    "passed": true,
    "checks": ["no-rgba", "no-letter-spacing-ar", "no-html-placeholders", "page-limit"]
  },
  "source_agent": "claude-opus-4-7",
  "reference_code": "PROP-2026-001"
}
```

## `tokens-snapshot.json`

Frozen copy of `domains/<domain>/tokens.json` at render time. Ensures re-rendering in 6 months produces the same output even if live tokens drift. Always keep this — it's small (~2KB) and essential.

## Re-render contract

`/katib rebuild <folder>` is idempotent if the folder contains:

1. `manifest.md` with all required frontmatter
2. `source/<doc>.<lang>.html`
3. `source/tokens-snapshot.json`
4. `.katib/run.json`

Re-render steps:

1. Read `manifest.md` frontmatter → know domain, doc type, languages, formats, cover style, layout
2. Read `source/tokens-snapshot.json` → use these tokens (not live ones) for CSS injection
3. Re-render each `source/<doc>.<lang>.html` → PDF in place
4. If `--regen-cover`: call `cover.py` with the original prompt from `run.json`; else reuse `assets/cover.png`
5. Update `manifest.md` `updated:` field and `run.json` `updated_at`
6. Run `build.py --verify` on the folder

## Index file (`$OUT/index.md`)

`build.py` appends one bullet per generation between `BUILD_LOG_START` / `BUILD_LOG_END` markers:

```markdown
- 2026-04-25 · business-proposal · [Sample Proposal](./business-proposal/2026-04-25-sample-proposal/manifest.md) · EN+AR · PDF
```

Append-only; never rewrites existing entries.

## Archive lifecycle

When a project goes cold:

```bash
mv $OUT/<domain>/<slug>/ \
   ~/archive/katib/<domain>/<year>/
```

- Manifest still works (relative links are folder-local)
- Re-render still works (all source + metadata present)
- `$OUT/index.md` entry stays (the bullet is informational; its link breaks — that's an archival signal, not a bug)
- Optional: `build.py --archive-check` reports broken index entries quarterly

## Destination modes (config)

Set by `~/.config/katib/config.yaml → output.destination`:

| Mode | Where artifacts land | Manifest? |
|---|---|---|
| `vault` | `~/vault/content/katib/<domain>/<slug>/` (or `~/vault/projects/<slug>/outputs/...` with `--project`) | Yes, in same folder |
| `custom` | `output.custom_path` (default `~/Documents/katib/`) | Optional via `always_create_manifest: true/false` |

The installer writes `destination: vault` if `~/vault/` exists at install time, otherwise `destination: custom` — you can flip it in `~/.config/katib/config.yaml` any time.

In vault mode, the write path goes through `POST /api/vault/notes` by default
(`KATIB_VAULT_MODE=api`) — pre-render governance check + duplicate-content
detection + graceful filesystem fallback. See `references/vault.md` for the
full mode matrix and exit-code contract.

## Memory (separate from output)

Feedback + run logs go to `~/.local/share/katib/memory/`, not in vault, not in projects:

```
~/.local/share/katib/memory/
├── runs.jsonl              # Every generation (append-only)
├── feedback.jsonl          # User corrections
├── domain-requests.jsonl   # Doc types that didn't fit any domain
└── stats.json              # Rolled-up counts
```

Each entry carries a `project:` field. `/katib stats --project <name>` filters; `/katib stats --global` aggregates.

## Enforcement

`build.py --verify <folder>` checks:

- Folder contains `manifest.md` + `source/` + `.katib/run.json`
- Manifest frontmatter matches required fields (per `content/katib/CLAUDE.md`)
- Manifest `created` matches folder date prefix
- Every artifact listed in manifest exists on disk
- `tokens-snapshot.json` is valid JSON matching domain schema
- No orphan files in the folder (e.g., `foo.pdf` not referenced by manifest)
