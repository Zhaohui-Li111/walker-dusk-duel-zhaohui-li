#!/usr/bin/env python3
"""Write SHOTLIST.md from beat_sheet.json (one row per beat: act, visual, source, timing)."""
import json, pathlib
REEL = pathlib.Path(__file__).resolve().parent.parent
d = json.loads((REEL / "beat_sheet.json").read_text(encoding="utf-8"))
rows = ["# SHOTLIST — " + d["metadata"]["title"], "",
        "Generated from beat_sheet.json by tools/build_shotlist.py. Times are measured narration "
        "(B13: the capture interval).", "",
        "| Beat | Act | s | Visual | Source / evidence | Audio |", "|---|---|---|---|---|---|"]
t = 0.0
for b in d["beats"]:
    s = b["shot"]
    pat = (s.get("remotion") or {}).get("pattern")
    if s.get("source") == "capture":
        vis = f"{s['type']} capture"
        src = (f"{s.get('capture_file')}" if s.get("capture") == "states"
               else f"capture/run-01.avi {s['capture_start_s']:.2f}-{s['capture_start_s'] + b['actual_duration_s']:.2f}s")
        src += f" · label: {s['label']}"
    else:
        vis = pat
        props = s["remotion"]["props"]
        src = props.get("path") or s.get("figure") or props.get("segment") or props.get("artifactTitle") or props.get("title", "")
    aud = "slice's own audio, no narration" if b["beat_id"] == "B13" else "Liam (Kokoro am_onyx)"
    rows.append(f"| {b['beat_id']} | {b['act']} | {b['actual_duration_s']:.2f} | {vis} | {src} | {aud} |")
    t += b["actual_duration_s"]
rows += ["", f"Total: {t:.1f} s ({int(t // 60)}:{t % 60:04.1f}). 16:9, 3840x2160, 30 fps."]
(REEL / "SHOTLIST.md").write_text("\n".join(rows) + "\n", encoding="utf-8")
print(f"{len(d['beats'])} beats, {t:.1f}s")
