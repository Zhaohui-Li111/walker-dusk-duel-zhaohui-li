"""Design-stage pose tools for walker-dusk-duel (written by Claude Code, not a generative model).

For each fighter this builds every pose by forward kinematics from ONE fixed set of
bone lengths, so proportions are identical across poses. It writes:

  design/character/<fighter>/openpose/*.png   ControlNet OpenPose conditioning inputs (COCO-18)
  design/character/<fighter>/openpose_sheet.png  all skeletons on one canvas (for one-shot pose sheets)
  design/character/<fighter>/blocking.png     solid mannequin blocking of every pose, labeled
  design/character/<fighter>/collision.png    planned hurtbox (green) / hitbox (red) over each pose
  design/character/silhouette.png             both fighters, solid black, at real on-screen size
  design/character/poses.json                 every angle and keypoint, for reproduction

None of these images is game art. They are design specifications and control inputs.

Angle convention (degrees, absolute, image space): 0 = down, 90 = forward (right, the
facing direction), 180 = up, -90 = back. Near side (toward camera) = the fighter's RIGHT
limbs; far side = LEFT (lead) limbs. Fighters are drawn facing right; facing left is
flip_h at runtime.

Run from the project root:  python tools/make_poses.py
"""
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "design" / "character"

W, H = 832, 1216          # SDXL-friendly portrait bucket
GROUND_Y = 1150
VIEWPORT_H = 360          # Godot viewport height (640x360, 2x window)

FIGHTERS = {
    # P1, player. Stocky, ~5 heads tall, big fists. Topknot + headband tails.
    "akaken": {
        "label": "Akaken (P1, red fist)",
        "screen_height_px": 112,   # standing height in the 640x360 viewport
        "bones": {"head_r": 86, "neck_to_nose": 96, "torso": 285, "shoulder": 56,
                  "hip": 36, "upper_arm": 118, "forearm": 108, "thigh": 172, "shin": 162},
        "widths": {"arm": 54, "leg": 64, "fist_r": 36, "foot": 70},
        "feature": "topknot",
        "poses": {
            "01_idle_stance": (172, (30, 165), (45, 160), (-22, -8), (22, 8), 0),
            "02_walk_forward": (175, (35, 165), (45, 160), (-25, -45), (30, 12), 0),
            "03_crouch": (163, (40, 172), (55, 165), (60, -20), (88, -5), 0),
            "04_jump_rising": (176, (100, 160), (120, 172), (80, -10), (102, 0), 260),
            "05_jump_falling": (178, (-105, -125), (110, 125), (-10, -20), (15, 2), 160),
            "06_punch_jab": (160, (30, 165), (92, 92), (-30, -12), (30, 10), 0),
            "07_high_kick": (196, (-60, -35), (40, 160), (-6, 0), (118, 112), 0),
            "08_block": (184, (78, 176), (68, 178), (-22, -8), (20, 6), 0),
            "09_hurt": (206, (-125, -150), (-60, -100), (-30, -18), (14, 0), 0),
            "10_ko_down": (-90, (80, 95), (100, 70), (110, 65), (125, 55), 0),
            "11_victory": (180, (172, 180), (30, -40), (-12, -4), (12, 4), 0),
        },
    },
    # Opponent. Taller and leaner, ~5.5 heads, long legs. Wide straw hat + braid.
    "aotake": {
        "label": "Aotake (CPU, blue bamboo)",
        "screen_height_px": 124,
        "bones": {"head_r": 78, "neck_to_nose": 88, "torso": 300, "shoulder": 42,
                  "hip": 28, "upper_arm": 134, "forearm": 124, "thigh": 205, "shin": 195},
        "widths": {"arm": 44, "leg": 52, "fist_r": 26, "foot": 64},
        "feature": "hat",
        "poses": {
            "01_idle_stance": (176, (25, 170), (50, 158), (-18, -6), (24, 10), 0),
            "02_front_kick": (192, (-50, -20), (35, 165), (-4, 0), (100, 92), 0),
            "03_block": (182, (75, 176), (65, 178), (-18, -6), (20, 6), 0),
            "04_hurt": (204, (-120, -150), (-55, -100), (-28, -16), (14, 0), 0),
            "05_ko_down": (-90, (80, 95), (100, 70), (120, 45), (135, 35), 0),
        },
    },
}

