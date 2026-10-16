#!/usr/bin/env python3
"""Lay out the A3 film's figure stills from files already in the repo (no new art).

Panels are existing images pasted unchanged except for cropping and scaling: Zhaohui's own
Blender screenshots (evidence/blender/), the engine stills recorded by tools/capture_stills.gd
(capture/stills/), and the MCP `look` renders Claude took during the build (capture/mcp_look/,
644 px originals). Numbers are copied from CHANGE-BRIEF.md and the recorded check output
(evidence/check-props3d.txt). The only new pixels are labels and the page. Every source and its
SHA-256 goes to figures/figures.json for SOURCES.md.
"""
import hashlib
import json
import pathlib
import sys

from PIL import Image, ImageDraw, ImageFont

REEL = pathlib.Path(__file__).resolve().parent.parent
REPO = REEL.parent.parent
MASKED = "--masked" in sys.argv     # labels only: every pasted source image becomes a blank panel
OUT = REEL / ("_qc/typecheck-masked/figures" if MASKED else "figures")
PAGE = (255, 253, 248)
INK = (61, 57, 41)
SOFT = (110, 100, 86)
ACCENT = (217, 119, 87)
WARN = (164, 74, 50)
W, H = 3200, 1160
used = {}


def font(size, bold=False):
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


def label(d, text, x, y, w, size=54, color=INK, bold=False):
    f = font(size, bold)
    d.text((x + (w - d.textlength(text, font=f)) / 2, y), text, font=f, fill=color)


def frame(d, ox, oy, img, color=INK, width=4):
    d.rectangle([ox - width, oy - width, ox + img.width + width - 1, oy + img.height + width - 1], outline=color, width=width)


def pair(name, left, right, ltxt, rtxt, lsub, rsub, crop_l=None, crop_r=None, bad="right"):
    """Two panels side by side, a caption and a sub-caption under each."""
    page = Image.new("RGB", (W, H), PAGE)
    d = ImageDraw.Draw(page)
    cw, ih = 1540, 900
    for i, (rel, crop, t1, t2) in enumerate(((left, crop_l, ltxt, lsub), (right, crop_r, rtxt, rsub))):
        img = src(rel)
        if crop:
            img = img.crop(crop)
        im = fit(img, cw, ih)
        x = 40 + i * (cw + 40)
        ox, oy = paste_center(page, im, x, 10, cw, ih)
        frame(d, ox, oy, im, WARN if (bad == ("left", "right")[i]) else INK)
        label(d, t1, x, ih + 40, cw, size=60, bold=True)
        label(d, t2, x, ih + 120, cw, size=50, color=SOFT)
    page.save(OUT / name)


def fig_brief():
    """CHANGE-BRIEF.md A3: the three specs, verbatim numbers."""
    page = Image.new("RGB", (W, H), PAGE)
    d = ImageDraw.Draw(page)
    props = [("PROP-LANTERN", "stone lantern", "0.60 × 0.60 × 1.40", "150", "8 / 8 / 6 / 6 segments",
              ["#6E6680", "#F5C542", "#4E475C"]),
             ("PROP-MAKIWARA", "striking post", "0.30 × 0.30 × 1.50", "120", "pad centre 1.20 m",
              ["#8A5A3B", "#D8B676", "#F2E6D0", "#6E6680"]),
             ("PROP-TAIKO", "drum on a stand", "0.70 × 0.55 × 0.95", "200", "12 segments, turned 90°",
              ["#D9482B", "#F2E6D0", "#1E1B22"])]
    cw = 1010
    for i, (pid, what, size, budget, note, cols) in enumerate(props):
        x = 50 + i * (cw + 40)
        d.rounded_rectangle([x, 20, x + cw, 1000], radius=24, outline=(204, 198, 186), width=4, fill=(255, 255, 255))
        label(d, pid, x, 50, cw, size=68, bold=True)
        label(d, what, x, 140, cw, size=54, color=SOFT)
        label(d, "W × D × H (m)", x, 250, cw, size=46, color=SOFT)
        label(d, size, x, 310, cw, size=78, bold=True)
        label(d, "triangle budget", x, 450, cw, size=46, color=SOFT)
        label(d, budget, x, 505, cw, size=78, bold=True)
        label(d, note, x, 640, cw, size=52)
        sw = 150
        x0 = x + (cw - (len(cols) * sw + (len(cols) - 1) * 24)) // 2
        for k, c in enumerate(cols):
            d.rectangle([x0 + k * (sw + 24), 760, x0 + k * (sw + 24) + sw, 880], fill=c, outline=INK, width=3)
        label(d, "Principled BSDF base colours", x, 905, cw, size=42, color=SOFT)
    label(d, "all three: origin at the underside centre, Z = 0 · tolerance ±0.02 m · rotation and scale applied",
          0, 1050, W, size=50)
    page.save(OUT / "fig_brief.png")


