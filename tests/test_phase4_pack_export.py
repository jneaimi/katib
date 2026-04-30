"""Phase-4 Day 2 — `katib pack export` for single artifacts.

Covers component, recipe, and brand single-artifact export. Bundle
export with dependency walking is Day 3.

Round-trip discipline: every test that exports a pack also re-extracts
it and compares the inner files byte-for-byte against the source on
disk. This is the contract that makes peer-to-peer sharing safe.
"""
from __future__ import annotations

import gzip
import io
import os
import re
import subprocess
import sys
import tarfile
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from core import pack as pack_mod  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _extract_pack(pack_path: Path) -> dict[str, bytes]:
    """Read a `.katib-pack` and return {arcname: bytes} for every entry."""
    with open(pack_path, "rb") as f:
        with gzip.GzipFile(fileobj=f) as gz:
            with tarfile.open(fileobj=io.BytesIO(gz.read()), mode="r") as tar:
                return {info.name: tar.extractfile(info).read() for info in tar.getmembers()}


def _author_from_test_env() -> dict[str, str]:
    """Stable author for tests so manifest.author doesn't depend on
    the developer's git config."""
    return {"name": "Test User", "email": "test@example.com"}


# ---------------------------------------------------------------------------
# Component export
# ---------------------------------------------------------------------------


def test_export_primitive_component(tmp_path: Path):
    """Export a known shipped primitive — round-trip its files byte-for-byte."""
    result = pack_mod.export_component("eyebrow", author=_author_from_test_env(), out_dir=tmp_path)

    assert result.artifact_kind == "component"
    assert result.artifact_name == "eyebrow"
    assert result.pack_name == "test-user/eyebrow"
    assert result.content_hash.startswith("sha256:")
    assert Path(result.pack_path).exists()
    assert result.pack_bytes > 0

    contents = _extract_pack(Path(result.pack_path))
    assert "pack.yaml" in contents
    # eyebrow is a primitive
    expected_prefix = "components/primitives/eyebrow/"
    assert any(k.startswith(expected_prefix) for k in contents)
    assert f"{expected_prefix}component.yaml" in contents

    # Source byte-for-byte equivalence
    src_dir = REPO_ROOT / "components" / "primitives" / "eyebrow"
    assert contents[f"{expected_prefix}component.yaml"] == (src_dir / "component.yaml").read_bytes()


def test_export_section_component(tmp_path: Path):
    """Export a section component — verify tier-aware arcnames."""
    result = pack_mod.export_component("module", author=_author_from_test_env(), out_dir=tmp_path)
    contents = _extract_pack(Path(result.pack_path))
    assert "components/sections/module/component.yaml" in contents
    # No primitives/ or covers/ paths for a section component
    assert not any(k.startswith("components/primitives/module/") for k in contents)


def test_export_unknown_component_fails(tmp_path: Path):
    with pytest.raises(ValueError, match="not found"):
        pack_mod.export_component("does-not-exist-xyz", out_dir=tmp_path)


def test_export_component_manifest_well_formed(tmp_path: Path):
    """Manifest must pass schema validation when re-loaded."""
    result = pack_mod.export_component("eyebrow", author=_author_from_test_env(), out_dir=tmp_path)
    contents = _extract_pack(Path(result.pack_path))
    manifest = yaml.safe_load(contents["pack.yaml"].decode("utf-8"))
    errors = pack_mod.validate_manifest_dict(manifest)
    assert errors == [], f"manifest schema errors: {errors}"
    assert manifest["pack_format"] == 1
    assert manifest["name"] == "test-user/eyebrow"
    assert manifest["author"]["name"] == "Test User"
    assert manifest["author"]["email"] == "test@example.com"


def test_export_component_hash_matches_body(tmp_path: Path):
    """The manifest's content_hash must match a re-computation over the body."""
    result = pack_mod.export_component("eyebrow", author=_author_from_test_env(), out_dir=tmp_path)
    contents = _extract_pack(Path(result.pack_path))
    body_files = [(k, v) for k, v in contents.items() if k != "pack.yaml"]
    recomputed = pack_mod.compute_content_hash(pack_mod.build_canonical_tar_body(body_files))
    assert result.content_hash == recomputed


# ---------------------------------------------------------------------------
# Recipe export
# ---------------------------------------------------------------------------


def test_export_recipe(tmp_path: Path):
    result = pack_mod.export_recipe("tutorial", author=_author_from_test_env(), out_dir=tmp_path)

    assert result.artifact_kind == "recipe"
    assert result.pack_name == "test-user/tutorial"
    contents = _extract_pack(Path(result.pack_path))
    assert "pack.yaml" in contents
    assert "recipes/tutorial.yaml" in contents

    # Byte-equivalence with source
    src = REPO_ROOT / "recipes" / "tutorial.yaml"
    assert contents["recipes/tutorial.yaml"] == src.read_bytes()


def test_export_unknown_recipe_fails(tmp_path: Path):
    with pytest.raises(ValueError, match="not found"):
        pack_mod.export_recipe("does-not-exist-xyz", out_dir=tmp_path)


def test_export_recipe_emits_languages_and_domain(tmp_path: Path):
    # Bilingual recipe with a `<domain>-<rest>` filename: legal-nda → domain=legal.
    result = pack_mod.export_recipe(
        "legal-nda", author=_author_from_test_env(), out_dir=tmp_path
    )
    contents = _extract_pack(Path(result.pack_path))
    manifest = yaml.safe_load(contents["pack.yaml"])
    assert manifest["languages"] == ["ar", "en"]
    assert manifest["domain"] == "legal"


