#!/usr/bin/env bash
# Rebuild capture/game: an isolated copy of godot/ with exactly these harness changes:
#   - capture_orbit.gd / capture_stills.gd added (camera drivers; the prop room itself is untouched)
#   - a 3840x2160 window so Movie Maker renders native 4K
# and capture/game-raised: the same copy with PROP-TAIKO raised 0.05 m in prop_room.tscn, used only
# for the labelled "can the check fail?" still. Nothing in godot/ is modified.
set -euo pipefail
REEL="$(cd "$(dirname "$0")/.." && pwd)"
GAME="$REEL/../../godot"
for name in game game-raised; do
  rm -rf "$REEL/capture/$name"
  mkdir -p "$REEL/capture"
  cp -r "$GAME" "$REEL/capture/$name"
  rm -rf "$REEL/capture/$name/.godot"
  cp "$REEL/tools/capture_orbit.gd" "$REEL/tools/capture_stills.gd" "$REEL/capture/$name/"
  python - "$REEL/capture/$name/project.godot" <<'PY'
import sys
p = sys.argv[1]
s = open(p, encoding="utf-8").read()
s = s.replace("window_width_override=1280", "window_width_override=3840")
s = s.replace("window_height_override=720", "window_height_override=2160")
open(p, "w", encoding="utf-8", newline="\n").write(s)
PY
done
python - "$REEL/capture/game-raised/props3d/prop_room.tscn" <<'PY'
import sys
p = sys.argv[1]
s = open(p, encoding="utf-8").read()
old = "0, 1, 0, 0, 0, 1, 0.5, 0, 0)"
assert s.count(old) == 1, "taiko transform not found"
open(p, "w", encoding="utf-8", newline="\n").write(s.replace(old, "0, 1, 0, 0, 0, 1, 0.5, 0.05, 0)"))
PY
echo "capture copies ready: $REEL/capture/game and $REEL/capture/game-raised"
