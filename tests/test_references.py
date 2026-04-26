"""Guard that katib's writing references are present and non-empty.

These references are the human-judgement layer of the content quality gate
(brand voice, MSA grammar, anti-slop, 5-dimension score). They sit on top of
core/content_lint.py's mechanical checks. If they go missing, recipe authors
silently fall back to the external /arabic Claude Code skill, which isn't
available to npm-installed users — breaking katib's self-sufficiency.
"""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_writing_ar_present():
    p = REPO_ROOT / "references" / "writing.ar.md"
    assert p.exists(), (
        "katib references/writing.ar.md missing — required for self-sustained "
        "Arabic content quality gate"
    )
    assert p.stat().st_size > 5000, "writing.ar.md appears truncated"


def test_writing_en_present():
    p = REPO_ROOT / "references" / "writing.en.md"
    assert p.exists()
    assert p.stat().st_size > 2000


def test_references_index_present():
    p = REPO_ROOT / "references" / "README.md"
    assert p.exists()
