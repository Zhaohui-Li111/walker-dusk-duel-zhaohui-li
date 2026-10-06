"""Builds notebooks/generate_images.ipynb (written by Claude Code).

Run from the project root:  python tools/build_colab_notebook.py notebooks/generate_images.ipynb
"""
import sys
from pathlib import Path

import notebook_common as common

nb = common.Notebook()

# tools/colorblock.py is pasted into the notebook (minus its local main()) so Colab needs no extra upload
_cb = (Path(__file__).parent / "colorblock.py").read_text(encoding="utf-8").replace("\r\n", "\n")
COLORBLOCK_SRC = _cb[_cb.index("import math"):_cb.index("def main():")].rstrip() + "\n"
md, code = nb.md, nb.code

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

# SDXL's text encoders read at most 77 CLIP tokens and silently drop the rest. The first prompts
# were ~110 tokens, so the whole style part (cel shading, outline, green background) was cut off.
# Prompts are now short, style first, and check_prompt() refuses anything over the limit.
MAX_TOKENS = 77

def token_count(text):
    p = globals().get("pipe")
    tok = getattr(p, "tokenizer", None) if p is not None else None
    return len(tok(text).input_ids) if tok is not None else None   # None until the model is loaded

def check_prompt(text):
    hits = [p for p in BANNED if re.search(p, text, flags=re.IGNORECASE if not p.startswith(r"\bby") else 0)]
    if hits:
        raise ValueError(f"Prompt blocked by rights check, matched: {hits}")
    n = token_count(text)
    if n is not None and n > MAX_TOKENS:
        raise ValueError(f"Prompt is {n} CLIP tokens; SDXL keeps only {MAX_TOKENS} and drops the rest. Shorten it.")
    return text

STYLE = ("flat cel-shaded 2D fighting game sprite, thick dark outline, full body, "
         "side view facing right, plain solid green background")

# Round 1 (seeds 101-104) ignored "red-orange gi" and drew bearded / bald older men, so the colour
# moved to the front and those traits went into the negative prompt. Round 2 (111-114) fixed age
# and topknot but no image had a headband, so round 3 leads with a more concrete headband phrase.
AKAKEN = ("white headband tied around forehead, red-orange sleeveless gi, dark pants, "
          "young chibi martial artist, big head, black topknot, huge cream-wrapped fists, yellow belt, barefoot")

AOTAKE = ("tall lean cartoon martial artist, long legs, wide conical straw hat, long black braid, "
          "teal robe, navy sash, dark pants, barefoot")

NEGATIVE = ("photo, realistic, 3d render, gradient background, scenery, text, watermark, extra limbs, "
            "extra fingers, multiple characters, cropped, blood, weapon, checkerboard, blurry, "
            "beard, old man, bald, boxing gloves")

# pose file stem -> (asset id, action words appended to the prompt)
AK_POSES = {
    "01_idle_stance": ("CHAR-AK-IDLE", "fighting stance, fists raised"),
    "02_walk_forward": ("CHAR-AK-WALK", "stepping forward, guard up"),
    "03_crouch": ("CHAR-AK-CROUCH", "crouching low, guard up"),
    "04_jump_rising": ("CHAR-AK-RISE", "jumping up, knees tucked"),
    "05_jump_falling": ("CHAR-AK-FALL", "falling, arms out"),
    "06_punch_jab": ("CHAR-AK-PUNCH", "straight punch, arm extended"),
    "07_high_kick": ("CHAR-AK-KICK", "high kick, leg extended"),
    "08_block": ("CHAR-AK-BLOCK", "blocking, forearms up"),
    "09_hurt": ("CHAR-AK-HURT", "recoiling from a hit, wincing"),
    "10_ko_down": ("CHAR-AK-KO", "knocked out, lying on back"),
    "11_victory": ("CHAR-AK-WIN", "victory pose, fist raised, smiling"),
}
AO_POSES = {
    "01_idle_stance": ("CHAR-AO-IDLE", "calm fighting stance"),
    "02_front_kick": ("CHAR-AO-KICK", "front kick, leg extended"),
    "03_block": ("CHAR-AO-BLOCK", "blocking, forearms up"),
    "04_hurt": ("CHAR-AO-HURT", "recoiling from a hit, wincing"),
    "05_ko_down": ("CHAR-AO-KO", "knocked out, lying on back, hat beside head"),
}

def char_prompt(character, action):
    return check_prompt(f"{STYLE}, {character}, {action}")

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
import os
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
import torch, diffusers, transformers
from huggingface_hub import model_info

