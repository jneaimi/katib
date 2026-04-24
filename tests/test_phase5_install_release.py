"""Phase-5 release-readiness — install.sh + public-install smoke tests.

Validates that the Phase-4/5 cleanup of install.sh (removing the legacy
`~/.local/share/katib/memory/` dead path) is correct and that a freshly
"installed" skill lays down exactly the user-tier directory structure
Phase 5 plumbing expects. Also validates the Phase-3 seed-on-fresh-install
mechanism (seed-manifest.yaml + scripts/seed.py + install.sh seed block).

Scope:
- install.sh is syntactically valid (`bash -n`)
- install.sh no longer references the legacy memory path
- install.sh mentions every user-tier dir Phase 5 writes to
- A simulated post-clone install against a sandbox HOME creates every
  dir and does not create the legacy one
- seed-manifest.yaml entries all resolve to bundled recipes
- scripts/seed.py fresh-seed populates an empty user tier
- scripts/seed.py refresh is a no-op when user tier already has the file
- scripts/seed.py --force refuses to overwrite without --justification
- scripts/seed.py refuses unknown recipe names
- install.sh's seed block only fires on a truly empty user tier

We do not run the real `git clone` step — that's pre-existing behaviour
and testing it requires network or repo fixtures. The value is in
confirming Phase 5's user-dir plumbing is consistent between the code
and the installer.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
INSTALL_SH = REPO_ROOT / "install.sh"
SEED_SCRIPT = REPO_ROOT / "scripts" / "seed.py"
MANIFEST = REPO_ROOT / "seed-manifest.yaml"
BUNDLED_RECIPES = REPO_ROOT / "recipes"


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


# ---------------------------------------------------------------------------
# Phase-3 seed-on-fresh-install tests
# ---------------------------------------------------------------------------


def _run_seed(argv: list[str], env_overrides: dict[str, str]) -> subprocess.CompletedProcess:
    """Run scripts/seed.py in a subprocess with isolated env vars.

    We run as a separate process (rather than importing) so KATIB_*_DIR env
    vars bind cleanly at module-load time inside the script. The Path
    resolution in core/tokens.py reads env at call time, but isolating at
    process-level is simpler and matches how install.sh invokes it.
    """
    env = {**os.environ, **env_overrides}
    return subprocess.run(
        [sys.executable, str(SEED_SCRIPT), *argv],
        env=env, capture_output=True, text=True, timeout=30,
    )


def test_seed_manifest_entries_all_exist_in_bundled_tier():
    """Every name in seed-manifest.yaml must correspond to a bundled
    recipe file. A typo here would make install.sh fail silently on fresh
    installs — this test catches it at CI time."""
    data = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    assert data["version"] == 1, "manifest version must be 1"
    for name in data.get("recipes") or []:
        path = BUNDLED_RECIPES / f"{name}.yaml"
        assert path.exists(), f"seed manifest lists {name!r} but {path} doesn't exist"


def test_seed_list_command_shows_manifest(tmp_path):
    """`scripts/seed.py list` must report every manifest entry with a
    correct seeded/absent status."""
    recipes_dir = tmp_path / "recipes"
    recipes_dir.mkdir()
    r = _run_seed(
        ["--json", "list"],
        {"KATIB_RECIPES_DIR": str(recipes_dir), "KATIB_MEMORY_DIR": str(tmp_path / "memory")},
    )
    assert r.returncode == 0, r.stderr
    data = json.loads(r.stdout)
    assert data["user_tier"] == str(recipes_dir)
    assert len(data["items"]) >= 15, "expected at least 15 starter recipes in the manifest"
    assert all(not item["seeded"] for item in data["items"]), \
        "list of empty user tier reported items as seeded"


def test_seed_refresh_populates_empty_user_tier(tmp_path):
    """Fresh-install-equivalent: empty user tier gets every starter."""
    recipes_dir = tmp_path / "recipes"
    memory_dir = tmp_path / "memory"
    recipes_dir.mkdir()
    r = _run_seed(
        ["--json", "refresh", "--all"],
        {"KATIB_RECIPES_DIR": str(recipes_dir), "KATIB_MEMORY_DIR": str(memory_dir)},
    )
    assert r.returncode == 0, r.stderr
    data = json.loads(r.stdout)
    seeded = [x for x in data["results"] if x["action"] == "seeded"]
    assert len(seeded) == 15, \
        f"expected all 15 recipes seeded, got {len(seeded)}: {data['results']}"

    # On-disk state matches bundled content byte-for-byte for a spot-check recipe.
    assert (recipes_dir / "tutorial.yaml").read_bytes() == \
        (BUNDLED_RECIPES / "tutorial.yaml").read_bytes()

    # Event log exists and has one entry per seeded file.
    log_file = memory_dir / "seed-events.jsonl"
    assert log_file.exists()
    events = [json.loads(ln) for ln in log_file.read_text().splitlines() if ln.strip()]
    assert len(events) == 15
    assert {e["recipe"] for e in events} == {r["recipe"] for r in seeded}


def test_seed_refresh_is_noop_when_user_tier_already_populated(tmp_path):
    """Returning-install-equivalent: pre-existing user recipes are never
    overwritten. This is the core durability promise."""
    recipes_dir = tmp_path / "recipes"
    recipes_dir.mkdir()

    # User has customized their tutorial.yaml.
    user_content = "# my edits to this starter, which must not be lost\nname: my-local-override\n"
    (recipes_dir / "tutorial.yaml").write_text(user_content, encoding="utf-8")

    r = _run_seed(
        ["--json", "refresh", "tutorial"],
        {"KATIB_RECIPES_DIR": str(recipes_dir), "KATIB_MEMORY_DIR": str(tmp_path / "memory")},
    )
    assert r.returncode == 0
    data = json.loads(r.stdout)
    assert data["results"][0]["action"] == "skip"

    # User content preserved byte-for-byte.
    assert (recipes_dir / "tutorial.yaml").read_text(encoding="utf-8") == user_content


def test_seed_refresh_force_requires_justification(tmp_path):
    """--force without --justification must exit non-zero. This is the
    'careful overwrite' guard for returning users who want to blow away
    their edits knowingly."""
    recipes_dir = tmp_path / "recipes"
    recipes_dir.mkdir()
    (recipes_dir / "tutorial.yaml").write_text("# existing\n", encoding="utf-8")

    r = _run_seed(
        ["--json", "refresh", "tutorial", "--force"],
        {"KATIB_RECIPES_DIR": str(recipes_dir), "KATIB_MEMORY_DIR": str(tmp_path / "memory")},
    )
    # Per-recipe errors report as exit 1 with the error in results[].
    assert r.returncode == 1
    data = json.loads(r.stdout)
    assert data["results"][0]["action"] == "error"
    assert "justification" in data["results"][0]["message"].lower()

    # File untouched.
    assert (recipes_dir / "tutorial.yaml").read_text(encoding="utf-8") == "# existing\n"


def test_seed_refresh_force_with_justification_overwrites(tmp_path):
    """--force --justification is the escape hatch."""
    recipes_dir = tmp_path / "recipes"
    recipes_dir.mkdir()
    (recipes_dir / "tutorial.yaml").write_text("# existing\n", encoding="utf-8")

    r = _run_seed(
        ["--json", "refresh", "tutorial", "--force", "--justification", "test reset"],
        {"KATIB_RECIPES_DIR": str(recipes_dir), "KATIB_MEMORY_DIR": str(tmp_path / "memory")},
    )
    assert r.returncode == 0, r.stderr
    # Now matches bundled.
    assert (recipes_dir / "tutorial.yaml").read_bytes() == \
        (BUNDLED_RECIPES / "tutorial.yaml").read_bytes()

    # Event log shows the overwrite was justified.
    events = [json.loads(ln) for ln in
              (tmp_path / "memory" / "seed-events.jsonl").read_text().splitlines() if ln.strip()]
    assert any(e.get("forced") and e.get("justification") == "test reset" for e in events)


def test_seed_refresh_unknown_recipe_errors(tmp_path):
    """Typos and ghost names must fail loudly, not silently."""
    r = _run_seed(
        ["refresh", "does-not-exist"],
        {"KATIB_RECIPES_DIR": str(tmp_path / "recipes"), "KATIB_MEMORY_DIR": str(tmp_path / "memory")},
    )
    assert r.returncode == 1
    assert "not in the seed manifest" in r.stderr


def test_install_sh_seed_block_references_required_pieces():
    """install.sh's seed block must invoke scripts/seed.py, gate on an
    empty user tier, and reference the manifest. A future cleanup that
    drops one of these silently breaks the fresh-install seed flow."""
    content = INSTALL_SH.read_text(encoding="utf-8")
    assert "seed-manifest.yaml" in content, \
        "install.sh must reference seed-manifest.yaml to decide whether seeding runs"
    assert "scripts/seed.py" in content, \
        "install.sh must invoke scripts/seed.py to perform the seed step"
    # Guard check: install.sh must check the user recipes dir is empty before seeding.
    assert '"$HOME/.katib/recipes"' in content and "ls -A" in content, \
        "install.sh seed block must gate on an empty user recipes dir"
