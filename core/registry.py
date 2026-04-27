"""HTTP client for the katib marketplace registry.

The registry is a Next.js Route Handler running at
`https://jneaimi.com/api/katib` (override via `$KATIB_REGISTRY_URL`).
This module wraps the read-side endpoints used by `katib pack search`
and `katib pack install`. The write side (`POST /admin/packs`) is
exercised by the marketplace publish-on-merge workflow, never by the
CLI — end-users do not have curation tokens.

Stdlib-only: uses `urllib.request` so katib doesn't grow an HTTP
dependency. All network calls have explicit timeouts; nothing here
silently retries.

Endpoints we talk to:
  GET /registry?[q=…&domain=…&language=…&page=…&per_page=…]
  GET /packs/<author>/<name>
  GET /packs/<author>/<name>/<version>/download    (302 → R2)
"""
from __future__ import annotations

import json
import os
import shutil
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_REGISTRY_URL = "https://jneaimi.com/api/katib"
USER_AGENT = "katib-cli/0.x"

# Connect/read split is what `urllib` actually exposes via the single
# `timeout` arg — we keep both modest. A slow registry shouldn't lock
# the CLI for minutes.
_CONNECT_TIMEOUT_S = 10
_READ_TIMEOUT_S = 30


class RegistryError(Exception):
    """Network or HTTP-shape failure when talking to the registry."""

    def __init__(self, message: str, *, status: int | None = None):
        super().__init__(message)
        self.status = status


def registry_url() -> str:
    """Return the active registry base URL.

    `$KATIB_REGISTRY_URL` overrides the default. Trailing slashes are
    stripped so callers can `f"{registry_url()}/registry"` safely.
    """
    return os.environ.get("KATIB_REGISTRY_URL", DEFAULT_REGISTRY_URL).rstrip("/")


def _request(
    url: str,
    *,
    method: str = "GET",
    follow_redirects: bool = True,
    timeout: int = _READ_TIMEOUT_S,
) -> tuple[int, dict[str, str], bytes]:
    """Run a single HTTP request. Returns (status, headers, body).

    Never raises on non-2xx — caller decides what to do with status.
    Raises RegistryError on transport failures (DNS, connection refused,
    timeout). Headers are lower-cased for case-insensitive lookups.
    """
    req = urllib.request.Request(url, method=method)
    req.add_header("User-Agent", USER_AGENT)
    req.add_header("Accept", "application/json")

    opener = (
        urllib.request.build_opener()
        if follow_redirects
        else urllib.request.build_opener(_NoRedirectHandler())
    )

    try:
        with opener.open(req, timeout=timeout) as resp:
            body = resp.read()
            headers = {k.lower(): v for k, v in resp.headers.items()}
            return resp.status, headers, body
    except urllib.error.HTTPError as e:
        # Non-2xx still gets returned via the response; only network /
        # protocol errors raise. urllib raises HTTPError for 4xx/5xx if
        # we don't install a handler that swallows them — capture them
        # uniformly here.
        body = e.read() if e.fp else b""
        headers = {k.lower(): v for k, v in (e.headers or {}).items()}
        return e.code, headers, body
    except urllib.error.URLError as e:
        raise RegistryError(f"network error: {e.reason}") from e
    except TimeoutError as e:
        raise RegistryError(f"timeout: {e}") from e


class _NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *_args, **_kwargs):  # noqa: D401
        return None