LIMBS = [(1, 2), (1, 5), (2, 3), (3, 4), (5, 6), (6, 7), (1, 8), (8, 9), (9, 10),
         (1, 11), (11, 12), (12, 13), (1, 0), (0, 14), (14, 16), (0, 15), (15, 17)]
COLORS = [(255, 0, 0), (255, 85, 0), (255, 170, 0), (255, 255, 0), (170, 255, 0),
          (85, 255, 0), (0, 255, 0), (0, 255, 85), (0, 255, 170), (0, 255, 255),
          (0, 170, 255), (0, 85, 255), (0, 0, 255), (85, 0, 255), (170, 0, 255),
          (255, 0, 255), (255, 0, 170), (255, 0, 85)]


def vec(angle, length):
    a = math.radians(angle)
    return (math.sin(a) * length, math.cos(a) * length)


def add(p, *vs):
    x, y = p
    for vx, vy in vs:
        x, y = x + vx, y + vy
    return (x, y)


def mul(v, s):
    return (v[0] * s, v[1] * s)


def solve(b, pose):
    torso, r_arm, l_arm, r_leg, l_leg, air = pose
    t = vec(torso, 1.0)       # unit hip -> neck
    f = (-t[1], t[0])         # facing direction
    hip = (0.0, 0.0)
    neck = add(hip, mul(t, b["torso"]))
    k = [None] * 18
    k[1] = neck
    k[2] = add(neck, mul(f, -b["shoulder"]))
    k[5] = add(neck, mul(f, b["shoulder"]))
    k[8] = add(hip, mul(f, -b["hip"]))
    k[11] = add(hip, mul(f, b["hip"]))
    for sh, el, wr, (ua, la) in ((2, 3, 4, r_arm), (5, 6, 7, l_arm)):
        k[el] = add(k[sh], vec(ua, b["upper_arm"]))
        k[wr] = add(k[el], vec(la, b["forearm"]))
    for hp, kn, an, (ta, sa) in ((8, 9, 10, r_leg), (11, 12, 13, l_leg)):
        k[kn] = add(k[hp], vec(ta, b["thigh"]))
        k[an] = add(k[kn], vec(sa, b["shin"]))
    hr = b["head_r"]
    head_c = add(neck, mul(t, hr + 8), mul(f, 6))
    k[0] = add(neck, mul(t, b["neck_to_nose"]), mul(f, hr * 0.75))      # nose
    k[14] = add(k[0], mul(t, 22), mul(f, -26))                         # R eye (near)
    k[15] = add(k[0], mul(t, 22), mul(f, 2))                           # L eye (far)
    k[16] = add(head_c, mul(f, -hr * 0.45))                             # R ear; L ear hidden

    # Lowest point of the solid body (feet, head, fists) rests on the ground line.
    pts = [p for p in k if p] + [add(head_c, (0, hr)), add(head_c, (0, -hr))]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    dx = W / 2 - (min(xs) + max(xs)) / 2
    dy = GROUND_Y - max(ys) - air
    sh = lambda p: (p[0] + dx, p[1] + dy) if p else None
    return [sh(p) for p in k], sh(head_c), t, f


def limb_polygon(a, b, half):
    (x1, y1), (x2, y2) = a, b
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    length = math.hypot(x2 - x1, y2 - y1) / 2
    ang = math.atan2(y2 - y1, x2 - x1)
    pts = []
    for i in range(0, 360, 10):
        r = math.radians(i)
        ex, ey = length * math.cos(r), half * math.sin(r)
        pts.append((mx + ex * math.cos(ang) - ey * math.sin(ang),
                    my + ex * math.sin(ang) + ey * math.cos(ang)))
    return pts


