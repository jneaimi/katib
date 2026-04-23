"""Composer — recipe + component loading, schema gates, language gates."""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from core.compose import (
    ComposeError,
    compose,
    load_component,
    load_recipe,
)


def test_load_recipe_by_name():
    r = load_recipe("phase-1-trivial")
    assert r["name"] == "phase-1-trivial"
    assert r["languages"] == ["en", "ar"]
    assert r["sections"]


def test_load_recipe_rejects_bad_schema(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text(
        "name: Bad-Name\n"  # uppercase name — fails kebab-case regex
        "version: 0.1.0\n"
        "namespace: katib\n"
        "languages: [en]\n"
        "sections: [{component: eyebrow}]\n"
    )
    with pytest.raises(ComposeError):
        load_recipe(str(bad))


def test_load_recipe_rejects_missing_sections(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text(
        "name: no-sections\n"
        "version: 0.1.0\n"
        "namespace: katib\n"
        "languages: [en]\n"
        "sections: []\n"
    )
    with pytest.raises(ComposeError):
        load_recipe(str(bad))


def test_load_recipe_not_found_is_filenotfound():
    with pytest.raises(FileNotFoundError):
        load_recipe("does-not-exist")


def test_load_component_happy():
    c = load_component("eyebrow")
    assert c["tier"] == "primitive"
    assert c["languages"] == ["en", "ar"]
    assert c["version"] == "0.1.0"


def test_load_component_not_found():
    with pytest.raises(FileNotFoundError):
        load_component("nonexistent-primitive")


def test_compose_en_produces_html():
    html, meta = compose("phase-1-trivial", "en")
    assert '<html lang="en" dir="ltr">' in html
    assert "Phase 1" in html
    assert "Reviewed" in html
    assert meta["recipe"]["name"] == "phase-1-trivial"


def test_compose_ar_produces_rtl_html():
    html, _ = compose("phase-1-trivial", "ar")
    assert '<html lang="ar" dir="rtl">' in html
    assert 'dir="rtl"' in html


def test_compose_unsupported_lang_rejected():
    with pytest.raises(ComposeError, match="languages"):
        compose("phase-1-trivial", "fr")


def test_compose_emits_token_css_root_block():
    html, _ = compose("phase-1-trivial", "en")
    assert ":root {" in html
    assert "--accent:" in html
    assert "--font-primary:" in html


def test_compose_component_styles_concatenate():
    html, _ = compose("phase-1-trivial", "en")
    # All 6 component style sets used by phase-1-trivial should be present
    for selector in (
        ".katib-eyebrow",
        ".katib-rule",
        ".katib-tag",
        ".katib-callout",
        ".katib-step",
        ".katib-pullquote",
        ".katib-signature",
    ):
        assert selector in html, f"missing styles for {selector}"


def test_compose_brand_override_flows_through(tmp_path, monkeypatch):
    brand_dir = tmp_path / "brands"
    brand_dir.mkdir()
    (brand_dir / "testbrand.yaml").write_text(
        "name: Test Brand\ncolors:\n  accent: '#FF00AA'\n"
    )
    monkeypatch.setenv("KATIB_BRANDS_DIR", str(brand_dir))
    html, _ = compose("phase-1-trivial", "en", brand="testbrand")
    assert "--accent: #FF00AA" in html


def test_compose_autoescapes_html_in_inputs(tmp_path):
    recipe_path = tmp_path / "xss.yaml"
    recipe_path.write_text(
        "name: xss-test\n"
        "version: 0.1.0\n"
        "namespace: katib\n"
        "languages: [en]\n"
        "sections:\n"
        '  - component: eyebrow\n'
        '    inputs:\n'
        '      text: \'<script>alert("x")</script>\'\n'
    )
    html, _ = compose(str(recipe_path), "en")
    assert "<script>" not in html
    assert "&lt;script&gt;" in html
