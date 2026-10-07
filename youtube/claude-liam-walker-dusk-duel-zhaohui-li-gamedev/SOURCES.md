# SOURCES — "Dusk Duel, Generated"

## The game (what the film is about)

| | |
|---|---|
| Project | walker-dusk-duel by Zhaohui Li; Godot project at `godot/` |
| Source revision shown | `4e0cf14`; the film's own files are added in a later commit that does not change `godot/` |
| Build id | `b640eef8…07e0` (see [CAPTURE.md](CAPTURE.md), [SOURCE-SNAPSHOT.json](SOURCE-SNAPSHOT.json)) |
| Code excerpts | read verbatim from the hashed files; ranges in `gamedev-evidence.json` |
| Started from | an empty Godot 4.7 project, with no starter code (repo README) |

## Engine evidence used in the film

| Beat | Media | Origin | SHA-256 |
|---|---|---|---|
| B02, B09, B12, B13 | `capture/run-01.avi` | Movie Maker capture of `capture/game` | `0cb0be38…20d0` |
| B13 audio | `audio/B13-slice.wav` | the same capture's audio, 12.20–29.40 s | `3b0c50a2…9aeb` |
| B07 | `capture/evidence/states/punch_4k.png` | frame 6 of `capture/states-run.avi` | `c10e40e5…ef33` |
| B15 | `evidence/test-run.txt` | `godot --headless --path godot --script res://tests/test_runner.gd` at `4e0cf14` | `c5b2de6e…6b26` |

## Repo files shown in figures (no new art)

`tools/build_figures.py` pastes existing files into the figure pages and adds only labels and
arrows. Each source's SHA-256 is in `figures/figures.json`.

| Figure | Beat | Files |
|---|---|---|
| `fig_design_punch.png` | B03 | `design/character/akaken/collision.png` (cell 06_punch_jab), `design/character/akaken/colorblock/06_punch_jab.png`; palette hex values copied from the CHARACTER-SHEET.md table |
| `fig_rounds_reference.png` | B04 | top rows of `design/generations/sheets/CHAR-AK-REF_*.png` for rounds 1, 3, 4 and 5 |
| `fig_pipeline_punch.png` | B05 | `design/character/akaken/openpose/06_punch_jab.png`, colour block 06, `design/generations/sheets/CHAR-AK-PUNCH_20261006-004722.png` (s201/s202), `godot/art/akaken/punch.png` |
| `fig_sfx_candidates.png` | B10 | `design/generations/audio/checks/SFX_candidates_spectrograms.png` |

## Facts and numbers on screen

| Claim | Source |
|---|---|
| Five reference rounds; rounds 1–3 prompt only; round 4 at strength 0.6; round 5 at 0.75; s143 kept | ASSET-LOG rows CHAR-AK-REF_*; FRICTIONAL.md 2026-10-05/06 |
| CLIP 77-token truncation; SDXL did not bind colours to garments from text | FRICTIONAL.md, same entry |
| Punch: ControlNet scale 0.9, IP-Adapter 0.6, strength 0.75, s201 palette 47.4 vs s202 51.8, 108 × 158 export at ×0.1296 | ASSET-LOG rows CHAR-AK-PUNCH_s201/s202 |
| Palette #D9482B, #F2E6D0, #F5C542, #E8B27A, #1E1B22 | CHARACTER-SHEET.md palette table |
| SFX picks: whiff s12 (5792 Hz), hit s12 (0 ms lead-in, 92.7 % below 250 Hz), block s14 (2780 Hz), K.O. s13 (ring 2.36 s inside 2.5 s) | ASSET-LOG SFX-* rows; FRICTIONAL.md 2026-10-06 sound effects |
| Punch frame data: startup 4, active 4, recovery 10, damage 8 | `godot/fighter/fighter.gd` ATTACKS |
| 94 checks, 0 failed; 13 attacks → 13 sound requests; muted run ends identically | `evidence/test-run.txt` |
| Rembg erased Aotake's K.O. pose (2 opaque px) and was re-exported with a chroma key | ASSET-LOG CHAR-AO-KO_s401 edits; FRICTIONAL.md |
| Who decided what | FRICTIONAL.md "Human / Claude / model" lines; ASSET-LOG "Decided by Claude" reasons |

## Models (in the game; none generated anything for the film)

| Model | Version | Licence |
|---|---|---|
| SDXL base 1.0 + VAE fp16 fix + xinsir ControlNet OpenPose + h94 IP-Adapter Plus ViT-H | commits in the repo's SOURCES.md | CreativeML Open RAIL++-M; MIT; Apache-2.0; Apache-2.0 |
| Stable Audio Open 1.0 | `f21265c1e2` | Stability AI Community License |
| MusicGen medium | `d3bd7b0076` | CC-BY-NC 4.0 (weights) |

## Film toolkit

- **Toolkit:** Brutalist toolkit at `D:\courses\7270\brutalist.art-main\brutalist.art-main`
  (course-provided).
  - `skills/make/godot-gamedev/SKILL.md` in walker mode, with ai-explainer, riff,
    godot-waikthrough (capture contract), OUTRO-LOCK and RENDER-TARGETS.
- **Remotion compositions:** ClaudeComposerAsk, BrutalistHesitantWriter, GodotDesignFigure,
  GodotDevWorkbench, ClaudeVerdictArtifact, ClaudeTitleOutro. All are stock; none was modified.
- **Narration:** Kokoro `am_onyx`, local and free. Checked with faster-whisper `base.en`.
- **No upstream documentation, paid service or generated media** was used for the film.

## Corrections applied (DOUBLE-CHECK LAW)

| Draft line | Problem | Correction |
|---|---|---|
| "Every image … came out of free models" | The hit sparks and HUD are drawn by code. | Fighters, courtyard, sound effects and music. |
| "The block was picked as the brightest" | s13 (2894 Hz) was brighter; it lost on a 120 ms lead-in. | "picked for its bright clack" |
| "With both buses muted, a seeded fight ends on the same frame" | The test compares health, positions, phase and sound count after 1300 frames. | "same health, positions and phase" |
| B07: "the red hitbox sits on the wrapped fist" | In a staged pose the box is drawn faint, because no attack is active. | Narration says so. |
