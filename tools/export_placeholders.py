"""Export Claude-drawn placeholder state images for Godot, and copy poses.json into the project.

Placeholders are the pose mannequins (tools/make_poses.py) at real on-screen size, on the SAME
full canvas the generated images will use, so swapping a placeholder for a generated export is
file-for-file with no change in alignment. They are not generated assets.

  godot/art/placeholder/<fighter>/<state>.png
  godot/data/poses.json

Run from the project root:  python tools/export_placeholders.py
"""
import shutil

from PIL import Image, ImageDraw

import make_poses as mp
import make_storyboard as sb

STATES = {
    "akaken": {"idle": "01_idle_stance", "walk": "02_walk_forward", "crouch": "03_crouch",
               "rise": "04_jump_rising", "fall": "05_jump_falling", "punch": "06_punch_jab",
               "kick": "07_high_kick", "block": "08_block", "hurt": "09_hurt", "ko": "10_ko_down",
               "win": "11_victory"},
    "aotake": {"idle": "01_idle_stance", "kick": "02_front_kick", "block": "03_block",
               "hurt": "04_hurt", "ko": "05_ko_down"},
}


def main():
    godot = mp.ROOT / "godot"
    record = mp.json.loads((mp.OUT / "poses.json").read_text())
    for fid, states in STATES.items():
        fighter = mp.FIGHTERS[fid]
        s = record["fighters"][fid]["canvas_to_screen_scale"]
        out = godot / "art" / "placeholder" / fid
        out.mkdir(parents=True, exist_ok=True)
        for state, stem in states.items():
            k, head_c, t, f = mp.solve(fighter["bones"], fighter["poses"][stem])
            img = Image.new("RGBA", (mp.W, mp.H), (0, 0, 0, 0))
            d = ImageDraw.Draw(img)
            mp.draw_body(d, fighter, k, head_c, t, f, sb.FILL[fid] + (255,))
            sb.draw_details(d, fid, k, head_c, t, f, eyes_closed=(state == "ko"))
            img.resize((round(mp.W * s), round(mp.H * s)), Image.LANCZOS).save(out / f"{state}.png")
        record["fighters"][fid]["states"] = states
    (godot / "data").mkdir(parents=True, exist_ok=True)
    (godot / "data" / "poses.json").write_text(mp.json.dumps(record, indent=1))
    print("placeholders:", {k: len(v) for k, v in STATES.items()}, "-> godot/art/placeholder/")


if __name__ == "__main__":
    main()