def _parse_json(status: int, body: bytes) -> Any:
    if not body:
        raise RegistryError(f"empty response (status {status})", status=status)
    try:
        return json.loads(body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise RegistryError(
            f"invalid JSON from registry (status {status}): {e}",
            status=status,
        ) from e


# ---------------------------------------------------------------------------
# Read endpoints
# ---------------------------------------------------------------------------


def search_packs(
    *,
    q: str | None = None,
    domain: str | None = None,
    language: str | None = None,
    page: int = 1,
    per_page: int = 50,
) -> dict[str, Any]:
    """Query the registry index. Returns the raw `{packs, total, page, per_page}` dict."""
    qs: dict[str, str] = {}
    if q:
        qs["q"] = q
    if domain:
        qs["domain"] = domain
    if language:
        qs["language"] = language
    if page != 1:
        qs["page"] = str(page)
    if per_page != 50:
        qs["per_page"] = str(per_page)

    base = f"{registry_url()}/registry"
    url = base if not qs else f"{base}?{urllib.parse.urlencode(qs)}"

    status, _headers, body = _request(url)
    if status >= 400:
        raise RegistryError(
            f"registry search failed (HTTP {status})",
            status=status,
        )
    return _parse_json(status, body)


def get_pack_detail(author: str, name: str) -> dict[str, Any] | None:
    """Fetch full detail for `<author>/<name>`. Returns None on 404."""
    url = f"{registry_url()}/packs/{urllib.parse.quote(author)}/{urllib.parse.quote(name)}"
    status, _headers, body = _request(url)
    if status == 404:
        return None
    if status >= 400:
        raise RegistryError(
            f"pack detail failed (HTTP {status})",
            status=status,
        )
    return _parse_json(status, body)


# ---------------------------------------------------------------------------
# Download
# ---------------------------------------------------------------------------


@dataclass
class DownloadResult:
    """Outcome of `download_pack`. Path is the on-disk artifact."""

    path: Path
    size_bytes: int
    redirect_url: str | None
    content_hash_header: str | None


def download_pack(
    author: str,
    name: str,
    version: str,
    dest_path: Path,
) -> DownloadResult:
    """Download `<author>/<name>@<version>` to `dest_path`.

    Two-step: hit the redirect endpoint without following, capture the
    `Location` and `X-Content-Hash` headers, then stream the redirect
    target into `dest_path`. The two-step buys us:
      - early access to `X-Content-Hash` for cross-check before
        `verify_pack` opens the file
      - clean error messages distinguishing "registry says no" (410
        deprecated, 404 missing) from "R2 is unreachable"

    On 410 (deprecated) or 404 (missing), raises RegistryError with the
    HTTP status set so the caller can decide how to react.
    """
    redirect_url = (
        f"{registry_url()}/packs/{urllib.parse.quote(author)}"
        f"/{urllib.parse.quote(name)}/{urllib.parse.quote(version)}/download"
    )
    status, headers, body = _request(redirect_url, follow_redirects=False)

    if status == 410:
        raise RegistryError(
            f"{author}/{name}@{version} is deprecated",
            status=410,
        )
    if status == 404:
        raise RegistryError(
            f"{author}/{name}@{version} not found in registry",
            status=404,
        )
    if status not in (301, 302, 303, 307, 308):
        raise RegistryError(
            f"expected redirect from download endpoint, got HTTP {status} "
            f"(body: {body[:200].decode('utf-8', errors='replace')!r})",
            status=status,
        )

    location = headers.get("location")
    if not location:
        raise RegistryError(
            f"download endpoint returned {status} without a Location header",
            status=status,
        )
    content_hash = headers.get("x-content-hash")

    # Stream the actual blob (unauthenticated, public R2).
    dest_path = Path(dest_path).expanduser()
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    blob_req = urllib.request.Request(location)
    blob_req.add_header("User-Agent", USER_AGENT)
    try:
        with urllib.request.urlopen(blob_req, timeout=_READ_TIMEOUT_S) as resp:
            if resp.status >= 400:
                raise RegistryError(
                    f"R2 blob fetch failed (HTTP {resp.status}) for {location}",
                    status=resp.status,
                )
            with dest_path.open("wb") as f:
                shutil.copyfileobj(resp, f)
    except urllib.error.URLError as e:
        raise RegistryError(f"R2 blob unreachable: {e.reason}") from e

    return DownloadResult(
        path=dest_path,
        size_bytes=dest_path.stat().st_size,
        redirect_url=location,
        content_hash_header=content_hash,
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def parse_pack_ref(ref: str) -> tuple[str, str, str | None]:
    """Parse `<author>/<name>[@<version>]` into a tuple.

    Raises ValueError on malformed input. Version is None when omitted —
    callers default to "latest" via `get_pack_detail`.
    """
    if "/" not in ref:
        raise ValueError(
            f"pack ref must be '<author>/<name>[@<version>]', got: {ref!r}"
        )

    body, sep, version = ref.partition("@")
    author, _, name = body.partition("/")
    if not author or not name:
        raise ValueError(
            f"pack ref must be '<author>/<name>[@<version>]', got: {ref!r}"
        )
    if sep and not version:
        raise ValueError(f"pack ref has empty @version: {ref!r}")
    return author, name, version or None
