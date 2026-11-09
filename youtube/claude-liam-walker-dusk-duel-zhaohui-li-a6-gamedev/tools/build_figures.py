#!/usr/bin/env python3
"""Lay out the A6 film's figure stills from files already in the repo (no new art).

Adapted from the A5 reel's tool. Engine panels are the committed Movie Maker strips in
captures/hit_spark/ and captures/embers/ (fixture captures of godot/previews/, 1280 x 720, fixed
seed), pasted unchanged except for cropping and nearest-neighbour enlargement, and bg.png (the
game's own background). Numbers, quotes and code are copied from CHANGE-BRIEF.md, TUNING.md,
TEST-REPORT.md, FRICTIONAL.md, the logs and the source files. The only new pixels are labels,
frames, sample rings, a rectangle showing the emission rect, and one clearly labelled diagnostic
panel (pixels that differ from the bare frame). Every source and its SHA-256 goes to
figures/figures.json for SOURCES.md.   python tools/build_figures.py [--masked]
"""
import hashlib
import json
import pathlib
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

REEL = pathlib.Path(__file__).resolve().parent.parent
REPO = REEL.parent.parent
MASKED = "--masked" in sys.argv
OUT = REEL / ("_qc/typecheck-masked/figures" if MASKED else "figures")
PAGE = (255, 253, 248)
CARD = (255, 255, 255)
RULE = (204, 198, 186)
INK = (61, 57, 41)
SOFT = (110, 100, 86)
ACCENT = (217, 119, 87)
WARN = (164, 74, 50)
GOOD = (60, 110, 70)
W, H = 3200, 1160
used = {}
SPARK = "captures/hit_spark"
EMB = "captures/embers"
DARK = (728, 404)        # brief's dark point (364, 202) in the 1280 x 720 capture
LANT = (1020, 416)       # brief's lantern point (510, 208)


def font(size, bold=False, mono=False):
    if mono:
        return ImageFont.truetype("C:/Windows/Fonts/consolab.ttf" if bold else "C:/Windows/Fonts/consola.ttf", size)
    return ImageFont.truetype("C:/Windows/Fonts/seguisb.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf", size)


def cjk(s):
    return any("\u3000" <= ch <= "\u9fff" or "\uff00" <= ch <= "\uffef" for ch in s)


def src(rel, mask=True):
    p = REPO / rel
    used[rel] = hashlib.sha256(p.read_bytes()).hexdigest()
    img = Image.open(p).convert("RGB")
    return Image.new("RGB", img.size, PAGE) if (MASKED and mask) else img


def text(d, s, x, y, w, size=54, color=INK, bold=False, mono=False, align="center"):
    if cjk(s):     # Zhaohui's Chinese: Segoe UI has no CJK glyphs
        f = ImageFont.truetype("C:/Windows/Fonts/msyhbd.ttc" if bold else "C:/Windows/Fonts/msyh.ttc", size)
    else:
        f = font(size, bold, mono)
    tw = d.textlength(s, font=f)
    xx = x + (w - tw) / 2 if align == "center" else x
    d.text((xx, y), s, font=f, fill=color)
    return tw


def frame(d, ox, oy, img, color=INK, width=4):
    d.rectangle([ox - width, oy - width, ox + img.width + width - 1, oy + img.height + width - 1],
                outline=color, width=width)


def card(d, x, y, w, h, outline=RULE):
    d.rounded_rectangle([x, y, x + w, y + h], radius=22, fill=CARD, outline=outline, width=4)


def new():
    page = Image.new("RGB", (W, H), PAGE)
    return page, ImageDraw.Draw(page)


def save(page, name):
    page.save(OUT / name)


def crop_zoom(rel, c, half, size):
    img = src(rel).crop((c[0] - half, c[1] - half, c[0] + half, c[1] + half))
    return img.resize((size, size), Image.NEAREST)


def strip_row(page, d, run, centre, frames, y, size, x0=40, gap=12, label=True):
    for i, f in enumerate(frames):
        im = crop_zoom(f"{SPARK}/{run}/frame{f:08d}.png", centre, 60, size)
        x = x0 + i * (size + gap)
        page.paste(im, (x, y))
        frame(d, x, y, im, RULE, 3)
        if label:
            text(d, f"frame {f}", x, y + size + 6, size, 34, SOFT)


# ---------------------------------------------------------------- Effect A

