"""Component authoring operations — the library behind `scripts/component.py`.

Exposes six entry points that mirror the ADR's component lifecycle CLI:

    scaffold        katib component new
    validate_full   katib component validate
    render_isolated katib component test
    register        katib component register
    bundle_share    katib component share
    lint_all        katib component lint --all

All functions return structured result dicts (no printing). The CLI wrapper
formats for human or JSON output.
"""
from __future__ import annotations

import json
import re
import shutil
import sys
import tarfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

from core.tokens import user_components_dir, user_memory_dir

REPO_ROOT = Path(__file__).resolve().parent.parent
COMPONENTS_DIR = REPO_ROOT / "components"
USER_COMPONENTS_DIR = user_components_dir()
SCHEMAS_DIR = REPO_ROOT / "schemas"
FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures" / "components"
DIST_DIR = REPO_ROOT / "dist"

# User-tier audit/requests paths (Phase 2). Phase 4 extends the user tier
# to component scaffold files themselves — see USER_COMPONENTS_DIR above.
MEMORY_DIR = user_memory_dir()
AUDIT_FILE = MEMORY_DIR / "component-audit.jsonl"
REQUESTS_FILE = MEMORY_DIR / "component-requests.jsonl"

TIER_DIRS = {"primitive": "primitives", "section": "sections", "cover": "covers"}
LANG_ENUM = ("en", "ar", "bilingual")

NAME_RE = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")

GRADUATION_THRESHOLD = 3


# ---------------------------------------------------------------------------
# shared helpers
# ---------------------------------------------------------------------------


def _load_schema() -> dict:
    return json.loads((SCHEMAS_DIR / "component.yaml.schema.json").read_text("utf-8"))


def _load_component_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _display_path(p: Path) -> str:
    """Render path relative to REPO_ROOT when possible, else absolute. User-tier
    paths (under `~/.katib/`) live outside REPO_ROOT and would raise on a
    naked `.relative_to(REPO_ROOT)` call."""
    try:
        return str(p.relative_to(REPO_ROOT))
    except ValueError:
        return str(p)


def _find_component(name: str) -> Path | None:
    """Return the component directory if it exists, else None. Searches the
    user tier first (so user components shadow bundled at lookup time), then
    the bundled tier. Same precedent as recipe resolution."""
    for base in (USER_COMPONENTS_DIR, COMPONENTS_DIR):
        for tier_dirname in TIER_DIRS.values():
            candidate = base / tier_dirname / name
            if (candidate / "component.yaml").exists():
                return candidate
    return None


def _find_bundled_component(name: str) -> Path | None:
    """Return the bundled-tier component path, ignoring any user-tier shadow.
    Used by the scaffold collision check — `_find_component` finds user-tier
    shadows too, but for "refuse to shadow bundled" we need the bundled path
    specifically."""
    for tier_dirname in TIER_DIRS.values():
        candidate = COMPONENTS_DIR / tier_dirname / name
        if (candidate / "component.yaml").exists():
            return candidate
    return None


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# scaffold — `katib component new`
# ---------------------------------------------------------------------------


@dataclass
class ScaffoldResult:
    component: str
    tier: str
    namespace: str
    path: str
    files_created: list[str]
    graduation_warning: str | None = None
    audit_entry: dict = field(default_factory=dict)


