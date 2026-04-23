#!/usr/bin/env bash
# Katib — golden-image tests for annotate.py and frame.py.
#
# Catches regressions in screenshot callouts, arrows, blurs, and browser
# chrome rendering by comparing output against committed golden PNGs with
# tight pixel tolerance.
#
# Limitation: goldens are machine-local. Generated on this Mac with
# the current Pillow + system fonts. Running on a different machine (or
# a major Pillow upgrade) will likely fail — regenerate with `--regenerate`
# after verifying the change is intended.
#
# Usage:
#   bash scripts/test-images.sh              # compare against goldens
#   bash scripts/test-images.sh --regenerate # overwrite goldens with
#                                            # current output (post-review
#                                            # checkpoint after legit changes)

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$SKILL_DIR"

FIXTURES="$SKILL_DIR/tests/fixtures"
GOLDEN="$SKILL_DIR/tests/golden"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

REGENERATE=0
if [ "${1:-}" = "--regenerate" ]; then
  REGENERATE=1
fi

# Tolerance — tight on same machine; loosens slightly to absorb PNG encoder
# drift across Pillow patch versions without letting real regressions pass.
MAX_PIXEL_DIFF=8     # single worst-channel delta
MEAN_PIXEL_DIFF=0.5  # average across the whole image

# =============================================================================
# Step 1: build the deterministic input fixture
# =============================================================================
echo "▶ Katib golden-image tests"
echo ""
echo "▶ Step 1: generate input fixture"

INPUT="$WORK/input.png"
uv run --quiet --with 'pillow>=10.0,<11' python3 - <<PY
from PIL import Image, ImageDraw
W, H = 1440, 900
img = Image.new("RGB", (W, H), (218, 222, 230))   # cool grey canvas
draw = ImageDraw.Draw(img)
# Draw a faux "content card" so annotations have something visible to sit on
draw.rectangle((160, 180, 1280, 720), fill=(250, 250, 252), outline=(190, 194, 204), width=2)
draw.rectangle((200, 220, 1000, 260), fill=(70, 95, 160))  # header bar
for i, y in enumerate((320, 380, 440, 500, 560, 620)):
    draw.rectangle((200, y, 1240 - i * 80, y + 28), fill=(210, 214, 222))
img.save("$INPUT", format="PNG", optimize=True)
print(f"  ✓ input fixture · {img.size}")
PY

# =============================================================================
# Step 2: run annotate scenarios
# =============================================================================
echo ""
echo "▶ Step 2: annotate scenarios"

run_annotate() {
  local name="$1"
  cp "$INPUT" "$WORK/$name.png"
  cp "$FIXTURES/$name.annot.json" "$WORK/$name.annot.json"
  uv run --quiet scripts/annotate.py "$WORK/$name.png" > /dev/null
  echo "  ✓ $name"
}

run_annotate annotate-callouts
run_annotate annotate-arrows
run_annotate annotate-blurs
run_annotate annotate-combined

# =============================================================================
# Step 3: run frame scenarios
# =============================================================================
echo ""
echo "▶ Step 3: frame scenarios"

run_frame() {
  local name="$1" chrome="$2" theme="$3"
  local src="$WORK/$name-src.png"
  cp "$INPUT" "$src"
  # Seed meta so --url defaults work
  cat > "${src%.png}.meta.json" <<EOF
{"type":"screenshot","url":"https://katib-test.local/page","viewport":{"width":1440,"height":900}}
EOF
  uv run --quiet scripts/frame.py "$src" \
    --out "$WORK/$name.png" --chrome "$chrome" --theme "$theme" > /dev/null
  echo "  ✓ $name"
}

run_frame frame-mac-light    mac     light
run_frame frame-mac-dark     mac     dark
run_frame frame-generic-light generic light
run_frame frame-none         none    light

# =============================================================================
# Step 4: compare or regenerate
# =============================================================================
echo ""
if [ "$REGENERATE" = "1" ]; then
  echo "▶ Step 4: REGENERATE — copying current output into tests/golden/"
  for out in annotate-callouts annotate-arrows annotate-blurs annotate-combined \
             frame-mac-light frame-mac-dark frame-generic-light frame-none; do
    # annotate output is <name>.annot.png, frame output is <name>.png
    if [ -f "$WORK/$out.annot.png" ]; then
      cp "$WORK/$out.annot.png" "$GOLDEN/$out.png"
    else
      cp "$WORK/$out.png" "$GOLDEN/$out.png"
    fi
    echo "  ↻ $out"
  done
  echo ""
  echo "✓ Goldens regenerated. Review diffs with git before committing."
  exit 0
fi

echo "▶ Step 4: compare against goldens (max<$MAX_PIXEL_DIFF, mean<$MEAN_PIXEL_DIFF)"

FAILED=0
compare_one() {
  local name="$1" actual="$2"
  local golden="$GOLDEN/$name.png"
  if [ ! -f "$golden" ]; then
    echo "  ✗ $name · no golden at $golden (run with --regenerate first)"
    FAILED=1
    return
  fi
  # Pixel comparison via Pillow
  local result
  result=$(uv run --quiet --with 'pillow>=10.0,<11' python3 - "$golden" "$actual" <<'PY'
import sys
from PIL import Image, ImageChops
g = Image.open(sys.argv[1]).convert("RGB")
a = Image.open(sys.argv[2]).convert("RGB")
if g.size != a.size:
    print(f"SIZE_MISMATCH golden={g.size} actual={a.size}")
    sys.exit(0)
diff = ImageChops.difference(g, a)
extrema = diff.getextrema()  # per-channel (min, max)
max_d = max(hi for _, hi in extrema)
# Mean across all pixels & channels
hist = diff.histogram()
total = sum(i * c for i, c in enumerate(hist[:256])) \
      + sum(i * c for i, c in enumerate(hist[256:512])) \
      + sum(i * c for i, c in enumerate(hist[512:768]))
n_samples = g.size[0] * g.size[1] * 3
mean_d = total / n_samples
print(f"{max_d} {mean_d:.3f}")
PY
  )
  if [[ "$result" == SIZE_MISMATCH* ]]; then
    echo "  ✗ $name · $result"
    FAILED=1
    return
  fi
  local max_d mean_d
  max_d=$(echo "$result" | awk '{print $1}')
  mean_d=$(echo "$result" | awk '{print $2}')
  if [ "$max_d" -gt "$MAX_PIXEL_DIFF" ] || \
     awk -v m="$mean_d" -v t="$MEAN_PIXEL_DIFF" 'BEGIN{exit !(m>t)}'; then
    echo "  ✗ $name · max=$max_d mean=$mean_d (threshold max<$MAX_PIXEL_DIFF mean<$MEAN_PIXEL_DIFF)"
    FAILED=1
  else
    echo "  ✓ $name · max=$max_d mean=$mean_d"
  fi
}

compare_one annotate-callouts  "$WORK/annotate-callouts.annot.png"
compare_one annotate-arrows    "$WORK/annotate-arrows.annot.png"
compare_one annotate-blurs     "$WORK/annotate-blurs.annot.png"
compare_one annotate-combined  "$WORK/annotate-combined.annot.png"
compare_one frame-mac-light    "$WORK/frame-mac-light.png"
compare_one frame-mac-dark     "$WORK/frame-mac-dark.png"
compare_one frame-generic-light "$WORK/frame-generic-light.png"
compare_one frame-none         "$WORK/frame-none.png"

echo ""
if [ "$FAILED" = "1" ]; then
  echo "✗ Golden-image tests FAILED — review diffs, regenerate with --regenerate if intended"
  exit 1
fi
echo "✓ All 8 golden-image comparisons passed"
