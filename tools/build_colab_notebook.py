"""Builds notebooks/generate_images.ipynb (written by Claude Code).

Run from the project root:  python tools/build_colab_notebook.py notebooks/generate_images.ipynb
"""
import json, sys
from pathlib import Path

cells = []
def md(s): cells.append(("markdown", s.strip("\n")))
def code(s): cells.append(("code", s.strip("\n")))

md(r'''
# walker-dusk-duel — image generation (Google Colab, free T4)

Generates the character and environment art for the asset slice with **diffusers**, saves every
output to Google Drive, and appends **one row per generation** to `asset_log.csv` / `ASSET-LOG.md`.

Written by Claude Code. The images come from the open models listed in cell 4, not from Claude.

**Before running**

1. `Runtime → Change runtime type → T4 GPU`.
2. In Google Drive, create `MyDrive/walker-dusk-duel/` and upload the repo's `design/character/`
   folder into `MyDrive/walker-dusk-duel/design/` (so `.../design/character/poses.json` exists).
3. Run cells 1–6 once per session. Then work stage by stage. Nothing is accepted automatically:
   look at each contact sheet and record your decision with `review()`.

**Rights rules (from the assignment):** no franchise, character, brand or named-artist style in any
prompt. `check_prompt()` blocks a list of such words before anything is generated.

**Order:** Stage 1 reference → choose → Stage 2 poses → Stage 3 opponent → Stage 4 background →
Stage 5 export → copy `ASSET-LOG.md`, `thumbs/`, `sheets/` and `export/` back into the repo.
''')

md("## 1 · Mount Drive and set paths")
code(r'''
import os, sys
from pathlib import Path

IN_COLAB = "google.colab" in sys.modules
if IN_COLAB:
    from google.colab import drive
    drive.mount("/content/drive")

ROOT = Path(os.environ.get("DUSK_ROOT", "/content/drive/MyDrive/walker-dusk-duel"))
CHAR = ROOT / "design" / "character"
GEN = ROOT / "design" / "generations"           # same relative paths as the repo, so log links survive the copy
RAW = ROOT / "raw"                               # full-size outputs: Drive only, never committed
THUMBS, SHEETS, CHECKS = GEN / "thumbs", GEN / "sheets", GEN / "checks"
EXPORT = ROOT / "godot" / "art"
for d in (RAW, THUMBS, SHEETS, CHECKS, EXPORT):
    d.mkdir(parents=True, exist_ok=True)
LOG_CSV, LOG_MD = ROOT / "asset_log.csv", ROOT / "ASSET-LOG.md"

assert (CHAR / "poses.json").exists(), f"Upload design/character/ to {CHAR.parent} first"
print("project root:", ROOT)
''')

md("## 2 · Install libraries")
code(r'''
%pip install -q -U diffusers transformers accelerate safetensors huggingface_hub
''')