def fig_intent_a():
    """CHANGE-BRIEF.md Effect A: event, intent block, against the real hit band of bg.png."""
    page, d = new()
    card(d, 40, 20, W - 80, 170)
    text(d, "EVENT  Fighter.attack_resolved(fighter, kind, result, point)   ·   result == \"hit\"   ·   at point",
         40, 40, W - 80, 52, INK, mono=True)
    text(d, "fighter.gd:19, emitted in _resolve() :221-223; point = centre of hitbox ∩ hurtbox (:170)", 40, 115, W - 80, 40, SOFT)
    bg = src("godot/art/env/bg.png")
    band = bg.crop((0, 180, 640, 280)).resize((1920, 300), Image.NEAREST)
    page.paste(band, (40, 230))
    frame(d, 40, 230, band)
    if not MASKED:
        for (vx, vy), lab in (((364, 202), "dark  L 0.0040"), ((510, 208), "lantern  L 0.2699")):
            px, py = 40 + vx * 3, 230 + (vy - 180) * 3
            d.ellipse([px - 26, py - 26, px + 26, py + 26], outline=ACCENT, width=6)
            text(d, lab, px - 300, 230 + 300 + 8, 600, 38, WARN, bold=True)
    text(d, "bg.png, the hit band (viewport y 180–280, enlarged 3×): where hits land, y ≈ 224–254", 40, 590, 1920, 38, SOFT)
    rows = [("First frame", "bright, compact flash at the hit point"),
            ("0 – 0.2 s", "sparks travel outward"),
            ("to 0.6 s", "slow, shrink and fade (lifetime 0.60 s)"),
            ("Colour", "#EAFBFF → pale cyan #83DFF2, additive"),
            ("Contrast", "13.1 : 1 band mean · 3.0 : 1 brightest lantern"),
            ("Scale", "burst radius 15–30 px (13–27 % of Akaken's 112 px)"),
            ("Emitters", "4 pooled one-shot slots × 20 = 80 max")]
    for i, (k, v) in enumerate(rows):
        y = 230 + i * 118
        card(d, 2000, y, 1160, 104)
        text(d, k, 2020, y + 26, 300, 42, ACCENT, bold=True, align="left")
        text(d, v, 2300, y + 30, 850, 36, INK, align="left")
    card(d, 40, 660, 1920, 460)
    text(d, "the intent block, Zhaohui's (brief committed efa8d71, before any build)", 40, 690, 1920, 44, SOFT)
    for i, s in enumerate(["“The hit spark provides immediate visual confirmation",
                           "that an attack connected, making the exact contact point",
                           "and impact strength easier to read.”",
                           "Kept beside the existing code-drawn spark in effects.gd (out of scope)."]):
        text(d, s, 40, 770 + i * 80, 1920, 50 if i < 3 else 40, INK if i < 3 else SOFT, bold=(i < 3))
    save(page, "fig_intent_a.png")


def fig_strip_a_r0():
    """TUNING.md Effect A r0: both strips, and Zhaohui's first look, verbatim, with the correction."""
    page, d = new()
    frames = [10, 12, 15, 20, 22, 24, 28, 30, 40, 50]
    size = 300
    text(d, "dark wall (364, 202)", 40, 6, 600, 40, INK, bold=True, align="left")
    strip_row(page, d, "r0", DARK, frames, 56, size)
    text(d, "next to the lantern (510, 208)", 40, 410, 800, 40, INK, bold=True, align="left")
    strip_row(page, d, "r0-lantern", LANT, frames, 460, size)
    text(d, "FIXTURE CAPTURE · godot/previews/hit_spark_preview.tscn · fixed seed · Movie Maker 30 fps · crops 120 px enlarged 2.5×",
         0, 812, W, 36, SOFT)
    card(d, 40, 870, W - 80, 270)
    text(d, "Zhaohui's first look, before Claude read the strip:", 60, 885, 1200, 38, SOFT, align="left")
    text(d, "火花比角色小很多，比较亮，持续5s左右，可以看得清。", 60, 935, 1500, 50, INK, bold=True, align="left")
    text(d, "“much smaller than the character, fairly bright, lasts about 5 s, can be seen clearly”",
         60, 1010, 1600, 38, INK, align="left")
    text(d, "Correction, after Claude noted lifetime 0.6 s:", 1760, 885, 1360, 38, SOFT, align="left")
    text(d, "改0.6吧", 1760, 935, 600, 50, WARN, bold=True, align="left")
    text(d, "“change it to 0.6” — original kept as written", 1760, 1010, 1360, 38, INK, align="left")
    text(d, "TUNING.md, Effect A r0", 60, 1080, 1000, 32, SOFT, align="left")
    save(page, "fig_strip_a_r0.png")


