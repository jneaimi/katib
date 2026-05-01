"""Pack format core (Phase 4).

A `.katib-pack` is a gzipped tarball containing a `pack.yaml` manifest plus
the contents of one or more shared artifacts (components, recipes, brand
profiles). The manifest is the source of truth for what's inside, who
authored it, and what the host install needs in order to use it.

This module owns:
- the manifest dataclass
- schema-driven validation of manifest dicts
- the deterministic content-hash computation (used for integrity checks)
- I/O helpers for reading and writing `pack.yaml`

Higher-level export/import logic lives in subsequent days. Day 1 ships the
foundation only.
"""
from __future__ import annotations

import gzip
import hashlib
import io
import json
import re
import subprocess
import tarfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

from core.tokens import (
    user_brands_dir,
    user_components_dir,
    user_recipes_dir,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMAS_DIR = REPO_ROOT / "schemas"

# Bundled tiers (skill-shipped content).
COMPONENTS_DIR = REPO_ROOT / "components"
RECIPES_DIR = REPO_ROOT / "recipes"
BRANDS_DIR = REPO_ROOT / "brands"

# User tiers (~/.katib/...).
USER_COMPONENTS_DIR = user_components_dir()
USER_RECIPES_DIR = user_recipes_dir()
USER_BRANDS_DIR = user_brands_dir()

# Default output directory for export. Overridable via --out.
DEFAULT_OUT_DIR = REPO_ROOT / "dist"

PACK_FORMAT_VERSION = 1
"""The pack_format value emitted by this host. Frozen at v1.0.0."""

CONTENT_HASH_PREFIX = "sha256:"

# The manifest filename inside every pack tarball.
MANIFEST_FILENAME = "pack.yaml"

# Map component-tier-singular to tier-dirname (matches core.component_ops).
TIER_DIRS = {"primitive": "primitives", "section": "sections", "cover": "covers"}

# Files we include from a component directory. Anything else (caches,
# editor backups) is excluded.
_COMPONENT_FILE_ALLOWLIST = (
    "component.yaml",
    "README.md",
    "styles.css",
    "en.html",
    "ar.html",
    "bilingual.html",
)
_COMPONENT_FIXTURE_FILE = ("tests", "test-inputs.yaml")

# Brand-asset sibling-dir convention from core.brand_presets:
# `<brand>.yaml` + `<brand>-assets/...`
_BRAND_ASSETS_SUFFIX = "-assets"


# ---------------------------------------------------------------------------
# Manifest dataclass
# ---------------------------------------------------------------------------


@dataclass
class PackManifest:
    """In-memory representation of pack.yaml.

    Mirrors the JSON schema. Optional fields default to None / empty.
    """

    pack_format: int
    name: str
    version: str
    content_hash: str
    contents: dict[str, list[dict]] = field(default_factory=dict)
    requires: dict[str, Any] = field(default_factory=dict)
    author: dict[str, str] | None = None
    license: str | None = None
    description: str | None = None
    tags: list[str] = field(default_factory=list)
    languages: list[str] = field(default_factory=list)
    domain: str | None = None
    marketplace: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Render to a dict suitable for YAML dump.

        Keys with empty/None values are omitted (except for the required
        ones, which are always present even if empty containers).
        """
        d: dict[str, Any] = {
            "pack_format": self.pack_format,
            "name": self.name,
            "version": self.version,
            "content_hash": self.content_hash,
            "contents": self.contents or {},
            "requires": self.requires or {},
        }
        if self.author:
            d["author"] = {k: v for k, v in self.author.items() if v}
        if self.license:
            d["license"] = self.license
        if self.description:
            d["description"] = self.description
        if self.tags:
            d["tags"] = list(self.tags)
        if self.languages:
            d["languages"] = list(self.languages)
        if self.domain:
            d["domain"] = self.domain
        if self.marketplace:
            d["marketplace"] = {k: v for k, v in self.marketplace.items() if v}
        return d


# ---------------------------------------------------------------------------
# Schema validation
# ---------------------------------------------------------------------------


def _load_schema() -> dict:
    return json.loads((SCHEMAS_DIR / "pack.yaml.schema.json").read_text("utf-8"))


_SCHEMA_VALIDATOR: Draft202012Validator | None = None


def _validator() -> Draft202012Validator:
    global _SCHEMA_VALIDATOR
    if _SCHEMA_VALIDATOR is None:
        _SCHEMA_VALIDATOR = Draft202012Validator(_load_schema())
    return _SCHEMA_VALIDATOR


def validate_manifest_dict(d: dict) -> list[str]:
    """Return a list of human-readable schema errors. Empty list = valid.

    Errors are formatted as `<path>: <message>` so callers can print
    them directly. Top-level errors use `(root)`.
    """
    errors: list[str] = []
    for e in sorted(_validator().iter_errors(d), key=lambda e: list(e.path)):
        path = list(e.path) or "(root)"
        errors.append(f"{path}: {e.message}")
    return errors


# ---------------------------------------------------------------------------
# Manifest I/O
# ---------------------------------------------------------------------------


def load_manifest(path: Path) -> PackManifest:
    """Load + schema-validate + hydrate a manifest from disk.

    Raises ValueError on schema violations.
    """
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    errors = validate_manifest_dict(raw)
    if errors:
        joined = "\n  - ".join(errors)
        raise ValueError(f"Invalid pack manifest at {path}:\n  - {joined}")
    return PackManifest(
        pack_format=raw["pack_format"],
        name=raw["name"],
        version=raw["version"],
        content_hash=raw["content_hash"],
        contents=raw.get("contents", {}),
        requires=raw.get("requires", {}),
        author=raw.get("author"),
        license=raw.get("license"),
        description=raw.get("description"),
        tags=raw.get("tags", []),
        languages=raw.get("languages", []),
        domain=raw.get("domain"),
        marketplace=raw.get("marketplace"),
    )


def dump_manifest(m: PackManifest) -> str:
    """Render manifest to a YAML string suitable for embedding in the tar.

    Uses `sort_keys=False` to preserve the canonical key order set by
    `to_dict()`. `default_flow_style=False` keeps it human-readable.
    """
    return yaml.safe_dump(
        m.to_dict(),
        sort_keys=False,
        default_flow_style=False,
        allow_unicode=True,
    )


# ---------------------------------------------------------------------------
# Content hash
# ---------------------------------------------------------------------------


def compute_content_hash(tar_body_bytes: bytes) -> str:
    """SHA-256 of the canonical tar body, prefixed with `sha256:`.

    The "tar body" is a deterministic tarball of the pack contents
    EXCLUDING the `pack.yaml` manifest itself (since the manifest
    contains the hash). This means:

    - Determinism: the same set of files always produces the same hash,
      regardless of when or where the pack is built.
    - Integrity: any tamper to file contents — text, binary, layout —
      flips the hash. Tampering with the manifest does not change the
      hash but is caught by schema validation.

    Use `build_canonical_tar_body(files)` to produce the input bytes.
    """
    h = hashlib.sha256(tar_body_bytes).hexdigest()
    return f"{CONTENT_HASH_PREFIX}{h}"


def build_canonical_tar_body(files: list[tuple[str, bytes]]) -> bytes:
    """Build a deterministic tarball body from `(arcname, data)` pairs.

    Determinism rules:
    - Entries sorted alphabetically by arcname before adding.
    - Every entry's mtime forced to 0 (Unix epoch).
    - Every entry's uid/gid forced to 0; uname/gname empty.
    - Every entry's mode forced to 0644.
    - Tarball is uncompressed (`w:`) — the gzip layer happens at the
      pack file boundary, not the content-hash input. This keeps the
      hash stable across compression-library versions.
    """
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w") as tar:
        for arcname, data in sorted(files, key=lambda x: x[0]):
            info = tarfile.TarInfo(name=arcname)
            info.size = len(data)
            info.mtime = 0
            info.mode = 0o644
            info.uid = 0
            info.gid = 0
            info.uname = ""
            info.gname = ""
            info.type = tarfile.REGTYPE
            tar.addfile(info, io.BytesIO(data))
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Convenience: classify pack name
# ---------------------------------------------------------------------------


def parse_pack_name(name: str) -> tuple[str, str]:
    """Split `<author>/<artifact>` into (author, artifact).

    Caller is responsible for ensuring the name passed schema validation
    first; this helper does not re-validate.
    """
    if "/" not in name:
        raise ValueError(f"Invalid pack name (missing slash): {name!r}")
    author, _, artifact = name.partition("/")
    return author, artifact


# ---------------------------------------------------------------------------
# Author defaulting
# ---------------------------------------------------------------------------


_AUTHOR_SLUG_RE = re.compile(r"[^a-z0-9]+")


def slugify_author(name: str) -> str:
    """Reduce a free-form name to the kebab-case author segment of a pack name.

    Lowercase, alphanum-only, hyphen-separated. Empty result falls back
    to `"unknown"`.
    """
    s = _AUTHOR_SLUG_RE.sub("-", name.lower()).strip("-")
    return s or "unknown"


def detect_git_author() -> dict[str, str]:
    """Read `git config user.name` / `user.email` if available.

    Returns a dict with keys `name` and `email` (each may be missing
    if git is unavailable or the config is unset). Never raises.
    """
    out: dict[str, str] = {}
    for key, field in (("user.name", "name"), ("user.email", "email")):
        try:
            r = subprocess.run(
                ["git", "config", "--get", key],
                capture_output=True,
                text=True,
                timeout=2,
                cwd=REPO_ROOT,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return out
        if r.returncode == 0 and r.stdout.strip():
            out[field] = r.stdout.strip()
    return out


def parse_author_string(s: str) -> dict[str, str]:
    """Parse `Name <email>` (npm-ish) into a dict.

    Either half may be missing. Whitespace-trimmed. Used by the CLI
    --author flag.
    """
    s = s.strip()
    if not s:
        return {}
    m = re.match(r"^\s*(.*?)\s*<\s*(.+?)\s*>\s*$", s)
    if m:
        d: dict[str, str] = {}
        if m.group(1):
            d["name"] = m.group(1)
        if m.group(2):
            d["email"] = m.group(2)
        return d
    # No email — treat the whole string as the name.
    return {"name": s}


# ---------------------------------------------------------------------------
# File collection (export side)
# ---------------------------------------------------------------------------


def _read_bytes(p: Path) -> bytes:
    return p.read_bytes()


def _find_component(name: str) -> tuple[Path, str] | None:
    """Resolve a component name to (dir, tier-singular) or None.

    User tier preferred; bundled tier as fallback. Same precedence as
    `core.component_ops._find_component()`.
    """
    for base in (USER_COMPONENTS_DIR, COMPONENTS_DIR):
        for tier_singular, tier_dirname in TIER_DIRS.items():
            cand = base / tier_dirname / name
            if (cand / "component.yaml").exists():
                return cand, tier_singular
    return None


def _find_recipe(name: str) -> Path | None:
    user = USER_RECIPES_DIR / f"{name}.yaml"
    if user.exists():
        return user
    bundled = RECIPES_DIR / f"{name}.yaml"
    if bundled.exists():
        return bundled
    return None


def _find_brand(name: str) -> Path | None:
    """Resolve a brand name to its YAML path. User tier preferred."""
    for base in (USER_BRANDS_DIR, BRANDS_DIR):
        cand = base / f"{name}.yaml"
        if cand.exists():
            return cand
    return None


def _collect_component_files(cdir: Path, tier: str, name: str) -> list[tuple[str, bytes]]:
    """Return [(arcname, bytes)] for a single component directory.

    Arcnames take the canonical pack form: `components/<tier-plural>/<name>/...`
    """
    tier_dir = TIER_DIRS[tier]
    base_arc = f"components/{tier_dir}/{name}"
    out: list[tuple[str, bytes]] = []
    for fname in _COMPONENT_FILE_ALLOWLIST:
        fpath = cdir / fname
        if fpath.exists():
            out.append((f"{base_arc}/{fname}", _read_bytes(fpath)))
    fixture = cdir / _COMPONENT_FIXTURE_FILE[0] / _COMPONENT_FIXTURE_FILE[1]
    if fixture.exists():
        out.append((f"{base_arc}/tests/test-inputs.yaml", _read_bytes(fixture)))
    return out


def _collect_recipe_files(rpath: Path, name: str) -> list[tuple[str, bytes]]:
    return [(f"recipes/{name}.yaml", _read_bytes(rpath))]


def _collect_brand_files(brand_yaml: Path, name: str) -> list[tuple[str, bytes]]:
    """Pack the brand YAML plus the sibling `<name>-assets/` dir if present.

    The shared `logos/` dir is intentionally NOT bundled — it belongs
    to no single brand.
    """
    out: list[tuple[str, bytes]] = [(f"brands/{name}.yaml", _read_bytes(brand_yaml))]
    assets_dir = brand_yaml.parent / f"{name}{_BRAND_ASSETS_SUFFIX}"
    if assets_dir.exists() and assets_dir.is_dir():
        for f in sorted(assets_dir.rglob("*")):
            if f.is_file():
                rel = f.relative_to(assets_dir)
                out.append((f"brands/{name}-assets/{rel.as_posix()}", _read_bytes(f)))
    return out


# ---------------------------------------------------------------------------
# Pack file writer
# ---------------------------------------------------------------------------


@dataclass
class ExportResult:
    artifact_kind: str           # "component" | "recipe" | "brand"
    artifact_name: str           # the source name on disk (e.g., "eyebrow")
    pack_name: str               # the namespaced name (e.g., "jneaimi/eyebrow")
    version: str                 # the artifact's own version
    pack_path: str               # absolute path to the .katib-pack file
    pack_bytes: int              # size of the .katib-pack on disk
    content_hash: str            # sha256:... of the canonical body
    files_included: list[str]    # arcnames of the contents (excludes pack.yaml)


def _write_pack_file(
    manifest: PackManifest,
    file_pairs: list[tuple[str, bytes]],
    out_dir: Path,
    pack_filename: str,
) -> Path:
    """Compose the final `.katib-pack` file (gzipped tar):

    Layout inside the gz tar:
      pack.yaml          ← manifest
      <file_pairs ...>   ← canonical body, also appears in content_hash input

    The outer file is gzipped via gzip mtime=0 for byte-for-byte
    reproducibility — needed for downstream content-addressing if
    Phase 6 wants to dedup packs by their hash.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    pack_path = out_dir / pack_filename
    manifest_yaml = dump_manifest(manifest).encode("utf-8")

    inner = io.BytesIO()
    with tarfile.open(fileobj=inner, mode="w") as tar:
        # Manifest first.
        info = tarfile.TarInfo(name=MANIFEST_FILENAME)
        info.size = len(manifest_yaml)
        info.mtime = 0
        info.mode = 0o644
        info.uid = 0
        info.gid = 0
        info.type = tarfile.REGTYPE
        tar.addfile(info, io.BytesIO(manifest_yaml))
        # Then the canonical body, sorted alphabetically.
        for arcname, data in sorted(file_pairs, key=lambda x: x[0]):
            info = tarfile.TarInfo(name=arcname)
            info.size = len(data)
            info.mtime = 0
            info.mode = 0o644
            info.uid = 0
            info.gid = 0
            info.type = tarfile.REGTYPE
            tar.addfile(info, io.BytesIO(data))

    raw_tar = inner.getvalue()
    # gzip with explicit mtime=0 → reproducible outer file.
    with open(pack_path, "wb") as f:
        with gzip.GzipFile(fileobj=f, mode="wb", mtime=0) as gz:
            gz.write(raw_tar)
    return pack_path


# ---------------------------------------------------------------------------
# Export — single artifact
# ---------------------------------------------------------------------------


def _resolve_default_author() -> dict[str, str]:
    """Author defaulting: git config first, then unknown."""
    git = detect_git_author()
    if git.get("name"):
        return git
    return {"name": "Unknown"}


def _make_pack_name(author_slug: str, artifact: str) -> str:
    return f"{author_slug}/{artifact}"


def _read_yaml(p: Path) -> dict:
    return yaml.safe_load(p.read_text(encoding="utf-8")) or {}


def _component_metadata(cdir: Path) -> dict:
    return _read_yaml(cdir / "component.yaml")


def _recipe_metadata(rpath: Path) -> dict:
    return _read_yaml(rpath)


def _brand_metadata(bpath: Path) -> dict:
    return _read_yaml(bpath)


def _infer_domain(artifact_name: str) -> str | None:
    # Recipe filenames follow `<domain>-<rest>` (legal-nda, financial-invoice).
    # Single-word names (tutorial) have no implicit domain.
    head, sep, _ = artifact_name.partition("-")
    return head if sep and head else None


def export_component(
    name: str,
    *,
    author: dict[str, str] | None = None,
    out_dir: Path | None = None,
    with_previews: bool = False,
) -> ExportResult:
    """Pack a single component into a `.katib-pack` file.

    Resolves the component in user tier first, then bundled. The
    resulting pack contains everything in the component dir that
    Katib renders from (HTML variants, CSS, README, fixture).

    When `with_previews=True`, a one-section wrapper recipe is
    synthesized around the component and rasterized to PNG via the
    same pipeline as recipe previews — gives the marketplace a
    "what does this look like in a document" sample without ever
    rendering author-specific content.
    """
    found = _find_component(name)
    if found is None:
        raise ValueError(
            f"Component {name!r} not found under {USER_COMPONENTS_DIR} or {COMPONENTS_DIR}"
        )
    cdir, tier = found
    meta = _component_metadata(cdir)
    version = meta.get("version", "0.0.0")
    description = meta.get("description")
    languages = list(meta.get("languages") or [])

    file_pairs = _collect_component_files(cdir, tier, name)

    marketplace: dict[str, Any] | None = None
    if with_previews:
        # Lazy import — pulls WeasyPrint + pypdfium2 transitively.
        from core.previews import render_component_previews

        preview_entries = render_component_previews(meta)
        if preview_entries:
            for entry in preview_entries:
                file_pairs.append((entry.arcname, entry.body))
            marketplace = {
                "previews": [e.manifest_entry for e in preview_entries]
            }

    body = build_canonical_tar_body(file_pairs)
    content_hash = compute_content_hash(body)

    author_dict = author or _resolve_default_author()
    pack_name = _make_pack_name(slugify_author(author_dict.get("name", "unknown")), name)

    tags: list[str] = sorted({t for t in (tier, *languages) if t})

    manifest = PackManifest(
        pack_format=PACK_FORMAT_VERSION,
        name=pack_name,
        version=version,
        content_hash=content_hash,
        contents={"components": [{"name": name, "tier": tier, "version": version}]},
        requires={},
        author=author_dict or None,
        description=description,
        tags=tags,
        languages=sorted(languages),
        marketplace=marketplace,
    )

    out_dir = out_dir or DEFAULT_OUT_DIR
    pack_filename = f"{name}-{version}.katib-pack"
    pack_path = _write_pack_file(manifest, file_pairs, out_dir, pack_filename)

    return ExportResult(
        artifact_kind="component",
        artifact_name=name,
        pack_name=pack_name,
        version=version,
        pack_path=str(pack_path),
        pack_bytes=pack_path.stat().st_size,
        content_hash=content_hash,
        files_included=[arc for arc, _ in file_pairs],
    )


def export_recipe(
    name: str,
    *,
    author: dict[str, str] | None = None,
    out_dir: Path | None = None,
    with_previews: bool = False,
) -> ExportResult:
    """Pack a single recipe YAML into a `.katib-pack` file.

    The recipe's component dependencies are NOT walked here — that's
    the `--bundle` flag. A standalone recipe pack is only useful
    if every section references a bundled component.

    When `with_previews=True`, the captured HTML for each declared
    language is rendered via core.compose, inlined to be self-contained,
    and stamped into the pack under `previews/<name>.<lang>.html` plus
    a `marketplace.previews` block in the manifest. Slice B feature.
    """
    rpath = _find_recipe(name)
    if rpath is None:
        raise ValueError(
            f"Recipe {name!r} not found under {USER_RECIPES_DIR} or {RECIPES_DIR}"
        )
    meta = _recipe_metadata(rpath)
    version = str(meta.get("version", "0.0.0"))
    description = meta.get("description")
    languages = list(meta.get("languages") or [])

    file_pairs = _collect_recipe_files(rpath, name)

    marketplace: dict[str, Any] | None = None
    if with_previews:
        # Lazy import — pulls in WeasyPrint/Jinja transitively. The
        # default --no-previews export path stays cheap.
        from core.previews import render_recipe_previews

        preview_entries = render_recipe_previews(meta)
        if preview_entries:
            for entry in preview_entries:
                file_pairs.append((entry.arcname, entry.body))
            marketplace = {
                "previews": [e.manifest_entry for e in preview_entries]
            }

    body = build_canonical_tar_body(file_pairs)
    content_hash = compute_content_hash(body)

    author_dict = author or _resolve_default_author()
    pack_name = _make_pack_name(slugify_author(author_dict.get("name", "unknown")), name)

    tags = sorted({t for t in ("recipe", *languages) if t})

    manifest = PackManifest(
        pack_format=PACK_FORMAT_VERSION,
        name=pack_name,
        version=version,
        content_hash=content_hash,
        contents={"recipes": [{"name": name, "version": version}]},
        requires={},
        author=author_dict or None,
        description=description,
        tags=tags,
        languages=sorted(languages),
        domain=_infer_domain(name),
        marketplace=marketplace,
    )

    out_dir = out_dir or DEFAULT_OUT_DIR
    pack_filename = f"{name}-{version}.katib-pack"
    pack_path = _write_pack_file(manifest, file_pairs, out_dir, pack_filename)

    return ExportResult(
        artifact_kind="recipe",
        artifact_name=name,
        pack_name=pack_name,
        version=version,
        pack_path=str(pack_path),
        pack_bytes=pack_path.stat().st_size,
        content_hash=content_hash,
        files_included=[arc for arc, _ in file_pairs],
    )


def _recipe_component_refs(recipe_name: str) -> list[str]:
    """Return the de-duplicated list of component names referenced in a
    recipe's section list, in first-seen order.

    Order is preserved so the bundle's `contents.components[]` and
    `requires.bundled_components[]` arrays read top-to-bottom in the
    same order they appear in the recipe — easier to debug.
    """
    rpath = _find_recipe(recipe_name)
    if rpath is None:
        raise ValueError(
            f"Recipe {recipe_name!r} not found under {USER_RECIPES_DIR} or {RECIPES_DIR}"
        )
    data = _read_yaml(rpath)
    seen: dict[str, None] = {}
    sections = data.get("sections") or []
    for idx, section in enumerate(sections):
        comp = (section or {}).get("component")
        if not comp:
            raise ValueError(
                f"Recipe {recipe_name!r} section #{idx} has no `component:` field"
            )
        seen.setdefault(comp, None)
    return list(seen.keys())


def _classify_component(name: str) -> str | None:
    """Return where a component lives: 'user', 'bundled', or None.

    User-tier wins when both exist (matches the runtime resolver).
    """
    for tier_dirname in TIER_DIRS.values():
        if (USER_COMPONENTS_DIR / tier_dirname / name / "component.yaml").exists():
            return "user"
    for tier_dirname in TIER_DIRS.values():
        if (COMPONENTS_DIR / tier_dirname / name / "component.yaml").exists():
            return "bundled"
    return None


def export_bundle(
    recipe_name: str,
    *,
    include_brand: str | None = None,
    author: dict[str, str] | None = None,
    out_dir: Path | None = None,
    with_previews: bool = False,
) -> ExportResult:
    """Pack a recipe + its user-tier component dependencies into one pack.

    Walk:
    1. Read the recipe's section list.
    2. For each `section.component` ref, classify as user-tier or bundled.
    3. User-tier components are included in the pack body.
    4. Bundled components are listed in `requires.bundled_components[]`.
    5. If `include_brand=<name>` is set, the brand YAML + sibling
       `<name>-assets/` dir are also included; bundled brands are
       declared in `requires.bundled_brands[]` (consistent with
       components — explicit, not silent).

    When `with_previews=True`, the recipe's HTML previews per declared
    language are rendered, inlined to be self-contained, and stamped
    into the pack under `previews/<name>.<lang>.html` plus a
    `marketplace.previews` block in the manifest. Mirrors the recipe
    export's Slice B feature so bundle exports don't lose their
    marketplace cards just because they ship their component deps.

    Refuses (with clear error) if any referenced component cannot be
    resolved in either tier.
    """
    rpath = _find_recipe(recipe_name)
    if rpath is None:
        raise ValueError(
            f"Recipe {recipe_name!r} not found under {USER_RECIPES_DIR} or {RECIPES_DIR}"
        )
    recipe_meta = _recipe_metadata(rpath)
    version = str(recipe_meta.get("version", "0.0.0"))
    description = recipe_meta.get("description")
    languages = list(recipe_meta.get("languages") or [])

    refs = _recipe_component_refs(recipe_name)
    user_components: list[tuple[str, str]] = []   # (name, tier)
    bundled_components: list[str] = []
    missing: list[str] = []
    for ref in refs:
        cls = _classify_component(ref)
        if cls == "user":
            found = _find_component(ref)
            assert found is not None  # _classify said user, but be defensive
            user_components.append((ref, found[1]))
        elif cls == "bundled":
            bundled_components.append(ref)
        else:
            missing.append(ref)
    if missing:
        raise ValueError(
            f"Recipe {recipe_name!r} references unresolvable component(s): "
            + ", ".join(repr(m) for m in missing)
        )

    file_pairs: list[tuple[str, bytes]] = []
    file_pairs.extend(_collect_recipe_files(rpath, recipe_name))
    for name, tier in user_components:
        cdir, _ = _find_component(name)
        file_pairs.extend(_collect_component_files(cdir, tier, name))

    # Brand handling: explicit-only.
    bundled_brands: list[str] = []
    if include_brand:
        bpath = _find_brand(include_brand)
        if bpath is None:
            raise ValueError(
                f"Brand {include_brand!r} not found under {USER_BRANDS_DIR} or {BRANDS_DIR}"
            )
        # Classify: if it lives under USER_BRANDS_DIR, include in pack;
        # otherwise (bundled) declare it as a bundled requirement.
        try:
            bpath.relative_to(USER_BRANDS_DIR)
            file_pairs.extend(_collect_brand_files(bpath, include_brand))
            included_brands = [include_brand]
        except ValueError:
            bundled_brands.append(include_brand)
            included_brands = []
    else:
        included_brands = []

    marketplace: dict[str, Any] | None = None
    if with_previews:
        # Lazy import — pulls in WeasyPrint/Jinja transitively. The
        # default --no-previews export path stays cheap. Mirrors
        # export_recipe's Slice B preview block exactly.
        from core.previews import render_recipe_previews

        preview_entries = render_recipe_previews(recipe_meta)
        if preview_entries:
            for entry in preview_entries:
                file_pairs.append((entry.arcname, entry.body))
            marketplace = {
                "previews": [e.manifest_entry for e in preview_entries]
            }

    body = build_canonical_tar_body(file_pairs)
    content_hash = compute_content_hash(body)

    author_dict = author or _resolve_default_author()
    pack_name = _make_pack_name(slugify_author(author_dict.get("name", "unknown")), recipe_name)

    contents: dict[str, list[dict]] = {
        "recipes": [{"name": recipe_name, "version": version}],
    }
    if user_components:
        contents["components"] = [
            {"name": n, "tier": t} for n, t in user_components
        ]
    if included_brands:
        contents["brands"] = [{"name": b} for b in included_brands]

    requires: dict[str, Any] = {}
    if bundled_components:
        requires["bundled_components"] = bundled_components
    if bundled_brands:
        requires["bundled_brands"] = bundled_brands

    # `kind` carries the semantic ("bundle" vs "recipe"); duplicating it
    # in `tags` only pollutes keyword search. Drop it from tags.
    tags = sorted({*languages})

    manifest = PackManifest(
        pack_format=PACK_FORMAT_VERSION,
        name=pack_name,
        version=version,
        content_hash=content_hash,
        contents=contents,
        requires=requires,
        author=author_dict or None,
        description=description,
        tags=tags,
        languages=sorted(languages),
        domain=_infer_domain(recipe_name),
        marketplace=marketplace,
    )

    out_dir = out_dir or DEFAULT_OUT_DIR
    pack_filename = f"{recipe_name}-{version}.katib-pack"
    pack_path = _write_pack_file(manifest, file_pairs, out_dir, pack_filename)

    return ExportResult(
        artifact_kind="bundle",
        artifact_name=recipe_name,
        pack_name=pack_name,
        version=version,
        pack_path=str(pack_path),
        pack_bytes=pack_path.stat().st_size,
        content_hash=content_hash,
        files_included=[arc for arc, _ in file_pairs],
    )


def _open_pack(pack_path: Path) -> dict[str, bytes]:
    """Read a `.katib-pack` and return {arcname: bytes} for every entry.

    Raises ValueError on malformed input (not a gzipped tar, missing
    `pack.yaml`, etc.). Public callers (inspect, verify, import) use
    this once at the start.
    """
    if not pack_path.exists():
        raise ValueError(f"Pack not found: {pack_path}")
    try:
        with open(pack_path, "rb") as f:
            with gzip.GzipFile(fileobj=f) as gz:
                inner = gz.read()
    except (OSError, EOFError, gzip.BadGzipFile) as e:
        raise ValueError(f"Pack is not a valid gzipped tar: {e}")
    try:
        with tarfile.open(fileobj=io.BytesIO(inner), mode="r") as tar:
            entries = {info.name: tar.extractfile(info).read() for info in tar.getmembers() if info.isfile()}
    except (tarfile.TarError, ValueError) as e:
        raise ValueError(f"Pack tar is malformed: {e}")
    if MANIFEST_FILENAME not in entries:
        raise ValueError(f"Pack is missing {MANIFEST_FILENAME!r}")
    return entries


def _pack_format_supported(n: int) -> bool:
    """Phase-4 hosts support pack_format=1 only. Future bumps require
    matching host-side support."""
    return n == PACK_FORMAT_VERSION


# ---------------------------------------------------------------------------
# Inspect
# ---------------------------------------------------------------------------


@dataclass
class PackInspectResult:
    pack_path: str
    pack_bytes: int
    name: str
    version: str
    pack_format: int
    content_hash_claim: str
    contents: dict[str, list[dict]]
    requires: dict[str, Any]
    author: dict[str, str] | None
    license: str | None
    description: str | None
    tags: list[str]
    files: list[str]


def inspect_pack(pack_path: Path) -> PackInspectResult:
    """Read manifest + list arcnames. No schema validation; no hash
    recomputation. Use `verify_pack()` for the safety-checked variant.

    Raises ValueError if the pack can't be opened or `pack.yaml` is
    not parseable as YAML. Schema violations don't block inspection
    (a corrupt pack should still tell you what's wrong with it).
    """
    entries = _open_pack(pack_path)
    try:
        manifest_dict = yaml.safe_load(entries[MANIFEST_FILENAME].decode("utf-8")) or {}
    except yaml.YAMLError as e:
        raise ValueError(f"Pack manifest is not valid YAML: {e}")

    files = sorted(k for k in entries.keys() if k != MANIFEST_FILENAME)

    return PackInspectResult(
        pack_path=str(pack_path),
        pack_bytes=pack_path.stat().st_size,
        name=manifest_dict.get("name", "(unknown)"),
        version=str(manifest_dict.get("version", "0.0.0")),
        pack_format=int(manifest_dict.get("pack_format", 0)),
        content_hash_claim=str(manifest_dict.get("content_hash", "")),
        contents=manifest_dict.get("contents") or {},
        requires=manifest_dict.get("requires") or {},
        author=manifest_dict.get("author"),
        license=manifest_dict.get("license"),
        description=manifest_dict.get("description"),
        tags=list(manifest_dict.get("tags") or []),
        files=files,
    )


# ---------------------------------------------------------------------------
# Verify
# ---------------------------------------------------------------------------


@dataclass
class PackVerifyResult:
    pack_path: str
    pack_name: str
    pack_format_supported: bool
    schema_errors: list[str]
    hash_match: bool
    component_issues: dict[str, list[dict]]
    recipe_issues: dict[str, list[dict]]

    @property
    def ok(self) -> bool:
        return (
            self.pack_format_supported
            and not self.schema_errors
            and self.hash_match
            and not any(self.component_issues.values())
            and not any(self.recipe_issues.values())
        )


def _validate_pack_components_in_tmpdir(
    entries: dict[str, bytes],
    component_specs: list[dict],
    recipe_specs: list[dict],
) -> tuple[dict[str, list[dict]], dict[str, list[dict]]]:
    """Extract pack contents into a tmp dir, redirect user-tier
    constants, run component + recipe validators, restore.

    Returns (component_issues, recipe_issues).

    Errors-only (warnings are not surfaced from verify; that's a
    deliberate choice — verify is a CI gate, warnings are informational).
    """
    import tempfile

    from core import component_ops, recipe_ops
    import scripts.build as build_mod

    component_issues: dict[str, list[dict]] = {}
    recipe_issues: dict[str, list[dict]] = {}

    with tempfile.TemporaryDirectory(prefix="katib-pack-verify-") as tmp:
        tmp_root = Path(tmp)
        comp_root = tmp_root / "components"
        recipe_root = tmp_root / "recipes"
        memory_root = tmp_root / "memory"
        for d in (comp_root, recipe_root, memory_root):
            d.mkdir(parents=True, exist_ok=True)

        # Extract every entry to its arcname under tmp_root.
        for arc, data in entries.items():
            if arc == MANIFEST_FILENAME:
                continue
            target = tmp_root / arc
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)

        # Audit bootstrap: append entries for each packed component +
        # recipe so the validators don't refuse them as orphans.
        # (validate_full doesn't actually consult the audit — the
        # build-time gate does — but recipe validation may; safer to
        # write them.)
        comp_audit = memory_root / "component-audit.jsonl"
        recipe_audit = memory_root / "recipe-audit.jsonl"
        with comp_audit.open("a") as f:
            for spec in component_specs:
                f.write(
                    json.dumps(
                        {"name": spec["name"], "tier": spec["tier"], "action": "audit-bootstrap"}
                    )
                    + "\n"
                )
        with recipe_audit.open("a") as f:
            for spec in recipe_specs:
                f.write(
                    json.dumps({"name": spec["name"], "action": "audit-bootstrap"}) + "\n"
                )

        # Capture originals
        orig = {
            "component_ops_USER": component_ops.USER_COMPONENTS_DIR,
            "component_ops_AUDIT": component_ops.AUDIT_FILE,
            "component_ops_REQUESTS": component_ops.REQUESTS_FILE,
            "component_ops_MEMORY": component_ops.MEMORY_DIR,
            "recipe_ops_USER_RECIPES": recipe_ops.USER_RECIPES_DIR,
            "recipe_ops_USER_COMPONENTS": recipe_ops.USER_COMPONENTS_DIR,
            "recipe_ops_AUDIT": recipe_ops.AUDIT_FILE,
            "recipe_ops_REQUESTS": recipe_ops.REQUESTS_FILE,
            "recipe_ops_MEMORY": recipe_ops.MEMORY_DIR,
            "build_AUDIT": build_mod.AUDIT_FILE,
            "build_RECIPE_AUDIT": build_mod.RECIPE_AUDIT_FILE,
        }
        try:
            component_ops.USER_COMPONENTS_DIR = comp_root
            component_ops.MEMORY_DIR = memory_root
            component_ops.AUDIT_FILE = comp_audit
            component_ops.REQUESTS_FILE = memory_root / "component-requests.jsonl"
            recipe_ops.USER_RECIPES_DIR = recipe_root
            recipe_ops.USER_COMPONENTS_DIR = comp_root
            recipe_ops.MEMORY_DIR = memory_root
            recipe_ops.AUDIT_FILE = recipe_audit
            recipe_ops.REQUESTS_FILE = memory_root / "recipe-requests.jsonl"
            build_mod.AUDIT_FILE = comp_audit
            build_mod.RECIPE_AUDIT_FILE = recipe_audit

            for spec in component_specs:
                name = spec["name"]
                try:
                    res = component_ops.validate_full(name)
                except ValueError as e:
                    component_issues[name] = [
                        {"severity": "error", "category": "resolve", "message": str(e)}
                    ]
                    continue
                errors = [i.as_dict() for i in res.errors]
                if errors:
                    component_issues[name] = errors

            for spec in recipe_specs:
                name = spec["name"]
                try:
                    res = recipe_ops.validate_recipe_full(name)
                except ValueError as e:
                    recipe_issues[name] = [
                        {"severity": "error", "category": "resolve", "message": str(e)}
                    ]
                    continue
                errors = [i.as_dict() for i in res.errors]
                if errors:
                    recipe_issues[name] = errors
        finally:
            component_ops.USER_COMPONENTS_DIR = orig["component_ops_USER"]
            component_ops.MEMORY_DIR = orig["component_ops_MEMORY"]
            component_ops.AUDIT_FILE = orig["component_ops_AUDIT"]
            component_ops.REQUESTS_FILE = orig["component_ops_REQUESTS"]
            recipe_ops.USER_RECIPES_DIR = orig["recipe_ops_USER_RECIPES"]
            recipe_ops.USER_COMPONENTS_DIR = orig["recipe_ops_USER_COMPONENTS"]
            recipe_ops.MEMORY_DIR = orig["recipe_ops_MEMORY"]
            recipe_ops.AUDIT_FILE = orig["recipe_ops_AUDIT"]
            recipe_ops.REQUESTS_FILE = orig["recipe_ops_REQUESTS"]
            build_mod.AUDIT_FILE = orig["build_AUDIT"]
            build_mod.RECIPE_AUDIT_FILE = orig["build_RECIPE_AUDIT"]

    return component_issues, recipe_issues


