"""Screenshot provider — Playwright + Chromium.

Captures a URL to PNG at 2x density (retina). Content-hashes the spec
(url + viewport + hide/wait rules) for caching — identical specs skip
Playwright entirely. Ported from v1 shot.py caching logic.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from core.image.base import ProviderError, ResolvedImage


class ScreenshotProvider:
    name = "screenshot"

    def is_available(self) -> tuple[bool, str]:
        try:
            from playwright.sync_api import sync_playwright  # noqa: F401
        except ImportError:
            return False, (
                "Playwright not installed. Install via:\n"
                "    uv sync --extra screenshots\n"
                "    uv run playwright install chromium"
            )
        return True, ""

    def cache_key(self, spec: dict) -> str:
        normalized = {
            "url": spec["url"],
            "viewport": spec.get("viewport", [1440, 900]),
            "wait_for": spec.get("wait_for"),
            "hide": sorted(spec.get("hide", [])),
            "device_scale": spec.get("device_scale", 2),
            "full_page": spec.get("full_page", False),
            "clip": spec.get("clip"),
        }
        blob = json.dumps(normalized, sort_keys=True)
        return hashlib.sha256(blob.encode()).hexdigest()[:16]

    def resolve(self, spec: dict, cache_dir: Path) -> ResolvedImage:
        if "url" not in spec:
            raise ProviderError("screenshot: spec missing 'url'")

        key = self.cache_key(spec)
        dest = cache_dir / f"{key}.png"
        if dest.exists():
            return ResolvedImage(
                path=dest.resolve(),
                content_hash=key,
                alt_hint=spec.get("alt_text"),
            )

        cache_dir.mkdir(parents=True, exist_ok=True)
        from playwright.sync_api import sync_playwright

        viewport = spec.get("viewport", [1440, 900])
        wait_for = spec.get("wait_for")
        hide = spec.get("hide", [])
        device_scale = spec.get("device_scale", 2)

        with sync_playwright() as p:
            browser = p.chromium.launch()
            try:
                ctx = browser.new_context(
                    viewport={"width": viewport[0], "height": viewport[1]},
                    device_scale_factor=device_scale,
                )
                page = ctx.new_page()
                page.goto(spec["url"], wait_until="networkidle")
                if wait_for:
                    page.wait_for_selector(wait_for)
                if hide:
                    page.add_style_tag(
                        content="\n".join(
                            f"{sel} {{ visibility: hidden !important }}" for sel in hide
                        )
                    )
                page.screenshot(
                    path=str(dest),
                    full_page=spec.get("full_page", False),
                )
            finally:
                browser.close()

        return ResolvedImage(
            path=dest.resolve(),
            content_hash=key,
            alt_hint=spec.get("alt_text"),
        )
