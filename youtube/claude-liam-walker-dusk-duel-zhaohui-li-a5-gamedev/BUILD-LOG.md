# BUILD-LOG — "Dusk Duel, Shaded" (godot-gamedev, walker mode)

Every deviation, workaround and failure in building this reel. Built by Claude Code (Opus 5.5)
for Zhaohui Li on 2026-10-29, in the session that did the A5 work, after Zhaohui said "Start the
film". The toolkit was not edited.

Host: Windows 11 Home China · Python 3.12.9 · Godot 4.7.2 (GL Compatibility, Intel UHD) ·
ffmpeg 9.0.2 · Kokoro `am_onyx` (local, free) · faster-whisper `base.en`.

## 1. What the assignment asks the film to show, and where it is

| Requirement (A5 text) | Beat(s) |
|---|---|
| The game, the state the effect communicates, the object given the textured shader | B00, B02, B12 |
| What a shader does (a line of code) | B04 (`hurt_flash.gdshader:7`) |
| How a material differs from a shader | B06 (`hurt_flash.gd:19-21`), B07, B12 |
| Why a texture is information | B11 (`granite.gdshader:3-5`), B14-B15 |
| What the Godot shading language is | B16 (`standard_generated:7, 19` beside `granite:3, 5`), B04 line 1 |
| The colour line in the spec, the shader and driver lines, controlled-value captures, the effect in play | B03, B04, B06, B05, B02/B07 |
| Hint experiment predicted and measured; interface sweep; two materials from one shader | B15, B13, B12 |
| Two annotated lines of the generated shader beside mine | B16 |
| What the tests proved, the mutations that failed them, what no headless run can show | B09, B10, B17 |
| Agent mistakes, uncertainty, next step, contributions, texture source, revision | B18 |
| Walker opening/summary, Verdict → Your Turn → regular outro | B00, B01, B18, B19, B20 |

## 2. Captures

- **Footage** (`capture/flash.avi`): Movie Maker on an isolated copy, 3840 × 2160 at 60 fps, 15 s.
  **Scripted input** (labelled on screen): the script places the fighters in punch range, presses
  `p1_punch` through `Input` twice, and gives Aotake a `ScriptedController` kick. The second punch
  whiffs (P2 health 92 after one hit). The first take was 8 s, too short for B02's narration;
  re-recorded at 15 s with the same events and the same end state (deterministic).
- **Stills:** `tests/capture_a5.gd` on the copy. **Windows clamps the window to the screen**, so
  the stills are 1924 × 1082 even with `--resolution 3840x2160`, also under Movie Maker. Used as
  they are; the sampled values match the repo's own run within one step.
- The first Movie Maker run failed (`ERR_CANT_OPEN`): the relative output path resolves against the
  project folder. An absolute path fixed it.

## 3. Narration

- Kokoro read 21 beats, 335.0 s. faster-whisper read every clip back (`_qc/transcripts.json`).
- **Re-voiced after the transcript:** B07 ("hurt amount" heard as "her to mount"), B11 ("colour,
  decode them" heard as "colored to code them"), B13 ("in Jow-hway's words" heard as "and jow each
  way's words"), B14 ("bool" heard as "bull"). Each was reworded, not respelled.
- The toolkit's generator re-made all 21 clips, not only the deleted four, which dropped the B01
  lead silence and the B20 tail. `tools/pad_audio.py` re-applied them from `mp3/raw/`.
- Whisper writes "Akakan" and "Aro Take" for Akaken and Aotake; accepted as close readings.

## 4. Rendering and the full C: drive

- Five Remotion queues started in parallel. **C: had 2.8 GB free** (99 %), and Remotion and
  Chromium write frames to the user temp folder on C:. Zhaohui pointed this out ("C盘空间好像不足了").
  The queues were stopped, and the leftover render processes were stopped by matching their command
  lines (`remotion`, `puppeteer_dev_chrome_profile`) only, not every Chrome. Four beats that were
  mid-render had failed (FFmpeg exit 0xC0000142 / duration conformance), most likely from the kill
  or the full disk. `tools/render_queue.sh` now sets `TEMP`/`TMP` to `D:\tmp\remotion`; the
  remaining 11 beats rendered there. Beats took 1-6 minutes each, not the A3 film's ~30.
- C: fell again to 4.3 GB during the second batch while the Temp folder grew only ~0.4 GB; the
  cause is outside this reel and was not investigated further on C:.

## 5. Visual QC

- Every beat's video length equals its narration within 0.03 s.
- Frames at 15 / 50 / 85 % of every beat (`_qc/contact_1.png`, `contact_2.png`), read by Claude.
  No BLOCKER or MAJOR. Minor, kept: B01's corrected line reads "The tests prove they parse right",
  because BrutalistHesitantWriter replaces one word.
- Figures first rendered Zhaohui's Chinese as boxes (Segoe UI has no CJK glyphs); fixed by using
  Microsoft YaHei for any string with Chinese.

## 6. Checks

- `./art godot-gamedev --check`: **PASS** — 32 source files, 102 exclusions, 7 components, 4 exact
  excerpts, 4 code-then-result pairs. It checks hashes, inventory and lines, not explanatory truth.
- `./art` needs `python3`; on this machine that is the Microsoft Store alias, so a shim pointing to
  Python 3.12 was put first on `PATH` (as the A3 build prompt says).
