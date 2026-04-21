#!/usr/bin/env python3
"""Katib manifest writer.

Builds a vault-compliant manifest.md and run.json for a generation folder.
Enforces the `~/vault/content/katib/CLAUDE.md` zone rules.

Usage:
    from manifest import write_manifest, append_index_entry

    meta = {
        "title": "Sample Proposal",
        "domain": "business-proposal",
        "doc_type": "proposal",
        "languages": ["en", "ar"],
        "formats": ["pdf"],
        ...
    }
    write_manifest(folder, meta)
    append_index_entry(vault_root, folder, meta)
"""
from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

KATIB_VERSION = "0.1.0"
REQUIRED_FIELDS = {
    "title", "domain", "doc_type", "languages", "formats",
    "cover_style", "layout", "project"
}


def _slugify(text: str, max_len: int = 60) -> str:
    s = text.lower().strip()
    s = re.sub(r"[^a-z0-9\u0600-\u06FF\s-]", "", s)  # keep Arabic too for bilingual titles
    s = re.sub(r"[\s_]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s[:max_len]


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _today_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def validate_meta(meta: dict[str, Any]) -> None:
    missing = REQUIRED_FIELDS - set(meta.keys())
    if missing:
        raise ValueError(f"manifest meta missing required fields: {sorted(missing)}")


def build_frontmatter(meta: dict[str, Any], *, created: str, updated: str) -> dict[str, Any]:
    tags = ["katib", meta["domain"], meta["doc_type"], *meta["languages"]]
    if meta.get("project") and meta["project"] != "katib":
        tags.append(meta["project"])
    return {
        "type": "output",
        "created": created,
        "updated": updated,
        "tags": tags,
        "project": meta.get("project", "katib"),
        "domain": meta["domain"],
        "doc_type": meta["doc_type"],
        "languages": meta["languages"],
        "formats": meta["formats"],
        "cover_style": meta["cover_style"],
        "layout": meta["layout"],
        "katib_version": KATIB_VERSION,
        "source_agent": meta.get("source_agent", "claude-opus-4-7"),
        **({"reference_code": meta["reference_code"]} if meta.get("reference_code") else {}),
    }


def _yaml_dump(data: dict[str, Any]) -> str:
    """Minimal YAML writer — avoids PyYAML dependency here.

    Handles only the scalar/list/dict types we actually use in frontmatter.
    """
    lines = []
    for k, v in data.items():
        if isinstance(v, list):
            rendered = "[" + ", ".join(str(x) for x in v) + "]"
            lines.append(f"{k}: {rendered}")
        elif isinstance(v, bool):
            lines.append(f"{k}: {'true' if v else 'false'}")
        elif v is None:
            lines.append(f"{k}: null")
        else:
            # Quote if contains special chars
            s = str(v)
            if any(c in s for c in [":", "#", "@", "|", ">", "{", "}", "[", "]"]):
                s = f'"{s}"'
            lines.append(f"{k}: {s}")
    return "\n".join(lines)


def render_manifest_body(meta: dict[str, Any], folder_name: str, folder: Path | None = None) -> str:
    title = meta["title"]
    project = meta.get("project", "katib")

    # Artifact links
    artifacts = []
    for lang in meta["languages"]:
        for fmt in meta["formats"]:
            artifacts.append(f"- [{meta['doc_type']}.{lang}.{fmt}](./{meta['doc_type']}.{lang}.{fmt})")

    # Source links
    sources = []
    for lang in meta["languages"]:
        sources.append(f"- HTML ({lang}): [source/{meta['doc_type']}.{lang}.html](./source/{meta['doc_type']}.{lang}.html)")
    # Only link cover.png when the image-engine generated a file on disk.
    # CSS-only covers (minimalist-typographic) render inline in HTML — no asset to link.
    cover_exists = folder is not None and (folder / "assets" / "cover.png").exists()
    if cover_exists:
        sources.append("- Cover: [assets/cover.png](./assets/cover.png)")
    sources.append("- Tokens snapshot: [source/tokens-snapshot.json](./source/tokens-snapshot.json)")

    # Purpose line
    purpose = meta.get("purpose", f"{meta['doc_type']} in the {meta['domain']} domain")

    body = f"""
# {title}

## Artifacts

{chr(10).join(artifacts)}

## Source

{chr(10).join(sources)}

## Context

Part of [[projects/{project}/index|{project}]]. Generated {meta.get('created', _today_iso())} — {purpose}.

## Re-render

```bash
/katib rebuild ~/vault/content/katib/{meta['domain']}/{folder_name}/
```
"""
    return body.lstrip()


def _parse_list_field(frontmatter_text: str, key: str) -> list[str]:
    """Pull an inline-list frontmatter value like `languages: [en, ar]` back out as a list."""
    m = re.search(rf"^{re.escape(key)}:\s*\[([^\]]*)\]", frontmatter_text, re.MULTILINE)
    if not m:
        return []
    return [s.strip() for s in m.group(1).split(",") if s.strip()]


def _merge_dedupe(*lists: list[str]) -> list[str]:
    """Union while preserving order of first appearance."""
    seen: dict[str, None] = {}
    for lst in lists:
        for item in lst:
            if item not in seen:
                seen[item] = None
    return list(seen.keys())


def write_manifest(folder: Path, meta: dict[str, Any], *, update: bool = False) -> Path:
    """Write manifest.md into the generation folder.

    If a manifest already exists, `languages` and `formats` are merged (union, dedup,
    preserving order) so that a second-language render doesn't erase the first.
    `created` is always preserved from the existing manifest; `updated` is always bumped.
    Other scalar fields (title, cover_style, etc.) let the new render win — callers that
    want to preserve first-write semantics should not overwrite those fields.
    """
    validate_meta(meta)
    manifest_path = folder / "manifest.md"
    now = _today_iso()

    merged_meta = dict(meta)
    if manifest_path.exists():
        existing = manifest_path.read_text(encoding="utf-8")
        m = re.search(r"^created:\s*(\S+)", existing, re.MULTILINE)
        created = m.group(1) if m else meta.get("created", now)

        existing_langs = _parse_list_field(existing, "languages")
        if existing_langs:
            merged_meta["languages"] = _merge_dedupe(existing_langs, list(meta["languages"]))

        existing_fmts = _parse_list_field(existing, "formats")
        if existing_fmts:
            merged_meta["formats"] = _merge_dedupe(existing_fmts, list(meta["formats"]))
    else:
        created = meta.get("created", now)

    frontmatter = build_frontmatter(merged_meta, created=created, updated=now)
    body = render_manifest_body(merged_meta, folder.name, folder=folder)

    content = f"---\n{_yaml_dump(frontmatter)}\n---\n\n{body}"
    manifest_path.write_text(content, encoding="utf-8")
    return manifest_path


def write_run_json(folder: Path, meta: dict[str, Any], render_meta: dict[str, Any]) -> Path:
    """Write .katib/run.json with full render metadata.

    If run.json already exists, merge languages, formats, and page_counts with the
    existing file so that a second-language render doesn't erase the first.
    generated_at is preserved; updated_at is always bumped.
    """
    katib_dir = folder / ".katib"
    katib_dir.mkdir(exist_ok=True)
    run_path = katib_dir / "run.json"
    now_iso = _utc_now_iso()

    # Merge with existing if present
    existing: dict[str, Any] = {}
    if run_path.exists():
        try:
            existing = json.loads(run_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            existing = {}

    merged_langs = _merge_dedupe(existing.get("languages", []), list(meta["languages"]))
    merged_fmts = _merge_dedupe(existing.get("formats", []), list(meta["formats"]))
    merged_page_counts = {**existing.get("page_counts", {}), **render_meta.get("page_counts", {})}

    data = {
        "katib_version": KATIB_VERSION,
        "generated_at": existing.get("generated_at", render_meta.get("generated_at", now_iso)),
        "updated_at": now_iso,
        "domain": meta["domain"],
        "doc_type": meta["doc_type"],
        "languages": merged_langs or list(meta["languages"]),
        "formats": merged_fmts or list(meta["formats"]),
        "cover": render_meta.get("cover", existing.get("cover", {})),
        "layout": meta["layout"],
        "page_counts": merged_page_counts,
        "verify": render_meta.get("verify", {"passed": None, "checks": []}),
        "source_agent": meta.get("source_agent", "claude-opus-4-7"),
        **({"reference_code": meta["reference_code"]} if meta.get("reference_code") else {}),
    }
    run_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return run_path


def write_tokens_snapshot(folder: Path, tokens: dict[str, Any]) -> Path:
    """Freeze domain tokens alongside the source HTML for stable re-render."""
    source_dir = folder / "source"
    source_dir.mkdir(exist_ok=True)
    snapshot_path = source_dir / "tokens-snapshot.json"
    snapshot_path.write_text(json.dumps(tokens, indent=2) + "\n", encoding="utf-8")
    return snapshot_path


def append_index_entry(vault_katib_root: Path, folder: Path, meta: dict[str, Any]) -> None:
    """Append one bullet to content/katib/index.md between BUILD_LOG markers.

    Append-only: never rewrites existing entries.
    """
    index_path = vault_katib_root / "index.md"
    if not index_path.exists():
        raise FileNotFoundError(f"index.md missing: {index_path}")

    existing = index_path.read_text(encoding="utf-8")
    start_marker = "<!-- BUILD_LOG_START"
    end_marker = "<!-- BUILD_LOG_END"

    # Build the bullet
    langs = "+".join(L.upper() for L in meta["languages"])
    fmts = "+".join(F.upper() for F in meta["formats"])
    rel_manifest = folder.relative_to(vault_katib_root).as_posix() + "/manifest.md"
    title = meta["title"]
    domain = meta["domain"]
    date = meta.get("created", _today_iso())

    entry = f"- {date} · {domain} · [{title}](./{rel_manifest}) · {langs} · {fmts}"

    # Find the BUILD_LOG_START line in full and splice the entry right after it.
    match = re.search(r"^(.*<!-- BUILD_LOG_START[^\n]*-->)\s*\n", existing, re.MULTILINE)
    if not match:
        raise ValueError(f"BUILD_LOG_START marker missing or malformed in {index_path}")
    marker_line = match.group(1)
    split_point = match.end()
    new_content = existing[:split_point] + entry + "\n" + existing[split_point:]

    # Update frontmatter updated field
    new_content = re.sub(
        r"^updated:\s*\S+",
        f"updated: {_today_iso()}",
        new_content,
        count=1,
        flags=re.MULTILINE,
    )

    index_path.write_text(new_content, encoding="utf-8")


def folder_name(date_str: str, title: str) -> str:
    return f"{date_str}-{_slugify(title)}"


if __name__ == "__main__":
    # Smoke test
    import tempfile
    sample_meta = {
        "title": "Sample Proposal",
        "domain": "business-proposal",
        "doc_type": "proposal",
        "languages": ["en", "ar"],
        "formats": ["pdf"],
        "cover_style": "neural-cartography",
        "layout": "classic",
        "project": "example-project",
        "reference_code": "PROP-2026-001",
        "purpose": "Example proposal — replace with your own content",
    }
    with tempfile.TemporaryDirectory() as td:
        folder = Path(td) / folder_name(_today_iso(), sample_meta["title"])
        folder.mkdir(parents=True)
        write_manifest(folder, sample_meta)
        write_run_json(folder, sample_meta, {"page_counts": {"proposal.en.pdf": 12}})
        write_tokens_snapshot(folder, {"accent": "#1B2A4A"})
        print(f"✓ manifest:\n{(folder / 'manifest.md').read_text()[:500]}...")
        print(f"\n✓ run.json:\n{(folder / '.katib' / 'run.json').read_text()}")
