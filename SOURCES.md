# SOURCES — walker-dusk-duel

## Started from

- Planned: an empty Godot 4.7 project, with project settings (640×360 viewport, 2× window,
  canvas_items stretch) matching my earlier `walker-jumpman` checkout. Update this line if code is
  copied from walker-jumpman or from a template.

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
| Stable Audio Open 1.0, MusicGen medium | *(filled in when the audio notebook runs)* | Colab T4 | Stability AI Community License; CC-BY-NC 4.0 | SFX, music |

Licence fields were read from the Hugging Face Hub by the notebook and are repeated in every
ASSET-LOG row. Non-commercial / attribution terms (MusicGen weights, Stable Audio Open) are
acceptable for coursework and are stated here.

## References consulted (not copied)

- GDQuest, godot-4-hitbox-hurtbox demo: https://github.com/gdquest-demos/godot-4-hitbox-hurtbox
- CodingQuests, godot-hitbox-hurtbox: https://github.com/CodingQuests/godot-hitbox-hurtbox

## Asset log

See [ASSET-LOG.md](ASSET-LOG.md) (created with the first generation).

## Human / AI contributions

- **Zhaohui Li:** genre, cartoon style, two-fighter premise, acceptance of the proposed characters, proportions and arena; review of all design documents.
- **Claude Code:** theme options, template research, pose/storyboard scripts, palette contrast check, first drafts of CONCEPT, STORYBOARD, CHARACTER-SHEET, CHANGE-BRIEF, FRICTIONAL.
- **Generative models:** none yet.
