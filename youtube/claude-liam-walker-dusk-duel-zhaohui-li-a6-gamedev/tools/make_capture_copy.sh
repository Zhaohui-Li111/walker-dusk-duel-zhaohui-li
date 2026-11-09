#!/usr/bin/env bash
# Rebuild capture/game: an isolated copy of godot/ (source revision 840bcfd) with exactly these
# harness changes, adapted from the A5 reel's tool:
#   - tools/capture_a6.gd added at the copy's root (scripted-input Movie Maker driver)
#   - a 3840x2160 window override, so Movie Maker renders native 4K
# Nothing in godot/ is modified; godot/shaders/ is copied, never edited.
set -euo pipefail
REEL="$(cd "$(dirname "$0")/.." && pwd)"
GAME="$REEL/../../godot"
rm -rf "$REEL/capture/game"
mkdir -p "$REEL/capture"
cp -r "$GAME" "$REEL/capture/game"
rm -rf "$REEL/capture/game/.godot"
cp "$REEL/tools/capture_a6.gd" "$REEL/capture/game/"
python - "$REEL/capture/game/project.godot" <<'PY'
import sys
p = sys.argv[1]
s = open(p, encoding="utf-8").read()
assert "window_width_override=1280" in s and "window_height_override=720" in s
s = s.replace("window_width_override=1280", "window_width_override=3840")
s = s.replace("window_height_override=720", "window_height_override=2160")
open(p, "w", encoding="utf-8", newline="\n").write(s)
PY
echo "capture copy ready: $REEL/capture/game"
