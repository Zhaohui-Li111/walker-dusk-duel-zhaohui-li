#!/usr/bin/env python3
"""Build _qc/typecheck-masked/: a copy of the reel for GATE T in which the beats whose pictures
are diegetic (engine captures, pages of generation outputs) keep only OUR typography.

- capture clips: the game area (3072x1728 inset) is filled with the page colour
- B04/B05: the figure is the labels-only version (tools/build_figures.py --masked); the
  Remotion beat must then be re-rendered in the masked folder
- every beat is typed GRAPHIC so GATE T runs all pixel checks; patterns are kept, so each
  component keeps exactly the exemptions it has in the real reel
"""
import base64
import json
import pathlib
import shutil
import subprocess

REEL = pathlib.Path(__file__).resolve().parent.parent
M = REEL / "_qc" / "typecheck-masked"
MASK = "drawbox=x=384:y=216:w=3072:h=1728:color=0xFAF9F5:t=fill"


def main():
    (M / "media").mkdir(parents=True, exist_ok=True)
    sheet = json.loads((REEL / "beat_sheet.json").read_text(encoding="utf-8"))
    for b in sheet["beats"]:
        bid, shot = b["beat_id"], b["shot"]
        src = REEL / "media" / f"{bid}.mp4"
        dst = M / "media" / f"{bid}.mp4"
        if shot.get("source") == "capture":
            subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(src), "-vf", MASK,
                            "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p", str(dst)],
                           check=True)
        elif bid in ("B04", "B05"):
            fig = M / "figures" / pathlib.Path(shot["figure"]).name
            shot["remotion"]["props"]["image"] = "data:image/png;base64," + base64.b64encode(fig.read_bytes()).decode()
            dst.unlink(missing_ok=True)          # re-rendered from the masked props
        else:
            shutil.copy2(src, dst)
        if shot["type"] in ("VIDEO", "STILL"):
            shot["masked_from"] = shot["type"]
            shot["type"] = "GRAPHIC"
    sheet["metadata"]["note"] = ("MASKED COPY for GATE T only: game frames and generation images replaced by the "
                                 "page colour; designed typography only. Not a film.")
    (M / "beat_sheet.json").write_text(json.dumps(sheet, indent=1, ensure_ascii=False), encoding="utf-8")
    print("masked copy ready; render B04 and B05 in it, then run type_check.py on it")


if __name__ == "__main__":
    main()