def fig_revise_a():
    """TUNING.md Effect A r1: Claude's reading of r0 (the ring), the one change, Claude's prediction."""
    page, d = new()
    for i, f in enumerate([12, 15]):
        im = crop_zoom(f"{SPARK}/r0/frame{f:08d}.png", DARK, 50, 520)
        x = 60 + i * 560
        page.paste(im, (x, 60))
        frame(d, x, 60, im)
        text(d, f"r0 · frame {f}", x, 590, 520, 44, INK, bold=True)
    text(d, "FIXTURE CAPTURE · r0, dark wall · enlarged 5.2×", 60, 650, 1080, 36, SOFT)
    card(d, 60, 720, 1080, 410)
    text(d, "Claude's reading of r0 (a claim):", 80, 740, 1040, 40, SOFT, align="left")
    for i, s in enumerate(["spread 180° and 45–75 px/s send every spark", "out at nearly the same speed:",
                           "a ring with an empty centre at frames 12–15.", "Also: no impact direction; late, small fade."]):
        text(d, s, 80, 800 + i * 70, 1040, 44, INK, align="left")
    card(d, 1200, 60, 1940, 300, outline=ACCENT)
    text(d, "CHANGE (one setting)", 1200, 80, 1940, 40, ACCENT, bold=True)
    text(d, "initial_velocity_min   45 → 15 px/s", 1200, 150, 1940, 76, INK, mono=True, bold=True)
    text(d, "initial_velocity_max stays 75 · commit 1a1e60e", 1200, 270, 1940, 40, SOFT)
    card(d, 1200, 400, 1940, 730)
    text(d, "Claude's prediction for r1 (same seed):", 1220, 420, 1900, 42, SOFT, align="left")
    preds = [("10", "unchanged: a solid white disc"),
             ("12, 15", "a filled, uneven cluster instead of a ring"),
             ("edge", "same outer edge as r0: ~31 px at 15, ~58 px at 24"),
             ("40, 50", "empty"),
             ("still", "no impact direction (needs a second change)")]
    for i, (k, v) in enumerate(preds):
        y = 500 + i * 120
        text(d, k, 1240, y, 260, 48, ACCENT, bold=True, align="left")
        text(d, v, 1500, y, 1620, 48, WARN if k == "edge" else INK, bold=(k == "edge"), align="left")
    text(d, "Zhaohui picked “It reads as a ring”, an option taken from this reading: not independent of it.",
         1220, 1090, 1900, 32, SOFT, align="left")
    save(page, "fig_revise_a.png")


def fig_r1_a():
    """TUNING.md Effect A r1: before/after strips, Claude's comparison (edge wrong), Zhaohui's verdict."""
    page, d = new()
    frames = [10, 12, 15, 20, 24, 30]
    size = 330
    text(d, "r0  (min 45)", 40, 10, 400, 44, INK, bold=True, align="left")
    strip_row(page, d, "r0", DARK, frames, 64, size, x0=40, gap=14, label=False)
    text(d, "r1  (min 15)", 40, 412, 400, 44, INK, bold=True, align="left")
    strip_row(page, d, "r1", DARK, frames, 466, size, x0=40, gap=14, label=True)
    text(d, "FIXTURE CAPTURE · same seed, dark wall · frames 10–30 · enlarged 2.75×", 40, 850, 2050, 34, SOFT)
    x = 2120
    card(d, x, 20, 1040, 360)
    text(d, "Matched", x, 40, 1040, 44, GOOD, bold=True)
    text(d, "frames 12–15: a filled cluster,", x, 110, 1040, 42, INK)
    text(d, "no hollow ring", x, 165, 1040, 42, INK)
    text(d, "40 and 50 empty", x, 240, 1040, 42, INK)
    card(d, x, 400, 1040, 470, outline=WARN)
    text(d, "Claude predicted wrong", x, 420, 1040, 44, WARN, bold=True)
    text(d, "edge across, r0 → r1", x, 490, 1040, 38, SOFT)
    text(d, "frame 15:  31 → 27 px", x, 550, 1040, 50, INK, mono=True)
    text(d, "frame 24:  58 → 48 px", x, 620, 1040, 50, INK, mono=True)
    text(d, "speed is drawn between min and max:", x, 710, 1040, 36, INK)
    text(d, "lowering min slows almost every spark", x, 760, 1040, 36, INK)
    text(d, "radius ≈ 24 px: still inside 15–30", x, 815, 1040, 36, GOOD)
    card(d, 40, 910, W - 80, 230)
    text(d, "Verdict — Zhaohui's answers to two questions Claude Code asked (after “好了，你看着写吧”):", 60, 930, 3000, 38, SOFT, align="left")
    text(d, "saw the ring in r0?  “Yes, I saw it”      r1?  “Keep”      →  KEPT  (CHANGE-BRIEF Revision 3)",
         60, 1000, 3000, 52, INK, bold=True, align="left")
    text(d, "TUNING.md, Effect A r1 · the comparison is Claude Code's", 60, 1080, 2000, 32, SOFT, align="left")
    save(page, "fig_r1_a.png")


# ---------------------------------------------------------------- Effect B

