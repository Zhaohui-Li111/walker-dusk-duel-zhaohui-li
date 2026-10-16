# Visual QC (manual) — "Dusk Duel, Measured"

QC was done by Claude Code (Opus 5.5) reading the frames below. **No human has watched or listened to
the master yet.**

## Pass 1: rendered beats

Each beat's `media/Bxx.mp4` was sampled at 15/50/85 % (`_qc/beats/*_strip.png`) and read against
the 9-point rubric. Six defects were found and fixed at the root, then the beats were re-rendered and
re-read:

| Beat | Defect | Severity | Fix | Re-check |
|---|---|---|---|---|
| B01 | Typing unfinished at the cut ("human eyes caught the") | BLOCKER | text shortened, hesitations off | last frame shows all four lines ✓ |
| B09 | Line 81 below the code panel's bottom edge (wrapped lines) | MAJOR | excerpt 72–81, font 23 | line 81 visible and highlighted at 85 % ✓ |
| B04 | Screenshot UI text unreadable (screenshot at about 1/3 of the panel) | MAJOR | one crop of the MCP + Transform panels | panel text readable ✓ |
| B10 | Shadow gap too thin to see | MAJOR | tighter crop on the stand | gap visible under the raised base ✓ |
| B15 | Drum small in Zhaohui's screenshots | minor | tighter crops | ✓ |
| B14 | Status time 16:28 (render was 16:29) | accuracy | wording | ✓ |

The other 13 beats had no defects (edge bleed, safe margins, overflow, collisions, legibility, brand
bug, aspect, canvas fill). Accepted as house style, same as the A2 reel: the composer beats
(B00, B05, B13, B17) leave the lower third of the page empty, which is how ClaudeComposerAsk is laid
out.

## Pass 2: the final master

- **File:** `exports/landscape/claude-liam-walker-dusk-duel-zhaohui-li-a3-gamedev.mp4`. Probe:
  3840 × 2160, 30 fps, AAC 48 kHz stereo, 321.77 s.
- **Frames:** 644 frames at 2 fps (`_qc/frames/sheet_00–08.png`), read in order. Every beat appears
  in sequence with no black frames, no stale slates and no mistimed cuts. The B01 correction
  ("look" → "measure") lands and the overview completes. The B02 and B08 engine footage plays at
  real speed with its label. The outro card holds.
- **Audio:**
  - `volumedetect`: mean −27.1 dB, max −3.8 dB.
  - `silencedetect` (−45 dB, ≥ 1.5 s) finds one silence, 320.19–321.77 s. That is the outro's
    locked tail hold, as intended.
  - No narrated beat is silent.
- **Gates:**
  - GATE T: PASS on the reel (run again by `./art final`).
  - GATE V (`runtime/qc/final_frame_check.py` on the master, strict): see `_qc/REPORT.md`.
  - Masked copy: see `typecheck-masked/TYPECHECK.md`.
  - gamedev checker: PASS.

**Result: 0 BLOCKER, 0 MAJOR open.**

## Not checked by Claude

- **Sound:** whether the narration sounds right. Whisper misheard B17's last words ("Liam, in for
  Bear" came back as "Come in for bear").
- **A human viewing:** whether the film reads well to someone watching it.

Zhaohui should watch and listen to the master once before submitting.
