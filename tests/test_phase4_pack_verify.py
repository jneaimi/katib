"""Phase-4 Day 4 — `katib pack verify`.

Verify is the CI-grade safety check. It runs in this order; each
step gates the next so a structurally-broken pack fails fast:

1. Pack opens cleanly (gzip + tar parseable, manifest present)
2. Manifest schema-validates
3. content_hash recomputes correctly
4. pack_format is supported by this host
5. Every component + recipe inside passes its existing validator

A pack must clear all five steps to be "verified". CI uses the exit
code: 0 = ok, 1 = something failed.
"""
from __future__ import annotations

import gzip
import io
import json
import subprocess
import sys
import tarfile
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from core import pack as pack_mod  # noqa: E402


def _author() -> dict[str, str]:
    return {"name": "Test User", "email": "test@example.com"}


def _rebuild_pack_with(
    src_path: Path,
    dest_path: Path,
    *,
    manifest_override: dict | None = None,
    drop_files: list[str] | None = None,
) -> None:
    """Re-pack `src_path` to `dest_path`, optionally overriding the
    manifest dict or dropping listed arcnames. Useful for crafting
    tampered packs in tests."""
    drop_files = drop_files or []
    with open(src_path, "rb") as f:
        with gzip.GzipFile(fileobj=f) as gz:
            inner = gz.read()
    entries: dict[str, bytes] = {}
    with tarfile.open(fileobj=io.BytesIO(inner), mode="r") as tar:
        for info in tar.getmembers():
            if info.name in drop_files:
                continue
            entries[info.name] = tar.extractfile(info).read()

    if manifest_override is not None:
        entries["pack.yaml"] = yaml.safe_dump(
            manifest_override, sort_keys=False, default_flow_style=False
        ).encode("utf-8")

    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w") as tar:
        for arcname in sorted(entries):
            data = entries[arcname]
            info = tarfile.TarInfo(name=arcname)
            info.size = len(data)
            info.mtime = 0
            info.mode = 0o644
            info.uid = 0
            info.gid = 0
            tar.addfile(info, io.BytesIO(data))

    with open(dest_path, "wb") as f:
        with gzip.GzipFile(fileobj=f, mode="wb", mtime=0) as gz:
            gz.write(raw.getvalue())


# ---------------------------------------------------------------------------
# Verify — happy path
# ---------------------------------------------------------------------------


def test_verify_fresh_component_pack(tmp_path):
    res = pack_mod.export_component("eyebrow", author=_author(), out_dir=tmp_path)
    v = pack_mod.verify_pack(Path(res.pack_path))
    assert v.ok, (
        f"verify failed unexpectedly: hash={v.hash_match} schema={v.schema_errors} "
        f"comp={v.component_issues} recipe={v.recipe_issues}"
    )
    assert v.hash_match is True
    assert v.schema_errors == []
    assert v.component_issues == {}


def test_verify_fresh_recipe_pack(tmp_path):
    res = pack_mod.export_recipe("tutorial", author=_author(), out_dir=tmp_path)
    v = pack_mod.verify_pack(Path(res.pack_path))
    assert v.ok


def test_verify_fresh_brand_pack(tmp_path):
    res = pack_mod.export_brand("example", author=_author(), out_dir=tmp_path)
    v = pack_mod.verify_pack(Path(res.pack_path))
    # No components or recipes inside, so per-artifact validation is empty.
    assert v.ok


# ---------------------------------------------------------------------------
# Verify — tamper detection
# ---------------------------------------------------------------------------


def test_verify_tampered_content_hash_refused(tmp_path):
    """Manually flip a byte in the manifest's claimed hash."""
    res = pack_mod.export_component("eyebrow", author=_author(), out_dir=tmp_path)
    src = Path(res.pack_path)
    insp = pack_mod.inspect_pack(src)
    # Read manifest, swap one hex char in the hash, rebuild
    hashed = insp.content_hash_claim
    tampered_hash = (
        hashed[: -1] + ("0" if hashed[-1] != "0" else "1")
    )
    bad_manifest = {
        "pack_format": 1,
        "name": insp.name,
        "version": insp.version,
        "content_hash": tampered_hash,
        "contents": insp.contents,
        "requires": insp.requires,
    }
    if insp.author:
        bad_manifest["author"] = insp.author
    if insp.description:
        bad_manifest["description"] = insp.description

    bad_path = tmp_path / "tampered.katib-pack"
    _rebuild_pack_with(src, bad_path, manifest_override=bad_manifest)

    v = pack_mod.verify_pack(bad_path)
    assert v.ok is False
    assert v.hash_match is False
    # Schema is still fine
    assert v.schema_errors == []