def verify_pack(pack_path: Path) -> PackVerifyResult:
    """CI-grade safety check.

    Runs (in order; each step gates the next):
    1. Open the pack (gzip + tar parseable, manifest present).
    2. Schema-validate `pack.yaml`.
    3. Re-compute content_hash from the canonical body; compare to claim.
    4. Refuse if `pack_format` is unsupported.
    5. Extract to a tmp dir; run `validate_full()` on each component
       and `validate_recipe_full()` on each recipe; collect errors.

    Steps 2 + 3 + 4 short-circuit subsequent steps (validators won't
    run on a structurally broken pack). Step 5 always runs if 1–4 pass
    so the operator gets the full picture in one go.
    """
    entries = _open_pack(pack_path)
    manifest_bytes = entries[MANIFEST_FILENAME]
    try:
        manifest_dict = yaml.safe_load(manifest_bytes.decode("utf-8")) or {}
    except yaml.YAMLError as e:
        return PackVerifyResult(
            pack_path=str(pack_path),
            pack_name="(unparseable)",
            pack_format_supported=False,
            schema_errors=[f"manifest YAML parse error: {e}"],
            hash_match=False,
            component_issues={},
            recipe_issues={},
        )

    schema_errors = validate_manifest_dict(manifest_dict)
    pack_name = manifest_dict.get("name", "(unknown)")
    pf = manifest_dict.get("pack_format", 0)
    pack_format_supported = isinstance(pf, int) and _pack_format_supported(pf)

    if schema_errors or not pack_format_supported:
        return PackVerifyResult(
            pack_path=str(pack_path),
            pack_name=pack_name,
            pack_format_supported=pack_format_supported,
            schema_errors=schema_errors,
            hash_match=False,
            component_issues={},
            recipe_issues={},
        )

    # 3. Hash recompute
    body_pairs = [(k, v) for k, v in entries.items() if k != MANIFEST_FILENAME]
    recomputed = compute_content_hash(build_canonical_tar_body(body_pairs))
    claimed = str(manifest_dict.get("content_hash", ""))
    hash_match = recomputed == claimed

    if not hash_match:
        return PackVerifyResult(
            pack_path=str(pack_path),
            pack_name=pack_name,
            pack_format_supported=True,
            schema_errors=[],
            hash_match=False,
            component_issues={},
            recipe_issues={},
        )

    # 5. Per-artifact validation
    contents = manifest_dict.get("contents") or {}
    component_specs = contents.get("components") or []
    recipe_specs = contents.get("recipes") or []
    component_issues, recipe_issues = _validate_pack_components_in_tmpdir(
        entries, component_specs, recipe_specs
    )

    return PackVerifyResult(
        pack_path=str(pack_path),
        pack_name=pack_name,
        pack_format_supported=True,
        schema_errors=[],
        hash_match=True,
        component_issues=component_issues,
        recipe_issues=recipe_issues,
    )


