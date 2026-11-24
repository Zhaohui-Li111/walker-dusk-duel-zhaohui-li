# FACTCHECK — "Dusk Duel: Final Project Pitch"

Every factual claim in the narration or on screen, and where it was checked. "Repo" is
`walker-dusk-duel-zhaohui-li` at HEAD `dff6cba`; `godot/` is unchanged since `8049c54`
(`git diff --stat 8049c54 HEAD -- godot` empty). Claims about the future are marked **will** and
are on panels stamped CONSTRUCTED · PROPOSED.

| Beat | Claim | Checked against | Result |
|---|---|---|---|
| B00 | Built in Godot since Assignment 2 | README.md (A2 asset slice, Godot 4.7.2); commit history from 2026-10-05 | ✓ |
| B01 | Will be a web vertical slice: one stage, player vs CPU, title to K.O. and rematch | PROJECT-BRIEF.md Version 1 q1, Revision 3 item 4 | **will** (spoken as "will") |
| B01 | Footage is the real game with scripted input | capture/a8_round.log = capture/dryrun2.log (diff empty); tools/capture_a8.gd | ✓ labelled on every frame |
| B02 | Today: title, full round vs CPU, K.O., rematch, on desktop | godot/game/main.gd:1-5, 84-102; commit 6317281; capture log (K.O. tick 1277, result 1368, rematch 1519) | ✓ (visual + log) |
| B03 | New: web build, stronger CPU with adjustable difficulty, wider tests, re-runnable report | PROJECT-BRIEF.md Revision 2 q5/q7, Revision 3 item 4; no export_presets.cfg in godot/ | **will**, panel stamped |
| B04 | KOF '97 played by Zhaohui; fast combat, timing, defence | PROJECT-BRIEF.md Revision 2 q3, Revision 3 item 1 (Zhaohui's words) | ✓ as Zhaohui's statement; no KOF media used |
| B04 | No install / no online opponent / no setup | depends on the web build | **will**, panel stamped |
| B05 | Lines 50, 53, 55, 57 of cpu_controller.gd: block close attacks, walk in, step back, kick; new decision every 10 ticks | godot/fighter/cpu_controller.gd:11 (REACTION 10), 49-59 shown verbatim (`godot-gamedev --check` exact excerpt) | ✓ |
| B05 | Notes: block 55 %, kick 50 %, 40-tick cooldown | cpu_controller.gd:12-14 | ✓ |
| B06 | Aotake blocks punches, then kicks; round 2 has no keys sent; Aotake walks in and kicks a standing Akaken | capture log: BLOCKED at ticks 449–826 (7.5–13.8 s, inside the 6.0–14.0 s segment), P2 kick hits tick 668; round 2 from tick 1578, P2 kick hits 1676-1906; capture_a8.gd `_release_all()` in round 2 | ✓ (visual + log) |
| B07 | Role gameplay programmer; reader tech lead or recruiter; first 60 s plan | PROJECT-BRIEF.md q2, Revision 3 item 3 | **will**; times on screen labelled "a plan, not a measurement" |
| B08 | Shaders A5, particles A6, animation A7, each with headless tests; round pinned by 94 checks, all passing | tags a5, a6, a7; logs/test_runner_60fps.log:24 (94 checks, 0 failed); the five other log lines shown | ✓ |
| B09 | On this laptop's Intel UHD Graphics, hit sparks added about 0.01 ms GPU time | TEST-REPORT.md "GPU price": +0.012 ms median, Intel UHD Graphics, OpenGL 3.3; logs/gpu_price_windowed.log | ✓ (rounded) |
| B09 | Will measure desktop vs browser the same way | PROJECT-BRIEF.md Revision 2 q7 point 3 | **will** |
| B10 | Out: online play, second stage, character select, saves, big roster | PROJECT-BRIEF.md q4 | ✓ as plan |
| B11 | Milestone 1: full match in Edge on this machine; seven criteria; recording + report | PROJECT-BRIEF.md Revision 2 q5, Revision 3 item 2 | **will**, panel stamped, boxes unticked |
| B12 | Risk: web differs from desktop; export early; compare same scene; fallback | PROJECT-BRIEF.md q6 | ✓ as plan; left image real capture, right panel stamped |
| B13 | Have: shaders, particles, animation, tests, each with a tag; new: CPU, web, benchmarks, tests | PROJECT-BRIEF.md Revision 2 q7; tags a5, a6, a7; commit 6317281 | ✓ |
| B14 | Godot 4.7.2, Compatibility renderer; "exported to the web" | godot/project.godot:35-36; export is proposed (end card says "Web export (proposed)") | ✓ / **will** |

Not shown on purpose: no Claude response, no King of Fighters imagery, no playtest quotes, no player
numbers or metrics beyond the A6 GPU measurement and the test counts.
