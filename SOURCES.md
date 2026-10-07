# SOURCES — walker-dusk-duel

## Started from

An empty Godot 4.7 project. The project settings (640×360 viewport, 2× window, canvas_items
stretch) were matched to my earlier `walker-jumpman` checkout by hand. No code or assets were
copied from walker-jumpman or from any template.

## Tools written for this project

| File | Author | Purpose |
|---|---|---|
| `tools/make_poses.py` | Claude Code (Opus 5.5), reviewed by Zhaohui | OpenPose conditioning skeletons, pose blocking, collision overlays, silhouette test, `poses.json` |
| `tools/make_storyboard.py` | Claude Code (Opus 5.5), reviewed by Zhaohui | Blocking thumbnails for gameplay storyboard panels |
| `notebooks/generate_images.ipynb` (built by `tools/build_colab_notebook.py`) | Claude Code (Opus 5.5), reviewed by Zhaohui | Colab/diffusers image generation; writes `ASSET-LOG.md` one row per generation |
| `notebooks/generate_audio.ipynb` (built by `tools/build_audio_notebook.py`) | Claude Code (Opus 5.5), reviewed by Zhaohui | Colab sound effects (Stable Audio Open) and music (MusicGen); trims SFX, cuts the loop at bar lines, logs to the same `ASSET-LOG.md` |
| `tools/notebook_common.py` | Claude Code (Opus 5.5) | Shared asset-log cell and notebook builder for both notebooks |
| `tools/colorblock.py` | Claude Code (Opus 5.5) | Colour-block mannequins (CHARACTER-SHEET palette painted on each pose) used as img2img starting images. Claude-drawn inputs, **not** generated assets; every log row names the starting image and strength |
| `tools/export_placeholders.py` | Claude Code (Opus 5.5) | Placeholder state sprites for Godot before the generated art existed |

These outputs are design specifications and ControlNet inputs. They are not generated assets and not game art.

## Generative models

| Model | Version | Where run | License / terms | Used for |
|---|---|---|---|---|
| Stable Diffusion XL base 1.0 (`stabilityai/stable-diffusion-xl-base-1.0`) | commit `4621659840` | Google Colab free tier, Tesla T4; torch 2.11, diffusers 0.40.0, transformers 5.18.0 | CreativeML Open RAIL++-M (`openrail++` on the model card) | all character and background images |
| ControlNet OpenPose SDXL (`xinsir/controlnet-openpose-sdxl-1.0`) | commit `23f966cd5c` | same | Apache-2.0 | pose control from `design/character/*/openpose/` |
| SDXL VAE fp16 fix (`madebyollin/sdxl-vae-fp16-fix`) | commit `207b116dae` | same | MIT | decoding in fp16 |
| IP-Adapter Plus SDXL ViT-H (`h94/IP-Adapter`) | commit `018e402774` | same | Apache-2.0 | keeps the character consistent across poses (Stage 2-3) |
| rembg `isnet-anime` | rembg (pip, latest at run time) | same | MIT | background removal on export |
| MusicGen medium (`facebook/musicgen-medium`) | commit `d3bd7b0076`, via transformers 5.19 | Colab T4 | CC-BY-NC 4.0 (weights) | music loop |
| Stable Audio Open 1.0 (`stabilityai/stable-audio-open-1.0`, gated) | commit `f21265c1e2`, via diffusers 0.41 | Colab T4 | Stability AI Community License (card field: other) | whiff, hit, block, K.O. |

Licence fields were read from the Hugging Face Hub by the notebook and are repeated in every
ASSET-LOG row. Non-commercial / attribution terms (MusicGen weights, Stable Audio Open) are
acceptable for coursework and are stated here.

## References consulted (not copied)

- GDQuest, godot-4-hitbox-hurtbox demo: https://github.com/gdquest-demos/godot-4-hitbox-hurtbox
- CodingQuests, godot-hitbox-hurtbox: https://github.com/CodingQuests/godot-hitbox-hurtbox

## Asset log

See [ASSET-LOG.md](ASSET-LOG.md) and `asset_log.csv`: one row per generation, including every rejected one.

## Human / AI contributions

- **Zhaohui Li:**
  - Chose the genre, cartoon style and two-fighter premise, and accepted the proposed characters,
    proportions and arena.
  - Reviewed the design documents.
  - Judged reference rounds 1–3 and chose plan B (colour-block img2img).
  - Ran Colab sign-in, Drive authorisation and the Hugging Face licence and token.
  - Playtested the slice.
  - Delegated the later picks, which are labelled "Decided by Claude" in ASSET-LOG, and still has
    to re-judge them.
- **Claude Code (Opus 5.5):**
  - Theme options, template research, and first drafts of every design document, FRICTIONAL
    entries and the test report.
  - All GDScript, Python tools and both notebooks.
  - Every prompt, and the colour-block mannequins.
  - Operating Colab through the browser.
  - Measurement-based picks after round 3: art and all audio.
  - The explainer film's script, tools and renders.
- **Generative models (they made the assets, not Claude):**

  | Model | Made |
  |---|---|
  | SDXL + ControlNet OpenPose + IP-Adapter | all 16 state images and the background |
  | Stable Audio Open | the four sound effects |
  | MusicGen medium | the music loop |
  | Kokoro (`am_onyx`, local) | the film narration |

## Share of code by author (estimate)

| Code | Written by hand by Zhaohui | Written by Claude Code |
|---|---|---|
| GDScript (`godot/`) | 0 % | about 100 %, reviewed and playtested by Zhaohui |
| Python tools and notebooks (`tools/`, `notebooks/`) | 0 % | about 100 % |
| Film tools (`youtube/*/tools/`) | 0 % | about 100 % |

Zhaohui's contribution is the specification, the decisions and the verification, not lines of
code. This is the course's intended division of work.

## Style guides

- **GDScript:** the official Godot GDScript style guide (snake_case functions and variables,
  PascalCase class names, tabs, typed declarations).
- **Python:** PEP 8.

## Licences of this repository's own files

- **Code and notebooks:** MIT. This licence was chosen by Claude for the submission; Zhaohui
  should confirm it or change it. It covers `godot/` scripts and scenes, `tools/`, `notebooks/`
  and the film tools.
- **Generated assets:** they keep the terms of the models that made them (table above). Music and
  sound effects are non-commercial or limited.

## Film toolkit

- **Toolkit:** the Brutalist video toolkit (course-provided), skill `godot-gamedev` in walker mode.
- **Toolkit change:** one layout line in `GodotDesignFigure.tsx` was changed. Details are in the
  reel's BUILD-LOG.
- **Narration:** Kokoro, local and free.
- **Film evidence:** under `youtube/claude-liam-walker-dusk-duel-zhaohui-li-gamedev/`.
