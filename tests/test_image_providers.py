"""Image providers — availability, cache keys, happy path, fail-loud."""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
from PIL import Image

from core.image.base import (
    ProviderError,
    ProviderUnavailable,
    default_providers,
    resolve_image,
)


@pytest.fixture
def providers():
    return default_providers()


@pytest.fixture
def cache_dir(tmp_path):
    d = tmp_path / "cache"
    d.mkdir()
    return d


@pytest.fixture
def tiny_png(tmp_path):
    p = tmp_path / "tiny.png"
    Image.new("RGB", (20, 10), color=(100, 150, 200)).save(p)
    return p


def test_registry_has_four_providers(providers):
    assert set(providers) == {"user-file", "screenshot", "gemini", "inline-svg"}


def test_user_file_happy_path(providers, cache_dir, tiny_png):
    res = resolve_image(
        {"source": "user-file", "path": str(tiny_png)}, cache_dir, providers
    )
    assert res.path is not None
    assert res.path.exists()
    assert res.path.parent == cache_dir
    assert res.content_hash


def test_user_file_cache_is_stable_for_same_input(providers, cache_dir, tiny_png):
    res1 = resolve_image(
        {"source": "user-file", "path": str(tiny_png)}, cache_dir, providers
    )
    res2 = resolve_image(
        {"source": "user-file", "path": str(tiny_png)}, cache_dir, providers
    )
    assert res1.path == res2.path
    assert res1.content_hash == res2.content_hash


def test_user_file_missing_path_fails_loud(providers, cache_dir):
    with pytest.raises(ProviderError, match="not found"):
        resolve_image(
            {"source": "user-file", "path": "/nonexistent/path.png"},
            cache_dir,
            providers,
        )


def test_inline_svg_donut_renders(providers, cache_dir):
    res = resolve_image(
        {
            "source": "inline-svg",
            "type": "donut",
            "data": [{"label": "a", "value": 30}, {"label": "b", "value": 70}],
            "title": "test",
        },
        cache_dir,
        providers,
    )
    assert res.inline_svg is not None
    assert res.path is None
    assert "<svg" in res.inline_svg
    assert "<circle" in res.inline_svg
    assert "aria-label" in res.inline_svg


def test_inline_svg_deterministic(providers, cache_dir):
    spec = {
        "source": "inline-svg",
        "type": "donut",
        "data": [{"label": "a", "value": 30}, {"label": "b", "value": 70}],
    }
    r1 = resolve_image(spec, cache_dir, providers)
    r2 = resolve_image(spec, cache_dir, providers)
    assert r1.inline_svg == r2.inline_svg
    assert r1.content_hash == r2.content_hash


def test_inline_svg_unknown_chart_type_rejected(providers, cache_dir):
    with pytest.raises(ProviderError, match="unknown chart type"):
        resolve_image(
            {"source": "inline-svg", "type": "unicorn", "data": [{"value": 1}]},
            cache_dir,
            providers,
        )


def test_inline_svg_zero_total_rejected(providers, cache_dir):
    with pytest.raises(ProviderError, match="all values are zero"):
        resolve_image(
            {
                "source": "inline-svg",
                "type": "donut",
                "data": [{"value": 0}, {"value": 0}],
            },
            cache_dir,
            providers,
        )


def test_gemini_fail_loud_without_key(providers, cache_dir, monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(ProviderUnavailable) as exc:
        resolve_image(
            {"source": "gemini", "prompt": "test"}, cache_dir, providers
        )
    msg = str(exc.value)
    assert "GEMINI_API_KEY" in msg
    assert "export" in msg
    assert "user-file" in msg  # actionable alternative listed


def test_sources_accepted_gate_blocks_disallowed_source(
    providers, cache_dir, tiny_png
):
    with pytest.raises(ProviderError, match="not in component's sources_accepted"):
        resolve_image(
            {"source": "gemini", "prompt": "x"},
            cache_dir,
            providers,
            sources_accepted=["user-file", "url"],
        )


def test_missing_source_field_rejected(providers, cache_dir):
    with pytest.raises(ProviderError, match="missing 'source'"):
        resolve_image({"path": "/x"}, cache_dir, providers)


def test_unknown_source_rejected(providers, cache_dir):
    with pytest.raises(ProviderError, match="no provider"):
        resolve_image({"source": "ouija-board"}, cache_dir, providers)


def test_screenshot_cache_key_deterministic(providers):
    sp = providers["screenshot"]
    spec = {
        "url": "https://example.com",
        "viewport": [1440, 900],
        "hide": [".cookie", ".banner"],
    }
    spec_reordered = {
        "hide": [".banner", ".cookie"],
        "viewport": [1440, 900],
        "url": "https://example.com",
    }
    assert sp.cache_key(spec) == sp.cache_key(spec_reordered)


def test_gemini_cache_key_changes_with_prompt(providers):
    gp = providers["gemini"]
    k1 = gp.cache_key({"prompt": "a cat"})
    k2 = gp.cache_key({"prompt": "a dog"})
    assert k1 != k2
