# TUNING — Assignment 6

Every revision: Claude's prediction, the strips before and after, Claude's comparison and
Zhaohui's verdict in the running game. Strips from `godot/previews/` are **fixture captures**
(a preview scene with a fixed seed, not gameplay). Claude's readings are claims; Zhaohui's verdict
in the running game decides.

Captured with Movie Maker at 30 fps, 1280 × 720. Frame file N = preview frame N (checked on
`r0-lantern`: the first pixels change on `frame00000010.png`, the trigger frame).

## Effect A — hit spark

### r0 — first look (before Claude reads any strip)

Strips (fixture captures): `captures/hit_spark/r0/` (dark, 364, 202),
`captures/hit_spark/r0-lantern/` (lantern, 510, 208).

What I saw (preview window, 1280 × 720, 2026-11-08, Zhaohui's words): 火花比角色小很多，比较亮，持续5s左右，可以看得清。
(Translation: the spark is much smaller than the character, fairly bright, lasts about 5 s, and
can be seen clearly.)

*Claude Code's note, not part of the verdict:* the scene's `lifetime` is 0.6 s and the preview
fires twice, at frames 10 and 22 (1.0 s apart in total from first spark to last particle), so
"about 5 s" does not match the settings. Zhaohui to recheck whether 0.5 s was meant.

**Correction (2026-11-08, Zhaohui, after the r0 strip was read):** "改0.6吧" (change it to 0.6):
each burst lasts about **0.6 s**, not 5 s. The original sentence above is kept as written.

### Claude's reading of r0 (a claim, not a verdict; 2026-11-08)

Read from zoomed crops of frames 10, 12, 15, 20, 22, 24, 28, 30, 40, 50 of both strips, plus the
changed-pixel bounding box of each frame against frame 0 (capture px; viewport px = capture / 2).

| Frame | Intent (brief) | What the strip shows | Match |
|---|---|---|---|
| 10 | burst appears, bright compact flash | solid white disc ≈ 14 px across (viewport), the 20 stars overlap into one blob | yes |
| 12 | bright outward motion | white ring forming, ≈ 21 px across, still hot white | yes |
| 15 | sparks spread | a fairly even ring of cyan-white stars, ≈ 31 px across | partly: reads as a symmetric ring, not as "impact direction" |
| 20 | first burst slowing and fading | separate stars ≈ 47 px across; still clearly visible, fading only a little | partly: little visible fade yet |
| 22 | second burst appears, first still alive | new white disc in the centre, first burst's stars around it | yes |
| 24 | both bursts visible | both visible; widest extent ≈ 58 px across (radius ≈ 29 px, about 26% of Akaken's 112 px) | yes, at the top of the 15–30 px intent |
| 28 | first burst ends | first burst gone, second ring of stars | yes |
| 30 | second burst dissipating | second burst's stars, still fairly bright | yes |
| 40 | second burst gone | nothing changed against frame 0 | yes |
| 50 | nothing left | nothing changed against frame 0 | yes |

Against the background: on the dark wall (r0) the white/cyan stars stand out at every frame. Next
to the lantern (r0-lantern) the frame-10 flash sits on top of the lantern glow and is whiter than
it; from frame 20 the small cyan stars over the purple sky are dimmer but still visible.

Where the strip and the intent disagree, as Claude reads it:
1. **No impact direction.** `spread` 180° sends sparks evenly in all directions, so frames 12–15
   read as an expanding ring. The brief's job line says the burst "communicates impact direction".
2. **Late, small fade.** Between frames 15 and 20 the stars barely dim; most of the alpha drop
   comes in the last third of the life (the ramp's 0.35 → 1.0 stop), so dissipation looks short.
3. **Timing matches the settings:** the whole burst lasts 18 frames (0.6 s) and frames 40 and 50
   are empty. This does not match "about 5 s" in Zhaohui's first look above.

## Effect B — courtyard embers

### r0 — first look (before Claude reads any strip)

Strips (fixture captures): `captures/embers/r0/` (as in play: `emitting` on at frame 10, off at
frame 100), `captures/embers/r0-restart/` (control: `restart()` at frame 10, for the open
`preprocess` question). Frames to read: 10, 25, 55, 100, 115, 145, 175.

What I saw (preview window, 1280 × 720, 2026-11-08): Zhaohui asked Claude Code to write this
entry; Claude Code declined to write the verdict and asked three multiple-choice questions
instead. Zhaohui's answers, as chosen:
- When it started: **already filled** (a field of embers appeared at once).
- Against the courtyard: **too faint** (hard to see at all).
- After it stopped: **faded out slowly** over a couple of seconds.

### Claude's reading of r0 (a claim, not a verdict; 2026-11-08, after the first look above)

Read from full frames 9, 10, 25, 55, 100, 115, 145, 175 of both strips, a 1:1 crop of frame 55,
and the count of capture pixels that differ from frame 0 by more than 8 levels (of 921 600).

| Frame | Intent (brief) | Changed px r0 / r0-restart | What the strip shows | Match |
|---|---|---|---|---|
| 9 | before the condition | 0 / 0 | the bare courtyard | yes |
| 10 | preprocessed field already populated | 168 / 168 | particles present at once, inside y 125–305 (viewport) as the rect says | yes, but barely visible |
| 25 | slow movement | 230 / 230 | a few faint dots | partly |
| 55 | steady ambience | 215 / 215 | at 1:1 only two or three dim specks are findable on the door | **no: it does not read** |
| 100 | emission stops | 274 / 274 | same faint field | — |
| 115 | particles begin clearing | 237 / 237 | still the faint field | yes |
| 145 | few particles left | 62 / 179 | fewer | yes |
| 175 | none left | 0 / 0 | bare courtyard | yes |

- **Preprocess (open question 3):** both strips have the field on frame 10 and are identical up to
  frame 115, so in round 1 setting `emitting = true` already runs `preprocess`; `restart()` changes
  nothing at the start. (Round 2 and later are not covered by this preview.)
- **Visibility:** about 200 changed pixels out of 921 600: the field is almost invisible. Likely
  causes: alpha peaks at only 0.28; the particles are 4 × 4 px at 0.6–1.2 scale on a dark wall; and,
  if `color_initial_ramp` multiplies `color_ramp` (open question 5), the amber comes out darker
  still. This agrees with Zhaohui's "too faint".

## 2026-11-08 — Effect B, revision r1
What I saw (preview window, 1280 × 720): "too faint" (Zhaohui's first look above). This revision
is driven by that observation.
Claude's reading of r0: the field is present from frame 10 but only ~200 of 921 600 pixels
change at steady state; at 1:1 only two or three specks are findable on frame 55.
Change: `color_ramp` alpha at offset 0.20: 0.28 → 0.70, and at offset 0.75: 0.20 → 0.50 (one
setting; colours, offsets, size and amount unchanged). Approved by Zhaohui ("嗯，你不用问我，直接
做就行", "fine, you don't need to ask me, just do it").
Claude's prediction for r1 (same seed, so the same particle positions as r0):
- 9 and 175: empty, 0 changed pixels.
- 10: field present at once; changed pixels 168 → about 400–600; separate amber dots visible
  on the dark wall.
- 25 and 55: the same dots, clearly visible but still small; about 500 changed pixels (r0:
  215–230).
- 100: like 55. 115: thinning but visible. 145: a few dots, easier to see than r0's 145.
- Next to the lanterns the amber still blends with the glow (a judgement for Zhaohui).
- Still dimmer than the white/cyan additive hit spark (intent: never brighter than the spark).
Claude's comparison of r1 with its prediction (changed pixels r0 → r1):
- 9: 0 → 0; 175: 0 → 0. Matches.
- 10: 168 → 447. Matches (predicted 400–600).
- 25: 230 → 624; 55: 215 → 658. Slightly above the predicted "about 500"; same positions as r0.
  At 1:1 on frame 55, small amber specks are now findable across the door, the wall and the sky,
  still 1–3 px and subtle.
- 100: 274 → 713; 115: 237 → 571; 145: 62 → 195. Thinning as predicted, easier to see than r0.
- Next to the lanterns the specks are visible against the purple sky but merge with the lamp
  glow itself, as predicted. Still far dimmer than the hit spark.
My verdict (preview window, 1280 × 720, Zhaohui's words): "录完了，我感觉差不多" ("recorded; I feel
it's about right"). Recorded as **kept**. Zhaohui asked Claude Code to write the rest of this
entry ("你自己看着写点吧"); everything above this verdict line is Claude Code's.
Strips: captures/embers/r0/, captures/embers/r1/
Commits: 6f0c304 (change), this commit (strip r1 and verdict)

<!-- Revision template (copy for each revision):

## <date> — Effect A, revision r<N+1>
What I saw (running game, <window size>):
Claude's reading of r<N>:
Change: <setting> <old> → <new>, approved by me
Claude's prediction for r<N+1>:
Claude's comparison of r<N+1> with its prediction:
My verdict (running game, <window size>): kept | reverted, because
Strips: captures/<effect>/r<N>/, captures/<effect>/r<N+1>/
Commits:
-->