def fig_intent_b():
    """CHANGE-BRIEF.md Effect B: job, condition, the feature A doesn't use, on bg.png with the rect."""
    page, d = new()
    bg = src("godot/art/env/bg.png")
    big = bg.resize((1920, 1080), Image.NEAREST)
    page.paste(big, (40, 40))
    frame(d, 40, 40, big)
    if not MASKED:
        x0, y0, x1, y1 = (40 + 40 * 3, 40 + 125 * 3, 40 + 600 * 3, 40 + 305 * 3)
        for k in range(0, 6):
            d.rectangle([x0 - k, y0 - k, x1 + k, y1 + k], outline=ACCENT)
        d.rectangle([x0, y0 - 64, x0 + 1140, y0 - 6], fill=CARD)
        text(d, "emission rect 560 × 180 px · centre (320, 215)", x0 + 10, y0 - 62, 1130, 44, WARN, bold=True, align="left")
    text(d, "bg.png at 3× · the rectangle is drawn from embers.tscn, not engine output", 40, 1124 - 4, 1920, 30, SOFT)
    x = 2000
    rows = [("Job", "ambience: air and warmth"), ("Condition", "phase == \"fight\" only"),
            ("Start", "emitting on entering fight"), ("Stop", "emitting off; particles finish (≤ 2.5 s)"),
            ("Colour", "muted amber #C58A55 → #E8C49A"), ("Size", "1–3 px in the 640 × 360 view"),
            ("Amount", "48 · lifetime 2.5 s · normal blend")]
    for i, (k, v) in enumerate(rows):
        y = 40 + i * 104
        card(d, x, y, 1160, 92)
        text(d, k, x + 20, y + 20, 300, 40, ACCENT, bold=True, align="left")
        text(d, v, x + 290, y + 24, 860, 34, INK, align="left")
    card(d, x, 790, 1160, 330, outline=ACCENT)
    text(d, "What Effect A doesn't use", x, 810, 1160, 42, ACCENT, bold=True)
    text(d, "rectangle emission   (A: point)", x, 890, 1160, 46, INK, bold=True)
    text(d, "preprocess = 1.5 s   (A: 0)", x, 960, 1160, 46, INK, bold=True)
    text(d, "“the ambience begins as an established field”", x, 1040, 1160, 36, SOFT)
    save(page, "fig_intent_b.png")


def diff_panel(run, f, box, size):
    """Diagnostic: pixels of frame f that differ from the bare frame 175 by more than 8 levels."""
    a = np.asarray(src(f"{EMB}/{run}/frame{f:08d}.png", mask=False)).astype(int)
    ref = np.asarray(src(f"{EMB}/{run}/frame00000175.png", mask=False)).astype(int)
    m = (np.abs(a - ref).max(axis=2) > 8)
    img = Image.fromarray(np.where(m[..., None], 255, 24).astype("uint8").repeat(3, axis=2))
    img = img.crop(box).resize(size, Image.NEAREST)
    return Image.new("RGB", img.size, PAGE) if MASKED else img


def fig_strip_b_r0():
    """TUNING.md Effect B r0: the strip, Zhaohui's multiple-choice first look, Claude's reading."""
    page, d = new()
    frames = [10, 25, 55, 100, 115, 145, 175]
    counts = [168, 230, 215, 274, 237, 62, 0]
    tw, th = 432, 243
    for i, (f, c) in enumerate(zip(frames, counts)):
        im = src(f"{EMB}/r0/frame{f:08d}.png").resize((tw, th), Image.LANCZOS)
        x = 40 + i * (tw + 12)
        page.paste(im, (x, 50))
        frame(d, x, 50, im, RULE, 3)
        text(d, f"frame {f}", x, 300, tw, 36, INK, bold=True)
        text(d, f"{c} px changed", x, 345, tw, 32, SOFT)
    text(d, "FIXTURE CAPTURE · godot/previews/embers_preview.tscn · condition on at frame 10, off at 100 · fixed seed",
         0, 6, W, 32, SOFT)
    big = src(f"{EMB}/r0/frame00000055.png").crop((640, 300, 960, 540)).resize((800, 600), Image.NEAREST)
    page.paste(big, (40, 430))
    frame(d, 40, 430, big)
    text(d, "frame 55, door, enlarged 2.5×", 40, 1040, 800, 34, SOFT)
    dp = diff_panel("r0", 55, (640, 300, 960, 540), (800, 600))
    page.paste(dp, (880, 430))
    frame(d, 880, 430, dp)
    text(d, "DIAGNOSTIC: pixels ≠ frame 175 (> 8 levels)", 880, 1040, 800, 30, WARN, bold=True)
    text(d, "computed for this film, not the picture", 880, 1080, 800, 30, SOFT)
    x = 1730
    card(d, x, 430, 1430, 330)
    text(d, "Zhaohui's first look — three multiple-choice", x + 20, 450, 1400, 36, SOFT, align="left")
    text(d, "questions Claude Code asked, answers as chosen:", x + 20, 495, 1400, 36, SOFT, align="left")
    for i, s in enumerate(["When it started:  already filled", "Against the courtyard:  too faint",
                           "After it stopped:  faded out slowly"]):
        text(d, s, x + 20, 560 + i * 62, 1400, 44, INK, bold=True, align="left")
    card(d, x, 780, 1430, 360)
    text(d, "Claude's reading (a claim):", x + 20, 800, 1400, 36, SOFT, align="left")
    for i, s in enumerate(["~200 of 921 600 pixels change: it does not read",
                           "frame 10 already populated: preprocess runs",
                           "when emitting turns on (open question 3)",
                           "r0-restart identical up to frame 115",
                           "px counts: TUNING.md, vs frame 0"]):
        text(d, s, x + 20, 855 + i * 54, 1400, 38, INK if i < 4 else SOFT, align="left")
    save(page, "fig_strip_b_r0.png")