BASE_REPO = "stabilityai/stable-diffusion-xl-base-1.0"
CN_REPO = "xinsir/controlnet-openpose-sdxl-1.0"
VAE_REPO = "madebyollin/sdxl-vae-fp16-fix"
IP_REPO, IP_SUB, IP_WEIGHT, IP_ENCODER = ("h94/IP-Adapter", "sdxl_models",
                                          "ip-adapter-plus_sdxl_vit-h.safetensors", "models/image_encoder")
# Keep the models on the GPU. Model CPU offload parks ~10 GB of weights in system RAM, which is
# more than free Colab's ~12.7 GB allows once generation starts: the session crashed in Stage 1.
# The T4's 15 GB VRAM holds them; VAE tiling keeps the 832x1216 decode under the limit.
OFFLOAD = False

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
    # With transformers 5 / diffusers 0.40 some components still arrived in fp32 (14 GB on the T4,
    # out of memory), and xinsir's ControlNet is stored in fp32. Cast everything to fp16 on the CPU
    # first, then move it, and print what each component ended up as.
    pipe.to(dtype=torch.float16)
    for name, comp in pipe.components.items():
        if isinstance(comp, torch.nn.Module):
            params = list(comp.parameters())
            gb = sum(t.numel() * t.element_size() for t in params) / 2**30
            print(f"  {name:15s} {params[0].dtype}  {gb:.2f} GB")
    if OFFLOAD:
        pipe.enable_model_cpu_offload()
    else:
        pipe.to("cuda")
    # diffusers 0.40 removed pipe.enable_vae_tiling(); tiling now lives on the VAE itself
    (pipe.vae.enable_tiling if hasattr(pipe.vae, "enable_tiling") else pipe.enable_vae_tiling)()
    pipe.set_progress_bar_config(disable=True)
    del controlnet, vae
    import gc; gc.collect()
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
def memory_report():
    import psutil
    ram = psutil.virtual_memory()
    vram = torch.cuda.memory_allocated() / 2**30 if torch.cuda.is_available() else 0.0
    total = torch.cuda.get_device_properties(0).total_memory / 2**30 if torch.cuda.is_available() else 0.0
    print(f"RAM used {(ram.total - ram.available) / 2**30:.1f} / {ram.total / 2**30:.1f} GB · "
          f"VRAM allocated {vram:.1f} / {total:.1f} GB")
print("pipeline ready, scheduler:", SCHEDULER)
memory_report()
''')

md("## 5 · Asset log helpers (one row per generation)")
code(common.LOG_CELL)

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
             cn_scale=0.9, ip_image=None, ip_scale=0.6, size=CANVAS, init=None, strength=0.6):
    """Generate one image per seed, save to Drive, log a 'pending' row for each. Returns gen_ids.
    init: a colour-block image to start from (img2img); strength 0 keeps it, 1 ignores it."""
    check_prompt(prompt)
    w, h = size
    ctrl = Image.open(control).convert("RGB") if control else Image.new("RGB", (w, h), "black")
    scale = cn_scale if control else 0.0       # no skeleton: ControlNet contributes nothing
    set_ip_adapter(ip_image is not None, ip_scale)
    ref = Image.open(ip_image).convert("RGB") if ip_image else None
    init_img = Image.open(init).convert("RGB").resize((w, h)) if init else None
    runner = pipe
    if init_img is not None:   # same weights, img2img entry point
        from diffusers import StableDiffusionXLControlNetImg2ImgPipeline
        # pass the SAME component objects; from_pipe() made extra copies here (CUDA out of memory)
        runner = StableDiffusionXLControlNetImg2ImgPipeline(**{k: v for k, v in pipe.components.items()})
        runner.set_progress_bar_config(disable=True)
    (RAW / asset_id).mkdir(exist_ok=True); (THUMBS / asset_id).mkdir(exist_ok=True)
    gen_ids, tiles = [], []
    for seed in seeds:
        gen_id = f"{asset_id}_s{seed}"
        kwargs = dict(prompt=prompt, negative_prompt=negative, controlnet_conditioning_scale=scale,
                      num_inference_steps=steps, guidance_scale=cfg,
                      generator=torch.Generator("cpu").manual_seed(seed))
        if init_img is not None:
            kwargs.update(image=init_img, control_image=ctrl, strength=strength)
        else:
            kwargs.update(image=ctrl, width=w, height=h)
        if ref is not None:
            kwargs["ip_adapter_image"] = ref
        t0 = time.time()
        img = runner(**kwargs).images[0]
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
            "init_image": rel(init) if init else "", "strength": strength if init else "",
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
''' + "\n\n# --- colour-block starting images (tools/colorblock.py) ---\n" + COLORBLOCK_SRC + r'''

def colorblock_file(fighter, stem):
    """Draw (once) the CHARACTER-SHEET colours onto this pose and return the PNG path on Drive."""
    out = CHAR / fighter / "colorblock" / f"{stem}.png"
    if not out.exists():
        out.parent.mkdir(parents=True, exist_ok=True)
        fd = POSES_JSON["fighters"][fighter]
        draw_colorblock(fighter, fd["poses"][stem], fd["bones"], fd["widths"], CANVAS).save(out)
    return out
''')

