"""Contact sheets of the Godot captures: evidence/states_contact.png and evidence/flow_contact.png.

Run after godot/tests/capture_states.gd and capture_flow.gd:
    python tools/make_contact.py
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
EVIDENCE = ROOT / "evidence"


def contact(folder, out, cols=3, scale=0.5):
    shots = sorted(folder.glob("*.png"))
    w, h = Image.open(shots[0]).size
    tw, th = int(w * scale), int(h * scale)
    label_h = 18
    rows = (len(shots) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw, rows * (th + label_h)), (24, 22, 28))
    draw = ImageDraw.Draw(sheet)
    try:
        label_font = ImageFont.truetype("arial.ttf", 13)
    except OSError:
        label_font = ImageFont.load_default()
    for i, path in enumerate(shots):
        x, y = (i % cols) * tw, (i // cols) * (th + label_h)
        sheet.paste(Image.open(path).convert("RGB").resize((tw, th), Image.LANCZOS), (x, y + label_h))
        draw.text((x + 4, y + 2), path.stem, fill=(240, 232, 214), font=label_font)
    sheet.save(out)
    print(f"{out.relative_to(ROOT)}: {len(shots)} shots")


if __name__ == "__main__":
    contact(EVIDENCE / "states", EVIDENCE / "states_contact.png", cols=4)
    contact(EVIDENCE / "flow", EVIDENCE / "flow_contact.png", cols=4)
