#!/usr/bin/env python3
"""Read every narration clip back with faster-whisper base.en; write _qc/transcripts.json."""
import json, pathlib, sys
from faster_whisper import WhisperModel
REEL = pathlib.Path(__file__).resolve().parent.parent
only = sys.argv[1:]
m = WhisperModel("base.en", device="cpu", compute_type="int8")
out_p = REEL / "_qc" / "transcripts.json"
out = json.loads(out_p.read_text(encoding="utf-8")) if out_p.exists() else {}
for mp3 in sorted((REEL / "mp3").glob("beat-*.mp3")):
    bid = mp3.stem.split("-")[1]
    if only and bid not in only:
        continue
    segs, _ = m.transcribe(str(mp3), beam_size=5)
    out[bid] = " ".join(s.text.strip() for s in segs)
    print(bid, "|", out[bid])
out_p.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