md("## 3 · Prompts and the rights check")
code(r'''
import re

# Words that must never reach a prompt: franchises, their characters, brands, studios,
# and "style of <artist>" phrasing. Extend this list; never shorten it to get a prompt through.
BANNED = [
    r"mortal\s*kombat", r"\bmk\d*\b", r"scorpion", r"sub[\s-]?zero", r"raiden", r"liu\s*kang",
    r"street\s*fighter", r"\bryu\b", r"tekken", r"king\s*of\s*fighters", r"capcom", r"netherrealm",
    r"nintendo", r"disney", r"pixar", r"ghibli", r"dreamworks", r"marvel", r"\bdc\b", r"bruce\s*lee",
    r"\bin the style of\b", r"\bstyle of\b", r"\bby [A-Z][a-z]+", r"artstation", r"trending on",
]

def check_prompt(text):
    hits = [p for p in BANNED if re.search(p, text, flags=re.IGNORECASE if not p.startswith(r"\bby") else 0)]
    if hits:
        raise ValueError(f"Prompt blocked by rights check, matched: {hits}")
    return text

STYLE = ("2D fighting game character sprite, flat cel shading, thick dark outline, simple shapes, "
         "flat colors, clean lineart, full body, three-quarter side view facing right, "
         "plain solid bright green background")

AKAKEN = ("cartoon martial artist, short stocky young fighter, big round head, about five heads tall, "
          "oversized fists wrapped in cream cloth bandages, black hair in a topknot bun on top of the head, "
          "cream headband with two tails flowing behind the head, sleeveless red-orange gi top, "
          "yellow belt, dark charcoal pants, bare feet")

AOTAKE = ("cartoon martial artist, tall lean fighter with long legs, wide conical straw hat, "
          "long black braid hanging down the back, teal robe, dark navy sash, dark pants, bare feet")

NEGATIVE = ("realistic, photo, 3d render, gradient background, scenery, floor shadow, text, watermark, "
            "signature, logo, extra limbs, extra arms, extra fingers, missing limbs, multiple characters, "
            "cropped, out of frame, blood, gore, weapon, checkerboard, transparent background, blurry")

# pose file stem -> (asset id, action words appended to the prompt)
AK_POSES = {
    "01_idle_stance": ("CHAR-AK-IDLE", "standing in a fighting stance, fists raised"),
    "02_walk_forward": ("CHAR-AK-WALK", "stepping forward in a fighting stance"),
    "03_crouch": ("CHAR-AK-CROUCH", "crouching low, guard up"),
    "04_jump_rising": ("CHAR-AK-RISE", "jumping upward, knees tucked"),
    "05_jump_falling": ("CHAR-AK-FALL", "falling from a jump, arms out for balance"),
    "06_punch_jab": ("CHAR-AK-PUNCH", "throwing a straight punch forward, arm fully extended"),
    "07_high_kick": ("CHAR-AK-KICK", "high kick forward, leg extended"),
    "08_block": ("CHAR-AK-BLOCK", "blocking with both forearms raised in front of the face"),
    "09_hurt": ("CHAR-AK-HURT", "recoiling backward after being hit, wincing"),
    "10_ko_down": ("CHAR-AK-KO", "knocked out lying on the back, eyes closed"),
    "11_victory": ("CHAR-AK-WIN", "victory pose, one fist raised high, smiling"),
}
AO_POSES = {
    "01_idle_stance": ("CHAR-AO-IDLE", "standing in a calm fighting stance"),
    "02_front_kick": ("CHAR-AO-KICK", "front kick forward, leg extended"),
    "03_block": ("CHAR-AO-BLOCK", "blocking with both forearms raised in front of the face"),
    "04_hurt": ("CHAR-AO-HURT", "recoiling backward after being hit, wincing"),
    "05_ko_down": ("CHAR-AO-KO", "knocked out lying on the back, hat beside the head"),
}

def char_prompt(character, action):
    return check_prompt(f"{character}, {action}, {STYLE}")

for t in (STYLE, AKAKEN, AOTAKE, NEGATIVE):
    check_prompt(t)
print("prompts pass the rights check")
''')

