"""Generate OpenPose-format (COCO-18) skeleton images for a right-facing 2D fighter.

These are ControlNet *conditioning inputs*, not game art. Every pose is built by
forward kinematics from one fixed set of bone lengths, so proportions are
identical across all poses (the character sheet's consistency rule).

Angle convention (degrees, absolute, image space): 0 = down, 90 = forward
(right, the facing direction), 180 = up, -90 = back (left).
Near side (toward camera) = character's RIGHT; far side = LEFT (lead limbs).

Run:  python make_poses.py      -> poses/*.png, contact_sheet.png, poses.json
"""
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 512, 768
GROUND_Y = 720
STICK = 4  # limb half-thickness, same as controlnet_aux

# Fixed bone lengths in pixels (about 7.5 heads tall).
BONES = {
    "torso": 175,      # mid-hip -> neck
    "shoulder": 26,    # half shoulder width (3/4 view, compressed)
    "hip": 18,         # half hip width
    "upper_arm": 92,
    "forearm": 84,
    "thigh": 128,
    "shin": 122,
    "head": 44,        # neck -> nose along torso axis
}

# name: (torso, R arm (upper, lower), L arm, R leg (thigh, shin), L leg, airborne_px)
POSES = {
    "01_idle_stance": (172, (30, 165), (45, 160), (-22, -8), (22, 8), 0),
    "02_walk_forward": (175, (35, 165), (45, 160), (-25, -45), (30, 12), 0),
    "03_crouch": (163, (40, 172), (55, 165), (60, -20), (88, -5), 0),
    "04_jump_rising": (176, (100, 160), (120, 172), (80, -10), (102, 0), 170),
    "05_jump_falling": (178, (-105, -125), (110, 125), (-10, -20), (15, 2), 120),
    "06_punch_jab": (160, (30, 165), (92, 92), (-30, -12), (30, 10), 0),
    "07_high_kick": (196, (-60, -35), (40, 160), (-6, 0), (118, 112), 0),
    "08_block": (184, (78, 176), (68, 178), (-22, -8), (20, 6), 0),
    "09_hurt": (206, (-125, -150), (-60, -100), (-30, -18), (14, 0), 0),
    "10_ko_down": (-90, (-100, -82), (-78, -95), (95, 88), (122, 62), 0),
    "11_victory": (180, (172, 180), (30, -40), (-12, -4), (12, 4), 0),
}

# OpenPose COCO-18 limb pairs and colours (matches controlnet_aux draw_bodypose).
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


def scale(v, s):
    return (v[0] * s, v[1] * s)


def solve(pose):
    torso, r_arm, l_arm, r_leg, l_leg, air = pose
    t = vec(torso, 1.0)            # unit hip -> neck
    f = (-t[1], t[0])              # facing direction, perpendicular to torso
    hip = (0.0, 0.0)
    neck = add(hip, scale(t, BONES["torso"]))
    k = [None] * 18
    k[1] = neck
    k[2] = add(neck, scale(f, -BONES["shoulder"]))   # R shoulder (near)
    k[5] = add(neck, scale(f, BONES["shoulder"]))    # L shoulder (far)
    k[8] = add(hip, scale(f, -BONES["hip"]))         # R hip
    k[11] = add(hip, scale(f, BONES["hip"]))         # L hip
    for sh, el, wr, (ua, la) in ((2, 3, 4, r_arm), (5, 6, 7, l_arm)):
        k[el] = add(k[sh], vec(ua, BONES["upper_arm"]))
        k[wr] = add(k[el], vec(la, BONES["forearm"]))
    for hp, kn, an, (ta, sa) in ((8, 9, 10, r_leg), (11, 12, 13, l_leg)):
        k[kn] = add(k[hp], vec(ta, BONES["thigh"]))
        k[an] = add(k[kn], vec(sa, BONES["shin"]))
    k[0] = add(neck, scale(t, BONES["head"]), scale(f, 14))   # nose
    k[14] = add(k[0], scale(t, 9), scale(f, -8))              # R eye
    k[15] = add(k[0], scale(t, 9), scale(f, 2))               # L eye
    k[16] = add(neck, scale(t, 38), scale(f, -16))            # R ear (L ear hidden)

    # Place on the canvas: centre horizontally, lowest point on the ground line.
    xs = [p[0] for p in k if p]
    ys = [p[1] for p in k if p]
    dx = W / 2 - (min(xs) + max(xs)) / 2
    dy = GROUND_Y - max(ys) - air
    return [(p[0] + dx, p[1] + dy) if p else None for p in k]


def limb_polygon(a, b, half):
    (x1, y1), (x2, y2) = a, b
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    length = math.hypot(x2 - x1, y2 - y1) / 2
    ang = math.atan2(y2 - y1, x2 - x1)
    pts = []
    for i in range(0, 360, 10):
        t = math.radians(i)
        ex, ey = length * math.cos(t), half * math.sin(t)
        pts.append((mx + ex * math.cos(ang) - ey * math.sin(ang),
                    my + ex * math.sin(ang) + ey * math.cos(ang)))
    return pts


def draw(k):
    img = Image.new("RGB", (W, H), "black")
    d = ImageDraw.Draw(img)
    for i, (a, b) in enumerate(LIMBS):
        if k[a] and k[b]:
            c = tuple(int(v * 0.6) for v in COLORS[i])
            d.polygon(limb_polygon(k[a], k[b], STICK), fill=c)
    for i, p in enumerate(k):
        if p:
            d.ellipse((p[0] - 4, p[1] - 4, p[0] + 4, p[1] + 4), fill=COLORS[i])
    return img


def main():
    out = Path(__file__).parent
    (out / "poses").mkdir(exist_ok=True)
    thumbs = []
    record = {"canvas": [W, H], "ground_y": GROUND_Y, "bones": BONES, "poses": {}}
    for name, pose in POSES.items():
        k = solve(pose)
        img = draw(k)
        img.save(out / "poses" / f"{name}.png")
        thumbs.append((name, img))
        record["poses"][name] = {
            "angles": {"torso": pose[0], "r_arm": pose[1], "l_arm": pose[2],
                       "r_leg": pose[3], "l_leg": pose[4], "airborne_px": pose[5]},
            "keypoints": [[round(p[0], 1), round(p[1], 1)] if p else None for p in k],
        }
    (out / "poses.json").write_text(json.dumps(record, indent=2))

    cols, tw, th, label = 4, W // 2, H // 2, 28
    rows = math.ceil(len(thumbs) / cols)
    sheet = Image.new("RGB", (cols * tw, rows * (th + label)), (24, 24, 24))
    d = ImageDraw.Draw(sheet)
    font = ImageFont.load_default(size=16)
    for i, (name, img) in enumerate(thumbs):
        x, y = (i % cols) * tw, (i // cols) * (th + label)
        sheet.paste(img.resize((tw, th)), (x, y))
        d.line((x, y + (GROUND_Y // 2), x + tw, y + (GROUND_Y // 2)), fill=(70, 70, 70))
        d.text((x + 8, y + th + 5), name, fill="white", font=font)
    sheet.save(out / "contact_sheet.png")
    print(f"wrote {len(thumbs)} poses + contact_sheet.png")


if __name__ == "__main__":
    main()
