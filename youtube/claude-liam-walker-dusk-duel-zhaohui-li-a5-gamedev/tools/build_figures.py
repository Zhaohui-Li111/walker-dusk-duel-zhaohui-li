#!/usr/bin/env python3
"""Lay out the A5 film's figure stills from files already in the repo (no new art).

Panels are engine stills recorded by godot/tests/capture_a5.gd on the isolated copy
(capture/evidence/a5/, 1924 x 1082: Windows clamps the window to the screen), pasted unchanged
except for cropping and scaling. Numbers and code are copied from CHANGE-BRIEF.md, TEST-REPORT.md,
the recorded logs and the shader files. The only new pixels are labels, sample-point rings and the
page. Every source and its SHA-256 goes to figures/figures.json for SOURCES.md.
"""
import hashlib
import json
import pathlib
import sys

from PIL import Image, ImageDraw, ImageFont

REEL = pathlib.Path(__file__).resolve().parent.parent
REPO = REEL.parent.parent
REL = REEL.relative_to(REPO).as_posix()
CAP = f"{REL}/capture/evidence/a5"
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


def font(size, bold=False, mono=False):
    if mono:
        return ImageFont.truetype("C:/Windows/Fonts/consolab.ttf" if bold else "C:/Windows/Fonts/consola.ttf", size)
    return ImageFont.truetype("C:/Windows/Fonts/seguisb.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf", size)


def src(rel):
    p = REPO / rel
    used[rel] = hashlib.sha256(p.read_bytes()).hexdigest()
    img = Image.open(p).convert("RGB")
    return Image.new("RGB", img.size, PAGE) if MASKED else img


def fit(img, box_w, box_h):
    s = min(box_w / img.width, box_h / img.height)
    return img.resize((max(1, round(img.width * s)), max(1, round(img.height * s))), Image.LANCZOS)


def paste_center(page, img, x, y, w, h):
    ox, oy = x + (w - img.width) // 2, y + (h - img.height) // 2
    page.paste(img, (ox, oy))
    return ox, oy


def text(d, s, x, y, w, size=54, color=INK, bold=False, mono=False, align="center"):
    if any("\u4e00" <= ch <= "\u9fff" for ch in s):     # Zhaohui's Chinese: Segoe UI has no CJK glyphs
        f = ImageFont.truetype("C:/Windows/Fonts/msyhbd.ttc" if bold else "C:/Windows/Fonts/msyh.ttc", size)
    else:
        f = font(size, bold, mono)
    tw = d.textlength(s, font=f)
    xx = x + (w - tw) / 2 if align == "center" else x
    d.text((xx, y), s, font=f, fill=color)


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


def fig_predict():
    """CHANGE-BRIEF.md A5: the colour line and Zhaohui's six hand predictions, before any shader."""
    page, d = new()
    card(d, 40, 20, W - 80, 260)
    text(d, "the colour line, written by Zhaohui (brief, committed 4c8d90a before any shader)", 40, 40, W - 80, 46, SOFT)
    text(d, "COLOR.rgb = mix(COLOR.rgb, flash_color.rgb, hurt_amount);", 40, 130, W - 80, 76, INK, mono=True)
    heads = ["pixel", "stored", "hurt_amount 0.0", "0.5", "1.0"]
    xs, ws = [60, 560, 1240, 1900, 2560], [500, 680, 660, 660, 580]
    for j, h in enumerate(heads):
        text(d, h, xs[j], 320, ws[j], 48, SOFT, bold=True)
    rows = [["P-gi", "(222, 89, 0)", "(222, 89, 0)", "(239, 45, 0) ±1", "(255, 0, 0)"],
            ["P-fist", "(240, 230, 172)", "(240, 230, 172)", "(248, 115, 86) ±1", "(255, 0, 0)"]]
    for i, r in enumerate(rows):
        y = 410 + i * 200
        card(d, 40, y, W - 80, 170)
        for j, v in enumerate(r):
            text(d, v, xs[j], y + 48, ws[j], 62, INK, bold=(j == 0))
    text(d, "computed by hand by Zhaohui: a + (b − a) · t per channel, flash_color = (255, 0, 0)",
         0, 850, W, 54, INK)
    text(d, "also predicted: contrast 3.93 → 3.73 against the background · hint_range does not clamp (Q7)",
         0, 950, W, 50, SOFT)
    save(page, "fig_predict.png")


