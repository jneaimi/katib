"""Phase-3e docs integrity — TUTORIAL.md, README, CHANGELOG don't rot.

Phase 3e added prose documentation that references concrete things in
the codebase — component names, CLI subcommands, file paths. These
tests guard against the docs drifting out of sync with the code.

Narrow scope: we check load-bearing claims (commands that must resolve,
components that must exist), not literary quality. A docs-heavy phase
shouldn't need heavy docs-maintenance tests; just enough to catch
silent rot.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
TUTORIAL = REPO_ROOT / "TUTORIAL.md"
README = REPO_ROOT / "README.md"
CHANGELOG = REPO_ROOT / "CHANGELOG.md"
MANIFEST = REPO_ROOT / "seed-manifest.yaml"


def test_tutorial_md_exists():
    assert TUTORIAL.exists(), \
        "TUTORIAL.md missing — README links to it from the 'Starter recipes' section"


def test_tutorial_references_real_cli_commands():
    """Every `scripts/component.py <sub>` cited in the tutorial must be
    a real subcommand. A renamed command without a doc update leads
    users to broken prompts."""
    content = TUTORIAL.read_text(encoding="utf-8")
    cited = set(re.findall(r"scripts/component\.py\s+([a-z][a-z-]*)", content))
    cited -= {"<name>"}

    r = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "component.py"), "--help"],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"component.py --help failed: {r.stderr}"
    m = re.search(r"\{([a-z,-]+)\}", r.stdout)
    real = set(m.group(1).split(","))

    missing = cited - real
    assert not missing, \
        f"TUTORIAL.md cites subcommands that don't exist: {sorted(missing)}"


def test_tutorial_exemplar_reference_exists():
    """The tutorial tells users to model 'testimonial' on the
    'pull-quote' exemplar. If pull-quote gets renamed or removed, the
    tutorial breaks silently."""
    content = TUTORIAL.read_text(encoding="utf-8")
    assert "pull-quote" in content, \
        "TUTORIAL.md no longer references pull-quote as the exemplar"
    assert (REPO_ROOT / "components" / "primitives" / "pull-quote" / "component.yaml").exists(), \
        "pull-quote exemplar cited by TUTORIAL.md doesn't exist on disk"


def test_readme_lists_accurate_starter_count():
    """The README mentions 'X starter recipes' — must match the
    manifest. Adding a starter without updating the README breaks
    the signal to fresh-install users."""
    content = README.read_text(encoding="utf-8")
    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    expected_count = len(manifest["recipes"])
    # README should mention the count literally somewhere.
    assert f"{expected_count} starter" in content, \
        f"README doesn't mention the current starter count ({expected_count}) — " \
        f"update the 'Fresh install' bullet and the library table"


def test_readme_component_count_matches_disk():
    """README claims '28 components'. Verify against what's actually
    on disk — primitives + sections + covers."""
    content = README.read_text(encoding="utf-8")
    # Pull the stated count out of "28 components" pattern.
    m = re.search(r"(\d+)\s+components\s*·", content)
    assert m, "README missing expected '<N> components · ...' line"
    claimed = int(m.group(1))

    # Count what's actually on disk.
    components_dir = REPO_ROOT / "components"
    real = sum(
        1 for tier in ("primitives", "sections", "covers")
        for item in (components_dir / tier).iterdir()
        if (item / "component.yaml").exists()
    )
    assert claimed == real, \
        f"README says {claimed} components; disk has {real}. Update the badge/table."


def test_readme_links_to_builder_and_tutorial():
    """The README must link to COMPONENT-BUILDER.md and TUTORIAL.md
    so users discover the AI-assisted flow."""
    content = README.read_text(encoding="utf-8")
    assert "COMPONENT-BUILDER.md" in content, \
        "README doesn't link to COMPONENT-BUILDER.md — builder is orphaned from the entry page"
    assert "TUTORIAL.md" in content, \
        "README doesn't link to TUTORIAL.md — tutorial is orphaned from the entry page"


def test_package_json_version_matches_readme():
    """If package.json says 1.0.0-alpha.2, README must mention it.
    Drift between the two misleads npm users about what they just
    installed."""
    import json
    pkg = json.loads((REPO_ROOT / "package.json").read_text(encoding="utf-8"))
    version = pkg["version"]
    content = README.read_text(encoding="utf-8")
    assert version in content, \
        f"README doesn't mention package.json version {version!r} — update the 'Where things stand' table"


def test_changelog_mentions_phase_3_completion():
    """CHANGELOG must have an entry for Phase 3 so the release history
    documents the largest v2-alpha jump."""
    content = CHANGELOG.read_text(encoding="utf-8")
    assert "Phase 3" in content, "CHANGELOG missing Phase-3 entry"
    assert "1.0.0-alpha.2" in content, \
        "CHANGELOG doesn't cite the 1.0.0-alpha.2 release tag"
