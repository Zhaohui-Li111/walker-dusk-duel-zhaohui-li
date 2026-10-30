# FACTCHECK — "Dusk Duel, Shaded"

Every factual claim in the narration or on screen, and where it was checked. "Repo" means
`walker-dusk-duel-zhaohui-li` at the film's build; `godot/` is unchanged since `043df17`.

| Beat | Claim | Checked against | Result |
|---|---|---|---|
| B00 | A5 adds two shaders Zhaohui typed by hand | `git log -- godot/shaders/`: f13d617, 25e6dd8 (and e6c40a6, a414f3b); commit messages; SOURCES.md | ✓ |
| B00 | Claude wrote the driver, tests and audit | sessions/session-2b, 2c, 2d, 3 and their commits | ✓ |
| B00 | 69 / 0 at 30, 60, 144; 96 / 0 from an empty cache; three mutations exit 1 | logs/test_hurt_flash_*fps.log; logs/test_materials_fresh_cache_60fps.log; logs/mutation*_60fps.log | ✓ |
| B00 | The Walker prompt | **Reconstruction** (labelled in runningText) | labelled |
| B01 | Headless proves parse, driving, wiring, not looks | the assignment text; TEST-REPORT A5 limitations | ✓, paraphrased |
| B02 | Aotake turns red for about a third of a second; then only Akaken flashes | capture/flash.avi frames: Aotake red 1.05-1.40 s, Akaken 4.2-4.4 s (_qc/flash, _qc/scan); 22 ticks = 0.367 s | ✓ (visual + rule 2) |
| B03 | The colour line was named before either shader | brief commit 4c8d90a precedes f13d617 | ✓ |
| B03 | Six hand predictions, two pixels, three values | CHANGE-BRIEF A5 prediction table; FRICTIONAL | ✓ |
| B04 | Line 1 canvas_item; lines 3-4 uniforms; line 7 the colour line | godot/shaders/hurt_flash.gdshader 1-8 (shown verbatim) | ✓ |
| B05 | Every pixel within one step; the shortfall is alpha 254 | capture/capture_a5_4k.log; logs/capture_a5.log; idle.png alpha 254 | ✓ |
| B06 | Lines 19-21 one material per fighter; line 27 stun / HITSTUN per physics tick; 22 ticks | godot/fighter/hurt_flash.gd 15-28 (shown verbatim); test_hurt_flash rule 2 | ✓ |
| B07 | Only Akaken flashes on the kick | capture/flash.avi 4.2-4.4 s | ✓ (visual) |
| B08 | Red saturates 1.0 and 2.0; grey 2.0 gives (34, 167, 254); not clamped | capture logs; fig_clamp arithmetic | ✓ |
| B08 | Zhaohui predicted "No" | CHANGE-BRIEF Revision 4, Q7 | ✓ |
| B09 | Real loop, J key, sampled every frame at 30/60/144 | godot/tests/test_hurt_flash.gd; logs | ✓ |
| B09 | First run failed four; two reasons; brief revised, not assertions; now 69 | logs from 7d245e3; CHANGE-BRIEF Revisions 6-7; diff of 7d4b352 (expectation changed with reason, none removed) | ✓ |
| B10 | Semicolon: empty list; rename: parses, 23 behaviour checks pass; source_color: material test fails | logs/mutation1/2/3 | ✓ |
| B11 | Lines 3-5 and their hints; uniforms in two groups | godot/shaders/granite.gdshader 1-23 (shown verbatim) | ✓ |
| B12 | Floor uv 6, plinth uv 1 and #6E6680; one value changes only the floor | godot/props3d/materials/*.tres; capture log | ✓ |
| B12 | Zhaohui checked that a shader edit changes both; "looks like wooden planks" | TEST-REPORT A5 human checks ("变了", "像木板") | ✓, Zhaohui's report |
| B12 | The box UVs stretch it | godot/MATERIALS.md findings 1-3 | ✓ |
| B13 | Each uniform swept; tint black "isn't good-looking" | capture/evidence/a5/granite_sweep_*.png; TEST-REPORT ("tint全黑不好看") | ✓ |
| B14 | One 3-pixel file, 64/128/192; lines 4-5; line 7 picks; unshaded | godot/shaders/hint_experiment.gdshader 1-15 (verbatim); write_hint_png.gd log | ✓ |
| B15 | Predicted 137/188/224 for B; both show stored values | CHANGE-BRIEF Revision 2; capture log | ✓ |
| B15 | Every albedo decoded, whatever the hint, then encoded | Godot 4.7.2 scene.glsl:2398, 2798 (read) | ✓ (source reading, consistent with the measurement) |
| B16 | Shader type instead of main; hints shape the Inspector | LANGUAGE-NOTES Q1, Q8; Godot shading language docs | ✓ |
| B16 | Generated line 7 matches Zhaohui's line 3 in source_color; line 19 uses hint_roughness_normal, which in the editor feeds the roughness import | standard_generated.gdshader:7, 19; granite.gdshader:3, 5; material_storage.cpp:953-967 | ✓ |
| B17 | What headless proves and cannot; Zhaohui's words; OS screenshot not done | TEST-REPORT A5 | ✓ |
| B18 | Claude's four mistakes | FRICTIONAL A5 entries; TEST-REPORT "What the agent got wrong" | ✓ |
| B18 | Next step: UV scale per axis | MATERIALS.md finding 1 | proposal |
| B19 | The handoff prompt | written for the viewer | — |
