"""Output routing for Katib v2.

Resolves where rendered documents are written.

Resolution order:
    1. KATIB_OUTPUT_ROOT env var  -> explicit override (tests, CI, custom workflows)
    2. platformdirs.user_documents_path() / "katib"  -> OS-standard fallback

Same two-level resolver on every install. No external-store code path, no
install-time prompt, no conditional integration. v2 deliberately ends at
the filesystem — file navigation belongs at a different layer.
"""
from __future__ import annotations

import os
from pathlib import Path

from platformdirs import user_cache_path, user_config_path, user_documents_path

OUTPUT_ROOT_ENV = "KATIB_OUTPUT_ROOT"
SUBDIR = "katib"
APP_NAME = "katib"


def resolve_output_root() -> Path:
    env = os.environ.get(OUTPUT_ROOT_ENV, "").strip()
    if env:
        root = Path(env).expanduser().resolve()
    else:
        root = user_documents_path() / SUBDIR
    root.mkdir(parents=True, exist_ok=True)
    return root


def resolve_document_folder(recipe_name: str, slug: str) -> Path:
    folder = resolve_output_root() / recipe_name / slug
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def resolve_cache_dir(subdir: str = "images") -> Path:
    cache = user_cache_path(APP_NAME) / subdir
    cache.mkdir(parents=True, exist_ok=True)
    return cache


def resolve_user_config_dir() -> Path:
    cfg = user_config_path(APP_NAME)
    cfg.mkdir(parents=True, exist_ok=True)
    return cfg


def resolve_user_components_dir() -> Path:
    comp = resolve_user_config_dir() / "components"
    comp.mkdir(parents=True, exist_ok=True)
    return comp