def draw_openpose(k, d, ox=0, oy=0, s=1.0):
    off = lambda p: (ox + p[0] * s, oy + p[1] * s)
    for i, (a, b) in enumerate(LIMBS):
        if k[a] and k[b]:
            d.polygon(limb_polygon(off(k[a]), off(k[b]), 6 * s),
                      fill=tuple(int(v * 0.6) for v in COLORS[i]))
    for i, p in enumerate(k):
        if p:
            x, y = off(p)
            d.ellipse((x - 6 * s, y - 6 * s, x + 6 * s, y + 6 * s), fill=COLORS[i])


def thick(d, a, b, w, fill):
    d.line((a, b), fill=fill, width=int(w))
    for p in (a, b):
        d.ellipse((p[0] - w / 2, p[1] - w / 2, p[0] + w / 2, p[1] + w / 2), fill=fill)


def draw_body(d, fighter, k, head_c, t, f, fill):
    """Solid mannequin: a stand-in for the silhouette, not final art."""
    b, w = fighter["bones"], fighter["widths"]
    hr = b["head_r"]
    # far limbs first, then torso, then near limbs
    for hp, kn, an in ((11, 12, 13),):
        thick(d, k[hp], k[kn], w["leg"], fill); thick(d, k[kn], k[an], w["leg"] * 0.85, fill)
        thick(d, k[an], add(k[an], mul(f, w["foot"] * 0.6)), w["leg"] * 0.5, fill)
    for sh, el, wr in ((5, 6, 7),):
        thick(d, k[sh], k[el], w["arm"], fill); thick(d, k[el], k[wr], w["arm"] * 0.9, fill)
        d.ellipse((k[wr][0] - w["fist_r"], k[wr][1] - w["fist_r"],
                   k[wr][0] + w["fist_r"], k[wr][1] + w["fist_r"]), fill=fill)
    torso = [k[2], k[5], k[11], k[8]]
    pad = b["head_r"] * 0.55 - b["shoulder"] * 0.3
    torso =[add(p, mul(f, (-1 if i in (0, 3) else 1) * pad)) for i, p in enumerate(torso)]
    d.polygon(torso, fill=fill)
    thick(d, k[1], add(k[1], mul(t, 30)), b["shoulder"] * 0.8, fill)
    d.ellipse((head_c[0] - hr, head_c[1] - hr, head_c[0] + hr, head_c[1] + hr), fill=fill)
    if fighter["feature"] == "topknot":
        top = add(head_c, mul(t, hr + 22), mul(f, -10))
        d.ellipse((top[0] - 28, top[1] - 28, top[0] + 28, top[1] + 28), fill=fill)
        tail0 = add(head_c, mul(f, -hr * 0.9), mul(t, hr * 0.3))
        thick(d, tail0, add(tail0, mul(f, -70), mul(t, -30)), 16, fill)
        thick(d, tail0, add(tail0, mul(f, -60), mul(t, 5)), 14, fill)
    else:  # wide straw hat + braid
        brim_c = add(head_c, mul(t, hr * 0.55))
        brim = [add(brim_c, mul(f, -hr * 1.9)), add(brim_c, mul(t, hr * 0.95)),
                add(brim_c, mul(f, hr * 1.9))]
        d.polygon(brim, fill=fill)
        b0 = add(head_c, mul(f, -hr * 0.8))
        thick(d, b0, add(b0, mul(t, -hr * 2.2), mul(f, -20)), 18, fill)
    for hp, kn, an in ((8, 9, 10),):
        thick(d, k[hp], k[kn], w["leg"], fill); thick(d, k[kn], k[an], w["leg"] * 0.85, fill)
        thick(d, k[an], add(k[an], mul(f, w["foot"] * 0.6)), w["leg"] * 0.5, fill)
    for sh, el, wr in ((2, 3, 4),):
        thick(d, k[sh], k[el], w["arm"], fill); thick(d, k[el], k[wr], w["arm"] * 0.9, fill)
        d.ellipse((k[wr][0] - w["fist_r"], k[wr][1] - w["fist_r"],
                   k[wr][0] + w["fist_r"], k[wr][1] + w["fist_r"]), fill=fill)