def fig_r1_b():
    """TUNING.md Effect B r1: alpha change, prediction, measured counts, verdict verbatim."""
    page, d = new()
    box = (640, 300, 960, 540)
    for i, run in enumerate(["r0", "r1"]):
        im = src(f"{EMB}/{run}/frame00000055.png").crop(box).resize((640, 480), Image.NEAREST)
        x = 40 + i * 680
        page.paste(im, (x, 70))
        frame(d, x, 70, im)
        text(d, f"{run} · frame 55 · enlarged 2×", x, 14, 640, 40, INK, bold=True)
        dp = diff_panel(run, 55, box, (640, 480))
        page.paste(dp, (x, 600))
        frame(d, x, 600, dp)
    text(d, "DIAGNOSTIC below: pixels ≠ frame 175 (computed for this film)", 40, 1094, 1320, 30, WARN, bold=True)
    text(d, "FIXTURE CAPTURE above · same seed", 40, 556, 1320, 34, SOFT)
    x = 1420
    card(d, x, 20, 1740, 220, outline=ACCENT)
    text(d, "CHANGE  color_ramp alpha", x, 40, 1740, 40, ACCENT, bold=True)
    text(d, "0.28 → 0.70  ·  0.20 → 0.50", x, 100, 1740, 70, INK, mono=True, bold=True)
    text(d, "colours, offsets, size, amount unchanged · commit 6f0c304", x, 190, 1740, 34, SOFT)
    card(d, x, 260, 1740, 600)
    heads = ["frame", "r0", "predicted r1", "measured r1"]
    cx = [x + 40, x + 330, x + 680, x + 1260]
    cw = [260, 320, 560, 440]
    for j, h in enumerate(heads):
        text(d, h, cx[j], 285, cw[j], 40, SOFT, bold=True)
    rows = [("10", "168", "400–600", "447"), ("25", "230", "~500", "624"), ("55", "215", "~500", "658"),
            ("115", "237", "thinning", "571"), ("145", "62", "a few dots", "195"), ("175", "0", "0", "0")]
    for i, r in enumerate(rows):
        y = 350 + i * 82
        for j, v in enumerate(r):
            text(d, v, cx[j], y, cw[j], 46, INK, bold=(j == 3), mono=(j != 2))
    text(d, "changed pixels of 921 600 (TUNING.md) · 25 and 55 slightly above prediction", x, 850 - 40, 1740, 32, SOFT)
    card(d, x, 880, 1740, 260)
    text(d, "Verdict, Zhaohui's words (preview window):", x + 20, 900, 1700, 36, SOFT, align="left")
    text(d, "录完了，我感觉差不多", x + 20, 950, 1700, 56, INK, bold=True, align="left")
    text(d, "“recorded; I feel it's about right”  →  KEPT (Revision 2)", x + 20, 1040, 1700, 40, INK, align="left")
    save(page, "fig_r1_b.png")


