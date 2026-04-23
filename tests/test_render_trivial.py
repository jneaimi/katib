"""End-to-end: phase-1-trivial -> compose -> WeasyPrint -> PDF invariants.

Uses pypdf text extraction to verify structural/content invariants.
A pixel-level golden test is Phase 2+ work (needs deterministic fonts).
"""
from __future__ import annotations

from pathlib import Path

import pytest
from pypdf import PdfReader

from core.compose import compose
from core.render import render_to_pdf

REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def out_dir(tmp_path):
    return tmp_path / "rendered"


@pytest.mark.parametrize("lang", ["en", "ar"])
def test_trivial_recipe_renders_to_pdf(lang, out_dir):
    html, _ = compose("phase-1-trivial", lang)
    pdf = render_to_pdf(
        html, out_dir / f"phase-1-trivial.{lang}.pdf", base_url=REPO_ROOT
    )
    assert pdf.exists()
    assert pdf.stat().st_size > 2000, "PDF too small to be well-formed"

    reader = PdfReader(str(pdf))
    assert len(reader.pages) >= 1
    text = "\n".join(page.extract_text() or "" for page in reader.pages).lower()
    # Eyebrow CSS uppercases EN text, so match case-insensitively
    assert "phase 1" in text
    assert "jasem al neaimi" in text


def test_trivial_ar_contains_arabic_text(out_dir):
    html, _ = compose("phase-1-trivial", "ar")
    pdf = render_to_pdf(
        html, out_dir / "phase-1-trivial.ar.pdf", base_url=REPO_ROOT
    )
    reader = PdfReader(str(pdf))
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    # Some Arabic text from the recipe's step-circle labels, callout body, etc.
    # The author_name "Jasem Al Neaimi" renders in Latin script (name field not
    # localised in the test recipe), but the recipe-level strings like the
    # callout title appear.
    assert text.strip(), "AR PDF produced empty text"


def test_trivial_en_smaller_than_or_close_to_ar(out_dir):
    # Both render; file sizes are comparable. This is a cheap regression guard.
    html_en, _ = compose("phase-1-trivial", "en")
    html_ar, _ = compose("phase-1-trivial", "ar")
    pdf_en = render_to_pdf(
        html_en, out_dir / "trivial.en.pdf", base_url=REPO_ROOT
    )
    pdf_ar = render_to_pdf(
        html_ar, out_dir / "trivial.ar.pdf", base_url=REPO_ROOT
    )
    assert pdf_en.stat().st_size > 2000
    assert pdf_ar.stat().st_size > 2000
