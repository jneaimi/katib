"""Capabilities index loader + recipe ranker.

The gate and context-sensor consult `capabilities.yaml` — the auto-generated
flat map of what Katib can do right now — before making any routing
decision. This module provides the in-process loader and a deterministic
keyword-based ranker for matching user intent to recipes.

No LLM dependency. Ranking is pure token-overlap with configurable weights
so tests can assert ranks without locking exact scores.

Public API:
    load_capabilities(path=None) -> dict
    rank_recipes(intent, caps, top_k=3) -> list[RecipeMatch]
    find_closest_recipe(intent, caps) -> RecipeMatch | None
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

CORE_DIR = Path(__file__).resolve().parent
REPO_ROOT = CORE_DIR.parent
DEFAULT_CAPS_FILE = REPO_ROOT / "capabilities.yaml"

# Common English stopwords that muddy keyword matching. Kept minimal —
# domain-specific terms (e.g., "guide", "recipe") are intentionally NOT
# stopped because they carry routing signal.
_STOPWORDS = frozenset(
    {
        "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
        "has", "have", "i", "in", "is", "it", "its", "of", "on", "or",
        "that", "the", "this", "to", "was", "were", "will", "with",
        "my", "me", "we", "you", "your", "our",
    }
)

# Weights for the final recipe score. Must sum to 1.0.
_W_NAME = 0.40
_W_KEYWORDS = 0.30
_W_WHEN_DESC = 0.20
_W_SECTIONS = 0.10


@dataclass
class RecipeMatch:
    name: str
    score: float                          # 0.0 – 1.0
    reasons: list[str] = field(default_factory=list)
    data: dict = field(default_factory=dict)   # raw recipe block from caps


def load_capabilities(path: Path | str | None = None) -> dict:
    p = Path(path) if path else DEFAULT_CAPS_FILE
    if not p.exists():
        raise FileNotFoundError(
            f"capabilities.yaml not found at {p}. "
            f"Run: uv run scripts/generate_capabilities.py"
        )
    data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    return data


def _tokenize(text: str) -> list[str]:
    """Lowercase, split on non-word, drop stopwords, keep kebab parts."""
    if not text:
        return []
    lowered = text.lower()
    # Split on non-letter/digit, then also split kebab-style words into parts
    raw = re.split(r"[^a-z0-9؀-ۿ]+", lowered)
    tokens: list[str] = []
    for tok in raw:
        if not tok:
            continue
        # kebab: "chart-donut" already comes pre-split; if it was an underscore
        # or dotted name it's already split by the regex above
        if tok in _STOPWORDS:
            continue
        if len(tok) < 2:
            continue
        tokens.append(tok)
    return tokens


def _name_score(intent_tokens: set[str], recipe_name: str) -> tuple[float, list[str]]:
    """How well the intent matches the recipe name."""
    reasons: list[str] = []
    if not intent_tokens:
        return 0.0, reasons
    name_tokens = set(_tokenize(recipe_name))
    if not name_tokens:
        return 0.0, reasons
    # Exact-name match (rare but strong)
    if recipe_name.lower() in " ".join(intent_tokens):
        reasons.append(f"name exact substring: {recipe_name!r}")
        return 1.0, reasons
    # Token overlap as ratio of name tokens covered
    shared = intent_tokens & name_tokens
    if not shared:
        return 0.0, reasons
    overlap = len(shared) / len(name_tokens)
    reasons.append(f"name tokens matched: {sorted(shared)} ({overlap:.0%})")
    return overlap, reasons


def _keyword_score(
    intent_tokens: set[str], recipe_keywords: list[str]
) -> tuple[float, list[str]]:
    reasons: list[str] = []
    if not intent_tokens or not recipe_keywords:
        return 0.0, reasons
    kw_token_set: set[str] = set()
    for kw in recipe_keywords:
        kw_token_set.update(_tokenize(kw))
    if not kw_token_set:
        return 0.0, reasons
    shared = intent_tokens & kw_token_set
    if not shared:
        return 0.0, reasons
    # Normalize by recipe-side (how many of its keywords matched)
    ratio = len(shared) / len(kw_token_set)
    reasons.append(f"keyword overlap: {sorted(shared)}")
    return min(ratio, 1.0), reasons


def _when_desc_score(
    intent_tokens: set[str], when: str, description: str
) -> tuple[float, list[str]]:
    reasons: list[str] = []
    if not intent_tokens:
        return 0.0, reasons
    combined_tokens = set(_tokenize(when or "")) | set(_tokenize(description or ""))
    if not combined_tokens:
        return 0.0, reasons
    shared = intent_tokens & combined_tokens
    if not shared:
        return 0.0, reasons
    # Normalize by intent side — of the user's tokens, how many are covered?
    ratio = len(shared) / len(intent_tokens)
    reasons.append(f"when/desc tokens matched: {sorted(shared)}")
    return min(ratio, 1.0), reasons


def _sections_score(
    intent_tokens: set[str], sections_shape: list[str]
) -> tuple[float, list[str]]:
    """Bonus when user intent hints at a component type in the recipe."""
    reasons: list[str] = []
    if not intent_tokens or not sections_shape:
        return 0.0, reasons
    # Build token set from section component names (split kebab)
    section_tokens: set[str] = set()
    for s in sections_shape:
        section_tokens.update(_tokenize(s))
    shared = intent_tokens & section_tokens
    if not shared:
        return 0.0, reasons
    reasons.append(f"section-shape hint: {sorted(shared)}")
    # Cap the contribution — sections are a weak signal
    return min(len(shared) / 3.0, 1.0), reasons


def rank_recipes(
    intent: str, caps: dict, top_k: int = 3
) -> list[RecipeMatch]:
    recipes = caps.get("recipes", {}) or {}
    if not recipes:
        return []
    intent_tokens = set(_tokenize(intent))
    matches: list[RecipeMatch] = []
    for name, block in recipes.items():
        n_score, n_reasons = _name_score(intent_tokens, name)
        k_score, k_reasons = _keyword_score(intent_tokens, block.get("keywords") or [])
        w_score, w_reasons = _when_desc_score(
            intent_tokens, block.get("when") or "", block.get("description") or ""
        )
        s_score, s_reasons = _sections_score(
            intent_tokens, block.get("sections_shape") or []
        )
        total = (
            _W_NAME * n_score
            + _W_KEYWORDS * k_score
            + _W_WHEN_DESC * w_score
            + _W_SECTIONS * s_score
        )
        if total <= 0.0:
            continue
        matches.append(
            RecipeMatch(
                name=name,
                score=round(total, 4),
                reasons=n_reasons + k_reasons + w_reasons + s_reasons,
                data=dict(block),
            )
        )
    matches.sort(key=lambda m: m.score, reverse=True)
    return matches[:top_k]


def find_closest_recipe(intent: str, caps: dict) -> RecipeMatch | None:
    ranked = rank_recipes(intent, caps, top_k=1)
    return ranked[0] if ranked else None