def fig_states_b():
    """CHANGE-BRIEF Effect B rules 2-4, the hidden finding and Revision 4 (TEST-REPORT)."""
    page, d = new()
    text(d, "Particles run on the engine's clock; the game's pause and hitstop never pause the tree", 0, 20, W, 46, INK, bold=True)
    rows = [("main.paused · hitstop", "controller sets speed_scale = 0", "0 on every paused and hitstop tick", GOOD),
            ("get_tree().paused", "process_mode INHERIT: node stops", "tree pause (SETUP) stops node and controller", GOOD),
            ("visible = false", "brief: keeps simulating while hidden", "test: particles stop ageing — rule revised", WARN)]
    heads = ["state", "what the brief / code does", "what the test saw (embers state test)"]
    xs, ws = [40, 940, 2000], [880, 1040, 1160]
    for j, h in enumerate(heads):
        text(d, h, xs[j], 110, ws[j], 40, SOFT, bold=True)
    for i, (a, b, c, col) in enumerate(rows):
        y = 170 + i * 150
        card(d, 40, y, W - 80, 130, outline=col)
        text(d, a, xs[0], y + 38, ws[0], 48, INK, bold=True, mono=True)
        text(d, b, xs[1], y + 42, ws[1], 40, INK)
        text(d, c, xs[2], y + 42, ws[2], 40, col, bold=True)
    card(d, 40, 650, 1540, 490)
    text(d, "Ticks from the stop until the node finishes", 40, 670, 1540, 40, SOFT)
    for i, (k, v) in enumerate([("plain stop", "153"), ("with a 60-tick tree pause", "215"),
                                ("while visible = false", "never within 600"), ("shown again", "finished 151 later")]):
        y = 750 + i * 92
        text(d, k, 80, y, 800, 46, INK, align="left")
        text(d, v, 860, y, 700, 46, WARN if i == 2 else INK, bold=True, align="left")
    text(d, "indirect: node flags over time; no headless run sees particles", 40, 1100 - 10, 1540, 30, SOFT)
    card(d, 1620, 650, 1540, 490, outline=ACCENT)
    text(d, "Revision 4 — Zhaohui's decision", 1620, 670, 1540, 42, ACCENT, bold=True)
    text(d, "那就1吧", 1620, 740, 1540, 64, INK, bold=True)
    text(d, "“option 1, then” — of two Claude Code laid out", 1620, 830, 1540, 38, SOFT)
    for i, s in enumerate(["Hidden: the particles freeze.", "Shown again: they continue.",
                           "The original rule 4 is kept as written."]):
        text(d, s, 1620, 900 + i * 66, 1540, 44, INK, bold=(i < 2))
    save(page, "fig_states_b.png")


# ---------------------------------------------------------------- shader, tests, price, limits

def gen_line(n):
    lines = (REPO / "godot/shaders/particles_generated.gdshader").read_text(encoding="utf-8").splitlines()
    used["godot/shaders/particles_generated.gdshader"] = hashlib.sha256(
        (REPO / "godot/shaders/particles_generated.gdshader").read_bytes()).hexdigest()
    return lines[n - 1].strip()


def fig_shader():
    """particles_generated.gdshader lines beside the brief settings they implement; the dropped ramp."""
    page, d = new()
    text(d, "godot/shaders/particles_generated.gdshader — generated by Zhaohui in the editor (CPU → GPU convert); nothing in the game uses it",
         0, 14, W, 36, SOFT)
    pairs = [(137, "initial_velocity_min / _max   15 / 75 px/s", "a speed drawn between min and max, per particle"),
             (260, "spread   180°", "a random direction inside the spread, times that speed"),
             (307, "gravity   (0, 25)", "the force starts as gravity …"),
             (320, "gravity, applied", "… and is added to the velocity every step")]
    for i, (n, brief, gloss) in enumerate(pairs):
        y = 70 + i * 200
        card(d, 40, y, 2080, 180)
        text(d, f"line {n}", 60, y + 20, 300, 40, ACCENT, bold=True, align="left")
        s = gen_line(n)
        size = 34 if len(s) < 90 else 27
        text(d, s, 60, y + 80, 2040, size, INK, mono=True, align="left")
        card(d, 2160, y, 1000, 180, outline=ACCENT)
        text(d, "brief:", 2180, y + 20, 200, 34, SOFT, align="left")
        text(d, brief, 2180, y + 62, 970, 40, INK, bold=True, mono=True, align="left")
        text(d, gloss, 2180, y + 122, 970, 30, SOFT, align="left")
    card(d, 40, 880, W - 80, 260, outline=WARN)
    text(d, "Finding: the conversion dropped color_ramp and scale_amount_curve", 40, 900, W - 80, 48, WARN, bold=True)
    text(d, f"line 348   {gen_line(348)}      one constant colour for every particle", 40, 980, W - 80, 38, INK, mono=True)
    text(d, f"line 147   {gen_line(147)}", 40, 1040, W - 80, 32, INK, mono=True)
    text(d, "Zhaohui cited lines 10, 43 and 189; Claude Code's check moved them to 137, 307 / 320 and 260 (TEST-REPORT)",
         40, 1094, W - 80, 30, SOFT)
    save(page, "fig_shader.png")