def ring(d, x, y, r=16, color=ACCENT):
    d.ellipse([x - r, y - r, x + r, y + r], outline=color, width=5)


def fig_controlled():
    """Three in-engine captures of Akaken at hurt_amount 0, 0.5, 1.0, cropped; measured vs predicted."""
    page, d = new()
    crop = (470, 430, 910, 990)            # Akaken's sprite in the 1924 x 1082 capture
    pts = {"P-gi": (675, 773), "P-fist": (744, 674)}
    meas = {"0_0": ["(221, 89, 0)", "(239, 229, 171)"], "0_5": ["(238, 44, 0)", "(247, 115, 86)"],
            "1_0": ["(254, 0, 0)", "(254, 0, 0)"]}
    pred = {"0_0": ["(222, 89, 0)", "(240, 230, 172)"], "0_5": ["(239, 45, 0)", "(248, 115, 86)"],
            "1_0": ["(255, 0, 0)", "(255, 0, 0)"]}
    cw = 1000
    for i, v in enumerate(["0_0", "0_5", "1_0"]):
        img = src(f"{CAP}/hurt_flash_{v}.png").crop(crop)
        im = fit(img, cw - 300, 640)
        x = 60 + i * (cw + 40)
        ox, oy = paste_center(page, im, x, 10, cw, 640)
        frame(d, ox, oy, im)
        s = im.width / (crop[2] - crop[0])
        if not MASKED:
            for name, (px, py) in pts.items():
                ring(d, ox + (px - crop[0]) * s, oy + (py - crop[1]) * s)
        text(d, f"hurt_amount {v.replace('_', '.')}", x, 670, cw, 58, INK, bold=True)
        text(d, f"P-gi  {meas[v][0]}", x, 760, cw, 50, INK)
        text(d, f"predicted {pred[v][0]}", x, 830, cw, 42, SOFT)
        text(d, f"P-fist  {meas[v][1]}", x, 900, cw, 50, INK)
        text(d, f"predicted {pred[v][1]}", x, 970, cw, 42, SOFT)
    text(d, "ENGINE CAPTURE · tests/capture_a5.gd · driver paused, value set from code · every pixel within one step",
         0, 1060, W, 44, SOFT)
    save(page, "fig_controlled.png")


def fig_clamp():
    """Q7: grey flash_color in memory, hurt_amount 1.0 vs 2.0."""
    page, d = new()
    crop = (470, 430, 910, 990)
    for i, (v, val) in enumerate([("1_0", "(128, 128, 128)"), ("2_0", "(34, 167, 254)")]):
        img = src(f"{CAP}/hurt_flash_grey_{v}.png").crop(crop)
        im = fit(img, 900, 700)
        x = 80 + i * 1000
        ox, oy = paste_center(page, im, x, 20, 900, 700)
        frame(d, ox, oy, im)
        if not MASKED:
            s = im.width / (crop[2] - crop[0])
            ring(d, ox + (675 - crop[0]) * s, oy + (773 - crop[1]) * s)
        text(d, f"hurt_amount {v.replace('_', '.')}", x, 750, 900, 60, INK, bold=True)
        text(d, f"P-gi {val}", x, 850, 900, 56, INK)
    x = 2120
    card(d, x, 60, 1040, 860)
    text(d, "if clamped to 1.0", x, 110, 1040, 50, SOFT)
    text(d, "(128, 128, 128)", x, 180, 1040, 62, INK, bold=True)
    text(d, "if not clamped: mix at t = 2", x, 330, 1040, 50, SOFT)
    text(d, "R = 222 + 2 × (128 − 222) = 34", x, 410, 1040, 50, INK, mono=True)
    text(d, "G = 89 + 2 × (128 − 89) = 167", x, 480, 1040, 50, INK, mono=True)
    text(d, "B = 0 + 2 × 128 = 256 → 255 → 254", x, 550, 1040, 50, INK, mono=True)
    text(d, "measured: not clamped", x, 700, 1040, 64, GOOD, bold=True)
    text(d, "Zhaohui predicted: No", x, 800, 1040, 50, SOFT)
    text(d, "flash_color set to grey in memory for this check only · red saturates both 1.0 and 2.0 to (254, 0, 0)",
         0, 1020, W, 44, SOFT)
    save(page, "fig_clamp.png")


