"""Phase-3b component-builder guide — integrity tests.

The AI-assisted component builder is a playbook Claude follows when the
user asks to build a new component. The playbook lives in
`COMPONENT-BUILDER.md` and is referenced from `SKILL.md`. There's no
runtime Python for the guide itself — it orchestrates existing CLI tools
(`scripts/component.py`). But the guide becomes misleading if:

- It references CLI subcommands that no longer exist
- It names exemplar components that were deleted or renamed
- Its "common pitfalls" cheat sheet drifts out of sync with reality
- The SKILL.md → COMPONENT-BUILDER.md cross-reference breaks

These tests are the guard. They're intentionally narrow — they only
check the claims that could silently rot, not the literary quality.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BUILDER_GUIDE = REPO_ROOT / "COMPONENT-BUILDER.md"
SKILL_MD = REPO_ROOT / "SKILL.md"
COMPONENT_CLI = REPO_ROOT / "scripts" / "component.py"


def test_builder_guide_file_exists():
    assert BUILDER_GUIDE.exists(), \
        "COMPONENT-BUILDER.md is missing — the AI-assisted builder flow has no playbook."


def test_skill_md_references_builder_guide():
    """SKILL.md must point Claude at the builder guide when user invokes
    `/katib component new` — otherwise the builder is orphaned."""
    content = SKILL_MD.read_text(encoding="utf-8")
    assert "COMPONENT-BUILDER.md" in content, \
        "SKILL.md doesn't reference COMPONENT-BUILDER.md — users invoking `/katib component new` will get no guidance."
    assert "component new" in content, \
        "SKILL.md invocation table doesn't list `component new` — discoverability broken."


def test_builder_guide_cli_commands_still_work():
    """Every `scripts/component.py <subcommand>` mentioned in the guide
    must be a real subcommand. Renaming a subcommand without updating
    the guide would silently lead Claude to wrong tooling."""
    content = BUILDER_GUIDE.read_text(encoding="utf-8")

    # Extract every `scripts/component.py X` subcommand reference.
    cited_subs = set(re.findall(r"scripts/component\.py\s+([a-z][a-z-]*)", content))
    # Filter out obvious name-of-component placeholders — we want commands only.
    cited_subs -= {"<name>"}

    # Get the real subcommand list from the CLI help.
    r = subprocess.run(
        [sys.executable, str(COMPONENT_CLI), "--help"],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"component.py --help failed: {r.stderr}"
    # argparse prints subcommands under a {a,b,c} group. Parse that.
    m = re.search(r"\{([a-z,-]+)\}", r.stdout)
    assert m, f"couldn't parse subcommand list from help:\n{r.stdout}"
    real_subs = set(m.group(1).split(","))

    missing = cited_subs - real_subs
    assert not missing, \
        f"COMPONENT-BUILDER.md cites subcommands that don't exist: {sorted(missing)}. " \
        f"Real subcommands: {sorted(real_subs)}"


def test_builder_guide_exemplars_exist_on_disk():
    """Every exemplar component named in the guide must exist. A renamed
    or deleted exemplar would lead Claude to read files that aren't there."""
    content = BUILDER_GUIDE.read_text(encoding="utf-8")

    # Extract every backticked component name from the exemplar section.
    # The "Picking exemplar candidates" block is the authoritative list;
    # extract inline-code mentions there.
    ex_section_match = re.search(
        r"### Picking exemplar candidates\n(.+?)(?=\n###|\n---)",
        content, re.DOTALL,
    )
    assert ex_section_match, "exemplar section structure changed — update this test"
    ex_block = ex_section_match.group(1)

    cited = set(re.findall(r"`([a-z][a-z0-9-]*)`", ex_block))

    # Collect real components on disk.
    real = set()
    components_dir = REPO_ROOT / "components"
    for tier in ("primitives", "sections", "covers"):
        tier_dir = components_dir / tier
        if not tier_dir.exists():
            continue
        for item in tier_dir.iterdir():
            if (item / "component.yaml").exists():
                real.add(item.name)

    missing = cited - real
    assert not missing, \
        f"COMPONENT-BUILDER.md names exemplar components that don't exist on disk: {sorted(missing)}. " \
        f"Real components: {sorted(real)}"


def test_builder_guide_lists_known_pitfalls():
    """The 'Common pitfalls' cheat sheet must include the bugs I hit
    while building the Phase-3a layout primitives. If a future editor
    deletes these, we lose the practical value of the guide."""
    content = BUILDER_GUIDE.read_text(encoding="utf-8")

    required_pitfalls = [
        # Keyword the description MUST contain.
        ("inset", "the WeasyPrint inset: 0 bug"),
        ("description", "the input-name-can't-be-description clash"),
        ("var(--accent)", "the hardcoded-colors anti-pattern"),
    ]
    for needle, why in required_pitfalls:
        assert needle in content, \
            f"COMPONENT-BUILDER.md pitfalls section doesn't mention {needle!r} ({why})"


def test_builder_guide_has_required_sections():
    """Structural invariants — Claude needs specific signposted sections."""
    content = BUILDER_GUIDE.read_text(encoding="utf-8")
    required_headings = [
        "## When to enter this mode",
        "## The flow",
        "## Step 1 — Interview",
        "## Step 2 — Scaffold",
        "## Step 3 — Generate",
        "## Step 4 — Validate",
        "## Step 5 — Preview",
        "## Step 6 — Iterate",
        "## Step 7 — Register",
        "## Common pitfalls",
    ]
    for heading in required_headings:
        assert heading in content, \
            f"COMPONENT-BUILDER.md missing required section: {heading!r}"