def _graduation_request_count(name: str) -> int:
    """Count matching entries in memory/component-requests.jsonl.

    Returns 0 if the file doesn't exist yet (no component requests have been
    logged via `katib log_request` or the graduation gate in `/katib`).
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


def _scaffold_component_yaml(
    name: str,
    tier: str,
    namespace: str,
    languages: list[str],
    requires_tokens: list[str],
    description: str,
) -> str:
    """Render a minimal, schema-conformant component.yaml as a YAML string."""
    data: dict[str, Any] = {
        "name": name,
        "tier": tier,
        "version": "0.1.0",
        "namespace": namespace,
        "description": description,
        "languages": languages,
    }
    if requires_tokens:
        data["requires"] = {"tokens": requires_tokens}
    data["accepts"] = {
        "inputs": [
            {"title": {"type": "string", "required": True}},
        ],
    }
    return yaml.safe_dump(data, sort_keys=False, allow_unicode=True)


def _scaffold_html(name: str, lang: str) -> str:
    if lang == "ar":
        return (
            f'<section class="katib-{name}" lang="ar" dir="rtl">\n'
            f"  <!-- TODO: replace with real Arabic content -->\n"
            f'  <h2>{{{{ input.title }}}}</h2>\n'
            f"</section>\n"
        )
    if lang == "bilingual":
        return (
            f'<section class="katib-{name}" lang="en">\n'
            f"  <!-- TODO: replace with bilingual two-column content -->\n"
            f'  <div class="katib-{name}__en"><h2>{{{{ input.title }}}}</h2></div>\n'
            f'  <div class="katib-{name}__ar" lang="ar" dir="rtl"><h2>{{{{ input.title }}}}</h2></div>\n'
            f"</section>\n"
        )
    return (
        f'<section class="katib-{name}" lang="en">\n'
        f"  <!-- TODO: replace with real content -->\n"
        f'  <h2>{{{{ input.title }}}}</h2>\n'
        f"</section>\n"
    )


def _scaffold_readme(name: str, tier: str, description: str) -> str:
    return (
        f"# {name}\n\n"
        f"**Tier:** {tier}\n\n"
        f"## Purpose\n\n"
        f"{description}\n\n"
        f"## Variants\n\n"
        f"- default\n\n"
        f"## Inputs\n\n"
        f"- `title` (string, required): …\n\n"
        f"## Usage Example\n\n"
        f"```yaml\n"
        f"- component: {name}\n"
        f"  inputs:\n"
        f"    title: \"Example title\"\n"
        f"```\n\n"
        f"## Accessibility Notes\n\n"
        f"- Root element carries `lang` / `dir` attributes\n"
    )


def _scaffold_fixture(name: str) -> str:
    return (
        f"# Test inputs for `{name}` isolated render.\n"
        f"# Used by `katib component test {name}`. Add realistic sample values.\n"
        f"inputs:\n"
        f"  title: \"Sample title\"\n"
        f"brand: null        # or a registered brand name, e.g. acme\n"
        f"variant: null      # or a declared variant name\n"
    )


def scaffold(
    name: str,
    *,
    tier: str,
    namespace: str = "katib",
    languages: list[str] | None = None,
    requires_tokens: list[str] | None = None,
    description: str | None = None,
    force: bool = False,
    justification: str | None = None,
    from_graduation: str | None = None,
) -> ScaffoldResult:
    """Scaffold a new component skeleton. Raises ValueError on misuse."""
    if not NAME_RE.match(name):
        raise ValueError(
            f"component name {name!r} must be kebab-case (e.g. my-widget)"
        )
    if tier not in TIER_DIRS:
        raise ValueError(
            f"tier must be one of {list(TIER_DIRS)}, got {tier!r}"
        )
    languages = languages or ["en", "ar"]
    for lang in languages:
        if lang not in LANG_ENUM:
            raise ValueError(
                f"language {lang!r} not in {list(LANG_ENUM)}"
            )

    # Existence / shadow check. Order matters:
    #   - For namespace=user, reject a user-tier duplicate outright, and
    #     reject a bundled-tier collision unless --force --justification is
    #     supplied (matches recipe precedent).
    #   - For namespace=katib, any existing component with the same name
    #     (either tier) is a hard error — core scaffolding does not shadow.
    existing = _find_component(name)
    bundled_collision = _find_bundled_component(name)
    if namespace == "user":
        if existing is not None and existing != bundled_collision:
            # User-tier duplicate — always a hard error.
            raise ValueError(
                f"component {name!r} already exists at {_display_path(existing)}"
            )
        if bundled_collision is not None and not force:
            raise ValueError(
                f"component {name!r} already exists in the bundled tier at "
                f"{_display_path(bundled_collision)}. User components cannot "
                f"shadow bundled components without "
                f"--force --justification '<reason>'."
            )
        if force and bundled_collision is not None and not justification:
            raise ValueError(
                "--force requires --justification '<reason>' (audited)"
            )
    else:
        if existing is not None:
            raise ValueError(
                f"component {name!r} already exists at {_display_path(existing)}"
            )

    # Graduation check — soft-pass until the requests log has enough entries.
    graduation_warning: str | None = None
    if namespace == "katib":
        count = _graduation_request_count(name)
        if count < GRADUATION_THRESHOLD and not force:
            if not REQUESTS_FILE.exists():
                graduation_warning = (
                    "Graduation gate: no component requests logged yet at "
                    f"{_display_path(REQUESTS_FILE)}. Scaffolded without a "
                    f"request count. Once requests accumulate, core namespace "
                    f"scaffolds will require >={GRADUATION_THRESHOLD} matching "
                    f"requests or --force --justification '<reason>'."
                )
            else:
                graduation_warning = (
                    f"Only {count} request(s) logged for {name!r}; "
                    f"graduation flow recommends >={GRADUATION_THRESHOLD}. "
                    f"Pass --force --justification '<reason>' to override (audited)."
                )
        elif force and not justification:
            raise ValueError(
                "--force requires --justification '<reason>' (audited)"
            )

    description = description or f"TODO: describe what {name} does."

    # Write root depends on namespace:
    #   user → USER_COMPONENTS_DIR (~/.katib/components/) — survives reinstall
    #   katib → COMPONENTS_DIR (bundled) — ships with the skill
    write_root = USER_COMPONENTS_DIR if namespace == "user" else COMPONENTS_DIR
    tier_dirname = TIER_DIRS[tier]
    cdir = write_root / tier_dirname / name
    cdir.mkdir(parents=True, exist_ok=False)

    created: list[str] = []

    # component.yaml
    yaml_text = _scaffold_component_yaml(
        name=name,
        tier=tier,
        namespace=namespace,
        languages=languages,
        requires_tokens=requires_tokens or [],
        description=description,
    )
    (cdir / "component.yaml").write_text(yaml_text, encoding="utf-8")
    created.append(_display_path(cdir / "component.yaml"))

    # HTML variants
    for lang in languages:
        html_path = cdir / f"{lang}.html"
        html_path.write_text(_scaffold_html(name, lang), encoding="utf-8")
        created.append(_display_path(html_path))

    # README
    readme_path = cdir / "README.md"
    readme_path.write_text(_scaffold_readme(name, tier, description), encoding="utf-8")
    created.append(_display_path(readme_path))

    # Test fixture — lives under REPO_ROOT/tests/fixtures/components/ for
    # bundled components. For user components, the fixture goes next to the
    # component itself so it survives reinstall.
    if namespace == "user":
        fixture_dir = cdir / "fixtures"
    else:
        fixture_dir = FIXTURES_DIR / name
    fixture_dir.mkdir(parents=True, exist_ok=True)
    fixture_path = fixture_dir / "test-inputs.yaml"
    fixture_path.write_text(_scaffold_fixture(name), encoding="utf-8")
    created.append(_display_path(fixture_path))

    # Audit entry — action: scaffold
    audit_entry = {
        "component": name,
        "tier": tier,
        "namespace": namespace,
        "action": "scaffold",
        "at": _now(),
        "from_graduation": from_graduation,
        "force_justification": justification if force else None,
        "note": "Scaffolded by katib component new",
    }
    _append_audit(audit_entry)

    return ScaffoldResult(
        component=name,
        tier=tier,
        namespace=namespace,
        path=_display_path(cdir),
        files_created=created,
        graduation_warning=graduation_warning,
        audit_entry=audit_entry,
    )


def _append_audit(entry: dict) -> None:
    _ensure_parent(AUDIT_FILE)
    with AUDIT_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
# validate — `katib component validate`
# ---------------------------------------------------------------------------


@dataclass
class ValidationIssue:
    severity: str     # "error" | "warning"
    category: str     # "schema" | "lang" | "tokens" | "brand" | "inputs" | "a11y" | "docs" | "tests"
    message: str

    def as_dict(self) -> dict:
        return {"severity": self.severity, "category": self.category, "message": self.message}


@dataclass
class ValidationResult:
    component: str
    tier: str | None
    path: str
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def errors(self) -> list[ValidationIssue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> list[ValidationIssue]:
        return [i for i in self.issues if i.severity == "warning"]

    @property
    def ok(self) -> bool:
        return not self.errors

    def as_dict(self) -> dict:
        return {
            "component": self.component,
            "tier": self.tier,
            "path": self.path,
            "ok": self.ok,
            "issues": [i.as_dict() for i in self.issues],
        }


# Regex patterns for token / brand / input references.
# HTML supports both {{ colors.X }} (Jinja direct ref) and var(--X) (embedded CSS);
# CSS supports var(--X).
_TOKEN_HTML_RE = re.compile(r"\{\{\s*colors\.([a-zA-Z_][a-zA-Z0-9_]*)")
_CSS_VAR_RE = re.compile(r"var\(--([a-zA-Z][a-zA-Z0-9-]*)\)")
_BRAND_RE = re.compile(r"\{\{\s*brand(?:\.[a-zA-Z_][a-zA-Z0-9_]*)+")
_INPUT_RE = re.compile(r"\{\{\s*(?:input|inputs)\.([a-zA-Z_][a-zA-Z0-9_]*)")
_ROOT_LANG_RE = re.compile(r"<(?:section|div|article|main)[^>]*\blang\s*=")


def _token_to_cssvar(key: str) -> str:
    """Translate a token key (snake_case) to its CSS variable name (kebab-case)."""
    try:
        from core.tokens import _COLOR_KEY_TO_VAR

        if key in _COLOR_KEY_TO_VAR:
            return _COLOR_KEY_TO_VAR[key].lstrip("-")
    except ImportError:
        pass
    return key.replace("_", "-")


# Non-token CSS variables the engine defines globally. Used to suppress false
# positives when scanning for "used but not declared" tokens.
_NON_TOKEN_CSS_VARS = frozenset({
    "font-primary", "font-display", "font-mono",
})


def _extract_brand_paths(html: str) -> set[str]:
    """Return set of dotted `brand.X.Y` paths seen in HTML."""
    out: set[str] = set()
    for m in re.finditer(r"\{\{\s*(brand(?:\.[a-zA-Z_][a-zA-Z0-9_]*)+)", html):
        dotted = m.group(1)[len("brand."):]
        out.add(dotted)
    return out


def _extract_input_names(html: str) -> set[str]:
    return set(_INPUT_RE.findall(html))


def _extract_html_token_refs(html: str) -> set[str]:
    """Return token keys referenced via `{{ colors.X }}` in Jinja templates."""
    return set(_TOKEN_HTML_RE.findall(html))


def _extract_css_vars(text: str) -> set[str]:
    """Return CSS variable names (without leading --) referenced via var(--X)."""
    return set(_CSS_VAR_RE.findall(text))


def _declared_input_names(comp: dict) -> set[str]:
    out: set[str] = set()
    for entry in comp.get("accepts", {}).get("inputs", []) or []:
        if not isinstance(entry, dict):
            continue
        if "type" in entry and "name" in entry:
            out.add(entry["name"])
        elif len(entry) == 1:
            out.add(next(iter(entry.keys())))
    return out


def _fixture_path(name: str) -> Path:
    """Locate the test-inputs.yaml for a component. Bundled components store
    fixtures under REPO_ROOT/tests/fixtures/components/<name>/. User
    components store them next to the component so they survive reinstall.
    Prefer user-tier when both exist (matches render shadow semantics)."""
    cdir = _find_component(name)
    if cdir is not None:
        colocated = cdir / "fixtures" / "test-inputs.yaml"
        if colocated.exists():
            return colocated
    return FIXTURES_DIR / name / "test-inputs.yaml"


def validate_full(name: str) -> ValidationResult:
    cdir = _find_component(name)
    if cdir is None:
        raise ValueError(
            f"component {name!r} not found under {COMPONENTS_DIR} "
            f"or {USER_COMPONENTS_DIR}"
        )
    meta_path = cdir / "component.yaml"

    result = ValidationResult(
        component=name,
        tier=None,
        path=_display_path(cdir),
    )

    # 1. Schema
    try:
        data = _load_component_yaml(meta_path)
    except yaml.YAMLError as e:
        result.issues.append(ValidationIssue("error", "schema", f"YAML parse error: {e}"))
        return result
    validator = Draft202012Validator(_load_schema())
    for e in sorted(validator.iter_errors(data), key=lambda e: list(e.path)):
        result.issues.append(
            ValidationIssue("error", "schema", f"{list(e.path) or '(root)'}: {e.message}")
        )
    result.tier = data.get("tier")
    if result.errors:
        return result   # don't run further checks on a broken schema

    # 2. Language completeness
    languages = data.get("languages", [])
    for lang in languages:
        if not (cdir / f"{lang}.html").exists():
            result.issues.append(
                ValidationIssue(
                    "error",
                    "lang",
                    f"declared lang {lang!r} but {lang}.html is missing",
                )
            )

    # 3+4+5. Token / brand / input parity — walk every present HTML file + styles.css
    declared_tokens = set(data.get("requires", {}).get("tokens", []))
    declared_brands = set(data.get("requires", {}).get("brand_fields", []))
    declared_inputs = _declared_input_names(data)
    html_token_refs: set[str] = set()
    css_var_refs: set[str] = set()
    used_brands: set[str] = set()
    used_inputs: set[str] = set()

    for lang in languages:
        html_path = cdir / f"{lang}.html"
        if not html_path.exists():
            continue
        html = html_path.read_text(encoding="utf-8")
        html_token_refs |= _extract_html_token_refs(html)
        css_var_refs |= _extract_css_vars(html)   # inline style blocks
        used_brands |= _extract_brand_paths(html)
        used_inputs |= _extract_input_names(html)

        # 6. A11y — root element must carry lang attribute
        if not _ROOT_LANG_RE.search(html):
            result.issues.append(
                ValidationIssue(
                    "warning",
                    "a11y",
                    f"{lang}.html root element has no lang= attribute",
                )
            )

    styles_path = cdir / "styles.css"
    if styles_path.exists():
        css_var_refs |= _extract_css_vars(styles_path.read_text(encoding="utf-8"))

    # Token hygiene
    # (a) HTML {{ colors.X }} refs — must be declared; unknown = error
    for t in sorted(html_token_refs - declared_tokens):
        result.issues.append(
            ValidationIssue(
                "error",
                "tokens",
                f"token {t!r} used via {{{{ colors.{t} }}}} in HTML but not in requires.tokens",
            )
        )
    # (b) Declared tokens must appear somewhere — either {{ colors.X }} in HTML
    #     OR `var(--<cssvar>)` in CSS / inline style blocks
    declared_cssvars = {_token_to_cssvar(t): t for t in declared_tokens}
    used_declared_via_cssvar = {
        declared_cssvars[v] for v in css_var_refs if v in declared_cssvars
    }
    used_declared = html_token_refs | used_declared_via_cssvar
    for t in sorted(declared_tokens - used_declared):
        result.issues.append(
            ValidationIssue(
                "warning",
                "tokens",
                f"token {t!r} declared in requires.tokens but not referenced in HTML or styles.css",
            )
        )

    # Brand hygiene — undeclared brand refs are errors
    # Any level-1 path (brand.X) is enough to match declared "X" or "X.Y"
    flat_declared_brands = declared_brands
    for b in sorted(used_brands):
        # Match either the full dotted path or any prefix
        if b not in flat_declared_brands and not any(
            b.startswith(d + ".") or d.startswith(b + ".") for d in flat_declared_brands
        ):
            result.issues.append(
                ValidationIssue(
                    "error",
                    "brand",
                    f"brand field {b!r} used but not in requires.brand_fields",
                )
            )

    # Input parity — undeclared inputs are errors
    for i in sorted(used_inputs - declared_inputs):
        result.issues.append(
            ValidationIssue(
                "error",
                "inputs",
                f"input {i!r} used in HTML but not in accepts.inputs",
            )
        )

    # 7. README presence + section headers
    readme_path = cdir / "README.md"
    if not readme_path.exists():
        result.issues.append(
            ValidationIssue("error", "docs", "README.md missing")
        )
    else:
        readme = readme_path.read_text(encoding="utf-8")
        for required_section in ("Purpose", "Inputs"):
            if not re.search(rf"^#+\s+{required_section}\b", readme, re.MULTILINE):
                result.issues.append(
                    ValidationIssue(
                        "warning",
                        "docs",
                        f"README.md missing '## {required_section}' section",
                    )
                )

    # 8. Test fixture presence
    if not _fixture_path(name).exists():
        result.issues.append(
            ValidationIssue(
                "warning",
                "tests",
                f"test fixture missing at tests/fixtures/components/{name}/test-inputs.yaml "
                f"(auto-synthesis will be used)",
            )
        )

    return result


# ---------------------------------------------------------------------------
# test — `katib component test`
# ---------------------------------------------------------------------------


@dataclass
class IsolatedRenderResult:
    component: str
    lang: str
    variant: str | None
    pdf_path: str
    pdf_bytes: int
    weasyprint_warnings: int


def _auto_inputs(comp: dict) -> dict:
    """Generate placeholder inputs from the declared accepts.inputs schema.

    Tries to produce something sensible for each type; image slots use the
    existing test fixture image.
    """
    out: dict[str, Any] = {}
    for entry in comp.get("accepts", {}).get("inputs", []) or []:
        if not isinstance(entry, dict):
            continue
        # Detect {name: {...}} vs {name: X, type: Y} form
        if "type" in entry and "name" in entry:
            name, decl = entry["name"], entry
        elif len(entry) == 1:
            name, decl = next(iter(entry.items()))
            if not isinstance(decl, dict):
                continue
        else:
            continue

        t = decl.get("type", "string")
        if t in ("string", "markdown"):
            out[name] = f"Sample {name}"
        elif t == "int":
            out[name] = 1
        elif t == "float":
            out[name] = 1.0
        elif t == "bool":
            out[name] = True
        elif t == "date":
            out[name] = "2026-01-01"
        elif t == "image":
            fixture_img = REPO_ROOT / "tests" / "fixtures" / "tutorial-step.png"
            sources = decl.get("sources_accepted") or ["user-file"]
            if "inline-svg" in sources:
                # Minimal donut spec — inline-svg provider accepts this shape.
                out[name] = {
                    "source": "inline-svg",
                    "type": "donut",
                    "data": [
                        {"label": "A", "value": 1},
                        {"label": "B", "value": 1},
                    ],
                }
            elif "user-file" in sources:
                out[name] = {
                    "source": "user-file",
                    "path": str(fixture_img),
                    "alt_text": "placeholder",
                }
            else:
                # Other sources require live dependencies — skip
                continue
        elif t == "array":
            out[name] = []
        elif t == "object":
            out[name] = {}
    return out


def _load_fixture(name: str) -> dict:
    fp = _fixture_path(name)
    if not fp.exists():
        return {}
    data = yaml.safe_load(fp.read_text(encoding="utf-8")) or {}
    return data


def render_isolated(
    name: str,
    lang: str | None = None,
    variant: str | None = None,
    out_dir: Path | None = None,
) -> list[IsolatedRenderResult]:
    """Render the component in isolation as a one-section recipe and return
    results for every (language × [variant or None]) combination.

    If `lang` is None, iterates over every lang declared by the component.
    If the fixture specifies inputs/brand/variant, those override auto-synth.
    """
    cdir = _find_component(name)
    if cdir is None:
        raise ValueError(
            f"component {name!r} not found under {COMPONENTS_DIR} or {USER_COMPONENTS_DIR}"
        )
    comp = _load_component_yaml(cdir / "component.yaml")
    declared_langs = comp.get("languages", [])
    if lang is not None:
        if lang not in declared_langs:
            raise ValueError(
                f"component {name!r} does not declare lang {lang!r} "
                f"(declares: {declared_langs})"
            )
        langs_to_render = [lang]
    else:
        langs_to_render = list(declared_langs)

    fixture = _load_fixture(name)
    fixture_inputs = fixture.get("inputs") or {}
    fixture_brand = fixture.get("brand")
    fixture_variant = fixture.get("variant")

    auto_inputs = _auto_inputs(comp)
    # Fixture values override auto-synth
    inputs = {**auto_inputs, **fixture_inputs}

    results: list[IsolatedRenderResult] = []
    out_dir = out_dir or (REPO_ROOT / "dist" / "component-tests" / name)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Local imports — heavy deps (Jinja, WeasyPrint) only pulled when actually rendering
    from core.compose import compose
    from core.render import render_to_pdf

    for rlang in langs_to_render:
        ephemeral_recipe = _synth_single_section_recipe(
            comp_name=name, lang=rlang, inputs=inputs, variant=variant or fixture_variant
        )
        recipe_path = out_dir / f"_{rlang}.recipe.yaml"
        recipe_path.write_text(
            yaml.safe_dump(ephemeral_recipe, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
        html, _meta = compose(str(recipe_path), rlang, brand=fixture_brand)
        pdf_path = out_dir / f"{name}.{rlang}.pdf"

        warn_count = _count_weasyprint_warnings(lambda: render_to_pdf(html, pdf_path, base_url=REPO_ROOT))
        if not pdf_path.exists() or pdf_path.stat().st_size == 0:
            raise RuntimeError(
                f"isolated render of {name!r} ({rlang}) produced no PDF bytes"
            )

        results.append(
            IsolatedRenderResult(
                component=name,
                lang=rlang,
                variant=variant or fixture_variant,
                pdf_path=str(pdf_path),
                pdf_bytes=pdf_path.stat().st_size,
                weasyprint_warnings=warn_count,
            )
        )

    return results


def _synth_single_section_recipe(
    *, comp_name: str, lang: str, inputs: dict, variant: str | None
) -> dict:
    section: dict[str, Any] = {"component": comp_name, "inputs": inputs}
    if variant:
        section["variant"] = variant
    return {
        "name": f"component-test-{comp_name}",
        "version": "0.0.0",
        "namespace": "katib",
        "description": f"Ephemeral single-section recipe for testing {comp_name}",
        "languages": [lang],
        "sections": [section],
    }


def _count_weasyprint_warnings(render_fn) -> int:
    """Count WeasyPrint log records emitted during render_fn()."""
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
# register — `katib component register`
# ---------------------------------------------------------------------------


@dataclass
class RegisterResult:
    component: str
    capabilities_regenerated: bool
    audit_entry: dict
    validation: ValidationResult


def register(name: str) -> RegisterResult:
    """Re-validate, regenerate capabilities.yaml, log audit entry.

    Raises ValueError if validation fails (never registers a broken component).
    """
    v = validate_full(name)
    if not v.ok:
        raise ValueError(
            f"cannot register {name!r}: {len(v.errors)} validation error(s). "
            f"Run `katib component validate {name}` for details."
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
        "component": name,
        "tier": v.tier,
        "namespace": _load_component_yaml(
            (REPO_ROOT / v.path) / "component.yaml"
        ).get("namespace", "katib"),
        "action": "register",
        "at": _now(),
        "from_graduation": None,
        "note": "Registered by katib component register",
    }
    _append_audit(audit_entry)

    return RegisterResult(
        component=name,
        capabilities_regenerated=True,
        audit_entry=audit_entry,
        validation=v,
    )


# ---------------------------------------------------------------------------
# share — `katib component share`
# ---------------------------------------------------------------------------


@dataclass
class ShareResult:
    component: str
    bundle_path: str
    bundle_bytes: int
    files_included: list[str]


# Files we allow inside a share bundle. Everything else is excluded.
_SHARE_ALLOWLIST = (
    "component.yaml",
    "README.md",
    "styles.css",
    "en.html",
    "ar.html",
    "bilingual.html",
)


def bundle_share(name: str, out_dir: Path | None = None) -> ShareResult:
    cdir = _find_component(name)
    if cdir is None:
        raise ValueError(
            f"component {name!r} not found under {COMPONENTS_DIR} or {USER_COMPONENTS_DIR}"
        )
    comp = _load_component_yaml(cdir / "component.yaml")
    version = comp.get("version", "0.0.0")

    out_dir = out_dir or DIST_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    bundle_path = out_dir / f"{name}-{version}.tar.gz"

    included: list[str] = []
    with tarfile.open(bundle_path, "w:gz") as tar:
        for fname in _SHARE_ALLOWLIST:
            fpath = cdir / fname
            if fpath.exists():
                arcname = f"{name}/{fname}"
                tar.add(fpath, arcname=arcname)
                included.append(arcname)
        # Include fixture if present
        fpath = _fixture_path(name)
        if fpath.exists():
            arcname = f"{name}/tests/test-inputs.yaml"
            tar.add(fpath, arcname=arcname)
            included.append(arcname)
        # Manifest
        manifest = {
            "component": name,
            "version": version,
            "tier": comp.get("tier"),
            "namespace": comp.get("namespace"),
            "bundled_at": _now(),
            "files": included,
        }
        manifest_bytes = json.dumps(manifest, indent=2, ensure_ascii=False).encode("utf-8")
        info = tarfile.TarInfo(name=f"{name}/MANIFEST.json")
        info.size = len(manifest_bytes)
        tar.addfile(info, BytesIO(manifest_bytes))
        included.append(f"{name}/MANIFEST.json")

    return ShareResult(
        component=name,
        bundle_path=str(bundle_path),
        bundle_bytes=bundle_path.stat().st_size,
        files_included=included,
    )


# ---------------------------------------------------------------------------
# lint --all — `katib component lint`
# ---------------------------------------------------------------------------


def lint_all() -> list[ValidationResult]:
    """Lint every component on disk across both bundled and user tiers.
    User components shadow bundled (same semantics as render) — each name
    is validated once, using whichever path `_find_component()` resolves."""
    results: list[ValidationResult] = []
    seen: set[str] = set()
    for base in (USER_COMPONENTS_DIR, COMPONENTS_DIR):
        for tier_dirname in TIER_DIRS.values():
            tdir = base / tier_dirname
            if not tdir.exists():
                continue
            for cdir in sorted(tdir.iterdir()):
                if not (cdir / "component.yaml").exists():
                    continue
                if cdir.name in seen:
                    continue
                seen.add(cdir.name)
                results.append(validate_full(cdir.name))
    return results


# ---------------------------------------------------------------------------
# teardown helpers (for testing)
# ---------------------------------------------------------------------------


def _cleanup_component_dir(name: str) -> None:
    """Test helper: remove scaffolded component + fixture + audit rows + regen caps."""
    cdir = _find_component(name)
    if cdir is not None:
        shutil.rmtree(cdir)
    fdir = FIXTURES_DIR / name
    if fdir.exists():
        shutil.rmtree(fdir)
    # Strip audit rows for this component
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
            if entry.get("component") != name:
                keep.append(line_stripped)
        AUDIT_FILE.write_text("\n".join(keep) + ("\n" if keep else ""), encoding="utf-8")
    # Regenerate capabilities.yaml if it still references the removed component
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
