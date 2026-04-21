#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "playwright>=1.44",
# ]
# ///
"""Katib screenshot capture — Playwright → PNG at print-quality density.

Produces crisp 2x (retina) PNGs suitable for embedding in WeasyPrint-rendered
PDFs. Supports viewport presets, login-cookie injection, wait-for-selector,
sticky-header hiding, and sidecar metadata for alt-text + provenance.

Usage:
    # Minimal — capture a page, save to folder
    uv run scripts/shot.py --url https://example.com --out step-1.png

    # Into a Katib generation folder (writes to <folder>/assets/screenshots/)
    uv run scripts/shot.py --url https://example.com --folder /path/to/gen-folder --name step-1

    # Viewport preset
    uv run scripts/shot.py --url ... --viewport mobile --out step-1.png

    # Wait for dynamic content
    uv run scripts/shot.py --url ... --wait-for ".dashboard-loaded" --out step.png

    # Hide sticky elements
    uv run scripts/shot.py --url ... --hide "header.sticky,.cookie-banner" --out step.png

    # Clip to a specific selector (only capture one region)
    uv run scripts/shot.py --url ... --clip ".hero-section" --out hero.png

    # Auth via cookies (JSON: [{name, value, domain, path}, ...])
    uv run scripts/shot.py --url ... --cookies ~/.katib/soul-hub-cookies.json --out step.png

    # Dark mode
    uv run scripts/shot.py --url ... --theme dark --out step.png

First run:
    playwright install chromium     # one-time browser download (~200MB)

Output:
    <path>.png        — PNG at --scale density (default 2x)
    <path>.meta.json  — alt-text, url, viewport, theme, timestamp
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

CACHE_SCHEMA_VERSION = 1

VIEWPORTS = {
    "desktop": {"width": 1440, "height": 900},
    "laptop":  {"width": 1280, "height": 800},
    "tablet":  {"width": 1024, "height": 768},
    "mobile":  {"width": 390,  "height": 844},
    "square":  {"width": 1200, "height": 1200},
}

# Per-user site configs — e.g. ~/.katib/sites/soul-hub.json — let callers
# invoke `--site soul-hub` instead of re-passing --hide / --cookies / --theme
# every time. CLI flags override config values.
SITE_CONFIG_DIR_ENV = "KATIB_SITES_DIR"
DEFAULT_SITE_CONFIG_DIR = Path.home() / ".katib" / "sites"

CACHE_DIR_ENV = "KATIB_CACHE_DIR"
DEFAULT_CACHE_DIR = Path.home() / ".katib" / "cache" / "screenshots"


def site_config_dir() -> Path:
    env = os.environ.get(SITE_CONFIG_DIR_ENV)
    return Path(env).expanduser() if env else DEFAULT_SITE_CONFIG_DIR


def load_site_config(name: str) -> dict:
    cfg_path = site_config_dir() / f"{name}.json"
    if not cfg_path.exists():
        print(f"✗ site config not found: {cfg_path}", file=sys.stderr)
        print(f"  Expected schema: {{\"hide\": [..], \"cookies\": \"path\", \"theme\": \"light|dark\", \"viewport\": \"laptop|...\"}}", file=sys.stderr)
        sys.exit(1)
    try:
        data = json.loads(cfg_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"✗ site config is not valid JSON: {cfg_path}: {e}", file=sys.stderr)
        sys.exit(1)
    if not isinstance(data, dict):
        print(f"✗ site config must be a JSON object: {cfg_path}", file=sys.stderr)
        sys.exit(1)
    # Resolve cookies path — absolute stays, relative resolves against config dir
    cookies = data.get("cookies")
    if cookies:
        p = Path(cookies).expanduser()
        if not p.is_absolute():
            p = (cfg_path.parent / p).resolve()
        data["cookies"] = str(p)
    return data


def resolve_output(args) -> Path:
    if args.out:
        return Path(args.out).expanduser().resolve()
    if args.folder:
        folder = Path(args.folder).expanduser().resolve()
        if not folder.exists():
            print(f"✗ folder not found: {folder}", file=sys.stderr)
            sys.exit(1)
        shots_dir = folder / "assets" / "screenshots"
        shots_dir.mkdir(parents=True, exist_ok=True)
        name = args.name or f"shot-{datetime.now().strftime('%H%M%S')}"
        if not name.endswith(".png"):
            name = f"{name}.png"
        return shots_dir / name
    print("✗ either --out or --folder is required", file=sys.stderr)
    sys.exit(1)


def load_cookies(path: str | None) -> list[dict]:
    if not path:
        return []
    p = Path(path).expanduser()
    if not p.exists():
        print(f"✗ cookies file not found: {p}", file=sys.stderr)
        sys.exit(1)
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"✗ cookies file not valid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    if not isinstance(data, list):
        print("✗ cookies file must be a JSON array of cookie objects", file=sys.stderr)
        sys.exit(1)
    return data


def cache_dir() -> Path:
    env = os.environ.get(CACHE_DIR_ENV)
    return Path(env).expanduser() if env else DEFAULT_CACHE_DIR


def _sha256_file(path: Path) -> str | None:
    """Hash a file's contents; returns None if unreadable."""
    try:
        h = hashlib.sha256()
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()
    except OSError:
        return None


