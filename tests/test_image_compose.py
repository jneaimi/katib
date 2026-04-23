"""Image providers wired into compose() — Phase 2 Day 1 integration tests."""
from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

from core.compose import ComposeError, compose
from core.render import render_to_pdf

REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def tiny_png(tmp_path):
    p = tmp_path / "fixture.png"
    Image.new("RGB", (80, 40), color=(80, 140, 60)).save(p)
    return p


def _recipe(tmp_path, image_spec):
    rfile = tmp_path / "r.yaml"
    rfile.write_text(
        "name: image-test\n"
        "version: 0.1.0\n"
        "namespace: katib\n"
        "languages: [en]\n"
        "sections:\n"
        "  - component: figure-with-caption\n"
        "    inputs:\n"
        f"      image: {image_spec}\n"
        "      alt_text: test fixture\n"
        "      caption: Figure 1.\n"
    )
    return rfile


def test_user_file_image_resolves_into_html(tmp_path, tiny_png):
    spec = f"{{source: user-file, path: {tiny_png}}}"
    rfile = _recipe(tmp_path, spec)
    html, _ = compose(str(rfile), "en")
    assert '<img class="katib-figure__img"' in html
    assert "katib/images" in html or str(tiny_png.stem) in html or "Caches/katib" in html
    assert 'alt="test fixture"' in html


def test_user_file_missing_path_fails_loud(tmp_path):
    spec = "{source: user-file, path: /nonexistent/file.png}"
    rfile = _recipe(tmp_path, spec)
    with pytest.raises(Exception) as exc:
        compose(str(rfile), "en")
    assert "not found" in str(exc.value).lower()


def test_raw_string_image_rejected(tmp_path):
    spec = "/path/without/dict/shape.png"
    rfile = _recipe(tmp_path, spec)
    with pytest.raises(ComposeError, match="expected dict"):
        compose(str(rfile), "en")


def test_sources_accepted_gate_blocks_disallowed(tmp_path):
    # figure-with-caption accepts [user-file, url, gemini] — NOT screenshot
    spec = "{source: screenshot, url: 'https://example.com'}"
    rfile = _recipe(tmp_path, spec)
    with pytest.raises(Exception) as exc:
        compose(str(rfile), "en")
    assert "sources_accepted" in str(exc.value)


def test_gemini_source_fail_loud_without_key(tmp_path, monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    spec = "{source: gemini, prompt: 'test prompt', aspect: '16:9'}"
    rfile = _recipe(tmp_path, spec)
    with pytest.raises(Exception) as exc:
        compose(str(rfile), "en")
    msg = str(exc.value)
    assert "GEMINI_API_KEY" in msg
    assert "user-file" in msg


def test_missing_required_image_rejected(tmp_path):
    rfile = tmp_path / "r.yaml"
    rfile.write_text(
        "name: no-image\n"
        "version: 0.1.0\n"
        "namespace: katib\n"
        "languages: [en]\n"
        "sections:\n"
        "  - component: figure-with-caption\n"
        "    inputs:\n"
        "      alt_text: missing image slot\n"
    )
    with pytest.raises(ComposeError, match="required image input"):
        compose(str(rfile), "en")


def test_figure_with_user_file_renders_to_pdf(tmp_path, tiny_png):
    spec = f"{{source: user-file, path: {tiny_png}}}"
    rfile = _recipe(tmp_path, spec)
    html, _ = compose(str(rfile), "en")
    pdf = render_to_pdf(html, tmp_path / "out.pdf", base_url=REPO_ROOT)
    assert pdf.exists()
    assert pdf.stat().st_size > 2000