md(r'''
## 4 · Load the models

| Role | Repo | Notes |
|---|---|---|
| Base | `stabilityai/stable-diffusion-xl-base-1.0` | fp16 weights |
| Pose control | `xinsir/controlnet-openpose-sdxl-1.0` | reads the COCO-18 skeletons from `tools/make_poses.py` |
| Consistency | `h94/IP-Adapter` → `ip-adapter-plus_sdxl_vit-h` | loaded only in stages that use a reference image |
| VAE | `madebyollin/sdxl-vae-fp16-fix` | avoids black/NaN images in fp16 on T4 |

The exact commit hash and the license field of every repo are read from the Hugging Face Hub and
written into each log row. **Open each model card once and confirm the license yourself** before
copying it into SOURCES.md. First run downloads about 12 GB (a few minutes on Colab).
''')
code(r'''
import torch, diffusers, transformers
from huggingface_hub import model_info

BASE_REPO = "stabilityai/stable-diffusion-xl-base-1.0"
CN_REPO = "xinsir/controlnet-openpose-sdxl-1.0"
VAE_REPO = "madebyollin/sdxl-vae-fp16-fix"
IP_REPO, IP_SUB, IP_WEIGHT, IP_ENCODER = ("h94/IP-Adapter", "sdxl_models",
                                          "ip-adapter-plus_sdxl_vit-h.safetensors", "models/image_encoder")
OFFLOAD = True   # model CPU offload: slower, but keeps peak VRAM safely under the T4's 15 GB

MODELS = {}
for role, repo in (("base", BASE_REPO), ("controlnet", CN_REPO), ("vae", VAE_REPO), ("ip_adapter", IP_REPO)):
    try:
        info = model_info(repo)
        lic = (info.card_data or {}).get("license", "see model card") if info.card_data else "see model card"
        MODELS[role] = {"repo": repo, "sha": info.sha, "license": str(lic)}
    except Exception as e:  # offline or rate-limited: still log what we can
        MODELS[role] = {"repo": repo, "sha": "unknown", "license": f"unknown ({type(e).__name__})"}
for k, v in MODELS.items():
    print(f"{k:11s} {v['repo']}  @{v['sha'][:10]}  license: {v['license']}")

GPU = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU"
ENV = f"Google Colab ({GPU}); torch {torch.__version__}, diffusers {diffusers.__version__}, transformers {transformers.__version__}"
print(ENV)

if os.environ.get("DUSK_FAKE_PIPE"):          # offline smoke test only; never set in Colab
    from fake_pipe import FakePipe
    pipe = FakePipe()
else:
    from diffusers import StableDiffusionXLControlNetPipeline, ControlNetModel, AutoencoderKL
    controlnet = ControlNetModel.from_pretrained(CN_REPO, revision=MODELS["controlnet"]["sha"]
                                                 if MODELS["controlnet"]["sha"] != "unknown" else None,
                                                 torch_dtype=torch.float16)
    vae = AutoencoderKL.from_pretrained(VAE_REPO, torch_dtype=torch.float16)
    pipe = StableDiffusionXLControlNetPipeline.from_pretrained(
        BASE_REPO, controlnet=controlnet, vae=vae, torch_dtype=torch.float16,
        variant="fp16", use_safetensors=True)
    if OFFLOAD:
        pipe.enable_model_cpu_offload()
    else:
        pipe.to("cuda")
    pipe.set_progress_bar_config(disable=True)
SCHEDULER = type(pipe.scheduler).__name__
IP_LOADED = False

def set_ip_adapter(on, scale=0.6):
    """Load IP-Adapter only when a reference image is used; unload it otherwise."""
    global IP_LOADED
    if on and not IP_LOADED:
        pipe.load_ip_adapter(IP_REPO, subfolder=IP_SUB, weight_name=IP_WEIGHT,
                             image_encoder_folder=IP_ENCODER)
        if OFFLOAD: pipe.enable_model_cpu_offload()
        IP_LOADED = True
    elif not on and IP_LOADED:
        pipe.unload_ip_adapter()
        if OFFLOAD: pipe.enable_model_cpu_offload()
        IP_LOADED = False
    if on:
        pipe.set_ip_adapter_scale(scale)
print("pipeline ready, scheduler:", SCHEDULER)
''')

