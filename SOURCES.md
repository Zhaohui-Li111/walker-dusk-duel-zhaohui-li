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

These outputs are design specifications and ControlNet inputs. They are not generated assets and not game art.

## Generative models

| Model | Version | Where run | License / terms | Used for |
|---|---|---|---|---|
| *(none yet; first generation happens after the design commit)* | | | | |

## References consulted (not copied)

- GDQuest, godot-4-hitbox-hurtbox demo: https://github.com/gdquest-demos/godot-4-hitbox-hurtbox
- CodingQuests, godot-hitbox-hurtbox: https://github.com/CodingQuests/godot-hitbox-hurtbox

## Asset log

See [ASSET-LOG.md](ASSET-LOG.md) (created with the first generation).

## Human / AI contributions

- **Zhaohui Li:** genre, cartoon style, two-fighter premise, acceptance of the proposed characters, proportions and arena; review of all design documents.
- **Claude Code:** theme options, template research, pose/storyboard scripts, palette contrast check, first drafts of CONCEPT, STORYBOARD, CHARACTER-SHEET, CHANGE-BRIEF, FRICTIONAL.
- **Generative models:** none yet.
