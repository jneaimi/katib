"""code-block primitive — schema invariants + render behavior.

Terminal (dark zinc) + inline (theme-aware light) variants for CLI /
command reference blocks. Accepts raw HTML in `code` input for inline
comment spans. Atomic — blocks never split across pages.
"""
from __future__ import annotations

from pathlib import Path

from core.compose import compose, load_component

REPO_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------- schema


def test_code_block_loads_against_schema():
    c = load_component("code-block")
    assert c["tier"] == "primitive"
    assert c["version"] == "0.1.0"
    assert c["namespace"] == "katib"
    assert set(c["languages"]) == {"en", "ar"}


def test_code_block_is_atomic():
    c = load_component("code-block")
    assert c["page_behavior"]["mode"] == "atomic"


def test_code_block_has_two_variants():
    c = load_component("code-block")
    assert set(c["variants"]) == {"terminal", "inline"}


# ---------------------------------------------------------------- render


def _recipe(tmp_path, section_yaml):
    r = tmp_path / "cb.yaml"
    r.write_text(
        "name: cb-test\n"
        "version: 0.1.0\n"
        "namespace: katib\n"
        "languages: [en, ar]\n"
        "sections:\n"
        f"{section_yaml}"
    )
    return r


def test_terminal_variant_renders_with_dark_bg(tmp_path):
    r = _recipe(
        tmp_path,
        """  - component: code-block
    variant: terminal
    inputs:
      code: "git clone https://github.com/jneaimi/katib.git"
""",
    )
    html, _ = compose(str(r), "en")
    assert "katib-code-block--terminal" in html
    # CSS rule for terminal background should be inlined
    assert "#27272A" in html
    assert "git clone" in html


def test_inline_variant_renders_with_theme_bg(tmp_path):
    r = _recipe(
        tmp_path,
        """  - component: code-block
    variant: inline
    inputs:
      code: "deploy rollback --to abc123"
""",
    )
    html, _ = compose(str(r), "en")
    assert "katib-code-block--inline" in html
    assert "deploy rollback" in html


def test_comment_span_passes_through_as_safe_html(tmp_path):
    """Recipes may embed <span class='katib-code-block__comment'> for inline
    comment styling. Jinja | safe must not escape the markup."""
    r = _recipe(
        tmp_path,
        """  - component: code-block
    variant: terminal
    inputs:
      code: |
        <span class="katib-code-block__comment"># install</span>
        uv run scripts/build.py
""",
    )
    html, _ = compose(str(r), "en")
    assert 'class="katib-code-block__comment"' in html
    # Should NOT be escaped
    assert "&lt;span" not in html


def test_label_renders_when_supplied(tmp_path):
    r = _recipe(
        tmp_path,
        """  - component: code-block
    variant: terminal
    inputs:
      label: "~/.config/katib/config.yaml"
      code: "output: vault"
""",
    )
    html, _ = compose(str(r), "en")
    assert 'class="katib-code-block__label"' in html
    assert "~/.config/katib/config.yaml" in html


def test_label_omitted_when_absent(tmp_path):
    r = _recipe(
        tmp_path,
        """  - component: code-block
    variant: terminal
    inputs:
      code: "ls -la"
""",
    )
    html, _ = compose(str(r), "en")
    # Class name appears in the CSS <style> block regardless; check for the
    # HTML element attribute specifically.
    assert 'class="katib-code-block__label"' not in html


def test_default_variant_is_terminal(tmp_path):
    """Variant defaults to terminal when not specified."""
    r = _recipe(
        tmp_path,
        """  - component: code-block
    inputs:
      code: "echo hello"
""",
    )
    html, _ = compose(str(r), "en")
    assert "katib-code-block--terminal" in html


def test_atomic_pagination_css_emitted(tmp_path):
    r = _recipe(
        tmp_path,
        """  - component: code-block
    inputs:
      code: "echo hi"
""",
    )
    html, _ = compose(str(r), "en")
    assert "#katib-section-0 { break-inside: avoid" in html


def test_ar_render_keeps_code_ltr(tmp_path):
    """Code always renders LTR regardless of document direction."""
    r = _recipe(
        tmp_path,
        """  - component: code-block
    inputs:
      code: "uv run scripts/build.py tutorial --lang ar"
""",
    )
    html, _ = compose(str(r), "ar")
    assert 'dir="rtl"' in html  # document-level RTL still present
    assert 'dir="ltr"' in html  # code-block forces LTR on its wrapper
