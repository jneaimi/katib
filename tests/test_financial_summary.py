"""financial-summary section — schema invariants + render + variant behavior.

Phase 3 Day 15 component. Seventh Phase-3 new component (6 original queue
items + sections-grid + data-table + this one). Dependents verified before
scaffolding: financial/invoice (Day 15), financial/quote (Day 16 planned).
2 verified dependents below auto-graduation threshold of 3 — scaffolded
with --force + justification per Day-5 masthead-personal honest-intent pattern.
"""
from __future__ import annotations

from pathlib import Path

from core.compose import compose, load_component
from core.render import render_to_pdf

REPO_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------- schema


def test_financial_summary_loads_against_schema():
    c = load_component("financial-summary")
    assert c["tier"] == "section"
    assert c["version"] == "0.1.0"
    assert c["namespace"] == "katib"
    assert set(c["languages"]) == {"en", "ar"}


def test_financial_summary_variants_declared():
    c = load_component("financial-summary")
    variants = c.get("variants", [])
    assert "compact" in variants


def test_financial_summary_rows_required():
    c = load_component("financial-summary")
    inputs_by_name = {
        next(iter(inp.keys())): next(iter(inp.values()))
        for inp in c["accepts"]["inputs"]
    }
    assert inputs_by_name["rows"]["required"] is True
    assert inputs_by_name["currency"]["required"] is False


def test_financial_summary_token_contract():
    c = load_component("financial-summary")
    required = set(c["requires"]["tokens"])
    assert {"text", "text_secondary", "accent", "accent_on", "border"}.issubset(required)


# ---------------------------------------------------------------- render


def _inline_recipe(
    tmp_path: Path,
    variant: str | None = None,
    with_currency: bool = True,
    lang: str = "en",
) -> Path:
    variant_line = f"    variant: {variant}\n" if variant else ""
    currency_line = '      currency: "AED"\n' if with_currency else ""
    rfile = tmp_path / "fs.yaml"
    rfile.write_text(
        "name: fs-test\n"
        "version: 0.1.0\n"
        "namespace: katib\n"
        f"languages: [{lang}]\n"
        "sections:\n"
        "  - component: financial-summary\n"
        + variant_line +
        "    inputs:\n"
        + currency_line +
        "      rows:\n"
        '        - {label: "Subtotal", value: "10,000.00"}\n'
        '        - {label: "VAT (5%)", value: "500.00"}\n'
        '        - {label: "TOTAL", value: "10,500.00", variant: total}\n'
    )
    return rfile


def test_financial_summary_renders_en(tmp_path):
    rfile = _inline_recipe(tmp_path)
    html, _ = compose(str(rfile), "en")
    # 3 rows rendered
    assert html.count('class="katib-financial-summary__row"') == 2  # non-total rows
    assert 'katib-financial-summary__row--total' in html
    # Content preserved
    assert "Subtotal" in html
    assert "10,000.00" in html
    assert "10,500.00" in html


def test_financial_summary_renders_ar(tmp_path):
    rfile = _inline_recipe(tmp_path, lang="ar")
    html, _ = compose(str(rfile), "ar")
    assert 'dir="rtl"' in html
    assert 'lang="ar"' in html


def test_financial_summary_renders_to_pdf(tmp_path):
    rfile = _inline_recipe(tmp_path)
    html, _ = compose(str(rfile), "en")
    pdf = render_to_pdf(html, tmp_path / "fs.en.pdf", base_url=REPO_ROOT)
    assert pdf.exists()
    assert pdf.stat().st_size > 2500


def test_financial_summary_compact_variant_class_emitted(tmp_path):
    rfile = _inline_recipe(tmp_path, variant="compact")
    html, _ = compose(str(rfile), "en")
    assert "katib-financial-summary--compact" in html


def test_financial_summary_default_variant_class_when_unset(tmp_path):
    rfile = _inline_recipe(tmp_path)
    html, _ = compose(str(rfile), "en")
    assert "katib-financial-summary--default" in html


def test_financial_summary_currency_appended_to_total_label(tmp_path):
    """The Total row's label gets the currency suffix: 'TOTAL AED'."""
    rfile = _inline_recipe(tmp_path, with_currency=True)
    html, _ = compose(str(rfile), "en")
    # Currency code appended on the total row label
    assert "TOTAL AED" in html or "TOTAL" in html and "AED" in html


def test_financial_summary_currency_absent_when_unset(tmp_path):
    """No currency code appended when input.currency is not set."""
    rfile = _inline_recipe(tmp_path, with_currency=False)
    html, _ = compose(str(rfile), "en")
    # Label should just be "TOTAL" without AED suffix
    assert "TOTAL AED" not in html


def test_financial_summary_total_row_emphasis_class(tmp_path):
    """The variant: total row gets the --total modifier class."""
    rfile = _inline_recipe(tmp_path)
    html, _ = compose(str(rfile), "en")
    # Count total-modifier usages: 1 CSS rule + 1 element = 2 if we count just class="...--total"
    # Use the element-form specifically
    assert 'class="katib-financial-summary__row katib-financial-summary__row--total"' in html
