# SOURCES — "Dusk Duel, Sparked" (godot-gamedev, walker mode)

## Source revision

- **Game source shown:** `godot/` at `840bcfd`, the last commit that changed `godot/`. The repo was
  at `55f231b` (documentation only after `840bcfd`) when the film was built; `godot/` had no
  uncommitted changes (`git status --short godot` empty).
- **Versions:** Godot 4.7.2.stable.official.ed1daf0bf, GL Compatibility (Intel UHD Graphics,
  OpenGL 3.3) · Windows 11 Home · Brutalist toolkit (course-provided) at
  `D:\courses\7270\brutalist.art-main\brutalist.art-main`, skill `godot-gamedev` in walker mode
  (not edited) · Kokoro `am_onyx` (local, free) · faster-whisper `base.en` (local).

## Engine evidence

### New capture (this build), isolated copy, scripted input

Made on `capture/game`, a copy of `godot/` built by `tools/make_capture_copy.sh` (window override
3840 × 2160; `tools/capture_a6.gd` added at its root). Nothing in `godot/` is changed.

| File | SHA-256 | How it was made |
|---|---|---|
| capture/a6_play.avi (422 MB, MJPEG, 3840 × 2160, 60 fps, 21.55 s) | `2ec33965b01e9e6ce6017db6c4a35ddb05b29297786f838d849bcce0e9226b06` | Movie Maker, `--fixed-fps 60 --disable-vsync --resolution 3840x2160 --script res://capture_a6.gd`. **Scripted input** (labelled on screen): Enter and Esc as `InputEventAction` through `Input.parse_input_event` (main.gd's own `_unhandled_input` handles them); `p1_right` / `p1_punch` the same way, read by the real `PlayerController`; Aotake given the game's `ScriptedController` (stands, never blocks, kicks every 110 ticks) after `round_started`. No position, health, phase or particle property written. |
| capture/a6_play.log | `f94f7d9e8624066a1ece4a9c3adafff4cda78fdcd5ebee3db0455326d94b8a6b` | Its event log: Enter 1.50 s; fight 2.50 s; hits every 0.5 s from 4.17 s; Esc 5.72 s and 8.72 s; K.O. 13.22 s; result 14.72 s; rematch 16.55 s; round-2 fight 17.55 s; "capture done, frames 1293; P1 health 100, P2 health 60, hits 18". |
| tools/capture_a6.gd | `b15cb0da1e70bf4189c8e90f5093afe5275597b529e84d5f87fc8a94139675b8` | The driver (written for this film, adapted from the A5 reel's `capture_flash.gd`). |

Clips cut by `tools/build_media.py`: B02 (0.6 s +), B09 (5.4 s +, cropped to x 2240-3520,
y 1020-1740 of the 4K frame and scaled 2.4×, labelled "cropped"), B15 (12.7 s +). Real speed:
the 60 fps capture is written at 30 fps by dropping alternate frames; no retiming.

### Committed strips (fixture captures, made by Zhaohui with Movie Maker, 1280 × 720, 30 fps)

`captures/hit_spark/r0`, `r0-lantern`, `r1`, `r1-lantern` (frames 10-50) and `captures/embers/r0`,
`r0-restart`, `r1` (frames 10-175), from `godot/previews/` scenes with fixed seeds. Every frame used
and its SHA-256 is in `figures/figures.json`. They are labelled "fixture capture" on screen.

## Figures

`tools/build_figures.py` lays out `figures/fig_*.png` from the strips, `godot/art/env/bg.png` and
text copied from CHANGE-BRIEF.md, TUNING.md, TEST-REPORT.md, FRICTIONAL.md, the logs and the source
files. New pixels: labels, frames, sample rings, the emission rectangle drawn from `embers.tscn`
(labelled "drawn, not engine output") and a **diagnostic** panel in B11/B13 (pixels of frame 55
that differ from the bare frame 175 by more than 8 levels, computed by this build; labelled). The
changed-pixel counts quoted on screen are TUNING.md's (against frame 0), not the diagnostic's.

## Code shown

Verbatim excerpts (hash-checked in `gamedev-evidence.json`): `godot/effects/hit_spark.tscn:17-30`
(B06), `godot/effects/hit_spark_pool.gd:43-56` (B08), `godot/effects/embers.tscn:21-34` (B12),
`godot/effects/embers_controller.gd:20-33` (B14); single lines of
`godot/shaders/particles_generated.gdshader` (137, 260, 307, 320, 348, 147) in B17's figure.
Editor views are labelled "Godot editor reconstruction".

## Textures in the game (A6)

Both drawn by code in the repository, no sourced or generated image: `godot/effects/hit_spark_star.png`
(8 × 8 star) and `godot/effects/embers_soft.png` (4 × 4 soft dot), by `godot/effects/make_textures.gd`
(SOURCES.md A6 of the repo).

## Human / AI contributions (from the repo's SOURCES.md A6, TUNING.md, TEST-REPORT.md)

- **Zhaohui Li:** chose both effects; wrote the brief's intent, settings, rules, predictions, budgets
  and short answers; decided the CLAUDE.md questions, rule 6's setup, the star sharpening and rule
  4's revision; ran every strip capture; gave the hit spark first look in words and the embers first
  look as three multiple-choice answers; made both mutations; gave both tuning verdicts (from
  questions Claude Code asked, in the preview window); generated the process shader in the editor
  and wrote its line references; read 0 in the Visual Profiler; reported the in-play check in one
  sentence; delegated the later agent steps.
- **Claude Code (Opus 5.5) and its `claude -p` agents:** CLAUDE.md, both scenes, configs tests,
  previews, controllers, state tests, cost script; the strip readings and predictions; the star and
  pool fixes; the GPU price measurement (windowed, RenderingServer) after the profiler read 0;
  approvals of the later agent steps under the delegation; this film.

## Film toolkit and narration

Brutalist toolkit, skill `godot-gamedev` (walker) with `ai-explainer` bookends; components
`ClaudeComposerAsk`, `BrutalistHesitantWriter`, `GodotDevWorkbench`, `GodotDesignFigure`,
`ClaudeVerdictArtifact`, `ClaudeTitleOutro`. Narration: Kokoro `am_onyx`, local, free; respelling
"Jow-hway Lee" for Zhaohui Li and "pree-process" for preprocess (narration only). No music, no game
audio, no captions.
