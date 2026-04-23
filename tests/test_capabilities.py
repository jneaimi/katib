"""Phase 2 Day 8 — capabilities loader + recipe ranker."""
from __future__ import annotations

from pathlib import Path

import pytest

from core.capabilities import (
    _tokenize,
    find_closest_recipe,
    load_capabilities,
    rank_recipes,
)

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_load_capabilities_real_file():
    caps = load_capabilities()
    assert "recipes" in caps
    assert "components" in caps
    # tutorial.yaml from Day 7 should be present
    assert "tutorial" in caps["recipes"]


def test_load_capabilities_raises_on_missing(tmp_path):
    with pytest.raises(FileNotFoundError, match="capabilities.yaml not found"):
        load_capabilities(tmp_path / "nope.yaml")


def test_tokenize_drops_stopwords_and_short():
    assert _tokenize("the quick brown fox") == ["quick", "brown", "fox"]
    assert _tokenize("") == []
    assert _tokenize("a") == []           # below min-length
    assert _tokenize("in on at") == []    # all stopwords


def test_tokenize_handles_kebab_and_punctuation():
    assert _tokenize("chart-donut showcase!") == ["chart", "donut", "showcase"]


def test_rank_tutorial_for_framework_intent():
    caps = load_capabilities()
    matches = rank_recipes("I want a framework tutorial guide", caps, top_k=3)
    names = [m.name for m in matches]
    assert "tutorial" in names
    # tutorial should rank high because both keyword and desc match
    assert matches[0].name == "tutorial"
    assert matches[0].score > 0.3


def test_rank_name_exact_dominates():
    caps = load_capabilities()
    matches = rank_recipes("run the tutorial", caps, top_k=3)
    assert matches[0].name == "tutorial"


def test_rank_keyword_overlap():
    caps = load_capabilities()
    matches = rank_recipes("chart sparkline showcase", caps, top_k=3)
    names = [m.name for m in matches]
    assert "phase-2-day6-showcase" in names


def test_rank_returns_empty_on_no_overlap():
    caps = load_capabilities()
    # Gibberish should produce zero matches
    matches = rank_recipes("xyzzyzzy nothing-here-blarg", caps, top_k=3)
    assert matches == []


def test_rank_respects_top_k():
    caps = load_capabilities()
    # Very generic intent — should match many
    matches = rank_recipes("showcase phase", caps, top_k=2)
    assert len(matches) <= 2


def test_find_closest_returns_single_or_none():
    caps = load_capabilities()
    m = find_closest_recipe("framework tutorial guide", caps)
    assert m is not None
    assert m.name == "tutorial"

    m = find_closest_recipe("asdflkjasdf", caps)
    assert m is None


def test_rank_empty_caps():
    assert rank_recipes("anything", {"recipes": {}}) == []
    assert rank_recipes("anything", {}) == []


def test_rank_reasons_populated_for_matches():
    caps = load_capabilities()
    matches = rank_recipes("tutorial framework", caps, top_k=1)
    assert matches
    assert matches[0].reasons, "reasons list should be non-empty for matches"
