# Katib pack format (v1)

A `.katib-pack` is a portable bundle of user-tier Katib content —
recipes, components, brand profiles — that can be exported from one
install and imported into another. This document is the public spec.

**Frozen at `pack_format: 1` for `@jasemal/katib@1.0.0`.** The schema
is a public contract. Future breaking changes will require
`pack_format: 2` with explicit migration; v1 packs will keep
installing on v1.x and v2.x hosts indefinitely.

> **Status: BETA.** Format frozen at `1.0.0-beta.1` (2026-04-25);
> stabilizes as the contract on v1.0.0 final after a ~1-week soak.
> No format-level changes are planned during the beta window —
> only bug fixes and documentation polish.

---

## At a glance

```
client-proposal-1.2.0.katib-pack            ← gzipped tar
├── pack.yaml                               ← manifest (REQUIRED)
├── components/
│   ├── sections/client-hero/
│   │   ├── component.yaml
│   │   ├── en.html
│   │   ├── ar.html
│   │   ├── styles.css
│   │   └── README.md
│   └── primitives/client-stat/...
├── recipes/
│   └── client-proposal.yaml
└── brands/
    ├── acme.yaml
    └── acme-assets/                        ← cover presets, logos
        └── covers/hero.png
```

The container is `tar` compressed with `gzip` (`mtime=0` for
byte-reproducibility). Inside the tar:

- `pack.yaml` is required; it is the only file outside the
  `components/`, `recipes/`, `brands/` namespaces.
- All other entries are organized by their target tier in `~/.katib/`.

---

## CLI summary

```bash
# Pack
katib pack export --component <name>            # one component
katib pack export --recipe <name>               # one recipe
katib pack export --brand <name>                # one brand profile
katib pack export --bundle <recipe>             # recipe + custom deps
katib pack export --bundle <recipe> --include-brand <name>

# Inspect / verify
katib pack inspect <pack>                       # manifest dump
katib pack verify <pack>                        # CI-grade safety check

# Install
katib pack import <pack>                        # writes to ~/.katib/
katib pack import <pack> --dry-run              # plan only
katib pack import <pack> --force --justification "<reason>"
```

All commands accept `--json` for machine-readable output. All exit
non-zero on operational error (missing artifact, schema violation,
verification failure, dep missing, collision refused).

---

## `pack.yaml` reference

### Required fields

| Field | Type | Description |
|---|---|---|
| `pack_format` | int (must be `1`) | Pack format version. Hosts refuse `pack_format > supported_max`. |
| `name` | string | Namespaced pack identity, `<author>/<artifact>`. Lowercase kebab-case both halves. |
| `version` | string (semver) | Pack version. Independent of internal artifact versions for bundles; equals the artifact version for single-artifact packs. |
| `content_hash` | string (`sha256:[0-9a-f]{64}`) | SHA-256 of the deterministic tar body (excluding `pack.yaml` itself). Tampering with any inner file flips this. |
| `contents` | object | What's inside. Keys: `components[]`, `recipes[]`, `brands[]`. |
| `requires` | object | Host requirements. Keys: `katib_min`, `bundled_components[]`, `bundled_brands[]`, `external_packs[]`. |

### `contents`

```yaml
contents:
  components:
    - name: client-hero
      tier: section            # primitive | section | cover
      version: 0.1.0           # optional
    - name: client-stat
      tier: primitive
  recipes:
    - name: client-proposal
      version: 1.2.0
  brands:
    - name: acme
```

### `requires`

```yaml
requires:
  katib_min: 1.0.0                     # host must be ≥ this
  bundled_components: [module, kv-list]   # must exist in host's bundled tier
  bundled_brands: [example]            # must exist in host's bundled tier
  external_packs: []                   # forward-compat for Phase 7 dep-on-other-pack
```

Import refuses with a clear message naming the missing items if any
of the bundled deps aren't satisfied. PEP-440 / semver comparison via
the `packaging` library — handles `1.0.0-alpha.2`-style npm
pre-release tags.

### Optional metadata

| Field | Type | Description |
|---|---|---|
| `author.name` | string | Free-form name. Used to slug the `<author>` segment of `name` on export. |
| `author.email` | string (email format) | Optional. Surfaces in `katib pack inspect`. |
| `author.url` | string (URL format) | Optional homepage. |
| `license` | string | SPDX identifier (`MIT`, `Apache-2.0`, etc.). |
| `description` | string | One-paragraph summary, ≤ 1000 chars. |
| `tags` | array of kebab-case strings | Free-form categorization. |
| `domain` | string (kebab-case) | Primary domain hint for marketplace categorization (`business`, `legal`, etc.). |
| `marketplace.preview_image` | string | Path inside the pack to a marketplace preview image (Phase 6+ only). |
| `marketplace.documentation_url` | string (URL) | External docs link (Phase 6+ only). |

### Reserved fields (Phase 7)

| Field | Status |
|---|---|
| `signature` | Reserved for pack signing. Ignored on import in v1. |
| `signed_by` | Reserved for verified-publisher binding. Ignored on import in v1. |

A v1 pack may include these fields; a v1 host stores them in the
imported manifest copy but does not act on them.

---

## Audit-bootstrap entries

Every imported component and recipe gets an audit entry written to
`~/.katib/memory/component-audit.jsonl` or `recipe-audit.jsonl`:

```json
{
  "component": "client-hero",
  "tier": "section",
  "namespace": "user",
  "action": "imported",
  "source_pack": "jneaimi/client-proposal",
  "source_pack_version": "1.2.0",
  "source_hash": "sha256:7b3f1c...",
  "at": "2026-04-25T12:34:56Z"
}
```

