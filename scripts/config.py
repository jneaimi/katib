#!/usr/bin/env python3
"""Katib config loader.

Resolves configuration from (in precedence order):
  1. CLI flags passed as dict
  2. <project-root>/.katib/config.yaml (if CWD is inside a project with one)
  3. ~/.config/katib/config.yaml (user global)
  4. Skill default (config.example.yaml adjacent to this script)

Usage:
    from config import load_config
    cfg = load_config(cli_overrides={"output.destination": "custom", ...})
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print("✗ missing dep: pip install pyyaml --break-system-packages", file=sys.stderr)
    sys.exit(1)

SKILL_ROOT = Path(__file__).resolve().parent.parent
USER_CONFIG = Path.home() / ".config" / "katib" / "config.yaml"
EXAMPLE_CONFIG = SKILL_ROOT / "config.example.yaml"


def _deep_merge(base: dict, override: dict) -> dict:
    """Recursively merge override into base. Override wins on conflict."""
    result = dict(base)
    for key, val in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(val, dict):
            result[key] = _deep_merge(result[key], val)
        else:
            result[key] = val
    return result


def _expand_paths(cfg: dict) -> dict:
    """Expand ~ and env vars in known path-typed keys."""
    path_keys = {
        ("output", "vault_path"),
        ("output", "custom_path"),
        ("memory", "location"),
        ("identity", "signature_path"),
        ("fonts", "core_path"),
        ("fonts", "optional_install_path"),
    }
    for section, key in path_keys:
        if section in cfg and key in cfg[section]:
            val = cfg[section][key]
            if isinstance(val, str) and val not in ("builtin", "null", None):
                cfg[section][key] = str(Path(os.path.expandvars(val)).expanduser())
    return cfg


def _find_project_config(cwd: Path) -> Path | None:
    """Walk up from CWD looking for .katib/config.yaml or pyproject.toml with [tool.katib]."""
    for parent in [cwd, *cwd.parents]:
        candidate = parent / ".katib" / "config.yaml"
        if candidate.exists():
            return candidate
        # Stop at home or filesystem root
        if parent == Path.home() or parent == parent.parent:
            break
    return None


def _apply_cli_overrides(cfg: dict, overrides: dict[str, Any]) -> dict:
    """Apply dotted-key CLI overrides, e.g. {'output.destination': 'custom'}."""
    for dotted_key, val in overrides.items():
        parts = dotted_key.split(".")
        target = cfg
        for part in parts[:-1]:
            target = target.setdefault(part, {})
        target[parts[-1]] = val
    return cfg


def load_config(cli_overrides: dict[str, Any] | None = None, cwd: Path | None = None) -> dict:
    """Load Katib config with full precedence resolution.

    Returns the merged config dict, with paths expanded and validated.
    """
    cwd = cwd or Path.cwd()
    cli_overrides = cli_overrides or {}

    # Tier 4: skill default
    if not EXAMPLE_CONFIG.exists():
        raise FileNotFoundError(f"Skill default config missing: {EXAMPLE_CONFIG}")
    with EXAMPLE_CONFIG.open() as f:
        cfg = yaml.safe_load(f) or {}

    # Tier 3: user global
    if USER_CONFIG.exists():
        with USER_CONFIG.open() as f:
            user_cfg = yaml.safe_load(f) or {}
        cfg = _deep_merge(cfg, user_cfg)

    # Tier 2: project-local
    project_cfg_path = _find_project_config(cwd)
    if project_cfg_path:
        with project_cfg_path.open() as f:
            project_cfg = yaml.safe_load(f) or {}
        cfg = _deep_merge(cfg, project_cfg)

    # Tier 1: CLI overrides
    cfg = _apply_cli_overrides(cfg, cli_overrides)

    cfg = _expand_paths(cfg)
    _validate(cfg)
    return cfg


def _validate(cfg: dict) -> None:
    """Basic validation — raises ValueError on malformed config."""
    dest = cfg.get("output", {}).get("destination")
    if dest not in ("vault", "custom"):
        raise ValueError(f"output.destination must be 'vault' or 'custom', got: {dest!r}")

    if dest == "custom" and not cfg.get("output", {}).get("custom_path"):
        raise ValueError("output.destination=custom requires output.custom_path to be set")

    mem_loc = cfg.get("memory", {}).get("location")
    if not mem_loc:
        raise ValueError("memory.location must be set")


def resolve_output_root(cfg: dict) -> Path:
    """Return the absolute output root for generated folders."""
    if cfg["output"]["destination"] == "vault":
        return Path(cfg["output"]["vault_path"]).expanduser()
    return Path(cfg["output"]["custom_path"]).expanduser()


def slug_folder(cfg: dict, domain: str, date_str: str, slug: str) -> Path:
    """Return the absolute folder path for a new generation."""
    root = resolve_output_root(cfg)
    return root / domain / f"{date_str}-{slug}"


if __name__ == "__main__":
    # Smoke test
    cfg = load_config()
    print(yaml.safe_dump(cfg, sort_keys=False, indent=2))
    print(f"\nOutput root: {resolve_output_root(cfg)}")
