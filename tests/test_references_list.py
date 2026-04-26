"""references-list section — URL hyperlink contract.

Bibliographic entries with a `url` field must render the URL inside an
`<a href>` element, not a `<span>`. Caught in the wild on a journalism
document where citation URLs looked correct on the page but were dead
text in the rendered PDF — the component contract documented hyperlinks
but the template emitted spans.
"""
from __future__ import annotations

from pathlib import Path

from core.compose import compose

REPO_ROOT = Path(__file__).resolve().parent.parent


def _inline_recipe(tmp_path: Path, lang: str = "en") -> Path:
    rfile = tmp_path / "rl.yaml"
    rfile.write_text(
        "name: rl-test\n"
        "version: 0.1.0\n"
        "namespace: katib\n"
        f"languages: [{lang}]\n"
        "sections:\n"
        "  - component: references-list\n"
        "    inputs:\n"
        "      title: \"References\"\n"
        "      entries:\n"
        "        - authors: \"Al Neaimi, J.\"\n"
        "          year: 2026\n"
        "          title: \"Bilingual print for the AI era\"\n"
        "          source: \"Katib internal notes\"\n"
        "          url: \"https://example.com/one\"\n"
        "        - authors: \"W3C\"\n"
        "          year: 2024\n"
        "          title: \"CSS Paged Media Module Level 3\"\n"
        "          source: \"w3.org/TR/css-page-3\"\n"
        "          url: \"https://example.com/two\"\n"
        "        - authors: \"CourtBouillon\"\n"
        "          year: 2025\n"
        "          title: \"WeasyPrint documentation\"\n"
        "          source: \"doc.courtbouillon.org\"\n"
        "          url: \"https://example.com/three\"\n"
    )
    return rfile


def test_references_list_urls_render_as_anchor_en(tmp_path):
    """EN render: every entry.url emits a real <a href> hyperlink, not
    a <span>. PDFs need clickable links to satisfy the citation contract."""
    rfile = _inline_recipe(tmp_path, lang="en")
    html, _ = compose(str(rfile), "en")

    for url in (
        "https://example.com/one",
        "https://example.com/two",
        "https://example.com/three",
    ):
        assert f'href="{url}"' in html, f"URL {url!r} not rendered as href in EN"

    assert '<a class="katib-references-list__url"' in html, \
        "EN template emits URLs as <a>, not <span>"
    assert '<span class="katib-references-list__url"' not in html, \
        "EN template still emits URLs as dead <span> — fix not applied"


def test_references_list_urls_render_as_anchor_ar(tmp_path):
    """AR render: same hyperlink contract holds in RTL."""
    rfile = _inline_recipe(tmp_path, lang="ar")
    html, _ = compose(str(rfile), "ar")

    for url in (
        "https://example.com/one",
        "https://example.com/two",
        "https://example.com/three",
    ):
        assert f'href="{url}"' in html, f"URL {url!r} not rendered as href in AR"

    assert '<a class="katib-references-list__url"' in html, \
        "AR template emits URLs as <a>, not <span>"
    assert '<span class="katib-references-list__url"' not in html, \
        "AR template still emits URLs as dead <span> — fix not applied"
