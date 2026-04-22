#!/usr/bin/env bash
# Smoke-test the brand profile system.
# Verifies: loader, tokens merge, context vars, end-to-end render with brand.

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$SKILL_DIR"

# Phase 2 regression: pin render tests to fs mode (see test-all.sh comment).
export KATIB_VAULT_MODE="${KATIB_VAULT_MODE:-fs}"

echo "▶ Katib brand profile smoke test"
echo ""

# ===== 1. Loader + unit-level merge/context =====
echo "▶ Step 1: brand.py helpers"
uv run --quiet --with 'pyyaml>=6.0' python3 -c "
import sys, json
from pathlib import Path
sys.path.insert(0, 'scripts')
from brand import load_brand, apply_brand_to_tokens, brand_context_vars, BrandError

skill_brands = Path('brands')
b = load_brand('example', skill_brands)
assert b['name'] == 'Example Corp', b
assert b['legal_name'] == 'Example Corporation FZE'

# Merge into synthetic tokens
tokens = {
    'semantic_colors': {'--accent': '#000', '--text': '#111'},
    'fonts': {'en': {'primary': 'Arial'}, 'ar': {'primary': 'Tahoma'}},
}
merged = apply_brand_to_tokens(tokens, b)
assert merged['semantic_colors']['--accent'] == '#1F3A68', merged['semantic_colors']
assert merged['semantic_colors']['--accent-2'] == '#D4A437'
assert merged['semantic_colors']['--text'] == '#111', 'domain default preserved when brand omits'
assert merged['fonts']['en']['primary'] == 'Inter'
assert merged['fonts']['ar']['primary'] == 'IBM Plex Arabic'

# No-brand passthrough
pass_through = apply_brand_to_tokens(tokens, None)
assert pass_through['semantic_colors']['--accent'] == '#000'

# Context vars
en_ctx = brand_context_vars(b, 'en')
assert en_ctx['name'] == 'Example Corp'
ar_ctx = brand_context_vars(b, 'ar')
assert ar_ctx['name'] == 'مثال', ar_ctx
assert en_ctx['identity']['email'] == 'hello@example.com'

# Missing brand → empty-but-safe
empty = brand_context_vars(None, 'en')
assert empty['name'] == ''
assert empty['identity'] == {}

# Error path
try:
    load_brand('nonexistent-brand', skill_brands)
    assert False, 'should have raised'
except BrandError:
    pass

# Color value type safety — non-string values must fail cleanly
import tempfile
with tempfile.NamedTemporaryFile('w', suffix='.yaml', delete=False) as f:
    f.write('name: Bad\ncolors:\n  accent: [not, a, string]\n')
    bad = f.name
try:
    bad_brand = load_brand(bad, skill_brands)
    apply_brand_to_tokens({'semantic_colors': {'--accent': '#000'}, 'fonts': {}}, bad_brand)
    assert False, 'non-string color should have raised'
except BrandError as e:
    assert 'must be a CSS color string' in str(e), str(e)

print('  ✓ 12 loader/merge/context assertions pass')
"

# ===== 1b. v1.3 validation hardening =====
echo ""
echo "▶ Step 1b: v1.3 validation (color injection, max_height bounds, empty name, bilingual fallback)"
uv run --quiet --with 'pyyaml>=6.0' python3 -c "
import sys, tempfile
from pathlib import Path
sys.path.insert(0, 'scripts')
from brand import load_brand, apply_brand_to_tokens, brand_context_vars, BrandError

skill_brands = Path('brands')
assertions = 0

def _brand_file(body: str) -> str:
    f = tempfile.NamedTemporaryFile('w', suffix='.yaml', delete=False)
    f.write(body)
    f.close()
    return f.name

