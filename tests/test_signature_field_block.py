"""signature-field-block primitive — schema invariants + render behavior.

Blank-field signature grid for counterparty execution. Distinct from
signature-block (pre-filled named signatory) and multi-party-signature-block
(pre-filled multi-signatory closing). Use for documents that will be printed
and countersigned by hand (MoUs, quotes, service agreements).
"""
from __future__ import annotations

from pathlib import Path

from core.compose import compose, load_component

REPO_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------- schema


def test_signature_field_block_loads_against_schema():
    c = load_component("signature-field-block")
    assert c["tier"] == "primitive"
    assert c["version"] == "0.1.0"
    assert c["namespace"] == "katib"
    assert set(c["languages"]) == {"en", "ar"}


def test_signature_field_block_is_atomic():
    c = load_component("signature-field-block")
    assert c["page_behavior"]["mode"] == "atomic"


def test_signature_field_block_requires_parties():
    c = load_component("signature-field-block")
    input_names = {next(iter(inp.keys())) for inp in c["accepts"]["inputs"]}
    assert "parties" in input_names


# ---------------------------------------------------------------- render


def _minimal_recipe(tmp_path, sections_yaml):
    r = tmp_path / "sfb.yaml"
    r.write_text(
        "name: sfb-test\n"
        "version: 0.1.0\n"
        "namespace: katib\n"
        "languages: [en, ar]\n"
        "sections:\n"
        f"{sections_yaml}"
    )
    return r


def test_two_party_four_field_renders_en(tmp_path):
    r = _minimal_recipe(
        tmp_path,
        """  - component: signature-field-block
    inputs:
      parties:
        - label: "For Party A"
          name: "Acme | Katib"
          fields: ["Name", "Title", "Signature", "Date"]
        - label: "For Party B"
          name: "[Party B]"
          fields: ["Name", "Title", "Signature", "Date"]
""",
    )
    html, _ = compose(str(r), "en")
    assert html.count('class="katib-signature-field-block__party"') == 2
    # 4 field-label pairs × 2 parties = 8 total
    assert html.count('class="katib-signature-field-block__field"') == 8
    # grid columns computed from len(parties)
    assert "grid-template-columns: repeat(2, 1fr)" in html
    # atomic CSS emitted
    assert "#katib-section-0 { break-inside: avoid" in html
    # party labels and names present
    assert "For Party A" in html
    assert "Acme | Katib" in html


def test_single_party_renders(tmp_path):
    """Single-party form (e.g., client-acceptance-only acknowledgment)."""
    r = _minimal_recipe(
        tmp_path,
        """  - component: signature-field-block
    inputs:
      parties:
        - label: "For Client"
          fields: ["Signature", "Date"]
""",
    )
    html, _ = compose(str(r), "en")
    assert "grid-template-columns: repeat(1, 1fr)" in html
    assert html.count('class="katib-signature-field-block__field"') == 2
    # Empty party name omitted
    assert 'class="katib-signature-field-block__name"' not in html


def test_three_party_renders(tmp_path):
    """Three-party (e.g., tri-partite agreement) — grid expands."""
    r = _minimal_recipe(
        tmp_path,
        """  - component: signature-field-block
    inputs:
      parties:
        - label: "Party A"
          fields: ["Signature"]
        - label: "Party B"
          fields: ["Signature"]
        - label: "Witness"
          fields: ["Name", "Signature"]
""",
    )
    html, _ = compose(str(r), "en")
    assert "grid-template-columns: repeat(3, 1fr)" in html
    # 1 + 1 + 2 fields
    assert html.count('class="katib-signature-field-block__field"') == 4


def test_ar_render_reads_right_to_left(tmp_path):
    r = _minimal_recipe(
        tmp_path,
        """  - component: signature-field-block
    inputs:
      parties:
        - label: "الطرف الأول"
          name: "Acme | Katib"
          fields: ["الاسم", "الصفة", "التوقيع", "التاريخ"]
        - label: "الطرف الثاني"
          fields: ["الاسم", "الصفة", "التوقيع", "التاريخ"]
""",
    )
    html, _ = compose(str(r), "ar")
    assert 'lang="ar"' in html
    assert 'dir="rtl"' in html
    assert "الطرف الأول" in html
    assert "التوقيع" in html
    # 8 fields total
    assert html.count('class="katib-signature-field-block__field"') == 8
