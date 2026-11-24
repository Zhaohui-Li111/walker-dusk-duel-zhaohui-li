#!/usr/bin/env bash
# Pull two unchanged frames of capture/a8_round.avi for the figures (B00 title, B12 desktop side).
# 2.0 s: the title screen; 10.5 s: the fight (Aotake blocking). Scaled 4K -> 1920x1080, nothing else.
set -euo pipefail
REEL="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$REEL/capture/stills"
ffmpeg -y -loglevel error -ss 2.0 -i "$REEL/capture/a8_round.avi" -frames:v 1 -vf scale=1920:1080 "$REEL/capture/stills/title.png"
ffmpeg -y -loglevel error -ss 10.5 -i "$REEL/capture/a8_round.avi" -frames:v 1 -vf scale=1920:1080 "$REEL/capture/stills/fight.png"
echo "stills ready"
