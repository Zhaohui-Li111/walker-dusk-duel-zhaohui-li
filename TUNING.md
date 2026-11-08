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
