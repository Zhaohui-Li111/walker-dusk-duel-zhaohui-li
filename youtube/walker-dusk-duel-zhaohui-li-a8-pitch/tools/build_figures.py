#!/usr/bin/env python3
"""Lay out the A8 pitch film's figure stills (adapted from the A7 reel's tool).

Real pixels: frames of capture/a8_round.avi (the scripted-input Movie Maker capture, extracted to
capture/stills/ by tools/extract_stills.sh) and godot/art/env/bg.png. Numbers and log lines are
copied from the logs, TEST-REPORT.md and PROJECT-BRIEF.md. Everything that does not exist yet is
drawn on a panel stamped "CONSTRUCTED · PROPOSED". No King of Fighters imagery is used. Every source
and its SHA-256 goes to figures/figures.json for SOURCES.md.
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
STILLS = REEL.relative_to(REPO).as_posix() + "/capture/stills"


def font(size, bold=False, mono=False):
    if mono:
        return ImageFont.truetype("C:/Windows/Fonts/consolab.ttf" if bold else "C:/Windows/Fonts/consola.ttf", size)
    return ImageFont.truetype("C:/Windows/Fonts/seguisb.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf", size)


def src(rel, mask=True):
    p = REPO / rel
    used[rel] = hashlib.sha256(p.read_bytes()).hexdigest()
    img = Image.open(p).convert("RGB")
    return Image.new("RGB", img.size, PAGE) if (MASKED and mask) else img


def text(d, s, x, y, w, size=54, color=INK, bold=False, mono=False, align="center"):
    f = font(size, bold, mono)
    tw = d.textlength(s, font=f)
    xx = x + (w - tw) / 2 if align == "center" else x
    d.text((xx, y), s, font=f, fill=color)
    return tw


def card(d, x, y, w, h, outline=RULE, fill=CARD, width=4):
    d.rounded_rectangle([x, y, x + w, y + h], radius=22, fill=fill, outline=outline, width=width)


def proposed(d, x, y, w, h):
    """A dashed warn-coloured frame and the stamp: everything inside does not exist yet."""
    for i in range(x, x + w, 40):
        d.line([i, y, min(i + 22, x + w), y], fill=WARN, width=6)
        d.line([i, y + h, min(i + 22, x + w), y + h], fill=WARN, width=6)
    for j in range(y, y + h, 40):
        d.line([x, j, x, min(j + 22, y + h)], fill=WARN, width=6)
        d.line([x + w, j, x + w, min(j + 22, y + h)], fill=WARN, width=6)
    f = font(46, True)
    s = "CONSTRUCTED · PROPOSED"
    tw = d.textlength(s, font=f)
    d.rectangle([x + 30, y - 32, x + 60 + tw, y + 32], fill=PAGE)
    d.text((x + 45, y - 30), s, font=f, fill=WARN)


def realtag(d, x, y, s):
    f = font(40, True)
    tw = d.textlength(s, font=f)
    d.rectangle([x, y, x + tw + 30, y + 58], fill=GOOD)
    d.text((x + 15, y + 4), s, font=f, fill=(255, 255, 255))


def new():
    page = Image.new("RGB", (W, H), PAGE)
    return page, ImageDraw.Draw(page)


def save(page, name):
    page.save(OUT / name)


def still(name, box=None, height=None):
    p = REPO / STILLS / name
    img = src(f"{STILLS}/{name}") if p.exists() else src("godot/art/env/bg.png")
    if box:
        img = img.crop(box)
    if height:
        img = img.resize((int(height * img.width / img.height), height), Image.LANCZOS)
    return img


# ---------------------------------------------------------------- B00 title
def fig_title():
    page, d = new()
    img = still("title.png", height=900)
    ox = 120
    page.paste(img, (ox, 130))
    realtag(d, ox, 60, "REAL CAPTURE · title screen · rev dff6cba")
    x = ox + img.width + 120
    text(d, "Dusk Duel", x, 300, W - x - 100, 150, INK, True, align="left")
    text(d, "Final project pitch", x, 500, W - x - 100, 80, SOFT, align="left")
    text(d, "Zhaohui Li · CSYE 7270 · Fall 2026", x, 640, W - x - 100, 58, SOFT, align="left")
    text(d, "Godot 4.7.2 · GDScript · Compatibility", x, 760, W - x - 100, 58, SOFT, align="left")
    save(page, "fig_title.png")


# ---------------------------------------------------------------- B03 what is new
def fig_new():
    page, d = new()
    text(d, "Exists today (desktop): title · fight vs CPU · K.O. · rematch", 0, 70, W, 64, GOOD, True)
    proposed(d, 100, 240, W - 200, 820)
    cards = [("Web build", ["a full match", "in a browser", "Microsoft Edge"]),
             ("Stronger CPU", ["deliberate choices", "distance-aware attacks", "adjustable difficulty"]),
             ("Wider tests", ["repeated matches", "state transitions", "a report anyone can re-run"])]
    cw = (W - 200 - 4 * 70) // 3
    for i, (title, lines) in enumerate(cards):
        x = 170 + i * (cw + 70)
        card(d, x, 330, cw, 660, WARN)
        text(d, title, x, 380, cw, 84, INK, True)
        for j, s in enumerate(lines):
            text(d, s, x, 560 + j * 120, cw, 60, SOFT)
    save(page, "fig_new.png")


# ---------------------------------------------------------------- B04 comparable
def fig_compare():
    page, d = new()
    cw = (W - 300) // 2
    card(d, 100, 120, cw, 940)
    text(d, "The King of Fighters '97", 100, 200, cw, 84, INK, True)
    text(d, "played by Zhaohui", 100, 320, cw, 56, SOFT)
    for j, s in enumerate(["fast combat", "attack timing", "defence", "a large roster, versus play"]):
        text(d, s, 100, 480 + j * 120, cw, 64, INK)
    text(d, "(named only; no images used)", 100, 960, cw, 44, SOFT)
    x = 200 + cw
    card(d, x, 120, cw, 940)
    text(d, "Dusk Duel", x, 200, cw, 84, INK, True)
    text(d, "one complete single-player match", x, 320, cw, 56, SOFT)
    realtag(d, x + 60, 450, "EXISTS · desktop, one round vs CPU")
    proposed(d, x + 60, 640, cw - 120, 360)
    for j, s in enumerate(["in a browser: no install,", "no online opponent, no setup"]):
        text(d, s, x + 60, 720 + j * 110, cw - 120, 60, INK)
    save(page, "fig_compare.png")


# ---------------------------------------------------------------- B07 first sixty seconds
def fig_sixty():
    page, d = new()
    text(d, "Reader: a technical lead or recruiter · Role: gameplay programmer", 0, 70, W, 64, INK, True)
    proposed(d, 100, 240, W - 200, 820)
    steps = [("0 s", "open the page"), ("~5 s", "press Enter"), ("~10 s", "fight a round"),
             ("~45 s", "see the K.O."), ("~55 s", "rematch")]
    n = len(steps)
    x0, x1, y = 380, W - 380, 560
    d.line([x0, y, x1, y], fill=INK, width=8)
    for i, (t, s) in enumerate(steps):
        x = x0 + i * (x1 - x0) // (n - 1)
        d.ellipse([x - 30, y - 30, x + 30, y + 30], fill=ACCENT)
        text(d, t, x - 250, y - 160, 500, 64, INK, True)
        text(d, s, x - 250, y + 70, 500, 58, SOFT)
    text(d, "no code to read · times are a plan, not a measurement", 0, 900, W, 56, WARN)
    save(page, "fig_sixty.png")


# ---------------------------------------------------------------- B08 tests (real output)
def log_line(rel, needle):
    lines = (REPO / rel).read_text(encoding="utf-8", errors="replace").splitlines()
    used[rel] = hashlib.sha256((REPO / rel).read_bytes()).hexdigest()
    for i, s in enumerate(lines, 1):
        if needle in s:
            return i, s.strip()
    raise SystemExit(f"{needle!r} not in {rel}")


def fig_tests():
    page, d = new()
    realtag(d, 100, 60, "REAL OUTPUT · headless, Godot 4.7.2 · logs in the repo at dff6cba")
    rows = [("round flow, hits, health", "logs/test_runner_60fps.log", "a2–a7"),
            ("hurt-flash shader (A5)", "logs/test_hurt_flash_60fps.log", "a5"),
            ("hit sparks (A6)", "logs/test_hit_spark_state_60fps.log", "a6"),
            ("embers (A6)", "logs/test_embers_state_60fps.log", "a6"),
            ("kick arc edges (A7)", "logs/test_kick_edges_60fps.log", "a7"),
            ("game unchanged: pins (A7)", "logs/test_pins_a7_60fps.log", "a7")]
    y = 200
    for what, rel, tag in rows:
        n, s = log_line(rel, "checks, ")
        card(d, 100, y, W - 200, 135)
        text(d, what, 140, y + 35, 900, 56, INK, True, align="left")
        text(d, s, 1080, y + 35, 900, 60, GOOD, True, mono=True, align="left")
        text(d, f"{rel}:{n}", 1900, y + 45, 1150, 44, SOFT, mono=True, align="left")
        y += 155
    save(page, "fig_tests.png")


# ---------------------------------------------------------------- B09 GPU price (A6, real)
def fig_gpu():
    page, d = new()
    realtag(d, 100, 60, "REAL MEASUREMENT · A6, 2026-11-08 · TEST-REPORT.md “GPU price”")
    text(d, "Intel UHD Graphics · OpenGL 3.3 · Compatibility · Windows 11 · 300 frames per case", 0, 190, W, 56, SOFT)
    hdr = ["Case", "GPU median ms", "Added"]
    rows = [("Hit sparks: 4 bursts on / off", "0.450 / 0.438", "+0.012 ms"),
            ("Embers: field full / hidden", "0.537 / 0.533", "+0.004 ms")]
    xs = [140, 1700, 2500]
    for x, h in zip(xs, hdr):
        text(d, h, x, 330, 900, 60, INK, True, align="left")
    d.line([120, 420, W - 120, 420], fill=RULE, width=4)
    for i, r in enumerate(rows):
        for x, c in zip(xs, r):
            text(d, c, x, 470 + i * 150, 1500, 66, GOOD if c.startswith("+") else INK, c.startswith("+"),
                 mono=c[0].isdigit() or c.startswith("+"), align="left")
    text(d, "The editor's Visual Profiler read 0 GPU time here; these come from", 0, 830, W, 52, SOFT)
    text(d, "RenderingServer.viewport_get_measured_render_time_gpu (godot/tests/gpu_price.gd)", 0, 900, W, 52, SOFT, mono=True)
    text(d, "Next: the same measurement, desktop against the browser (proposed)", 0, 1010, W, 56, WARN, True)
    used["TEST-REPORT.md"] = hashlib.sha256((REPO / "TEST-REPORT.md").read_bytes()).hexdigest()
    save(page, "fig_gpu.png")


# ---------------------------------------------------------------- B10 out of scope
def fig_out():
    page, d = new()
    text(d, "Deliberately out", 0, 80, W, 90, INK, True)
    items = ["online play / multiplayer", "a second stage", "character select, equipment",
             "accounts, cloud saves, progress saves", "a large roster of characters and moves"]
    for i, s in enumerate(items):
        y = 260 + i * 160
        f = font(76)
        tw = d.textlength(s, font=f)
        x = (W - tw) / 2
        d.text((x, y), s, font=f, fill=SOFT)
        d.line([x - 20, y + 52, x + tw + 20, y + 52], fill=WARN, width=8)
    save(page, "fig_out.png")


# ---------------------------------------------------------------- B11 milestone 1
def fig_milestone():
    page, d = new()
    text(d, "Milestone 1 · a full match in a web browser · this laptop, Microsoft Edge", 0, 60, W, 62, INK, True)
    proposed(d, 100, 200, W - 200, 900)
    crit = ["loads in the browser", "start from the title screen", "move, attack, block work",
            "CPU approaches, attacks, defends", "shaders, particles, animation draw", "the round reaches K.O.",
            "a rematch plays"]
    for i, s in enumerate(crit):
        col, row = divmod(i, 4)
        x = 220 + col * 1450
        y = 300 + row * 185
        d.rectangle([x, y + 10, x + 70, y + 80], outline=INK, width=6)
        text(d, s, x + 110, y + 10, 1300, 64, INK, align="left")
    text(d, "proof: a browser recording + a test report naming the Edge version", 1670, 920, 1350, 48, WARN, align="left")
    save(page, "fig_milestone.png")


# ---------------------------------------------------------------- B12 risk
def fig_risk():
    page, d = new()
    cw = (W - 300) // 2
    img = still("fight.png", height=int(cw * 9 / 16))
    page.paste(img, (100, 180))
    realtag(d, 100, 100, "REAL CAPTURE · desktop · rev dff6cba")
    text(d, "Desktop (Windows, Compatibility)", 100, 1010, cw, 56, INK, True)
    x = 200 + cw
    proposed(d, x, 180, cw, img.height)
    text(d, "Web build: not made yet", x, 180 + img.height // 2 - 90, cw, 72, WARN, True)
    text(d, "shader colour? particle blending? frame rate?", x, 180 + img.height // 2 + 20, cw, 54, SOFT)
    text(d, "Browser (Edge)", x, 1010, cw, 56, INK, True)
    save(page, "fig_risk.png")


# ---------------------------------------------------------------- B13 why
def fig_why():
    page, d = new()
    cw = (W - 300) // 2
    card(d, 100, 100, cw, 980, GOOD)
    text(d, "Have, with evidence", 100, 150, cw, 76, GOOD, True)
    have = [("shaders, materials", "a5"), ("particle effects", "a6"), ("animation clips", "a7"),
            ("edge tests, tuning log", "a7"), ("round flow, basic CPU", "6317281")]
    for i, (s, tag) in enumerate(have):
        y = 320 + i * 140
        text(d, s, 170, y, cw - 400, 64, INK, align="left")
        text(d, tag, 100 + cw - 330, y, 260, 64, GOOD, True, mono=True, align="left")
    x = 200 + cw
    card(d, x, 100, cw, 980, WARN)
    text(d, "New to me", x, 150, cw, 76, WARN, True)
    for i, s in enumerate(["a smarter CPU opponent", "shipping Godot to the web", "repeatable benchmarks",
                           "wider gameplay tests"]):
        text(d, s, x + 70, 320 + i * 140, cw - 140, 64, INK, align="left")
    save(page, "fig_why.png")


# ---------------------------------------------------------------- B14 end
def fig_end():
    page, d = new()
    text(d, "Dusk Duel", 0, 260, W, 170, INK, True)
    text(d, "a fighting game a stranger can open, play and verify", 0, 500, W, 74, SOFT)
    text(d, "Zhaohui Li · CSYE 7270 · Fall 2026", 0, 700, W, 64, INK)
    text(d, "Godot 4.7.2 · GL Compatibility · Web export (proposed)", 0, 810, W, 58, SOFT)
    save(page, "fig_end.png")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for f in (fig_title, fig_new, fig_compare, fig_sixty, fig_tests, fig_gpu, fig_out, fig_milestone,
              fig_risk, fig_why, fig_end):
        f()
        print("wrote", f.__name__)
    if not MASKED:
        (OUT / "figures.json").write_text(json.dumps({"sources": used}, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
