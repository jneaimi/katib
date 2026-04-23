"""Output resolver — env override, OS-standard fallback, folder creation."""
from __future__ import annotations

from pathlib import Path

from core.output import (
    APP_NAME,
    OUTPUT_ROOT_ENV,
    resolve_cache_dir,
    resolve_document_folder,
    resolve_output_root,
    resolve_user_components_dir,
    resolve_user_config_dir,
)


def test_env_override_beats_default(tmp_path, monkeypatch):
    monkeypatch.setenv(OUTPUT_ROOT_ENV, str(tmp_path))
    root = resolve_output_root()
    assert root == tmp_path.resolve()
    assert root.exists()


def test_default_falls_through_to_documents(monkeypatch):
    monkeypatch.delenv(OUTPUT_ROOT_ENV, raising=False)
    root = resolve_output_root()
    assert root.name == "katib"
    assert root.exists()


def test_document_folder_creates_nested_dirs(tmp_path, monkeypatch):
    monkeypatch.setenv(OUTPUT_ROOT_ENV, str(tmp_path))
    folder = resolve_document_folder("my-recipe", "2026-04-23-test")
    assert folder == (tmp_path / "my-recipe" / "2026-04-23-test").resolve()
    assert folder.exists()
    assert folder.parent.name == "my-recipe"


def test_empty_env_var_falls_through(monkeypatch):
    monkeypatch.setenv(OUTPUT_ROOT_ENV, "   ")
    root = resolve_output_root()
    assert root.name == "katib"
    assert str(root).endswith(f"/{APP_NAME}")


def test_cache_dir_exists(monkeypatch):
    monkeypatch.delenv(OUTPUT_ROOT_ENV, raising=False)
    cache = resolve_cache_dir("images")
    assert cache.exists()
    assert cache.name == "images"


def test_user_config_dirs_exist():
    cfg = resolve_user_config_dir()
    comp = resolve_user_components_dir()
    assert cfg.exists()
    assert comp.exists()
    assert comp.parent == cfg
