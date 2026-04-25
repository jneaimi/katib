"""Phase-4 Day 6 — bundled-dependency check on import.

A pack can declare three classes of host requirement:
- requires.bundled_components — components that must ship with the host
- requires.bundled_brands — brands that must ship with the host
- requires.katib_min — minimum host Katib version

Import refuses cleanly with a named-missing-items message when any
of these aren't satisfied. This is the "this pack is from a future
host I don't yet support" gate.
"""
from __future__ import annotations

import gzip
import io
import json
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


def _rebuild_pack_with_manifest(src_path: Path, dest_path: Path, manifest: dict) -> None:
    """Re-pack `src_path` to `dest_path` with a swapped manifest.

    Recomputes the hash to keep the pack self-consistent except for
    the requires field — used to graft different `requires.*` blocks
    onto an otherwise-valid pack."""
    with open(src_path, "rb") as f:
        with gzip.GzipFile(fileobj=f) as gz:
            inner = gz.read()
    entries: dict[str, bytes] = {}
    with tarfile.open(fileobj=io.BytesIO(inner), mode="r") as tar:
        for info in tar.getmembers():
            entries[info.name] = tar.extractfile(info).read()

    body = [(k, v) for k, v in entries.items() if k != "pack.yaml"]
    manifest["content_hash"] = pack_mod.compute_content_hash(
        pack_mod.build_canonical_tar_body(body)
    )
    entries["pack.yaml"] = yaml.safe_dump(
        manifest, sort_keys=False, default_flow_style=False
    ).encode("utf-8")

    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w") as tar:
        for arcname in sorted(entries):
            data = entries[arcname]
            info = tarfile.TarInfo(name=arcname)
            info.size = len(data)
            info.mtime = 0
            info.mode = 0o644
            tar.addfile(info, io.BytesIO(data))
    with open(dest_path, "wb") as f:
        with gzip.GzipFile(fileobj=f, mode="wb", mtime=0) as gz:
            gz.write(raw.getvalue())


# ---------------------------------------------------------------------------
# Bundled-component dep
# ---------------------------------------------------------------------------


def test_bundled_component_check_pass(isolated_user_dirs, tmp_path):
    """A pack declaring `bundled_components: [module]` imports cleanly
    because module ships in the bundled tier."""
    user_recipes = isolated_user_dirs / "recipes"
    _scaffold_user_recipe(user_recipes, "needs-module", [{"component": "module"}])
    res = pack_mod.export_bundle("needs-module", author=_author(), out_dir=tmp_path / "out")

    # Confirm the manifest does have bundled_components: [module]
    insp = pack_mod.inspect_pack(Path(res.pack_path))
    assert insp.requires.get("bundled_components") == ["module"]

    # Wipe target so import doesn't collide
    (user_recipes / "needs-module.yaml").unlink()

    imp = pack_mod.import_pack(Path(res.pack_path), regenerate_capabilities=False)
    assert imp.audit_entries_added == 1


def test_bundled_component_check_missing_refused(isolated_user_dirs, tmp_path):
    """A pack declaring a non-existent bundled component is refused."""
    user_recipes = isolated_user_dirs / "recipes"
    _scaffold_user_recipe(user_recipes, "ghost-recipe", [{"component": "module"}])
    res = pack_mod.export_bundle("ghost-recipe", author=_author(), out_dir=tmp_path / "out")
    src = Path(res.pack_path)

    insp = pack_mod.inspect_pack(src)
    bad_manifest = {
        "pack_format": 1,
        "name": insp.name,
        "version": insp.version,
        "content_hash": insp.content_hash_claim,   # will be overwritten
        "contents": insp.contents,
        "requires": {"bundled_components": ["module", "ghost-component-xyz"]},
    }
    bad_path = tmp_path / "missing-dep.katib-pack"
    _rebuild_pack_with_manifest(src, bad_path, bad_manifest)

    # Wipe to avoid collision so we know the dep check is what fired
    (user_recipes / "ghost-recipe.yaml").unlink()

    with pytest.raises(ValueError, match="ghost-component-xyz"):
        pack_mod.import_pack(bad_path, regenerate_capabilities=False)


def test_bundled_brand_check_missing_refused(isolated_user_dirs, tmp_path):
    """Same gate for brands declared in requires.bundled_brands[]."""
    user_recipes = isolated_user_dirs / "recipes"
    _scaffold_user_recipe(user_recipes, "needs-brand", [{"component": "module"}])
    res = pack_mod.export_bundle("needs-brand", author=_author(), out_dir=tmp_path / "out")
    src = Path(res.pack_path)

    insp = pack_mod.inspect_pack(src)
    bad_manifest = {
        "pack_format": 1,
        "name": insp.name,
        "version": insp.version,
        "content_hash": insp.content_hash_claim,
        "contents": insp.contents,
        "requires": {"bundled_brands": ["does-not-exist"]},
    }
    bad_path = tmp_path / "missing-brand.katib-pack"
    _rebuild_pack_with_manifest(src, bad_path, bad_manifest)

    (user_recipes / "needs-brand.yaml").unlink()

    with pytest.raises(ValueError, match="does-not-exist"):
        pack_mod.import_pack(bad_path, regenerate_capabilities=False)