def compute_cache_key(args, viewport: dict, cookies_path: str | None) -> tuple[str, dict]:
    """Derive a stable content-address hash for a capture's inputs.

    Returns (hex_digest_16, canonical_dict). The canonical dict is what
    gets hashed — inspectable via --dry-run for debugging.

    Schema v1 inputs: url, resolved viewport w/h, scale, theme, full_page,
    clip, wait_for, wait_ms, wait_until, hide (normalized), cookies file SHA.
    """
    hide_norm = ""
    if args.hide:
        hide_norm = ",".join(sorted(s.strip() for s in args.hide.split(",") if s.strip()))

    cookies_sha = None
    if cookies_path:
        cookies_sha = _sha256_file(Path(cookies_path).expanduser())

    canonical = {
        "v": CACHE_SCHEMA_VERSION,
        "url": args.url,
        "viewport": {"width": int(viewport["width"]), "height": int(viewport["height"])},
        "scale": float(args.scale),
        "theme": args.theme,
        "full_page": bool(args.full_page),
        "clip": args.clip or None,
        "wait_for": args.wait_for or None,
        "wait_ms": int(args.wait_ms),
        "wait_until": args.wait_until,
        "hide": hide_norm,
        "cookies_sha": cookies_sha,
    }
    payload = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
    digest = hashlib.sha256(payload).hexdigest()[:16]
    return digest, canonical


