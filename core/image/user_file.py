"""User-file + URL provider.

Serves two source names from the same implementation:
    user-file  -> local path (e.g. ~/Downloads/photo.png)
    url        -> HTTP/HTTPS URL (downloaded once, cached)

Both resolve to a stable cached file path. Copy-on-reference means a
render succeeds even if the source file is later moved or deleted.
"""
from __future__ import annotations

import hashlib
import shutil
import urllib.parse
import urllib.request
from pathlib import Path

from core.image.base import ProviderError, ResolvedImage


class UserFileProvider:
    name = "user-file"

    def is_available(self) -> tuple[bool, str]:
        return True, ""

    def cache_key(self, spec: dict) -> str:
        source = spec.get("source", "user-file")
        if source == "url":
            blob = f"url:{spec['url']}"
        else:
            path_raw = spec.get("path")
            if not path_raw:
                raise ProviderError("user-file: spec missing 'path'")
            path = Path(path_raw).expanduser().resolve()
            mtime = path.stat().st_mtime if path.exists() else "missing"
            blob = f"file:{path}:{mtime}"
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]

    def resolve(self, spec: dict, cache_dir: Path) -> ResolvedImage:
        source = spec.get("source", "user-file")
        key = self.cache_key(spec)

        if source == "url":
            url = spec["url"]
            parsed_path = urllib.parse.urlparse(url).path
            suffix = Path(parsed_path).suffix or ".png"
            dest = cache_dir / f"{key}{suffix}"
            if not dest.exists():
                cache_dir.mkdir(parents=True, exist_ok=True)
                req = urllib.request.Request(url, headers={"User-Agent": "katib/1.0"})
                with urllib.request.urlopen(req) as r, dest.open("wb") as f:
                    shutil.copyfileobj(r, f)
            return ResolvedImage(
                path=dest.resolve(),
                content_hash=key,
                alt_hint=spec.get("alt_text"),
            )

        src = Path(spec["path"]).expanduser().resolve()
        if not src.exists():
            raise ProviderError(f"user-file: path not found: {src}")
        dest = cache_dir / f"{key}{src.suffix}"
        if not dest.exists() or dest.stat().st_mtime < src.stat().st_mtime:
            cache_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
        return ResolvedImage(
            path=dest.resolve(),
            content_hash=key,
            alt_hint=spec.get("alt_text"),
        )
