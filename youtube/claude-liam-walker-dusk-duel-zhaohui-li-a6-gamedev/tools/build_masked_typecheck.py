#!/usr/bin/env python3
"""Build _qc/typecheck-masked/: a copy of the reel for GATE T in which the beats whose pictures are
diegetic (engine captures, Zhaohui's screenshots, MCP look renders) keep only OUR typography.
Adapted from the A2 reel's tool.

- capture clips: the game area (3072x1728 inset) is filled with the page colour
- STILL figure beats: the figure is the labels-only version (tools/build_figures.py --masked); the
  Remotion beat is then re-rendered in the masked folder
- every beat is typed GRAPHIC so GATE T runs all pixel checks; patterns are kept, so each component
  keeps exactly the exemptions it has in the real reel
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
    for d in ("mp3",):
        if (M / d).exists():
            shutil.rmtree(M / d)
        shutil.copytree(REEL / d, M / d)
    sheet = json.loads((REEL / "beat_sheet.json").read_text(encoding="utf-8"))
    rerender = []
    for b in sheet["beats"]:
        bid, shot = b["beat_id"], b["shot"]
        src = REEL / "media" / f"{bid}.mp4"
        dst = M / "media" / f"{bid}.mp4"
        if shot.get("source") == "capture":
            subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(src), "-vf", MASK,
                            "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p", str(dst)],
                           check=True)
        elif shot["type"] == "STILL" and shot.get("figure"):
            fig = M / "figures" / pathlib.Path(shot["figure"]).name
            shot["remotion"]["props"]["image"] = "data:image/png;base64," + base64.b64encode(fig.read_bytes()).decode()
            dst.unlink(missing_ok=True)          # re-rendered from the masked props
            rerender.append(bid)
        else:
            shutil.copy2(src, dst)
        if shot["type"] in ("VIDEO", "STILL"):
            shot["masked_from"] = shot["type"]
            shot["type"] = "GRAPHIC"
    sheet["metadata"]["note"] = ("MASKED COPY for GATE T only: game frames, screenshots and MCP renders replaced by "
                                 "the page colour; designed typography only. Not a film.")
    (M / "beat_sheet.json").write_text(json.dumps(sheet, indent=1, ensure_ascii=False), encoding="utf-8")
    print("masked copy ready; re-render in it:", " ".join(rerender), "— then run type_check.py on it")


if __name__ == "__main__":
    main()
