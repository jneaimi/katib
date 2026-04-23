#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Katib — install_fonts.py: fetch + install OFL fonts the skill depends on.

Fonts come from github.com/google/fonts (OFL collection). WeasyPrint resolves
them via fontconfig / OS font cache, so we drop files into:
  - macOS:   ~/Library/Fonts/Katib/
  - Linux:   ~/.local/share/fonts/Katib/
  - Windows: unsupported in this release — install fonts manually

Without this script, WeasyPrint silently falls back to system fonts whenever a
tokens.json family isn't installed locally — e.g. Amiri renders as Times, Cairo
renders as Arial — producing technically-valid but visually-wrong output.

Usage:
  python3 scripts/install_fonts.py              # install missing
  python3 scripts/install_fonts.py --list       # print manifest, no network
  python3 scripts/install_fonts.py --verify     # check what's already there
  python3 scripts/install_fonts.py --force      # re-download everything
  python3 scripts/install_fonts.py --dry-run    # preview, no writes
  python3 scripts/install_fonts.py --only Cairo,Amiri  # subset
"""
from __future__ import annotations

import argparse
import hashlib
import os
import platform
import shutil
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

SKILL_ROOT = Path(__file__).resolve().parent.parent

# ===================== MANIFEST =====================
#
# Each entry lists file names + the raw github path they live at.
# Base URL always ends with '/' and joins with file name. Sourced from the
# official google/fonts OFL repository, which mirrors fonts.google.com.

GH_RAW = "https://github.com/google/fonts/raw/main/ofl"

FONTS: dict[str, dict[str, Any]] = {
    "Cairo": {
        "base_url": f"{GH_RAW}/cairo/",
        "files": ["Cairo[slnt,wght].ttf"],  # variable font, one file covers all weights
        "script": "arabic",
        "used_by": ["tutorial", "personal", "financial", "marketing-print"],
        "license": "OFL-1.1",
    },
    "Amiri": {
        "base_url": f"{GH_RAW}/amiri/",
        "files": [
            "Amiri-Regular.ttf",
            "Amiri-Bold.ttf",
            "Amiri-Italic.ttf",
            "Amiri-BoldItalic.ttf",
        ],
        "script": "arabic",
        "used_by": ["editorial", "formal", "academic", "report", "legal"],
        "license": "OFL-1.1",
    },
    "Tajawal": {
        "base_url": f"{GH_RAW}/tajawal/",
        "files": ["Tajawal-Regular.ttf", "Tajawal-Medium.ttf", "Tajawal-Bold.ttf"],
        "script": "arabic",
        "used_by": ["(optional AR corporate preset in add_domain.py)"],
        "license": "OFL-1.1",
    },
    "IBM Plex Sans Arabic": {
        "base_url": f"{GH_RAW}/ibmplexsansarabic/",
        "files": [
            "IBMPlexSansArabic-Regular.ttf",
            "IBMPlexSansArabic-Medium.ttf",
            "IBMPlexSansArabic-SemiBold.ttf",
            "IBMPlexSansArabic-Bold.ttf",
        ],
        "script": "arabic",
        "used_by": ["tutorial (fallback)", "personal (fallback)"],
        "license": "OFL-1.1",
    },
    "Inter": {
        "base_url": f"{GH_RAW}/inter/",
        "files": ["Inter[opsz,wght].ttf", "Inter-Italic[opsz,wght].ttf"],
        "script": "latin",
        "used_by": ["tutorial", "personal", "financial", "marketing-print"],
        "license": "OFL-1.1",
    },
    "Newsreader": {
        "base_url": f"{GH_RAW}/newsreader/",
        "files": ["Newsreader[opsz,wght].ttf", "Newsreader-Italic[opsz,wght].ttf"],
        "script": "latin",
        "used_by": ["editorial", "academic", "report", "legal"],
        "license": "OFL-1.1",
    },
    "JetBrains Mono": {
        "base_url": f"{GH_RAW}/jetbrainsmono/",
        "files": ["JetBrainsMono[wght].ttf", "JetBrainsMono-Italic[wght].ttf"],
        "script": "latin",
        "used_by": ["all (code blocks)"],
        "license": "OFL-1.1",
    },
}


# ===================== PATH RESOLUTION =====================

def default_install_dir() -> Path:
    """OS-standard user font dir, suffixed with Katib/ to keep ours grouped."""
    system = platform.system()
    if system == "Darwin":
        return Path.home() / "Library" / "Fonts" / "Katib"
    if system == "Linux":
        base = os.environ.get("XDG_DATA_HOME") or str(Path.home() / ".local" / "share")
        return Path(base) / "fonts" / "Katib"
    # Windows & others — leave to the user; fail loudly below.
    return Path.home() / "AppData" / "Local" / "Microsoft" / "Windows" / "Fonts" / "Katib"


def supported_os() -> bool:
    return platform.system() in ("Darwin", "Linux")


# ===================== HTTP =====================

def _encode_url(url: str) -> str:
    """Percent-encode the path portion so brackets in variable-font filenames
    (e.g. 'Cairo[slnt,wght].ttf') survive GitHub's raw URL handling."""
    parts = urllib.parse.urlsplit(url)
    # Preserve `/` in the path, encode everything else.
    safe_path = urllib.parse.quote(parts.path, safe="/")
    return urllib.parse.urlunsplit(
        (parts.scheme, parts.netloc, safe_path, parts.query, parts.fragment)
    )


