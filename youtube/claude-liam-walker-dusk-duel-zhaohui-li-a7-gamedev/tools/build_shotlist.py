#!/usr/bin/env python3
"""Write SHOTLIST.md from beat_sheet.json (one row per beat: act, visual, source, timing). A6 tool, adapted
for footage segments."""
import json, pathlib
REEL = pathlib.Path(__file__).resolve().parent.parent
d = json.loads((REEL / "beat_sheet.json").read_text(encoding="utf-8"))
rows = ["# SHOTLIST — " + d["metadata"]["title"], "",
        "Generated from beat_sheet.json by tools/build_shotlist.py. Times are measured narration (audio is the clock). "
        "Footage segments are seconds into capture/a7_play.avi; the last segment runs until the narration ends.", "",
        "| Beat | Act | s | Visual | Source / evidence | Audio |", "|---|---|---|---|---|---|"]
t = 0.0
for b in d["beats"]:
    s = b["shot"]
    pat = (s.get("remotion") or {}).get("pattern")
    if s.get("source") == "capture":
        vis = f"{s['type']} capture"
        segs = "; ".join(f"{g['start']:.2f}" + (f"-{g['end']:.2f}s" if "end" in g else "s→") +
                         ("" if g["speed"] == 1 else f" REPLAY {g['speed']}×") for g in s["segments"])
        src = f"{s['capture_file']} {segs} · crop {s.get('crop', 'none')} · label: {s['label']}"
    else:
        vis = pat
        props = s["remotion"]["props"]
        src = props.get("path") or s.get("figure") or props.get("segment") or props.get("artifactTitle") or props.get("title", "")
    rows.append(f"| {b['beat_id']} | {b['act']} | {b['actual_duration_s']:.2f} | {vis} | {src} | Liam (Kokoro am_onyx) |")
    t += b["actual_duration_s"]
rows += ["", f"Total narration: {t:.1f} s ({int(t // 60)}:{t % 60:04.1f}). 16:9, 3840x2160, 30 fps."]
(REEL / "SHOTLIST.md").write_text("\n".join(rows) + "\n", encoding="utf-8")
print(f"{len(d['beats'])} beats, {t:.1f}s")
