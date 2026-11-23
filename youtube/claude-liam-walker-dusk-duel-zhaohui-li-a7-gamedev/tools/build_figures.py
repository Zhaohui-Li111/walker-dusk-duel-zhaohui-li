#!/usr/bin/env python3
"""Lay out the A7 film's figure stills from files already in the repo (no new art).

Adapted from the A6 reel's tool. Engine panels are the committed Movie Maker strips in
captures/kick_arc/r0 and r1 (fixture captures of godot/previews/kick_arc_preview.tscn, 1280 x 720,
made by Zhaohui), pasted unchanged except for cropping and nearest-neighbour enlargement, and the
committed sheet godot/art/sheets/lantern_flame.png (shown on a flat dark backdrop because it is
transparent). Numbers, quotes and code are copied from CHANGE-BRIEF.md, TUNING.md, TEST-REPORT.md,
FRICTIONAL.md, the logs and the source files. The only new pixels are labels, frames, grid lines
and arrows. Every source and its SHA-256 goes to figures/figures.json for SOURCES.md.
    python tools/build_figures.py [--masked]
"""
import hashlib
import json
import pathlib
import sys

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
DARK = (34, 24, 40)
W, H = 3200, 1160
used = {}
KICK = "captures/kick_arc"
P1BOX = (330, 380, 620, 630)       # TUNING.md A7: crop around P1 in the 1280 x 720 strips


def font(size, bold=False, mono=False):
    if mono:
        return ImageFont.truetype("C:/Windows/Fonts/consolab.ttf" if bold else "C:/Windows/Fonts/consola.ttf", size)
    return ImageFont.truetype("C:/Windows/Fonts/seguisb.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf", size)


def cjk(s):
    return any("\u3000" <= ch <= "\u9fff" or "\uff00" <= ch <= "\uffef" for ch in s)


def src(rel, mask=True, mode="RGB"):
    p = REPO / rel
    used[rel] = hashlib.sha256(p.read_bytes()).hexdigest()
    img = Image.open(p).convert(mode)
    return Image.new(mode, img.size, PAGE) if (MASKED and mask) else img


def text(d, s, x, y, w, size=54, color=INK, bold=False, mono=False, align="center"):
    if cjk(s):
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


def card(d, x, y, w, h, outline=RULE, fill=CARD):
    d.rounded_rectangle([x, y, x + w, y + h], radius=22, fill=fill, outline=outline, width=4)


def new():
    page = Image.new("RGB", (W, H), PAGE)
    return page, ImageDraw.Draw(page)


def save(page, name):
    page.save(OUT / name)


def p1crop(run, f, size):
    img = src(f"{KICK}/{run}/frame{f:08d}.png").crop(P1BOX)
    return img.resize((int(size * img.width / img.height), size), Image.NEAREST)


# ---------------------------------------------------------------- the two clips

def fig_clips():
    page, d = new()
    cols = [("", 520), ("Clip 1 · lantern flame", 1300), ("Clip 2 · kick arc", 1300)]
    rows = [("Kind", "cycle: loops (LOOP_LINEAR)", "committing action (LOOP_NONE)"),
            ("Route", "Sprite2D + AnimationPlayer frame track", "cutout rig keyed as resource text"),
            ("Resource", "animations/lantern_flicker.tres", "animations/kick_arc.tres · kick_rest.tres"),
            ("Plays on", "LanternLeft (238, 218) · LanternRight (439, 219)", "KickRig → Pivot → Trail, Core (Polygon2D)"),
            ("Authority", "each lantern's own AnimationPlayer", "KickRig/AnimationPlayer, seek from kick_rig.gd"),
            ("Clock", "idle tick (PROCESS_IDLE, default)", "MANUAL, seek(frame / 60) each physics tick"),
            ("Reads", "nothing: burns through pause and hitstop", "Fighter.state, Fighter.frame (read only)")]
    x = 40
    for i, (lab, w) in enumerate(cols):
        if lab:
            card(d, x, 20, w - 20, 110, outline=ACCENT, fill=(250, 238, 228))
            text(d, lab, x, 42, w - 20, 54, INK, bold=True)
        x += w
    for r, row in enumerate(rows):
        y = 150 + r * 140
        x = 40
        for c, (cell, (lab, w)) in enumerate(zip(row, cols)):
            card(d, x, y, w - 20, 124)
            text(d, cell, x + 24, y + 34, w - 60, 44 if c else 46, ACCENT if c == 0 else INK, bold=(c == 0),
                 mono=(r == 2 and c > 0), align="left")
            x += w
    save(page, "fig_clips.png")


