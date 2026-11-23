# BUILD-LOG — "Dusk Duel, Animated" (godot-gamedev, walker mode)

Every deviation, workaround and failure in building this reel. Built by Claude Code (Opus 5.5), as a
subagent of the main Claude Code session, for Zhaohui Li on 2026-11-22. The toolkit, the earlier reels
and everything under `godot/` were not edited; nothing was committed or pushed; no paid call.

Host: Windows 11 Home China · Python 3.12.9 (shim `D:\tmp\py3shim\python3`) · Godot 4.7.2 (GL
Compatibility) · ffmpeg 9.0.2 · Kokoro `am_onyx` (local, kokoro-onnx) · faster-whisper `base.en` (local).
Source shown: `godot/` at `8049c54` (repo HEAD `c2a846d`, `godot/` clean).

## 1. What the A7 handout asks the film to show, and where it is

| Requirement | Beat(s) |
|---|---|
| 1. The game, both clips, their routes, which loops and which commits | B00, B02 (in play), B03 (table) |
| 2. The four questions, each at a line of the student's clip, test or brief | Q1 clip: B07 (kick_arc.tres:31, mutation 1 log, the probe); Q2 one authority: B15 (fighter.gd:286-291, read-back authority checks), B12; Q3 two clocks: B16 (test_anim_states log :57-58), B12 (kick_rig.gd:35), B13 (pause footage); Q4 feel in frames: B08 (fighter.gd:35-38, 90, 164-165; phase table), B09 (kick_arc.tres:35-38) |
| 3. The sheet, its slicing, the frame track that reads it | B04 (sheet, grid, base), B05 (lantern_flicker.tres 5-18), B06 (result in play) |
| 4. Phase table beside the key times; the strip at each boundary (capture frames 10, 13, 14, 16, 17, 23, 24) | B08, B09, B10 (committed r1 strip), B11 (tuning r0 → r1) |
| 5. The state machine playing each clip in real play, an interrupt in each phase | B02, B06, B13 (whole kick, pause), B14 (interrupts on Fighter.frame 4 / 10 / 20, SCRIPTED-INPUT CAPTURE) |
| 6. What the read-backs proved, the mutations that failed them, what no headless run shows | B17, B07, B18 |
| 7. Agent mistakes, Claude's wrong/overruled strip readings, uncertainty, next step, contributions, sheet source and licence, revision | B19, B11, B20 (and B04 for the licence, B06/B20 for the hidden left lantern) |
| Walker opening and summary; Verdict → Your Turn → regular outro | B00, B01, B20, B21, B22 |

## 2. Capture (new, isolated copy, scripted input)

- `tools/make_capture_copy.sh` copies `godot/` to `capture/game` (4K window override, driver
  `capture_a7.gd` added). Movie Maker with an absolute output path (A5/A6 lesson), `--fixed-fps 60`.
- **Interrupt geometry, found by a headless dry run (`capture/dryrun1.log`):** kick reach P1 52.6,
  Aotake 64.5. At a gap of 69.5–70 px Akaken's kick whiffs and Aotake's lands, so Aotake can hit
  Akaken at any chosen kick frame without Akaken hitting first. The driver walks P1 to that gap and gives
  Aotake one scripted kick 4 ticks before / 2 ticks after / 12 ticks after Akaken's K press; the hits landed
  on Akaken's Fighter.frame 4, 10 and 20 as planned.
- **Take 1** (12.5 s, title 1.5 s, pause 2 s) was too short for the narration; re-captured with the title
  held 6 s, 60 ticks between events, a second whiff and a 3 s pause. **Take 2 used**: 1436 frames,
  23.93 s, "P1 health 58, P2 health 100". Its tick log is identical to the headless dry run `dryrun2.log`
  (diff empty). Take 1's AVI was deleted; its log is `capture/a7_take1.log`.
- The arc is ~40 px in the 640 × 360 viewport, so B13/B14 are cropped 1.55× and B06 1.8× (both labelled).
  Each kick lasts 0.47 s, so B13/B14 add **labelled 1/8-speed replays** (each captured 60 fps frame held for
  4 output frames, nothing interpolated), then the same events at real speed.
- The capture also shows the A5 hurt flash (red) and the A6 hit spark on Aotake's hits, and effects.gd's
  whiff streak after Akaken's whiffs; neither is part of A7.

## 3. Narration

