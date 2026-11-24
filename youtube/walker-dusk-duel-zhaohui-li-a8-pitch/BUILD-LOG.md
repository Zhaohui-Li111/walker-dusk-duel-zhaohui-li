# BUILD-LOG — "Dusk Duel: Final Project Pitch" (A8)

Built 2026-11-23 by Claude Code (Claude Opus 5.5) on Zhaohui's machine (Windows 11, Intel UHD Graphics,
Git Bash), from repository HEAD `dff6cba` (`godot/` unchanged since `8049c54`). Toolkit: local Brutalist
checkout `D:\courses\7270\brutalist.art-main\brutalist.art-main`.

## 1. Script

- `pitch/SCRIPT-DRAFT.md` (14 beats) was approved by Zhaohui on 2026-11-23 ("批准，开始做").
- Changes made while building, none of which changes a claim:
  - Draft beat 6 is split into B05 (code: `cpu_controller.gd:49-59`) and B06 (the result in the
    capture), as `godot-gamedev --check` requires a code beat to be followed by its visible result.
    Its line "re-decides every ten ticks" moved to B05. B05 adds the line-by-line reading of the
    four branches. B06 says the round-2 footage has no keys sent, because that is true of the
    capture.
  - B08 shows the six real log lines as a figure instead of capture inserts.
  - B10 says "and no big roster" as drafted. B14 adds a 1.0 s silent tail hold.
- Words: 571. Narration measured: 187.3 s (`SHOTLIST.md`).

## 2. Capture

- `tools/make_capture_copy.sh` (copy of `godot/` + `capture_a8.gd`, 4K window override), then
  `godot --headless --path capture/game --import`.
- Dry runs: `capture/dryrun1.log` (round 2 held 120 ticks), then `capture/dryrun2.log` (held 360, so
  B06 has enough round-2 footage): 1938 frames, Akaken wins 58–0, K.O. at tick 1277.
- **Take 1 (discarded):**
  - First try: Bash syntax pasted into PowerShell 5.1, so nothing ran.
  - Second try: a key was pressed in the game window (Zhaohui: "按过"). The title went to the round
    at tick 127, and the log differs from the dry run. Kept locally as
    `capture/a8_round_take1_keypress.*`.
- **Take 2 (used):** started by Zhaohui, nothing touched.
  - `capture/a8_round.log` equals `dryrun2.log` on every `tick`/`capture` line (diff empty).
  - The `.avi` is 3840 × 2160, 60 fps, 1938 frames, 32.3 s.
- Stills: `tools/extract_stills.sh` (2.0 s title, 10.5 s fight), scaled only.

## 3. Audio

- Kokoro `am_onyx`, local, through `runtime/scripts/generate_audio_kokoro.py`; then `tools/pad_audio.py`
  (B14 +1.0 s tail). Respellings: Zhaohui Li → "Jow-hway Lee", Akaken, Aotake (on-screen text keeps
  the real spellings).
- Read back with faster-whisper `base.en` (`_qc/transcripts.json`). Accepted homophones:
  - names: "Jao Hui Li", "Akakan", "Arotake";
  - "Dusk dual"; "a K, O" (K.O.);
  - "fight around" for "fight a round" (B07);
  - "God out" for "Godot" (B13);
  - "or skills" for "are skills" (B13).

  No line had its meaning changed.

## 4. Pictures

- `tools/build_figures.py`: 11 figures. Everything not yet built sits in a dashed panel stamped
  "CONSTRUCTED · PROPOSED". Real output carries a green "REAL …" tag.
- `tools/build_media.py`: B01 (0–12.1 s), B02 (17.0–23.5 s, then 23.5 s on), B06 (6.0–14.0 s, then
  26.0 s on). All are real speed, with a persistent label on every frame.
- Remotion: 12 beats through `tools/render_queue.sh`.
  - First render: every figure/code beat showed a hard-coded `@NikBearBrown` footer.
  - Fix: the toolkit's `GodotDesignFigure.tsx` and `GodotDevWorkbench.tsx` now take a `handle` prop
    (default `@NikBearBrown`, unchanged for other reels). This reel passes `""`. Originals backed up
    to `D:\tmp\*.tsx.bak`.
  - Re-rendered with `--force` (the first re-render silently skipped existing clips). Footer checked
    on sampled frames: gone.

## 5. Gates

- `./art godot-gamedev --check`: **PASS**. 12 source files, 162 exclusions, 4 components, 1 exact
  excerpt, 1 code/result pair (`_qc/gamedev_check.json`).
- GATE T on the reel: **PASS**, 0 FAILs (`TYPECHECK.md`). Capture beats are SKIP ("no video").
- Masked GATE T: see `_qc/typecheck-masked/TYPECHECK.md`. The copy has the game area painted out;
  every beat is typed GRAPHIC so all pixel checks run.
- `compile.py` warnings expected: cold open not `ClaudeComposerAsk`, outro not `ClaudeTitleOutro`.
  The A8 handout forbids the instructor's credit line (FRICTIONAL).