def fig_sheet():
    page, d = new()
    sheet = src("godot/art/sheets/lantern_flame.png", mode="RGBA")
    k = 20
    big = sheet.resize((sheet.width * k, sheet.height * k), Image.NEAREST)
    ox, oy = 80, 140
    back = Image.new("RGB", big.size, DARK)
    back.paste(big, (0, 0), big)
    page.paste(back, (ox, oy))
    frame(d, ox, oy, back)
    for c in range(1, 4):
        d.line([ox + c * 12 * k, oy, ox + c * 12 * k, oy + 32 * k], fill=ACCENT, width=4)
    d.line([ox, oy + 16 * k, ox + 48 * k, oy + 16 * k], fill=ACCENT, width=4)
    for n in range(8):
        cx, cy = ox + (n % 4) * 12 * k, oy + (n // 4) * 16 * k
        text(d, str(n), cx + 12, cy + 6, 60, 52, (255, 240, 220), bold=True, align="left")
        bx, by = cx + 6 * k, cy + 15 * k
        if not MASKED:
            d.ellipse([bx - 9, by - 9, bx + 9, by + 9], outline=(120, 220, 255), width=4)
    text(d, "lantern_flame.png · 48 × 32 px, enlarged 20× · on a dark backdrop (the PNG is transparent)",
         ox, 30, 960, 34, SOFT, align="left")
    text(d, "orange lines: the 4 × 2 slicing · blue rings: flame base (6, 15) in every cell", ox, 80, 960, 34, SOFT,
         align="left")
    x = 1100
    rows = [("Cell", "12 × 16 px, no padding, no margin"),
            ("Grid", "hframes 4 × vframes 2 = 8 cells"),
            ("Order", "cell n = Sprite2D.frame n (column n % 4, row n / 4)"),
            ("Registration", "base (6, 15); sprite offset (−6, −15)"),
            ("Source", "make_lantern_flame_sheet.gd (written by Claude Code)"),
            ("Chosen by", "Zhaohui: “直接用代码生成吧” (generate it by code)"),
            ("Licence", "MIT (repository LICENSE) · no third-party art, no model")]
    for i, (k2, v) in enumerate(rows):
        y = 140 + i * 140
        card(d, x, y, 2060, 124)
        text(d, k2, x + 26, y + 36, 380, 44, ACCENT, bold=True, align="left")
        text(d, v, x + 400, y + 38, 1640, 40, INK, align="left")
    text(d, "godot/art/sheets/ATTRIBUTION.md · CHANGE-BRIEF.md (A7) “The sheet” · FRICTIONAL.md A7 setup",
         ox, 1100, 3000, 32, SOFT, align="left")
    save(page, "fig_sheet.png")


def fig_clip_data():
    """Q1: a clip is tracks; a wrong property name is silent; mutation 1 and the probe."""
    page, d = new()
    card(d, 40, 30, 1540, 560)
    text(d, "A clip is data: tracks of (node path : property, keys)", 40, 50, 1540, 44, ACCENT, bold=True)
    lines = ['tracks/1/path = NodePath("Pivot:rotation")',
             '"times":  PackedFloat32Array(0, 0.116667, ...)',
             '"values": [1.48353, 1.745329, ...]']
    for i, s in enumerate(lines):
        text(d, s, 80, 150 + i * 80, 1480, 40, INK, mono=True, align="left")
    text(d, "kick_arc.tres :31, :35, :38", 80, 400, 1480, 34, SOFT, align="left")
    text(d, "The path resolves from the player's root_node (KickRig).", 80, 470, 1480, 38, INK, align="left")
    text(d, "Nothing checks it when the clip plays.", 80, 520, 1480, 38, INK, align="left")
    card(d, 1620, 30, 1540, 560, outline=WARN)
    text(d, "Mutation 1 (in a worktree, then removed)", 1620, 50, 1540, 44, WARN, bold=True)
    text(d, 'NodePath("Pivot:rotaton")', 1660, 150, 1460, 50, INK, mono=True, bold=True, align="left")
    text(d, "one letter missing · no engine error in the log", 1660, 230, 1460, 38, INK, align="left")
    text(d, "the only failing line is the read-back's own check:", 1660, 300, 1460, 36, SOFT, align="left")
    text(d, "track problem: kick_arc track 1:", 1660, 370, 1460, 40, INK, mono=True, align="left")
    text(d, "  Pivot has no property rotaton", 1660, 420, 1460, 40, INK, mono=True, align="left")
    text(d, "FAIL [tracks] ... (1 problems) → exit 1", 1660, 480, 1460, 40, WARN, mono=True, bold=True, align="left")
    text(d, "logs/mutation_a7_1_subname_60fps.log:9-10", 1660, 540, 1460, 30, SOFT, align="left")
    card(d, 40, 630, W - 80, 500)
    text(d, "The same failure, met by the agent (TEST-REPORT A7, Findings 3; CLAUDE.md headless facts)", 70, 650,
         3000, 38, SOFT, align="left")
    text(d, "A probe keyed ..:rotation from a player whose root_node was already the parent:", 70, 720, 3000, 46,
         INK, align="left")
    text(d, "it moved nothing and printed nothing.", 70, 790, 3000, 46, WARN, bold=True, align="left")
    text(d, "So “the clip plays” proves nothing about the node it was meant to move.", 70, 880, 3000, 44, INK,
         align="left")
    text(d, "The read-back asks every track to resolve: track_problems() in tests/anim_checks.gd.", 70, 950, 3000,
         44, INK, align="left")
    text(d, "Zhaohui's own account: 如果路径写错 … 不一定会直接产生明显错误 (“if a path is wrong … not necessarily an obvious error”)",
         70, 1040, 3000, 36, SOFT, align="left")
    save(page, "fig_clip_data.png")


def fig_phase():
    """Q4: the phase table counted from fighter.gd beside the key times built from it."""
    page, d = new()
    card(d, 40, 20, 1180, 560)
    text(d, "fighter.gd, what the code says (abridged)", 40, 40, 1180, 40, SOFT, bold=True)
    code = ['36  const ATTACKS := {', '38    "kick": {"startup": 7,', '         "active": 5, "recovery": 16, ...',
            '90  frame += 1   # start of each step', '164 if frame <= a["startup"] or',
            '      frame > a["startup"] + a["active"]:', '      return   # no hit check', '106 if frame >= 7 + 5 + 16: idle']
    for i, s in enumerate(code):
        text(d, s, 70, 100 + i * 52, 1120, 34, INK, mono=True, align="left")
    text(d, "constants 7 / 5 / 16 · counted from the code 8 / 5 / 15", 40, 515, 1180, 34, WARN, bold=True)
    # timeline
    x0, x1, y = 1300, 3140, 140
    unit = (x1 - x0) / 28
    segs = [(0, 8, "startup", (240, 214, 190)), (8, 13, "active", ACCENT), (13, 28, "recovery", (214, 206, 190))]
    for a, b, lab, col in segs:
        d.rectangle([x0 + a * unit, y, x0 + b * unit, y + 130], fill=col, outline=INK, width=3)
        text(d, lab, x0 + a * unit, y + 40, (b - a) * unit, 46, INK, bold=True)
    for f in range(29):
        xx = x0 + f * unit
        d.line([xx, y + 130, xx, y + 150], fill=INK, width=2)
        if f in (0, 7, 8, 12, 13, 27, 28):
            text(d, str(f), xx - 40, y + 156, 80, 34, INK, bold=f in (0, 8, 13, 28))
    text(d, "Fighter.frame (60 ticks/s) · the kick image shows on frames 0–27; idle on 28", x0, 40, x1 - x0, 38, SOFT)
    hdr = ["Phase", "Frames", "Begins", "Key time", "Game reads"]
    xs = [1300, 1680, 1980, 2200, 2640]
    rows = [("Startup", "8 (0–7)", "0", "0.0000 s", "no hit check"),
            ("Active", "5 (8–12)", "8", "0.1333 s", "check_hit: 7 < frame ≤ 12"),
            ("Recovery", "15 (13–27)", "13", "0.2167 s", "whiff resolves at 13"),
            ("(end)", "—", "28", "0.4667 s", "idle = length; input 29")]
    for j, h in enumerate(hdr):
        text(d, h, xs[j], 380, 400, 36, SOFT, bold=True, align="left")
    for i, r in enumerate(rows):
        yy = 430 + i * 100
        card(d, 1290, yy, 1860, 88, outline=ACCENT if i == 1 else RULE)
        for j, v in enumerate(r):
            text(d, v, xs[j], yy + 22, 440, 38, INK, bold=(j in (0, 3)), mono=(j == 3), align="left")
    card(d, 40, 600, 1180, 530)
    text(d, "Feel, in frames", 40, 615, 1180, 44, ACCENT, bold=True)
    for i, s in enumerate(["key time = frame / 60, step 1/60 s", "keys at every phase boundary and the frame before:",
                           "0, 7, 8, 12, 13, 27, 28", "transition 2.0 into active: an accelerating sweep",
                           "transition 0.4 through recovery: it settles", "Zhaohui chose the measured 8 / 5 / 15",
                           "(“按代码实测 8/5/15”)"]):
        text(d, s, 80, 685 + i * 60, 1120, 38, INK if i < 5 else SOFT, bold=(i == 2), align="left")
    text(d, "CHANGE-BRIEF.md (A7): project facts, “The phase table”, revision 4 · fighter.gd:35-38, 90, 103-108, 164-165",
         1300, 1090, 1860, 30, SOFT, align="left")
    save(page, "fig_phase.png")


def fig_strip():
    """Req 4: the committed r1 strip at each phase boundary (capture frames 10-24)."""
    page, d = new()
    frames = [(10, 0, "startup begins"), (13, 6, "late startup"), (14, 8, "active opens"), (16, 12, "last active"),
              (17, 14, "recovery"), (23, 26, "late recovery"), (24, 28, "idle")]
    size = 400
    for i, (f, ff, lab) in enumerate(frames):
        im = p1crop("r1", f, size)
        row, col = divmod(i, 4)
        x = 40 + col * (im.width + 330)
        y = 10 + row * 520
        page.paste(im, (x, y + 50))
        act = 14 <= f <= 16
        frame(d, x, y + 50, im, ACCENT if act else RULE, 4)
        text(d, f"frame {f}", x, y, im.width, 40, INK, bold=True)
        text(d, f"Fighter.frame {ff}", x + im.width + 16, y + 170, 300, 30, INK, mono=True, align="left")
        text(d, lab, x + im.width + 20, y + 220, 300, 34, ACCENT if act else SOFT, bold=True, align="left")
    x = 40 + 3 * (464 + 330)
    card(d, 40 + 3 * 794, 540, 3160 - (40 + 3 * 794), 440)
    for i, s2 in enumerate(["Frame 13 falls", "between captures", "16 and 17. The thin", "line on 17 is", "effects.gd's whiff",
                            "streak, not the clip", "(TUNING.md A7)."]):
        text(d, s2, 40 + 3 * 794 + 30, 560 + i * 58, 560, 36, INK, align="left")
    text(d, "FIXTURE CAPTURE · godot/previews/kick_arc_preview.tscn (real main.tscn, title skipped, P1 kicking by "
            "ScriptedController) · Movie Maker 30 fps, run by Zhaohui · captures/kick_arc/r1", 40, 1050, 3120, 32, SOFT)
    text(d, "crops of viewport x 165–310, y 190–315, enlarged · 2 ticks per captured frame · frame N ↔ "
            "logs/kick_arc_preview_frames.log line N + 1", 40, 1100, 3120, 30, SOFT)
    save(page, "fig_strip.png")


def fig_tuning():
    """TUNING.md A7: r0 reading, r1 change and prediction, comparison, verdict."""
    page, d = new()
    for i, (run, lab) in enumerate((("r0", "r0 · key 0 alpha 0"), ("r1", "r1 · key 0 alpha 0.25"))):
        im = p1crop(run, 10, 520)
        x = 60 + i * (im.width + 40)
        page.paste(im, (x, 90))
        frame(d, x, 90, im, WARN if run == "r1" else RULE)
        text(d, lab + " · frame 10", x, 24, im.width, 40, INK, bold=True)
    text(d, "FIXTURE CAPTURE · captures/kick_arc/r0 and r1, frame 10 (Fighter.frame 0), same crop", 60, 630, 1250, 32, SOFT,
         align="left")
    card(d, 60, 690, 1250, 440)
    text(d, "Who drove r1", 80, 710, 1210, 42, ACCENT, bold=True, align="left")
    for i, s in enumerate(["Zhaohui's first look (before any reading): “刚好” (just right)",
                           "verdict on r0: nothing to change",
                           "then: “改吧” (change them), on Claude's r0 points",
                           "this change approved: “批准” (approved)",
                           "→ from Claude's strip reading, approved and judged by Zhaohui"]):
        text(d, s, 80, 780 + i * 66, 1210, 36, WARN if i == 4 else INK, bold=(i == 4), align="left")
    x = 1360
    card(d, x, 30, 1800, 250, outline=ACCENT)
    text(d, "Claude's r0 reading (a claim)", x, 50, 1800, 40, SOFT)
    text(d, "frame 10: no arc — the brief asks for a faint wind-up", x, 110, 1800, 46, INK, bold=True)
    text(d, "cause: Pivot:modulate key 0 has alpha 0", x, 190, 1800, 40, INK)
    card(d, x, 300, 1800, 180, outline=ACCENT)
    text(d, "CHANGE (one value) · kick_arc.tres :50 · commit 8049c54", x, 320, 1800, 36, ACCENT, bold=True)
    text(d, "key 0 alpha   0 → 0.25", x, 380, 1800, 60, INK, mono=True, bold=True)
    card(d, x, 500, 1800, 400)
    text(d, "Prediction (written first)  →  measured (Claude's comparison)", x, 520, 1800, 38, SOFT)
    rows = [("10", "faint arc, ~25 %, down-forward", "740 px changed: yes"),
            ("11", "slightly brighter", "185 px: yes"),
            ("12", "slightly brighter", "37 px: too small to see"),
            ("13–24", "identical to r0", "35–50 px, ember noise: yes")]
    for i, (f, p, m) in enumerate(rows):
        y = 590 + i * 74
        text(d, f, x + 30, y, 200, 40, ACCENT, bold=True, align="left")
        text(d, p, x + 230, y, 860, 38, INK, align="left")
        text(d, m, x + 1100, y, 690, 38, GOOD if "yes" in m else WARN, align="left")
    card(d, x, 920, 1800, 210, outline=GOOD)
    text(d, "Zhaohui's verdict after play", x, 940, 1800, 38, SOFT)
    text(d, "能看的出来，刚好。", x, 990, 1800, 56, INK, bold=True)
    text(d, "“it can be seen, just right” → r1 KEPT (CHANGE-BRIEF Revision 5)", x, 1070, 1800, 36, GOOD, bold=True)
    save(page, "fig_tuning.png")


def fig_authority():
    """Q2: one writer per animated property; what two writers would do."""
    page, d = new()
    rows = [("LanternFlame/Sprite2D.frame", "that lantern's AnimationPlayer (flicker)", "lantern_flame.gd only play() + seek() once"),
            ("KickRig/Pivot, Trail, Core", "KickRig/AnimationPlayer (kick_arc, rest)", "positioned by seek(), never by hand"),
            ("KickRig position, scale", "kick_rig.gd (hip pivot, size, facing)", "the script's only writes"),
            ("Fighter/Sprite2D texture, flip, offset", "fighter.gd _update_sprite() every step", "fighter.gd:286-291 · no clip keys it")]
    text(d, "Property", 60, 30, 900, 38, SOFT, bold=True, align="left")
    text(d, "Its one writer", 1060, 30, 1000, 38, SOFT, bold=True, align="left")
    text(d, "Note", 2160, 30, 900, 38, SOFT, bold=True, align="left")
    for i, (a, b, c) in enumerate(rows):
        y = 90 + i * 130
        card(d, 40, y, W - 80, 112, outline=ACCENT if i == 3 else RULE)
        text(d, a, 70, y + 32, 980, 38, INK, bold=True, mono=True, align="left")
        text(d, b, 1060, y + 32, 1080, 38, INK, align="left")
        text(d, c, 2160, y + 34, 980, 34, SOFT, align="left")
    card(d, 40, 640, 1540, 490, outline=WARN)
    text(d, "With two writers", 40, 660, 1540, 46, WARN, bold=True)
    for i, s in enumerate(["fighter.gd sets the sprite every physics step;",
                           "a clip keying the same sprite would set it too:", "the last write in each tick wins,",
                           "so the clip is overwritten or the picture flickers.",
                           "(brief, predicted failure 4)"]):
        text(d, s, 80, 740 + i * 66, 1460, 40, INK if i < 4 else SOFT, align="left")
    card(d, 1620, 640, 1540, 490, outline=GOOD)
    text(d, "What guards it", 1620, 660, 1540, 46, GOOD, bold=True)
    for i, s in enumerate(["kick read-back: every track writes inside KickRig,",
                           "never the fighter or its Sprite2D (6 checks)",
                           "lantern read-back: one AnimationPlayer; the root",
                           "script's code never names the sprite",
                           "Not staged in this film: no two-writer run was made."]):
        text(d, s, 1660, 740 + i * 66, 1460, 40, WARN if i == 4 else INK, bold=(i == 4), align="left")
    save(page, "fig_authority.png")


def fig_clocks():
    """Q3: the two clocks and the measured 0 s."""
    page, d = new()
    card(d, 40, 30, 1540, 620)
    text(d, "Clock 1 · lantern flame", 40, 50, 1540, 48, ACCENT, bold=True)
    for i, s in enumerate(["AnimationPlayer, callback_mode_process IDLE (1)", "advances once per process (idle) tick",
                           "reads no game state", "keeps burning through pause and hitstop (L1)",
                           "test_anim_states: left 0.12 → 0.62 s over 30 paused ticks"]):
        text(d, s, 80, 140 + i * 90, 1460, 40, INK if i < 4 else SOFT, align="left")
    card(d, 1620, 30, 1540, 620)
    text(d, "Clock 2 · kick arc", 1620, 50, 1540, 48, ACCENT, bold=True)
    for i, s in enumerate(["AnimationPlayer, callback_mode_process MANUAL (2)", "never advances by itself",
                           "kick_rig.gd: seek(Fighter.frame / 60, true)", "on the physics tick, priority 100 (after Main)",
                           "the same tick check_hit reads 7 < frame ≤ 12"]):
        text(d, s, 1660, 140 + i * 90, 1460, 40, INK, mono=(i == 2), align="left")
    card(d, 40, 690, W - 80, 440, outline=GOOD)
    text(d, "Measured over a whole kick (tests/test_anim_states.gd, real loop, 60 ticks/s)", 70, 710, 3000, 38, SOFT,
         align="left")
    text(d, "largest |clip time − Fighter.frame / 60| = 0.000000000 s", 70, 790, 3000, 66, INK, mono=True, bold=True,
         align="left")
    text(d, "logs/test_anim_states_60fps.log:57-58 · predicted 0 s in the brief (Zhaohui's short answer 5, revision 2)",
         70, 890, 3000, 36, SOFT, align="left")
    text(d, "hitstop: the arc holds at frame 8 for the hit tick and 4 more · pause: 30 ticks at 0.1667 s (:65, :71)",
         70, 960, 3000, 40, INK, align="left")
    text(d, "The two clocks never need to agree: the lantern takes part in no hit check.", 70, 1040, 3000, 40, INK,
         align="left")
    save(page, "fig_clocks.png")


def fig_tests():
    page, d = new()
    rows = [("test_lantern_readback", "47 / 0", "slicing 4 × 2, DISCRETE, keys k × 0.1, step 0.1, LOOP_LINEAR, seam"),
            ("test_kick_readback", "52 / 0", "keys on 0 / 8 / 13 / 28, step 1/60, LOOP_NONE, MANUAL, no Sprite2D track"),
            ("test_anim_states", "58 / 0", "every state → a clip; real input; clip = frame / 60; hitstop, pause"),
            ("test_kick_edges", "38 / 0", "hit on frames 0,1 · 7,8,9 · 12,13,14 · 27,28 → rest that tick"),
            ("test_pins_a7", "19 / 0", "before any clip and after: game behaviour unchanged")]
    for i, (n, r, w) in enumerate(rows):
        y = 20 + i * 112
        card(d, 40, y, W - 80, 100)
        text(d, n, 70, y + 26, 820, 42, INK, mono=True, bold=True, align="left")
        text(d, r, 900, y + 22, 300, 50, GOOD, bold=True, align="left")
        text(d, w, 1200, y + 30, 1940, 36, INK, align="left")
    muts = [("1", "Pivot:rotation → rotaton", "exit 1", "1 of 51: no property rotaton"),
            ("2", "flicker loop_mode 1 → 0", "exit 1", "1 of 47: loop_mode is LOOP_LINEAR (got 0)"),
            ("3", "last frame key 7 → 8", "exit 1", "2 of 47: cell order; “key 7's cell 8 is inside the sheet (< 8)”"),
            ("4", "empty import cache", "exit 0", "expected: no clip is imported, nothing to drop")]
    text(d, "Mutations (each in a worktree at 48a3b60, then removed) · logs/mutation_a7_*", 40, 590, 3000, 36, SOFT,
         align="left")
    for i, (k, m, e, why) in enumerate(muts):
        y = 640 + i * 112
        card(d, 40, y, W - 80, 100, outline=WARN if e == "exit 1" else RULE)
        text(d, k, 70, y + 24, 60, 46, ACCENT, bold=True, align="left")
        text(d, m, 150, y + 26, 1100, 40, INK, mono=True, align="left")
        text(d, e, 1300, y + 24, 260, 46, WARN if e == "exit 1" else SOFT, bold=True, align="left")
        text(d, why, 1580, y + 30, 1560, 36, INK, align="left")
    save(page, "fig_tests.png")


def fig_human():
    page, d = new()
    card(d, 40, 30, 1540, 460, outline=GOOD)
    text(d, "Headless proves", 40, 50, 1540, 48, GOOD, bold=True)
    for i, s in enumerate(["keys, times, loop modes, slicing", "which clip each state plays, on which tick",
                           "the arc frozen in hitstop and pause", "game behaviour unchanged (pins)"]):
        text(d, s, 80, 140 + i * 78, 1460, 42, INK, align="left")
    card(d, 1620, 30, 1540, 460, outline=WARN)
    text(d, "No headless run can show", 1620, 50, 1540, 48, WARN, bold=True)
    for i, s in enumerate(["whether the seam stutters", "whether the phases read apart",
                           "whether the flame drifts", "whether it reads on dark and lit stone"]):
        text(d, s, 1660, 140 + i * 78, 1460, 42, INK, align="left")
    card(d, 40, 520, W - 80, 610)
    text(d, "Zhaohui's checks in the running game (TEST-REPORT A7, Human checks; Claude Code did not watch)", 70, 540,
         3000, 36, SOFT, align="left")
    rows = [("Seam, 5+ wraps", "没有卡顿", "no stutter"),
            ("Kick in play, interrupts", "能分清，打断后消失", "the phases can be told apart; after an interrupt it disappears"),
            ("Registration", "在同一位置，没有漂移", "stays in the same place, no drift"),
            ("Dark (x≈364) and lit (x≈510)", "看得清", "clearly visible")]
    for i, (k, zh, en) in enumerate(rows):
        y = 610 + i * 124
        text(d, k, 70, y + 10, 820, 40, ACCENT, bold=True, align="left")
        text(d, zh, 900, y, 900, 52, INK, bold=True, align="left")
        text(d, "“" + en + "”", 1700, y + 10, 1440, 38, INK, align="left")
    save(page, "fig_human.png")


def fig_mistakes():
    page, d = new()
    rows = [("Guessed a pin", "jump airtime guessed 44; the first run failed it; pinned as measured, 42"),
            ("Broke an A6 test", "lanterns after Stage failed test_embers_state's draw order (37/38); moved after Embers"),
            ("Wrong fact in the brief", "input read again on kick frame 28 — it is 29 (edge test; revision 4)"),
            ("Inert probe track", "..:rotation from a player rooted at the parent moved nothing, printed nothing"),
            ("Harness bugs", "comment text in an authority check, a %e format, an always-true check, late-armed hits"),
            ("Sign-in", "claude -p stopped twice (OAuth expired); Step 1 ran in the desktop session"),
            ("Claude's strip reading", "guessed a polygon seam; the line was effects.gd's whiff streak (own renders)")]
    for i, (k, v) in enumerate(rows):
        y = 30 + i * 158
        card(d, 40, y, W - 80, 140, outline=WARN if i == 6 else RULE)
        text(d, k, 70, y + 40, 900, 48, WARN if i == 6 else INK, bold=True, align="left")
        text(d, v, 980, y + 46, 2160, 38, INK, align="left")
    save(page, "fig_mistakes.png")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for fn in (fig_clips, fig_sheet, fig_clip_data, fig_phase, fig_strip, fig_tuning, fig_authority, fig_clocks,
               fig_tests, fig_human, fig_mistakes):
        fn()
        print("figure", fn.__name__)
    if not MASKED:
        (OUT / "figures.json").write_text(json.dumps(used, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
