#!/usr/bin/env python3
"""Cut media/Bxx.mp4 for the capture beats (B02, B06, B13, B14) from capture/a7_play.avi (A7 reel).

Adapted from the A6 reel's tool (godot-waikthrough capture contract, reused by godot-gamedev):
  - shot["segments"] = [{"start": s, "end": e, "speed": 1 | 0.125}, ...] in capture seconds.
    speed 1 is real speed: the 60 fps capture is written at 30 fps by dropping alternate frames.
    speed 0.125 is a LABELLED slow replay: each captured 60 fps frame is held for 4 output frames
    (setpts x 8, then fps 30 duplicates frames); no frame is interpolated or invented.
  - the last segment has no "end": it runs until the beat's measured narration is filled
  - every clip carries a persistent label (what it is; "REPLAY 1/8 SPEED" on slow segments)
  - shot["crop"] = [x, y, w, h] (4K source pixels) crops before scaling; the label says "cropped"
  - the 4K frame is inset at 0.8 (3072x1728) on the page so the label sits in the bottom band
  - silent: the narration is the only audio
"""
import json
import pathlib
import subprocess
import sys

REEL = pathlib.Path(__file__).resolve().parent.parent
MEDIA = REEL / "media"
TMP = REEL / "_qc" / "clips"
MP3 = REEL / "mp3"
FPS = 30
W, H = 3840, 2160
GAME_W, GAME_H = 3072, 1728
BAND = (H - GAME_H) // 2
PAGE = "0xFAF9F5"
FONT = "C\\:/Windows/Fonts/seguisb.ttf"
LABEL_SIZE = 56
LABEL_Y = BAND + GAME_H + 18
TOP_Y = BAND - 18 - LABEL_SIZE


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
    TMP.mkdir(parents=True, exist_ok=True)
    only = sys.argv[1:]
    sheet = json.loads((REEL / "beat_sheet.json").read_text(encoding="utf-8"))
    for b in sheet["beats"]:
        shot = b.get("shot", {})
        if shot.get("source") != "capture" or (only and b["beat_id"] not in only):
            continue
        bid = b["beat_id"]
        src = REEL / shot["capture_file"]
        total = probe(src)
        length = round(probe(MP3 / f"beat-{bid}.mp3"), 3)
        crop = shot.get("crop")
        pre = f"crop={crop[2]}:{crop[3]}:{crop[0]}:{crop[1]}," if crop else ""
        parts, used = [], 0.0
        for i, seg in enumerate(shot["segments"]):
            speed = seg["speed"]
            last = i == len(shot["segments"]) - 1
            if last:
                out_len = round(length - used, 3)
                src_len = out_len * speed
                if seg["start"] + src_len > total + 1e-3:
                    sys.exit(f"{bid}: last segment {seg['start']}+{src_len:.2f}s runs past the capture ({total:.2f}s)")
            else:
                src_len = seg["end"] - seg["start"]
                out_len = round(src_len / speed, 3)
            used += out_len
            top = "REPLAY 1/8 SPEED · each captured frame held, none added" if speed != 1 else "REAL SPEED"
            vf = (f"{pre}scale={GAME_W}:{GAME_H}:flags=lanczos,setpts={1 / speed:.4f}*(PTS-STARTPTS),fps={FPS},"
                  f"pad={W}:{H}:{(W - GAME_W) // 2}:{BAND}:color={PAGE},"
                  f"drawtext=fontfile='{FONT}':text='{esc(shot['label'])}':x=(w-text_w)/2:y={LABEL_Y}:"
                  f"fontsize={LABEL_SIZE}:fontcolor=0x3D3929,"
                  f"drawtext=fontfile='{FONT}':text='{esc(top)}':x=(w-text_w)/2:y={TOP_Y}:"
                  f"fontsize={LABEL_SIZE}:fontcolor={'0xA44A32' if speed != 1 else '0x3D3929'}")
            part = TMP / f"{bid}_{i}.mp4"
            run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-ss", f"{seg['start']:.3f}", "-i", str(src),
                 "-t", f"{src_len:.4f}", "-vf", vf, "-t", f"{out_len:.3f}", "-an", "-c:v", "libx264",
                 "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", "-r", str(FPS), str(part)])
            parts.append(part)
            print(f"{bid} seg {i}: {seg['start']:.3f}s +{src_len:.3f}s at {speed}x -> {out_len:.3f}s")
        lst = TMP / f"{bid}_list.txt"
        lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in parts), encoding="utf-8")
        run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
             "-c", "copy", str(MEDIA / f"{bid}.mp4")])
        print(f"{bid:<6}{probe(MEDIA / f'{bid}.mp4'):.3f}s (narration {length:.3f}s)")


if __name__ == "__main__":
    main()
