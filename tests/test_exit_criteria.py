"""Phase 2 Day 14 — exit-criteria compliance tests.

One assertion per criterion listed in the ADR (§Phase 2 exit criteria).
CI failure on any of these means Phase 2 is no longer shippable.

Mapping:
    EC1  Bloom framework guide renders via v2 tutorial recipe
    EC2  two-column-image-text renders with user-file / gemini / url
    EC3  tutorial-step renders with and without screenshots
    EC4  chart-donut renders via inline-svg
    EC5  Gemini-missing-key path fails loud
    EC6  SKILL.md describes v2 flow + enforcement rules
    EC7  /katib context-aware mode infers recipe + brand + lang
    EC8  Fresh-install check — build.py tutorial --lang en works cleanly
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


# ================================================================ EC1


def test_ec1_bloom_framework_guide_renders(tmp_path):
    """EC1: The Bloom framework guide renders via v2 tutorial recipe."""
    out_pdf = tmp_path / "tutorial.en.pdf"
    result = subprocess.run(
        ["uv", "run", "scripts/build.py", "tutorial",
         "--lang", "en", "--brand", "jasem", "--out", str(out_pdf)],
        cwd=REPO_ROOT, capture_output=True, text=True, timeout=120,
    )
    assert result.returncode == 0, (
        f"tutorial render failed:\n  stdout: {result.stdout}\n  stderr: {result.stderr}"
    )
    assert out_pdf.exists()
    # Bloom framework guide is ~90-120KB in EN
    assert 50_000 < out_pdf.stat().st_size < 300_000, (
        f"tutorial PDF size {out_pdf.stat().st_size} outside expected range"
    )


# ================================================================ EC2


def test_ec2_two_column_image_text_component_exists():
    """EC2: two-column-image-text component shipped with user-file + gemini + url support."""
    import yaml
    cdir = REPO_ROOT / "components" / "sections" / "two-column-image-text"
    assert (cdir / "component.yaml").exists()
    meta = yaml.safe_load((cdir / "component.yaml").read_text("utf-8"))
    # Extract sources_accepted from the image input declaration
    sources: set = set()
    for entry in meta.get("accepts", {}).get("inputs", []) or []:
        if isinstance(entry, dict) and len(entry) == 1:
            _, decl = next(iter(entry.items()))
            if isinstance(decl, dict) and decl.get("type") == "image":
                sources.update(decl.get("sources_accepted", []))
    assert "user-file" in sources
    assert "gemini" in sources
    assert "url" in sources


# ================================================================ EC3


def test_ec3_tutorial_step_component_supports_optional_screenshot():
    """EC3: tutorial-step declares screenshot input as optional + accepts user-file."""
    import yaml
    cdir = REPO_ROOT / "components" / "sections" / "tutorial-step"
    assert (cdir / "component.yaml").exists()
    meta = yaml.safe_load((cdir / "component.yaml").read_text("utf-8"))
    # Find screenshot input
    screenshot_decl = None
    for entry in meta.get("accepts", {}).get("inputs", []) or []:
        if isinstance(entry, dict) and len(entry) == 1:
            name, decl = next(iter(entry.items()))
            if name == "screenshot" and isinstance(decl, dict):
                screenshot_decl = decl
                break
    assert screenshot_decl is not None, "tutorial-step must declare a screenshot input"
    assert not screenshot_decl.get("required", False), "screenshot must be optional"
    sources = set(screenshot_decl.get("sources_accepted", []))
    assert "screenshot" in sources or "user-file" in sources


# ================================================================ EC4


def test_ec4_chart_donut_renders_via_inline_svg():
    """EC4: chart-donut declares inline-svg as its only accepted source."""
    import yaml
    cdir = REPO_ROOT / "components" / "sections" / "chart-donut"
    assert (cdir / "component.yaml").exists()
    meta = yaml.safe_load((cdir / "component.yaml").read_text("utf-8"))
    sources: set = set()
    for entry in meta.get("accepts", {}).get("inputs", []) or []:
        if isinstance(entry, dict) and len(entry) == 1:
            _, decl = next(iter(entry.items()))
            if isinstance(decl, dict) and decl.get("type") == "image":
                sources.update(decl.get("sources_accepted", []))
    assert sources == {"inline-svg"}, (
        f"chart-donut must accept only inline-svg; got {sources}"
    )


# ================================================================ EC5


def test_ec5_gemini_missing_key_fails_loud(monkeypatch):
    """EC5: Gemini-sourced request without GEMINI_API_KEY raises a clear error."""
    from core.image.gemini import GeminiProvider
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    provider = GeminiProvider()
    ready, reason = provider.is_available()
    assert not ready
    assert "GEMINI_API_KEY" in reason


# ================================================================ EC6


def test_ec6_skill_md_describes_v2_flow():
    """EC6: SKILL.md references the invocation modes + decision gate + rules."""
    skill_md = (REPO_ROOT / "SKILL.md").read_text("utf-8")
    # Sanity markers — these are the concrete v2-flow elements
    required_markers = [
        "Invocation modes",
        "route.py",
        "infer",
        "ask_questions",
        "AskUserQuestion",
        "capabilities.yaml",
    ]
    missing = [m for m in required_markers if m not in skill_md]
    assert not missing, f"SKILL.md missing v2 markers: {missing}"


# ================================================================ EC7


def test_ec7_context_aware_mode_infers_signals(tmp_path):
    """EC7: /katib context-aware mode — transcript → correct recipe + brand + lang."""
    transcript = (
        "render tutorial framework-guide bloom ai-collaboration production "
        "in English with jasem brand"
    )
    result = subprocess.run(
        ["uv", "run", "scripts/route.py", "infer",
         "--transcript", transcript, "--no-persist"],
        cwd=REPO_ROOT, capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0
    inferred = json.loads(result.stdout)
    assert inferred["action"] == "render"
    assert inferred["recipe"] == "tutorial"
    assert inferred["brand"] == "jasem"
    assert inferred["lang"] == "en"
    assert inferred["confidence"] == "HIGH"


# ================================================================ EC8


def test_ec8_fresh_install_tutorial_renders(tmp_path):
    """EC8: build.py tutorial --lang en runs cleanly from repo HEAD.

    Proxy for the fresh-install check: if the CLI works from a freshly-imported
    Python environment (which pytest gives us), the same code path will work
    after install.sh runs.
    """
    out_pdf = tmp_path / "fresh.pdf"
    result = subprocess.run(
        ["uv", "run", "scripts/build.py", "tutorial",
         "--lang", "en", "--out", str(out_pdf)],
        cwd=REPO_ROOT, capture_output=True, text=True, timeout=120,
    )
    assert result.returncode == 0, (
        f"fresh-install build failed:\n  stdout: {result.stdout}\n  stderr: {result.stderr}"
    )
    assert out_pdf.exists()
    # No raw Python tracebacks leaked — clean stdout
    assert "Traceback" not in result.stdout
    assert "Traceback" not in result.stderr
