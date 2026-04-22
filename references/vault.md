# Katib — Vault Integration

Katib is a vault-API-first client. Every render produces a governed manifest
note that the Soul Hub vault has accepted (or, in fallback, one marked clearly
for later reconciliation). This document covers the integration contract,
routing rules, mode selection, and the tooling that keeps the vault healthy.

The migration that delivered this was tracked in ADR §20 (vault-integration
migration) and shipped across five versions — v0.14.0 through v0.18.0.

---

## TL;DR

```bash
# Default: API write path, pre-render governance check, graceful fallback
uv run scripts/build.py proposal --domain business-proposal --lang en \
    --project ils-offers --title "..."

# CI mode — fail hard if Soul Hub is unreachable
KATIB_VAULT_MODE=strict uv run scripts/build.py ...

# Offline / render-only mode — skip the API entirely
KATIB_VAULT_MODE=fs uv run scripts/build.py ...
```

---

## 1. Routing — where outputs land

Output folder is chosen at render time based on `--project <slug>`:

| `--project` value | Output root | Governance zone |
|---|---|---|
| `katib` (default) | `<vault>/content/katib/<domain>/<slug>/` | `content/katib/` |
| anything else | `<vault>/projects/<slug>/outputs/<domain>/<slug>/` | `projects/<slug>/outputs/` (inherits from `projects/`) |

The vault root itself resolves in this order:

1. `KATIB_VAULT_ROOT` env var — absolute override
2. `cfg.output.vault_root` — if set in `~/.config/katib/config.yaml`
3. Strip `content/katib` from `cfg.output.vault_path` — the install-time convention

`KATIB_OUTPUT_ROOT` overrides the full output path (used by test harnesses to
isolate writes).

## 2. Mode matrix — `KATIB_VAULT_MODE`

| Mode | Pre-render check | Manifest write | Network failure |
|---|---|---|---|
| `api` (default) | On | `POST /api/vault/notes` → FS fallback with `katib-fallback` tag | Fallback to FS; warn on stderr |
| `strict` | On | `POST /api/vault/notes` only | Raise `VaultNetworkError`, exit 5 |
| `fs` | Off (skipped by design) | Direct FS write via atomic temp-file-then-replace | N/A |

The `api` mode is the right default for interactive use: it gets the vault's
duplicate-content detector, zone validation, and provenance tracking on every
write, but never blocks a legitimate render if Soul Hub happens to be down.

The `strict` mode is for CI — where silent fallback to FS would hide a real
configuration issue. Pair it with `--strict-governance` (on by default in
`strict` mode) for full enforcement.

The `fs` mode is for render tests and offline work — deterministic and fast,
but bypasses all governance. Renders made in `fs` mode get a `katib-fs-only`
tag so they're easy to audit later.

## 3. Pre-render governance check

Before any PDF render starts, Katib fetches the target zone's governance:

```
GET http://localhost:2400/api/vault/zones/<path>
→ { zone, resolvedFrom, allowedTypes, requiredFields, namingPattern, requireTemplate }
```

Katib then validates the proposed manifest against the contract. If it would
fail (e.g. zone disallows `type: output`, required field missing, naming
pattern mismatch), the build exits 4 with a readable error — no PDF gets
rendered, no orphan folder gets left behind.

Governance responses are cached in-memory for 60s keyed on `base_url::zone`
(measured ~1100× speedup for repeat lookups in the same process).

Turn it off with `--no-strict-governance` if you're developing against a zone
whose `CLAUDE.md` is known-stale. Default: on when `KATIB_VAULT_MODE=api|strict`,
off for `fs`.

## 4. Manifest write contract

The manifest frontmatter sent to `POST /api/vault/notes`:

```yaml
---
type: output
created: 2026-04-22          # ISO date, coerced to string
updated: 2026-04-22
tags: [katib, <project>, auto-generated]
project: <project-slug>
domain: <domain>
doc_type: <doc_type>
languages: [en, ar]
formats: [pdf]
cover_style: <style>
layout: <layout>
katib_version: 0.18.0
source_agent: claude-opus-4-7
source_context: katib-<hash8>   # BLAKE2s hash of run-id for provenance
reference_code: <RC>
---
```

