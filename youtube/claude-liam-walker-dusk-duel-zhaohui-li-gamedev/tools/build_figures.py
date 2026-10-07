#!/usr/bin/env python3
"""Lay out the film's figure stills from files already in the repo (no new art).

Every panel is an existing file, pasted unchanged except for scaling; the only new pixels
are labels, arrows and the page. Sources and their SHA-256 go to figures/figures.json so
SOURCES.md can cite them.
"""
import hashlib
import json
import pathlib
import sys

from PIL import Image, ImageDraw, ImageFont

REEL = pathlib.Path(__file__).resolve().parent.parent
REPO = REEL.parent.parent
OUT = REEL / ("_qc/typecheck-masked/figures" if "--masked" in sys.argv else "figures")
FONTS = pathlib.Path("D:/courses/7270/brutalist.art-main/brutalist.art-main/runtime/fonts")
PAGE = (255, 253, 248)
INK = (61, 57, 41)
SOFT = (110, 100, 86)
ACCENT = (217, 119, 87)
W, H = 3200, 1160
used = {}


def font(size, serif=False):
    if serif:
        for p in (FONTS / "EB_Garamond").glob("*.ttf"):
            if "Medium" in p.name or "Regular" in p.name or "VariableFont" in p.name:
                return ImageFont.truetype(str(p), size)
    for p in (FONTS / "Inter").rglob("*.ttf"):
        return ImageFont.truetype(str(p), size)
    return ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", size)


MASKED = "--masked" in sys.argv     # labels only: every pasted source image becomes a blank panel


def src(rel):
    p = REPO / rel
    used[rel] = hashlib.sha256(p.read_bytes()).hexdigest()
    img = Image.open(p)
    if MASKED:
        return Image.new(img.mode if img.mode in ("RGB", "RGBA") else "RGB", img.size,
                         (255, 253, 248, 255) if img.mode == "RGBA" else (255, 253, 248))
    return img


def fit(img, box_w, box_h, nearest=False):
    s = min(box_w / img.width, box_h / img.height)
    return img.resize((max(1, round(img.width * s)), max(1, round(img.height * s))),
                      Image.NEAREST if nearest else Image.LANCZOS)


def paste_center(page, img, x, y, w, h):
    ox, oy = x + (w - img.width) // 2, y + (h - img.height) // 2
    page.paste(img, (ox, oy), img if img.mode == "RGBA" else None)
    return ox, oy


def label(d, text, x, y, w, size=46, color=INK):
    f = font(size)
    tw = d.textlength(text, font=f)
    d.text((x + (w - tw) / 2, y), text, font=f, fill=color)


def arrow(d, x0, x1, y):
    d.line([(x0, y), (x1 - 24, y)], fill=ACCENT, width=10)
    d.polygon([(x1, y), (x1 - 40, y - 26), (x1 - 40, y + 26)], fill=ACCENT)