# ---- CSS injection attempts must raise ----
attacks = [
    '#FF0000; } body { display: none; /*',
    'red; background: url(http://evil)',
    'navy\n--foo: bar',
    '#FF0000/* wtf */',
    '\";alert(1);//',
]
for attack in attacks:
    p = _brand_file(f'name: Hack\ncolors:\n  accent: {attack!r}\n')
    try:
        apply_brand_to_tokens({'semantic_colors': {}, 'fonts': {}}, load_brand(p, skill_brands))
        print(f'  ✗ injection was NOT caught: {attack!r}')
        sys.exit(1)
    except BrandError:
        assertions += 1

# ---- Legitimate color shapes must pass ----
good = ['#FF0000', '#F00', '#FF0000AA', 'rgb(255,0,0)', 'rgba(255, 0, 0, 0.5)', 'hsl(210, 50%, 40%)', 'navy', 'transparent']
for color in good:
    p = _brand_file(f'name: Good\ncolors:\n  accent: {color!r}\n')
    merged = apply_brand_to_tokens({'semantic_colors': {}, 'fonts': {}}, load_brand(p, skill_brands))
    assert merged['semantic_colors']['--accent'] == color, f'unexpected value for {color!r}'
    assertions += 1

# ---- max_height_mm bounds ----
for bad in [-5, 0, 201, 9999]:
    p = _brand_file(f'name: T\nlogo:\n  max_height_mm: {bad}\n')
    try:
        load_brand(p, skill_brands)
        print(f'  ✗ out-of-range max_height_mm={bad} accepted')
        sys.exit(1)
    except BrandError as e:
        assert 'between' in str(e), str(e)
        assertions += 1

# String with unit ('18mm') must fail cleanly, not with ValueError traceback
p = _brand_file('name: T\nlogo:\n  max_height_mm: \"18mm\"\n')
try:
    load_brand(p, skill_brands)
    print('  ✗ string \"18mm\" accepted')
    sys.exit(1)
except BrandError as e:
    assert 'integer' in str(e), str(e)
    assertions += 1

# Valid heights pass
for good in [1, 18, 50, 200]:
    p = _brand_file(f'name: T\nlogo:\n  max_height_mm: {good}\n')
    b = load_brand(p, skill_brands)
    assert b['_resolved_logo']['max_height_mm'] == good
    assertions += 1

# ---- Empty/null name rejected ----
for bad in ['', '{}', 'name:\n', 'name: \"\"\n', 'name: {en: \"\", ar: \"\"}\n']:
    body = bad if bad.startswith('name') else f'name: {bad}\n'
    p = _brand_file(body)
    try:
        load_brand(p, skill_brands)
        print(f'  ✗ empty name accepted: {body!r}')
        sys.exit(1)
    except BrandError as e:
        assert 'name' in str(e).lower(), str(e)
        assertions += 1

# Bilingual name dict passes
p = _brand_file('name:\n  en: Acme\n  ar: أكمي\n')
b = load_brand(p, skill_brands)
assert brand_context_vars(b, 'ar')['name'] == 'أكمي'
assert brand_context_vars(b, 'en')['name'] == 'Acme'
assertions += 2

# ---- Bilingual fallback for legal_name and identity ----
p = _brand_file('''
name: Acme
name_ar: أكمي
legal_name: Acme Corp FZE
legal_name_ar: شركة أكمي ذ.م.م
identity:
  author_name: John Doe
  email: hello@acme.com
  address: Dubai, UAE
identity_ar:
  author_name: جون دو
  address: دبي، الإمارات
''')
b = load_brand(p, skill_brands)

en = brand_context_vars(b, 'en')
ar = brand_context_vars(b, 'ar')

assert en['legal_name'] == 'Acme Corp FZE'
assert ar['legal_name'] == 'شركة أكمي ذ.م.م', ar['legal_name']
assert en['identity']['author_name'] == 'John Doe'
assert ar['identity']['author_name'] == 'جون دو', ar['identity']
assert ar['identity']['address'] == 'دبي، الإمارات'
assert ar['identity']['email'] == 'hello@acme.com', 'email should fall through to EN'
assertions += 6

