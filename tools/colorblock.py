"""Colour-block mannequins: img2img starting images for walker-dusk-duel (written by Claude Code).

Three prompt-only rounds (36 images were planned, 12 made) showed SDXL would not bind the sheet's colours
to the right body parts and never drew a headband. These images paint the CHARACTER-SHEET palette
onto each pose, on the plain green background, so img2img starts from the right colours in the right
places and the model only restyles them. They are design inputs, not game art.

Everything is rebuilt from poses.json (keypoints, bones, widths), so the same code runs locally and
inside the Colab notebook, which pastes this file into a cell.
"""
import math

from PIL import Image, ImageDraw, ImageFilter

GREEN = (0, 177, 64)
INK = (30, 27, 34)
PALETTE = {
    "akaken": {"skin": (232, 178, 122), "top": (217, 72, 43), "pants": (46, 42, 51),
               "belt": (245, 197, 66), "cloth": (242, 230, 208), "hair": (30, 27, 34)},
    "aotake": {"skin": (217, 162, 122), "top": (47, 163, 176), "pants": (46, 42, 51),
               "belt": (23, 50, 77), "hat": (216, 182, 118), "hair": (30, 27, 34)},
}
FEATURE = {"akaken": "topknot", "aotake": "hat"}


def _add(p, *vs):
    x, y = p
    for vx, vy in vs:
        x, y = x + vx, y + vy
    return (x, y)


def _mul(v, s):
    return (v[0] * s, v[1] * s)


def _thick(d, a, b, w, fill):
    d.line((a, b), fill=fill, width=int(w))
    for p in (a, b):
        d.ellipse((p[0] - w / 2, p[1] - w / 2, p[0] + w / 2, p[1] + w / 2), fill=fill)


def _dot(d, p, r, fill):
    d.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill=fill)


def frame(keypoints, bones):
    """Recover the torso axis t, facing f and head centre from the stored keypoints."""
    k = [tuple(p) if p else None for p in keypoints]
    hip = ((k[8][0] + k[11][0]) / 2, (k[8][1] + k[11][1]) / 2)
    dx, dy = k[1][0] - hip[0], k[1][1] - hip[1]
    n = math.hypot(dx, dy)
    t = (dx / n, dy / n)
    f = (-t[1], t[0])
    head_c = _add(k[1], _mul(t, bones["head_r"] + 8), _mul(f, 6))
    return k, t, f, head_c