def fig_tests():
    """TEST-REPORT A6: config and state suites, both mutations, earlier suites."""
    page, d = new()
    cols = [("Config read-back", [("test_hit_spark_config", "69 / 0"), ("test_embers_config", "85 / 0")],
             "every brief setting read back from the .tscn; agent build 0ac83ee failed its own star check (69 / 1)"),
            ("State, real loop + input", [("test_hit_spark_state", "57 / 0"), ("test_embers_state", "38 / 0")],
             "16 hits → 16 bursts, 31 other results → 0; frozen in pause and hitstop; SETUP cases labelled")]
    for i, (h, rows, note) in enumerate(cols):
        x = 40 + i * 1040
        card(d, x, 20, 1000, 560)
        text(d, h, x, 40, 1000, 46, ACCENT, bold=True)
        for j, (k, v) in enumerate(rows):
            text(d, k, x + 30, 140 + j * 120, 640, 40, INK, mono=True, align="left")
            text(d, v, x + 680, 130 + j * 120, 290, 60, GOOD, bold=True, mono=True, align="left")
        words, line, yy = note.split(), "", 400
        for w_ in words:
            if d.textlength(line + " " + w_, font=font(34)) > 930:
                text(d, line.strip(), x + 30, yy, 940, 34, SOFT, align="left"); yy += 46; line = ""
            line += " " + w_
        text(d, line.strip(), x + 30, yy, 940, 34, SOFT, align="left")
    x = 2120
    card(d, x, 20, 1040, 560)
    text(d, "Earlier suites, unchanged", x, 40, 1040, 46, ACCENT, bold=True)
    for j, (k, v) in enumerate([("test_runner", "94 / 0"), ("test_hurt_flash ×3", "69 / 0"),
                                ("check_props3d", "49 / 0"), ("test_materials", "96 / 0"), ("calibrate_normal_map", "PASS")]):
        text(d, k, x + 30, 130 + j * 84, 640, 40, INK, mono=True, align="left")
        text(d, v, x + 700, 126 + j * 84, 320, 46, GOOD, bold=True, mono=True, align="left")
    card(d, 40, 610, W - 80, 530, outline=WARN)
    text(d, "Mutations of hit_spark.tscn — each made by Zhaohui, each restored", 40, 630, W - 80, 46, WARN, bold=True)
    rows = [("1", "initial_velocity_min = 45.0  →  initial_velocity = 45.0", "exit 1 · 2 failed",
             "Godot 3 name: loads with no error, min falls to 0 · Zhaohui saw: “我觉得火花好像慢了一些” (a little slower)"),
            ("2", "amount = 20  →  amount = 25", "exit 1 · 1 failed", "value drift, brief unchanged · game not run")]
    for i, (n, m, r, note) in enumerate(rows):
        y = 720 + i * 200
        text(d, n, 80, y, 60, 56, ACCENT, bold=True, align="left")
        text(d, m, 160, y + 6, 2000, 46, INK, mono=True, align="left")
        text(d, r, 2300, y + 4, 820, 50, WARN, bold=True, align="left")
        text(d, note, 160, y + 86, 2960, 36, SOFT, align="left")
    save(page, "fig_tests.png")


def fig_price():
    """TEST-REPORT A6: CPU and GPU price vs prediction and budget; why headless GPU is ~0."""
    page, d = new()
    heads = ["", "measured (median)", "predicted", "budget", ""]
    xs, ws = [40, 640, 1260, 1760, 2240], [600, 620, 500, 480, 300]
    for j, h in enumerate(heads):
        text(d, h, xs[j], 30, ws[j], 40, SOFT, bold=True)
    rows = [("A · CPU", "0.010 ms", "0.08 ms", "≤ 0.25 ms"), ("B · CPU", "0.006 ms", "0.05 ms", "≤ 0.50 ms"),
            ("A · GPU", "+0.012 ms", "0.04 ms", "≤ 0.25 ms"), ("B · GPU", "+0.004 ms", "0.02 ms", "≤ 0.50 ms")]
    for i, r in enumerate(rows):
        y = 100 + i * 130
        card(d, 40, y, 2500, 112)
        for j, v in enumerate(r):
            text(d, v, xs[j], y + 26, ws[j], 52, INK if j != 1 else GOOD, bold=(j < 2), mono=(j > 0))
        text(d, "under", xs[4], y + 30, ws[4], 46, GOOD, bold=True)
    text(d, "per frame at each effect's heaviest state · B GPU is within the frame-to-frame spread (p95 − median ≈ 0.01 ms)",
         40, 630, 2500, 32, SOFT)
    card(d, 2580, 100, 580, 520)
    text(d, "control", 2580, 120, 580, 40, ACCENT, bold=True)
    for i, s in enumerate(["empty scene E", "5.3–5.8 µs", "differs from every", "case: the script", "isn't measuring", "itself"]):
        text(d, s, 2580, 190 + i * 64, 580, 40, INK)
    card(d, 40, 690, 1540, 450)
    text(d, "Why a GPU effect's headless price ≈ 0", 40, 710, 1540, 42, ACCENT, bold=True)
    for i, s in enumerate(["GPUParticles2D runs its process as a shader;", "the headless dummy renderer runs no shader,",
                           "so a headless frame timer sees almost nothing.", "These are CPUParticles2D: the CPU simulates,",
                           "the GPU still draws, so both prices count.", "(brief, short answer 4 and price section)"]):
        text(d, s, 70, 790 + i * 56, 1500, 38, INK if i < 5 else SOFT, align="left")
    card(d, 1620, 690, 1540, 450, outline=WARN)
    text(d, "Where the GPU numbers came from", 1620, 710, 1540, 42, WARN, bold=True)
    text(d, "Visual Profiler (Zhaohui): frame time GPU column read 0", 1650, 790, 1480, 36, INK, align="left")
    text(d, "“frametime那里一直都是0啊”", 1650, 845, 1480, 40, INK, bold=True, align="left")
    for i, s in enumerate(["Measured instead by Claude Code, windowed:", "RenderingServer GPU render time, 300 frames",
                           "per case, same scene with the effect on / off", "gpu_price.gd · logs/gpu_price_windowed.log"]):
        text(d, s, 1650, 920 + i * 52, 1480, 36, INK if i < 3 else SOFT, align="left")
    save(page, "fig_price.png")