# Dict-shaped identity value also works (inline {en, ar})
p = _brand_file('''
name: Acme
identity:
  author_name:
    en: John Doe
    ar: جون دو
''')
b = load_brand(p, skill_brands)
assert brand_context_vars(b, 'ar')['identity']['author_name'] == 'جون دو'
assertions += 1

print(f'  ✓ {assertions} v1.3 validation assertions pass')
"

# ===== 1c. v1.4 polish (.yml parity, unknown color warn, logo format, brand-file shadow) =====
echo ""
echo "▶ Step 1c: v1.4 polish (.yml parity, logo format whitelist, unknown color warn)"
uv run --quiet --with 'pyyaml>=6.0' python3 -c "
import sys, tempfile, os, io, contextlib
from pathlib import Path
sys.path.insert(0, 'scripts')
from brand import load_brand, apply_brand_to_tokens, list_brands, BrandError

skill_brands = Path('brands')
assertions = 0

# .yml in user dir must be discoverable by both list_brands and name-lookup
with tempfile.TemporaryDirectory() as td:
    td_path = Path(td)
    (td_path / 'yaml-profile.yaml').write_text('name: Yaml Brand\n')
    (td_path / 'yml-profile.yml').write_text('name: Yml Brand\n')
    os.environ['KATIB_BRANDS_DIR'] = str(td_path)

    names = {b['name'] for b in list_brands(skill_brands)}
    assert 'yaml-profile' in names, names
    assert 'yml-profile' in names, '.yml not discovered by list_brands'
    assertions += 2

    # Name-based lookup across both extensions
    b = load_brand('yml-profile', skill_brands)
    assert b['name'] == 'Yml Brand'
    assertions += 1

    os.environ.pop('KATIB_BRANDS_DIR')

# Logo format whitelist — .webp rejected, .png accepted
with tempfile.TemporaryDirectory() as td:
    td_path = Path(td)
    (td_path / 'bad.webp').write_bytes(b'fake webp')
    bad_yaml = td_path / 'brand.yaml'
    bad_yaml.write_text('name: Bad\nlogo:\n  primary: bad.webp\n')
    try:
        load_brand(str(bad_yaml), skill_brands)
        print('  ✗ .webp logo accepted (should have raised)')
        sys.exit(1)
    except BrandError as e:
        assert '.webp' in str(e) or '.webp' in repr(e) or 'one of' in str(e), str(e)
        assertions += 1

    # Valid extensions — png, svg, jpg
    for ext in ('.png', '.svg', '.jpg'):
        (td_path / f'logo{ext}').write_bytes(b'fake')
        good_yaml = td_path / f'good{ext}.yaml'
        good_yaml.write_text(f'name: Good\nlogo:\n  primary: logo{ext}\n')
        b = load_brand(str(good_yaml), skill_brands)
        assert b['_resolved_logo']['primary'].endswith(f'logo{ext}'), b
        assertions += 1

# Unknown color key emits stderr warning
buf = io.StringIO()
with tempfile.NamedTemporaryFile('w', suffix='.yaml', delete=False) as f:
    f.write('name: T\ncolors:\n  not_a_key: \"#123456\"\n')
    p = f.name
b = load_brand(p, skill_brands)
with contextlib.redirect_stderr(buf):
    apply_brand_to_tokens({'semantic_colors': {}, 'fonts': {}}, b)
warn = buf.getvalue()
assert 'not_a_key' in warn and 'not a recognized' in warn, warn
assertions += 1

print(f'  ✓ {assertions} v1.4 polish assertions pass')
"

# ===== 1d. --brand + --brand-file shadow warning (build.py path) =====
echo ""
echo "▶ Step 1d: --brand-file shadow warning"
SHADOW_OUT=$(uv run scripts/build.py one-pager --domain business-proposal --lang en \
  --title 'Shadow test' --project 'katib-shadow-test' --slug katib-shadow-test \
  --brand example --brand-file "$(pwd)/brands/triden.yaml" 2>&1)
