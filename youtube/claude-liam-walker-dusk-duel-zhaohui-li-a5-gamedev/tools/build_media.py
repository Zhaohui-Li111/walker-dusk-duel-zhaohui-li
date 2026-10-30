#!/usr/bin/env python3
"""Cut media/Bxx.mp4 for the capture beats (B02, B08) from capture/orbit.avi.

Rules (godot-waikthrough capture contract, reused by godot-gamedev; adapted from the A2 reel):
  - real speed only: no setpts, no frame-rate change inside an action; the 60 fps Movie Maker
    capture is written at the film's 30 fps by dropping alternate frames, which keeps time
  - each clip is exactly its beat's measured narration length, from the beat's capture_start_s
  - every clip carries a persistent label saying what it is (engine capture, scripted camera)
  - the 4K frame is inset at 0.8 (3072x1728) on the page so the label sits in the bottom band
  - silent: the prop room has no sound, and the narration is the only audio
"""
import json
import pathlib
import subprocess
import sys

REEL = pathlib.Path(__file__).resolve().parent.parent
MEDIA = REEL / "media"
MP3 = REEL / "mp3"
FPS = 30
W, H = 3840, 2160
GAME_W, GAME_H = 3072, 1728
BAND = (H - GAME_H) // 2
PAGE = "0xFAF9F5"
FONT = "C\\:/Windows/Fonts/seguisb.ttf"
LABEL_SIZE = 60                       # cap height clears GATE T's 41 px floor at 2160
LABEL_Y = BAND + GAME_H + 16          # inside the bottom band, above the 5% safe line (2052)


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"ffmpeg failed:\n{' '.join(map(str, cmd))}\n{r.stderr[-1500:]}")


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "default=nw=1:nk=1", str(path)], capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def esc(text):
    return text.replace("\\", "\\\\").replace(":", "\\:").replace("'", "’")


def main():
    MEDIA.mkdir(exist_ok=True)
    sheet = json.loads((REEL / "beat_sheet.json").read_text(encoding="utf-8"))
    for b in sheet["beats"]:
        shot = b.get("shot", {})
        if shot.get("source") != "capture":
            continue
        bid = b["beat_id"]
        src = REEL / shot["capture_file"]
        length = round(probe(MP3 / f"beat-{bid}.mp3"), 3)
        start = float(shot["capture_start_s"])
        if start + length > probe(src):
            sys.exit(f"{bid}: window {start}+{length} runs past the capture")
        vf = (f"scale={GAME_W}:{GAME_H}:flags=lanczos,"
              f"pad={W}:{H}:{(W - GAME_W) // 2}:{BAND}:color={PAGE},"
              f"drawtext=fontfile='{FONT}':text='{esc(shot['label'])}':x=(w-text_w)/2:y={LABEL_Y}:"
              f"fontsize={LABEL_SIZE}:fontcolor=0x3D3929")
        run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-ss", f"{start:.3f}", "-i", str(src),
             "-t", f"{length:.3f}", "-vf", vf, "-r", str(FPS), "-an", "-c:v", "libx264", "-preset", "medium",
             "-crf", "16", "-pix_fmt", "yuv420p", str(MEDIA / f"{bid}.mp4")])
        print(f"{bid:<6}{start:.2f}-{start + length:.2f}s  {length:.3f}s")


if __name__ == "__main__":
    main()
