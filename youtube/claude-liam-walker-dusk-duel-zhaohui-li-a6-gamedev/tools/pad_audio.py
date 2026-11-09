#!/usr/bin/env python3
"""Add the silences the skill's laws require but the toolkit does not implement:
lead_silence_s before B01's narration (the hesitant writer needs a head start) and tail_hold_s
after the outro's narration (the card must not cut on the last syllable). The original Kokoro
take is kept as mp3/raw/beat-Bxx.mp3; the padded file replaces mp3/beat-Bxx.mp3. Logged in BUILD-LOG.
"""
import json, pathlib, shutil, subprocess

REEL = pathlib.Path(__file__).resolve().parent.parent
sheet = json.loads((REEL / "beat_sheet.json").read_text(encoding="utf-8"))
(REEL / "mp3" / "raw").mkdir(exist_ok=True)
for b in sheet["beats"]:
    lead, tail = float(b.get("lead_silence_s") or 0), float(b.get("tail_hold_s") or 0)
    if not (lead or tail):
        continue
    mp3 = REEL / "mp3" / f"beat-{b['beat_id']}.mp3"
    raw = REEL / "mp3" / "raw" / mp3.name
    if not raw.exists():
        shutil.copy2(mp3, raw)
    af = []
    if lead:
        af.append(f"adelay={int(lead * 1000)}:all=1")
    if tail:
        af.append(f"apad=pad_dur={tail}")
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(raw),
                    "-af", ",".join(af), "-c:a", "libmp3lame", "-q:a", "2", str(mp3)], check=True)
    d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                              "default=nw=1:nk=1", str(mp3)], capture_output=True, text=True).stdout)
    print(f"{b['beat_id']}: +{lead}s lead, +{tail}s tail -> {d:.2f}s")