If `--force --justification "<reason>"` is used to overwrite a
collision, the entry also includes:

```json
{
  ...,
  "force": true,
  "justification": "<reason>"
}
```

These rows satisfy the same audit gate that hand-edited registry
entries fail. There is no back door.

---

## Refusal classes (in order)

`katib pack import` and `katib pack verify` apply the same gates in
the same order. Each step short-circuits the next:

1. **Pack opens cleanly.** Gzip + tar parseable, `pack.yaml` present.
   Fails: `Pack is not a valid gzipped tar`, `Pack is missing 'pack.yaml'`.
2. **Manifest schema-valid.** Required fields present, types correct,
   no extra top-level keys, name/version/hash regex match.
   Fails: `manifest schema error: ...`.
3. **`pack_format` supported.** Host refuses any `pack_format > 1`.
   Fails: `unsupported pack_format`.
4. **`content_hash` matches.** Recompute SHA-256 over the canonical
   body and compare to the manifest claim.
   Fails: `content_hash mismatch`.
5. **Per-artifact validation.** Every component runs through
   `scripts/component.py validate` semantics; every recipe runs
   through `scripts/recipe.py validate` semantics.
   Fails: `<N> component error(s)`, `<N> recipe error(s)`.
6. **Bundled-dep gate (import only).** Host has every name in
   `requires.bundled_components` + `requires.bundled_brands`, and
   host version ≥ `requires.katib_min`.
   Fails: `missing bundled component(s): ...`, `host Katib version
   N is older than required minimum M`.
7. **Collision check (import only).** If any target path exists in
   the user tier and `--force` is not set, refuse.
   Fails: `Import would overwrite N existing path(s)...`.
8. **Force requires justification.** If `--force` is set and there
   are collisions, `--justification "<reason>"` must be supplied.
   Fails: `--force requires --justification`.

Verify reports across steps 1–5 in one run so the operator gets a
full picture. Import short-circuits at the first failing step (no
partial writes).

---

## Determinism

Two consecutive `katib pack export` runs on the same source state
produce **byte-identical** `.katib-pack` files. Mechanisms:

- Tar entries sorted alphabetically before adding.
- Every tar entry's `mtime` forced to `0`, `uid`/`gid` to `0`,
  `uname`/`gname` empty, `mode` to `0644`.
- The outer gzip is created with `mtime=0`.
- The `content_hash` is computed over an inner deterministic tar
  (uncompressed) — same hash whether the outer gzip is built with
  Python 3.12, 3.13, or any future version.

This is the foundation for Phase-6 content-addressable distribution:
the registry can dedup packs by their content hash, and a pack
fetched twice must hash to the same value.

---

## Versioning

| Component | Versioning rule |
|---|---|
| `pack_format` | Frozen at `1` for v1.0.0. New format = `2`. |
| `name` | Namespace `<author>/<artifact>`. Lowercase kebab-case. |
| `version` (pack) | Semver. Independent of internal artifact versions for bundles. |
| Component / recipe versions | Their own semver, declared in their respective YAMLs. |

Forward-compat for `pack_format`: hosts must refuse a pack whose
`pack_format` exceeds the host's max-supported. v1 hosts always
refuse `pack_format: 2` packs.

Backward-compat: v2 hosts will read v1 packs indefinitely (or
until v3 if a future redesign requires it).

---

## What's NOT in the pack

- **Bundled components, recipes, or brands** — these ship with the
  Katib install. The pack only carries user-tier content.
- **Capabilities cache** (`capabilities.yaml`) — regenerated on import.
- **Audit history** — bootstrap entries are written on import; the
  pack does not carry the source machine's audit log.
- **Generated PDFs / output** — the pack is content-only.
- **Editor backups, dot-files** — only the allowlist of source files
  per tier (`component.yaml`, `*.html`, `styles.css`, `README.md`,
  `tests/test-inputs.yaml`) is included.

---

## Distributing packs

Phase 4 (this document) ships **local** sharing only:

- Email a `.katib-pack` to a colleague.
- Drop it on a shared drive / S3 / Dropbox.
- Attach to a GitHub release.
- Sync it across your own machines via Syncthing / Dropbox / Drive.

**Phase 6** (post-v1.0.0) ships a curated marketplace at
`katib.jneaimi.com` where packs are listed, fetched, and updated
via:

```bash
katib search invoice
katib install jneaimi/financial-invoice
katib install jneaimi/financial-invoice@1.2.0
katib update jneaimi/financial-invoice
```

The artifact format does not change between Phase 4 and Phase 6 —
the same `.katib-pack` ships from a CDN instead of a USB stick.

---

## Spec source of truth

The JSON Schema for `pack.yaml` lives at
[`schemas/pack.yaml.schema.json`](schemas/pack.yaml.schema.json).
The schema is part of the public contract — breaking changes require
a `pack_format` bump.

Validation logic lives in `core/pack.py`. CLI entry point is
`scripts/pack.py`.

---

## Related

- [Marketplace + Sharing ADR](https://github.com/jneaimi/katib/blob/main/docs/) — design rationale and the Phase 5/6/7 plan
- [v2 Component Architecture ADR](https://github.com/jneaimi/katib/blob/main/docs/) — the broader v2 redesign that the pack format ships into
- [User-Content Layout ADR](https://github.com/jneaimi/katib/blob/main/docs/) — `~/.katib/` is where imported packs land
