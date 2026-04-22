#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6.0"]
# ///
"""Katib meta_validator — schema gate that mirrors the vault engine's governance.

This is the Phase 1 bedrock of the vault-API-first migration (see ADR §20).
Every Katib manifest built from Phase 1 onward must pass this validator *before*
any write happens — FS or API. In Phase 2, the API's `createNote()` becomes the
authoritative gate and this validator becomes a pre-flight; they must stay
aligned because any drift here silently becomes "write succeeds locally,
governance rejects it when Phase 2 flips on the API path."

Contract reproduced from soul-hub:
  - Global required fields: `type`, `created`, `tags`
  - Max note size: 1 MB (enforced by API; we warn at >900 KB)
  - Auto-tag `auto-generated` added by the engine when `source_agent` is set,
    so Katib must include it preemptively to keep tags stable across FS→API
    write modes (otherwise the same manifest gets an extra tag on Phase 2)

Zone-specific rules:
  - `content/katib/` (legacy target): allowed types `output, index`; inherits
    content zone's required fields `type, created, tags`
  - `projects/<slug>/outputs/` (new Phase 2 target): allowed types
    `project, learning, decision, debugging, output, index, task, design,
    requirements, reference`; required fields `type, created, tags, project`

Katib-internal fields that must always be present on a manifest (enforced in
addition to vault rules): `title, domain, doc_type, languages, formats,
cover_style, layout, project, katib_version, source_agent`.

Usage:
    # Python API
    from meta_validator import validate, SchemaViolation
    violations = validate(frontmatter_dict, zone="content/katib/tutorial")
    if violations:
        for v in violations:
            print(v)

    # CLI — validate a manifest.md on disk
    python3 scripts/meta_validator.py --manifest path/to/manifest.md
    python3 scripts/meta_validator.py --manifest path/to/manifest.md --zone projects/ils-offers/outputs
    python3 scripts/meta_validator.py --describe-schema  # dump the schema as JSON
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None  # optional; only needed for CLI --manifest mode


# ===================== SCHEMA =====================
# Keep this file in lockstep with:
#   soul-hub/src/lib/vault/types.ts       GLOBAL_REQUIRED_FIELDS, MAX_NOTE_SIZE
#   vault/*/CLAUDE.md                     Allowed Types + Required Fields per zone

GLOBAL_REQUIRED = ["type", "created", "tags"]
MAX_NOTE_SIZE_BYTES = 1024 * 1024
SIZE_WARN_BYTES = 900 * 1024

# Zone governance — mirrors each vault CLAUDE.md
ZONE_GOVERNANCE: dict[str, dict[str, Any]] = {
    "content": {
        "allowed_types": [
            "draft", "social-draft", "social-post", "article-draft",
            "video-script", "video-script-draft", "content-menu", "content-prep",
            "ideas", "daily-quote", "media-asset", "insight-draft",
            "miner-report", "signal-report", "strategist-prep", "output", "index",
        ],
        "required_fields": ["type", "created", "tags"],
    },
    "content/katib": {
        # Inherits from content; restricts to a narrower allowed set
        "allowed_types": ["output", "index"],
        "required_fields": ["type", "created", "tags"],
    },
    "projects": {
        "allowed_types": [
            "project", "learning", "decision", "debugging", "output",
            "index", "task", "design", "requirements", "reference",
        ],
        "required_fields": ["type", "created", "tags", "project"],
    },
    "knowledge": {
        "allowed_types": [
            "research", "pattern", "snippet", "decision", "review", "recipe",
            "report", "analysis", "evaluation", "data-pack", "reference",
            "guide", "wiki", "learning", "debugging", "index",
        ],
        "required_fields": ["type", "created", "tags"],
    },
}

# Katib-specific fields the manifest must always carry in frontmatter.
# `title` is intentionally NOT in this list — the vault engine's parser
# falls back to the first H1 in the body, and Katib's template always
# emits `# {{ title }}` as the first H1, so making title a frontmatter
# requirement would duplicate source-of-truth.
KATIB_REQUIRED = [
    "domain", "doc_type", "languages", "formats",
    "cover_style", "layout", "project", "katib_version", "source_agent",
]


# ===================== VIOLATION TYPES =====================

SEVERITY_ERROR = "error"
SEVERITY_WARN = "warn"


@dataclass
class SchemaViolation:
    severity: str      # "error" | "warn"
    rule: str          # short identifier like "global.required.missing"
    field: str | None  # which field (if applicable)
    message: str       # human-readable

    def __str__(self) -> str:
        prefix = "✗" if self.severity == SEVERITY_ERROR else "⚠"
        field_part = f" [{self.field}]" if self.field else ""
        return f"  {prefix} {self.rule}{field_part}: {self.message}"


# ===================== ZONE RESOLUTION =====================

def resolve_zone(zone: str) -> dict[str, Any]:
    """Walk from most-specific to least-specific and return the matching governance."""
    parts = zone.strip("/").split("/")
    # projects/<slug>/outputs   → match "projects" (the slug is variable)
    # content/katib/<domain>    → match "content/katib" (domain is variable)
    # content/<anything-else>   → match "content"
    # Try exact match first, then walk up.
    for i in range(len(parts), 0, -1):
        candidate = "/".join(parts[:i])
        if candidate in ZONE_GOVERNANCE:
            return ZONE_GOVERNANCE[candidate]
    return {"allowed_types": [], "required_fields": []}


# ===================== VALIDATOR =====================

def validate(
    meta: dict[str, Any],
    *,
    zone: str,
    content_length: int = 0,
) -> list[SchemaViolation]:
    """Return a list of violations. Empty list = schema is clean.

    `zone` is the target vault zone (e.g. "content/katib/tutorial",
    "projects/ils-offers/outputs"). The validator resolves the closest
    matching governance block.
    """
    violations: list[SchemaViolation] = []
    gov = resolve_zone(zone)

    # ── A. Global required fields ──
    for field in GLOBAL_REQUIRED:
        if field not in meta or meta[field] in (None, "", []):
            violations.append(SchemaViolation(
                severity=SEVERITY_ERROR,
                rule="global.required.missing",
                field=field,
                message=f"Global required field '{field}' is missing or empty",
            ))

    # ── B. Zone-specific required fields ──
    for field in gov.get("required_fields", []):
        if field in GLOBAL_REQUIRED:
            continue  # already checked
        if field not in meta or meta[field] in (None, "", []):
            violations.append(SchemaViolation(
                severity=SEVERITY_ERROR,
                rule="zone.required.missing",
                field=field,
                message=f"Zone '{zone}' requires field '{field}' which is missing or empty",
            ))

    # ── C. Type allowlist ──
    note_type = meta.get("type")
    if note_type and gov.get("allowed_types"):
        if note_type not in gov["allowed_types"]:
            violations.append(SchemaViolation(
                severity=SEVERITY_ERROR,
                rule="zone.type.disallowed",
                field="type",
                message=(
                    f"Type '{note_type}' not allowed in zone '{zone}'. "
                    f"Allowed: {', '.join(gov['allowed_types'])}"
                ),
            ))

    # ── D. Katib-specific required fields ──
    for field in KATIB_REQUIRED:
        if field not in meta or meta[field] in (None, "", []):
            # cover_style may legitimately be null for cover-less domains (formal);
            # layout is always required; everything else is a hard error.
            if field == "cover_style" and meta.get("cover_style") is None:
                continue
            violations.append(SchemaViolation(
                severity=SEVERITY_ERROR,
                rule="katib.required.missing",
                field=field,
                message=f"Katib requires field '{field}' on every manifest",
            ))

    # ── E. Tag shape rules ──
    tags = meta.get("tags") or []
    if not isinstance(tags, list):
        violations.append(SchemaViolation(
            severity=SEVERITY_ERROR,
            rule="tags.shape",
            field="tags",
            message="tags must be a list",
        ))
    else:
        # E1. source_agent present ⇒ "auto-generated" tag required
        # (the vault engine auto-adds this; we pre-add it to keep tags stable
        # across FS writes vs API writes, so Phase 2 doesn't change the schema)
        if meta.get("source_agent") and "auto-generated" not in tags:
            violations.append(SchemaViolation(
                severity=SEVERITY_ERROR,
                rule="tags.auto_generated.missing",
                field="tags",
                message=(
                    "source_agent is set → tags must include 'auto-generated' "
                    "(the vault engine adds this automatically; Katib must pre-add "
                    "it so tag shape is stable across FS/API write modes)"
                ),
            ))

        # E2. 'katib' tag always present
        if "katib" not in tags:
            violations.append(SchemaViolation(
                severity=SEVERITY_ERROR,
                rule="tags.katib.missing",
                field="tags",
                message="tags must include 'katib'",
            ))

        # E3. Tag-pollution warning: domain/doc_type/language codes shouldn't
        # appear in tags since they're already structured frontmatter fields.
        lang_codes = ["en", "ar"]
        polluted_tags: list[str] = []
        for t in tags:
            if t == meta.get("domain"):
                polluted_tags.append(f"'{t}' (duplicates frontmatter field 'domain')")
            elif t == meta.get("doc_type"):
                polluted_tags.append(f"'{t}' (duplicates frontmatter field 'doc_type')")
            elif t in lang_codes and t in (meta.get("languages") or []):
                polluted_tags.append(f"'{t}' (duplicates frontmatter field 'languages')")
        for t in polluted_tags:
            violations.append(SchemaViolation(
                severity=SEVERITY_WARN,
                rule="tags.pollution",
                field="tags",
                message=f"Tag {t} — prefer querying via the structured field",
            ))

    # ── F. project field sanity ──
    project = meta.get("project")
    if zone.startswith("projects/"):
        # The project slug must match the path: projects/<slug>/...
        path_parts = zone.strip("/").split("/")
        if len(path_parts) >= 2 and project and project != path_parts[1]:
            violations.append(SchemaViolation(
                severity=SEVERITY_ERROR,
                rule="project.path_mismatch",
                field="project",
                message=(
                    f"Frontmatter project='{project}' but zone path says "
                    f"project='{path_parts[1]}'"
                ),
            ))

    # ── G. Size guards ──
    if content_length > MAX_NOTE_SIZE_BYTES:
        violations.append(SchemaViolation(
            severity=SEVERITY_ERROR,
            rule="size.over_limit",
            field=None,
            message=(
                f"Manifest is {content_length} bytes; max is {MAX_NOTE_SIZE_BYTES} "
                f"(the vault engine would reject on Phase 2)"
            ),
        ))
    elif content_length > SIZE_WARN_BYTES:
        violations.append(SchemaViolation(
            severity=SEVERITY_WARN,
            rule="size.near_limit",
            field=None,
            message=(
                f"Manifest is {content_length} bytes (>{SIZE_WARN_BYTES}); "
                f"approaching 1 MB limit"
            ),
        ))

    return violations


# ===================== MANIFEST.MD READER =====================

_FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n(.*)", re.DOTALL)


def read_manifest(path: Path) -> tuple[dict[str, Any], int]:
    """Parse a manifest.md file and return (frontmatter_dict, byte_length)."""
    if yaml is None:
        raise RuntimeError("pyyaml is required for --manifest mode. `pip install pyyaml`.")
    raw = path.read_text(encoding="utf-8")
    m = _FRONTMATTER_RE.match(raw)
    if not m:
        raise ValueError(f"{path} has no YAML frontmatter block")
    meta = yaml.safe_load(m.group(1)) or {}
    if not isinstance(meta, dict):
        raise ValueError(f"{path} frontmatter is not a dict")
    return meta, len(raw.encode("utf-8"))


# ===================== CLI =====================

def _cli_describe_schema() -> int:
    schema = {
        "global_required": GLOBAL_REQUIRED,
        "max_note_size_bytes": MAX_NOTE_SIZE_BYTES,
        "katib_required": KATIB_REQUIRED,
        "zones": ZONE_GOVERNANCE,
    }
    print(json.dumps(schema, indent=2))
    return 0


def _cli_validate_manifest(path: Path, zone: str | None) -> int:
    meta, size = read_manifest(path)
    if zone is None:
        # Try to infer from the path — works when it's under ~/vault/
        abs_path = path.resolve()
        try:
            parts = abs_path.parts
            if "vault" in parts:
                vault_idx = parts.index("vault")
                zone = "/".join(parts[vault_idx + 1:-1])  # everything between vault/ and manifest.md
            else:
                zone = "content/katib"  # best guess
        except Exception:
            zone = "content/katib"

    print(f"▶ Validating {path}")
    print(f"  zone: {zone}")
    print(f"  size: {size} bytes\n")

    violations = validate(meta, zone=zone, content_length=size)
    if not violations:
        print("✓ clean — no violations")
        return 0

    errors = [v for v in violations if v.severity == SEVERITY_ERROR]
    warns = [v for v in violations if v.severity == SEVERITY_WARN]

    if errors:
        print(f"✗ {len(errors)} error(s):")
        for v in errors:
            print(v)
    if warns:
        print(f"\n⚠ {len(warns)} warning(s):")
        for v in warns:
            print(v)

    return 1 if errors else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--manifest", metavar="PATH", help="Validate an on-disk manifest.md")
    parser.add_argument("--zone", default=None,
                        help="Override the zone (default: inferred from --manifest path)")
    parser.add_argument("--describe-schema", action="store_true",
                        help="Dump the full schema as JSON and exit")
    args = parser.parse_args()

    if args.describe_schema:
        return _cli_describe_schema()
    if args.manifest:
        return _cli_validate_manifest(Path(args.manifest), args.zone)
    parser.error("one of --manifest or --describe-schema is required")


if __name__ == "__main__":
    sys.exit(main())
