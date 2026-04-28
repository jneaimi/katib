"""Phase-4 Day 5 — `katib pack import`.

Import is the receiving side of the round-trip. It must:
- gate on verify_pack() (no broken packs into the user tier)
- refuse collisions without --force --justification
- write files atomically into ~/.katib/
- append audit entries with action: 'imported' and provenance fields
- be safe to re-run on a fresh tier (idempotent — without --force)

Tests use the `isolated_user_dirs` fixture so writes go to tmp_path
and ~/.katib/ stays untouched.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from core import pack as pack_mod  # noqa: E402


def _author() -> dict[str, str]:
    return {"name": "Test User", "email": "test@example.com"}


def _scaffold_user_component(user_components_dir: Path, name: str, tier: str = "primitive") -> Path:
    tier_dir = {"primitive": "primitives", "section": "sections", "cover": "covers"}[tier]
    cdir = user_components_dir / tier_dir / name
    cdir.mkdir(parents=True, exist_ok=True)
    (cdir / "component.yaml").write_text(
        yaml.safe_dump(
            {
                "name": name,
                "tier": tier,
                "version": "0.1.0",
                "namespace": "user",
                "languages": ["en"],
                "description": f"test component {name}",
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    (cdir / "en.html").write_text(f"<div>{name}</div>", encoding="utf-8")
    (cdir / "styles.css").write_text(f"/* {name} */\n", encoding="utf-8")
    (cdir / "README.md").write_text(f"# {name}\n", encoding="utf-8")
    return cdir


def _scaffold_user_recipe(user_recipes_dir: Path, name: str, sections: list[dict]) -> Path:
    rpath = user_recipes_dir / f"{name}.yaml"
    rpath.write_text(
        yaml.safe_dump(
            {
                "name": name,
                "version": "1.0.0",
                "namespace": "user",
                "languages": ["en"],
                "description": "test recipe",
                "sections": sections,
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    return rpath


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


def test_import_component_into_clean_tier(isolated_user_dirs, tmp_path):
    """Pack a fresh component, then import into an empty tier."""
    # Build a pack from the bundled tier (it doesn't matter where it
    # came from — what matters is the import target is empty).
    res = pack_mod.export_component("eyebrow", author=_author(), out_dir=tmp_path)

    # Import goes to the isolated user tier (per fixture).
    imp = pack_mod.import_pack(
        Path(res.pack_path), regenerate_capabilities=False
    )
    assert imp.pack_name == "test-user/eyebrow"
    assert imp.audit_entries_added == 1
    assert not imp.force

    # The component now lives in the user tier.
    assert pack_mod._classify_component("eyebrow") == "user"

    # Audit entry has the right shape.
    audit_path = isolated_user_dirs / "memory" / "component-audit.jsonl"
    rows = [json.loads(line) for line in audit_path.read_text().splitlines()]
    assert len(rows) == 1
    row = rows[0]
    assert row["component"] == "eyebrow"
    assert row["tier"] == "primitive"
    assert row["namespace"] == "user"
    assert row["action"] == "imported"
    assert row["source_pack"] == "test-user/eyebrow"
    assert row["source_pack_version"]
    assert row["source_hash"].startswith("sha256:")
    assert "at" in row


def test_import_recipe_into_clean_tier(isolated_user_dirs, tmp_path):
    res = pack_mod.export_recipe("tutorial", author=_author(), out_dir=tmp_path)
    imp = pack_mod.import_pack(Path(res.pack_path), regenerate_capabilities=False)

    target = isolated_user_dirs / "recipes" / "tutorial.yaml"
    assert target.exists()
    assert imp.audit_entries_added == 1

    # Recipe audit shape
    audit_path = isolated_user_dirs / "memory" / "recipe-audit.jsonl"
    rows = [json.loads(line) for line in audit_path.read_text().splitlines()]
    assert rows[0]["recipe"] == "tutorial"
    assert rows[0]["action"] == "imported"


def test_import_skips_marketplace_previews(isolated_user_dirs, tmp_path):
    """A `.katib-pack` produced with --with-previews carries
    `previews/<name>.<lang>.html` arcnames intended for the marketplace
    publisher. Local import must silently skip them — they don't belong
    in the user tier and an unrecognized-prefix raise would block any
    `katib pack install` of a Slice-B-era pack."""
    res = pack_mod.export_recipe(
        "tutorial", author=_author(), out_dir=tmp_path, with_previews=True
    )
    # Sanity: the pack actually contains previews
    import tarfile
    with tarfile.open(res.pack_path, "r:gz") as tf:
        names = tf.getnames()
    assert any(n.startswith("previews/") for n in names), (
        "fixture precondition: pack must contain previews"
    )

    imp = pack_mod.import_pack(Path(res.pack_path), regenerate_capabilities=False)

    # Recipe lands; no previews/ directory is created in the user tier
    assert (isolated_user_dirs / "recipes" / "tutorial.yaml").exists()
    assert not (isolated_user_dirs / "previews").exists()
    assert imp.audit_entries_added == 1


def test_import_bundle_writes_recipe_and_components(isolated_user_dirs, tmp_path):
    """A bundle pack drops a recipe + its custom components into the
    user tier in one go."""
    user_components = isolated_user_dirs / "components"
    user_recipes = isolated_user_dirs / "recipes"
    _scaffold_user_component(user_components, "client-hero", tier="section")
    _scaffold_user_recipe(
        user_recipes,
        "imp-bundle",
        [{"component": "module"}, {"component": "client-hero"}],
    )

    out_dir = tmp_path / "out"
    res = pack_mod.export_bundle("imp-bundle", author=_author(), out_dir=out_dir)

    # Now wipe the user tier and re-import the pack — should restore
    # the same state.
    import shutil
    shutil.rmtree(user_components / "sections" / "client-hero")
    (user_recipes / "imp-bundle.yaml").unlink()
    assert not (user_recipes / "imp-bundle.yaml").exists()

    imp = pack_mod.import_pack(Path(res.pack_path), regenerate_capabilities=False)
    assert (user_recipes / "imp-bundle.yaml").exists()
    assert (user_components / "sections" / "client-hero" / "component.yaml").exists()
    # 1 component + 1 recipe = 2 audit entries
    assert imp.audit_entries_added == 2


# ---------------------------------------------------------------------------
# Collision refusal
# ---------------------------------------------------------------------------


def test_import_collision_refused_without_force(isolated_user_dirs, tmp_path):
    """If the user tier already has the artifact, refuse without --force."""
    res = pack_mod.export_component("eyebrow", author=_author(), out_dir=tmp_path)
    # First import — clean.
    pack_mod.import_pack(Path(res.pack_path), regenerate_capabilities=False)

    # Second import — collision.
    with pytest.raises(ValueError, match="overwrite"):
        pack_mod.import_pack(Path(res.pack_path), regenerate_capabilities=False)


def test_import_force_without_justification_refused(isolated_user_dirs, tmp_path):
    res = pack_mod.export_component("eyebrow", author=_author(), out_dir=tmp_path)
    pack_mod.import_pack(Path(res.pack_path), regenerate_capabilities=False)

    with pytest.raises(ValueError, match="justification"):
        pack_mod.import_pack(
            Path(res.pack_path), force=True, regenerate_capabilities=False
        )


def test_import_force_with_justification_overwrites(isolated_user_dirs, tmp_path):
    """--force --justification proceeds and records both in the audit."""
    res = pack_mod.export_component("eyebrow", author=_author(), out_dir=tmp_path)
    pack_mod.import_pack(Path(res.pack_path), regenerate_capabilities=False)

    imp = pack_mod.import_pack(
        Path(res.pack_path),
        force=True,
        justification="re-import to test overwrite path",
        regenerate_capabilities=False,
    )
    assert imp.force is True
    assert imp.justification == "re-import to test overwrite path"
    assert len(imp.collisions_resolved) > 0

    # Latest audit row records the force + justification.
    audit_path = isolated_user_dirs / "memory" / "component-audit.jsonl"
    rows = [json.loads(line) for line in audit_path.read_text().splitlines()]
    last = rows[-1]
    assert last["force"] is True
    assert last["justification"] == "re-import to test overwrite path"


# ---------------------------------------------------------------------------
# Verify gating
# ---------------------------------------------------------------------------


def test_import_refuses_tampered_pack(isolated_user_dirs, tmp_path):
    """A pack with mismatched content_hash is refused at the verify gate."""
    import gzip
    import io
    import tarfile

    res = pack_mod.export_component("eyebrow", author=_author(), out_dir=tmp_path)
    src = Path(res.pack_path)

    # Build a bad pack with a bogus claimed hash.
    insp = pack_mod.inspect_pack(src)
    bad_manifest = {
        "pack_format": 1,
        "name": insp.name,
        "version": insp.version,
        "content_hash": "sha256:" + "0" * 64,
        "contents": insp.contents,
        "requires": insp.requires,
    }
    bad_path = tmp_path / "bad.katib-pack"
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
        for name in sorted(entries):
            data = entries[name]
            info = tarfile.TarInfo(name=name)
            info.size = len(data)
            info.mtime = 0
            info.mode = 0o644
            tar.addfile(info, io.BytesIO(data))
    with open(bad_path, "wb") as f:
        with gzip.GzipFile(fileobj=f, mode="wb", mtime=0) as gz:
            gz.write(raw.getvalue())

    with pytest.raises(ValueError, match="verification"):
        pack_mod.import_pack(bad_path, regenerate_capabilities=False)

    # Nothing was written.
    target = isolated_user_dirs / "components" / "primitives" / "eyebrow"
    assert not target.exists()


def test_import_refuses_nonexistent_path(isolated_user_dirs, tmp_path):
    with pytest.raises(ValueError, match="not found"):
        pack_mod.import_pack(tmp_path / "no.katib-pack", regenerate_capabilities=False)


# ---------------------------------------------------------------------------
# Audit shape — round-trip with build gate
# ---------------------------------------------------------------------------


def test_imported_component_passes_build_audit_gate(isolated_user_dirs, tmp_path):
    """The audit-entry shape we write must satisfy build.py's audit gate.
    `_audit_entries()` reads `component` field per row — confirm match."""
    res = pack_mod.export_component("eyebrow", author=_author(), out_dir=tmp_path)
    pack_mod.import_pack(Path(res.pack_path), regenerate_capabilities=False)

    import scripts.build as build_mod

    audited = build_mod._audit_entries()
    # The user-tier audit file is read in addition to bundled.
    assert "eyebrow" in audited


# ---------------------------------------------------------------------------
# CLI subprocess
# ---------------------------------------------------------------------------


def test_cli_import_human_output(isolated_user_dirs, tmp_path):
    import os
    import subprocess

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
        ],
        capture_output=True,
        text=True,
        env=env,
        timeout=60,
    )
    assert r.returncode == 0, f"stderr={r.stderr}\nstdout={r.stdout}"
    assert "imported" in r.stdout
    assert "test-user/eyebrow" in r.stdout


# --dry-run graduated in Phase-4 Day 6 — see tests/test_phase4_pack_dry_run.py
