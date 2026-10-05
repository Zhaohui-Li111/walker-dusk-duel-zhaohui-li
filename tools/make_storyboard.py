"""Blocking thumbnails for the GAMEPLAY storyboard panels (16:9, fixed side camera, eye level).

Written by Claude Code. These are layout aids built from the pose mannequins in
make_poses.py, not game art and not generated assets. Design-view panels (title,
fighter intro, KO close-up) are meant to be hand-sketched and are not drawn here.

Run from the project root:  python tools/make_storyboard.py
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

import make_poses as mp

OUT = mp.ROOT / "design" / "storyboard"
PW, PH = 1280, 720            # panel = 2x the 640x360 viewport
FLOOR_Y = 610
WALL, SKY, FLOOR = (0x3A, 0x33, 0x47), (0x5A, 0x47, 0x66), (0x2B, 0x27, 0x33)
FILL = {"akaken": (0xD9, 0x48, 0x2B), "aotake": (0x2F, 0xA3, 0xB0)}


def fighter_sprite(fid, pose_name, face_left=False):
    fighter = mp.FIGHTERS[fid]
    k, head_c, t, f = mp.solve(fighter["bones"], fighter["poses"][pose_name])
    img = Image.new("RGBA", (mp.W, mp.H), (0, 0, 0, 0))
    mp.draw_body(ImageDraw.Draw(img), fighter, k, head_c, t, f, FILL[fid] + (255,))
    # same canvas->screen scale as the silhouette test, doubled for the 1280 panel
    rec_scale = fighter["screen_height_px"] * 2 / 820
    img = img.resize((round(mp.W * rec_scale), round(mp.H * rec_scale)), Image.LANCZOS)
    return ImageOps.mirror(img) if face_left else img


def base(font):
    img = Image.new("RGB", (PW, PH), SKY)
    d = ImageDraw.Draw(img)
    d.rectangle((0, 200, PW, FLOOR_Y), fill=WALL)
    for x in (140, 1140):                                   # lanterns
        d.line((x, 200, x, 250), fill=(20, 20, 20), width=4)
        d.ellipse((x - 26, 250, x + 26, 310), fill=(0xF2, 0xA5, 0x41))
    d.rectangle((0, FLOOR_Y, PW, PH), fill=FLOOR)
    return img, d


def hud(d, font, p1=1.0, p2=1.0, text=None):
    for x0, hp, name in ((40, p1, "AKAKEN"), (PW - 540, p2, "AOTAKE")):
        d.rectangle((x0, 30, x0 + 500, 58), outline=(240, 240, 240), width=3)
        w = int(494 * hp)
        if x0 > PW / 2:
            d.rectangle((x0 + 3 + 494 - w, 33, x0 + 497, 55), fill=(0xF5, 0xC5, 0x42))
        else:
            d.rectangle((x0 + 3, 33, x0 + 3 + w, 55), fill=(0xF5, 0xC5, 0x42))
        d.text((x0, 64), name, fill=(240, 240, 240), font=font)
    if text:
        d.text((PW / 2, 150), text, fill=(240, 240, 240), font=font, anchor="mm")


def place(img, sprite, x_center):
    img.paste(sprite, (int(x_center - sprite.width / 2), FLOOR_Y + 12 - sprite.height), sprite)


def spark(d, x, y, color=(255, 255, 255)):
    for dx, dy in ((40, 0), (-40, 0), (0, 40), (0, -40), (28, 28), (-28, -28), (28, -28), (-28, 28)):
        d.line((x, y, x + dx, y + dy), fill=color, width=6)


def label(d, font, text):
    d.rectangle((0, PH - 44, PW, PH), fill=(15, 15, 15))
    d.text((16, PH - 34), text, fill=(240, 240, 240), font=font)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    font = ImageFont.load_default(size=26)
    panels = {
        "03-first-exchange": (("akaken", "06_punch_jab", 520), ("aotake", "03_block", 800),
                              1.0, 1.0, None, (690, None), "P3 wide - eye level - gameplay: jab meets block"),
        "04-clean-hit": (("akaken", "07_high_kick", 500), ("aotake", "04_hurt", 680),
                         1.0, 0.7, None, (600, "hit"), "P4 wide - eye level - gameplay: kick lands"),
        "05-taking-a-hit": (("akaken", "09_hurt", 500), ("aotake", "02_front_kick", 690),
                            0.65, 0.7, None, (560, "hit"), "P5 wide - eye level - gameplay: player is hit"),
        "07-rematch": (("akaken", "01_idle_stance", 400), ("aotake", "01_idle_stance", 880),
                       1.0, 1.0, "ROUND 2  -  FIGHT", None, "P7 wide - eye level - gameplay: reset and retry"),
        "08-victory": (("akaken", "11_victory", 470), ("aotake", "05_ko_down", 860),
                       0.4, 0.0, "AKAKEN WINS  -  Enter: rematch   Esc: quit", None,
                       "P8 wide - eye level - gameplay: session end"),
    }
    for name, (a, b, hp1, hp2, text, fx, cap) in panels.items():
        img, d = base(font)
        place(img, fighter_sprite(a[0], a[1]), a[2])
        place(img, fighter_sprite(b[0], b[1], face_left=True), b[2])
        hud(d, font, hp1, hp2, text)
        if fx and fx[1] == "hit":
            spark(d, fx[0], 460)
        elif fx:
            d.rectangle((fx[0] - 10, 330, fx[0] + 10, 430), outline=(200, 220, 255), width=5)
        label(d, font, cap + "   [Claude blocking thumbnail, not art]")
        img.save(OUT / f"{name}.png")
    print("wrote", len(panels), "gameplay blocking panels")


if __name__ == "__main__":
    main()
