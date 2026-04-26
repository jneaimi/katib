"""Per-project Katib defaults via `.katib.yaml`.

A `.katib.yaml` file in any ancestor directory of the cwd supplies fallback
values for `brand` and `lang` when neither an explicit CLI flag nor the
context sensor produced a value. Precedence:

    explicit --flag  >  sensor inference  >  .katib.yaml default

The file is discovered by walking up from `start_dir` until either a file
is found or the filesystem root is reached. A discovered file outside the
user's home tree is honored — there is no scope check beyond walk-up.

Schema (v1):

    version: 1
    defaults:
      brand: <brand name>     # optional
      lang: en | ar           # optional

Unknown keys are ignored (forward compatibility). Malformed YAML or an
unsupported `version` raises `ProjectConfigError` so the caller can decide
whether to surface it as a routing error or swallow it.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


CONFIG_FILENAME = ".katib.yaml"
SUPPORTED_VERSIONS = {1}


class ProjectConfigError(ValueError):
    """Raised when a .katib.yaml is found but cannot be parsed or honored."""


@dataclass
class ProjectConfig:
    path: Path
    default_brand: str | None = None
    default_lang: str | None = None

    @property
    def is_empty(self) -> bool:
        return self.default_brand is None and self.default_lang is None


def find_config_file(start_dir: Path | str) -> Path | None:
    """Walk upward from start_dir looking for .katib.yaml. Return path or None."""
    current = Path(start_dir).resolve()
    for candidate_dir in [current, *current.parents]:
        candidate = candidate_dir / CONFIG_FILENAME
        if candidate.is_file():
            return candidate
    return None


def load_project_config(start_dir: Path | str) -> ProjectConfig | None:
    """Return the discovered ProjectConfig or None if no .katib.yaml exists."""
    path = find_config_file(start_dir)
    if path is None:
        return None
    return _parse_config_file(path)


def _parse_config_file(path: Path) -> ProjectConfig:
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ProjectConfigError(f"{path}: invalid YAML — {exc}") from exc

    if raw is None:
        return ProjectConfig(path=path)

    if not isinstance(raw, dict):
        raise ProjectConfigError(f"{path}: top-level must be a mapping")

    version = raw.get("version", 1)
    if version not in SUPPORTED_VERSIONS:
        raise ProjectConfigError(
            f"{path}: unsupported version {version!r}; expected one of {sorted(SUPPORTED_VERSIONS)}"
        )

    defaults = raw.get("defaults") or {}
    if not isinstance(defaults, dict):
        raise ProjectConfigError(f"{path}: 'defaults' must be a mapping")

    brand = defaults.get("brand")
    if brand is not None and not isinstance(brand, str):
        raise ProjectConfigError(f"{path}: defaults.brand must be a string")

    lang = defaults.get("lang")
    if lang is not None:
        if not isinstance(lang, str) or lang not in {"en", "ar"}:
            raise ProjectConfigError(
                f"{path}: defaults.lang must be 'en' or 'ar' (got {lang!r})"
            )

    return ProjectConfig(path=path, default_brand=brand, default_lang=lang)