if echo "$SHADOW_OUT" | grep -q 'overrides --brand'; then
  echo "  ✓ shadow warning emitted when both flags passed"
else
  echo "  ✗ expected shadow warning, got:"
  echo "$SHADOW_OUT" | head -5
  exit 1
fi
# Clean up the shadow-test render folder
SHADOW_FOLDER="$HOME/vault/content/katib/business-proposal/$(ls -t ~/vault/content/katib/business-proposal/ | grep katib-shadow-test | head -1)"
[ -d "$SHADOW_FOLDER" ] && rm -rf "$SHADOW_FOLDER"

# ===== 2. End-to-end render with --brand (real PDF render, no cover) =====
echo ""
echo "▶ Step 2: end-to-end render with --brand example"

uv run scripts/build.py one-pager \
  --domain business-proposal \
  --lang en \
  --title "Brand smoke test one-pager" \
  --project "katib-brand-smoke" \
  --slug katib-brand-smoke \
  --ref "BRAND-SMOKE-001" \
  --brand example 2>&1 | tail -4

# Check the rendered HTML actually has the brand accent color injected
FOLDER="$HOME/vault/content/katib/business-proposal/$(ls -t ~/vault/content/katib/business-proposal/ | grep katib-brand-smoke | head -1)"
HTML="$FOLDER/source/one-pager.en.html"

if [ ! -f "$HTML" ]; then
  echo "  ✗ rendered HTML not found at $HTML"
  exit 1
fi

# Brand color should appear in the tokens CSS block inside the HTML
if grep -q '\-\-accent: #1F3A68' "$HTML"; then
  echo "  ✓ brand --accent color present in rendered HTML"
else
  echo "  ✗ brand accent color NOT in rendered HTML"
  grep '^\s*--accent' "$HTML" || true
  exit 1
fi

# Brand letterhead img should appear on business-proposal one-pager
if grep -q 'class="brand-letterhead"' "$HTML"; then
  echo "  ✓ brand-letterhead img present on business-proposal render"
else
  echo "  ✗ brand-letterhead img missing from business-proposal render"
  exit 1
fi

# Tokens snapshot should reflect the merge
SNAP="$FOLDER/source/tokens-snapshot.json"
if [ -f "$SNAP" ]; then
  if grep -q '1F3A68' "$SNAP"; then
    echo "  ✓ brand color in tokens-snapshot.json"
  else
    echo "  ✗ brand color missing from tokens-snapshot.json"
    exit 1
  fi
fi

# ===== 3. No-brand regression — default katib output unchanged =====
echo ""
echo "▶ Step 3: no-brand render still works (regression)"
uv run scripts/build.py one-pager \
  --domain business-proposal \
  --lang en \
  --title "Default render" \
  --project "katib-brand-regression" \
  --slug katib-brand-regression \
  --ref "REG-001" 2>&1 | tail -3

REG_FOLDER="$HOME/vault/content/katib/business-proposal/$(ls -t ~/vault/content/katib/business-proposal/ | grep katib-brand-regression | head -1)"
REG_HTML="$REG_FOLDER/source/one-pager.en.html"
if grep -q '\-\-accent: #1B2A4A' "$REG_HTML"; then
  echo "  ✓ default domain accent (Navy) preserved when --brand omitted"
else
  echo "  ✗ default domain accent NOT preserved"
  exit 1
fi

# No-brand regression must NOT render a letterhead
if grep -q 'class="brand-letterhead"' "$REG_HTML"; then
  echo "  ✗ brand-letterhead rendered on no-brand document (should be absent)"
  exit 1
else
  echo "  ✓ no brand-letterhead on no-brand render"
fi

# ===== 4. Logo pipeline (v1.1) =====
echo ""
echo "▶ Step 4: logo resolution + render"

uv run --quiet --with 'pyyaml>=6.0' python3 -c "
import sys
from pathlib import Path
sys.path.insert(0, 'scripts')
from brand import load_brand, brand_context_vars, BrandError