Tag contract is exactly `[katib, <project>, auto-generated]` — no domain,
doc_type, or language pollution. The zone CLAUDE.md enforces this.

## 5. Fallback semantics

When `KATIB_VAULT_MODE=api` (default) and the API fails:

| Failure | Fallback | Tag added |
|---|---|---|
| Connection refused / timeout | Write to FS | `katib-fallback` |
| HTTP 5xx | Write to FS | `katib-fallback` |
| HTTP 409 (conflict) | Raise `VaultConflictError`, exit 5 | — |
| HTTP 4xx (other) | Raise `VaultGovernanceError`, exit 4 | — |
| Non-JSON response | Write to FS | `katib-fallback` |

`katib-fallback` tags are visible in `audit_vault.py --json` output so they
can be reconciled after the fact (POST them through once Soul Hub is back).

## 6. Incident recovery

`scripts/recover_vault.py` finds folders with `.katib/run.json` but no
`manifest.md` (the shape an incomplete migration or interrupted write
leaves behind). It reconstructs the manifest from the surviving run-log +
HTML source (extracts title from `<h1>` or `<title>`), writes it with
current v0.18.0 contract.

Idempotent on a healthy vault — safe to run unconditionally:

```bash
uv run scripts/recover_vault.py                 # scan + report
uv run scripts/recover_vault.py --execute       # actually rebuild
```

## 7. Audit & migration tools

`scripts/audit_vault.py` — read-only walker:

```bash
uv run scripts/audit_vault.py                   # text summary
uv run scripts/audit_vault.py --verbose         # per-manifest breakdown
uv run scripts/audit_vault.py --json            # for tooling
uv run scripts/audit_vault.py --report          # markdown → vault/knowledge/
```

`scripts/migrate_vault.py` — retroactive cleanup:

```bash
uv run scripts/migrate_vault.py                 # dry-run (default)
uv run scripts/migrate_vault.py --execute       # apply with confirmation
uv run scripts/migrate_vault.py --execute --yes # skip confirmation (CI)
```

Migrate rebuilds tags, updates `katib_version` + `source_agent`, adds
`migrated_at` audit stamp, relocates `project != 'katib'` folders out of
`content/katib/` into `projects/<slug>/outputs/`. Writes via FS with atomic
temp-file-then-replace — never delete-then-write.

## 8. Exit-code contract

| Exit | Reason | What to do |
|---|---|---|
| 0 | Success — manifest written via API or FS | — |
| 1 | Generic render failure (template missing, bad input, etc.) | Read stderr |
| 2 | Verification failure (page overflow, placeholder, font issue) | Fix content |
| 3 | Page-limit exceeded (hard limit from `styles.json`) | Trim content |
| 4 | Governance rejection (pre-render check or API 4xx) | Update manifest or zone `CLAUDE.md` |
| 5 | Network failure in `strict` mode, or HTTP 409 conflict | Retry or resolve conflict manually |

## 9. Configuration

`~/.config/katib/config.yaml`:

```yaml
output:
  destination: vault               # or "custom"
  vault_path: ~/vault/content/katib    # the katib zone inside the vault
  vault_root: ~/vault              # optional — explicit vault root
  custom_path: ~/Documents/katib   # used when destination=custom
  always_create_manifest: true
```

`vault_path` is the katib zone specifically. `vault_root` is the whole vault
(needed for project routing). If `vault_root` is omitted, Katib derives it by
stripping `content/katib` from `vault_path`.

## 10. Related

- `content/katib/CLAUDE.md` — zone governance for katib-specific outputs
- `projects/CLAUDE.md` + `projects/<slug>/CLAUDE.md` — zone governance for project outputs
- `scripts/meta_validator.py` — the offline validator (mirrors server-side governance)
- `scripts/vault_client.py` — the HTTP client (stdlib urllib only)
- Soul Hub `src/routes/api/vault/zones/[...path]/+server.ts` — governance read endpoint
- Soul Hub `src/routes/api/vault/notes/+server.ts` — manifest write endpoint
- ADR §20 in `vault/knowledge/adr-katib-document-generation-skill.md`
