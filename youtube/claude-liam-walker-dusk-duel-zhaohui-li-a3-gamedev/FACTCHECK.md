# FACTCHECK — "Dusk Duel, Measured"

Every factual claim in the narration or on screen, and where it was checked. "Repo" means
`walker-dusk-duel-zhaohui-li` at the film's build; `godot/` is unchanged since `1e88b83`.

| Beat | Claim | Checked against | Result |
|---|---|---|---|
| B00 | Dusk Duel is a 2D fighting game; A3 adds three simple 3D props | README.md; CHANGE-BRIEF.md A3 | ✓ |
| B00 | 100, 92 and 168 triangles | evidence/check-props3d.txt (tris per prop) | ✓ |
| B00 | Blender 5.2.2, mcp-for-blender 2.1.9, generators off | FRICTIONAL.md A3 setup; `get_addon_status` output; Zhaohui's screenshot | ✓ |
| B00 | 49 checks, 0 failed | evidence/check-props3d.txt | ✓ |
| B00 | The Walker prompt | **Reconstruction** (labelled in runningText); the work was many steps in one session | labelled |
| B01 | Checks prove measured size, not looks | the assignment text ("A passing check shows your assets arrived at the size you intended; it does not show they look right") | ✓, paraphrased |
| B02 | Lantern echoes the courtyard lanterns; makiwara is Akaken's punching post, pad at fist height; taiko is the source of the taiko loop | CHANGE-BRIEF.md A3 "In the game" lines (pad centre 1.20 m) | ✓ |
| B02 | The grey box is Akaken, 1.70 m | CHANGE-BRIEF.md scale reference; prop_room.tscn `Mesh_ref` 0.3 × 1.7 × 0.2 | ✓ |
| B03 | The brief was committed before any prop was built | `git log`: brief commit `30513a4` (on main) precedes `0f3e3f5` (the .blend files); FRICTIONAL "Second connection check" | ✓ |
| B03 | Seven predicted failure cases | CHANGE-BRIEF.md A3, items 1–7 | ✓ |
| B03 | A default 32-segment cylinder costs 124 triangles | 32 × 2 side + 2 × 30 cap = 124; also stated in the brief | ✓ |
| B04 | Zhaohui's own screenshot | evidence/blender/zhaohui_object_mode_taiko_selected.png (Win + PrtScn, 16:40; FRICTIONAL) | ✓ |
| B04 | The course's `claude mcp add -e … blender -- …` line failed because `-e` read the name as a second variable; name first worked | FRICTIONAL.md A3 "MCP setup", error text quoted there | ✓ |
| B04 | Port 9876; downloads and generators unticked | the screenshot itself; add-on source read in FRICTIONAL | ✓ (Tripo is not listed in the panel; `get_addon_status` reports it "off (Premium only)") |
| B05 | One execute_blender_code call per prop; the brief came from the parent Claude session | session record; FRICTIONAL correction entry | ✓ (the lantern and taiko each needed a 2nd call: save / origin fix) |
| B05 | Low segment counts; colours on the shader node; drum turned 90° and applied | tools/blender/build_*.py | ✓ |
| B05 | Printed lines, including `z -0.03 0.92` | the call's tool result, verbatim; the print() in build_taiko.py call 1 | ✓ |
| B06 | Failure case 3 was predicted | CHANGE-BRIEF.md A3 item 3 | ✓ |
| B06 | Join kept the base bar's origin, 3 cm up; scene info said on ground | FRICTIONAL "PROP-TAIKO built"; `get_scene_info` output in the session | ✓ |
| B06 | Fixed by moving the mesh, not the object | build_taiko.py call 2 (`mesh.transform(Translation(location))`) | ✓ |
| B07 | Each GLB is instanced at y = 0 with an identity basis; box centre y 0.85 | godot/props3d/prop_room.tscn lines 49–60 (shown verbatim) | ✓ |
| B08 | All three bases meet the floor in the low pass; heads face front and back | capture/orbit.avi 9.0–20.3 s, frames inspected (_qc/capture) | ✓ (visual) |
| B09 | Line 72 measures relative to the prop node; line 79 relative to the Floor top; line 81 tolerance 0.01 | godot/tests/check_props3d.gd lines 71–81 (shown verbatim) | ✓ |
| B10 | Raised 0.05 m in a copy → `FAIL: sits on the floor (gap 0.0500)`, 49 checks, 1 failed | evidence/check-props3d-raised-copy.txt | ✓ |
| B10 | The line-72 assertion still passed on the raised copy | same file: no FAIL line for "min y" | ✓ |
| B11 | Zero deviation; Blender Z = Godot Y via +Y up; scale 1, rotation 0; albedo hex exact | evidence/check-props3d.txt; tools/blender/export_glb.py (`export_yup=True`) | ✓ |
| B12 | Round bands stood about 4 cm out; ellipse option could not enclose the pad; chamfered 0.19 × 0.17 at 92 tris, 1.5 cm out | FRICTIONAL makiwara entries (geometry worked there) | ✓ |
| B12 | Zhaohui chose the chamfered rings | Zhaohui's answer "倒角矩形 0.19×0.17" | ✓ |
| B13 | Zhaohui edited the taiko by mouse in Edit Mode; body moved about 1 cm (1.2 cm); front head flattened | per-part and per-vertex comparisons (FRICTIONAL "Hand edit 1", "repaired", "Correction: the drumhead entry") | ✓ |
| B13 | Zhaohui typed "我不太会改，你改吧" | session record, verbatim | ✓ |
| B13 | Two repair calls; the first fixed only half | build_taiko.py calls 3–4; FRICTIONAL | ✓ |
| B14 | Saved edit: depth 0.53 m, 0 non-manifold edges | check_blend.py output; `get_scene_info` topology | ✓ |
| B14 | Red shows through; head flattened and twisted | MCP look render 16:29; vertex comparison. **Not claimed:** z-fighting (untested; see FRICTIONAL correction) | ✓ |
| B14 | 24 vertices restored; body nudge kept | build_taiko.py call 4; vertex comparison after repair | ✓ |
| B15 | Zhaohui looked from below and behind in Blender, walked round in Godot, said no problems | the two screenshots; "我看了一一下，没问题" after the Godot editor session | ✓ (one overall answer) |
| B16 | Four things Claude got wrong | TEST-REPORT A3 "What Claude got wrong" 1, 2, 3, 5 (item 4, the overexposed render, is left out for time) | ✓ |
| B16 | Source shown 1e88b83 | `git log -1 -- godot/` | ✓ |
| B16 | Contributions | SOURCES.md "Who did what in A3" | ✓ |

**Dated items stripped:** no model version for Claude is named in the narration. Tool versions
appear only on screen, where they are the subject.
