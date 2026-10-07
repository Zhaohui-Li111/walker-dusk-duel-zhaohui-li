#!/usr/bin/env bash
# Rebuild capture/game: an isolated copy of godot/ with exactly two harness changes
# (the capture driver autoload, and a 3840x2160 window so Movie Maker renders native 4K).
set -euo pipefail
REEL="$(cd "$(dirname "$0")/.." && pwd)"
GAME="$REEL/../../godot"
rm -rf "$REEL/capture/game"
mkdir -p "$REEL/capture"
cp -r "$GAME" "$REEL/capture/game"
cp "$REEL/tools/capture_driver.gd" "$REEL/capture/game/capture_driver.gd"
python - "$REEL/capture/game/project.godot" <<'PY'
import sys
p = sys.argv[1]
s = open(p, encoding="utf-8").read()
s = s.replace('Controls="*res://game/controls.gd"',
              'Controls="*res://game/controls.gd"\nCaptureDriver="*res://capture_driver.gd"')
s = s.replace("window_width_override=1280", "window_width_override=3840")
s = s.replace("window_height_override=720", "window_height_override=2160")
open(p, "w", encoding="utf-8", newline="\n").write(s)
PY
echo "capture copy ready: $REEL/capture/game"