def test_bundled_brand_check_pass(isolated_user_dirs, tmp_path):
    """`example` brand ships with the host."""
    user_recipes = isolated_user_dirs / "recipes"
    _scaffold_user_recipe(user_recipes, "needs-example-brand", [{"component": "module"}])
    res = pack_mod.export_bundle(
        "needs-example-brand", author=_author(), out_dir=tmp_path / "out"
    )
    src = Path(res.pack_path)

    insp = pack_mod.inspect_pack(src)
    good_manifest = {
        "pack_format": 1,
        "name": insp.name,
        "version": insp.version,
        "content_hash": insp.content_hash_claim,
        "contents": insp.contents,
        "requires": {"bundled_brands": ["example"]},
    }
    good_path = tmp_path / "with-example-brand.katib-pack"
    _rebuild_pack_with_manifest(src, good_path, good_manifest)

    (user_recipes / "needs-example-brand.yaml").unlink()

    imp = pack_mod.import_pack(good_path, regenerate_capabilities=False)
    assert imp.audit_entries_added == 1


# ---------------------------------------------------------------------------
# katib_min
# ---------------------------------------------------------------------------


def test_katib_min_satisfied(isolated_user_dirs, tmp_path):
    """Host is 1.0.0-alpha.2; a pack requiring 0.1.0 should pass."""
    user_recipes = isolated_user_dirs / "recipes"
    _scaffold_user_recipe(user_recipes, "needs-old", [{"component": "module"}])
    res = pack_mod.export_bundle("needs-old", author=_author(), out_dir=tmp_path / "out")
    src = Path(res.pack_path)

    insp = pack_mod.inspect_pack(src)
    good_manifest = {
        "pack_format": 1,
        "name": insp.name,
        "version": insp.version,
        "content_hash": insp.content_hash_claim,
        "contents": insp.contents,
        "requires": {"katib_min": "0.1.0"},
    }
    good_path = tmp_path / "old-min.katib-pack"
    _rebuild_pack_with_manifest(src, good_path, good_manifest)

    (user_recipes / "needs-old.yaml").unlink()

    imp = pack_mod.import_pack(good_path, regenerate_capabilities=False)
    assert imp.audit_entries_added == 1


def test_katib_min_unsatisfied_refused(isolated_user_dirs, tmp_path):
    """A pack requiring katib_min=99.0.0 is refused on this host."""
    user_recipes = isolated_user_dirs / "recipes"
    _scaffold_user_recipe(user_recipes, "needs-future", [{"component": "module"}])
    res = pack_mod.export_bundle("needs-future", author=_author(), out_dir=tmp_path / "out")
    src = Path(res.pack_path)

    insp = pack_mod.inspect_pack(src)
    bad_manifest = {
        "pack_format": 1,
        "name": insp.name,
        "version": insp.version,
        "content_hash": insp.content_hash_claim,
        "contents": insp.contents,
        "requires": {"katib_min": "99.0.0"},
    }
    bad_path = tmp_path / "future-min.katib-pack"
    _rebuild_pack_with_manifest(src, bad_path, bad_manifest)

    (user_recipes / "needs-future.yaml").unlink()

    with pytest.raises(ValueError, match="99.0.0"):
        pack_mod.import_pack(bad_path, regenerate_capabilities=False)


# ---------------------------------------------------------------------------
# Helper exposure
# ---------------------------------------------------------------------------


def test_host_version_matches_package_json():
    pkg = json.loads((REPO_ROOT / "package.json").read_text(encoding="utf-8"))
    assert pack_mod._host_katib_version() == pkg["version"]


def test_check_bundled_deps_returns_empty_for_satisfied_manifest():
    manifest = {
        "requires": {
            "bundled_components": ["module", "kv-list"],   # both ship
            "katib_min": "0.1.0",
        }
    }
    assert pack_mod._check_bundled_deps(manifest) == []


def test_check_bundled_deps_lists_missing():
    manifest = {
        "requires": {
            "bundled_components": ["module", "ghost-a", "ghost-b"],
        }
    }
    errors = pack_mod._check_bundled_deps(manifest)
    assert len(errors) == 1
    msg = errors[0]
    assert "ghost-a" in msg and "ghost-b" in msg