- Kokoro read 23 beats; faster-whisper read every clip back (`_qc/transcripts.json`).
- **Re-voiced after the transcript (reworded):** B07 ("In mutation one" heard "A mutation when"; "And
  Claude Code" heard "Enclawed code"), B08 ("the constants say seven, five, sixteen" heard "75, 16"; key times
  re-said with "zero point …"), B14 ("in active" heard "inactive" → "during active"), B18 ("after an interrupt
  it disappears" → "the arc disappears"), B19 ("And Claude's" heard "Enclawed"; "polygon seam" heard
  "seemed", then "scene" → "an edge between polygons"), B20 ("use setup hits" heard "you set up hits" →
  "inject their hits").
- **Accepted readings:** "Zhao Hui" / "Jowhui" for Jow-hway; "Akakan" / "Otake"; "sells" for cells; "cash"
  for cache; "hits stop" for hitstop; "Claude Coe" (B18); "LAM in forbear" (B21 sign-off, as in A6).

## 4. Rendering

- Two Remotion queues (`tools/render_queue.sh`), the second started about a minute after the first (A6:
  parallel starts failed together), with `TEMP`/`TMP`/`TMPDIR` on `D:	mpemotion`. All 19 beats rendered
  on the first try (93–167 s each).
- **B12 re-rendered** (`--force`): the third note card ("Clock") was clipped at the bottom of the
  GodotDevWorkbench notes column; the note texts were shortened. B05 and B09 were checked and fit.
- **B06 re-cut:** its label first said "cropped 2.3×"; the real scale is 3072 / 1680 = 1.8×. Fixed.
- Footage labels are 56 px (A6 used 60). The masked GATE T measured them at exactly the 41 px floor (PASS).
- `beat_sheet.json` was only rebuilt when no render or TTS process was running.

## 5. Visual QC

Frames at 15 / 50 / 85 % of every beat (`_qc/contact_1..5.png`), read by Claude Code. No BLOCKER or MAJOR.
MINOR, kept: the strip crops in B10 and the r0/r1 crops in B11 are small inside GodotDesignFigure (about
500 px wide each at 4K); the arc in B02 is small at full frame (B06/B13/B14 crop it); figure footnote text
is small; B02 runs on into the paused kick, which B13 explains later.

## 6. Checks

- `./art godot-gamedev --check`: **PASS** before and after export — 21 source files, 153 exclusions,
  6 components, 3 exact excerpts, 3 code-then-result pairs (`_qc/gamedev_check.json`,
  `_qc/gamedev_check_after_export.json`). It checks hashes, inventory and lines, not explanatory truth.
- GATE T in `./art final`: **PASS**, 0 FAILs; the four capture beats are skipped as "no video" by the
  checker. **Masked GATE T** (`_qc/typecheck-masked/`, game area painted out): **PASS**; B02, B06, B13,
  B14 labels at 41 px = floor. The five STILL figure beats were not re-rendered masked (already PASS in
  the real reel's GATE T); a deviation from the A6 procedure, to save about ten minutes of rendering.
- Transcripts: see section 3 and `_qc/REPORT.md`.
- Game tests were **not re-run** for this film: the film quotes the committed logs (TEST-REPORT A7). The
  capture's own dry run and take ran without SCRIPT ERROR.

## 7. Final export

- `./art final <reel> --height 2160 --fps 30 --out <reel>/exports/landscape`: status `ready`, 23/23 slots,
  receipt `exports/landscape/…verified.json`. Passed on the first run.
- Master: `exports/landscape/claude-liam-walker-dusk-duel-zhaohui-li-a7-gamedev.mp4`, 459.7 s (7:39.7),
  3840 × 2160, 30 fps, H.264 + AAC, 43,291,283 bytes,
  SHA-256 `8496e357676eef3aaea118863e090a8dff57b06e2771efa412c45019974e674b`. Audio mean −27.1 dB,
  max −3.0 dB.
- **Not done by Claude Code:** watching and listening to the master end to end. That is Zhaohui's check.

## 8. Disk and git

- Everything is on D: (capture AVI 447 MB and the 26 MB capture copy, both gitignored; media, mp3,
  Remotion temp). C: had 7.1 GB free at the start.
- Nothing staged would exceed 25 MB: the largest untracked files are `beat_sheet.json` (3.3 MB, figures as
  data URIs) and the masked copy's sheet (2.8 MB); mp4/mp3/avi, `media/`, `mp3/`, `exports/`,
  `capture/game/`, `_qc/capture/`, `_qc/clips/` are ignored. Nothing was committed.