def _atomic_write_bytes(path: Path, data: bytes) -> None:
    """Write-to-temp-then-rename to avoid torn files on concurrent captures."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_bytes(data)
    tmp.replace(path)


def _atomic_copy(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    tmp = dst.with_suffix(dst.suffix + ".tmp")
    shutil.copyfile(src, tmp)
    tmp.replace(dst)


def resolve_text_bundle(legacy: str | None, en: str | None, ar: str | None) -> str | dict | None:
    """Build an alt/caption value for the sidecar.

    If any per-language flag is set, emit a dict (bundle form). Otherwise
    fall back to the legacy single string. None stays absent in the sidecar.
    """
    if en is not None or ar is not None:
        bundle: dict[str, str] = {}
        if en is not None:
            bundle["en"] = en
        if ar is not None:
            bundle["ar"] = ar
        if legacy is not None:
            for lang in ("en", "ar"):
                bundle.setdefault(lang, legacy)
        return bundle
    return legacy


def hide_selectors_js(selectors: list[str]) -> str:
    """Return JS that hides elements matching any of the selectors."""
    # Simple & safe — no string interpolation that could break CSS
    sel_json = json.dumps(selectors)
    return f"""
    (selectors => {{
      for (const sel of selectors) {{
        try {{
          document.querySelectorAll(sel).forEach(el => {{
            el.style.setProperty('visibility', 'hidden', 'important');
          }});
        }} catch (e) {{ /* invalid selector — skip */ }}
      }}
    }})({sel_json});
    """


def main() -> int:
    parser = argparse.ArgumentParser(description="Katib screenshot capture")
    parser.add_argument("--url", required=True, help="URL to capture")
    parser.add_argument("--out", help="Output PNG path (bypasses folder mode)")
    parser.add_argument("--folder", help="Katib generation folder (writes to <folder>/assets/screenshots/)")
    parser.add_argument("--name", help="Filename inside the screenshots dir (with or without .png)")

    parser.add_argument("--site", help="Load ~/.katib/sites/<name>.json for defaults (hide/cookies/theme/viewport). CLI flags override.")

    # Defaults None so we can distinguish user-set from unset; resolved below.
    parser.add_argument("--viewport", default=None, choices=list(VIEWPORTS.keys()),
                        help="Viewport preset (default: laptop, or site config)")
    parser.add_argument("--width", type=int, help="Custom viewport width (overrides preset)")
    parser.add_argument("--height", type=int, help="Custom viewport height (overrides preset)")
    parser.add_argument("--scale", type=float, default=2.0, help="Device scale factor (default: 2.0 for retina)")

    parser.add_argument("--full-page", action="store_true", help="Capture full scrolling page (not just viewport)")
    parser.add_argument("--clip", help="CSS selector — capture only this element's bounding box")

    parser.add_argument("--wait-for", help="CSS selector to wait for before capture")
    parser.add_argument("--wait-ms", type=int, default=800, help="Additional wait after page load (ms, default 800)")
    parser.add_argument("--wait-until", default="domcontentloaded",
                        choices=["load", "domcontentloaded", "networkidle", "commit"],
                        help="Playwright wait strategy (default: domcontentloaded — safe for SPAs with persistent connections)")
    parser.add_argument("--timeout-ms", type=int, default=20000, help="Navigation timeout (default 20000)")

    parser.add_argument("--hide", help="Comma-separated CSS selectors to hide before capture (e.g., sticky headers, cookie banners)")
    parser.add_argument("--cookies", help="Path to JSON file with cookies for auth")
    parser.add_argument("--theme", default=None, choices=["light", "dark"], help="prefers-color-scheme (default: light, or site config)")

    parser.add_argument("--alt", help="Alt text (legacy: applies to all languages)")
    parser.add_argument("--alt-en", help="English alt text (preferred over --alt for bilingual docs)")
    parser.add_argument("--alt-ar", help="Arabic alt text")
    parser.add_argument("--caption", help="Caption (legacy: applies to all languages)")
    parser.add_argument("--caption-en", help="English caption (preferred over --caption for bilingual docs)")
    parser.add_argument("--caption-ar", help="Arabic caption")

    parser.add_argument("--force", action="store_true", help="Overwrite existing PNG and bypass/refresh cache")
    parser.add_argument("--no-cache", action="store_true", help="Skip the content-addressed cache (always re-capture)")
    parser.add_argument("--cache-dir", help=f"Cache dir (default: ${CACHE_DIR_ENV} or {DEFAULT_CACHE_DIR})")
    parser.add_argument("--dry-run", action="store_true", help="Print resolved config + cache key, do not call Playwright")

    args = parser.parse_args()

    # Merge site config: CLI flag > config value > hardcoded default.
    site_cfg: dict = {}
    if args.site:
        site_cfg = load_site_config(args.site)

    if args.viewport is None:
        args.viewport = site_cfg.get("viewport", "laptop")
    if args.theme is None:
        args.theme = site_cfg.get("theme", "light")
    if args.hide is None and site_cfg.get("hide"):
        # Config stores list; shot.py --hide takes CSV string for consistency.
        hide_val = site_cfg["hide"]
        if isinstance(hide_val, list):
            args.hide = ",".join(hide_val)
        else:
            args.hide = str(hide_val)
    if args.cookies is None and site_cfg.get("cookies"):
        cookies_path = Path(site_cfg["cookies"])
        if cookies_path.exists():
            args.cookies = str(cookies_path)
        else:
            print(f"  ⚠ site cookies file missing: {cookies_path} — proceeding without auth", file=sys.stderr)

    # Validate viewport after merge (argparse choices only fires for explicit CLI value).
    if args.viewport not in VIEWPORTS:
        print(f"✗ viewport {args.viewport!r} from site config not in {sorted(VIEWPORTS)}", file=sys.stderr)
        return 1
    if args.theme not in ("light", "dark"):
        print(f"✗ theme {args.theme!r} from site config must be 'light' or 'dark'", file=sys.stderr)
        return 1

    target = resolve_output(args)

    vp = dict(VIEWPORTS[args.viewport])
    if args.width:
        vp["width"] = args.width
    if args.height:
        vp["height"] = args.height

    cache_root = Path(args.cache_dir).expanduser() if args.cache_dir else cache_dir()
    cache_enabled = not args.no_cache
    cache_key, _canonical = compute_cache_key(args, vp, args.cookies)
    cache_png = cache_root / f"{cache_key}.png"
    cache_meta = cache_root / f"{cache_key}.meta.json"

    if args.dry_run:
        print("DRY RUN — not calling Playwright")
        print(f"  site:     {args.site or 'none'}")
        print(f"  url:      {args.url}")
        print(f"  viewport: {vp['width']}x{vp['height']} @ {args.scale}x")
        print(f"  theme:    {args.theme}")
        print(f"  full_page: {args.full_page}")
        print(f"  clip:     {args.clip or 'none'}")
        print(f"  wait_for: {args.wait_for or 'none'}")
        print(f"  hide:     {args.hide or 'none'}")
        print(f"  cookies:  {args.cookies or 'none'}")
        print(f"  target:   {target}")
        print(f"  cache:    {'off' if not cache_enabled else 'on'} · key={cache_key} · "
              f"{'HIT' if (cache_enabled and cache_png.exists()) else 'MISS'} · {cache_png}")
        return 0

    if target.exists() and not args.force:
        print(f"✓ screenshot exists (use --force to regenerate): {target}")
        return 0

    alt_value = resolve_text_bundle(args.alt, args.alt_en, args.alt_ar)
    caption_value = resolve_text_bundle(args.caption, args.caption_en, args.caption_ar)

    if cache_enabled and not args.force and cache_png.exists():
        _atomic_copy(cache_png, target)
        size = target.stat().st_size
        meta = {
            "type": "screenshot",
            "url": args.url,
            "viewport": vp,
            "scale": args.scale,
            "theme": args.theme,
            "full_page": args.full_page,
            "clip": args.clip,
            "wait_for": args.wait_for,
            "hide": args.hide,
            "alt": alt_value if alt_value is not None else "",
            "caption": caption_value if caption_value is not None else "",
            "bytes": size,
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "cached_from": cache_key,
        }
        target.with_suffix(".meta.json").write_text(
            json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        print(f"✓ cache HIT · {size/1024:.0f} KB · key={cache_key}")
        print(f"  → {target}")
        return 0

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("✗ playwright not installed. Run via `uv run` or `pip install playwright`", file=sys.stderr)
        return 1

    cookies = load_cookies(args.cookies)

    print(f"Capturing · {args.viewport} ({vp['width']}x{vp['height']}) @ {args.scale}x · {args.url}", file=sys.stderr)

    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            context = browser.new_context(
                viewport=vp,
                device_scale_factor=args.scale,
                color_scheme=args.theme,
            )
            if cookies:
                context.add_cookies(cookies)

            page = context.new_page()
            try:
                page.goto(args.url, timeout=args.timeout_ms, wait_until=args.wait_until)
            except Exception as e:
                print(f"✗ failed to load {args.url}: {e}", file=sys.stderr)
                browser.close()
                return 2

            if args.wait_for:
                try:
                    page.wait_for_selector(args.wait_for, timeout=args.timeout_ms)
                except Exception as e:
                    print(f"  ⚠ wait-for selector {args.wait_for!r} did not appear: {e}", file=sys.stderr)

            if args.wait_ms:
                page.wait_for_timeout(args.wait_ms)

            if args.hide:
                selectors = [s.strip() for s in args.hide.split(",") if s.strip()]
                if selectors:
                    page.evaluate(hide_selectors_js(selectors))

            target.parent.mkdir(parents=True, exist_ok=True)

            if args.clip:
                el = page.locator(args.clip).first
                try:
                    el.screenshot(path=str(target))
                except Exception as e:
                    print(f"✗ failed to clip to {args.clip!r}: {e}", file=sys.stderr)
                    browser.close()
                    return 3
            else:
                page.screenshot(path=str(target), full_page=args.full_page)

            browser.close()
    except Exception as e:
        print(f"✗ playwright error: {e}", file=sys.stderr)
        return 4

    size = target.stat().st_size
    meta = {
        "type": "screenshot",
        "url": args.url,
        "viewport": vp,
        "scale": args.scale,
        "theme": args.theme,
        "full_page": args.full_page,
        "clip": args.clip,
        "wait_for": args.wait_for,
        "hide": args.hide,
        "alt": alt_value if alt_value is not None else "",
        "caption": caption_value if caption_value is not None else "",
        "bytes": size,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "cache_key": cache_key if cache_enabled else None,
    }
    meta_path = target.with_suffix(".meta.json")
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    if cache_enabled:
        try:
            _atomic_copy(target, cache_png)
            cache_meta_data = {
                "v": CACHE_SCHEMA_VERSION,
                "key": cache_key,
                "url": args.url,
                "viewport": vp,
                "scale": args.scale,
                "theme": args.theme,
                "full_page": args.full_page,
                "clip": args.clip,
                "wait_for": args.wait_for,
                "wait_ms": args.wait_ms,
                "wait_until": args.wait_until,
                "hide": args.hide,
                "bytes": size,
                "created_at": meta["generated_at"],
            }
            _atomic_write_bytes(
                cache_meta,
                (json.dumps(cache_meta_data, indent=2) + "\n").encode("utf-8"),
            )
        except OSError as e:
            print(f"  ⚠ cache write failed (non-fatal): {e}", file=sys.stderr)

    cache_note = f" · cached[{cache_key}]" if cache_enabled else " · no-cache"
    print(f"✓ screenshot saved · {size/1024:.0f} KB{cache_note}")
    print(f"  → {target}")
    print(f"  meta: {meta_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
