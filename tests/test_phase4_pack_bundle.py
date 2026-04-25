"""Phase-4 Day 3 — `katib pack export --bundle <recipe>` with dep walk.

A bundle pack is the natural unit for sharing a recipe that depends
on user-tier components: one tarball, self-contained for everything
user-tier, strict declarations for everything bundled.

Test fixtures stage user-tier components and recipes in `tmp_path`
via the `isolated_user_dirs` fixture — this avoids touching
`~/.katib/` and keeps tests deterministic.
"""
from __future__ import annotations

import gzip
import io
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
    with open(pack_path, "rb") as f:
        with gzip.GzipFile(fileobj=f) as gz:
            with tarfile.open(fileobj=io.BytesIO(gz.read()), mode="r") as tar:
                return {info.name: tar.extractfile(info).read() for info in tar.getmembers()}


def _author() -> dict[str, str]:
    return {"name": "Test User", "email": "test@example.com"}


def _scaffold_user_component(
    user_components_dir: Path, name: str, tier: str = "primitive"
) -> Path:
    """Drop a minimal user-tier component on disk.

    Just enough files for the file-collector to find them — not full
    enough to render. Good for testing pack-shape mechanics.
    """
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


def _scaffold_user_recipe(
    user_recipes_dir: Path, name: str, sections: list[dict]
) -> Path:
    rpath = user_recipes_dir / f"{name}.yaml"
    rpath.write_text(
        yaml.safe_dump(
            {
                "name": name,
                "version": "1.0.0",
                "namespace": "user",
                "languages": ["en"],
                "description": "test recipe for bundle export",
                "sections": sections,
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    return rpath


# ---------------------------------------------------------------------------
# Component classification
# ---------------------------------------------------------------------------


def test_classify_known_bundled_component():
    """Sanity: a real bundled component classifies as 'bundled'."""
    assert pack_mod._classify_component("module") == "bundled"


def test_classify_user_component(isolated_user_dirs, tmp_path):
    user_components = isolated_user_dirs / "components"
    _scaffold_user_component(user_components, "fake-widget", tier="primitive")
    assert pack_mod._classify_component("fake-widget") == "user"


def test_classify_unknown_component():
    assert pack_mod._classify_component("does-not-exist-xyz") is None


def test_user_shadows_bundled(isolated_user_dirs, tmp_path):
    """A user-tier component with the same name as a bundled one wins
    in classification — matches runtime resolver semantics."""
    user_components = isolated_user_dirs / "components"
    _scaffold_user_component(user_components, "module", tier="section")
    assert pack_mod._classify_component("module") == "user"


# ---------------------------------------------------------------------------
# Recipe ref extraction
# ---------------------------------------------------------------------------


def test_recipe_component_refs_dedupe(isolated_user_dirs):
    user_recipes = isolated_user_dirs / "recipes"
    _scaffold_user_recipe(
        user_recipes,
        "demo-recipe",
        [
            {"component": "module", "inputs": {"title": "A"}},
            {"component": "kv-list"},
            {"component": "module", "inputs": {"title": "B"}},  # repeat
        ],
    )
    refs = pack_mod._recipe_component_refs("demo-recipe")
    assert refs == ["module", "kv-list"]


def test_recipe_component_refs_missing_field_errors(isolated_user_dirs):
    user_recipes = isolated_user_dirs / "recipes"
    rpath = user_recipes / "broken.yaml"
    rpath.write_text(
        yaml.safe_dump(
            {
                "name": "broken",
                "version": "0.1.0",
                "namespace": "user",
                "languages": ["en"],
                "sections": [{"variant": "default"}],   # missing component:
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="section #0"):
        pack_mod._recipe_component_refs("broken")


# ---------------------------------------------------------------------------
# Bundle export — recipe with bundled-only deps
# ---------------------------------------------------------------------------


def test_bundle_recipe_with_bundled_only_deps(isolated_user_dirs, tmp_path):
    """A recipe referencing only bundled components packs the recipe
    alone and declares all refs in requires.bundled_components."""
    user_recipes = isolated_user_dirs / "recipes"
    _scaffold_user_recipe(
        user_recipes,
        "all-bundled",
        [
            {"component": "module", "inputs": {"title": "T", "body": "B"}},
            {"component": "kv-list", "inputs": {"items": []}},
        ],
    )

    out_dir = tmp_path / "out"
    result = pack_mod.export_bundle("all-bundled", author=_author(), out_dir=out_dir)

    assert result.artifact_kind == "bundle"
    assert result.pack_name == "test-user/all-bundled"

    contents = _extract_pack(Path(result.pack_path))
    # Only recipe + manifest in the pack body
    assert "recipes/all-bundled.yaml" in contents
    assert not any(k.startswith("components/") for k in contents)

    # Manifest correctly declares bundled deps
    manifest = yaml.safe_load(contents["pack.yaml"].decode("utf-8"))
    assert manifest["requires"]["bundled_components"] == ["module", "kv-list"]
    assert "components" not in manifest.get("contents", {})


# ---------------------------------------------------------------------------
# Bundle export — recipe with user-tier component deps
# ---------------------------------------------------------------------------


def test_bundle_recipe_with_user_components(isolated_user_dirs, tmp_path):
    """A recipe referencing user-tier components packs them in-band
    AND still declares the bundled deps separately."""
    user_components = isolated_user_dirs / "components"
    user_recipes = isolated_user_dirs / "recipes"
    _scaffold_user_component(user_components, "client-hero", tier="section")
    _scaffold_user_component(user_components, "client-stat", tier="primitive")
    _scaffold_user_recipe(
        user_recipes,
        "client-proposal",
        [
            {"component": "module", "inputs": {"title": "Intro", "body": "..."}},
            {"component": "client-hero"},
            {"component": "client-stat"},
            {"component": "kv-list"},
        ],
    )

    out_dir = tmp_path / "out"
    result = pack_mod.export_bundle("client-proposal", author=_author(), out_dir=out_dir)

    contents = _extract_pack(Path(result.pack_path))
    # User components are included in-band
    assert "components/sections/client-hero/component.yaml" in contents
    assert "components/sections/client-hero/en.html" in contents
    assert "components/primitives/client-stat/component.yaml" in contents
    # Recipe is included
    assert "recipes/client-proposal.yaml" in contents
    # Manifest declares user vs bundled correctly
    manifest = yaml.safe_load(contents["pack.yaml"].decode("utf-8"))
    user_names = {c["name"] for c in manifest["contents"]["components"]}
    bundled = manifest["requires"]["bundled_components"]
    assert user_names == {"client-hero", "client-stat"}
    assert set(bundled) == {"module", "kv-list"}


def test_bundle_files_match_source_bytes(isolated_user_dirs, tmp_path):
    """Round-trip discipline: every packed file matches the source byte-for-byte."""
    user_components = isolated_user_dirs / "components"
    user_recipes = isolated_user_dirs / "recipes"
    cdir = _scaffold_user_component(user_components, "fancy-block", tier="section")
    rpath = _scaffold_user_recipe(
        user_recipes,
        "uses-fancy",
        [{"component": "module"}, {"component": "fancy-block"}],
    )

    out_dir = tmp_path / "out"
    result = pack_mod.export_bundle("uses-fancy", author=_author(), out_dir=out_dir)
    contents = _extract_pack(Path(result.pack_path))

    assert contents["recipes/uses-fancy.yaml"] == rpath.read_bytes()
    assert contents["components/sections/fancy-block/component.yaml"] == (
        cdir / "component.yaml"
    ).read_bytes()
    assert contents["components/sections/fancy-block/en.html"] == (
        cdir / "en.html"
    ).read_bytes()


# ---------------------------------------------------------------------------
# Bundle with a brand
# ---------------------------------------------------------------------------


def test_bundle_with_user_tier_brand(isolated_user_dirs, tmp_path):
    """`--include-brand` for a user-tier brand packs the YAML +
    `<name>-assets/` recursively."""
    user_components = isolated_user_dirs / "components"
    user_recipes = isolated_user_dirs / "recipes"
    user_brands = isolated_user_dirs / "brands"
    user_brands.mkdir(exist_ok=True)
    (user_brands / "myco.yaml").write_text("name: My Co\n", encoding="utf-8")
    assets = user_brands / "myco-assets" / "covers"
    assets.mkdir(parents=True)
    (assets / "hero.png").write_bytes(b"fakepng")

    _scaffold_user_recipe(user_recipes, "branded", [{"component": "module"}])

    out_dir = tmp_path / "out"
    result = pack_mod.export_bundle(
        "branded",
        include_brand="myco",
        author=_author(),
        out_dir=out_dir,
    )

    contents = _extract_pack(Path(result.pack_path))
    assert "brands/myco.yaml" in contents
    assert "brands/myco-assets/covers/hero.png" in contents

    manifest = yaml.safe_load(contents["pack.yaml"].decode("utf-8"))
    assert manifest["contents"]["brands"] == [{"name": "myco"}]


def test_bundle_with_unknown_brand_errors(isolated_user_dirs, tmp_path):
    user_recipes = isolated_user_dirs / "recipes"
    _scaffold_user_recipe(user_recipes, "no-brand", [{"component": "module"}])

    with pytest.raises(ValueError, match="not found"):
        pack_mod.export_bundle(
            "no-brand",
            include_brand="does-not-exist-xyz",
            author=_author(),
            out_dir=tmp_path,
        )


# ---------------------------------------------------------------------------
# Error paths
# ---------------------------------------------------------------------------


def test_bundle_unknown_recipe_errors(tmp_path):
    with pytest.raises(ValueError, match="not found"):
        pack_mod.export_bundle("does-not-exist-xyz", out_dir=tmp_path)


def test_bundle_recipe_with_unresolvable_component(isolated_user_dirs, tmp_path):
    user_recipes = isolated_user_dirs / "recipes"
    _scaffold_user_recipe(
        user_recipes,
        "broken-deps",
        [
            {"component": "module"},
            {"component": "ghost-component-xyz"},   # doesn't exist
        ],
    )
    with pytest.raises(ValueError, match="unresolvable component"):
        pack_mod.export_bundle("broken-deps", out_dir=tmp_path)


# ---------------------------------------------------------------------------
# CLI subprocess
# ---------------------------------------------------------------------------


def test_cli_bundle_round_trip(isolated_user_dirs, tmp_path):
    """Hit the CLI through subprocess; confirm `--bundle` is wired."""
    import json
    import os
    import subprocess

    user_recipes = isolated_user_dirs / "recipes"
    _scaffold_user_recipe(user_recipes, "cli-bundle-test", [{"component": "module"}])

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
            "export",
            "--bundle",
            "cli-bundle-test",
            "--author",
            "Test User <t@x.com>",
            "--out",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
        env=env,
        timeout=15,
    )
    assert r.returncode == 0, f"stderr={r.stderr}"
    payload = json.loads(r.stdout)
    assert payload["artifact_kind"] == "bundle"
    assert payload["pack_name"] == "test-user/cli-bundle-test"


def test_cli_include_brand_without_bundle_rejected(tmp_path):
    """--include-brand makes no sense without --bundle; CLI must reject."""
    import subprocess

    r = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "pack.py"),
            "export",
            "--component",
            "eyebrow",
            "--include-brand",
            "example",
            "--out",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert r.returncode == 1
    combined = r.stderr + r.stdout
    assert "include-brand" in combined or "bundle" in combined


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------


def test_bundle_export_is_deterministic(isolated_user_dirs, tmp_path):
    user_recipes = isolated_user_dirs / "recipes"
    _scaffold_user_recipe(
        user_recipes, "stable-bundle", [{"component": "module"}, {"component": "kv-list"}]
    )

    r1 = pack_mod.export_bundle("stable-bundle", author=_author(), out_dir=tmp_path / "a")
    r2 = pack_mod.export_bundle("stable-bundle", author=_author(), out_dir=tmp_path / "b")
    assert r1.content_hash == r2.content_hash
    assert Path(r1.pack_path).read_bytes() == Path(r2.pack_path).read_bytes()