def test_verify_dropped_required_file_refused(tmp_path):
    """If a required component file (e.g., en.html for an EN-language
    component) is dropped from the pack, the body content_hash will
    differ — and the per-component validator would fail too if hash
    weren't already gating."""
    res = pack_mod.export_component("eyebrow", author=_author(), out_dir=tmp_path)
    src = Path(res.pack_path)
    # Drop en.html from the pack body (without rewriting manifest).
    bad_path = tmp_path / "missing-en.katib-pack"
    _rebuild_pack_with(
        src, bad_path, drop_files=["components/primitives/eyebrow/en.html"]
    )
    v = pack_mod.verify_pack(bad_path)
    assert v.ok is False
    assert v.hash_match is False


# ---------------------------------------------------------------------------
# Verify — schema violations
# ---------------------------------------------------------------------------


def test_verify_unsupported_pack_format_refused(tmp_path):
    """Forward-compat: a pack from a future host with pack_format > 1
    must be refused, not silently parsed."""
    res = pack_mod.export_component("eyebrow", author=_author(), out_dir=tmp_path)
    src = Path(res.pack_path)
    insp = pack_mod.inspect_pack(src)
    bad_manifest = {
        "pack_format": 2,            # invalid for this host
        "name": insp.name,
        "version": insp.version,
        "content_hash": insp.content_hash_claim,
        "contents": insp.contents,
        "requires": insp.requires,
    }
    bad_path = tmp_path / "future-format.katib-pack"
    _rebuild_pack_with(src, bad_path, manifest_override=bad_manifest)

    v = pack_mod.verify_pack(bad_path)
    assert v.ok is False
    # Schema rejects pack_format=2 because schema is `const: 1`. Either
    # `pack_format_supported=False` or `schema_errors` non-empty would
    # block. We assert schema catches it (the const check fires first).
    assert v.schema_errors, "expected schema error for pack_format=2"


def test_verify_extra_top_level_key_refused(tmp_path):
    res = pack_mod.export_component("eyebrow", author=_author(), out_dir=tmp_path)
    src = Path(res.pack_path)
    insp = pack_mod.inspect_pack(src)
    bad_manifest = {
        "pack_format": 1,
        "name": insp.name,
        "version": insp.version,
        "content_hash": insp.content_hash_claim,
        "contents": insp.contents,
        "requires": insp.requires,
        "future_field": "should be rejected",  # additionalProperties: false
    }
    bad_path = tmp_path / "extra-field.katib-pack"
    _rebuild_pack_with(src, bad_path, manifest_override=bad_manifest)

    v = pack_mod.verify_pack(bad_path)
    assert v.ok is False
    assert any("future_field" in e or "(root)" in e for e in v.schema_errors), v.schema_errors


# ---------------------------------------------------------------------------
# Verify — non-pack files
# ---------------------------------------------------------------------------


def test_verify_nonexistent_path_raises(tmp_path):
    with pytest.raises(ValueError, match="not found"):
        pack_mod.verify_pack(tmp_path / "no.katib-pack")


def test_verify_non_gzip_raises(tmp_path):
    p = tmp_path / "junk.katib-pack"
    p.write_bytes(b"not gzipped")
    with pytest.raises(ValueError, match="not a valid gzipped tar"):
        pack_mod.verify_pack(p)


# ---------------------------------------------------------------------------
# CLI subprocess — exit codes
# ---------------------------------------------------------------------------


def test_cli_verify_ok_exits_zero(tmp_path):
    res = pack_mod.export_component("eyebrow", author=_author(), out_dir=tmp_path)
    r = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "pack.py"), "verify", res.pack_path],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"stderr={r.stderr}"
    assert "VERIFIED" in r.stdout


def test_cli_verify_tampered_exits_one(tmp_path):
    res = pack_mod.export_component("eyebrow", author=_author(), out_dir=tmp_path)
    src = Path(res.pack_path)
    insp = pack_mod.inspect_pack(src)
    bad_manifest = {
        "pack_format": 1,
        "name": insp.name,
        "version": insp.version,
        "content_hash": "sha256:" + "0" * 64,    # zero hash → won't match
        "contents": insp.contents,
        "requires": insp.requires,
    }
    bad_path = tmp_path / "tampered.katib-pack"
    _rebuild_pack_with(src, bad_path, manifest_override=bad_manifest)

    r = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "pack.py"), "verify", str(bad_path)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 1
    assert "FAILED" in r.stdout


def test_cli_verify_json(tmp_path):
    res = pack_mod.export_component("eyebrow", author=_author(), out_dir=tmp_path)
    r = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "pack.py"),
            "--json",
            "verify",
            res.pack_path,
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0
    payload = json.loads(r.stdout)
    assert payload["ok"] is True
    assert payload["hash_match"] is True
    assert payload["pack_format_supported"] is True
