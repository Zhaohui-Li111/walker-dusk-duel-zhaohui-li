# SOURCES — "Dusk Duel, Shaded" (godot-gamedev, walker mode)

## Source revision

- **Game source shown:** `godot/` at `043df17`, the last commit that changed `godot/` when the film
  was built. Captures were made from the working tree at `5ee48b4`, whose `godot/` is identical.
- **Versions:** Godot 4.7.2.stable.official.ed1daf0bf, GL Compatibility (`opengl3`, Intel UHD
  Graphics) · Windows 11 Home · Brutalist toolkit (course-provided) at
  `D:\courses\7270\brutalist.art-main\brutalist.art-main`, skill `godot-gamedev` in walker mode.

## Engine evidence (native, unretouched)

All made on `capture/game`, an isolated copy of `godot/` built by `tools/make_capture_copy.sh`
(window override 3840 × 2160; `tools/capture_flash.gd` added). Nothing in `godot/` is changed.

| File | SHA-256 | How it was made |
|---|---|---|
| capture/flash.avi (gitignored, 155 MB+) | `628be567319b5afa856c5477181892543623d33b62119cb345ef8e75947af541` | Movie Maker, `--fixed-fps 60 --resolution 3840x2160`, `res://capture_flash.gd`. **Scripted input:** the script places the fighters in punch range, presses `p1_punch` through `Input` (the real PlayerController reads it) at frames 60 and 180, and gives Aotake a `ScriptedController` kick at frame 240. 15.0 s, 900 frames; P1 health 86, P2 92 at the end. Labelled on screen. |
| capture/evidence/a5/hurt_flash_0_0.png | `7e5b0b3f2cb4458556c606be643d4fc4aa0f8fa9c2dd33972183ff7e4661cba5` | `godot/tests/capture_a5.gd`, windowed, driver paused, `hurt_amount` 0.0 |
| capture/evidence/a5/hurt_flash_0_5.png | `5a6cb0cee403c4b882914fb99e8fab420c6c32374ca5377d9fd26c69d2b1cf83` | the same, 0.5 |
| capture/evidence/a5/hurt_flash_1_0.png | `b24ec3af1b1b3ee151bbe4121a0aeea19297f42b65c505672a52cd6053c5d2ed` | the same, 1.0 |
| capture/evidence/a5/hurt_flash_grey_1_0.png | `2bd43b72df7405be0912cfe3d6599a622567b1151275c05983a943dc633fe39b` | grey `flash_color` set in memory, 1.0 |
| capture/evidence/a5/hurt_flash_grey_2_0.png | `3cd66855f6142d3c6aaaeab1e413d388d288f02d23141e454d4a019a2ffc1c54` | the same, 2.0 |
| capture/evidence/a5/hint_experiment.png | `7b61986a3f923e7611d6dd4dbe2bd2d463aea65d464c25c43bffb166a705cb71` | the hint scene as committed |
| capture/evidence/a5/granite_materials.png | `d0ac4cea532275adefcbcfe768abc24bb9ecee7f42ef81f3504fdf0c64cf6264` | the prop room as committed |
| capture/evidence/a5/granite_one_material_changed.png | `66b745e18dadeaa3467f2eba12635081b3c0c8d056f9e2383859f33dca2e0a94` | floor `tint` changed in memory only |
| capture/evidence/a5/granite_sweep_*.png | in `figures/figures.json` | floor uniforms at min / max, in memory |

The stills are 1924 × 1082: Windows clamps the window to the screen even under Movie Maker (see
BUILD-LOG). The sampled values in `capture/capture_a5_4k.log` match the repo's own capture run
(`logs/capture_a5.log`) within one step.

## Figures

`tools/build_figures.py` lays out `figures/fig_*.png` from the stills above and from text copied
from the repo (CHANGE-BRIEF.md, TEST-REPORT.md, the logs, the shader files). The only new pixels
are labels, sample rings and the page. Every source file and its SHA-256 are in
`figures/figures.json`.

## Engine source consulted (read, not copied into the game)

- Godot 4.7.2-stable, `drivers/gles3/shaders/scene.glsl` lines 2398 and 2798 (shown in B15), and
  `drivers/gles3/storage/material_storage.cpp` lines 953-967 (the B16 note on
  `hint_roughness_normal`), from https://github.com/godotengine/godot at tag `4.7.2-stable`.

## Textures in the game

Poly Haven *Granite Wall*, https://polyhaven.com/a/granite_wall, Dimitrios Savva, CC0 (credits and
hashes in `godot/props3d/textures/ATTRIBUTION.md`).

## Narration and tools

- **Narration:** Kokoro `am_onyx`, local and free, via the toolkit's
  `runtime/scripts/generate_audio_kokoro.py`. Checked with faster-whisper `base.en`
  (`_qc/transcripts.json`). Cost $0.00.
- **Rendering:** the toolkit's Remotion patterns through `runtime/scripts/remotion_scenes.py`:
  ClaudeComposerAsk, BrutalistHesitantWriter, GodotDevWorkbench, GodotDesignFigure,
  ClaudeVerdictArtifact, ClaudeTitleOutro. ffmpeg 9.0.2 for the footage clips.
- **Author of the reel:** Claude Code (Opus 5.5), for Zhaohui Li, 2026-10-29.

## Who did what in what the film shows

- **Zhaohui Li:** typed all three shaders (`hurt_flash`, `granite`, `hint_experiment`); wrote the
  colour line and computed the predictions; made the three mutations; did the Step 4 conversion in
  the editor; wrote LANGUAGE-NOTES; did the human checks quoted in B12, B13 and B17.
- **Claude Code:** the driver, the tests, the audit, the capture scripts, this film's script,
  figures, tools and renders.
