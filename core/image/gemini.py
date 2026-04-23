"""Gemini image provider — Gemini Nano Banana 2.

Generates decorative cover art or editorial illustrations from a text
prompt. Content-hashes the full spec (prompt + style + aspect + model)
for caching — a repeat render with the same prompt skips the API call
and saves ~$0.12 per hit.

Fails loud on missing API key with actionable guidance. No silent
placeholder substitution — a PDF with a missing image is a production
incident for print deliverables.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

from core.image.base import ProviderError, ResolvedImage

GEMINI_MODEL = os.environ.get("KATIB_GEMINI_MODEL", "gemini-3-pro-image-preview")


class GeminiProvider:
    name = "gemini"

    def is_available(self) -> tuple[bool, str]:
        if not os.environ.get("GEMINI_API_KEY"):
            return False, (
                "GEMINI_API_KEY not set. Options:\n"
                "    1. export GEMINI_API_KEY=<your key>\n"
                "    2. Save it in ~/.config/katib/config.yaml\n"
                "    3. Change the recipe source from `gemini` to `user-file`\n"
                "    4. Run with --no-gemini-images to skip all gemini sources"
            )
        try:
            from google import genai  # noqa: F401
        except ImportError:
            return False, (
                "google-genai not installed. Install via: uv sync --extra gemini"
            )
        return True, ""

    def cache_key(self, spec: dict) -> str:
        normalized = {
            "prompt": spec.get("prompt", ""),
            "style": spec.get("style"),
            "aspect": spec.get("aspect", "1:1"),
            "model": GEMINI_MODEL,
        }
        blob = json.dumps(normalized, sort_keys=True)
        return hashlib.sha256(blob.encode()).hexdigest()[:16]

    def resolve(self, spec: dict, cache_dir: Path) -> ResolvedImage:
        prompt = spec.get("prompt")
        if not prompt:
            raise ProviderError("gemini: spec missing 'prompt'")

        key = self.cache_key(spec)
        dest = cache_dir / f"{key}.png"
        if dest.exists():
            return ResolvedImage(
                path=dest.resolve(),
                content_hash=key,
                alt_hint=spec.get("alt_text") or prompt[:120],
            )

        cache_dir.mkdir(parents=True, exist_ok=True)
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ProviderError("GEMINI_API_KEY missing at resolve() time")

        from google import genai

        style = spec.get("style")
        full_prompt = f"Style: {style}. {prompt}" if style else prompt

        client = genai.Client(api_key=api_key)
        resp = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=full_prompt,
        )

        img_bytes: bytes | None = None
        for candidate in getattr(resp, "candidates", []) or []:
            content = getattr(candidate, "content", None)
            for part in getattr(content, "parts", []) or []:
                inline = getattr(part, "inline_data", None)
                if inline and getattr(inline, "data", None):
                    img_bytes = inline.data
                    break
            if img_bytes:
                break

        if not img_bytes:
            raise ProviderError(
                f"Gemini did not return image data for prompt: {prompt[:80]!r}"
            )

        dest.write_bytes(img_bytes)
        return ResolvedImage(
            path=dest.resolve(),
            content_hash=key,
            alt_hint=spec.get("alt_text") or prompt[:120],
        )
