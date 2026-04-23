"""Shared pytest fixtures."""
from __future__ import annotations

import os
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture
def clean_env(monkeypatch):
    for var in ("KATIB_OUTPUT_ROOT", "KATIB_BRANDS_DIR", "GEMINI_API_KEY"):
        monkeypatch.delenv(var, raising=False)
    return monkeypatch
