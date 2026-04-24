"""Phase-4 Day-4: brand cover presets — read path + save path.

Covers:
    - `covers:` map validation in load_brand (required fields, path resolution, name charset)
    - `brand-preset` meta-source resolver in compose (lookup, fallback errors)
    - `save_cover_preset` — file copy, yaml round-trip with ruamel, --force guard
    - build.py CLI integration: --save-cover-preset requires --brand, writes preset, refuses overwrite
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
import yaml
from PIL import Image

from core.brand_presets import (
    SavePresetError,
    find_cover_image,
    save_cover_preset,
)
from core.compose import ComposeError, compose
from core.tokens import TokenError, load_brand

REPO_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------- helpers


def _tiny_png(p: Path) -> Path:
    p.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (40, 40), color=(180, 120, 60)).save(p)
    return p


def _write_brand(
    tmp_path: Path,
    brand_name: str,
    *,
    covers: dict | None = None,
) -> Path:
    brand_path = tmp_path / f"{brand_name}.yaml"
    data: dict = {
        "name": "Test Brand",
        "colors": {"accent": "#112233"},
    }
    if covers is not None:
        data["covers"] = covers
    brand_path.write_text(yaml.safe_dump(data), encoding="utf-8")
    return brand_path


# ---------------------------------------------------------------- load_brand: covers validation


def test_covers_map_resolves_relative_user_file_path(tmp_path):
    img = _tiny_png(tmp_path / "acme-assets" / "covers" / "launch.png")
    brand = _write_brand(
        tmp_path,
        "acme",
        covers={
            "launch": {
                "source": "user-file",
                "path": "acme-assets/covers/launch.png",
                "alt_text": "Launch cover",
            }
        },
    )
    data = load_brand(str(brand))
    resolved = data["covers"]["launch"]["path"]
    assert Path(resolved).is_absolute()
    assert Path(resolved) == img.resolve()


def test_covers_map_absolute_path_passes_through(tmp_path):
    img = _tiny_png(tmp_path / "somewhere" / "shot.png")
    brand = _write_brand(
        tmp_path,
        "abs",
        covers={"shot": {"source": "user-file", "path": str(img)}},
    )
    data = load_brand(str(brand))
    assert data["covers"]["shot"]["path"] == str(img.resolve())


def test_covers_missing_file_fails_loud(tmp_path):
    brand = _write_brand(
        tmp_path,
        "bad",
        covers={"ghost": {"source": "user-file", "path": "no/such/file.png"}},
    )
    with pytest.raises(TokenError, match="not found"):
        load_brand(str(brand))


def test_covers_rejects_unknown_source(tmp_path):
    brand = _write_brand(
        tmp_path,
        "bad",
        covers={"x": {"source": "dall-e", "path": "x.png"}},
    )
    with pytest.raises(TokenError, match="source must be one of"):
        load_brand(str(brand))


def test_covers_rejects_bad_name_charset(tmp_path):
    img = _tiny_png(tmp_path / "ok.png")
    brand = _write_brand(
        tmp_path,
        "bad",
        covers={"BadName!": {"source": "user-file", "path": str(img)}},
    )
    with pytest.raises(TokenError, match="must match"):
        load_brand(str(brand))


def test_covers_rejects_bad_extension(tmp_path):
    weird = tmp_path / "x.txt"
    weird.write_text("nope")
    brand = _write_brand(
        tmp_path,
        "bad",
        covers={"x": {"source": "user-file", "path": str(weird)}},
    )
    with pytest.raises(TokenError, match="not in"):
        load_brand(str(brand))


def test_covers_inline_svg_requires_svg_field(tmp_path):
    brand = _write_brand(
        tmp_path,
        "sv",
        covers={"x": {"source": "inline-svg"}},
    )
    with pytest.raises(TokenError, match="svg is required"):
        load_brand(str(brand))


def test_covers_optional_when_absent(tmp_path):
    brand = _write_brand(tmp_path, "plain")
    data = load_brand(str(brand))
    assert "covers" not in data or not data.get("covers")


# ---------------------------------------------------------------- compose: brand-preset resolver


def _recipe_with_cover(
    tmp_path: Path,
    image_spec: str,
) -> Path:
    rfile = tmp_path / "r.yaml"
    rfile.write_text(
        "name: preset-test\n"
        "version: 0.1.0\n"
        "namespace: katib\n"
        "languages: [en]\n"
        "sections:\n"
        "  - component: cover-page\n"
        "    variant: image-background\n"
        "    inputs:\n"
        "      eyebrow: Test\n"
        "      title: Preset Cover Smoke\n"
        "      subtitle: Validating brand-preset lookup.\n"
        "      reference_code: TST-001\n"
        f"      image: {image_spec}\n"
    )
    return rfile


def test_brand_preset_resolves_to_stored_user_file(tmp_path, monkeypatch):
    img = _tiny_png(tmp_path / "acme-assets" / "covers" / "main.png")
    brand = _write_brand(
        tmp_path,
        "acme",
        covers={
            "main": {
                "source": "user-file",
                "path": "acme-assets/covers/main.png",
                "alt_text": "Main cover",
            }
        },
    )
    monkeypatch.setenv("KATIB_BRANDS_DIR", str(tmp_path))
    rfile = _recipe_with_cover(
        tmp_path,
        "{source: brand-preset, name: main}",
    )
    html, meta = compose(str(rfile), "en", brand="acme")
    assert "katib-cover" in html
    covers_hits = [
        r for r in meta["resolved_images"] if r["component"] == "cover-page"
    ]
    assert len(covers_hits) == 1
    assert covers_hits[0]["source"] == "user-file"
    assert Path(covers_hits[0]["resolved_path"]).exists()


def test_brand_preset_without_brand_errors(tmp_path):
    rfile = _recipe_with_cover(
        tmp_path, "{source: brand-preset, name: whatever}"
    )
    with pytest.raises(ComposeError, match="brand-preset"):
        compose(str(rfile), "en")


def test_brand_preset_unknown_name_errors(tmp_path, monkeypatch):
    img = _tiny_png(tmp_path / "e-assets" / "covers" / "real.png")
    brand = _write_brand(
        tmp_path,
        "e",
        covers={"real": {"source": "user-file", "path": "e-assets/covers/real.png"}},
    )
    monkeypatch.setenv("KATIB_BRANDS_DIR", str(tmp_path))
    rfile = _recipe_with_cover(
        tmp_path, "{source: brand-preset, name: ghost}"
    )
    with pytest.raises(ComposeError, match="not defined"):
        compose(str(rfile), "en", brand="e")


def test_brand_preset_without_brand_covers_errors(tmp_path, monkeypatch):
    """Brand has no `covers:` at all — should error with a helpful message."""
    brand = _write_brand(tmp_path, "empty")
    monkeypatch.setenv("KATIB_BRANDS_DIR", str(tmp_path))
    rfile = _recipe_with_cover(
        tmp_path, "{source: brand-preset, name: ghost}"
    )
    with pytest.raises(ComposeError, match="no brand with cover presets"):
        compose(str(rfile), "en", brand="empty")


def test_brand_preset_alt_text_overrides_stored_alt(tmp_path, monkeypatch):
    """Recipe-level alt_text on a brand-preset spec wins over the brand's stored alt.
    The cover-page template currently hardcodes alt="" on the background image,
    so we verify through the resolved_images meta (which downstream tooling like
    save-preset reads) rather than the HTML output."""
    img = _tiny_png(tmp_path / "x-assets" / "covers" / "a.png")
    brand = _write_brand(
        tmp_path,
        "x",
        covers={
            "a": {
                "source": "user-file",
                "path": "x-assets/covers/a.png",
                "alt_text": "stored alt",
            }
        },
    )
    monkeypatch.setenv("KATIB_BRANDS_DIR", str(tmp_path))
    rfile = _recipe_with_cover(
        tmp_path,
        '{source: brand-preset, name: a, alt_text: "recipe alt"}',
    )
    html, meta = compose(str(rfile), "en", brand="x")
    cover_hits = [r for r in meta["resolved_images"] if r["component"] == "cover-page"]
    assert cover_hits and cover_hits[0]["alt"] == "recipe alt"


# ---------------------------------------------------------------- save_cover_preset


def _make_brand_and_fake_resolved_image(tmp_path: Path, brand_name: str = "save"):
    src = _tiny_png(tmp_path / "cache" / "abcd.png")
    brand = _write_brand(tmp_path, brand_name)
    return brand, src


def test_save_cover_preset_writes_file_and_updates_yaml(tmp_path, monkeypatch):
    brand, src = _make_brand_and_fake_resolved_image(tmp_path)
    monkeypatch.setenv("KATIB_BRANDS_DIR", str(tmp_path))

    dest = save_cover_preset(
        brand="save",
        preset_name="launch",
        cover_image={
            "component": "cover-page",
            "tier": "cover",
            "slot": "image",
            "source": "gemini",
            "resolved_path": str(src),
            "alt": "Hero cover",
        },
    )
    assert dest.exists()
    assert dest.name == "launch.png"
    assert dest.parent == tmp_path / "save-assets" / "covers"

    reloaded = yaml.safe_load(brand.read_text(encoding="utf-8"))
    entry = reloaded["covers"]["launch"]
    assert entry["source"] == "user-file"
    assert entry["path"] == "save-assets/covers/launch.png"
    assert entry["alt_text"] == "Hero cover"


def test_save_cover_preset_refuses_overwrite_without_force(tmp_path, monkeypatch):
    brand, src = _make_brand_and_fake_resolved_image(tmp_path)
    monkeypatch.setenv("KATIB_BRANDS_DIR", str(tmp_path))
    img = {
        "component": "cover-page", "tier": "cover", "slot": "image",
        "source": "gemini", "resolved_path": str(src), "alt": "",
    }
    save_cover_preset(brand="save", preset_name="dup", cover_image=img)
    with pytest.raises(SavePresetError, match="already has cover preset"):
        save_cover_preset(brand="save", preset_name="dup", cover_image=img)


def test_save_cover_preset_force_overwrites(tmp_path, monkeypatch):
    brand, src = _make_brand_and_fake_resolved_image(tmp_path)
    monkeypatch.setenv("KATIB_BRANDS_DIR", str(tmp_path))
    img = {
        "component": "cover-page", "tier": "cover", "slot": "image",
        "source": "gemini", "resolved_path": str(src), "alt": "old",
    }
    save_cover_preset(brand="save", preset_name="x", cover_image=img)
    img2 = dict(img, alt="new")
    save_cover_preset(brand="save", preset_name="x", cover_image=img2, force=True)
    reloaded = yaml.safe_load(brand.read_text(encoding="utf-8"))
    assert reloaded["covers"]["x"]["alt_text"] == "new"


def test_save_cover_preset_preserves_comments(tmp_path, monkeypatch):
    brand = tmp_path / "commented.yaml"
    brand.write_text(
        "# A commented brand — this comment must survive save-back.\n"
        "name: Commented\n"
        "colors:\n"
        "  accent: '#ABCDEF'   # inline comment\n",
        encoding="utf-8",
    )
    src = _tiny_png(tmp_path / "cache" / "keep.png")
    monkeypatch.setenv("KATIB_BRANDS_DIR", str(tmp_path))
    save_cover_preset(
        brand="commented",
        preset_name="z",
        cover_image={
            "component": "cover-page", "tier": "cover", "slot": "image",
            "source": "user-file", "resolved_path": str(src), "alt": "",
        },
    )
    raw = brand.read_text(encoding="utf-8")
    assert "# A commented brand" in raw
    assert "inline comment" in raw
    assert "covers:" in raw


def test_save_cover_preset_rejects_bad_preset_name(tmp_path, monkeypatch):
    brand, src = _make_brand_and_fake_resolved_image(tmp_path)
    monkeypatch.setenv("KATIB_BRANDS_DIR", str(tmp_path))
    with pytest.raises(SavePresetError, match="must match"):
        save_cover_preset(
            brand="save",
            preset_name="Has Spaces!",
            cover_image={
                "component": "cover-page", "tier": "cover", "slot": "image",
                "source": "user-file", "resolved_path": str(src), "alt": "",
            },
        )


# ---------------------------------------------------------------- find_cover_image


def test_find_cover_image_picks_first_cover_tier():
    images = [
        {"tier": "section", "component": "figure-with-caption",
         "slot": "image", "resolved_path": "/skip/me.png"},
        {"tier": "cover", "component": "cover-page",
         "slot": "image", "resolved_path": "/pick/me.png"},
        {"tier": "cover", "component": "cover-page",
         "slot": "image", "resolved_path": "/also/cover.png"},
    ]
    picked = find_cover_image(images)
    assert picked["resolved_path"] == "/pick/me.png"


def test_find_cover_image_none_when_no_cover_tier():
    images = [
        {"tier": "section", "component": "figure-with-caption",
         "slot": "image", "resolved_path": "/figure.png"},
    ]
    assert find_cover_image(images) is None


# ---------------------------------------------------------------- build.py CLI integration


def test_build_cli_save_requires_brand(tmp_path):
    """--save-cover-preset without --brand exits 1."""
    result = subprocess.run(
        [
            sys.executable, "scripts/build.py",
            "tutorial-katib-walkthrough", "--lang", "en",
            "--save-cover-preset", "x",
            "--skip-audit-check",
            "--out", str(tmp_path / "out.pdf"),
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "requires --brand" in result.stderr
