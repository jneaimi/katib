"""personal-cv recipe — thirteenth Phase-3 recipe; FIRST production consumer
of cv-layout + skill-bar-list + tag-chips (all Day-18 infra, 24-hour ship
discipline — 4th consecutive application).

SINGLE-SECTION recipe — fewest sections ever in a Phase-3 recipe (1 vs.
mou's 25). All CV content lives inside cv-layout's sidebar_html +
main_html raw-HTML inputs. Primitive CSS auto-loads via
compose's _load_primitive_styles() so inline `katib-skill-bar-list` +
`katib-tag-chips` class usage renders correctly.

Closes the personal domain (cover-letter Day 6 + cv Day 19) — 3rd
complete domain after business-proposal and financial.

Content adapted from v1-reference/domains/personal/templates/cv.en.html.
Placeholder prose preserved.

Renders to 2 pages; target_pages [1, 2], page_limit 2.

AR variant deferred — pending inputs_by_lang schema resolution.
"""
from __future__ import annotations

from pathlib import Path

import yaml
from pypdf import PdfReader

from core import recipe_ops as ops
from core.compose import compose, load_recipe
from core.render import render_to_pdf

REPO_ROOT = Path(__file__).resolve().parent.parent
RECIPE_NAME = "personal-cv"


# ---------------------------------------------------------------- schema


def test_cv_loads():
    r = load_recipe(RECIPE_NAME)
    assert r["name"] == RECIPE_NAME
    assert r["namespace"] == "katib"
    assert r["version"] == "0.1.0"


def test_cv_en_only():
    r = load_recipe(RECIPE_NAME)
    assert r["languages"] == ["en"]


def test_cv_page_targets():
    r = load_recipe(RECIPE_NAME)
    assert r["target_pages"] == [1, 2]
    assert r["page_limit"] == 2


def test_cv_is_single_section():
    """FEWEST SECTIONS EVER in Phase-3 — 1 section (cv-layout).
    All content lives in sidebar_html + main_html raw inputs."""
    r = load_recipe(RECIPE_NAME)
    assert len(r["sections"]) == 1
    assert r["sections"][0]["component"] == "cv-layout"


# ---------------------------------------------------------------- production proofs


def test_cv_is_first_cv_layout_consumer():
    """FIRST production consumer of cv-layout (Day-18 built → Day-19 shipped
    = 24-hour ship discipline, 4th consecutive application after
    sections-grid Day 11→12, data-table Day 13→14, financial-summary
    Day 15→16)."""
    r = load_recipe(RECIPE_NAME)
    layout = r["sections"][0]
    assert layout["component"] == "cv-layout"
    assert "sidebar_html" in layout["inputs"]
    assert "main_html" in layout["inputs"]


def test_cv_sidebar_html_has_skill_bar_list_inline():
    """FIRST production consumer of skill-bar-list — used INLINE in
    cv-layout's sidebar_html via primitive class names. Primitive CSS
    auto-loads via compose's _load_primitive_styles()."""
    r = load_recipe(RECIPE_NAME)
    sidebar = r["sections"][0]["inputs"]["sidebar_html"]
    # Two skill-bar-list uses: Languages + Core Skills
    assert sidebar.count('class="katib-skill-bar-list"') == 2
    # Level modifier classes
    assert "katib-skill-bar-list__level--l5" in sidebar  # Language proficiency
    assert "katib-skill-bar-list__level--l4" in sidebar  # Core skill proficiency
    assert "katib-skill-bar-list__level--l3" in sidebar
    # Skill items
    assert sidebar.count('katib-skill-bar-list__item') == 6  # 2 langs + 4 skills


def test_cv_sidebar_html_has_tag_chips_inline():
    """FIRST production consumer of tag-chips — used INLINE in
    cv-layout's sidebar_html for Tools section."""
    r = load_recipe(RECIPE_NAME)
    sidebar = r["sections"][0]["inputs"]["sidebar_html"]
    assert 'class="katib-tag-chips"' in sidebar
    # 4 tool chips
    assert sidebar.count("katib-tag-chips__chip") == 4


def test_cv_sidebar_has_all_identity_sections():
    """Sidebar contains Contact + Personal + Languages + Core Skills + Tools
    sections in that order."""
    r = load_recipe(RECIPE_NAME)
    sidebar = r["sections"][0]["inputs"]["sidebar_html"]
    # All 5 sidebar section headings
    for heading in ("Contact", "Personal", "Languages", "Core Skills", "Tools"):
        assert f"<h3>{heading}</h3>" in sidebar


def test_cv_main_html_has_four_main_sections():
    """Main column contains Summary + Experience + Education + Selected Projects."""
    r = load_recipe(RECIPE_NAME)
    main = r["sections"][0]["inputs"]["main_html"]
    for heading in ("Summary", "Experience", "Education", "Selected Projects"):
        assert f"<h2>{heading}</h2>" in main


def test_cv_main_html_has_three_experience_entries():
    """v1 CV has 3 experience entries (most-recent + previous + earlier)."""
    r = load_recipe(RECIPE_NAME)
    main = r["sections"][0]["inputs"]["main_html"]
    # Count cv-entry divs in main (experience section has 3, projects has 1 = 4 total)
    import re
    entries = re.findall(r'class="cv-entry"', main)
    assert len(entries) == 4  # 3 experience + 1 project


def test_cv_main_html_has_two_education_entries():
    """v1 CV has 2 education entries."""
    r = load_recipe(RECIPE_NAME)
    main = r["sections"][0]["inputs"]["main_html"]
    import re
    entries = re.findall(r'class="cv-edu-entry"', main)
    assert len(entries) == 2


