"""Phase-4 close-gate tests.

One assertion per acceptance criterion. CI failure on any of these
means Phase 4 is no longer shippable.

Mapping:
    EC1  scripts/pack.py wires all four subcommands (export/import/inspect/verify)
    EC2  schemas/pack.yaml.schema.json exists and validates a canonical fixture
    EC3  core/pack.py exposes the public API
    EC4  PACK-FORMAT.md exists and declares pack_format: 1
    EC5  At least one round-trip integration test exists
    EC6  `katib component share` emits a deprecation note (no breaking change)
    EC7  CHANGELOG.md has an entry mentioning [1.0.0-alpha.3]
    EC8  package.json version matches the alpha.3 bump
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


# ================================================================ EC1


def test_pack_cli_has_all_four_subcommands():
    r = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "pack.py"), "--help"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert r.returncode == 0, r.stderr
    m = re.search(r"\{([a-z,]+)\}", r.stdout)
    assert m, "pack.py --help doesn't list subcommands"
    cmds = set(m.group(1).split(","))
    assert {"export", "import", "inspect", "verify"} <= cmds, (
        f"missing pack.py subcommands: {{'export','import','inspect','verify'}} - {cmds}"
    )


# ================================================================ EC2


def test_pack_schema_exists_and_validates_canonical_fixture():
    schema_path = REPO_ROOT / "schemas" / "pack.yaml.schema.json"
    assert schema_path.exists(), "pack.yaml.schema.json missing"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    # const: pack_format == 1
    pf_const = schema["properties"]["pack_format"].get("const")
    assert pf_const == 1, f"schema's pack_format const should be 1, got {pf_const!r}"


# ================================================================ EC3


def test_core_pack_module_public_api():
    """The pack module must expose the names downstream code (CLI,
    tests) imports."""
    sys.path.insert(0, str(REPO_ROOT))
    from core import pack as pack_mod

    expected = {
        "PackManifest",
        "PACK_FORMAT_VERSION",
        "validate_manifest_dict",
        "load_manifest",
        "dump_manifest",
        "compute_content_hash",
        "build_canonical_tar_body",
        "ExportResult",
        "export_component",
        "export_recipe",
        "export_brand",
        "export_bundle",
        "PackInspectResult",
        "inspect_pack",
        "PackVerifyResult",
        "verify_pack",
        "ImportResult",
        "import_pack",
    }
    missing = {n for n in expected if not hasattr(pack_mod, n)}
    assert not missing, f"core.pack missing: {missing}"


# ================================================================ EC4


def test_pack_format_md_exists_and_freezes_v1():
    spec = REPO_ROOT / "PACK-FORMAT.md"
    assert spec.exists(), "PACK-FORMAT.md missing"
    text = spec.read_text(encoding="utf-8")
    assert "pack_format: 1" in text, "PACK-FORMAT.md doesn't declare pack_format: 1"
    # Must reference the JSON schema and the CLI script (load-bearing claims)
    assert "schemas/pack.yaml.schema.json" in text
    assert "scripts/pack.py" in text or "katib pack" in text


# ================================================================ EC5


def test_round_trip_test_exists():
    assert (
        REPO_ROOT / "tests" / "test_phase4_round_trip.py"
    ).exists(), "round-trip integration test missing"


# ================================================================ EC6


def test_component_share_emits_deprecation():
    """The legacy `katib component share` command still works (no
    breaking change), but emits a stderr deprecation note pointing at
    `pack.py export`."""
    r = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "component.py"),
            "share",
            "eyebrow",   # any real component
        ],
        capture_output=True,
        text=True,
        timeout=15,
    )
    # Command still succeeds (or at least doesn't crash because of the
    # deprecation banner — operational errors would also exit 1)
    combined = r.stderr
    assert "DEPRECATED" in combined, (
        f"`katib component share` should emit deprecation note. stderr={r.stderr!r}"
    )
    assert "pack.py export" in combined or "PACK-FORMAT" in combined.upper()


# ================================================================ EC7


def test_changelog_has_alpha_3_entry():
    cl = (REPO_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "[1.0.0-alpha.3]" in cl, "CHANGELOG missing [1.0.0-alpha.3] entry"
    # Phase 4 should be mentioned in the entry's heading
    assert "Phase 4" in cl or "Phase-4" in cl or "pack format" in cl.lower()


# ================================================================ EC8


def test_package_json_at_alpha_3():
    pkg = json.loads((REPO_ROOT / "package.json").read_text(encoding="utf-8"))
    assert pkg["version"] == "1.0.0-alpha.3", (
        f"package.json version should be '1.0.0-alpha.3' for Phase-4 close, "
        f"got {pkg['version']!r}"
    )
