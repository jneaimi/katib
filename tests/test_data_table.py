"""data-table primitive — schema invariants + render + variant behavior.

Phase 3 Day 13 component. Second Phase-3 primitive. Dependents verified
before scaffolding: white-paper (5-col numeric time-series), proposal
(4-col deliverables with # column), invoice (7-col line-items with desc+sub
cells), onboarding (3-col text-only windows).

Second Phase-3 component to auto-graduate through the request log
(sections-grid Day 11 was first).
"""
from __future__ import annotations

from pathlib import Path

from core.compose import compose, load_component
from core.render import render_to_pdf

REPO_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------- schema


def test_data_table_loads_against_schema():
    c = load_component("data-table")
    assert c["tier"] == "primitive"
    assert c["version"] == "0.1.0"
    assert c["namespace"] == "katib"
    assert set(c["languages"]) == {"en", "ar"}


def test_data_table_variants_declared():
    c = load_component("data-table")
    variants = c.get("variants", [])
    assert "bordered" in variants
    assert "dense" in variants


def test_data_table_columns_and_rows_required():
    c = load_component("data-table")
    inputs_by_name = {
        next(iter(inp.keys())): next(iter(inp.values()))
        for inp in c["accepts"]["inputs"]
    }
    assert inputs_by_name["columns"]["required"] is True
    assert inputs_by_name["rows"]["required"] is True
    assert inputs_by_name["caption"]["required"] is False


def test_data_table_token_contract():
    c = load_component("data-table")
    required = set(c["requires"]["tokens"])
    assert {"text", "accent", "accent_on", "border", "tag_bg"}.issubset(required)


# ---------------------------------------------------------------- render


def _inline_recipe(
    tmp_path: Path,
    variant: str | None = None,
    with_caption: bool = False,
    with_sub_cell: bool = False,
    lang: str = "en",
) -> Path:
    variant_line = f"    variant: {variant}\n" if variant else ""
    caption_line = '      caption: "Test table caption"\n' if with_caption else ""
    sub_cell_row = (
        '        - ["1", {text: "Service", sub: "Scope note"}, "5,000.00"]\n'
        if with_sub_cell
        else '        - ["1", "Service", "5,000.00"]\n'
    )
    rfile = tmp_path / "dt.yaml"
    rfile.write_text(
        "name: dt-test\n"
        "version: 0.1.0\n"
        "namespace: katib\n"
        f"languages: [{lang}]\n"
        "sections:\n"
        "  - component: data-table\n"
        + variant_line +
        "    inputs:\n"
        + caption_line +
        "      columns:\n"
        '        - {label: "#", align: num}\n'
        '        - {label: "Description"}\n'
        '        - {label: "Amount", align: num}\n'
        "      rows:\n"
        + sub_cell_row +
        '        - ["2", "Consulting", "12,000.00"]\n'
    )
    return rfile


def test_data_table_renders_en(tmp_path):
    rfile = _inline_recipe(tmp_path)
    html, _ = compose(str(rfile), "en")
    # Semantic structure
    assert "<table" in html
    assert "<thead" in html
    assert "<tbody" in html
    assert html.count("<th ") >= 3  # 3 column headers
    # Numeric class applied to the align:num columns (# and Amount)
    assert 'class="katib-data-table__th katib-data-table__th--num"' in html
    # Content preserved
    assert "Description" in html
    assert "5,000.00" in html
    assert "Consulting" in html


def test_data_table_renders_ar(tmp_path):
    rfile = _inline_recipe(tmp_path, lang="ar")
    html, _ = compose(str(rfile), "ar")
    assert 'dir="rtl"' in html
    assert 'lang="ar"' in html


def test_data_table_renders_to_pdf(tmp_path):
    rfile = _inline_recipe(tmp_path)
    html, _ = compose(str(rfile), "en")
    pdf = render_to_pdf(html, tmp_path / "dt.en.pdf", base_url=REPO_ROOT)
    assert pdf.exists()
    assert pdf.stat().st_size > 3000


def test_data_table_bordered_variant_class_emitted(tmp_path):
    rfile = _inline_recipe(tmp_path, variant="bordered")
    html, _ = compose(str(rfile), "en")
    assert "katib-data-table--bordered" in html


def test_data_table_dense_variant_class_emitted(tmp_path):
    rfile = _inline_recipe(tmp_path, variant="dense")
    html, _ = compose(str(rfile), "en")
    assert "katib-data-table--dense" in html


def test_data_table_default_variant_class_when_unset(tmp_path):
    rfile = _inline_recipe(tmp_path)
    html, _ = compose(str(rfile), "en")
    assert "katib-data-table--default" in html


def test_data_table_caption_rendered_when_set(tmp_path):
    rfile = _inline_recipe(tmp_path, with_caption=True)
    html, _ = compose(str(rfile), "en")
    assert "<caption" in html
    assert "Test table caption" in html


def test_data_table_caption_absent_when_unset(tmp_path):
    rfile = _inline_recipe(tmp_path)
    html, _ = compose(str(rfile), "en")
    assert "<caption" not in html


def test_data_table_cell_with_sub_text(tmp_path):
    """Invoice-style cell: {text, sub} renders as two spans inside one <td>."""
    rfile = _inline_recipe(tmp_path, with_sub_cell=True)
    html, _ = compose(str(rfile), "en")
    assert 'class="katib-data-table__cell-text"' in html
    assert 'class="katib-data-table__cell-sub"' in html
    assert ">Service<" in html
    assert ">Scope note<" in html


def test_data_table_column_width_hint_applied(tmp_path):
    """width input emits inline style="width: ..." on <th>."""
    rfile = tmp_path / "dt.yaml"
    rfile.write_text(
        "name: dt-w\n"
        "version: 0.1.0\n"
        "namespace: katib\n"
        "languages: [en]\n"
        "sections:\n"
        "  - component: data-table\n"
        "    inputs:\n"
        "      columns:\n"
        '        - {label: "#", width: "30pt"}\n'
        '        - {label: "Description"}\n'
        "      rows:\n"
        '        - ["1", "Item"]\n'
    )
    html, _ = compose(str(rfile), "en")
    assert 'style="width: 30pt;"' in html


def test_data_table_th_scope_attribute_for_a11y(tmp_path):
    """Column headers carry scope='col' for screen-reader accessibility."""
    rfile = _inline_recipe(tmp_path)
    html, _ = compose(str(rfile), "en")
    assert 'scope="col"' in html
    assert html.count('scope="col"') == 3  # one per column