def boxes(fighter, name, k, head_c):
    """Planned collision: one hurtbox per pose (body core, no fists/feet/hat/braid),
    plus a hitbox on the striking limb for attack poses. Canvas pixels."""
    hr = fighter["bones"]["head_r"]
    hipx = (k[8][0] + k[11][0]) / 2
    if "ko_down" in name:
        return None, None
    core = [k[1], k[2], k[5], k[8], k[11], head_c]
    core_y = [p[1] for p in core]
    top = head_c[1] - hr * 0.9
    feet = max(k[10][1], k[13][1])
    half_w = hr * 1.05
    cx = (hipx + k[1][0]) / 2
    hurt = (cx - half_w, min(top, min(core_y)), cx + half_w, feet)
    hit = None
    r = fighter["widths"]["fist_r"] * 1.2
    if "punch" in name:
        p = k[7]; hit = (p[0] - r, p[1] - r, p[0] + r * 1.2, p[1] + r)
    if "kick" in name:
        p = k[13]; hit = (p[0] - r * 1.2, p[1] - r * 1.2, p[0] + r * 1.6, p[1] + r * 1.2)
    return hurt, hit


def labeled_grid(tiles, cols, title, font, tfont):
    tw, th, lab = W // 3, H // 3, 30
    rows = math.ceil(len(tiles) / cols)
    sheet = Image.new("RGB", (cols * tw, rows * (th + lab) + 44), (245, 242, 235))
    d = ImageDraw.Draw(sheet)
    d.text((10, 10), title, fill=(20, 20, 20), font=tfont)
    for i, (name, img) in enumerate(tiles):
        x, y = (i % cols) * tw, 44 + (i // cols) * (th + lab)
        sheet.paste(img.resize((tw, th), Image.LANCZOS), (x, y))
        d.text((x + 8, y + th + 6), name, fill=(20, 20, 20), font=font)
    return sheet


def main():
    font = ImageFont.load_default(size=16)
    tfont = ImageFont.load_default(size=22)
    record = {"canvas": [W, H], "ground_y": GROUND_Y, "angle_convention":
              "0=down, 90=forward/right, 180=up, -90=back; near side = fighter's right",
              "fighters": {}}
    sil_row = []
    for fid, fighter in FIGHTERS.items():
        fdir = OUT / fid
        (fdir / "openpose").mkdir(parents=True, exist_ok=True)
        rec = {"label": fighter["label"], "bones": fighter["bones"],
               "widths": fighter["widths"], "screen_height_px": fighter["screen_height_px"],
               "poses": {}}
        op_tiles, block_tiles, col_tiles = [], [], []
        idle_height = None
        for name, pose in fighter["poses"].items():
            k, head_c, t, f = solve(fighter["bones"], pose)
            op = Image.new("RGB", (W, H), "black")
            draw_openpose(k, ImageDraw.Draw(op))
            op.save(fdir / "openpose" / f"{name}.png")
            op_tiles.append((name, op))

            blk = Image.new("RGB", (W, H), "white")
            bd = ImageDraw.Draw(blk)
            bd.line((0, GROUND_Y, W, GROUND_Y), fill=(180, 180, 180), width=3)
            draw_body(bd, fighter, k, head_c, t, f, (25, 25, 25))
            block_tiles.append((name, blk))

            col = Image.new("RGB", (W, H), "white")
            cd = ImageDraw.Draw(col)
            draw_body(cd, fighter, k, head_c, t, f, (170, 170, 170))
            hurt, hit = boxes(fighter, name, k, head_c)
            if hurt:
                cd.rectangle(hurt, outline=(0, 160, 60), width=8)
            if hit:
                cd.rectangle(hit, outline=(220, 30, 30), width=8)
            if not hurt:
                cd.text((40, 60), "no hurtbox (KO)", fill=(0, 120, 40), font=tfont)
            col_tiles.append((name, col))

            if name.startswith("01_"):
                # measure standing height for the silhouette scale
                mask = Image.new("L", (W, H), 0)
                draw_body(ImageDraw.Draw(mask), fighter, k, head_c, t, f, 255)
                bbox = mask.getbbox()
                idle_height = bbox[3] - bbox[1]
                scale = fighter["screen_height_px"] / idle_height
                small = blk.crop(bbox).resize(
                    (max(1, round((bbox[2] - bbox[0]) * scale)), fighter["screen_height_px"]),
                    Image.LANCZOS)
                sil_row.append((fighter["label"], small, scale))
            rec["poses"][name] = {
                "angles": {"torso": pose[0], "r_arm": pose[1], "l_arm": pose[2],
                           "r_leg": pose[3], "l_leg": pose[4], "airborne_px": pose[5]},
                "keypoints": [[round(p[0], 1), round(p[1], 1)] if p else None for p in k],
                "hurtbox": [round(v, 1) for v in hurt] if hurt else None,
                "hitbox": [round(v, 1) for v in hit] if hit else None,
            }
        rec["canvas_idle_height_px"] = idle_height
        rec["canvas_to_screen_scale"] = round(fighter["screen_height_px"] / idle_height, 4)
        record["fighters"][fid] = rec

        cols = 4
        labeled_grid(block_tiles, cols, f"{fighter['label']} - pose blocking (mannequin, not art)",
                     font, tfont).save(fdir / "blocking.png")
        labeled_grid(col_tiles, cols, f"{fighter['label']} - green: hurtbox, red: hitbox",
                     font, tfont).save(fdir / "collision.png")
        # all skeletons on one canvas for a one-shot pose sheet (ControlNet input)
        n = len(op_tiles)
        rows = math.ceil(n / cols)
        sheet = Image.new("RGB", (cols * W // 2, rows * H // 2), "black")
        sd = ImageDraw.Draw(sheet)
        for i, (name, _) in enumerate(op_tiles):
            k, *_ = solve(fighter["bones"], fighter["poses"][name])
            draw_openpose(k, sd, (i % cols) * W // 2, (i // cols) * H // 2, 0.5)
        sheet.save(fdir / "openpose_sheet.png")

    # Silhouette test: real on-screen pixels, shown 1:1 and magnified 4x (nearest).
    gap = 24
    w1 = sum(s.width for _, s, _ in sil_row) + gap * (len(sil_row) + 1)
    one = Image.new("RGB", (w1, 140), "white")
    x = gap
    for _, s, _ in sil_row:
        one.paste(s, (x, 140 - 8 - s.height)); x += s.width + gap
    big = one.resize((one.width * 4, one.height * 4), Image.NEAREST)
    canvas = Image.new("RGB", (max(big.width + 40, 900), big.height + one.height + 120), "white")
    cd = ImageDraw.Draw(canvas)
    cd.text((20, 10), "Silhouette test - 1:1 at 640x360 viewport scale (top), 4x nearest (bottom)",
            fill="black", font=tfont)
    canvas.paste(one, (20, 44))
    canvas.paste(big, (20, 44 + one.height + 30))
    canvas.save(OUT / "silhouette.png")
    (OUT / "poses.json").write_text(json.dumps(record, indent=2))
    print("ok:", ", ".join(f"{k} {len(v['poses'])} poses" for k, v in record["fighters"].items()))


if __name__ == "__main__":
    main()
