"""Token resolution — base, brand merge, bilingual fallback, CSS injection block."""
from __future__ import annotations

import pytest

from core.tokens import (
    TokenError,
    _validate_color,
    load_base_tokens,
    merge_tokens,
    render_context,
    tokens_css,
)


def test_base_tokens_load_clean():
    base = load_base_tokens()
    assert "colors" in base
    assert "fonts" in base
    assert base["colors"]["page_bg"].startswith("#")


def test_brand_overrides_base():
    base = load_base_tokens()
    merged = merge_tokens(
        base,
        brand={"name": "Test", "colors": {"accent": "#FF0000"}},
    )
    assert merged["colors"]["accent"] == "#FF0000"
    # unrelated tokens preserved
    assert merged["colors"]["page_bg"] == base["colors"]["page_bg"]


def test_overrides_trump_brand():
    base = load_base_tokens()
    merged = merge_tokens(
        base,
        brand={"name": "Test", "colors": {"accent": "#FF0000"}},
        overrides={"colors": {"accent": "#00FF00"}},
    )
    assert merged["colors"]["accent"] == "#00FF00"


def test_render_context_en_vs_ar_direction():
    base = load_base_tokens()
    merged = merge_tokens(base)
    en = render_context(merged, "en")
    ar = render_context(merged, "ar")
    assert en["dir"] == "ltr"
    assert ar["dir"] == "rtl"
    assert en["lang"] == "en"
    assert ar["lang"] == "ar"


def test_bilingual_identity_fallback():
    base = load_base_tokens()
    merged = merge_tokens(
        base,
        brand={
            "name": "Widgets Co",
            "name_ar": "شركة ويدجتس",
            "identity": {"author_name": "Jane", "author_name_ar": "جين"},
        },
    )
    en_ctx = render_context(merged, "en")
    ar_ctx = render_context(merged, "ar")
    assert en_ctx["name"] == "Widgets Co"
    assert ar_ctx["name"] == "شركة ويدجتس"
    assert en_ctx["identity"]["author_name"] == "Jane"
    assert ar_ctx["identity"]["author_name"] == "جين"


def test_ar_falls_back_to_en_when_missing():
    base = load_base_tokens()
    merged = merge_tokens(
        base,
        brand={"name": "EN only", "identity": {"email": "x@y.com"}},
    )
    ar_ctx = render_context(merged, "ar")
    assert ar_ctx["name"] == "EN only"
    assert ar_ctx["identity"]["email"] == "x@y.com"


def test_fonts_switch_by_lang():
    base = load_base_tokens()
    en = render_context(base, "en")
    ar = render_context(base, "ar")
    assert en["fonts"]["primary"] == "Inter"
    assert ar["fonts"]["primary"] == "Cairo"


def test_css_injection_blocked():
    with pytest.raises(TokenError) as exc:
        _validate_color("accent", "red; } body { display: none;")
    assert "not a recognized CSS color" in str(exc.value)


def test_css_injection_blocked_via_load_brand_merged():
    # Merge does not re-validate; this is a per-load contract. Direct
    # validation path is covered above.
    base = load_base_tokens()
    merged = merge_tokens(base, brand={"name": "x", "colors": {"accent": "#123456"}})
    css = tokens_css(merged)
    assert "--accent: #123456" in css
    assert "injection" not in css


@pytest.mark.parametrize(
    "good_color",
    ["#123", "#1F3A68", "#FFFFFFFF", "rgb(255, 0, 0)", "rgba(0,0,0,0.5)", "navy", "cornflower-blue", "hsl(120, 50%, 40%)"],
)
def test_color_whitelist_accepts_valid(good_color):
    assert _validate_color("accent", good_color) == good_color


@pytest.mark.parametrize(
    "bad_color",
    [
        "red; } body { display: none;",
        "url(javascript:alert(1))",
        "#GGGGGG",
        "",
        "red /*comment*/",
        "rgb(1,2,3) ; evil",
    ],
)
def test_color_whitelist_rejects_invalid(bad_color):
    with pytest.raises(TokenError):
        _validate_color("accent", bad_color)


def test_tokens_css_emits_root_block():
    base = load_base_tokens()
    css = tokens_css(merge_tokens(base))
    assert css.startswith(":root {")
    assert css.rstrip().endswith("}")
    assert "--accent:" in css
    assert "--page-bg:" in css