def fig_numbers():
    """Brief vs Blender vs Godot headless, from CHANGE-BRIEF and the recorded check output."""
    page = Image.new("RGB", (W, H), PAGE)
    d = ImageDraw.Draw(page)
    head = ["", "brief W×D×H", "Blender X×Y×Z", "Godot AABB x×y×z", "floor gap", "tris / budget"]
    rows = [["LANTERN", "0.60×0.60×1.40", "0.60×0.60×1.40", "0.600×1.400×0.600", "0.0000", "100 / 150"],
            ["MAKIWARA", "0.30×0.30×1.50", "0.30×0.30×1.50", "0.300×1.500×0.300", "0.0000", "92 / 120"],
            ["TAIKO", "0.70×0.55×0.95", "0.70×0.55×0.95", "0.700×0.950×0.550", "0.0000", "168 / 200"]]
    xs = [40, 480, 1010, 1540, 2240, 2660]
    ws = [440, 530, 530, 700, 420, 500]
    for j, h in enumerate(head):
        label(d, h, xs[j], 40, ws[j], size=50, color=SOFT, bold=True)
    for i, r in enumerate(rows):
        y = 190 + i * 240
        d.rounded_rectangle([30, y - 20, W - 30, y + 170], radius=18, fill=(255, 255, 255), outline=(204, 198, 186), width=3)
        for j, v in enumerate(r):
            label(d, v, xs[j], y + 35, ws[j], size=68 if j == 0 else 64, bold=(j in (0, 3)))
    d.rectangle([1540 + 60, 925, 1540 + 640, 935], fill=ACCENT)
    label(d, "HEADLESS · tests/check_props3d.gd · 49 checks, 0 failed · scale 1,1,1 · rotation 0 · tallest axis Y",
          0, 990, W, size=50)
    page.save(OUT / "fig_numbers.png")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    fig_brief()
    fig_numbers()
    # Zhaohui's own screenshot, cropped to the add-on panel and the Transform panel beside it
    page = Image.new("RGB", (W, H), PAGE)
    shot = src("evidence/blender/zhaohui_object_mode_taiko_selected.png").crop((1240, 130, 1910, 700))
    im = fit(shot, W - 40, H - 20)
    ox, oy = paste_center(page, im, 20, 10, W - 40, H - 20)
    frame(ImageDraw.Draw(page), ox, oy, im)
    page.save(OUT / "fig_session.png")
    pair("fig_zhaohui_views.png", "evidence/blender/zhaohui_bottom_view_taiko.png",
         "evidence/blender/zhaohui_back_view_taiko.png", "from below", "from behind",
         "Zhaohui's screenshot, 16:41", "Zhaohui's screenshot, 16:41",
         crop_l=(640, 440, 940, 665), crop_r=(635, 370, 935, 595), bad=None)
    REL = REEL.relative_to(REPO).as_posix()
    pair("fig_taiko_build.png", f"{REL}/capture/mcp_look/1552_taiko_angles.png",
         f"{REL}/capture/stills/real_taiko_floor.png", "Blender, after the origin fix",
         "Godot prop room, same mesh", "MCP look render (Claude), 644 px", "engine still, 4K",
         crop_r=(1100, 150, 2900, 1500), bad=None)
    pair("fig_floor_check.png", f"{REL}/capture/stills/real_taiko_floor.png",
         f"{REL}/capture/stills/raised_taiko_floor.png", "real scene: gap 0.0000",
         "test copy: raised 0.05 m", "check: 49 checks, 0 failed", "check: 49 checks, 1 failed",
         crop_l=(1550, 1150, 2450, 1600), crop_r=(1550, 1150, 2450, 1600))
    pair("fig_hand_edit.png", f"{REL}/capture/mcp_look/1629_taiko_after_hand_edit.png",
         f"{REL}/capture/mcp_look/1635_taiko_repaired.png", "after the hand edit (saved 16:28)",
         "after Claude's repair, 16:35", "MCP look render · head 0 m thick", "MCP look render · head 0.02 m",
         crop_l=(0, 322, 644, 644), crop_r=(0, 322, 644, 644), bad="left")
    pair("fig_makiwara.png", f"{REL}/capture/mcp_look/1549_makiwara_round_bands.png",
         f"{REL}/capture/mcp_look/1550_makiwara_chamfered_bands.png", "round bands, r 0.12",
         "chamfered rings 0.19 × 0.17", "MCP look render · 4 cm past the pad", "MCP look render · 1.5 cm",
         crop_l=(322, 322, 644, 644), crop_r=(322, 322, 644, 644), bad="left")
    out = {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(OUT.glob("fig_*.png"))}
    (OUT / "figures.json").write_text(json.dumps({"figures": out, "sources": used}, indent=2), encoding="utf-8")
    print("\n".join(f"{k}  {v[:12]}" for k, v in out.items()))


if __name__ == "__main__":
    main()