md("## 5 · Asset log helpers (one row per generation)")
code(r'''
import csv, json, datetime

COLUMNS = ["gen_id", "asset_id", "timestamp_utc", "file", "thumb", "model", "where_run", "license",
           "prompt", "negative_prompt", "seed", "size", "steps", "cfg", "scheduler",
           "control_image", "controlnet_scale", "ip_reference", "ip_scale", "seconds",
           "outcome", "reason", "edits", "where_used"]
OUTCOMES = {"pending", "accepted", "edited", "rejected"}

def _read_log():
    if not LOG_CSV.exists():
        return []
    with open(LOG_CSV, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def _write_log(rows):
    tmp = LOG_CSV.with_suffix(".tmp")
    with open(tmp, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader(); w.writerows(rows)
    tmp.replace(LOG_CSV)
    _write_md(rows)

def _cell(s):
    return str(s).replace("|", "\\|").replace("\n", " ")

def _write_md(rows):
    lines = ["# ASSET-LOG — walker-dusk-duel", "",
             "Generated automatically by `notebooks/generate_images.ipynb`; one row per generation.",
             "Outcome and reason are written by Zhaohui with `review()`. Settings are sufficient to reproduce",
             "an image on the same model commits (small GPU-to-GPU differences are possible).", "",
             "| Gen ID | Asset ID | Model and version · where run · license | Prompt and settings | Outcome | Edits | Where used |",
             "|---|---|---|---|---|---|---|"]
    for r in rows:
        settings = (f"**prompt:** {r['prompt']}<br>**negative:** {r['negative_prompt']}<br>"
                    f"seed {r['seed']} · {r['size']} · {r['steps']} steps · cfg {r['cfg']} · {r['scheduler']}"
                    f" · control `{r['control_image'] or 'none'}` @ {r['controlnet_scale']}"
                    f" · IP ref `{r['ip_reference'] or 'none'}` @ {r['ip_scale']} · {r['seconds']} s")
        outcome = r["outcome"] + (f": {r['reason']}" if r["reason"] else "")
        lines.append("| " + " | ".join(_cell(x) for x in (
            f"`{r['gen_id']}`<br>![]({r['thumb']})", r["asset_id"],
            f"{r['model']} · {r['where_run']} · {r['license']}", settings, outcome,
            r["edits"] or "—", r["where_used"] or "—")) + " |")
    LOG_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

def log_generation(row):
    rows = [r for r in _read_log() if r["gen_id"] != row["gen_id"]]
    rows.append({c: row.get(c, "") for c in COLUMNS})
    _write_log(rows)

def review(gen_id, outcome, reason, where_used=None):
    """Record YOUR judgment. Example: review("CHAR-AK-REF_s103", "accepted", "matches rules 1-7; fists read at 112 px")"""
    assert outcome in OUTCOMES, f"outcome must be one of {OUTCOMES}"
    assert reason.strip() or outcome == "pending", "write the reason, judged against the sheet/storyboard/pillars"
    rows = _read_log()
    for r in rows:
        if r["gen_id"] == gen_id:
            r["outcome"], r["reason"] = outcome, reason
            if where_used is not None:
                r["where_used"] = where_used
            _write_log(rows); print("logged:", gen_id, outcome); return
    raise KeyError(gen_id)

def add_edit(gen_id, edit, where_used=None):
    rows = _read_log()
    for r in rows:
        if r["gen_id"] == gen_id:
            r["edits"] = (r["edits"] + "; " if r["edits"] else "") + edit
            if r["outcome"] == "accepted":
                r["outcome"] = "edited"
            if where_used:
                r["where_used"] = where_used
            _write_log(rows); return
    raise KeyError(gen_id)

def show_log(asset_prefix=""):
    for r in _read_log():
        if r["asset_id"].startswith(asset_prefix):
            print(f"{r['gen_id']:28s} {r['outcome']:9s} {r['reason'][:70]}")
print("log:", LOG_CSV)
''')

