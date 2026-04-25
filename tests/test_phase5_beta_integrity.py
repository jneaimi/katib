"""Phase-5 beta integrity — `1.0.0-beta.1` release engineering doesn't rot.

Phase 5a (beta release) added doc surfaces that reference concrete
things in the codebase: CLI commands in MIGRATING.md, status banner
in PACK-FORMAT.md, version coherence between README and package.json.
These tests catch silent rot: if PACK-FORMAT loses its frozen banner
or MIGRATING.md cites a removed CLI subcommand, CI fails fast.

Narrow scope. Heavy docs work doesn't justify heavy doc tests — just
enough to keep the load-bearing claims in sync with the codebase.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
README = REPO_ROOT / "README.md"
MIGRATING = REPO_ROOT / "MIGRATING.md"
PACK_FORMAT = REPO_ROOT / "PACK-FORMAT.md"
CHANGELOG = REPO_ROOT / "CHANGELOG.md"


# ---------------------------------------------------------------------------
# MIGRATING.md exists and links real things
# ---------------------------------------------------------------------------


def test_migrating_md_exists():
    assert MIGRATING.exists(), (
        "MIGRATING.md missing — Phase 5 beta requires a v0→v1 migration guide"
    )


def test_migrating_references_real_pack_cli_subcommands():
    """The migration guide cites `scripts/pack.py <sub>` commands;
    every cited subcommand must actually exist."""
    content = MIGRATING.read_text(encoding="utf-8")
    cited = set(re.findall(r"scripts/pack\.py\s+([a-z][a-z-]*)", content))

    r = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "pack.py"), "--help"],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"pack.py --help failed: {r.stderr}"
    m = re.search(r"\{([a-z,]+)\}", r.stdout)
    real = set(m.group(1).split(","))

    missing = cited - real
    assert not missing, (
        f"MIGRATING.md cites pack.py subcommands that don't exist: {sorted(missing)}"
    )


def test_migrating_references_pack_format_md():
    """The migration guide must link to the pack-format spec."""
    content = MIGRATING.read_text(encoding="utf-8")
    assert "PACK-FORMAT.md" in content, (
        "MIGRATING.md doesn't link to PACK-FORMAT.md — readers can't find the spec"
    )


# ---------------------------------------------------------------------------
# README beta posture
# ---------------------------------------------------------------------------


def test_readme_links_to_migrating():
    content = README.read_text(encoding="utf-8")
    assert "MIGRATING.md" in content, (
        "README must link to MIGRATING.md so v0.x users find the upgrade path"
    )


def test_readme_no_longer_says_alpha_only():
    """The README's status copy must reflect beta — explicit text
    that v2 is in alpha is stale once we're in beta."""
    content = README.read_text(encoding="utf-8")
    # The phrase "v2 is in alpha" was the alpha-era warning we should be past
    assert "v2 is in alpha" not in content, (
        "README still has the alpha-era warning; should reference beta status now"
    )


def test_readme_status_badge_is_beta():
    """The status badge in the header must say beta, not alpha."""
    content = README.read_text(encoding="utf-8")
    # Crude but effective check on the status badge
    badge_lines = [l for l in content.splitlines() if "shields.io" in l and "status" in l.lower()]
    assert badge_lines, "no status badge found in README header"
    assert any("beta" in l.lower() for l in badge_lines), (
        f"status badge doesn't reflect beta: {badge_lines}"
    )


# ---------------------------------------------------------------------------
# PACK-FORMAT.md frozen declaration
# ---------------------------------------------------------------------------


def test_pack_format_declares_frozen():
    """PACK-FORMAT.md must explicitly declare the format frozen for v1.0.0."""
    content = PACK_FORMAT.read_text(encoding="utf-8")
    assert "pack_format: 1" in content
    assert "frozen" in content.lower() or "Frozen" in content, (
        "PACK-FORMAT.md must explicitly call the format 'frozen' for v1.0.0"
    )


# ---------------------------------------------------------------------------
# Version coherence
# ---------------------------------------------------------------------------


def test_package_json_at_beta_1():
    pkg = json.loads((REPO_ROOT / "package.json").read_text(encoding="utf-8"))
    assert pkg["version"] == "1.0.0-beta.1", (
        f"package.json version should be '1.0.0-beta.1' for Phase-5 beta, "
        f"got {pkg['version']!r}"
    )


def test_changelog_has_beta_1_entry():
    content = CHANGELOG.read_text(encoding="utf-8")
    assert "[1.0.0-beta.1]" in content, "CHANGELOG missing [1.0.0-beta.1] entry"
    # Must mention what beta means: format frozen + migration guide
    beta_section = content.split("[1.0.0-beta.1]")[1].split("[1.0.0-alpha.3]")[0]
    assert "frozen" in beta_section.lower(), (
        "beta entry must declare the format frozen"
    )
    assert "MIGRATING" in beta_section or "migration" in beta_section.lower(), (
        "beta entry must reference the migration guide"
    )
