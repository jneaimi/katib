"""Recipe authoring operations — the library behind `scripts/recipe.py`.

Mirrors `core/component_ops.py` for recipes:

    scaffold_recipe       katib recipe new
    validate_recipe_full  katib recipe validate
    render_recipe         katib recipe test
    register_recipe       katib recipe register
    bundle_share_recipe   katib recipe share
    lint_all_recipes      katib recipe lint --all

All entry points return structured result dataclasses (no printing). The CLI
wrapper formats for human vs. JSON consumers.
"""
from __future__ import annotations

import difflib
import json
import re
import shutil
import tarfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

from core.tokens import user_memory_dir, user_recipes_dir

REPO_ROOT = Path(__file__).resolve().parent.parent
COMPONENTS_DIR = REPO_ROOT / "components"
# Two-tier recipe layout (Phase 3):
#   RECIPES_DIR      = bundled (shipped with the skill)
#   USER_RECIPES_DIR = user-authored content in ~/.katib/recipes/
# User tier takes precedence on lookup; scaffold always writes to user tier.
RECIPES_DIR = REPO_ROOT / "recipes"
USER_RECIPES_DIR = user_recipes_dir()
SCHEMAS_DIR = REPO_ROOT / "schemas"
DIST_DIR = REPO_ROOT / "dist"

# User-tier audit + requests paths (Phase 2). Evaluated at import time;
# tests that need to redirect should `monkeypatch.setattr` the module
# attribute (or use the `isolated_user_dirs` fixture from conftest).
MEMORY_DIR = user_memory_dir()
AUDIT_FILE = MEMORY_DIR / "recipe-audit.jsonl"
REQUESTS_FILE = MEMORY_DIR / "recipe-requests.jsonl"

TIER_DIRS = ("primitives", "sections", "covers")
LANG_ENUM = ("en", "ar", "bilingual")

NAME_RE = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")


def _display_path(p: Path) -> str:
    """Render a path as REPO_ROOT-relative when possible, absolute otherwise.

    After Phase 2 the user tier lives outside REPO_ROOT, so `.relative_to`
    raises `ValueError` for those paths. This helper gives a readable
    string for both tiers without leaking full home-dir prefixes when the
    file is bundled.
    """
    try:
        return str(p.relative_to(REPO_ROOT))
    except ValueError:
        return str(p)

GRADUATION_THRESHOLD = 3


# ---------------------------------------------------------------------------
# shared helpers
# ---------------------------------------------------------------------------


def _load_schema() -> dict:
    return json.loads((SCHEMAS_DIR / "recipe.yaml.schema.json").read_text("utf-8"))


def _load_recipe_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _recipe_path(name: str) -> Path:
    """Path to an existing recipe — user tier first, bundled fallback.

    Returns the first match on disk. If neither tier has the file,
    returns the *bundled* path (the historical default) so callers
    that handle non-existence themselves see a stable value. Use
    `_find_recipe()` when you want `None` for missing recipes.
    """
    user_path = USER_RECIPES_DIR / f"{name}.yaml"
    if user_path.exists():
        return user_path
    return RECIPES_DIR / f"{name}.yaml"


def _find_recipe(name: str) -> Path | None:
    """Resolve a recipe name to a path or None. User tier preferred."""
    user_path = USER_RECIPES_DIR / f"{name}.yaml"
    if user_path.exists():
        return user_path
    bundled = RECIPES_DIR / f"{name}.yaml"
    if bundled.exists():
        return bundled
    return None


def _user_scaffold_path(name: str) -> Path:
    """Where a new user-scaffolded recipe is written."""
    return USER_RECIPES_DIR / f"{name}.yaml"


def _all_component_names() -> dict[str, Path]:
    """Return {name: path-to-component-dir} across every tier."""
    out: dict[str, Path] = {}
    for tier_dirname in TIER_DIRS:
        tier_dir = COMPONENTS_DIR / tier_dirname
        if not tier_dir.exists():
            continue
        for cdir in tier_dir.iterdir():
            if (cdir / "component.yaml").exists():
                out[cdir.name] = cdir
    return out


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _append_audit(entry: dict) -> None:
    AUDIT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with AUDIT_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
# scaffold — `katib recipe new`
# ---------------------------------------------------------------------------