md(r'''
## Stage 1 · Akaken reference (CHAR-AK-REF)

Idle skeleton, no reference image. Four seeds. Judge each against CHARACTER-SHEET consistency rules
1–8 **at game size** (cell below the sheet shows them at 112 px tall) before choosing.
''')
code(r'''
# Round 5: img2img from the colour-block mannequin. Rounds 1-3 (prompt only, seeds 101-104,
# 111-114, 121-124) never put the sheet's colours on the right parts and never drew the headband.
# Round 4 (131-134, strength 0.6) fixed colours and headband but stayed too close to the code-drawn
# mannequin, so round 5 raises strength to 0.75 to let the model redraw more.
ref_ids = generate("CHAR-AK-REF", char_prompt(AKAKEN, AK_POSES["01_idle_stance"][1]),
                   control=pose_file("akaken", "01_idle_stance"),
                   init=colorblock_file("akaken", "01_idle_stance"), strength=0.75,
                   seeds=[141, 142, 143, 144])
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
AK_REF = RAW / "CHAR-AK-REF" / "CHAR-AK-REF_s143.png"     # accepted in round 5 (see review cell)
assert AK_REF.exists(), AK_REF

AK_TODO = list(AK_POSES)          # or e.g. ["06_punch_jab", "09_hurt"] to redo only some
for stem in AK_TODO:
    asset_id, action = AK_POSES[stem]
    generate(asset_id, char_prompt(AKAKEN, action), control=pose_file("akaken", stem),
             init=colorblock_file("akaken", stem), strength=0.75,
             seeds=[201, 202], ip_image=AK_REF, ip_scale=0.6, cn_scale=0.9)
''')
code(r'''
# review("CHAR-AK-PUNCH_s201", "accepted", "...")
show_log("CHAR-AK")
''')

md(r"""
## Stage 2b · Palette fidelity check

A reproducible check of each image against CHARACTER-SHEET colours: the colour block says which
pixels should be top / pants / belt / cloth / hat / skin / hair; the score is the mean RGB distance
(0-441) between the generated image and the sheet colour on those pixels (eroded masks, so outlines
and edges do not count). Lower is closer. Used to pick between seeds after a visual check.
""")
code(r"""
import numpy as _np
from PIL import ImageFilter as _F

def palette_score(fighter, aid, stem, seed):
    P = PALETTE[fighter]
    cb = _np.array(Image.open(colorblock_file(fighter, stem)).convert("RGB")).astype(int)
    out = _np.array(Image.open(RAW / aid / f"{aid}_s{seed}.png").convert("RGB").resize((cb.shape[1], cb.shape[0]))).astype(int)
    res = {}
    for part, col in P.items():
        m = _np.all(cb == _np.array(col), axis=2)
        m = _np.array(Image.fromarray((m * 255).astype("uint8")).filter(_F.MinFilter(7))) > 0
        if m.sum() >= 50:
            res[part] = float(_np.sqrt(((out[m] - _np.array(col)) ** 2).sum(axis=1)).mean())
    return round(sum(res.values()) / len(res), 1), {k: round(v) for k, v in res.items()}

def score_table(fighter, jobs):
    for aid, stem, seed in jobs:
        tot, parts = palette_score(fighter, aid, stem, seed)
        print(f"{aid:15s} s{seed}  mean {tot:6.1f}  {parts}")

score_table("akaken", [(aid, stem, s) for stem, (aid, _a) in AK_POSES.items() for s in (201, 202)])
""")