# ---------------------------------------------------------------- validation + content-lint


def test_cv_validates_clean():
    v = ops.validate_recipe_full(RECIPE_NAME)
    assert v.ok, f"validation failed: {[i.message for i in v.issues]}"


def test_cv_validates_strict_clean():
    v = ops.validate_recipe_full(RECIPE_NAME, strict=True)
    assert v.ok, f"strict validation failed: {[i.message for i in v.issues]}"
    content_issues = [i for i in v.issues if i.category == "content"]
    assert content_issues == []


# ---------------------------------------------------------------- render + content


def test_cv_renders_en():
    html, _ = compose(RECIPE_NAME, "en")
    # cv-layout grid structure
    assert "katib-cv-layout" in html
    assert "katib-cv-layout__sidebar" in html
    assert "katib-cv-layout__main" in html
    # Primitive classes (inline in sidebar_html)
    assert "katib-skill-bar-list" in html
    assert "katib-tag-chips" in html


def test_cv_pdf_within_target_pages(tmp_path):
    """target_pages [1, 2]; renders to 1-2 pages with placeholder content."""
    html, _ = compose(RECIPE_NAME, "en")
    pdf = render_to_pdf(html, tmp_path / "cv.en.pdf", base_url=REPO_ROOT)
    assert pdf.exists()
    reader = PdfReader(str(pdf))
    assert 1 <= len(reader.pages) <= 2


def test_cv_renders_all_v1_content(tmp_path):
    """Every fixed phrase from v1 CV should survive to the PDF."""
    import re
    html, _ = compose(RECIPE_NAME, "en")
    pdf = render_to_pdf(html, tmp_path / "cv.en.pdf", base_url=REPO_ROOT)
    raw = "\n".join(p.extract_text() or "" for p in PdfReader(str(pdf)).pages)
    flat = re.sub(r"\s+", " ", raw).strip()

    # Name + identity
    assert "Jasem Al Neaimi" in flat
    assert "Professional Headline" in flat
    # Contact labels (uppercased by sidebar CSS)
    for label in ("Email", "Phone", "Location", "Portfolio", "LinkedIn"):
        assert label.upper() in flat.upper(), f"contact label missing: {label}"
    # Personal labels
    for label in ("Nationality", "Visa Status", "Date of Birth"):
        assert label.upper() in flat.upper(), f"personal label missing: {label}"
    # Sidebar section headings (uppercased by sidebar CSS)
    for heading in ("Contact", "Personal", "Languages", "Core Skills", "Tools"):
        assert heading.upper() in flat.upper(), f"sidebar heading missing: {heading}"
    # Languages
    assert "English" in flat
    assert "Arabic" in flat
    # Main section headings (uppercased by main-column CSS)
    for heading in ("Summary", "Experience", "Education", "Selected Projects"):
        assert heading.upper() in flat.upper(), f"main heading missing: {heading}"
    # Placeholders preserved
    assert "AI engineer" in flat  # from Summary example
    assert "Company Name" in flat  # Experience placeholder
    assert "University Name" in flat  # Education placeholder


def test_cv_has_two_skill_bar_list_uls_in_html():
    """Regression guard: Languages + Core Skills = 2 skill-bar-list uls."""
    import re
    html, _ = compose(RECIPE_NAME, "en")
    matches = re.findall(r'<ul class="katib-skill-bar-list"', html)
    assert len(matches) == 2


def test_cv_has_one_tag_chips_ul_in_html():
    """Regression guard: Tools = 1 tag-chips ul."""
    import re
    html, _ = compose(RECIPE_NAME, "en")
    matches = re.findall(r'<ul class="katib-tag-chips"', html)
    assert len(matches) == 1


def test_cv_has_six_skill_items_in_html():
    """Regression guard: 2 languages + 4 core skills = 6 skill-bar-list items."""
    import re
    html, _ = compose(RECIPE_NAME, "en")
    matches = re.findall(r'class="katib-skill-bar-list__item"', html)
    assert len(matches) == 6


def test_cv_has_four_tag_chips_in_html():
    """Regression guard: 4 tool chips."""
    import re
    html, _ = compose(RECIPE_NAME, "en")
    matches = re.findall(r'class="katib-tag-chips__chip"', html)
    assert len(matches) == 4


def test_cv_has_grid_layout_in_html():
    """Regression guard: cv-layout grid declaration present in rendered HTML."""
    html, _ = compose(RECIPE_NAME, "en")
    assert "grid-template-columns: 70mm 1fr" in html


def test_cv_sidebar_has_photo_slot():
    """Regression guard: photo placeholder slot in sidebar (styled circular div)."""
    html, _ = compose(RECIPE_NAME, "en")
    assert 'class="cv-photo"' in html
    assert "border-radius: 50%" in html


# ---------------------------------------------------------------- audit + registration


def test_cv_in_capabilities():
    caps_path = REPO_ROOT / "capabilities.yaml"
    caps = yaml.safe_load(caps_path.read_text(encoding="utf-8"))
    recipes = caps.get("recipes", {})
    assert RECIPE_NAME in recipes
    assert recipes[RECIPE_NAME]["namespace"] == "katib"


def test_cv_audit_entry_exists():
    audit = (REPO_ROOT / "memory" / "recipe-audit.jsonl").read_text(encoding="utf-8")
    import json
    lines = [json.loads(line) for line in audit.splitlines() if line.strip()]
    register_entries = [
        e for e in lines
        if e.get("recipe") == RECIPE_NAME and e.get("action") == "register"
    ]
    assert len(register_entries) >= 1