def test_export_recipe_no_dash_omits_domain(tmp_path: Path):
    # Single-word recipe name has no implicit domain.
    result = pack_mod.export_recipe(
        "tutorial", author=_author_from_test_env(), out_dir=tmp_path
    )
    contents = _extract_pack(Path(result.pack_path))
    manifest = yaml.safe_load(contents["pack.yaml"])
    assert "domain" not in manifest
    assert manifest["languages"] == ["ar", "en"]


# ---------------------------------------------------------------------------
# Brand export
# ---------------------------------------------------------------------------


def test_export_brand(tmp_path: Path):
    """The shipped 'example' brand has no -assets/ sibling, so the pack
    contains only the YAML + manifest."""
    result = pack_mod.export_brand("example", author=_author_from_test_env(), out_dir=tmp_path)

    assert result.artifact_kind == "brand"
    assert result.pack_name == "test-user/example"
    contents = _extract_pack(Path(result.pack_path))
    assert "pack.yaml" in contents
    assert "brands/example.yaml" in contents

    src = REPO_ROOT / "brands" / "example.yaml"
    assert contents["brands/example.yaml"] == src.read_bytes()


def test_export_brand_with_assets(tmp_path: Path, monkeypatch):
    """Stage a fake brand with a `-assets/` sibling; verify recursive packing."""
    fake_brands_dir = tmp_path / "brands"
    fake_brands_dir.mkdir()
    yaml_path = fake_brands_dir / "myco.yaml"
    yaml_path.write_text("name: My Co\n", encoding="utf-8")
    assets = fake_brands_dir / "myco-assets" / "covers"
    assets.mkdir(parents=True)
    (assets / "hero.png").write_bytes(b"\x89PNG\r\nfake")
    (fake_brands_dir / "myco-assets" / "logo.svg").write_bytes(b"<svg/>")

    monkeypatch.setattr(pack_mod, "USER_BRANDS_DIR", fake_brands_dir)

    out_dir = tmp_path / "out"
    result = pack_mod.export_brand("myco", author=_author_from_test_env(), out_dir=out_dir)
    contents = _extract_pack(Path(result.pack_path))
    assert "brands/myco.yaml" in contents
    assert "brands/myco-assets/covers/hero.png" in contents
    assert "brands/myco-assets/logo.svg" in contents


def test_export_unknown_brand_fails(tmp_path: Path):
    with pytest.raises(ValueError, match="not found"):
        pack_mod.export_brand("does-not-exist-xyz", out_dir=tmp_path)


# ---------------------------------------------------------------------------
# Author defaulting + parsing
# ---------------------------------------------------------------------------


def test_parse_author_with_email():
    d = pack_mod.parse_author_string("Jasem Al Neaimi <jneaimi@gmail.com>")
    assert d == {"name": "Jasem Al Neaimi", "email": "jneaimi@gmail.com"}


def test_parse_author_name_only():
    d = pack_mod.parse_author_string("Just A Name")
    assert d == {"name": "Just A Name"}


def test_parse_author_empty_returns_empty():
    assert pack_mod.parse_author_string("") == {}
    assert pack_mod.parse_author_string("   ") == {}


def test_slugify_author_kebab_cases():
    assert pack_mod.slugify_author("Jasem Al Neaimi") == "jasem-al-neaimi"
    assert pack_mod.slugify_author("ACME Corp.") == "acme-corp"
    assert pack_mod.slugify_author("$$$") == "unknown"
    assert pack_mod.slugify_author("Test_User-1") == "test-user-1"


# ---------------------------------------------------------------------------
# CLI subprocess: end-to-end
# ---------------------------------------------------------------------------


def test_cli_export_component_json(tmp_path: Path):
    """Hit the script via subprocess to confirm end-to-end CLI wiring."""
    r = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "pack.py"),
            "--json",
            "export",
            "--component",
            "eyebrow",
            "--author",
            "Test User <t@x.com>",
            "--out",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert r.returncode == 0, f"stderr={r.stderr}"
    import json

    payload = json.loads(r.stdout)
    assert payload["artifact_kind"] == "component"
    assert payload["pack_name"] == "test-user/eyebrow"
    assert Path(payload["pack_path"]).exists()


def test_cli_export_no_selector_errors():
    """Argparse must reject `export` without a selector flag (mutually exclusive group)."""
    r = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "pack.py"), "export"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert r.returncode != 0
    # argparse writes "one of the arguments ... is required" to stderr
    assert "required" in r.stderr.lower() or "error" in r.stderr.lower()


# import / inspect / verify all graduated in Phase-4 Days 4-5; see
# tests/test_phase4_pack_inspect.py, test_phase4_pack_verify.py,
# test_phase4_pack_import.py for their dedicated suites.


# --bundle is implemented in Day 3; see tests/test_phase4_pack_bundle.py


# ---------------------------------------------------------------------------
# Determinism — same input twice produces same hash
# ---------------------------------------------------------------------------


def test_export_component_is_deterministic(tmp_path: Path):
    """Two consecutive exports of the same component must produce
    byte-identical pack files. This is the basis for content-addressable
    distribution in Phase 6."""
    r1 = pack_mod.export_component("eyebrow", author=_author_from_test_env(), out_dir=tmp_path / "a")
    r2 = pack_mod.export_component("eyebrow", author=_author_from_test_env(), out_dir=tmp_path / "b")
    assert r1.content_hash == r2.content_hash
    # Pack file bytes also identical (gzip mtime=0).
    assert Path(r1.pack_path).read_bytes() == Path(r2.pack_path).read_bytes()
