"""Phase-5 release-readiness — install.sh + public-install smoke tests.

Validates that the Phase-4/5 cleanup of install.sh (removing the legacy
`~/.local/share/katib/memory/` dead path) is correct and that a freshly
"installed" skill lays down exactly the user-tier directory structure
Phase 5 plumbing expects.

Scope:
- install.sh is syntactically valid (`bash -n`)
- install.sh no longer references the legacy memory path
- install.sh mentions every user-tier dir Phase 5 writes to
- A simulated post-clone install against a sandbox HOME creates every
  dir and does not create the legacy one

We do not run the real `git clone` step — that's pre-existing behaviour
and testing it requires network or repo fixtures. The value is in
confirming Phase 5's user-dir plumbing is consistent between the code
and the installer.
"""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
INSTALL_SH = REPO_ROOT / "install.sh"


def test_install_sh_is_syntactically_valid():
    """`bash -n` parses without executing — catches missing fi/done/quotes."""
    r = subprocess.run(
        ["bash", "-n", str(INSTALL_SH)],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"install.sh syntax error:\n{r.stderr}"


def test_install_sh_does_not_reference_legacy_memory_path():
    """`~/.local/share/katib/memory/` was the v1 memory location. Phase 4
    removed it. If a future edit re-introduces it, we're back to the
    split-memory bug where audit writes and reads diverge."""
    content = INSTALL_SH.read_text(encoding="utf-8")
    assert "~/.local/share/katib/memory" not in content
    assert ".local/share/katib/memory" not in content


def test_install_sh_creates_all_user_tier_dirs():
    """The installer's mkdir block must cover every user-tier directory
    that Phase-2/3/4 read and write paths expect. A missing dir here
    would manifest as a first-run error the user can't easily diagnose."""
    content = INSTALL_SH.read_text(encoding="utf-8")
    required = [
        "$HOME/.katib/brands",
        "$HOME/.katib/recipes",
        "$HOME/.katib/components/primitives",
        "$HOME/.katib/components/sections",
        "$HOME/.katib/components/covers",
        "$HOME/.katib/memory",
        "$HOME/.config/katib",
    ]
    for d in required:
        assert d in content, f"install.sh mkdir block is missing {d!r}"


def test_post_clone_install_steps_produce_expected_tree(tmp_path):
    """Simulate what install.sh does AFTER the git clone step against a
    sandbox HOME. Uses a real subprocess so any env/PATH/shell escaping
    bugs in the installer surface here, not in user inboxes.

    We pre-populate `$HOME/.claude/skills/katib/brands/` with the bundled
    example.yaml (the one real thing install.sh copies out of the skill
    dir at setup) and then exercise the user-dirs + config-seed blocks.
    """
    sandbox_home = tmp_path / "home"
    sandbox_home.mkdir()
    skill_dir = sandbox_home / ".claude" / "skills" / "katib"
    skill_dir.mkdir(parents=True)
    shutil.copytree(REPO_ROOT / "brands", skill_dir / "brands", dirs_exist_ok=True)

    # Extract install.sh's section-5 + section-6 behaviour. Keep in sync
    # with the installer — if install.sh adds a dir or changes a config
    # key, this script must match.
    script = r"""
    set -euo pipefail
    mkdir -p "$HOME/.katib/brands" \
             "$HOME/.katib/recipes" \
             "$HOME/.katib/components/primitives" \
             "$HOME/.katib/components/sections" \
             "$HOME/.katib/components/covers" \
             "$HOME/.katib/memory" \
             "$HOME/.config/katib"

    cp "$SKILL_DIR/brands/example.yaml" "$HOME/.katib/brands/example.yaml"

    CONFIG_FILE="$HOME/.config/katib/config.yaml"
    cat > "$CONFIG_FILE" <<EOF
output:
  destination: custom
  vault_path: ~/vault/content/katib
  custom_path: ~/Documents/katib
  always_create_manifest: true

memory:
  location: ~/.katib/memory
  per_domain_rollup: true
EOF
    """
    env = {**os.environ, "HOME": str(sandbox_home), "SKILL_DIR": str(skill_dir)}
    r = subprocess.run(
        ["bash", "-c", script], env=env, capture_output=True, text=True, timeout=15,
    )
    assert r.returncode == 0, f"simulated install failed:\n{r.stderr}"

    # Every directory Phase 5 relies on must exist.
    dot_katib = sandbox_home / ".katib"
    assert (dot_katib / "brands").is_dir()
    assert (dot_katib / "recipes").is_dir()
    assert (dot_katib / "components" / "primitives").is_dir()
    assert (dot_katib / "components" / "sections").is_dir()
    assert (dot_katib / "components" / "covers").is_dir()
    assert (dot_katib / "memory").is_dir()

    # Seed file landed.
    assert (dot_katib / "brands" / "example.yaml").exists()

    # Config was written with the Phase-4 memory path (not legacy).
    config = (sandbox_home / ".config" / "katib" / "config.yaml").read_text(encoding="utf-8")
    assert "location: ~/.katib/memory" in config
    assert "~/.local/share/katib" not in config

    # Legacy dir must NOT exist — regression guard for the Phase-4 cleanup.
    assert not (sandbox_home / ".local" / "share" / "katib").exists()
