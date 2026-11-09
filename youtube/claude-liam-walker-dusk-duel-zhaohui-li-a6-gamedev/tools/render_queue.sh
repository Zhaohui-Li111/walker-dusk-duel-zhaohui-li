#!/usr/bin/env bash
# Render the given Remotion beats one after another through the toolkit wrapper (A5 reel).
#   bash tools/render_queue.sh B00 B01 ...     Several queues may run at once (as in the A3 reel).
set -u
export PYTHONUTF8=1
# C: is nearly full on this machine; Remotion and Chromium write their frames to the temp folder.
export TEMP="D:\tmp\remotion" TMP="D:\tmp\remotion" TMPDIR="D:/tmp/remotion"
REEL="$(cd "$(dirname "$0")/.." && pwd)"
T=/d/courses/7270/brutalist.art-main/brutalist.art-main
mkdir -p "$REEL/_qc/render"
for b in "$@"; do
  start=$(date +%s)
  (cd "$T" && python runtime/scripts/remotion_scenes.py "$(cygpath -m "$REEL")" --only "$b") > "$REEL/_qc/render/$b.log" 2>&1
  echo "$b exit=$? $(( $(date +%s) - start ))s"
done