# ---------------------------------------------------------------------------
# Import
# ---------------------------------------------------------------------------


@dataclass
class ImportResult:
    pack_path: str
    pack_name: str
    pack_version: str
    files_written: list[str]            # in dry-run, this is "would-write"
    audit_entries_added: int
    capabilities_regenerated: bool
    force: bool
    justification: str | None
    collisions_resolved: list[str]      # arcnames overwritten under --force
    dry_run: bool = False               # True → no disk changes were made


_HOST_VERSION_CACHE: str | None = None


def _host_katib_version() -> str:
    """Read the host's installed Katib version from `package.json`.

    Cached for the process. The PEP-440-incompatible npm-style
    `1.0.0-alpha.2` is normalized via `packaging.version.Version`
    on comparison, so callers don't need to pre-process.
    """
    global _HOST_VERSION_CACHE
    if _HOST_VERSION_CACHE is None:
        pkg = json.loads((REPO_ROOT / "package.json").read_text(encoding="utf-8"))
        _HOST_VERSION_CACHE = pkg.get("version", "0.0.0")
    return _HOST_VERSION_CACHE


def _bundled_component_exists(name: str) -> bool:
    """True if a component by that name lives in the bundled tier
    (any of the three tier dirs)."""
    for tier_dirname in TIER_DIRS.values():
        if (COMPONENTS_DIR / tier_dirname / name / "component.yaml").exists():
            return True
    return False


