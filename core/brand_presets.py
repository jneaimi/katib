"""Save a freshly-rendered cover image as a reusable brand preset.

Writes the resolved image to `<brand-dir>/<brand>-assets/covers/<name>.<ext>`
(relative path stored in the brand YAML) and edits the brand profile in
place using ruamel.yaml to preserve comments and key ordering.

Re-saving the same preset name requires --force; the engine refuses to
silently overwrite an existing preset.
"""
from __future__ import annotations

import re
import shutil
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML

from core.tokens import brand_file_path

_SLOT_ALIASES: dict[str, tuple[str, ...]] = {
    "cover-page": ("background", "image"),
}

_PRESET_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")


class SavePresetError(RuntimeError):
    pass


def find_cover_image(resolved_images: list[dict]) -> dict | None:
    """Pick the first cover-tier image slot with a resolved file path."""
    for item in resolved_images:
        if item.get("tier") != "cover":
            continue
        if not item.get("resolved_path"):
            continue
        expected = _SLOT_ALIASES.get(item.get("component", ""), ())
        if expected and item.get("slot") not in expected:
            continue
        return item
    return None


def save_cover_preset(
    *,
    brand: str,
    preset_name: str,
    cover_image: dict,
    force: bool = False,
) -> Path:
    """Copy the resolved cover to `<brand>-assets/covers/` and update brand.yaml.

    Returns the absolute path of the saved image.
    """
    if not _PRESET_NAME_RE.match(preset_name):
        raise SavePresetError(
            f"preset name {preset_name!r} must match [a-z0-9][a-z0-9_-]*"
        )
    source = cover_image.get("source")
    src_path_str = cover_image.get("resolved_path")
    if not src_path_str:
        raise SavePresetError("no resolved cover image path to save")
    src_path = Path(src_path_str)
    if not src_path.exists():
        raise SavePresetError(f"source image missing on disk: {src_path}")

    brand_yaml = brand_file_path(brand)
    assets_dir = brand_yaml.parent / f"{brand_yaml.stem}-assets" / "covers"
    assets_dir.mkdir(parents=True, exist_ok=True)
    ext = src_path.suffix.lower() or ".png"
    dest_path = assets_dir / f"{preset_name}{ext}"

    yaml_rt = YAML()
    yaml_rt.preserve_quotes = True
    with brand_yaml.open("r", encoding="utf-8") as f:
        doc: Any = yaml_rt.load(f) or {}

    covers = doc.get("covers")
    if covers is None:
        covers = {}
        doc["covers"] = covers
    if preset_name in covers and not force:
        raise SavePresetError(
            f"brand {brand!r} already has cover preset {preset_name!r}. "
            f"Pass --force to overwrite."
        )

    shutil.copyfile(src_path, dest_path)
    rel_path = dest_path.relative_to(brand_yaml.parent).as_posix()
    new_entry: dict[str, Any] = {"source": "user-file", "path": rel_path}
    if cover_image.get("alt"):
        new_entry["alt_text"] = cover_image["alt"]
    covers[preset_name] = new_entry

    with brand_yaml.open("w", encoding="utf-8") as f:
        yaml_rt.dump(doc, f)

    # Gemini-sourced previews live only in the content-addressed cache and
    # should become durable user-file references. Always keep original source
    # hint in the saved entry so future graduations to inline-svg etc. can
    # still happen without guessing.
    if source and source not in ("user-file",):
        # No-op right now — the stored entry is user-file regardless.
        # Reserved for future metadata like `original_source: gemini`.
        pass

    return dest_path