skill_brands = Path('brands')

# example has a logo → resolves to file:// URI
b = load_brand('example', skill_brands)
assert b['_resolved_logo']['primary'].startswith('file://'), b['_resolved_logo']
assert b['_resolved_logo']['primary'].endswith('placeholder-logo.svg')
assert b['_resolved_logo']['max_height_mm'] == 18

# triden has no logo → empty
t = load_brand('triden', skill_brands)
assert t['_resolved_logo']['primary'] == '', t['_resolved_logo']

# Context vars expose logo
ctx = brand_context_vars(b, 'en')
assert ctx['logo']['primary'].startswith('file://')
assert ctx['logo']['max_height_mm'] == 18

# Empty logo context (no brand)
empty = brand_context_vars(None, 'en')
assert empty['logo']['primary'] == ''

# Missing logo file fails cleanly
import tempfile
with tempfile.NamedTemporaryFile('w', suffix='.yaml', delete=False) as f:
    f.write('name: Broken\nlogo: nonexistent-file.png\n')
    bad_path = f.name
try:
    load_brand(bad_path, skill_brands)
    assert False, 'should have raised on missing logo file'
except BrandError as e:
    assert 'missing file' in str(e), str(e)

print('  ✓ 6 logo resolution assertions pass')
"

# End-to-end: tutorial render with logo brand
uv run scripts/build.py how-to \
  --domain tutorial \
  --lang en \
  --title "Logo smoke test" \
  --project "katib-logo-smoke" \
  --slug katib-logo-smoke \
  --brand example 2>&1 | tail -3

LOGO_FOLDER="$HOME/vault/content/katib/tutorial/$(ls -t ~/vault/content/katib/tutorial/ | grep katib-logo-smoke | head -1)"
LOGO_HTML="$LOGO_FOLDER/source/how-to.en.html"

if grep -q 'class="brand-logo"' "$LOGO_HTML"; then
  echo "  ✓ brand-logo img tag present in rendered HTML"
else
  echo "  ✗ brand-logo img tag NOT in rendered HTML"
  exit 1
fi

if grep -q 'placeholder-logo.svg' "$LOGO_HTML"; then
  echo "  ✓ logo src resolves to fixture path"
else
  echo "  ✗ logo src missing"
  exit 1
fi

# No-logo brand (triden) should not inject img
uv run scripts/build.py how-to \
  --domain tutorial \
  --lang en \
  --title "No-logo smoke test" \
  --project "katib-nologo-smoke" \
  --slug katib-nologo-smoke \
  --brand triden 2>&1 | tail -2

NOLOGO_FOLDER="$HOME/vault/content/katib/tutorial/$(ls -t ~/vault/content/katib/tutorial/ | grep katib-nologo-smoke | head -1)"
NOLOGO_HTML="$NOLOGO_FOLDER/source/how-to.en.html"

if grep -q 'class="brand-logo"' "$NOLOGO_HTML"; then
  echo "  ✗ brand-logo unexpectedly rendered for no-logo brand"
  exit 1
else
  echo "  ✓ no brand-logo img when brand lacks logo field"
fi

# ===== 5. --list-brands =====
echo ""
echo "▶ Step 5: --list-brands"
LIST_OUT=$(uv run scripts/build.py --list-brands 2>&1)
if echo "$LIST_OUT" | grep -q 'example' && echo "$LIST_OUT" | grep -q 'triden'; then
  echo "  ✓ --list-brands shows example and triden"
else
  echo "  ✗ --list-brands missing expected entries"
  echo "$LIST_OUT"
  exit 1
fi

# ===== Cleanup =====
for d in "$FOLDER" "$REG_FOLDER" "$LOGO_FOLDER" "$NOLOGO_FOLDER"; do
  [ -d "$d" ] && rm -rf "$d"
done

echo ""
echo "✓ Brand profile smoke test passed"