def _bundled_brand_exists(name: str) -> bool:
    return (BRANDS_DIR / f"{name}.yaml").exists()


def _check_bundled_deps(manifest: dict) -> list[str]:
    """Return a list of human-readable error strings for missing
    bundled dependencies. Empty list = all deps satisfied.

    Three classes of dep:
    - `requires.bundled_components[]` — must exist on the host
    - `requires.bundled_brands[]` — must exist on the host
    - `requires.katib_min` — host's package.json version must be ≥ min
    """
    from packaging.version import InvalidVersion, Version

    errors: list[str] = []
    requires = manifest.get("requires") or {}

    missing_components = [
        n for n in (requires.get("bundled_components") or []) if not _bundled_component_exists(n)
    ]
    if missing_components:
        errors.append(
            "missing bundled component(s): "
            + ", ".join(repr(n) for n in missing_components)
            + ". Update Katib to a version that ships them."
        )

    missing_brands = [
        n for n in (requires.get("bundled_brands") or []) if not _bundled_brand_exists(n)
    ]
    if missing_brands:
        errors.append(
            "missing bundled brand(s): " + ", ".join(repr(n) for n in missing_brands)
        )

    katib_min = requires.get("katib_min")
    if katib_min:
        host = _host_katib_version()
        try:
            if Version(host) < Version(katib_min):
                errors.append(
                    f"host Katib version {host!r} is older than required minimum {katib_min!r}. "
                    f"Update Katib to {katib_min} or later."
                )
        except InvalidVersion as e:
            errors.append(f"could not compare versions ({host!r} vs {katib_min!r}): {e}")

    return errors