md("## 6 · Generate, contact sheet, skeleton overlay check")
code(r'''
import time
from PIL import Image, ImageDraw, ImageFont
from IPython.display import display

POSES_JSON = json.loads((CHAR / "poses.json").read_text())
CANVAS = tuple(POSES_JSON["canvas"])          # (832, 1216): same canvas as the skeletons
FONT = ImageFont.load_default(size=18) if hasattr(ImageFont, "load_default") else None

def rel(p):
    return Path(p).relative_to(ROOT).as_posix() if p else ""

def generate(asset_id, prompt, *, control=None, seeds=(1,), negative=NEGATIVE, steps=30, cfg=6.0,
             cn_scale=0.9, ip_image=None, ip_scale=0.6, size=CANVAS):
    """Generate one image per seed, save to Drive, log a 'pending' row for each. Returns gen_ids."""
    check_prompt(prompt)
    w, h = size
    ctrl = Image.open(control).convert("RGB") if control else Image.new("RGB", (w, h), "black")
    scale = cn_scale if control else 0.0       # no skeleton: ControlNet contributes nothing
    set_ip_adapter(ip_image is not None, ip_scale)
    ref = Image.open(ip_image).convert("RGB") if ip_image else None
    (RAW / asset_id).mkdir(exist_ok=True); (THUMBS / asset_id).mkdir(exist_ok=True)
    gen_ids, tiles = [], []
    for seed in seeds:
        gen_id = f"{asset_id}_s{seed}"
        kwargs = dict(prompt=prompt, negative_prompt=negative, image=ctrl, controlnet_conditioning_scale=scale,
                      num_inference_steps=steps, guidance_scale=cfg, width=w, height=h,
                      generator=torch.Generator("cpu").manual_seed(seed))
        if ref is not None:
            kwargs["ip_adapter_image"] = ref
        t0 = time.time()
        img = pipe(**kwargs).images[0]
        secs = round(time.time() - t0, 1)
        out = RAW / asset_id / f"{gen_id}.png"
        img.save(out)
        th = img.copy(); th.thumbnail((256, 256)); tpath = THUMBS / asset_id / f"{gen_id}.png"; th.save(tpath)
        models = [f"SDXL base 1.0 @{MODELS['base']['sha'][:10]}", f"VAE fp16-fix @{MODELS['vae']['sha'][:10]}"]
        lic = [f"SDXL: {MODELS['base']['license']}", f"VAE: {MODELS['vae']['license']}"]
        if control:
            models.append(f"ControlNet OpenPose (xinsir) @{MODELS['controlnet']['sha'][:10]}")
            lic.append(f"ControlNet: {MODELS['controlnet']['license']}")
        if ref is not None:
            models.append(f"IP-Adapter plus ViT-H @{MODELS['ip_adapter']['sha'][:10]}")
            lic.append(f"IP-Adapter: {MODELS['ip_adapter']['license']}")
        log_generation({
            "gen_id": gen_id, "asset_id": asset_id,
            "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            "file": rel(out), "thumb": rel(tpath), "model": " + ".join(models), "where_run": ENV,
            "license": "; ".join(lic), "prompt": prompt, "negative_prompt": negative, "seed": seed,
            "size": f"{w}x{h}", "steps": steps, "cfg": cfg, "scheduler": SCHEDULER,
            "control_image": rel(control) if control else "", "controlnet_scale": scale,
            "ip_reference": rel(ip_image) if ip_image else "", "ip_scale": ip_scale if ip_image else "",
            "seconds": secs, "outcome": "pending"})
        gen_ids.append(gen_id); tiles.append((gen_id, img))
        print(f"{gen_id}: {secs} s")
    sheet = contact_sheet(asset_id, tiles, Image.open(control).convert("RGB") if control else None)
    display(sheet)
    return gen_ids

def contact_sheet(asset_id, tiles, skeleton=None, tile_h=420):
    """Row 1: raw outputs. Row 2 (pose stages): output blended 50/50 with its skeleton, for drift checks."""
    w0, h0 = tiles[0][1].size
    tw = round(w0 * tile_h / h0)
    rows = 2 if skeleton is not None else 1
    sheet = Image.new("RGB", (tw * len(tiles), rows * (tile_h + 28)), (245, 242, 235))
    d = ImageDraw.Draw(sheet)
    for i, (gid, img) in enumerate(tiles):
        sheet.paste(img.resize((tw, tile_h)), (i * tw, 0))
        d.text((i * tw + 6, tile_h + 4), gid, fill="black", font=FONT)
        if skeleton is not None:
            blend = Image.blend(img.convert("RGB"), skeleton.resize(img.size), 0.5)
            blend.resize((tw, tile_h)).save(CHECKS / f"{gid}_overlay.png")
            sheet.paste(blend.resize((tw, tile_h)), (i * tw, tile_h + 28))
    path = SHEETS / f"{asset_id}_{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}.png"
    sheet.save(path)
    print("contact sheet:", rel(path))
    return sheet

def pose_file(fighter, stem):
    return CHAR / fighter / "openpose" / f"{stem}.png"
''')

