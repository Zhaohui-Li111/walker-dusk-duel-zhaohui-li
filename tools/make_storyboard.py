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
    design_panels(font)


CREAM, INK = (0xF2, 0xE6, 0xD0, 255), (0x1E, 0x1B, 0x22, 255)


def draw_details(d, fid, k, head_c, t, f, eyes_closed):
    """Close-up details from the character sheet: wrapped fists, headband, eye."""
    fighter = mp.FIGHTERS[fid]
    hr, fr = fighter["bones"]["head_r"], fighter["widths"]["fist_r"]
    if fid == "akaken":
        for wr in (7, 4):
            x, y = k[wr]
            d.ellipse((x - fr, y - fr, x + fr, y + fr), fill=CREAM, outline=INK, width=4)
        a, b = mp.add(head_c, mp.mul(f, -hr), mp.mul(t, hr * 0.3)), mp.add(head_c, mp.mul(f, hr), mp.mul(t, hr * 0.3))
        mp.thick(d, a, b, 22, CREAM)
    eye = mp.add(head_c, mp.mul(f, hr * 0.5), mp.mul(t, hr * 0.05))
    if eyes_closed:
        d.line((eye[0] - 14, eye[1] - 6, eye[0] + 14, eye[1] + 6), fill=INK, width=6)
    else:
        d.ellipse((eye[0] - 9, eye[1] - 12, eye[0] + 9, eye[1] + 12), fill=INK)


def big_sprite(fid, pose_name, height_px, face_left=False, detail=False):
    """Mannequin rendered so its full canvas is height_px tall (for design-view panels)."""
    fighter = mp.FIGHTERS[fid]
    k, head_c, t, f = mp.solve(fighter["bones"], fighter["poses"][pose_name])
    img = Image.new("RGBA", (mp.W, mp.H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    mp.draw_body(d, fighter, k, head_c, t, f, FILL[fid] + (255,))
    if detail:
        draw_details(d, fid, k, head_c, t, f, eyes_closed="ko" in pose_name)
    img = img.crop(img.getbbox())
    s = height_px / img.height
    img = img.resize((round(img.width * s), height_px), Image.LANCZOS)
    return ImageOps.mirror(img) if face_left else img


def design_panels(font):
    """Design views (not the gameplay camera): P1 high angle, P2 low angle, P6 Dutch close-up."""
    big = ImageFont.load_default(size=64)

    # P1 - wide, high angle: looking down into the courtyard from the temple roof.
    img = Image.new("RGB", (PW, PH), SKY)
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, PW, 120), fill=WALL)                       # far wall, seen from above: a thin strip
    d.polygon([(0, 120), (PW, 120), (PW, PH), (0, PH)], fill=FLOOR)
    for i in range(1, 7):                                          # paving lines converge toward the far wall
        y = 120 + (PH - 120) * (i / 7) ** 1.4
        d.line((0, y, PW, y), fill=(0x3A, 0x35, 0x44), width=2)
    for x in range(-600, PW + 600, 160):
        d.line((PW / 2 + (x - PW / 2) * 0.35, 120, x, PH), fill=(0x3A, 0x35, 0x44), width=2)
    for x, y in ((150, 230), (1130, 230), (150, 560), (1130, 560)):  # lanterns on posts, seen from above
        d.ellipse((x - 34, y - 34, x + 34, y + 34), fill=(0xF2, 0xA5, 0x41))
    for fid, pose, x, left in (("akaken", "01_idle_stance", 520, False), ("aotake", "01_idle_stance", 760, True)):
        s = big_sprite(fid, pose, 150, left)
        s = s.resize((s.width, round(s.height * 0.62)))            # foreshortened from above
        d.ellipse((x - 50, 455, x + 50, 485), fill=(0x22, 0x1F, 0x29))
        img.paste(s, (x - s.width // 2, 470 - s.height), s)
    d.text((PW / 2, 220), "DUSK DUEL", fill=(240, 236, 228), font=big, anchor="mm")
    d.text((PW / 2, 290), "press Enter", fill=(240, 236, 228), font=font, anchor="mm")
    label(d, font, "P1 wide - high angle (from the temple roof) - design view: title   [Claude drawing, not art]")
    img.save(OUT / "01-title.png")

    # P2 - medium, low angle: camera at knee height looking up at Akaken.
    img = Image.new("RGB", (PW, PH), SKY)
    d = ImageDraw.Draw(img)
    d.rectangle((0, 470, PW, PH), fill=WALL)                        # wall top is low in frame: camera is low
    d.rectangle((0, 640, PW, PH), fill=FLOOR)
    for x in (220, 1060):
        d.line((x, 0, x, 300), fill=(20, 20, 20), width=6)
        d.ellipse((x - 46, 300, x + 46, 400), fill=(0xF2, 0xA5, 0x41))
    s = big_sprite("akaken", "01_idle_stance", 980, detail=True)
    w, h = s.size
    a = w * 0.10                                                    # head farther from a low camera -> narrower top
    s = s.transform((w, h), Image.QUAD, (-a, 0, 0, h, w, h, w + a, 0), Image.BICUBIC)
    img.paste(s, (PW // 2 - w // 2, 40), s)                         # medium shot: cropped at the thighs by the frame
    d.text((1000, 560), "FIGHT", fill=(240, 236, 228), font=big, anchor="mm")
    label(d, font, "P2 medium - low angle (knee height, looking up) - design view: fighter intro   [Claude drawing, not art]")
    img.save(OUT / "02-intro.png")

    # P6 - close-up, Dutch tilt: Akaken's head on the stone floor at KO.
    tilt = Image.new("RGB", (PW * 2, PH * 2), FLOOR)
    td = ImageDraw.Draw(tilt)
    td.rectangle((0, 0, PW * 2, PH * 2 - 760), fill=WALL)
    for x in range(0, PW * 2, 260):                                 # floor slab joints
        td.line((x, PH * 2 - 760, x - 120, PH * 2), fill=(0x3A, 0x35, 0x44), width=6)
    s = big_sprite("akaken", "10_ko_down", 430, detail=True)
    tilt.paste(s, (PW - 330, PH * 2 - 760 - s.height + 215), s)
    tilt = tilt.rotate(15, resample=Image.BICUBIC, center=(PW, PH))
    img = tilt.crop((PW // 2, PH // 2, PW // 2 + PW, PH // 2 + PH))
    d = ImageDraw.Draw(img)
    d.text((PW - 260, 150), "K.O.", fill=(240, 236, 228), font=ImageFont.load_default(size=110), anchor="mm")
    label(d, font, "P6 close-up - Dutch tilt 15 deg - design view: KO transition (held frame)   [Claude drawing, not art]")
    img.save(OUT / "06-ko-closeup.png")
    print("wrote 3 design-view panels")


if __name__ == "__main__":
    main()