def table(d, y0, heads, rows, xs, ws, size=56, hsize=46, rh=150):
    for j, h in enumerate(heads):
        text(d, h, xs[j], y0, ws[j], hsize, SOFT, bold=True)
    for i, r in enumerate(rows):
        y = y0 + 80 + i * (rh + 20)
        card(d, 40, y, W - 80, rh, outline=WARN if r[-1].startswith("FAIL") else RULE)
        for j, v in enumerate(r):
            text(d, v, xs[j], y + (rh - size) // 2 - 8, ws[j], size, WARN if v.startswith("FAIL") else INK,
                 bold=(j == 0))


def fig_tests():
    """test_hurt_flash.gd: the first run vs after Revision 7 (recorded logs)."""
    page, d = new()
    heads = ["run", "30 fps", "60 fps", "144 fps", "what failed"]
    xs, ws = [60, 760, 1260, 1760, 2260], [700, 500, 500, 500, 880]
    rows = [["first run (Revision 6)", "58 / 4 failed", "58 / 4 failed", "58 / 4 failed", "FAIL rule 3 ×3, rule 4"],
            ["after Revision 7", "69 / 0", "69 / 0", "69 / 0", "none"]]
    table(d, 30, heads, rows, xs, ws)
    card(d, 40, 480, 1540, 560)
    text(d, "rule 3: retrigger", 40, 510, 1540, 58, INK, bold=True)
    text(d, "defender leaves hurt at tick T+22", 40, 610, 1540, 50)
    text(d, "next punch connects at T+23 at the earliest", 40, 680, 1540, 50)
    text(d, "probe: 0 of 7 840 cases reach it", 40, 750, 1540, 50)
    text(d, "→ second hit by labelled SETUP: receive_hit()", 40, 850, 1540, 50, ACCENT, bold=True)
    text(d, "restart lasts 18 ticks: no hitstop", 40, 930, 1540, 46, SOFT)
    card(d, 1620, 480, 1540, 560)
    text(d, "rule 4: Engine.time_scale = 0.5", 1620, 510, 1540, 58, INK, bold=True)
    text(d, "still 60 physics ticks per second", 1620, 610, 1540, 50)
    text(d, "the fight steps by ticks; frame data ignores delta", 1620, 680, 1540, 50)
    text(d, "windowed run too: 60.0 ticks/s at 0.5", 1620, 750, 1540, 50)
    text(d, "→ expectation 0.733 s became 0.367 s", 1620, 850, 1540, 50, ACCENT, bold=True)
    text(d, "the flash follows game state", 1620, 930, 1540, 46, SOFT)
    text(d, "HEADLESS · real loop, J key through PlayerController · logs/test_hurt_flash_*fps.log", 0, 1080, W, 42, SOFT)
    save(page, "fig_tests.png")


def fig_mutations():
    """The three mutations Zhaohui made in the shaders, and what caught each (recorded logs)."""
    page, d = new()
    heads = ["mutation (by Zhaohui)", "SHADER ERROR", "result", "caught by"]
    xs, ws = [60, 1160, 1640, 2240], [1100, 480, 600, 900]
    rows = [["delete ';' on hurt_flash:3", "yes", "exit 1 · 7 of 69", "empty uniform list"],
            ["rename hurt_amount (shader only)", "no", "exit 1 · 6 of 69", "uniform names"],
            ["delete source_color from granite:3", "no", "exit 1 · 1 of 96", "hints read from source"]]
    table(d, 40, heads, rows, xs, ws, size=54, rh=170)
    card(d, 40, 720, W - 80, 300, outline=ACCENT)
    text(d, "during the rename, all 23 behaviour checks still passed", 40, 760, W - 80, 62, INK, bold=True)
    text(d, "set_shader_parameter(\"hurt_amount\", …) raised no error, and reading it back returned the stored value",
         40, 860, W - 80, 48)
    text(d, "only the uniform list noticed that the shader no longer declares it", 40, 930, W - 80, 48, SOFT)
    text(d, "logs/mutation1_semicolon_60fps.log · mutation2_rename_60fps.log · mutation3_source_color_60fps.log",
         0, 1070, W, 42, SOFT)
    save(page, "fig_mutations.png")