def fetch(url: str, timeout: int = 30) -> bytes:
    """GET with a reasonable UA. Raises on HTTP != 200."""
    req = urllib.request.Request(
        _encode_url(url),
        headers={"User-Agent": "katib/install_fonts.py (https://github.com/jneaimi/katib)"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        if resp.status != 200:
            raise RuntimeError(f"HTTP {resp.status} for {url}")
        return resp.read()


def sha256_of(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# ===================== ACTIONS =====================

def list_manifest(only: set[str] | None = None) -> None:
    """Print the manifest (no network)."""
    total_files = 0
    print(f"\nKatib font manifest — all OFL-1.1, sourced from github.com/google/fonts\n")
    print(f"  Install dir: {default_install_dir()}\n")
    for name, meta in FONTS.items():
        if only and name not in only:
            continue
        used = ", ".join(meta["used_by"])
        print(f"  {name:<20}  ({meta['script']})  — used by: {used}")
        for f in meta["files"]:
            print(f"      {f}")
        total_files += len(meta["files"])
        print()
    print(f"  Total: {len([n for n in FONTS if not only or n in only])} families, {total_files} files")
    print()


def verify_installed(target: Path, only: set[str] | None = None) -> dict[str, Any]:
    """Return {"installed": [...], "missing": [...]} relative to the manifest."""
    installed, missing = [], []
    for name, meta in FONTS.items():
        if only and name not in only:
            continue
        for fname in meta["files"]:
            path = target / fname
            if path.exists() and path.stat().st_size > 1024:
                installed.append((name, fname, path.stat().st_size))
            else:
                missing.append((name, fname))
    return {"installed": installed, "missing": missing}


def install_font_files(
    target: Path,
    *,
    force: bool,
    dry_run: bool,
    only: set[str] | None,
) -> dict[str, Any]:
    """Fetch + drop files into target. Returns {"ok": [...], "skipped": [...], "failed": [...]}."""
    if not dry_run:
        target.mkdir(parents=True, exist_ok=True)

    ok, skipped, failed = [], [], []

    for name, meta in FONTS.items():
        if only and name not in only:
            continue
        for fname in meta["files"]:
            dest = target / fname
            url = meta["base_url"] + fname

            if dest.exists() and dest.stat().st_size > 1024 and not force:
                skipped.append((name, fname, "already present"))
                continue

            if dry_run:
                ok.append((name, fname, url, 0, "(dry-run)"))
                continue

            try:
                data = fetch(url)
                if len(data) < 1024:
                    raise RuntimeError(f"response too small ({len(data)} bytes) — likely 404 HTML")
                dest.write_bytes(data)
                sha = sha256_of(data)[:12]
                ok.append((name, fname, url, len(data), sha))
            except (urllib.error.URLError, RuntimeError, TimeoutError) as e:
                failed.append((name, fname, url, str(e)))

    return {"ok": ok, "skipped": skipped, "failed": failed}


def refresh_font_cache(target: Path) -> None:
    """Kick the OS font cache so newly-installed fonts are findable.

    macOS: fontconfig picks up ~/Library/Fonts on next process start — no action
    required for WeasyPrint CLI invocations.
    Linux: `fc-cache -f` is the standard refresh.
    """
    if platform.system() == "Linux" and shutil.which("fc-cache"):
        try:
            subprocess.run(["fc-cache", "-f", str(target.parent)],
                           check=False, capture_output=True, timeout=60)
            print("  ✓ refreshed fontconfig cache (fc-cache)")
        except (subprocess.SubprocessError, OSError) as e:
            print(f"  ⚠ fc-cache failed: {e} (fonts still installed — try manually)")


# ===================== OUTPUT =====================

def _fmt_size(n: int) -> str:
    if n < 1024:
        return f"{n} B"
    if n < 1024 * 1024:
        return f"{n // 1024} KB"
    return f"{n / (1024 * 1024):.1f} MB"


def print_install_summary(result: dict[str, Any], *, dry_run: bool) -> None:
    ok = result["ok"]
    skipped = result["skipped"]
    failed = result["failed"]

    for name, fname, url, size, sha in ok:
        if dry_run:
            print(f"  + would fetch {fname:<36}  {url}")
        else:
            print(f"  ✓ installed   {fname:<36}  {_fmt_size(size):>10}  sha256:{sha}…")
    for name, fname, reason in skipped:
        print(f"  · skipped     {fname:<36}  ({reason})")
    for name, fname, url, err in failed:
        print(f"  ✗ failed      {fname:<36}  {err}")
        print(f"    (tried: {url})")

    total_ok = len(ok)
    total_skipped = len(skipped)
    total_failed = len(failed)
    print()
    if dry_run:
        print(f"  dry-run: would fetch {total_ok} files, skip {total_skipped}, would leave {total_failed} failed")
    else:
        print(f"  fetched={total_ok}  skipped={total_skipped}  failed={total_failed}")


def print_verify_summary(result: dict[str, Any]) -> None:
    installed = result["installed"]
    missing = result["missing"]
    for name, fname, size in installed:
        print(f"  ✓ {fname:<36}  {_fmt_size(size):>10}")
    for name, fname in missing:
        print(f"  ✗ missing    {fname:<36}")
    print()
    print(f"  installed={len(installed)}  missing={len(missing)}")


# ===================== MAIN =====================

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--list", action="store_true", help="Print manifest, no network")
    parser.add_argument("--verify", action="store_true", help="Check what's already installed")
    parser.add_argument("--force", action="store_true", help="Re-fetch even if file exists")
    parser.add_argument("--dry-run", action="store_true", help="Print plan, no writes/fetches")
    parser.add_argument("--only", metavar="FAMILIES",
                        help="Comma-separated subset (e.g. 'Cairo,Amiri')")
    parser.add_argument("--target", metavar="DIR",
                        help="Override install dir (default: OS-standard)")
    args = parser.parse_args()

    only: set[str] | None = None
    if args.only:
        only = {s.strip() for s in args.only.split(",") if s.strip()}
        unknown = only - set(FONTS)
        if unknown:
            print(f"✗ unknown font(s): {', '.join(sorted(unknown))}", file=sys.stderr)
            print(f"  known: {', '.join(FONTS)}", file=sys.stderr)
            return 2

    if args.list:
        list_manifest(only)
        return 0

    target = Path(args.target).expanduser() if args.target else default_install_dir()

    if args.verify:
        print(f"\n▶ Verifying fonts in {target}\n")
        print_verify_summary(verify_installed(target, only))
        return 0

    if not supported_os():
        print(f"✗ OS not supported: {platform.system()}. "
              f"Install fonts manually from github.com/google/fonts/ofl/", file=sys.stderr)
        return 3

    print(f"\n▶ Installing Katib fonts to {target}")
    print(f"  (source: github.com/google/fonts, OFL-1.1)\n")
    result = install_font_files(target, force=args.force, dry_run=args.dry_run, only=only)
    print_install_summary(result, dry_run=args.dry_run)

    if args.dry_run:
        return 0

    if result["ok"]:
        refresh_font_cache(target)

    if result["failed"]:
        print(f"\n⚠ {len(result['failed'])} file(s) failed to download. "
              f"Re-run with --force to retry, or install manually from the URLs above.")
        return 1

    print(f"\n✓ Done. Run `python3 scripts/install_fonts.py --verify` to confirm.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
