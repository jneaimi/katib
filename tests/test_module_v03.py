"""module section v0.3.0 — title-optional behavior.

Phase 3 Day 3 upgrade: v0.2.0 → v0.3.0 relaxed `title` from required to
optional. A module with only `raw_body` (or `body`) now renders as
continuous prose — used for letter bodies, legal recitals, abstract
paragraphs, and any section where a heading is not appropriate.

Pre-existing tests in test_module_and_cover.py cover the with-title case;
this file covers the new heading-less case and the regression guards.
"""
from __future__ import annotations

from pathlib import Path

from core.compose import compose, load_component

REPO_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------- schema


def test_module_version_bumped_to_030():
    c = load_component("module")
    assert c["version"] == "0.3.0"


def test_module_title_is_optional_in_030():
    c = load_component("module")
    title_decl = next(
        (next(iter(inp.values())) for inp in c["accepts"]["inputs"] if "title" in inp),
        None,
    )
    assert title_decl is not None
    assert title_decl["required"] is False


# ---------------------------------------------------------------- render (new no-title paths)


def test_module_renders_without_title_raw_body_only(tmp_path):
    """Letter-body shape: no eyebrow, no title, no intro, just raw prose."""
    rfile = tmp_path / "m.yaml"
    rfile.write_text(
        "name: m-test\n"
        "version: 0.1.0\n"
        "namespace: katib\n"
        "languages: [en]\n"
        "sections:\n"
        "  - component: module\n"
        "    inputs:\n"
        "      raw_body: |\n"
        "        <p>Dear Ms. Al-Hashimi,</p>\n"
        "        <p>Thank you for the opportunity.</p>\n"
        "        <p>Kind regards,</p>\n"
    )
    html, _ = compose(str(rfile), "en")
    # Body prose is present
    assert "Dear Ms. Al-Hashimi," in html
    assert "Kind regards," in html
    # No h2 title element (the class appears in inlined <style>; check the actual tag)
    assert "<h2 " not in html
    # No head div either — when all heading inputs are missing, the head block
    # collapses entirely
    assert '<div class="katib-module__head">' not in html


def test_module_renders_without_title_plain_body_only(tmp_path):
    """Plain-body (auto-escaped) version of the no-heading path."""
    rfile = tmp_path / "m.yaml"
    rfile.write_text(
        "name: m-test\n"
        "version: 0.1.0\n"
        "namespace: katib\n"
        "languages: [en]\n"
        "sections:\n"
        "  - component: module\n"
        "    inputs:\n"
        "      body: |\n"
        "        A paragraph of continuous prose without any heading.\n"
    )
    html, _ = compose(str(rfile), "en")
    assert "continuous prose without any heading" in html
    assert "<h2 " not in html


def test_module_without_title_bilingual(tmp_path):
    """AR render of heading-less module."""
    rfile = tmp_path / "m.yaml"
    rfile.write_text(
        "name: m-test\n"
        "version: 0.1.0\n"
        "namespace: katib\n"
        "languages: [ar]\n"
        "sections:\n"
        "  - component: module\n"
        "    inputs:\n"
        "      raw_body: |\n"
        "        <p>السلام عليكم ورحمة الله وبركاته</p>\n"
        "        <p>تفضلوا بقبول فائق الاحترام والتقدير</p>\n"
    )
    html, _ = compose(str(rfile), "ar")
    assert 'dir="rtl"' in html
    assert "السلام عليكم" in html
    assert "<h2 " not in html


# ---------------------------------------------------------------- regression guards


def test_module_with_title_still_emits_h2(tmp_path):
    """Regression: existing recipes providing title must still get an <h2>."""
    rfile = tmp_path / "m.yaml"
    rfile.write_text(
        "name: m-test\n"
        "version: 0.1.0\n"
        "namespace: katib\n"
        "languages: [en]\n"
        "sections:\n"
        "  - component: module\n"
        "    inputs:\n"
        '      title: "Where this comes from"\n'
        '      eyebrow: "Part 1 · Origins"\n'
        '      intro: "Context sentence."\n'
        "      body: \"Body text.\"\n"
    )
    html, _ = compose(str(rfile), "en")
    assert "<h2 " in html
    assert "Where this comes from" in html
    assert "katib-module__head" in html
    assert "Part 1 · Origins" in html


def test_module_tutorial_recipe_still_renders(tmp_path):
    """Regression: production tutorial.yaml uses 9 modules with titles — must
    render unchanged after v0.3.0."""
    html, _ = compose("tutorial", "en")
    # Every module title from tutorial.yaml should appear (spot-check 3)
    assert "Where this comes from" in html
    assert "Six levels, two lanes, one boundary" in html
    assert "Putting the framework to work this week" in html
    # And h2 emission must be there
    assert "<h2 " in html


def test_module_eyebrow_only_still_renders_head(tmp_path):
    """Edge case: eyebrow set but no title — head div should still render
    because eyebrow is heading content."""
    rfile = tmp_path / "m.yaml"
    rfile.write_text(
        "name: m-test\n"
        "version: 0.1.0\n"
        "namespace: katib\n"
        "languages: [en]\n"
        "sections:\n"
        "  - component: module\n"
        "    inputs:\n"
        '      eyebrow: "Preface"\n'
        '      body: "Body text."\n'
    )
    html, _ = compose(str(rfile), "en")
    assert "katib-module__head" in html
    assert "Preface" in html
    # Still no h2 since title is unset
    assert "<h2 " not in html
