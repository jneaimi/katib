"""kv-list section v0.2.0 — boxed variant.

Phase 3 Day 7 upgrade: v0.1.0 → v0.2.0 added the `boxed` variant for
field-summary use (NOC employee details, invoice/quote meta blocks).
Inverts emphasis compared to default: term becomes small-uppercase
label-style, value becomes bold emphasized data. Adds container
styling (bg + leading accent border + padding).

Pre-existing tests in test_kv_list.py (13 tests) cover default/dense/
spacious; this file covers the boxed variant addition.
"""
from __future__ import annotations

from pathlib import Path

from core.compose import compose, load_component
from core.render import render_to_pdf

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_kv_list_version_bumped_to_020():
    c = load_component("kv-list")
    assert c["version"] == "0.2.0"


def test_kv_list_boxed_variant_declared():
    c = load_component("kv-list")
    variants = c.get("variants", [])
    assert "boxed" in variants
    # Pre-existing variants still present
    assert "dense" in variants
    assert "spacious" in variants


def test_kv_list_requires_added_tokens_for_boxed():
    c = load_component("kv-list")
    required = set(c["requires"]["tokens"])
    assert "tag_bg" in required
    assert "accent" in required


def _inline_recipe(tmp_path: Path, *, variant: str | None = None, lang: str = "en") -> Path:
    variant_line = f"    variant: {variant}\n" if variant else ""
    rfile = tmp_path / "kv.yaml"
    rfile.write_text(
        "name: kv-test\n"
        "version: 0.1.0\n"
        "namespace: katib\n"
        f"languages: [{lang}]\n"
        "sections:\n"
        "  - component: kv-list\n"
        + variant_line +
        "    inputs:\n"
        "      heading: Employee details\n"
        "      items:\n"
        '        - {term: Name, value: "Jasem Al Neaimi"}\n'
        '        - {term: Passport No., value: "A1234567"}\n'
        '        - {term: Emirates ID, value: "784-YYYY-NNNNNNN-N"}\n'
        '        - {term: Employment Status, value: "Active — Full Time"}\n'
    )
    return rfile


def test_kv_list_boxed_renders_en(tmp_path):
    rfile = _inline_recipe(tmp_path, variant="boxed")
    html, _ = compose(str(rfile), "en")
    assert "katib-kv-list--boxed" in html
    assert "Employee details" in html
    assert "Passport No." in html


def test_kv_list_boxed_renders_to_pdf(tmp_path):
    rfile = _inline_recipe(tmp_path, variant="boxed")
    html, _ = compose(str(rfile), "en")
    pdf = render_to_pdf(html, tmp_path / "kv.en.pdf", base_url=REPO_ROOT)
    assert pdf.exists()
    assert pdf.stat().st_size > 4000


def test_kv_list_boxed_ar_flips_accent_border_to_right(tmp_path):
    """RTL renders must flip the leading accent border from left to right."""
    rfile = _inline_recipe(tmp_path, variant="boxed", lang="ar")
    html, _ = compose(str(rfile), "ar")
    assert 'dir="rtl"' in html
    assert "katib-kv-list--boxed" in html
    # The stylesheet contains both border-left and the RTL override
    assert ".katib-kv-list--boxed[dir=\"rtl\"]" in html


def test_kv_list_boxed_styles_use_tokens_only():
    """Regression guard — the boxed variant's added CSS must use tokens only."""
    css = (REPO_ROOT / "components" / "sections" / "kv-list" / "styles.css").read_text()
    import re
    hex_refs = re.findall(r"#[0-9a-fA-F]{3,8}\b", css)
    assert hex_refs == [], f"hex colors in styles.css: {hex_refs}"


def test_kv_list_boxed_emphasis_inverted():
    """Stylesheet contract: boxed variant's term uses label-style (lighter,
    small, uppercase); value uses emphasized (bold, normal size). This inverts
    the default variant's emphasis."""
    css = (REPO_ROOT / "components" / "sections" / "kv-list" / "styles.css").read_text()
    # Term styling under boxed uses text-secondary (lighter)
    assert ".katib-kv-list--boxed .katib-kv-list__term" in css
    assert "text-transform: uppercase" in css
    # Value styling under boxed uses text (emphasis) + bold
    assert ".katib-kv-list--boxed .katib-kv-list__value" in css
    # Dotted row separator unique to boxed
    assert "dotted var(--border)" in css