@dataclass
class RecipeScaffoldResult:
    recipe: str
    namespace: str
    path: str
    graduation_warning: str | None = None
    audit_entry: dict = field(default_factory=dict)


def _graduation_request_count(name: str) -> int:
    """Count matching entries in memory/recipe-requests.jsonl.

    Returns 0 if the file doesn't exist yet (Day 13 starts writing it).
    """
    if not REQUESTS_FILE.exists():
        return 0
    n = 0
    for line in REQUESTS_FILE.read_text("utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if entry.get("closest_existing") == name or entry.get("requested") == name:
            n += 1
    return n


_DEFAULT_SCAFFOLD_SECTIONS = [
    {
        "component": "cover-page",
        "variant": "minimalist-typographic",
        "inputs": {
            "eyebrow": "Document",
            "title": "TODO: document title",
            "subtitle": "TODO: subtitle",
        },
    },
    {
        "component": "module",
        "inputs": {
            "title": "TODO: first module",
            "body": "TODO: module body — plain text or markdown.",
        },
    },
    {
        "component": "summary",
        "inputs": {
            "heading": "Summary",
            "items": ["TODO: takeaway one", "TODO: takeaway two"],
        },
    },
    {
        "component": "whats-next",
        "inputs": {
            "heading": "What's next",
            "items": ["TODO: next step one", "TODO: next step two"],
        },
    },
]


def _scaffold_recipe_yaml(
    name: str,
    namespace: str,
    languages: list[str],
    description: str,
    domain_hint: str | None,
    target_pages: list[int] | None,
    page_limit: int | None,
    keywords: list[str],
    when: str | None,
) -> str:
    data: dict[str, Any] = {
        "name": name,
        "version": "0.1.0",
        "namespace": namespace,
        "description": description,
        "languages": languages,
    }
    if target_pages:
        data["target_pages"] = target_pages
    if page_limit:
        data["page_limit"] = page_limit
    if domain_hint:
        data["domain_hint"] = domain_hint
    if when:
        data["when"] = when
    if keywords:
        data["keywords"] = keywords
    data["sections"] = _DEFAULT_SCAFFOLD_SECTIONS
    return yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=100)


def scaffold_recipe(
    name: str,
    *,
    namespace: str = "katib",
    languages: list[str] | None = None,
    description: str | None = None,
    domain_hint: str | None = None,
    target_pages: list[int] | None = None,
    page_limit: int | None = None,
    keywords: list[str] | None = None,
    when: str | None = None,
    force: bool = False,
    justification: str | None = None,
    from_graduation: str | None = None,
) -> RecipeScaffoldResult:
    """Scaffold a new recipe file. Raises ValueError on misuse."""
    if not NAME_RE.match(name):
        raise ValueError(
            f"recipe name {name!r} must be kebab-case (e.g. my-recipe)"
        )
    languages = languages or ["en"]
    for lang in languages:
        if lang not in LANG_ENUM:
            raise ValueError(f"language {lang!r} not in {list(LANG_ENUM)}")

    # Dual-tier existence check. A user recipe with the same name as a
    # bundled recipe would silently shadow at load time — we refuse at
    # scaffold time unless --force is passed.
    rpath = _user_scaffold_path(name)
    if rpath.exists():
        raise ValueError(
            f"recipe {name!r} already exists at {_display_path(rpath)}"
        )
    bundled_rpath = RECIPES_DIR / f"{name}.yaml"
    if bundled_rpath.exists() and not force:
        raise ValueError(
            f"recipe {name!r} already exists in the bundled tier at "
            f"{_display_path(bundled_rpath)}. User recipes cannot shadow "
            f"bundled recipes without --force --justification '<reason>'."
        )

    graduation_warning: str | None = None
    if namespace == "katib":
        count = _graduation_request_count(name)
        if count < GRADUATION_THRESHOLD and not force:
            if not REQUESTS_FILE.exists():
                graduation_warning = (
                    "Graduation gate is not yet active — "
                    f"{_display_path(REQUESTS_FILE)} does not exist "
                    "(Day 13 will start writing it). Scaffolded without a "
                    "request count. When the log exists, core namespace "
                    f"scaffolds will require >={GRADUATION_THRESHOLD} matching "
                    "requests or --force --justification '<reason>'."
                )
            else:
                graduation_warning = (
                    f"Only {count} request(s) logged for {name!r}; "
                    f"graduation flow recommends >={GRADUATION_THRESHOLD}. "
                    "Pass --force --justification '<reason>' to override (audited)."
                )
        elif force and not justification:
            raise ValueError(
                "--force requires --justification '<reason>' (audited)"
            )

    description = description or f"TODO: describe {name}."
    keywords = keywords or []

    USER_RECIPES_DIR.mkdir(parents=True, exist_ok=True)
    yaml_text = _scaffold_recipe_yaml(
        name=name,
        namespace=namespace,
        languages=languages,
        description=description,
        domain_hint=domain_hint,
        target_pages=target_pages,
        page_limit=page_limit,
        keywords=keywords,
        when=when,
    )
    rpath.write_text(yaml_text, encoding="utf-8")

    audit_entry = {
        "recipe": name,
        "namespace": namespace,
        "action": "scaffold",
        "at": _now(),
        "from_graduation": from_graduation,
        "force_justification": justification if force else None,
        "note": "Scaffolded by katib recipe new",
    }
    _append_audit(audit_entry)

    return RecipeScaffoldResult(
        recipe=name,
        namespace=namespace,
        path=_display_path(rpath),
        graduation_warning=graduation_warning,
        audit_entry=audit_entry,
    )