md("## Stage 3 · Aotake reference and poses")
code(r'''
ao_ref_ids = generate("CHAR-AO-REF", char_prompt(AOTAKE, AO_POSES["01_idle_stance"][1]),
                      control=pose_file("aotake", "01_idle_stance"),
                      init=colorblock_file("aotake", "01_idle_stance"), strength=0.75,
                      seeds=[301, 302, 303, 304])
''')
code(r'''
# review("CHAR-AO-REF_s30x", "accepted", "...")
AO_REF = RAW / "CHAR-AO-REF" / "CHAR-AO-REF_s301.png"     # <- the one you accepted
assert AO_REF.exists(), AO_REF
for stem, (asset_id, action) in AO_POSES.items():
    generate(asset_id, char_prompt(AOTAKE, action), control=pose_file("aotake", stem),
             init=colorblock_file("aotake", stem), strength=0.75,
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
    "flat cel-shaded 2D fighting game stage background, side view, empty stone temple courtyard at dusk, "
    "dark purple-grey wall across the middle, glowing orange paper lanterns left and right, "
    "purple dusk sky, dark stone floor, no people")
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
import numpy as _np
from rembg import remove, new_session
REMBG = new_session("isnet-anime")

def chroma_key(img, margin=40):
    """Key out the plain green background the prompts ask for. rembg (isnet-anime) erased Aotake's
    whole K.O. pose (2 opaque pixels left), so lying poses are keyed by colour instead: a pixel is
    background when green beats both red and blue by `margin`; edges get a soft ramp and the green
    spill on them is pulled down to the red/blue average."""
    a = _np.asarray(img.convert("RGB")).astype(_np.float32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    lead = g - _np.maximum(r, b)
    alpha = _np.clip(1.0 - (lead - margin * 0.5) / (margin * 0.5), 0.0, 1.0)
    spill = _np.minimum(g, (r + b) / 2 + 20)
    a[..., 1] = _np.where(alpha < 1.0, spill, g)
    out = _np.dstack([a, alpha * 255]).astype(_np.uint8)
    return Image.fromarray(out, "RGBA")

def export_character(gen_id, fighter, name, where_used, method="rembg"):
    asset = gen_id.rsplit("_s", 1)[0]
    img = Image.open(RAW / asset / f"{gen_id}.png").convert("RGB")
    cut = remove(img, session=REMBG) if method == "rembg" else chroma_key(img)
    s = POSES_JSON["fighters"][fighter]["canvas_to_screen_scale"]
    size = (round(img.width * s), round(img.height * s))
    out = EXPORT / fighter / f"{name}.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    cut.resize(size, Image.LANCZOS).save(out)
    how = "rembg isnet-anime background removal" if method == "rembg" else "green chroma key (margin 40, spill suppressed)"
    add_edit(gen_id, f"{how}; full canvas scaled x{s} to {size[0]}x{size[1]} (LANCZOS) -> {rel(out)}",
             where_used=where_used)
    return out

def export_background(gen_id, where_used="godot/art/env/bg.png (all panels)"):
    img = Image.open(RAW / "ENV-BG" / f"{gen_id}.png").convert("RGB")
    out = EXPORT / "env" / "bg.png"; out.parent.mkdir(parents=True, exist_ok=True)
    img.resize((640, 360), Image.LANCZOS).save(out)
    add_edit(gen_id, f"resized 1344x768 -> 640x360 (LANCZOS) -> {rel(out)}", where_used=where_used)
    return out

# asset id -> (fighter, Godot state file). Matches tools/export_placeholders.py STATES.
EXPORT_MAP = {aid: ("akaken", st) for aid, st in [
    ("CHAR-AK-IDLE", "idle"), ("CHAR-AK-WALK", "walk"), ("CHAR-AK-CROUCH", "crouch"),
    ("CHAR-AK-RISE", "rise"), ("CHAR-AK-FALL", "fall"), ("CHAR-AK-PUNCH", "punch"),
    ("CHAR-AK-KICK", "kick"), ("CHAR-AK-BLOCK", "block"), ("CHAR-AK-HURT", "hurt"),
    ("CHAR-AK-KO", "ko"), ("CHAR-AK-WIN", "win")]}
EXPORT_MAP.update({aid: ("aotake", st) for aid, st in [
    ("CHAR-AO-IDLE", "idle"), ("CHAR-AO-KICK", "kick"), ("CHAR-AO-BLOCK", "block"),
    ("CHAR-AO-HURT", "hurt"), ("CHAR-AO-KO", "ko")]})

def export_accepted():
    """Export every accepted (not yet exported) state image and the accepted background."""
    done = []
    for r in _read_log():
        if r["outcome"] != "accepted":
            continue
        if r["asset_id"] in EXPORT_MAP:
            fighter, state = EXPORT_MAP[r["asset_id"]]
            done.append(export_character(r["gen_id"], fighter, state, f"godot/art/{fighter}/{state}.png"))
        elif r["asset_id"] == "ENV-BG":
            done.append(export_background(r["gen_id"]))
    print("exported:", [rel(p) for p in done])
    return done

# export_accepted()      # run after review() has marked the chosen images "accepted"
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

nb.save(sys.argv[1])
