"""callout primitive v0.2.0 — neutral tone addition.

Phase 3 Day 5 upgrade: v0.1.0 → v0.2.0 added the `neutral` tone for
non-status highlighted boxes (cover-letter subject lines, legal
non-binding notices). The existing info/warn/danger/tip tones are
unchanged and regression-guarded below.
"""
from __future__ import annotations

from pathlib import Path
import tempfile

from core.compose import compose, load_component
from core.render import render_to_pdf

REPO_ROOT = Path(__file__).resolve().parent.parent


def _inline_recipe(tmp_path: Path, tone: str, lang: str = "en") -> Path:
    rfile = tmp_path / "cb.yaml"
    rfile.write_text(
        "name: cb-test\n"
        "version: 0.1.0\n"
        "namespace: katib\n"
        f"languages: [{lang}]\n"
        "sections:\n"
        "  - component: callout\n"
        "    inputs:\n"
        f"      tone: {tone}\n"
        "      title: Test title\n"
        "      body: Sample body text for the callout.\n"
    )
    return rfile


# ---------------------------------------------------------------- schema


def test_callout_version_bumped_to_020():
    c = load_component("callout")
    assert c["version"] == "0.2.0"


def test_callout_requires_tokens_added_for_neutral():
    """0.2.0 adds tag_bg + accent to requires.tokens for the neutral tone's
    background + border pair."""
    c = load_component("callout")
    required = set(c["requires"]["tokens"])
    assert "tag_bg" in required
    assert "accent" in required
    # Existing status-tone tokens unchanged
    for key in ("callout_info_bg", "callout_info_accent", "callout_warn_bg",
                "callout_danger_bg", "callout_tip_bg"):
        assert key in required


# ---------------------------------------------------------------- render — neutral tone (new)


def test_callout_neutral_tone_renders_class(tmp_path):
    rfile = _inline_recipe(tmp_path, tone="neutral")
    html, _ = compose(str(rfile), "en")
    assert "katib-callout--neutral" in html


def test_callout_neutral_renders_to_pdf(tmp_path):
    rfile = _inline_recipe(tmp_path, tone="neutral")
    html, _ = compose(str(rfile), "en")
    pdf = render_to_pdf(html, tmp_path / "cb.en.pdf", base_url=REPO_ROOT)
    assert pdf.exists()
    assert pdf.stat().st_size > 3000


def test_callout_neutral_tone_bilingual(tmp_path):
    rfile = _inline_recipe(tmp_path, tone="neutral", lang="ar")
    html, _ = compose(str(rfile), "ar")
    assert 'dir="rtl"' in html
    assert "katib-callout--neutral" in html


# ---------------------------------------------------------------- regression — existing tones unchanged


def test_callout_existing_tones_still_render(tmp_path):
    """All 4 pre-0.2.0 tones must still render cleanly — regression guard for
    the schema + styles extension."""
    for tone in ("info", "warn", "danger", "tip"):
        rfile = _inline_recipe(tmp_path, tone=tone)
        html, _ = compose(str(rfile), "en")
        assert f"katib-callout--{tone}" in html


def test_callout_stylesheet_has_neutral_rules():
    """Stylesheet must define .katib-callout--neutral background + border +
    title rules using the correct tokens."""
    css = (REPO_ROOT / "components" / "primitives" / "callout" / "styles.css").read_text()
    assert ".katib-callout--neutral" in css
    assert "var(--tag-bg)" in css
    assert "var(--accent)" in css


def test_callout_stylesheet_preserves_all_five_tones():
    """Stylesheet must define selector blocks for all 5 tones."""
    css = (REPO_ROOT / "components" / "primitives" / "callout" / "styles.css").read_text()
    for tone in ("info", "warn", "danger", "tip", "neutral"):
        assert f".katib-callout--{tone}" in css, f"tone {tone} missing from stylesheet"
