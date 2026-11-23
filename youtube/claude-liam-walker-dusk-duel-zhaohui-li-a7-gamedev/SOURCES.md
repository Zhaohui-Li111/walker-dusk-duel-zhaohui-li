# SOURCES — "Dusk Duel, Animated" (godot-gamedev, walker mode)

## Source revision

- **Game source shown:** `godot/` at `8049c54`, the last commit that changed `godot/`. The repo was at
  `c2a846d` (documentation only after `8049c54`) when the film was built; `godot/` had no uncommitted
  changes.
- **Versions:** Godot 4.7.2.stable.official.ed1daf0bf, GL Compatibility · Windows 11 Home · Brutalist toolkit
  (course-provided) at `D:\courses\7270\brutalist.art-main\brutalist.art-main`, skill `godot-gamedev` in
  walker mode (not edited) · Kokoro `am_onyx` (local, free) · faster-whisper `base.en` (local) · ffmpeg 9.0.2.

## Engine evidence

### New capture (this build), isolated copy, scripted input

Made on `capture/game`, a copy of `godot/` built by `tools/make_capture_copy.sh` (window override
3840 × 2160; `tools/capture_a7.gd` added at its root). Nothing in `godot/` is changed.

| File | SHA-256 | How it was made |
|---|---|---|
| capture/a7_play.avi (447 MB, MJPEG, 3840 × 2160, 60 fps, 23.93 s, 1436 frames) | `77794c0e7f139e776df9bd0f3332144deb3d573d8069fc9f9e898d4062679f9b` | Movie Maker, `--fixed-fps 60 --disable-vsync --resolution 3840x2160 --script res://capture_a7.gd`. **Scripted input** (labelled on screen): Enter, Esc, D, K as `InputEventAction` through `Input.parse_input_event` (main.gd's `_unhandled_input` and P1's real `PlayerController` read them); Aotake given the game's `ScriptedController` after `round_started` (stands; one kick at chosen ticks). No position, health, phase, state, frame, clip or animation property written. |
| capture/a7_play.log | `abfe4ced19860e3d5c97e10ced941f039d85ba56b5d1a8bea21b01ace71ab894` | Its event log: one line per fighter per tick while a kick, hurt or pause is under way (state, Fighter.frame, rig clip, clip time, Pivot visible, both lantern clip times). Enter tick 360; fight 420; kicks 571 and 662 whiff; kick paused at Fighter.frame 10 ticks 764–943; Aotake hits Akaken at ticks 1031 (P1 frame 4), 1136 (frame 10), 1251 (frame 20); "capture done, frames 1436; P1 health 58, P2 health 100". Tick lines identical to the headless dry run `capture/dryrun2.log`. |
| tools/capture_a7.gd | `d89df218f24755c111548859aae9aa55753738b8c8d64d95abf4e196ed6393ea` | The driver (written for this film, adapted from the A6 reel's `capture_a6.gd`). |

Clips cut by `tools/build_media.py` (segments in `beat_sheet.json`): B02 full frame 0–18.8 s; B06 cropped
to both lanterns (4K x 1200–2880, y 900–1845) from 1.5 s; B13 ticks 556–606 at 1/8 then real speed from
606; B14 ticks 1020–1040, 1122–1142, 1230–1258 at 1/8 then real speed from 1005; B13/B14 cropped to
4K x 1230–3210, y 750–1864. Real speed drops alternate 60 fps frames to 30 fps; the 1/8 replays hold
each captured frame for 4 output frames (no interpolation) and carry the on-screen label "REPLAY 1/8
SPEED · each captured frame held, none added".

### Committed strips (fixture captures, made by Zhaohui with Movie Maker, 1280 × 720, 30 fps)

`captures/kick_arc/r1` frames 10, 13, 14, 16, 17, 23, 24 and `captures/kick_arc/r0` frame 10, from
`godot/previews/kick_arc_preview.tscn`. Every frame used and its SHA-256 is in `figures/figures.json`.
Labelled "fixture capture" on screen.

## Figures

`tools/build_figures.py` lays out `figures/fig_*.png` from the strips, the sheet
`godot/art/sheets/lantern_flame.png` (SHA-256 `53efa3cf…b367`, enlarged 20× with nearest filtering on a
flat dark backdrop because it is transparent) and text copied from CHANGE-BRIEF.md, TUNING.md,
TEST-REPORT.md, FRICTIONAL.md, the logs and the source files. New pixels: labels, frames, grid lines,
base rings, the phase timeline. Editor views (B05, B09, B12) are **Godot editor reconstructions**
(GodotDevWorkbench) with verbatim excerpts.

## Repo records quoted

- CHANGE-BRIEF.md (A7, v1 and Revisions 2–5): clips, routes, phase table, clocks, Zhaohui's choices.
- TUNING.md (A7): first look "刚好", r0 reading, the whiff-streak line, verdict, r1 prediction, comparison,
  verdict "能看的出来，刚好".
- TEST-REPORT.md (Assignment 7): results, mutations, findings, human checks, "Claude against you".
- FRICTIONAL.md (A7): the factual record and Zhaohui's own account (one line quoted in B07's figure).
- SUBMISSION.md, README.md (A7): contribution split, known limitations.
- Logs: `logs/test_lantern_readback_60fps.log`, `test_kick_readback_60fps.log`, `test_anim_states_60fps.log`,
  `test_kick_edges_60fps.log`, `test_pins_a7_60fps.log`, `mutation_a7_1_subname_60fps.log`,
  `mutation_a7_2_loop_none_60fps.log`, `mutation_a7_3_cell_8_60fps.log`, `mutation_a7_4_emptycache_*`,
  `kick_arc_preview_frames.log`.

## Authorship

- **Zhaohui Li:** the clips, routes, objects, frame order and rate, the 8 / 5 / 15 phase table choice, the
  interrupt rule, the clocks, the lantern decisions, the short answers, the approval of the wiring plan and
  of r1, both Movie Maker strips, the first look and verdicts, the four human checks, their own account.
- **Claude Code (Opus 5.5):** the sheet generator, CLAUDE.md, pins, clips, scenes, rig controller,
  read-backs, state and edge tests, mutations, preview, strip readings and document drafts (SUBMISSION.md).
- **This film:** built by Claude Code (Opus 5.5) as a subagent of the main Claude Code session; capture
  driver, figures, narration script, edit. Voice is synthetic (Kokoro). No paid service.

## Sheet licence

`lantern_flame.png` is generated by `make_lantern_flame_sheet.gd` (MIT, the repository's `LICENSE`);
no third-party art, model or reference image (`godot/art/sheets/ATTRIBUTION.md`).
