"""Phase-4 Day 6 — `katib pack import --dry-run`.

Dry-run runs every check (verify + dep + collision) and reports the
plan, but writes nothing to disk and adds no audit entries. Useful
for CI ("does this pack still install on a fresh host?") and human
pre-flight ("what is this pack about to do?").

Strict invariant: dry-run must not change the user tier in any way.
Tests verify this by snapshotting the directory tree before/after.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from core import pack as pack_mod  # noqa: E402


def _author() -> dict[str, str]:
    return {"name": "Test User", "email": "test@example.com"}


def _snapshot(root: Path) -> set[str]:
    """Return a set of relative paths under `root` (sorted, file-only).
    Used to confirm dry-run leaves the tier untouched."""
    if not root.exists():
        return set()
    return {str(p.relative_to(root)) for p in root.rglob("*") if p.is_file()}


# ---------------------------------------------------------------------------
# Happy dry-run
# ---------------------------------------------------------------------------


def test_dry_run_clean_tier_writes_nothing(isolated_user_dirs, tmp_path):
    res = pack_mod.export_component("eyebrow", author=_author(), out_dir=tmp_path)

    before_components = _snapshot(isolated_user_dirs / "components")
    before_recipes = _snapshot(isolated_user_dirs / "recipes")
    before_memory = _snapshot(isolated_user_dirs / "memory")

    imp = pack_mod.import_pack(
        Path(res.pack_path), dry_run=True, regenerate_capabilities=False
    )

    assert imp.dry_run is True
    assert imp.capabilities_regenerated is False
    # files_written reports the plan (not zero)
    assert len(imp.files_written) > 0
    # audit count reports what would have been added
    assert imp.audit_entries_added == 1   # one component

    # Disk is unchanged
    assert _snapshot(isolated_user_dirs / "components") == before_components
    assert _snapshot(isolated_user_dirs / "recipes") == before_recipes
    assert _snapshot(isolated_user_dirs / "memory") == before_memory


def test_dry_run_does_not_create_audit_files(isolated_user_dirs, tmp_path):
    """Audit JSONLs may be append-mode opened; dry-run must not even create them."""
    res = pack_mod.export_recipe("tutorial", author=_author(), out_dir=tmp_path)

    audit_components = isolated_user_dirs / "memory" / "component-audit.jsonl"
    audit_recipes = isolated_user_dirs / "memory" / "recipe-audit.jsonl"
    assert not audit_components.exists()
    assert not audit_recipes.exists()

    pack_mod.import_pack(
        Path(res.pack_path), dry_run=True, regenerate_capabilities=False
    )

    assert not audit_components.exists()
    assert not audit_recipes.exists()


# ---------------------------------------------------------------------------
# Dry-run still gates on safety checks
# ---------------------------------------------------------------------------


def test_dry_run_refused_on_collision_without_force(isolated_user_dirs, tmp_path):
    """Even dry-run respects the collision rule — better to refuse a
    plan you'd never actually run than mislead the operator."""
    res = pack_mod.export_component("eyebrow", author=_author(), out_dir=tmp_path)
    pack_mod.import_pack(Path(res.pack_path), regenerate_capabilities=False)

    with pytest.raises(ValueError, match="overwrite"):
        pack_mod.import_pack(
            Path(res.pack_path), dry_run=True, regenerate_capabilities=False
        )


def test_dry_run_with_force_justification_returns_plan(isolated_user_dirs, tmp_path):
    """Dry-run + --force --justification reports the plan (no writes)
    and the disk stays untouched."""
    res = pack_mod.export_component("eyebrow", author=_author(), out_dir=tmp_path)
    pack_mod.import_pack(Path(res.pack_path), regenerate_capabilities=False)

    snapshot_before = _snapshot(isolated_user_dirs / "components")
    audit_before = _snapshot(isolated_user_dirs / "memory")

    imp = pack_mod.import_pack(
        Path(res.pack_path),
        dry_run=True,
        force=True,
        justification="dry-run pre-flight",
        regenerate_capabilities=False,
    )
    assert imp.dry_run is True
    assert imp.force is True
    assert len(imp.collisions_resolved) > 0

    # Disk unchanged — no overwrite even though force is set
    assert _snapshot(isolated_user_dirs / "components") == snapshot_before
    assert _snapshot(isolated_user_dirs / "memory") == audit_before