def fig_sweep():
    """Interface sweep on the floor material, in memory: six engine stills."""
    page, d = new()
    shots = [("uv_scale_min", "uv_scale 0.25"), ("uv_scale_max", "uv_scale 8.0"),
             ("roughness_scale_min", "roughness_scale 0.0"), ("normal_strength_min", "normal_strength 0.0"),
             ("normal_strength_max", "normal_strength 2.0"), ("tint_min", "tint black")]
    crop = (0, 560, 1924, 1082)
    cw, chh = 1000, 420
    for i, (f, lab) in enumerate(shots):
        img = src(f"{CAP}/granite_sweep_{f}.png").crop(crop)
        im = fit(img, cw, chh)
        x = 60 + (i % 3) * (cw + 40)
        y = 10 + (i // 3) * (chh + 120)
        ox, oy = paste_center(page, im, x, y, cw, chh)
        frame(d, ox, oy, im, WARN if f == "tint_min" else INK)
        text(d, lab, x, y + chh + 14, cw, 54, WARN if f == "tint_min" else INK, bold=True)
    text(d, "ENGINE CAPTURE · floor material changed in memory, one uniform at a time · Zhaohui: \"tint全黑不好看\"",
         0, 1090, W, 42, SOFT)
    save(page, "fig_sweep.png")


def fig_materials():
    """One shader, two materials: as saved, and with only the floor's tint changed."""
    page, d = new()
    for i, (f, t1, t2) in enumerate([("granite_materials", "as saved", "floor uv 6.0 · plinth uv 1.0, tint #6E6680"),
                                     ("granite_one_material_changed", "floor tint only → (0.4, 0.8, 0.4)",
                                      "the plinth's pixel did not change")]):
        img = src(f"{CAP}/{f}.png")
        im = fit(img, 1520, 860)
        x = 40 + i * 1580
        ox, oy = paste_center(page, im, x, 10, 1520, 860)
        frame(d, ox, oy, im)
        text(d, t1, x, 890, 1520, 58, INK, bold=True)
        text(d, t2, x, 970, 1520, 46, SOFT)
    text(d, "ENGINE CAPTURE · granite_floor.tres and granite_plinth.tres both use shaders/granite.gdshader · Zhaohui: \"像木板\"",
         0, 1070, W, 42, SOFT)
    save(page, "fig_materials.png")


def fig_hint():
    """Hint experiment: the capture, predicted vs measured, and the Compatibility source line."""
    page, d = new()
    img = src(f"{CAP}/hint_experiment.png").crop((300, 120, 1500, 960))
    im = fit(img, 1300, 900)
    ox, oy = paste_center(page, im, 40, 20, 1300, 900)
    frame(d, ox, oy, im)
    text(d, "ENGINE CAPTURE · unshaded · Linear · exposure 1.0", 40, 960, 1300, 42, SOFT)
    x = 1400
    heads = ["", "stored", "A predicted", "B predicted", "measured A / B"]
    xs = [x, x + 120, x + 420, x + 800, x + 1180]
    ws = [120, 300, 380, 380, 560]
    for j, h in enumerate(heads):
        text(d, h, xs[j], 40, ws[j], 42, SOFT, bold=True)
    for i, (s, a, b) in enumerate([(64, 64, 137), (128, 128, 188), (192, 192, 224)]):
        y = 120 + i * 150
        card(d, x, y, 1760, 130)
        for j, v in enumerate([str(i + 1), str(s), str(a), str(b), f"{s} / {s}"]):
            text(d, v, xs[j], y + 32, ws[j], 58, WARN if j == 3 else INK, bold=(j == 4))
    card(d, x, 600, 1760, 420, outline=ACCENT)
    text(d, "Godot 4.7.2 Compatibility, drivers/gles3/shaders/scene.glsl", x, 630, 1760, 44, SOFT)
    text(d, "2398:  albedo = srgb_to_linear(albedo);", x + 60, 720, 1700, 50, INK, mono=True, align="left")
    text(d, "2798:  frag_color.rgb = linear_to_srgb(frag_color.rgb);", x + 60, 800, 1700, 50, INK, mono=True, align="left")
    text(d, "every ALBEDO decoded, whatever the hint, then encoded:", x, 890, 1760, 46, INK)
    text(d, "both quads show the stored values", x, 950, 1760, 46, ACCENT, bold=True)
    text(d, "own texture object for B (in memory): still 64 / 128 / 192", 0, 1080, W, 42, SOFT)
    save(page, "fig_hint.png")


def code_lines(rel, nums):
    lines = (REPO / rel).read_text(encoding="utf-8").splitlines()
    return [(n, lines[n - 1].strip()) for n in nums]


def fig_generated():
    """Two lines of Godot's generated shader beside their equivalents in Zhaohui's granite shader."""
    page, d = new()
    gen = code_lines("godot/shaders/standard_generated.gdshader", [7, 19])
    mine = code_lines("godot/shaders/granite.gdshader", [3, 5])
    notes = ["colour: decoded as sRGB · Godot adds mipmapped linear filtering",
             "data: normal map · Godot's hint also feeds the roughness import (editor)"]
    for i in range(2):
        y = 30 + i * 520
        card(d, 40, y, W - 80, 470, outline=ACCENT if i == 1 else RULE)
        text(d, f"generated by Godot · standard_generated.gdshader:{gen[i][0]}", 80, y + 30, W - 160, 42, SOFT, align="left")
        text(d, gen[i][1], 80, y + 95, W - 160, 46, INK, mono=True, align="left")
        text(d, f"Zhaohui's · granite.gdshader:{mine[i][0]}", 80, y + 200, W - 160, 42, SOFT, align="left")
        text(d, mine[i][1], 80, y + 265, W - 160, 46, INK, mono=True, align="left")
        text(d, notes[i], 80, y + 370, W - 160, 48, ACCENT if i == 1 else INK, bold=True, align="left")
    text(d, "standard_generated.gdshader: Convert to ShaderMaterial in the editor, by Zhaohui · nothing in the game uses it",
         0, 1080, W, 42, SOFT)
    save(page, "fig_generated.png")


def fig_limits():
    """What the headless suites prove, what they cannot, and Zhaohui's human checks (verbatim)."""
    page, d = new()
    card(d, 40, 20, 1540, 1040)
    text(d, "headless proves", 40, 50, 1540, 64, GOOD, bold=True)
    for k, s in enumerate(["the shaders parse (non-empty uniform list)", "uniform names, types, hints, defaults",
                           "one material per fighter", "hurt_amount over ticks at 30 / 60 / 144",
                           "materials wired as audited, also from an empty cache",
                           "normal map curl: GL 0.35 / DX 1.65"]):
        text(d, "· " + s, 100, 170 + k * 110, 1440, 50, INK, align="left")
    card(d, 1620, 20, 1540, 1040, outline=ACCENT)
    text(d, "only eyes can say", 1620, 50, 1540, 64, ACCENT, bold=True)
    for k, (q, a) in enumerate([("captures change to red?", "能看出来"), ("hint quads alike?", "一样"),
                                ("sweep: what breaks?", "tint全黑不好看"), ("the granite?", "像木板"),
                                ("muted play: who was hit?", "可以看出"), ("one shader line edited?", "变了")]):
        text(d, q, 1680, 170 + k * 140, 900, 50, INK, align="left")
        text(d, a, 2560, 170 + k * 140, 560, 52, INK, bold=True, align="left")
    text(d, "Zhaohui's words, verbatim (TEST-REPORT A5) · OS-screenshot comparison not done", 1620, 1000, 1540, 38, SOFT)
    save(page, "fig_limits.png")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for f in (fig_predict, fig_controlled, fig_clamp, fig_tests, fig_mutations, fig_sweep, fig_materials,
              fig_hint, fig_generated, fig_limits):
        f()
    out = {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(OUT.glob("fig_*.png"))}
    (OUT / "figures.json").write_text(json.dumps({"figures": out, "sources": used}, indent=2), encoding="utf-8")
    print("\n".join(f"{k}  {v[:12]}" for k, v in out.items()))


if __name__ == "__main__":
    main()
