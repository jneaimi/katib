"""Tests for core/project_config.py — .katib.yaml discovery + parsing."""
from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from core.project_config import (
    CONFIG_FILENAME,
    ProjectConfigError,
    find_config_file,
    load_project_config,
)


# ================================================================ find_config_file


def test_find_config_in_start_dir(tmp_path):
    cfg = tmp_path / CONFIG_FILENAME
    cfg.write_text("version: 1\ndefaults:\n  brand: jasem\n")
    assert find_config_file(tmp_path) == cfg


def test_find_config_walks_up_to_ancestor(tmp_path):
    cfg = tmp_path / CONFIG_FILENAME
    cfg.write_text("version: 1\n")
    nested = tmp_path / "a" / "b" / "c"
    nested.mkdir(parents=True)
    assert find_config_file(nested) == cfg


def test_find_config_returns_none_when_absent(tmp_path):
    nested = tmp_path / "deep" / "tree"
    nested.mkdir(parents=True)
    assert find_config_file(nested) is None


def test_find_config_picks_nearest_when_multiple_exist(tmp_path):
    outer = tmp_path / CONFIG_FILENAME
    outer.write_text("version: 1\n")
    inner_dir = tmp_path / "sub"
    inner_dir.mkdir()
    inner = inner_dir / CONFIG_FILENAME
    inner.write_text("version: 1\n")
    assert find_config_file(inner_dir) == inner


# ================================================================ load_project_config


def test_load_returns_none_when_missing(tmp_path):
    assert load_project_config(tmp_path) is None


def test_load_full_config(tmp_path):
    (tmp_path / CONFIG_FILENAME).write_text(
        textwrap.dedent("""
            version: 1
            defaults:
              brand: jasem
              lang: ar
        """).strip()
    )
    cfg = load_project_config(tmp_path)
    assert cfg is not None
    assert cfg.default_brand == "jasem"
    assert cfg.default_lang == "ar"
    assert not cfg.is_empty


def test_load_partial_config_brand_only(tmp_path):
    (tmp_path / CONFIG_FILENAME).write_text("version: 1\ndefaults:\n  brand: acme\n")
    cfg = load_project_config(tmp_path)
    assert cfg.default_brand == "acme"
    assert cfg.default_lang is None


def test_load_empty_file_yields_empty_config(tmp_path):
    (tmp_path / CONFIG_FILENAME).write_text("")
    cfg = load_project_config(tmp_path)
    assert cfg is not None
    assert cfg.is_empty


def test_load_malformed_yaml_raises(tmp_path):
    (tmp_path / CONFIG_FILENAME).write_text("defaults: {brand: [unterminated")
    with pytest.raises(ProjectConfigError, match="invalid YAML"):
        load_project_config(tmp_path)


def test_load_non_mapping_top_level_raises(tmp_path):
    (tmp_path / CONFIG_FILENAME).write_text("- just\n- a\n- list\n")
    with pytest.raises(ProjectConfigError, match="top-level must be a mapping"):
        load_project_config(tmp_path)


def test_load_unsupported_version_raises(tmp_path):
    (tmp_path / CONFIG_FILENAME).write_text("version: 99\n")
    with pytest.raises(ProjectConfigError, match="unsupported version"):
        load_project_config(tmp_path)


def test_load_invalid_lang_raises(tmp_path):
    (tmp_path / CONFIG_FILENAME).write_text(
        "version: 1\ndefaults:\n  lang: fr\n"
    )
    with pytest.raises(ProjectConfigError, match="defaults.lang"):
        load_project_config(tmp_path)


def test_load_invalid_brand_type_raises(tmp_path):
    (tmp_path / CONFIG_FILENAME).write_text(
        "version: 1\ndefaults:\n  brand: 42\n"
    )
    with pytest.raises(ProjectConfigError, match="defaults.brand"):
        load_project_config(tmp_path)


def test_load_unknown_keys_ignored(tmp_path):
    """Forward compatibility — extra keys must not cause an error."""
    (tmp_path / CONFIG_FILENAME).write_text(
        textwrap.dedent("""
            version: 1
            defaults:
              brand: jasem
              future_field: whatever
            other_section:
              also_ignored: true
        """).strip()
    )
    cfg = load_project_config(tmp_path)
    assert cfg.default_brand == "jasem"
