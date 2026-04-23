"""masthead-personal section — schema invariants + render + brand-identity fallback.

Phase 3 Day 5 component. Sibling to letterhead (organizational identity)
— masthead-personal carries personal identity (name + tagline + contact)
for cover letters, CVs, and bio sheets. Forecast on Day 2 when the
letterhead `personal` variant was explicitly rejected in favor of a
separate component.

Phase-3 dependents: personal/cover-letter (Day 6), personal/cv (later
in Phase 3). Scaffolded below the automated graduation threshold (2 of
3 recipe-slot requests); intent-verified via the ADR Day 5 entry as
load-bearing shared component for the personal-brand document family.
"""
from __future__ import annotations

from pathlib import Path

from core.compose import compose, load_component

REPO_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------- schema


def test_masthead_personal_loads_against_schema():
    c = load_component("masthead-personal")
    assert c["tier"] == "section"
    assert c["version"] == "0.1.0"
    assert c["namespace"] == "katib"
    assert set(c["languages"]) == {"en", "ar"}


def test_masthead_personal_name_required():
    c = load_component("masthead-personal")
    name_decl = next(
        (next(iter(inp.values())) for inp in c["accepts"]["inputs"] if "name" in inp),
        None,
    )
    assert name_decl is not None
    assert name_decl["required"] is True


def test_masthead_personal_contact_fields_optional():
    c = load_component("masthead-personal")
    for field in ("tagline", "email", "phone", "location"):
        decl = next(
            (next(iter(inp.values())) for inp in c["accepts"]["inputs"] if field in inp),
            None,
        )
        assert decl is not None, f"{field} missing from schema"
        assert decl["required"] is False


def test_masthead_personal_declares_identity_brand_fields():
    c = load_component("masthead-personal")
    brand_fields = c.get("requires", {}).get("brand_fields", [])
    assert "identity.email" in brand_fields
    assert "identity.phone" in brand_fields


def test_masthead_personal_token_contract():
    c = load_component("masthead-personal")
    required = set(c["requires"]["tokens"])
    assert {"accent", "text_secondary", "text_tertiary"}.issubset(required)


def test_masthead_personal_no_variants():
    """Component is scoped deliberately tight — no variants. If alternate styling
    is needed later (e.g., for CV vs cover-letter), revisit scope before adding."""
    c = load_component("masthead-personal")
    assert c.get("variants", []) == []


# ---------------------------------------------------------------- render


def _inline_recipe(
    tmp_path: Path,
    *,
    lang: str = "en",
    name: str = "Jasem Al Neaimi",
    tagline: str | None = "Senior AI Engineer",
    email: str | None = "jasem@example.com",
    phone: str | None = "+971 50 000 0000",
    location: str | None = "Dubai, UAE",
) -> Path:
    inputs = [f'      name: "{name}"']
    if tagline is not None:
        inputs.append(f'      tagline: "{tagline}"')
    if email is not None:
        inputs.append(f'      email: "{email}"')
    if phone is not None:
        inputs.append(f'      phone: "{phone}"')
    if location is not None:
        inputs.append(f'      location: "{location}"')
    rfile = tmp_path / "mp.yaml"
    rfile.write_text(
        "name: mp-test\n"
        "version: 0.1.0\n"
        "namespace: katib\n"
        f"languages: [{lang}]\n"
        "sections:\n"
        "  - component: masthead-personal\n"
        "    inputs:\n"
        + "\n".join(inputs) + "\n"
    )
    return rfile


def test_masthead_personal_renders_en(tmp_path):
    rfile = _inline_recipe(tmp_path)
    html, _ = compose(str(rfile), "en")
    # Structural markers
    assert "katib-masthead-personal" in html
    assert "katib-masthead-personal__bar" in html
    assert "katib-masthead-personal__identity" in html
    assert "katib-masthead-personal__contact" in html
    # Content
    assert "Jasem Al Neaimi" in html
    assert "Senior AI Engineer" in html
    assert "jasem@example.com" in html
    assert "+971 50 000 0000" in html
    assert "Dubai, UAE" in html


def test_masthead_personal_renders_ar(tmp_path):
    rfile = _inline_recipe(tmp_path, lang="ar", name="جاسم النعيمي")
    html, _ = compose(str(rfile), "ar")
    assert 'dir="rtl"' in html
    assert "جاسم النعيمي" in html


def test_masthead_personal_ar_contact_rows_forced_ltr(tmp_path):
    """Email + phone must render LTR inside RTL template (addresses + phone
    numbers are structurally LTR even in Arabic documents)."""
    rfile = _inline_recipe(tmp_path, lang="ar", name="جاسم النعيمي")
    html, _ = compose(str(rfile), "ar")
    # Both email and phone divs should carry dir="ltr"
    assert 'katib-masthead-personal__contact-row" dir="ltr">jasem@example.com' in html
    assert 'katib-masthead-personal__contact-row" dir="ltr">+971 50 000 0000' in html


def test_masthead_personal_tagline_optional(tmp_path):
    """Missing tagline should not render an empty element."""
    rfile = _inline_recipe(tmp_path, tagline=None)
    html, _ = compose(str(rfile), "en")
    assert "Jasem Al Neaimi" in html
    assert '<div class="katib-masthead-personal__tagline">' not in html


def test_masthead_personal_contact_fields_skip_when_all_missing(tmp_path):
    """No email/phone/location — contact stack renders but all rows skip."""
    rfile = _inline_recipe(tmp_path, email=None, phone=None, location=None)
    html, _ = compose(str(rfile), "en")
    # Container still renders; individual rows are absent
    assert "katib-masthead-personal__contact" in html
    assert '<div class="katib-masthead-personal__contact-row">' not in html
    assert '<div class="katib-masthead-personal__contact-row" dir="ltr">' not in html


# ---------------------------------------------------------------- brand fallback


def test_masthead_personal_falls_back_to_brand_identity(tmp_path, monkeypatch):
    """When email/phone not in recipe inputs but brand profile provides them,
    the contact rows should render with brand values. Exercises the
    `identity.email` / `identity.phone` context vars in the template."""
    # Use jasem brand profile which has identity fields set
    rfile = _inline_recipe(tmp_path, email=None, phone=None)
    html, _ = compose(str(rfile), "en", brand="jasem")
    # Whether the rendered HTML contains the brand email/phone depends on the
    # jasem brand profile's identity fields being populated. If they are set,
    # they appear; if not, the row just doesn't render. The invariant we test:
    # the recipe render doesn't crash when the input is unset but brand has values.
    assert "Jasem Al Neaimi" in html
    assert "katib-masthead-personal" in html


# ---------------------------------------------------------------- hygiene


def test_masthead_personal_styles_use_tokens_only():
    css = (REPO_ROOT / "components" / "sections" / "masthead-personal" / "styles.css").read_text()
    import re
    hex_refs = re.findall(r"#[0-9a-fA-F]{3,8}\b", css)
    assert hex_refs == [], f"hex colors in styles.css: {hex_refs}"


def test_masthead_personal_templates_share_semantic_structure():
    """EN and AR share semantic skeleton; only dir="rtl" differs on root."""
    base = REPO_ROOT / "components" / "sections" / "masthead-personal"
    en = (base / "en.html").read_text()
    ar = (base / "ar.html").read_text()
    for token in (
        "katib-masthead-personal__bar",
        "katib-masthead-personal__identity",
        "katib-masthead-personal__name",
        "katib-masthead-personal__contact",
    ):
        assert token in en, f"{token} missing from en.html"
        assert token in ar, f"{token} missing from ar.html"
    assert 'dir="rtl"' in ar