def draw_colorblock(fighter_id, pose, bones, widths, size):
    """pose: one entry of poses.json["fighters"][id]["poses"]. Returns an RGB image."""
    k, t, f, head_c = frame(pose["keypoints"], bones)
    c = PALETTE[fighter_id]
    hr = bones["head_r"]
    w = widths
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    def leg(hp, kn, an):
        _thick(d, k[hp], k[kn], w["leg"], c["pants"] + (255,))
        _thick(d, k[kn], k[an], w["leg"] * 0.85, c["pants"] + (255,))
        _thick(d, k[an], _add(k[an], _mul(f, w["foot"] * 0.6)), w["leg"] * 0.5, c["skin"] + (255,))

    def arm(sh, el, wr):
        sleeve = c["top"] if fighter_id == "aotake" else c["skin"]      # Akaken is sleeveless
        _thick(d, k[sh], k[el], w["arm"], sleeve + (255,))
        _thick(d, k[el], k[wr], w["arm"] * 0.9, c["skin"] + (255,))
        fist = c["cloth"] if fighter_id == "akaken" else c["skin"]      # cream hand wraps
        _dot(d, k[wr], w["fist_r"], fist + (255,))

    leg(11, 12, 13)
    arm(5, 6, 7)
    pad = hr * 0.55 - bones["shoulder"] * 0.3
    torso = [_add(p, _mul(f, (-1 if i in (0, 3) else 1) * pad)) for i, p in enumerate([k[2], k[5], k[11], k[8]])]
    if fighter_id == "aotake":                                           # robe covers the thighs
        hem = [_add(p, _mul(t, -bones["thigh"] * 0.55)) for p in (torso[2], torso[3])]
        d.polygon([torso[0], torso[1], hem[0], hem[1]], fill=c["top"] + (255,))
    else:
        d.polygon(torso, fill=c["top"] + (255,))
    belt_a, belt_b = _add(torso[3], _mul(t, 14)), _add(torso[2], _mul(t, 14))
    _thick(d, belt_a, belt_b, 22, c["belt"] + (255,))
    _thick(d, k[1], _add(k[1], _mul(t, 30)), bones["shoulder"] * 0.8, c["skin"] + (255,))
    _dot(d, head_c, hr, c["skin"] + (255,))
    # hair over the crown and back of the head, then the face back on top at the front
    _dot(d, _add(head_c, _mul(f, -hr * 0.3), _mul(t, hr * 0.35)), hr * 0.78, c["hair"] + (255,))
    _dot(d, _add(head_c, _mul(f, hr * 0.28), _mul(t, -hr * 0.18)), hr * 0.76, c["skin"] + (255,))
    if FEATURE[fighter_id] == "topknot":
        _dot(d, _add(head_c, _mul(t, hr + 22), _mul(f, -10)), 28, c["hair"] + (255,))
        band_a = _add(head_c, _mul(f, -hr * 0.98), _mul(t, hr * 0.32))
        band_b = _add(head_c, _mul(f, hr * 0.98), _mul(t, hr * 0.32))
        _thick(d, band_a, band_b, 20, c["cloth"] + (255,))
        tail0 = _add(head_c, _mul(f, -hr * 0.95), _mul(t, hr * 0.3))
        _thick(d, tail0, _add(tail0, _mul(f, -70), _mul(t, -30)), 16, c["cloth"] + (255,))
        _thick(d, tail0, _add(tail0, _mul(f, -60), _mul(t, 5)), 14, c["cloth"] + (255,))
    else:
        b0 = _add(head_c, _mul(f, -hr * 0.8))
        _thick(d, b0, _add(b0, _mul(t, -hr * 2.2), _mul(f, -20)), 18, c["hair"] + (255,))
        brim_c = _add(head_c, _mul(t, hr * 0.55))
        d.polygon([_add(brim_c, _mul(f, -hr * 1.9)), _add(brim_c, _mul(t, hr * 0.95)),
                   _add(brim_c, _mul(f, hr * 1.9))], fill=c["hat"] + (255,))
    # face: one eye on the facing side
    eye = _add(head_c, _mul(f, hr * 0.5), _mul(t, hr * 0.05))
    _dot(d, eye, 9, INK + (255,))
    leg(8, 9, 10)
    arm(2, 3, 4)

    # thick dark outline = the silhouette grown by a few pixels, under the colours
    alpha = layer.split()[3]
    outline = alpha.filter(ImageFilter.MaxFilter(11))
    img = Image.new("RGB", size, GREEN)
    img.paste(Image.new("RGB", size, INK), (0, 0), outline)
    img.paste(layer, (0, 0), layer)
    return img


def main():
    """Local run: write design/character/<fighter>/colorblock/*.png and a contact sheet."""
    import json
    from pathlib import Path
    root = Path(__file__).resolve().parent.parent / "design" / "character"
    data = json.loads((root / "poses.json").read_text())
    size = tuple(data["canvas"])
    tiles = []
    for fid, fdata in data["fighters"].items():
        out = root / fid / "colorblock"
        out.mkdir(parents=True, exist_ok=True)
        for name, pose in fdata["poses"].items():
            img = draw_colorblock(fid, pose, fdata["bones"], fdata["widths"], size)
            img.save(out / f"{name}.png")
            tiles.append(img)
    tw, th = size[0] // 4, size[1] // 4
    cols = 8
    sheet = Image.new("RGB", (cols * tw, math.ceil(len(tiles) / cols) * th), (245, 242, 235))
    for i, img in enumerate(tiles):
        sheet.paste(img.resize((tw, th), Image.LANCZOS), ((i % cols) * tw, (i // cols) * th))
    sheet.save(root / "colorblock_sheet.png")
    print("colour blocks:", len(tiles))


if __name__ == "__main__":
    main()