md(r'''
## Stage 1 · Akaken reference (CHAR-AK-REF)

Idle skeleton, no reference image. Four seeds. Judge each against CHARACTER-SHEET consistency rules
1–8 **at game size** (cell below the sheet shows them at 112 px tall) before choosing.
''')
code(r'''
ref_ids = generate("CHAR-AK-REF", char_prompt(AKAKEN, AK_POSES["01_idle_stance"][1]),
                   control=pose_file("akaken", "01_idle_stance"), seeds=[101, 102, 103, 104])
''')
code(r'''
# Preview every candidate at real on-screen size (112 px standing height), 1x and 3x nearest.
def at_game_size(gen_id, fighter="akaken"):
    asset = gen_id.rsplit("_s", 1)[0]
    img = Image.open(RAW / asset / f"{gen_id}.png")
    s = POSES_JSON["fighters"][fighter]["canvas_to_screen_scale"]
    small = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
    return small, small.resize((small.width * 3, small.height * 3), Image.NEAREST)

row = [at_game_size(g) for g in ref_ids]
strip = Image.new("RGB", (sum(b.width for _, b in row) + 10 * len(row), row[0][1].height), "white")
x = 0
for _, big in row:
    strip.paste(big, (x, 0)); x += big.width + 10
display(strip)
''')
code(r'''
# YOUR decision. Edit and run one line per candidate, e.g.:
# review("CHAR-AK-REF_s101", "rejected", "headband tails in front of face (rule 3); fists smaller than head (rule 2)")
# review("CHAR-AK-REF_s103", "accepted", "rules 1-8 hold; topknot and fists still read at 112 px", where_used="reference for all CHAR-AK poses")
show_log("CHAR-AK-REF")
''')

md(r'''
## Stage 2 · Akaken poses (IP-Adapter reference + skeleton)

Set `AK_REF` to the accepted reference. Start with two seeds per pose; regenerate only the poses you
reject, ideally after changing **one** setting and noting why in FRICTIONAL.md.
''')
code(r'''
AK_REF = RAW / "CHAR-AK-REF" / "CHAR-AK-REF_s103.png"     # <- the one you accepted
assert AK_REF.exists(), AK_REF

AK_TODO = list(AK_POSES)          # or e.g. ["06_punch_jab", "09_hurt"] to redo only some
for stem in AK_TODO:
    asset_id, action = AK_POSES[stem]
    generate(asset_id, char_prompt(AKAKEN, action), control=pose_file("akaken", stem),
             seeds=[201, 202], ip_image=AK_REF, ip_scale=0.6, cn_scale=0.9)
''')
code(r'''
# review("CHAR-AK-PUNCH_s201", "accepted", "...")
show_log("CHAR-AK")
''')

md("## Stage 3 · Aotake reference and poses")
code(r'''
ao_ref_ids = generate("CHAR-AO-REF", char_prompt(AOTAKE, AO_POSES["01_idle_stance"][1]),
                      control=pose_file("aotake", "01_idle_stance"), seeds=[301, 302, 303, 304])
''')
code(r'''
# review("CHAR-AO-REF_s30x", "accepted", "...")
AO_REF = RAW / "CHAR-AO-REF" / "CHAR-AO-REF_s301.png"     # <- the one you accepted
assert AO_REF.exists(), AO_REF
for stem, (asset_id, action) in AO_POSES.items():
    generate(asset_id, char_prompt(AOTAKE, action), control=pose_file("aotake", stem),
             seeds=[401, 402], ip_image=AO_REF, ip_scale=0.6, cn_scale=0.9)
''')

md(r'''
## Stage 4 · Environment (ENV-BG)

No skeleton (ControlNet scale 0) and no reference image. 1344×768 is the SDXL 16:9 size; export
scales it to the 640×360 viewport. The fighters stand in front of the **wall band**, which must stay
dark (CHARACTER-SHEET palette check: wall ≈ `#3A3347`).
''')
code(r'''
ENV_PROMPT = check_prompt(
    "2D fighting game stage background, side view, empty stone temple courtyard at dusk, "
    "dark purple-grey stone wall across the middle of the image, paper lanterns glowing warm orange "
    "hanging on the left and right, soft purple dusk sky above the wall, dark stone floor along the bottom, "
    "flat cel-shaded cartoon style, simple shapes, low detail, calm, no people")
ENV_NEG = ("people, person, character, animal, text, watermark, logo, photo, realistic, busy details, "
           "high contrast, bright wall, perspective floor grid")
env_ids = generate("ENV-BG", ENV_PROMPT, negative=ENV_NEG, seeds=[501, 502, 503, 504], size=(1344, 768))
''')
code(r'''
# review("ENV-BG_s50x", "accepted", "...")
show_log("ENV")
''')