def checker(w, h, cell=24):
    img = Image.new("RGB", (w, h), (236, 232, 222))
    d = ImageDraw.Draw(img)
    for yy in range(0, h, cell):
        for xx in range(0, w, cell):
            if (xx // cell + yy // cell) % 2:
                d.rectangle([xx, yy, xx + cell, yy + cell], fill=(222, 216, 204))
    return img


def fig_design():
    """CHARACTER-SHEET collision panel for 06_punch_jab next to its colour-block mannequin."""
    page = Image.new("RGB", (W, H), PAGE)
    d = ImageDraw.Draw(page)
    sheet = src("design/character/akaken/collision.png").convert("RGB")
    panel = sheet.crop((277, 480, 554, 912))           # the 06_punch_jab cell, label included
    block = src("design/character/akaken/colorblock/06_punch_jab.png").convert("RGB")
    # CHARACTER-SHEET.md palette table, verbatim
    pal = [("#D9482B", "gi"), ("#F2E6D0", "wraps, headband"), ("#F5C542", "belt"),
           ("#E8B27A", "skin"), ("#1E1B22", "outline, pants")]
    a = fit(panel, 900, 1010)
    b = fit(block, 760, 1010)
    paste_center(page, a, 40, 10, 900, 1010)
    paste_center(page, b, 1000, 10, 760, 1010)
    label(d, "pose 06 + boxes", 40, 1060, 900, size=54)
    label(d, "colour-block mannequin", 1000, 1060, 760, size=54)
    d.text((1900, 30), "palette (CHARACTER-SHEET)", font=font(64), fill=INK)
    for i, (hexc, name) in enumerate(pal):
        y = 150 + i * 200
        d.rectangle([1900, y, 2080, y + 160], fill=hexc, outline=INK, width=4)
        d.text((2130, y + 8), name, font=font(66), fill=INK)
        d.text((2130, y + 90), hexc, font=font(56), fill=SOFT)
    page.save(OUT / "fig_design_punch.png")


def fig_pipeline():
    """Skeleton -> colour block -> two candidates -> exported sprite, all for the punch."""
    page = Image.new("RGB", (W, H), PAGE)
    d = ImageDraw.Draw(page)
    pose = src("design/character/akaken/openpose/06_punch_jab.png").convert("RGB")
    block = src("design/character/akaken/colorblock/06_punch_jab.png").convert("RGB")
    cands = src("design/generations/sheets/CHAR-AK-PUNCH_20261006-004722.png").convert("RGB")
    s201 = cands.crop((0, 0, 287, 420))
    s202 = cands.crop((287, 0, 574, 420))
    sprite = src("godot/art/akaken/punch.png").convert("RGBA")
    cols = [(pose, "OpenPose skeleton", "controls the pose"),
            (block, "colour block", "img2img start, 0.75"),
            (s201, "s201  score 47.4", "accepted"),
            (s202, "s202  score 51.8", "rejected"),
            (sprite, "punch.png  108x158", "cut out, scaled x0.1296")]
    cw, gap, top, ih = 560, 75, 20, 840
    for i, (img, t1, t2) in enumerate(cols):
        x = 40 + i * (cw + gap)
        if img.mode == "RGBA":
            bg = checker(cw, ih)
            page.paste(bg, (x, top))
            im = fit(img, cw - 40, ih - 40, nearest=True)
            paste_center(page, im, x, top, cw, ih)
        else:
            im = fit(img, cw, ih)
            ox, oy = paste_center(page, im, x, top, cw, ih)
            if i == 3:
                d.line([(ox + 20, oy + 20), (ox + im.width - 20, oy + im.height - 20)],
                       fill=(164, 74, 50), width=8)
        label(d, t1, x, top + ih + 40, cw, size=58)
        label(d, t2, x, top + ih + 120, cw, size=52, color=INK if i == 2 else SOFT)
        if i == 2:                                   # emphasis is a bar, never accent-coloured text
            d.rectangle([x + 150, top + ih + 190, x + cw - 150, top + ih + 200], fill=ACCENT)
        if i in (0, 1):
            arrow(d, x + cw + 6, x + cw + gap - 6, top + ih // 2)
    arrow(d, 40 + 3 * (cw + gap) + cw + 6, 40 + 4 * (cw + gap) - 6, top + ih // 2)
    page.save(OUT / "fig_pipeline_punch.png")


def fig_rounds():
    """Top rows of the five reference-round contact sheets: prompts alone vs colour blocks."""
    page = Image.new("RGB", (W, H), PAGE)
    d = ImageDraw.Draw(page)
    sheets = sorted((REPO / "design/generations/sheets").glob("CHAR-AK-REF_*.png"))
    rows = [(0, "round 1  prompt only"), (2, "round 3  prompt only"),
            (3, "round 4  colour block, strength 0.6"), (4, "round 5  colour block, strength 0.75")]
    rw, rh = 1550, 570
    for k, (idx, text) in enumerate(rows):
        rel = sheets[idx].relative_to(REPO).as_posix()
        top = src(rel).convert("RGB").crop((0, 0, 1148, 420))
        im = fit(top, rw, rh - 90)
        x = 30 + (k % 2) * (rw + 40)
        y = 10 + (k // 2) * (rh + 10)
        paste_center(page, im, x, y, rw, rh - 90)
        label(d, text, x, y + rh - 84, rw, size=60, color=INK)
        if k == 3:
            d.rectangle([x + 300, y + rh - 8, x + rw - 300, y + rh + 2], fill=ACCENT)
    page.save(OUT / "fig_rounds_reference.png")


def fig_audio():
    """The measured SFX candidates (Stage 1 check image) as rendered by the audio notebook."""
    page = Image.new("RGB", (W, H), PAGE)
    spec = src("design/generations/audio/checks/SFX_candidates_spectrograms.png").convert("RGB")
    im = fit(spec, 2000, 1140)
    paste_center(page, im, 10, 10, 2000, 1140)
    d = ImageDraw.Draw(page)
    rows = [("whiff", "s12", "brightest, 5792 Hz"), ("hit", "s12", "0 ms lead-in, heaviest"),
            ("block", "s14", "bright clack, 2780 Hz"), ("K.O.", "s13", "rings out inside 2.5 s")]
    d.text((2080, 20), "rows: events · columns: seeds 11-14", font=font(46), fill=SOFT)
    for i, (ev, seed, why) in enumerate(rows):
        y = 150 + i * 250
        d.text((2080, y), f"{ev}: {seed}", font=font(72), fill=INK)
        if i in (1, 2):
            d.rectangle([2050, y + 10, 2062, y + 170], fill=ACCENT)
        d.text((2080, y + 95), why, font=font(52), fill=INK)
    page.save(OUT / "fig_sfx_candidates.png")


def main():
    OUT.mkdir(exist_ok=True)
    fig_design()
    fig_pipeline()
    fig_rounds()
    fig_audio()
    out = {}
    for f in sorted(OUT.glob("fig_*.png")):
        out[f.name] = hashlib.sha256(f.read_bytes()).hexdigest()
    (OUT / "figures.json").write_text(json.dumps({"figures": out, "sources": used}, indent=2),
                                      encoding="utf-8")
    print("\n".join(f"{k}  {v[:12]}" for k, v in out.items()))


if __name__ == "__main__":
    main()
