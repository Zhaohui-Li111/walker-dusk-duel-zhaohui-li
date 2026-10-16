# BUILD-LOG — "Dusk Duel, Measured" (godot-gamedev, walker mode)

Every deviation, workaround and failure in building this reel. Built by Claude Code (Opus 5.5)
for Zhaohui Li on 2026-10-16, in the same session that built the props.

Host: Windows 11 Home China 10.0.26200 · Python 3.12.9 · Godot 4.7.2 · Blender 5.2.2 LTS ·
ffmpeg 9.0.2 · Kokoro `am_onyx` (local, free) · faster-whisper `base.en`.

The toolkit environment (ffmpeg, Kokoro, Remotion node modules, the `npx` fix in
`runtime/scripts/remotion_scenes.py`, and the A2 handle fix in `GodotDesignFigure.tsx`) was already
installed from Zhaohui's earlier reels. **No toolkit file was changed for this reel.**

## 1. What the assignment asks the film to show, and where it is

| Requirement (A3 text) | Beat(s) |
|---|---|
| The game, the three assets and why the game needs each | B00, B02 |
| Zhaohui's real Blender session: own screenshots, labelled | B04, B15 (Zhaohui's screenshots, labelled as such) |
| At least one prompt to Claude and what it built | B05 → B06 (the build brief), B13 → B14 (Zhaohui's own prompt) |
| Zhaohui's own hand edit | B13–B14. **No recording of the edit itself exists**: it was saved before anyone thought to record it. The film shows its saved result (MCP look render) and says so. |
| The three assets in the running Godot scene | B02, B08 (engine capture) |
| The headless numbers beside the brief, labelled as headless | B11 ("HEADLESS" banner), B09–B10 |
| What was checked, what is uncertain, what Claude got wrong, a next step, human/AI contributions, the source revision | B16 |
| Walker opening/summary, Verdict → Your Turn → regular outro | B00, B01, B16, B17, B18 |

## 2. The Blender code is outside the gamedev ledger

- **The constraint:** `verify_gamedev.py` accepts excerpts only from files under the folder that
  holds `project.godot` (`godot/`). The Blender scripts live in `tools/blender/`.
- **The choice:** the Blender side is shown as two ASK → RESULT pairs with the calls' real
  printouts, not as GodotDevWorkbench code. Calling them "Godot editor" views would have been false.
- **What the ledger certifies:** the two Godot code → result pairs, B07 → B08 and B09 → B10.
- **Where the Blender evidence is recorded:** SOURCES.md.

## 3. Captures

- **Isolated copies:** `tools/make_capture_copy.sh` makes `capture/game` (a copy of `godot/` plus two
  camera scripts and a 4K window) and `capture/game-raised` (the same, with the taiko at y = 0.05,
  for the labelled failing-check still).
- **One crash:** the first `--import` of `capture/game` segfaulted (exit 139) after importing. A
  second `--import` exited 0, and everything was rendered after that.
- **Stills reframed:** the first `taiko_floor` still cut off the drum's top. The camera was moved
  back (2.4, 0.22, 2.2 → target 0.5, 0.42, 0) and both stills were re-rendered. The first crop of
  `fig_floor_check` missed the base and showed no gap, so it was re-cropped to the stand.
- **Timing:** the orbit is real speed. The 60 fps capture is written at 30 fps by dropping frames.

## 4. Narration: respelling, checked with Whisper

- **First pass:** whisper read "taiko" as "take-o". In B10 "raised the taiko five centimetres" came
  back as "raised the take 0.5 centimeters", which changes the meaning. It also read "makiwara" as
  "Macuara".
- **The fix:** `build_beatsheet.py` respells only the narration (`tie-koh`, `mah-kee-wah-rah`). On
  screen the real spellings stay. All 19 beats were re-voiced (`mp3/raw` cleared first, so
  `pad_audio.py` padded the new takes).
- **Second pass:** "tyco/taiko" and "five centimeters" come back correctly.
- **Still uncertain:** B17's closing "Liam, in for Bear" came back as "Come in for bear". The same
  words in B00 came back correctly, so this is probably a base-model miss at the end of a long take.
  **It needs a human ear**, because Claude cannot listen.

## 5. Facts corrected before voicing

These are in SOURCES.md and FRICTIONAL.md:
- The build prompt was not Zhaohui's.
- The drumhead defect is not established as z-fighting.
- "One call per prop" needed qualifying: the lantern and the taiko each needed a second call.

## 6. Rendering

- **Speed:** `remotion_scenes.py` renders at `--concurrency=1 --scale=2`. B05 alone took 30 min.
- **The workaround:** the remaining 16 beats ran as four parallel `--only` queues. The script reads
  the sheet at its start and rewrites it at its end, so parallel runs only race on the "rendered"
  stamps. `build_beatsheet.py` regenerates the sheet afterwards anyway.
- **Sleep:** keep-awake was requested for the render (the A2 render stalled when the machine slept).

- **Four renders failed, and C: is the likely cause.**
  - The first parallel run lost B16, B17, B04 and B13. Each logged only "FAIL: <pattern>"; the
    queue's grep had dropped the detail.
  - C: had 4.9 GB free, and Remotion writes its bundles and frames to %TEMP% on C:. Four 4K renders
    at once probably ran it out. This is likely, not proven.
  - Zhaohui flagged the low disk at the same time.
- **What was done:**
  - The renders were stopped and their leftover processes ended.
  - TEMP/TMP point at `D:\coursesǗ0\.render-tmp` for every render from now on.
  - B16 re-rendered alone and succeeded in 2:53.
  - The remaining 12 beats run as two queues.
- **C: cleanup at Zhaohui's request:**
  - npm cache, 2.5 GB, cleared with `npm cache clean --force`.
  - pip cache, 575 files, cleared with `pip cache purge`.
  - Claude's own temp files from this session and the Remotion and Chrome profile leftovers removed.
  - Nothing else on C: was touched.

## 7. Visual QC on the rendered beats (before the cut)

Each beat was sampled at 15/50/85 % and read (`_qc/beats/*_strip.png`). Defects found and fixed:

| Beat | Defect | Severity | Fix |
|---|---|---|---|
| B01 | The writer had not finished typing at the cut: it ended on "human eyes caught the" | BLOCKER | Text shortened to four short lines, hesitations off; re-rendered. The last frame shows the corrected overview in full. |
| B09 | Code lines wrapped, so line 81 (the floor check) sat below the panel's bottom edge | MAJOR (container overflow) | Excerpt 72–81, code font 23; re-rendered. Line 81 is now visible and highlighted. |
| B04 | Zhaohui's screenshot shrank to about a third of the panel; its UI text was unreadable | MAJOR (legibility) | The figure is now one crop covering the MCP panel and the Transform panel, filling the frame. |
| B10 | The 5 cm shadow gap was too thin to see at film size | MAJOR | Crop tightened to the stand. |
| B15 | The drum was small in Zhaohui's bottom/back screenshots | minor | Crops tightened. |
| B14 | The status said the render was at 16:28; it was at 16:29 (the edit was saved at 16:28) | accuracy | Wording corrected. |

## 8. GATE T and the gamedev checker

- **GATE T, first run:** FAIL. §8.10: the inner ask beats B05 and B13 had empty greetings, and the
  SPARK-LINE LAW wants a line of four words or fewer. They got "Starts below zero." and "You fix
  it.", and were re-rendered. **GATE T: PASS.**
- **gamedev checker:** `./art godot-gamedev --check` gives PASS: 9 source files, 95 exclusions,
  3 components, 2 exact excerpts, 2 code/result pairs.
- **Masked copy** for the diegetic beats: see `_qc/typecheck-masked/TYPECHECK.md`.

## 9. The review cut failed on a toolkit bug; the final cut avoids that code path

- **The bug:** `./art run` encoded all 19 beats, then failed in the review-only timecode overlay.
  `compile.py` passes `fontfile=D:\...\EBGaramond-Regular.ttf` to ffmpeg's drawtext unescaped, and
  ffmpeg reads the Windows backslashes as escapes ("No option name near
  'courses7270brutalist…'").
- **Why the final is unaffected:** the drawtext branch runs only with `--review`.
- **What was done:** the toolkit was not edited. QC was done on the beat media and then on the final
  master itself.

## 10. Final master

- **Command:** `./art final <reel> --height 2160 --fps 30 --out <reel>/exports/landscape`, with
  TEMP/TMP on D:. It ran GATE T again (PASS), compiled 19/19 filled beats, and wrote the
  hash-bound receipt `exports/landscape/*.verified.json`.
- **Output:** `claude-liam-walker-dusk-duel-zhaohui-li-a3-gamedev.mp4`
  - 3840 × 2160, 30 fps, AAC 48 kHz stereo, 321.77 s, 29.7 MB.
  - SHA-256 `9331a6244a9c8e33ef414912a8e3d0a02cff78ce59994771401339ab61c771d2`.
- **Gates:**
  - GATE T: PASS on the reel, and PASS on the masked copy with every pixel check on all 19 beats
    (`_qc/typecheck-masked/TYPECHECK.md`).
  - GATE V on the master: 38 frames, 0 BLOCKER, 0 MAJOR, in both lenient and strict mode
    (`_qc/REPORT.md`).
  - gamedev checker: PASS.
- **Manual QC:** 644 frames at 2 fps, plus an audio level and silence check. See `_qc/VISUAL-QC.md`.
- **A mistake in QC bookkeeping:** Claude wrote its manual QC notes to `_qc/REPORT.md` without
  reading that file first, and overwrote the GATE V report that `./art final` had written there.
  The notes were moved to `_qc/VISUAL-QC.md`, and GATE V was re-run on the master to regenerate
  `_qc/REPORT.md`.
- **Not done by Claude:** watching and listening with human eyes and ears. Zhaohui should play the
  master once before submitting, and listen for B17's sign-off in particular.
- **Not on GitHub:** the MP4 (over 25 MB, and MP4 is gitignored). It goes to the course media
  storage, and README carries its file name and SHA-256.

## 11. Contributions

| Who | What |
|---|---|
| **Zhaohui Li** | Chose the props and the film workflow, and asked for this film. Took the three Blender screenshots. Made the hand edit. Did the Godot look check. Flagged the full C: drive. |
| **Claude Code** | Wrote the beat sheet, narration, figures and every tool in `tools/`. Ran the captures and the renders. Made the QC judgements, and corrected its own logged errors. |
| **Local models** | Kokoro voiced the narration. faster-whisper checked it. |
