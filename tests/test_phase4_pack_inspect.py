"""Phase-4 Day 4 — `katib pack inspect`.

Inspect is read-only — it dumps the manifest + arcname tree. It must
work even on slightly-broken packs (corrupt body, schema-invalid
manifest) so the operator can see what's wrong with a pack they were
sent. Hard-broken packs (not gzip, missing pack.yaml) raise.
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

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from core import pack as pack_mod  # noqa: E402


def _author() -> dict[str, str]:
    return {"name": "Test User", "email": "test@example.com"}


# ---------------------------------------------------------------------------
# Inspect — happy path
# ---------------------------------------------------------------------------


def test_inspect_component_pack(tmp_path):
    res = pack_mod.export_component("eyebrow", author=_author(), out_dir=tmp_path)
    insp = pack_mod.inspect_pack(Path(res.pack_path))

    assert insp.name == "test-user/eyebrow"
    assert insp.pack_format == 1
    assert insp.content_hash_claim.startswith("sha256:")
    assert insp.author == {"name": "Test User", "email": "test@example.com"}
    # The component file shows up in the files list
    assert any(f.startswith("components/primitives/eyebrow/") for f in insp.files)
    # Contents has the component spec
    assert insp.contents["components"][0]["name"] == "eyebrow"


def test_inspect_recipe_pack(tmp_path):
    res = pack_mod.export_recipe("tutorial", author=_author(), out_dir=tmp_path)
    insp = pack_mod.inspect_pack(Path(res.pack_path))

    assert insp.name == "test-user/tutorial"
    assert insp.contents["recipes"][0]["name"] == "tutorial"
    assert "recipes/tutorial.yaml" in insp.files


def test_inspect_brand_pack(tmp_path):
    res = pack_mod.export_brand("example", author=_author(), out_dir=tmp_path)
    insp = pack_mod.inspect_pack(Path(res.pack_path))

    assert insp.name == "test-user/example"
    assert insp.contents["brands"][0]["name"] == "example"


# ---------------------------------------------------------------------------
# Inspect — error paths
# ---------------------------------------------------------------------------


def test_inspect_nonexistent_path_raises(tmp_path):
    with pytest.raises(ValueError, match="not found"):
        pack_mod.inspect_pack(tmp_path / "nope.katib-pack")


def test_inspect_non_gzip_raises(tmp_path):
    p = tmp_path / "not-a-pack.katib-pack"
    p.write_bytes(b"this is not a gzip stream")
    with pytest.raises(ValueError, match="not a valid gzipped tar"):
        pack_mod.inspect_pack(p)


def test_inspect_tar_without_manifest_raises(tmp_path):
    """A gzipped tar that doesn't contain pack.yaml is structurally invalid."""
    p = tmp_path / "no-manifest.katib-pack"
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w") as tar:
        info = tarfile.TarInfo(name="some-other-file.txt")
        data = b"hello"
        info.size = len(data)
        tar.addfile(info, io.BytesIO(data))
    with open(p, "wb") as f:
        with gzip.GzipFile(fileobj=f, mode="wb", mtime=0) as gz:
            gz.write(raw.getvalue())
    with pytest.raises(ValueError, match="missing"):
        pack_mod.inspect_pack(p)


def test_inspect_tolerates_schema_invalid_manifest(tmp_path):
    """Schema validation is verify's job. Inspect should still report
    what it sees, so the user can debug."""
    # Build a pack with a manifest that has an unknown extra key.
    p = tmp_path / "weird.katib-pack"
    raw = io.BytesIO()
    bad_manifest = "pack_format: 1\nname: x/y\nversion: 1.0.0\nfuture_field: oops\n"
    with tarfile.open(fileobj=raw, mode="w") as tar:
        info = tarfile.TarInfo(name="pack.yaml")
        data = bad_manifest.encode("utf-8")
        info.size = len(data)
        tar.addfile(info, io.BytesIO(data))
    with open(p, "wb") as f:
        with gzip.GzipFile(fileobj=f, mode="wb", mtime=0) as gz:
            gz.write(raw.getvalue())

    # Inspect should succeed (read-only — no schema check).
    insp = pack_mod.inspect_pack(p)
    assert insp.name == "x/y"
    assert insp.version == "1.0.0"


# ---------------------------------------------------------------------------
# CLI subprocess
# ---------------------------------------------------------------------------


def test_cli_inspect_human(tmp_path):
    res = pack_mod.export_recipe("tutorial", author=_author(), out_dir=tmp_path)
    r = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "pack.py"), "inspect", res.pack_path],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert r.returncode == 0
    assert "test-user/tutorial" in r.stdout
    assert "recipes/tutorial.yaml" in r.stdout


def test_cli_inspect_json(tmp_path):
    res = pack_mod.export_component("eyebrow", author=_author(), out_dir=tmp_path)
    r = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "pack.py"),
            "--json",
            "inspect",
            res.pack_path,
        ],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert r.returncode == 0
    payload = json.loads(r.stdout)
    assert payload["name"] == "test-user/eyebrow"
    assert payload["pack_format"] == 1
    assert "files" in payload