md(r'''
## Stage 5 · Export accepted images for Godot

- Characters: background removed with **rembg** (`isnet-anime`, local, MIT), then the **whole
  832×1216 canvas** is scaled by the fighter's `canvas_to_screen_scale` from `poses.json`. Keeping
  the full canvas means every state image shares the same ground line, so swapping states does not
  make the sprite jump.
- Background: resized to 640×360.
- Every export appends its edits to the log row automatically.
''')
code(r'''
%pip install -q rembg onnxruntime
''')
code(r'''
from rembg import remove, new_session
REMBG = new_session("isnet-anime")

def export_character(gen_id, fighter, name, where_used):
    asset = gen_id.rsplit("_s", 1)[0]
    img = Image.open(RAW / asset / f"{gen_id}.png").convert("RGB")
    cut = remove(img, session=REMBG)
    s = POSES_JSON["fighters"][fighter]["canvas_to_screen_scale"]
    size = (round(img.width * s), round(img.height * s))
    out = EXPORT / fighter / f"{name}.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    cut.resize(size, Image.LANCZOS).save(out)
    add_edit(gen_id, f"rembg isnet-anime background removal; full canvas scaled x{s} to {size[0]}x{size[1]} (LANCZOS) -> {rel(out)}",
             where_used=where_used)
    return out

def export_background(gen_id, where_used="godot/art/env/bg.png (all panels)"):
    img = Image.open(RAW / "ENV-BG" / f"{gen_id}.png").convert("RGB")
    out = EXPORT / "env" / "bg.png"; out.parent.mkdir(parents=True, exist_ok=True)
    img.resize((640, 360), Image.LANCZOS).save(out)
    add_edit(gen_id, f"resized 1344x768 -> 640x360 (LANCZOS) -> {rel(out)}", where_used=where_used)
    return out

# Example, after review() marked them accepted:
# export_character("CHAR-AK-IDLE_s201", "akaken", "idle", "godot/art/akaken/idle.png (panels 2, 7)")
# export_character("CHAR-AO-KO_s401", "aotake", "ko", "godot/art/aotake/ko.png (panel 8)")
# export_background("ENV-BG_s502")
''')

md(r'''
## Stage 6 · Bring results back into the repo

The Drive folder mirrors the repo layout, so copy these to the **same paths** in the repo
(download from Drive, or use Google Drive for desktop):

| Path (Drive = repo) | Contents |
|---|---|
| `ASSET-LOG.md`, `asset_log.csv` | the log, one row per generation |
| `design/generations/thumbs/`, `sheets/`, `checks/` | 256 px thumbnails and contact sheets of **every** output, including rejected ones; skeleton overlays |
| `godot/art/` | exported state images and background used by the slice |

Keep `raw/` (full-size) on Drive only; the log's `file` column points there. Then commit, e.g. *"Add Akaken reference and poses; log 26 generations"*.
''')

nb = {"cells": [], "metadata": {
        "accelerator": "GPU", "colab": {"gpuType": "T4", "provenance": []},
        "kernelspec": {"display_name": "Python 3", "name": "python3"},
        "language_info": {"name": "python"}},
      "nbformat": 4, "nbformat_minor": 0}
for kind, src in cells:
    lines = src.split("\n")
    source = [l + "\n" for l in lines[:-1]] + [lines[-1]]
    c = {"cell_type": kind, "metadata": {}, "source": source}
    if kind == "code":
        c.update(execution_count=None, outputs=[])
    nb["cells"].append(c)
out = Path(sys.argv[1])
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(nb, indent=1, ensure_ascii=False), encoding="utf-8")
print("cells:", len(cells), "->", out)
