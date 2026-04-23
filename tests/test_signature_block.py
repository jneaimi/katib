"""signature-block primitive — schema invariants + render behavior for signatories and addressees.

Phase 3 Day 3 upgrade: v0.1.0 → v0.2.0 added `organization` + `location` inputs
and a `recipient` variant for use as an addressee block (letter opener).
The primitive's conceptual role widened from "signatory" to "named party
in a document's context."
"""
from __future__ import annotations

from pathlib import Path

from core.compose import compose, load_component

REPO_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------- schema


def test_signature_block_loads_against_schema():
    c = load_component("signature-block")
    assert c["tier"] == "primitive"
    assert c["version"] == "0.2.0"
    assert c["namespace"] == "katib"
    assert set(c["languages"]) == {"en", "ar"}


def test_signature_block_new_fields_present():
    c = load_component("signature-block")
    input_names = {next(iter(inp.keys())) for inp in c["accepts"]["inputs"]}
    # 0.2.0 additions
    assert "organization" in input_names
    assert "location" in input_names
    # Pre-existing fields unchanged
    assert "name" in input_names
    assert "title" in input_names
    assert "date" in input_names


def test_signature_block_recipient_variant_declared():
    c = load_component("signature-block")
    variants = c.get("variants", [])
    # 0.2.0 adds recipient; pre-existing variants stay
    assert "recipient" in variants
    assert "line-over" in variants
    assert "label-prefix" in variants


def test_signature_block_new_fields_optional():
    """Backwards compatibility: organization + location must stay optional so
    existing pre-0.2.0 recipes (providing only name/title/date) keep working."""
    c = load_component("signature-block")
    for field_name in ("organization", "location"):
        decl = next(
            (next(iter(inp.values())) for inp in c["accepts"]["inputs"] if field_name in inp),
            None,
        )
        assert decl is not None, f"{field_name} missing from schema"
        assert decl["required"] is False


# ---------------------------------------------------------------- render


def _inline_recipe(
    tmp_path: Path,
    *,
    variant: str | None = None,
    lang: str = "en",
    name: str = "Jasem Al Neaimi",
    title: str | None = "Managing Director",
    organization: str | None = None,
    location: str | None = None,
) -> Path:
    variant_line = f"    variant: {variant}\n" if variant else ""
    inputs = [f'      name: "{name}"']
    if title:
        inputs.append(f'      title: "{title}"')
    if organization:
        inputs.append(f'      organization: "{organization}"')
    if location:
        inputs.append(f'      location: "{location}"')
    input_block = "\n".join(inputs)
    rfile = tmp_path / "sig.yaml"
    rfile.write_text(
        "name: sig-test\n"
        "version: 0.1.0\n"
        "namespace: katib\n"
        f"languages: [{lang}]\n"
        "sections:\n"
        "  - component: signature-block\n"
        + variant_line +
        "    inputs:\n"
        + input_block + "\n"
    )
    return rfile


def test_signature_block_renders_default_signatory(tmp_path):
    rfile = _inline_recipe(tmp_path)
    html, _ = compose(str(rfile), "en")
    # Default variant is line-over
    assert "katib-signature--line-over" in html
    # No "Signed" label element under line-over (the class appears in inlined <style>;
    # check the actual div element)
    assert '<div class="katib-signature__label">' not in html
    assert "Jasem Al Neaimi" in html
    assert "Managing Director" in html


def test_signature_block_renders_recipient_with_full_fields(tmp_path):
    rfile = _inline_recipe(
        tmp_path,
        variant="recipient",
        name="Ms. Sara Al-Hashimi",
        title="VP of Learning & Development",
        organization="ACME Corp",
        location="Dubai, United Arab Emirates",
    )
    html, _ = compose(str(rfile), "en")
    assert "katib-signature--recipient" in html
    # No "Signed" label under recipient variant
    assert '<div class="katib-signature__label">' not in html
    # All four fields render
    assert "Ms. Sara Al-Hashimi" in html
    assert "VP of Learning &amp; Development" in html or "VP of Learning & Development" in html
    assert "ACME Corp" in html
    assert "Dubai, United Arab Emirates" in html
    # Field-specific CSS classes emitted
    assert "katib-signature__organization" in html
    assert "katib-signature__location" in html


def test_signature_block_label_prefix_still_works(tmp_path):
    """Regression guard: label-prefix variant unchanged by 0.2.0 extension."""
    rfile = _inline_recipe(tmp_path, variant="label-prefix")
    html, _ = compose(str(rfile), "en")
    assert "katib-signature--label-prefix" in html
    # label-prefix DOES render the label (unlike line-over and recipient)
    assert '<div class="katib-signature__label">' in html
    assert "Signed" in html


def test_signature_block_recipient_bilingual(tmp_path):
    """RTL cascade works for recipient variant too."""
    rfile = _inline_recipe(
        tmp_path,
        variant="recipient",
        lang="ar",
        name="السيدة سارة الهاشمي",
        title="نائب الرئيس للتدريب والتطوير",
        organization="شركة أكمي",
        location="دبي، الإمارات العربية المتحدة",
    )
    html, _ = compose(str(rfile), "ar")
    assert 'dir="rtl"' in html
    assert "katib-signature--recipient" in html
    assert "السيدة سارة الهاشمي" in html
    assert "شركة أكمي" in html


def test_signature_block_without_optional_fields_still_renders(tmp_path):
    """Minimal recipe — only required `name` field."""
    rfile = _inline_recipe(tmp_path, title=None)
    html, _ = compose(str(rfile), "en")
    assert "Jasem Al Neaimi" in html
    # No title element when unset (the class name appears in inlined <style>; check for the div)
    assert '<div class="katib-signature__title">' not in html
    assert '<div class="katib-signature__organization">' not in html
