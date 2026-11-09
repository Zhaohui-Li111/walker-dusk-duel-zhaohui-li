#!/usr/bin/env python3
"""Visual QC: frames at 15 / 50 / 85 % of every beat's media -> _qc/contact_N.png (5 beats per sheet)."""
import json, pathlib, subprocess
from PIL import Image, ImageDraw, ImageFont
REEL = pathlib.Path(__file__).resolve().parent.parent
Q = REEL / "_qc" / "frames"; Q.mkdir(parents=True, exist_ok=True)
sheet = json.loads((REEL / "beat_sheet.json").read_text(encoding="utf-8"))
ids = [b["beat_id"] for b in sheet["beats"]]
f = ImageFont.truetype("C:/Windows/Fonts/seguisb.ttf", 28)
for n in range(0, len(ids), 5):
    out = Image.new("RGB", (3 * 960, 5 * 560), "white"); d = ImageDraw.Draw(out)
    for r, bid in enumerate(ids[n:n + 5]):
        m = REEL / "media" / f"{bid}.mp4"
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(m)],
                                   capture_output=True, text=True).stdout)
        for c, fr in enumerate((0.15, 0.5, 0.85)):
            p = Q / f"{bid}_{int(fr*100)}.png"
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{dur*fr:.2f}", "-i", str(m), "-frames:v", "1",
                            "-vf", "scale=960:540", str(p)], check=True)
            out.paste(Image.open(p), (c * 960, r * 560 + 20))
        d.text((10, r * 560 - 2), f"{bid}  {dur:.2f}s", font=f, fill="red")
    out.save(REEL / "_qc" / f"contact_{n // 5 + 1}.png")
    print("contact", n // 5 + 1)
