"""Common image-provider interface.

Components declare `type: image` inputs with `sources_accepted: [...]`.
Recipes supply a provider-specific spec per invocation. The engine walks
the provider registry, validates availability, computes a content-hash
cache key, resolves the image, and returns a `ResolvedImage` that the
component template embeds (either a file path or inline SVG).

Providers fail loud on unmet prerequisites (missing API key, missing
Playwright, invalid spec). Silent degradation is unacceptable — a print
deliverable with a missing image is a production incident.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, runtime_checkable


@dataclass
class ResolvedImage:
    """A provider's output. Exactly one of `path` or `inline_svg` is set."""

    path: Path | None = None
    inline_svg: str | None = None
    content_hash: str | None = None
    alt_hint: str | None = None


@runtime_checkable
class Provider(Protocol):
    name: str

    def is_available(self) -> tuple[bool, str]: ...
    def cache_key(self, spec: dict) -> str: ...
    def resolve(self, spec: dict, cache_dir: Path) -> ResolvedImage: ...


class ProviderError(RuntimeError):
    """A provider couldn't resolve (bad spec, API failure, etc.)."""


class ProviderUnavailable(ProviderError):
    """Prerequisites unmet — missing dep, missing key, offline, etc."""


def resolve_image(
    spec: dict,
    cache_dir: Path,
    providers: dict[str, Provider],
    sources_accepted: list[str] | None = None,
) -> ResolvedImage:
    source = spec.get("source") or spec.get("provider")
    if not source:
        raise ProviderError(f"image spec missing 'source' field: {spec}")

    if sources_accepted is not None and source not in sources_accepted:
        raise ProviderError(
            f"source {source!r} not in component's sources_accepted "
            f"{sources_accepted}"
        )

    provider_name = "user-file" if source in ("url", "user-file") else source
    provider = providers.get(provider_name)
    if not provider:
        raise ProviderError(
            f"no provider registered for source {source!r}; "
            f"known: {sorted(providers)}"
        )

    available, reason = provider.is_available()
    if not available:
        raise ProviderUnavailable(f"{provider_name}: {reason}")

    return provider.resolve(spec, cache_dir)


def default_providers() -> dict[str, Provider]:
    from core.image.gemini import GeminiProvider
    from core.image.inline_svg import InlineSvgProvider
    from core.image.screenshot import ScreenshotProvider
    from core.image.user_file import UserFileProvider

    return {
        "user-file": UserFileProvider(),
        "screenshot": ScreenshotProvider(),
        "gemini": GeminiProvider(),
        "inline-svg": InlineSvgProvider(),
    }
