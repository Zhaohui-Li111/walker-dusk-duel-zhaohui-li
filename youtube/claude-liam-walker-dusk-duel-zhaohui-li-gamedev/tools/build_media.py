#!/usr/bin/env python3
"""Cut media/Bxx.mp4 for the capture beats, and the slice-audio track for B13.

Rules (godot-waikthrough capture contract, reused by godot-gamedev):
  - real speed only: no setpts, no frame-rate change inside an action; the 60 fps Movie Maker
    capture is written at the film's 30 fps by dropping alternate frames, which keeps time
  - each narrated clip is exactly its beat's measured narration length, starting at the
    window start in tools/windows.json, so the compiler has nothing to retime
  - every clip carries a persistent label saying what it is (scripted input, staged pose,
    slice audio); the gameplay is inset at 4.8x the 640x360 canvas (3072x1728)
  - B13's audio is the capture's own audio for the same interval as its frames
"""
import json
import pathlib
import subprocess
import sys

REEL = pathlib.Path(__file__).resolve().parent.parent
CAPTURE = REEL / "capture" / "run-01.avi"
STATES = REEL / "capture" / "evidence" / "states"
MEDIA = REEL / "media"
MP3 = REEL / "mp3"
AUDIO = REEL / "audio"
FPS = 30
W, H = 3840, 2160
GAME_W, GAME_H = 3072, 1728          # 4.8x the 640x360 canvas, leaves 216 px bands
BAND = (H - GAME_H) // 2
PAGE = "0xFAF9F5"
FONT = "C\\:/Windows/Fonts/seguisb.ttf"
LABEL_SIZE = 64                       # cap height clears GATE T's 41 px floor at 2160
LABEL_Y = BAND + GAME_H + 14          # inside the bottom band (1944-2160), above the 5% safe line (2052)
TOP_LABEL_Y = int(H * 0.05) + 8       # inside the top band (0-216), below the 5% safe line (108)


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


def frame_chain(label, top=None):
    chain = (f"scale={GAME_W}:{GAME_H}:flags=lanczos,"
             f"pad={W}:{H}:{(W - GAME_W) // 2}:{BAND}:color={PAGE},"
             f"drawtext=fontfile='{FONT}':text='{esc(label)}':x=(w-text_w)/2:y={LABEL_Y}:"
             f"fontsize={LABEL_SIZE}:fontcolor=0x3D3929")
    if top:
        chain += (f",drawtext=fontfile='{FONT}':text='{esc(top)}':x=(w-text_w)/2:y={TOP_LABEL_Y}:"
                  f"fontsize={LABEL_SIZE}:fontcolor=0xB4532F")
    return chain


def encode(inputs, vf, length, out, extra=()):
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *inputs, "-t", f"{length:.3f}",
         "-vf", vf, "-r", str(FPS), "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "16",
         "-pix_fmt", "yuv420p", *extra, str(out)])


def main():
    MEDIA.mkdir(exist_ok=True)
    AUDIO.mkdir(exist_ok=True)
    sheet = json.loads((REEL / "beat_sheet.json").read_text(encoding="utf-8"))
    cap_len = probe(CAPTURE)
    rows = []
    for b in sheet["beats"]:
        shot = b.get("shot", {})
        if shot.get("source") != "capture":
            continue
        bid = b["beat_id"]
        out = MEDIA / f"{bid}.mp4"
        if b["beat_id"] == "B13":
            start, end = shot["capture_start_s"], shot["capture_end_s"]
            length = round(end - start, 3)
            encode(["-ss", f"{start:.3f}", "-i", str(CAPTURE)],
                   frame_chain(shot["label"], top="SLICE AUDIO · no narration"), length, out)
            wav = AUDIO / "B13-slice.wav"
            run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-ss", f"{start:.3f}", "-i", str(CAPTURE),
                 "-t", f"{length:.3f}", "-vn", "-af",
                 f"afade=t=in:d=0.02,afade=t=out:st={length - 0.02:.3f}:d=0.02",
                 "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", str(wav)])
            rows.append((bid, f"{start:.2f}-{end:.2f}s + own audio", length))
            continue
        length = round(probe(MP3 / f"beat-{bid}.mp3"), 3)
        if shot.get("capture") == "states":
            src = REEL / shot["capture_file"]
            encode(["-loop", "1", "-i", str(src)], frame_chain(shot["label"]), length, out)
            rows.append((bid, f"still {src.name}", length))
            continue
        start = float(shot["capture_start_s"])
        if start + length > cap_len:
            sys.exit(f"{bid}: window {start}+{length} runs past the capture ({cap_len:.2f}s)")
        encode(["-ss", f"{start:.3f}", "-i", str(CAPTURE)], frame_chain(shot["label"]), length, out)
        rows.append((bid, f"{start:.2f}-{start + length:.2f}s", length))
    for r in rows:
        print(f"{r[0]:<6}{r[1]:<32}{r[2]:>8.3f}")


if __name__ == "__main__":
    main()