# ---------------------------------------------------------------------------
# validate — `katib recipe validate`
# ---------------------------------------------------------------------------


@dataclass
class RecipeIssue:
    severity: str     # "error" | "warning"
    category: str     # "schema" | "component-ref" | "variant" | "lang" | "keywords" | "pages" | "content"
    message: str

    def as_dict(self) -> dict:
        return {"severity": self.severity, "category": self.category, "message": self.message}


@dataclass
class RecipeValidationResult:
    recipe: str
    path: str
    issues: list[RecipeIssue] = field(default_factory=list)

    @property
    def errors(self) -> list[RecipeIssue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> list[RecipeIssue]:
        return [i for i in self.issues if i.severity == "warning"]

    @property
    def ok(self) -> bool:
        return not self.errors

    def as_dict(self) -> dict:
        return {
            "recipe": self.recipe,
            "path": self.path,
            "ok": self.ok,
            "issues": [i.as_dict() for i in self.issues],
        }


def validate_recipe_full(
    name: str,
    *,
    content_lint: bool = True,
    strict: bool = False,
) -> RecipeValidationResult:
    """Validate a recipe end-to-end.

    Args:
        name: Recipe name (filename stem).
        content_lint: If True, also run content_lint over the recipe YAML
            prose. Default True. Violations are added as category='content'
            issues with severity preserved from content_lint ('warn' → 'warning').
        strict: If True, promote content-lint warnings to errors. Respects
            KATIB_STRICT_LINT=1 env var as a synonym. CI-friendly.
    """
    rpath = _recipe_path(name)
    if not rpath.exists():
        raise ValueError(f"recipe {name!r} not found at {rpath}")

    result = RecipeValidationResult(
        recipe=name, path=_display_path(rpath)
    )

    # 1. Schema
    try:
        data = _load_recipe_yaml(rpath)
    except yaml.YAMLError as e:
        result.issues.append(RecipeIssue("error", "schema", f"YAML parse error: {e}"))
        return result
    validator = Draft202012Validator(_load_schema())
    for e in sorted(validator.iter_errors(data), key=lambda e: list(e.path)):
        result.issues.append(
            RecipeIssue("error", "schema", f"{list(e.path) or '(root)'}: {e.message}")
        )
    if result.errors:
        return result

    # Gather component info for downstream checks
    components = _all_component_names()
    recipe_langs = set(data.get("languages", []))

    for idx, section in enumerate(data.get("sections", []) or []):
        comp_name = section.get("component")
        if not comp_name:
            continue

        # 2. Component exists
        if comp_name not in components:
            closest = difflib.get_close_matches(comp_name, components.keys(), n=1)
            hint = f" (did you mean {closest[0]!r}?)" if closest else ""
            result.issues.append(
                RecipeIssue(
                    "error",
                    "component-ref",
                    f"section[{idx}]: component {comp_name!r} not found in components/{hint}",
                )
            )
            continue

        comp_yaml = _load_recipe_component(components[comp_name])

        # 3. Language compatibility
        comp_langs = set(comp_yaml.get("languages", []))
        unsupported = recipe_langs - comp_langs
        if unsupported:
            result.issues.append(
                RecipeIssue(
                    "error",
                    "lang",
                    f"section[{idx}] {comp_name!r}: declares {sorted(comp_langs)} "
                    f"but recipe requires {sorted(recipe_langs)} — unsupported: {sorted(unsupported)}",
                )
            )

        # 4. Variant validity
        variant = section.get("variant")
        if variant is not None:
            declared_variants = comp_yaml.get("variants", []) or []
            if variant not in declared_variants:
                result.issues.append(
                    RecipeIssue(
                        "error",
                        "variant",
                        f"section[{idx}] {comp_name!r}: variant {variant!r} not declared "
                        f"(component has: {declared_variants})",
                    )
                )

    # 5. Keywords populated (warning — ranker needs them)
    if not data.get("keywords"):
        result.issues.append(
            RecipeIssue(
                "warning",
                "keywords",
                "recipe declares no keywords[] — capability ranker will downgrade match score",
            )
        )

    # 6. target_pages / page_limit sanity
    target_pages = data.get("target_pages")
    page_limit = data.get("page_limit")
    if target_pages and len(target_pages) == 2:
        lo, hi = target_pages
        if lo > hi:
            result.issues.append(
                RecipeIssue(
                    "error",
                    "pages",
                    f"target_pages {target_pages} inverted (lower bound > upper bound)",
                )
            )
        if page_limit and hi > page_limit:
            result.issues.append(
                RecipeIssue(
                    "warning",
                    "pages",
                    f"target_pages upper bound {hi} exceeds page_limit {page_limit}",
                )
            )

    # 7. Content lint — anti-slop on the recipe's prose
    if content_lint:
        import os
        from core import content_lint as cl

        env_strict = os.environ.get("KATIB_STRICT_LINT", "").strip() in ("1", "true", "yes")
        promote_to_error = strict or env_strict

        raw = rpath.read_text(encoding="utf-8")
        text = cl.extract_text(raw)
        # Recipe prose is EN or AR; default to EN for mixed/explicit detection per recipe metadata
        recipe_langs = data.get("languages", []) or ["en"]
        lint_lang = "ar" if "ar" in recipe_langs and "en" not in recipe_langs else "en"

        try:
            violations = cl.lint(text, lint_lang)
        except ValueError:
            violations = []

        for v in violations:
            # All content-lint findings surface as warnings by default so the
            # authoring workflow stays unblocked on intentional prose. --strict
            # (or KATIB_STRICT_LINT=1) promotes every finding to an error,
            # which blocks register. Content-lint's internal 'error' vs 'warn'
            # granularity is preserved in the message text for human review.
            out_severity = "error" if promote_to_error else "warning"
            result.issues.append(
                RecipeIssue(
                    severity=out_severity,
                    category="content",
                    message=(
                        f"L{v.line} [{v.rule}/{v.severity}] {v.pattern}"
                        + (f" — {v.snippet}" if v.snippet else "")
                    ),
                )
            )

    return result


def _load_recipe_component(cdir: Path) -> dict:
    """Load a component's yaml — best effort, no schema re-validation here."""
    try:
        return yaml.safe_load((cdir / "component.yaml").read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        return {}


# ---------------------------------------------------------------------------
# test (render) — `katib recipe test`
# ---------------------------------------------------------------------------


@dataclass
class RecipeRenderResult:
    recipe: str
    lang: str
    pdf_path: str
    pdf_bytes: int
    weasyprint_warnings: int


def render_recipe(
    name: str,
    langs: list[str] | None = None,
    brand: str | None = None,
    out_dir: Path | None = None,
) -> list[RecipeRenderResult]:
    """Render the recipe to PDF(s) in a throwaway directory.

    If `langs` is None, renders the first declared language only (fast path for
    authoring). Pass `langs=["en", "ar"]` or use the CLI's `--all-langs` flag
    to render every declared language.
    """
    rpath = _recipe_path(name)
    if not rpath.exists():
        raise ValueError(f"recipe {name!r} not found at {rpath}")

    data = _load_recipe_yaml(rpath)
    declared_langs = data.get("languages", [])

    if langs is None:
        render_langs = declared_langs[:1]   # fastest path: just the first lang
    else:
        for l in langs:
            if l not in declared_langs:
                raise ValueError(
                    f"recipe {name!r} does not declare lang {l!r} (declares: {declared_langs})"
                )
        render_langs = langs

    out_dir = out_dir or (REPO_ROOT / "dist" / "recipe-tests" / name)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Local imports — heavy deps only when actually rendering
    from core.compose import compose
    from core.render import render_to_pdf

    results: list[RecipeRenderResult] = []
    for lang in render_langs:
        html, _meta = compose(str(rpath), lang, brand=brand)
        pdf_path = out_dir / f"{name}.{lang}.pdf"
        warn_count = _count_weasyprint_warnings(
            lambda: render_to_pdf(html, pdf_path, base_url=REPO_ROOT)
        )
        if not pdf_path.exists() or pdf_path.stat().st_size == 0:
            raise RuntimeError(
                f"recipe {name!r} ({lang}) produced no PDF bytes"
            )
        results.append(
            RecipeRenderResult(
                recipe=name,
                lang=lang,
                pdf_path=str(pdf_path),
                pdf_bytes=pdf_path.stat().st_size,
                weasyprint_warnings=warn_count,
            )
        )

    return results


def _count_weasyprint_warnings(render_fn) -> int:
    import logging

    class _Counter(logging.Handler):
        def __init__(self):
            super().__init__(level=logging.WARNING)
            self.count = 0

        def emit(self, record):
            if record.levelno >= logging.WARNING:
                self.count += 1

    counter = _Counter()
    wp_logger = logging.getLogger("weasyprint")
    wp_logger.addHandler(counter)
    try:
        render_fn()
    finally:
        wp_logger.removeHandler(counter)
    return counter.count


# ---------------------------------------------------------------------------
# register — `katib recipe register`
# ---------------------------------------------------------------------------


@dataclass
class RecipeRegisterResult:
    recipe: str
    capabilities_regenerated: bool
    audit_entry: dict
    validation: RecipeValidationResult


def register_recipe(
    name: str,
    *,
    content_lint: bool = True,
    strict: bool = False,
) -> RecipeRegisterResult:
    v = validate_recipe_full(name, content_lint=content_lint, strict=strict)
    if not v.ok:
        raise ValueError(
            f"cannot register {name!r}: {len(v.errors)} validation error(s). "
            f"Run `katib recipe validate {name}` for details."
        )

    # Regenerate capabilities.yaml
    from scripts.generate_capabilities import build_capabilities

    caps = build_capabilities()
    text = yaml.safe_dump(caps, sort_keys=False, allow_unicode=True, width=100)
    banner = (
        "# capabilities.yaml — AUTO-GENERATED from components/ + recipes/.\n"
        "# Do not hand-edit. Regenerate with:\n"
        "#     uv run scripts/generate_capabilities.py\n\n"
    )
    (REPO_ROOT / "capabilities.yaml").write_text(banner + text, encoding="utf-8")

    audit_entry = {
        "recipe": name,
        "namespace": _load_recipe_yaml(_recipe_path(name)).get("namespace", "katib"),
        "action": "register",
        "at": _now(),
        "from_graduation": None,
        "note": "Registered by katib recipe register",
    }
    _append_audit(audit_entry)

    return RecipeRegisterResult(
        recipe=name,
        capabilities_regenerated=True,
        audit_entry=audit_entry,
        validation=v,
    )


# ---------------------------------------------------------------------------
# share — `katib recipe share`
# ---------------------------------------------------------------------------


@dataclass
class RecipeShareResult:
    recipe: str
    bundle_path: str
    bundle_bytes: int
    files_included: list[str]


def bundle_share_recipe(
    name: str,
    out_dir: Path | None = None,
    *,
    content_lint: bool = True,
    strict: bool = False,
) -> RecipeShareResult:
    rpath = _recipe_path(name)
    if not rpath.exists():
        raise ValueError(f"recipe {name!r} not found at {rpath}")
    # Validate first — never bundle a broken recipe
    v = validate_recipe_full(name, content_lint=content_lint, strict=strict)
    if not v.ok:
        raise ValueError(
            f"cannot share {name!r}: {len(v.errors)} validation error(s). "
            f"Run `katib recipe validate {name}` for details."
        )

    data = _load_recipe_yaml(rpath)
    version = data.get("version", "0.0.0")

    out_dir = out_dir or DIST_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    bundle_path = out_dir / f"recipe-{name}-{version}.tar.gz"

    # Referenced components (metadata only)
    referenced = sorted({s.get("component") for s in data.get("sections", []) if s.get("component")})

    manifest = {
        "recipe": name,
        "version": version,
        "namespace": data.get("namespace"),
        "languages": data.get("languages"),
        "bundled_at": _now(),
        "referenced_components": referenced,
        "note": "Receiver must have the referenced components installed.",
    }
    manifest_bytes = json.dumps(manifest, indent=2, ensure_ascii=False).encode("utf-8")

    with tarfile.open(bundle_path, "w:gz") as tar:
        # The recipe YAML
        tar.add(rpath, arcname=f"{name}/{name}.yaml")
        # MANIFEST.json
        info = tarfile.TarInfo(name=f"{name}/MANIFEST.json")
        info.size = len(manifest_bytes)
        tar.addfile(info, BytesIO(manifest_bytes))

    included = [f"{name}/{name}.yaml", f"{name}/MANIFEST.json"]
    return RecipeShareResult(
        recipe=name,
        bundle_path=str(bundle_path),
        bundle_bytes=bundle_path.stat().st_size,
        files_included=included,
    )


# ---------------------------------------------------------------------------
# lint --all — `katib recipe lint`
# ---------------------------------------------------------------------------


def lint_all_recipes(
    *, content_lint: bool = True, strict: bool = False
) -> list[RecipeValidationResult]:
    """Lint every recipe in both user and bundled tiers.

    User tier is processed first so user recipes that shadow bundled names
    win (bundled version is suppressed). `validate_recipe_full` routes
    through `_find_recipe()` which also prefers user tier — so a shadowed
    bundled recipe is not double-linted.
    """
    results: list[RecipeValidationResult] = []
    seen: set[str] = set()
    if USER_RECIPES_DIR.exists():
        for rfile in sorted(USER_RECIPES_DIR.glob("*.yaml")):
            name = rfile.stem
            seen.add(name)
            results.append(
                validate_recipe_full(name, content_lint=content_lint, strict=strict)
            )
    if RECIPES_DIR.exists():
        for rfile in sorted(RECIPES_DIR.glob("*.yaml")):
            name = rfile.stem
            if name in seen:
                continue  # user tier shadowed this bundled recipe
            results.append(
                validate_recipe_full(name, content_lint=content_lint, strict=strict)
            )
    return results


# ---------------------------------------------------------------------------
# test helpers
# ---------------------------------------------------------------------------


def _cleanup_recipe(name: str) -> None:
    """Test helper: remove scaffolded recipe + audit rows + regen caps if stale."""
    rpath = _recipe_path(name)
    if rpath.exists():
        rpath.unlink()
    if AUDIT_FILE.exists():
        keep: list[str] = []
        for line in AUDIT_FILE.read_text("utf-8").splitlines():
            line_stripped = line.strip()
            if not line_stripped:
                continue
            try:
                entry = json.loads(line_stripped)
            except json.JSONDecodeError:
                keep.append(line_stripped)
                continue
            if entry.get("recipe") != name:
                keep.append(line_stripped)
        AUDIT_FILE.write_text("\n".join(keep) + ("\n" if keep else ""), encoding="utf-8")
    caps_file = REPO_ROOT / "capabilities.yaml"
    if caps_file.exists() and name in caps_file.read_text("utf-8"):
        from scripts.generate_capabilities import build_capabilities

        caps = build_capabilities()
        text = yaml.safe_dump(caps, sort_keys=False, allow_unicode=True, width=100)
        banner = (
            "# capabilities.yaml — AUTO-GENERATED from components/ + recipes/.\n"
            "# Do not hand-edit. Regenerate with:\n"
            "#     uv run scripts/generate_capabilities.py\n\n"
        )
        caps_file.write_text(banner + text, encoding="utf-8")
    # Clean render outputs for this recipe
    render_dir = REPO_ROOT / "dist" / "recipe-tests" / name
    if render_dir.exists():
        shutil.rmtree(render_dir)