def fig_limits():
    """TEST-REPORT A6 and README limitations: what headless runs prove and cannot show."""
    page, d = new()
    card(d, 40, 30, 1540, 640, outline=GOOD)
    text(d, "Headless proves", 40, 50, 1540, 50, GOOD, bold=True)
    for i, s in enumerate(["every setting matches the brief", "fires on every hit, never otherwise",
                           "at the hit point, within 1 px", "a second hit takes another slot",
                           "frozen in pause and hitstop", "emitting == (phase == \"fight\")", "both prices, far under budget"]):
        text(d, s, 80, 140 + i * 72, 1460, 44, INK, align="left")
    card(d, 1620, 30, 1540, 640, outline=WARN)
    text(d, "No headless run can show", 1620, 50, 1540, 50, WARN, bold=True)
    for i, s in enumerate(["what a particle looks like", "whether it reads on the lantern glow",
                           "whether the embers are too faint", "whether hidden particles really freeze",
                           "the Visual Profiler GPU number (it read 0)"]):
        text(d, s, 1660, 140 + i * 72, 1460, 44, INK, align="left")
    text(d, "→ the strips and Zhaohui's eyes", 1660, 140 + 5 * 72 + 20, 1460, 44, WARN, bold=True, align="left")
    card(d, 40, 700, W - 80, 440)
    text(d, "In play — Zhaohui's whole report (HUMAN CHECK):", 70, 720, 3000, 38, SOFT, align="left")
    text(d, "我运行游戏的时候，一切正常，没什么问题", 70, 780, 3000, 56, INK, bold=True, align="left")
    text(d, "“when I ran the game everything was normal, no problems” — recorded as given", 70, 870, 3000, 40, INK, align="left")
    for i, s in enumerate(["It does not name rapid repeats, the lantern, the screen edge or the first frames one by one.",
                           "Never reached in a test: the pool's all-four-busy fallback. Rule 6 only with labelled SETUP.",
                           "Not done: the vsync-off FPS comparison (F9)."]):
        text(d, s, 70, 950 + i * 56, 3000, 38, SOFT, align="left")
    save(page, "fig_limits.png")


def fig_mistakes():
    """FRICTIONAL / TEST-REPORT A6: what the agent got wrong, and Claude's wrong strip reading."""
    page, d = new()
    rows = [("Cost script measured itself", "Performance.TIME_PROCESS refreshes ~once a second; the empty-scene control caught it"),
            ("Generator through the test wrapper", "ran make_textures.gd via run-test.sh, then rm'd that log (9 denials in step 2)"),
            ("Star check failed its own texture", "tip / gap 7.72 / 5.46 on 8 × 8; Zhaohui chose to sharpen; 873d614"),
            ("Pool trusted a late finished", "a late signal after a round reset could free a busy slot; now reads emitting, e96c916"),
            ("Denied commands", "compound Bash; ; echo after run-test.sh; 4 probes outside the wrapper — reran plainly"),
            ("Claude misread a strip", "predicted r1 keeps the spark's outer edge; it shrank 58 → 48 px (frame 24)"),
            ("Claude's own brief error", "phase cited at main.gd:25; it is :24 (Revision 2)")]
    for i, (k, v) in enumerate(rows):
        y = 30 + i * 158
        card(d, 40, y, W - 80, 140, outline=WARN if i == 5 else RULE)
        text(d, k, 70, y + 40, 1060, 48, WARN if i >= 5 else INK, bold=True, align="left")
        text(d, v, 1140, y + 46, 2000, 38, INK, align="left")
    save(page, "fig_mistakes.png")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for fn in (fig_intent_a, fig_strip_a_r0, fig_revise_a, fig_r1_a, fig_intent_b, fig_strip_b_r0, fig_r1_b,
               fig_states_b, fig_shader, fig_tests, fig_price, fig_limits, fig_mistakes):
        fn()
        print("figure", fn.__name__)
    if not MASKED:
        (OUT / "figures.json").write_text(json.dumps(used, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