def _user_target_for_arcname(arc: str) -> Path | None:
    """Map an arcname inside a pack to its user-tier filesystem target.

    Returns None for arcnames that don't belong in the user tier
    (e.g., the manifest itself).
    """
    if arc == MANIFEST_FILENAME:
        return None
    if arc.startswith("components/"):
        # components/<tier-dir>/<name>/<rel>...
        return USER_COMPONENTS_DIR / Path(*Path(arc).parts[1:])
    if arc.startswith("recipes/"):
        return USER_RECIPES_DIR / Path(*Path(arc).parts[1:])
    if arc.startswith("brands/"):
        return USER_BRANDS_DIR / Path(*Path(arc).parts[1:])
    if arc.startswith("previews/"):
        # Slice B HTML previews — published to R2 by the marketplace
        # CI, not extracted into the user tier. Importing the pack
        # locally should silently skip them.
        return None
    raise ValueError(f"Unrecognized arcname prefix: {arc!r}")


def _now_iso() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _regenerate_capabilities() -> bool:
    """Run scripts/generate_capabilities.py via subprocess. Returns
    True on success. Never raises — capabilities regen is best-effort
    (route.py also has staleness detection that heals)."""
    try:
        r = subprocess.run(
            ["uv", "run", "python", "scripts/generate_capabilities.py"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=60,
        )
        return r.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def _user_tier_audit_paths() -> tuple[Path, Path]:
    """Return (component_audit_path, recipe_audit_path) under the
    user-tier memory dir.

    Reads via core.tokens.user_memory_dir() so the env var redirects
    used by tests (KATIB_MEMORY_DIR) are honored at call time.
    """
    from core.tokens import user_memory_dir as _umd

    mem = _umd()
    mem.mkdir(parents=True, exist_ok=True)
    return mem / "component-audit.jsonl", mem / "recipe-audit.jsonl"


def import_pack(
    pack_path: Path,
    *,
    force: bool = False,
    justification: str | None = None,
    regenerate_capabilities: bool = True,
    dry_run: bool = False,
) -> ImportResult:
    """Install a `.katib-pack` into the user tier with audit-gate equivalence.

    Order of operations (each step gates the next):
    1. `verify_pack()` — refuse if the pack isn't structurally sound
       and per-artifact-valid.
    2. Bundled-dep check — refuse if `requires.bundled_components`,
       `requires.bundled_brands`, or `requires.katib_min` are not
       satisfied by the host.
    3. Map every body arcname to its user-tier target path.
    4. Collision check — if any target exists and `--force` is not
       set, refuse with a list of collisions.
    5. If `--force` but no `--justification`, refuse (audit-gate equivalence).
    6. (skipped under `dry_run=True`) Write each file (creating parent dirs).
    7. (skipped under `dry_run=True`) Append audit entries for every
       imported component + recipe.
    8. (skipped under `dry_run=True`) Trigger capabilities regen.

    `dry_run=True` runs every check and returns the plan without
    touching disk. Useful for CI ("is this pack still good after
    we updated katib?") and for human pre-flight.
    """
    pack_path = Path(pack_path).expanduser().resolve()
    verify = verify_pack(pack_path)
    if not verify.ok:
        # Surface a single readable line.
        problems = []
        if not verify.pack_format_supported:
            problems.append("unsupported pack_format")
        if verify.schema_errors:
            problems.append(f"{len(verify.schema_errors)} schema error(s)")
        if not verify.hash_match:
            problems.append("content_hash mismatch")
        if any(verify.component_issues.values()):
            problems.append(
                f"{sum(len(v) for v in verify.component_issues.values())} component error(s)"
            )
        if any(verify.recipe_issues.values()):
            problems.append(
                f"{sum(len(v) for v in verify.recipe_issues.values())} recipe error(s)"
            )
        raise ValueError(
            f"Pack failed verification: {'; '.join(problems)}. "
            f"Run `katib pack verify {pack_path}` for details."
        )

    entries = _open_pack(pack_path)
    manifest_dict = yaml.safe_load(entries[MANIFEST_FILENAME].decode("utf-8")) or {}

    # Bundled-dep check
    dep_errors = _check_bundled_deps(manifest_dict)
    if dep_errors:
        raise ValueError(
            "Pack cannot be imported on this host:\n  - " + "\n  - ".join(dep_errors)
        )

    # Plan + collision check
    plan: list[tuple[str, Path]] = []   # (arcname, target_path)
    collisions: list[str] = []
    for arc in entries:
        target = _user_target_for_arcname(arc)
        if target is None:
            continue
        plan.append((arc, target))
        if target.exists():
            collisions.append(arc)

    if collisions and not force:
        joined = "\n  - ".join(collisions[:10])
        more = f"\n  ...and {len(collisions) - 10} more" if len(collisions) > 10 else ""
        raise ValueError(
            f"Import would overwrite {len(collisions)} existing path(s) under user tier:\n"
            f"  - {joined}{more}\n"
            f"Use --force --justification '<reason>' to overwrite."
        )
    if force and collisions and not justification:
        raise ValueError(
            "--force requires --justification '<reason>' (audited)"
        )

    # Pre-extract metadata used by both write + audit (needed even under dry_run)
    pack_name = str(manifest_dict.get("name", "(unknown)"))
    pack_version = str(manifest_dict.get("version", "0.0.0"))
    content_hash = str(manifest_dict.get("content_hash", ""))
    contents = manifest_dict.get("contents") or {}
    component_specs = contents.get("components") or []
    recipe_specs = contents.get("recipes") or []

    if dry_run:
        # Plan-only return — nothing on disk changes.
        return ImportResult(
            pack_path=str(pack_path),
            pack_name=pack_name,
            pack_version=pack_version,
            files_written=[arc for arc, _ in plan],   # what *would* be written
            audit_entries_added=len(component_specs) + len(recipe_specs),
            capabilities_regenerated=False,
            force=force,
            justification=justification,
            collisions_resolved=collisions if force else [],
            dry_run=True,
        )

    # Write
    files_written: list[str] = []
    for arc, target in plan:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(entries[arc])
        files_written.append(arc)

    # Audit (pack_name / version / content_hash / specs already pulled above)
    comp_audit_path, recipe_audit_path = _user_tier_audit_paths()
    audit_count = 0
    base_meta = {
        "action": "imported",
        "source_pack": pack_name,
        "source_pack_version": pack_version,
        "source_hash": content_hash,
        "at": _now_iso(),
    }
    if force:
        base_meta["force"] = True
    if justification:
        base_meta["justification"] = justification

    if component_specs:
        with comp_audit_path.open("a", encoding="utf-8") as f:
            for spec in component_specs:
                row = {
                    "component": spec["name"],
                    "tier": spec.get("tier"),
                    "namespace": "user",
                    **base_meta,
                }
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
                audit_count += 1

    if recipe_specs:
        with recipe_audit_path.open("a", encoding="utf-8") as f:
            for spec in recipe_specs:
                row = {
                    "recipe": spec["name"],
                    "namespace": "user",
                    **base_meta,
                }
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
                audit_count += 1

    caps_ok = False
    if regenerate_capabilities:
        caps_ok = _regenerate_capabilities()

    return ImportResult(
        pack_path=str(pack_path),
        pack_name=pack_name,
        pack_version=pack_version,
        files_written=files_written,
        audit_entries_added=audit_count,
        capabilities_regenerated=caps_ok,
        force=force,
        justification=justification,
        collisions_resolved=collisions if force else [],
    )


def export_brand(
    name: str,
    *,
    author: dict[str, str] | None = None,
    out_dir: Path | None = None,
) -> ExportResult:
    """Pack a single brand profile (+ its `<name>-assets/` dir) into a pack."""
    bpath = _find_brand(name)
    if bpath is None:
        raise ValueError(
            f"Brand {name!r} not found under {USER_BRANDS_DIR} or {BRANDS_DIR}"
        )
    meta = _brand_metadata(bpath)
    description = meta.get("description")
    # Brand YAML doesn't carry a version field today; pack version
    # tracks the brand-schema version (1.x).
    version = "1.0.0"

    file_pairs = _collect_brand_files(bpath, name)
    body = build_canonical_tar_body(file_pairs)
    content_hash = compute_content_hash(body)

    author_dict = author or _resolve_default_author()
    pack_name = _make_pack_name(slugify_author(author_dict.get("name", "unknown")), name)

    manifest = PackManifest(
        pack_format=PACK_FORMAT_VERSION,
        name=pack_name,
        version=version,
        content_hash=content_hash,
        contents={"brands": [{"name": name}]},
        requires={},
        author=author_dict or None,
        description=description,
        tags=["brand"],
    )

    out_dir = out_dir or DEFAULT_OUT_DIR
    pack_filename = f"{name}-{version}.katib-pack"
    pack_path = _write_pack_file(manifest, file_pairs, out_dir, pack_filename)

    return ExportResult(
        artifact_kind="brand",
        artifact_name=name,
        pack_name=pack_name,
        version=version,
        pack_path=str(pack_path),
        pack_bytes=pack_path.stat().st_size,
        content_hash=content_hash,
        files_included=[arc for arc, _ in file_pairs],
    )