def test_dry_run_refused_on_tampered_pack(isolated_user_dirs, tmp_path):
    """Verify gates even under dry-run. Sanity: dry-run should say
    'this pack is broken' before saying 'this is what would happen'."""
    import gzip
    import io
    import tarfile

    res = pack_mod.export_component("eyebrow", author=_author(), out_dir=tmp_path)
    src = Path(res.pack_path)

    insp = pack_mod.inspect_pack(src)
    bad_manifest = {
        "pack_format": 1,
        "name": insp.name,
        "version": insp.version,
        "content_hash": "sha256:" + "0" * 64,
        "contents": insp.contents,
        "requires": insp.requires,
    }
    bad_path = tmp_path / "tampered.katib-pack"
    with open(src, "rb") as f:
        with gzip.GzipFile(fileobj=f) as gz:
            inner = gz.read()
    entries: dict[str, bytes] = {}
    with tarfile.open(fileobj=io.BytesIO(inner), mode="r") as tar:
        for info in tar.getmembers():
            entries[info.name] = tar.extractfile(info).read()
    entries["pack.yaml"] = yaml.safe_dump(
        bad_manifest, sort_keys=False, default_flow_style=False
    ).encode("utf-8")
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w") as tar:
        for arc in sorted(entries):
            data = entries[arc]
            info = tarfile.TarInfo(name=arc)
            info.size = len(data)
            info.mtime = 0
            tar.addfile(info, io.BytesIO(data))
    with open(bad_path, "wb") as f:
        with gzip.GzipFile(fileobj=f, mode="wb", mtime=0) as gz:
            gz.write(raw.getvalue())

    with pytest.raises(ValueError, match="verification"):
        pack_mod.import_pack(bad_path, dry_run=True, regenerate_capabilities=False)


# ---------------------------------------------------------------------------
# CLI subprocess
# ---------------------------------------------------------------------------


def test_cli_dry_run_human_output(isolated_user_dirs, tmp_path):
    res = pack_mod.export_component("eyebrow", author=_author(), out_dir=tmp_path)

    env = os.environ.copy()
    env["KATIB_RECIPES_DIR"] = str(isolated_user_dirs / "recipes")
    env["KATIB_COMPONENTS_DIR"] = str(isolated_user_dirs / "components")
    env["KATIB_MEMORY_DIR"] = str(isolated_user_dirs / "memory")
    env["KATIB_BRANDS_DIR"] = str(isolated_user_dirs / "brands")

    r = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "pack.py"),
            "import",
            res.pack_path,
            "--dry-run",
        ],
        capture_output=True,
        text=True,
        env=env,
        timeout=60,
    )
    assert r.returncode == 0, f"stderr={r.stderr}\nstdout={r.stdout}"
    assert "would import" in r.stdout
    assert "Plan:" in r.stdout

    # Disk unchanged
    assert not (isolated_user_dirs / "components" / "primitives" / "eyebrow").exists()


def test_cli_dry_run_json(isolated_user_dirs, tmp_path):
    res = pack_mod.export_recipe("tutorial", author=_author(), out_dir=tmp_path)

    env = os.environ.copy()
    env["KATIB_RECIPES_DIR"] = str(isolated_user_dirs / "recipes")
    env["KATIB_COMPONENTS_DIR"] = str(isolated_user_dirs / "components")
    env["KATIB_MEMORY_DIR"] = str(isolated_user_dirs / "memory")
    env["KATIB_BRANDS_DIR"] = str(isolated_user_dirs / "brands")

    r = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "pack.py"),
            "--json",
            "import",
            res.pack_path,
            "--dry-run",
        ],
        capture_output=True,
        text=True,
        env=env,
        timeout=60,
    )
    assert r.returncode == 0
    payload = json.loads(r.stdout)
    assert payload["dry_run"] is True
    assert payload["capabilities_regenerated"] is False
    assert payload["audit_entries_added"] == 1   # tutorial recipe
    assert isinstance(payload["files_written"], list)
