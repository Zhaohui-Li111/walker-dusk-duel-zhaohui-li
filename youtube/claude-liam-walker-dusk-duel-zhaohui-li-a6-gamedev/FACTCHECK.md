# FACTCHECK — "Dusk Duel, Sparked"

Every factual claim in the narration or on screen, and where it was checked. "Repo" means
`walker-dusk-duel-zhaohui-li` at HEAD `55f231b`; `godot/` is unchanged since `840bcfd`.

| Beat | Claim | Checked against | Result |
|---|---|---|---|
| B00 | A6 adds a hit spark and courtyard embers | CHANGE-BRIEF.md (A6) header; `godot/effects/` | ✓ |
| B00 | Zhaohui wrote the brief, every setting and prediction | CHANGE-BRIEF.md authorship note ("I wrote it", "I wrote it myself"; third round not asked separately); SOURCES.md A6 | ✓, as recorded (Claude Code's factual and consistency edits marked inline in the brief) |
| B00 | Claude Code and its agents built the scenes, controllers and tests | SOURCES.md A6; commits 0ac83ee, 607f5d1, 220b5a8, 6b55ff8, fbb55af; `sessions/a6/` | ✓ |
| B00 | RESULT lines 69/0, 85/0, 57/0, 38/0; under budget | logs/test_hit_spark_config_60fps.log:77, test_embers_config:93, test_hit_spark_state:112, test_embers_state:75; TEST-REPORT A6 prices | ✓ |
| B00 | The Walker prompt | **Reconstruction** (labelled in runningText) | labelled |
| B01 | Headless proves firing, freezing, price; not the look | TEST-REPORT A6; README A6 limitations ("Headless runs see node state, never particles") | ✓, paraphrased |
| B02 | No embers on the title; field present when the fight begins; cyan particles around the old white code-drawn star | capture/a6_play.log (embers_emitting false in title/intro, true at tick 150); frames of capture/a6_play.avi (_qc); `effects.gd:31-35` draws the white 8-line spark (brief, project facts) | ✓ (visual + log) |
| B03 | Job, event `attack_resolved` result hit at point; flash, ~0.2 s outward, 0.6 s lifetime; contrast 13.1:1 and 3.0:1; 4 slots × 20 | CHANGE-BRIEF A6 Effect A (job, facts, intent block, settings) | ✓ |
| B04 | Fixture capture, fixed seed, fires at frames 10 and 22 | godot/previews/hit_spark_preview.gd:12-13, 43-44; TUNING.md | ✓ |
| B04 | First look quote and its correction to 0.6 s | TUNING.md Effect A r0 (Chinese original + translation; "改0.6吧") | ✓ verbatim |
| B05 | Claude's reading (ring at 12-15); Zhaohui chose "It reads as a ring" from Claude's options; change 45 → 15; prediction of same edge | TUNING.md Effect A r1 | ✓ |
| B06 | Lines 17, 19, 20, 22, 25, 27-30 of hit_spark.tscn and their roles; emission / process / draw split | godot/effects/hit_spark.tscn 17-30 (shown verbatim); CHANGE-BRIEF short answer 6 (Zhaohui's split, revised after review N) | ✓ |
| B07 | Ring gone; 58 → 48 px across at frame 24 (31 → 27 at 15); Claude's edge prediction wrong; radius ~24 px inside 15-30 | TUNING.md Effect A r1 comparison; captures/hit_spark/r0, r1 | ✓ |
| B07 | Verdict "Yes, I saw it", "Keep" | TUNING.md ("from two questions Claude Code asked") | ✓ verbatim, the question context shown on screen |
| B08 | Lines 43, 45, 47, 56 of hit_spark_pool.gd | godot/effects/hit_spark_pool.gd 43-56 (verbatim) | ✓ |
| B08 | Neither pause nor hitstop pauses the tree | main.gd:55-62, 105-116; brief project facts | ✓ |
| B09 | Sparks frozen during pause, then finish; hits 0.5 s apart overlap | capture/a6_play.log (pause 5.72-8.72 s, sparks_emitting 2 at pause; hits every 30 ticks < 36-tick lifetime); frames (_qc) | ✓ (visual + log) |
| B10 | Job ambience; condition phase == fight; rect 560 × 180; preprocess 1.5 s | CHANGE-BRIEF A6 Effect B; embers.tscn:29, 33-34 | ✓ |
| B11 | Condition on at 10, off at 100; first look as three multiple-choice answers; ~200 of 921 600 px; preprocess runs on emitting (r0 = r0-restart to 115) | TUNING.md Effect B r0; embers_preview.gd:12-13 | ✓ |
| B12 | Lines 27, 29, 33, 34; alpha change on line 18 | godot/effects/embers.tscn 21-34 (verbatim) and :18 | ✓ |
| B13 | Alpha 0.28 → 0.70, 0.20 → 0.50; predicted 400-600; measured 447; later counts above "about 500"; verdict quote | TUNING.md Effect B r1; CHANGE-BRIEF Revision 2 | ✓ |
| B14 | Polls phase each tick; line 28 restart (preprocess each round); line 30 stop; speed_scale 0 in pause/hitstop | godot/effects/embers_controller.gd 20-33 (verbatim), :37 | ✓ |
| B15 | K.O. stops emission; embers fade; rematch, field back | capture/a6_play.log (embers_emitting false at K.O. tick 793; true at round-2 fight tick 1053); frames (_qc) — the fade is faint at full frame | ✓ (log; visual faint) |
| B16 | Pause/hitstop speed_scale 0 every tick; tree pause stops node; hidden: never finishes within 600 ticks, 153 plain, 215 with tree pause, 151 after shown; option 1 ("那就1吧"); indirect | TEST-REPORT A6 (state tests, open finding); CHANGE-BRIEF Revision 4; logs/test_embers_state_60fps.log:61, 65 | ✓ |
| B17 | Zhaohui generated the shader in the editor; lines 137, 260, 307, 320 as shown; ramp and scale curve dropped (348, 147) | TEST-REPORT A6 "The process shader"; godot/shaders/particles_generated.gdshader (lines copied verbatim into the figure); commit 840bcfd | ✓ |
| B17 | Zhaohui cited 10, 43, 189; Claude Code's check moved them | TEST-REPORT A6 line-reference table | ✓ |
| B18 | 69 and 85 config checks, 0 failed; state: 16 hits → 16 bursts, 31 others → 0; frozen | TEST-REPORT A6; logs | ✓ |
| B18 | Mutation 1 loads silently, exit 1 with 2 failed; Zhaohui saw slower sparks; mutation 2 exit 1, 1 failed | TEST-REPORT A6 mutation table; logs/mutation_a6_1_*, mutation_a6_2_* (69 checks, 2 / 1 failed) | ✓ |
| B18 | Earlier suites unchanged | TEST-REPORT A6 (all earlier suites after wiring) | ✓ |
| B19 | CPU medians A 0.010, B 0.006 ms; budgets 0.25 / 0.50; predictions 0.08 / 0.05 | TEST-REPORT A6 headless CPU price; logs/cost_effects_60fps.log:102-103 | ✓ |
| B19 | Headless GPU ≈ 0 because the process is a shader and the dummy renderer runs none; CPU nodes still drawn by GPU | CHANGE-BRIEF short answer 4 and price section (Zhaohui) | ✓ |
| B19 | Visual Profiler read 0 (Zhaohui); GPU measured by Claude Code, windowed: +0.012, +0.004 ms | TEST-REPORT A6 GPU price; logs/gpu_price_windowed.log:58; commit 7888427 | ✓ |
| B20 | In-play report quote; does not name the specific checks; fallback never reached | TEST-REPORT A6 "In play"; README A6 limitations | ✓ verbatim |
| B21 | Cost script measured itself (TIME_PROCESS), control caught it; generator through wrapper and `rm` of the log; star check failed its own texture (7.72 / 5.46); late `finished`; denied commands | FRICTIONAL.md A6 (steps 2, 3/5, 7); TEST-REPORT A6; commits 873d614, e96c916 | ✓ |
| B21 | Claude misread a strip (edge prediction) | TUNING.md Effect A r1 | ✓ |
| B21 (figure) | Claude's own brief error `main.gd:25` → `:24` | CHANGE-BRIEF Revision 2; FRICTIONAL | ✓ |
| B22 | Verdict lines; Zhaohui's and Claude Code's contributions; delegation; textures by make_textures.gd; source 840bcfd; next step direction | SOURCES.md A6; FRICTIONAL; README A6 limitations (no impact direction) | ✓ |
| B22 | "after Jow-hway said: do the rest yourself" | FRICTIONAL.md A6: "你把剩下的任务自己做完吧" (translation by this build) | ✓, translated |
| B23 | Handoff prompt | written for the viewer | — |
| B24 | Title, handle | OUTRO-LOCK.md | ✓ |

**Not claimed:** no human playtest beyond Zhaohui's one-sentence in-play report; the tuning verdicts
were given in the preview window (TUNING.md says so), not in the running game; no claim that
Zhaohui watched this film.
