# FACTCHECK — every spoken or on-screen claim, against its source

Checked by Claude Code on 2026-10-06 against revision `4e0cf14`. ✓ = verified. ✎ = corrected
before render (see SOURCES.md, Corrections).

| Beat | Claim | Source | |
|---|---|---|---|
| B00 | Its fighters, courtyard, sound effects and music came from free models | ASSET-LOG; repo SOURCES.md (SDXL stack, Stable Audio Open, MusicGen on a free Colab T4) | ✎ |
| B00 | RESULT: "Godot test run: 94 checks, 0 failed." | evidence/test-run.txt | ✓ |
| B00 | The Walker prompt is a reconstruction | labelled on screen ("reconstructed ask") | ✓ |
| B01 | The design sheet fixed poses, colours and events first; tests checked the fit | CHARACTER-SHEET.md and CHANGE-BRIEF.md predate generation (git log b8f1815 → 1b8e5c8) | ✓ |
| B02 | Akaken is scripted keyboard input; Aotake is the game's seeded CPU | tools/capture_driver.gd; main.gd `CpuController.new(7270 + round_number)` | ✓ |
| B02 | The sparks and health bars are drawn by code | game/effects.gd and game/hud.gd `_draw()` | ✎ |
| B03 | Green box = hurtbox, red box = hitbox from elbow to fist; five colours | design/character/akaken/collision.png legend; CHARACTER-SHEET.md revision 2; palette table | ✓ |
| B04 | Rounds 1–3 prompt only: no red gi, beards, a turban for the headband | FRICTIONAL.md rounds 1–3; the round-1 and round-3 sheets on screen | ✓ |
| B04 | Round 4 at strength 0.6 was too close to the mannequin; round 5 at 0.75 kept | FRICTIONAL.md; ASSET-LOG strength column | ✓ |
| B05 | ControlNet steers the pose; colour-block start; IP-Adapter from the round-5 reference | ASSET-LOG CHAR-AK-PUNCH rows (control_image, init_image, ip_reference s143) | ✓ |
| B05 | Claude chose s201 for Zhaohui: palette 47.4 vs 51.8 | ASSET-LOG reasons, "Decided by Claude" | ✓ |
| B05 | Background cut away; scaled to 108 × 158 | ASSET-LOG edits for s201 (rembg; ×0.1296) | ✓ |
| B06 | Hip from keypoints 8 and 11; anchor at the ground line; boxes from the pose; generated image wins over the placeholder | fighter_art.gd lines 35–44 (on screen) | ✓ |
| B07 | Feet on the ground line; hurtbox over the body; faint hitbox on the fist | punch_4k.png; fighter.gd `_draw()` draws inactive hitboxes at alpha 0.35 | ✎ |
| B08 | Active frames only; blocked or not decided by the defender; resolved exactly once | fighter.gd 160–172; header comment lines 10–15 | ✓ |
| B09 | Spark at the overlap, bar drops, push-back | B09 frames at +0.3, +0.5 and +1.2 s; HIT_PUSH in fighter.gd | ✓ |
| B10 | Four events, four takes each; measured, not heard | ASSET-LOG SFX-*; spectrogram figure | ✓ |
| B10 | Hit with no lead-in and the most weight; block for its bright clack | SFX-HIT_s12 0 ms, 92.7 %; SFX-BLOCK_s14 2780 Hz (s13 brighter, but a 120 ms lead-in) | ✎ |
| B11 | One result, one sound; knockout plays the K.O. sound and stops the loop; never changes state | audio_director.gd 100–108 and its header | ✓ |
| B12 | Whiff, block and hit in that order | B12 frames at +0.6, +1.4 and +2.6 s; driver log ticks 180, 223, 297 | ✓ |
| B13 | The slice's own audio, no narration | CAPTURE.md B13 audio route | ✓ |
| B14 | The test places the dummy by hand; it proves the wiring, not reachability or sound quality | test_runner.gd 351 `p2.position.x = …` | ✓ |
| B15 | 94 checks; 13 attacks → 13 requests; the muted run ends with the same health, positions and phase | test-run.txt; test_runner.gd 393–415 | ✎ |
| B15 | The "image shows a body" check came from the rembg bug | FRICTIONAL.md 2026-10-06 export bug; test_runner.gd 149–158 | ✓ |
| B16 | Zhaohui: theme, design, plan B, the playtest. Claude: docs, code, prompts, colour blocks, picks after round 3 | FRICTIONAL.md "Human / Claude / model" lines; TEST-REPORT (playtest) | ✓ |
| B16 | Limits: lighter top, blank face, five Aotake poses, non-commercial licences | FRICTIONAL.md; README Known limitations | ✓ |
| B18 | Exact title, @NikBearBrown, spoken, no jingle | OUTRO-LOCK.md | ✓ |

## Dating check

- The narration names no model version numbers or counts that will drift. Commits and versions
  appear only in the source lines on screen.
- "94 checks" is tied to revision 4e0cf14 on screen.
