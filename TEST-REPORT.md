# TEST-REPORT — walker-dusk-duel asset slice

> Draft by Claude Code, updated 2026-10-06 with the generated art and audio. Sections marked
> **TO DO (human)** need Zhaohui's own words; Claude has only recorded what Zhaohui said in chat.

- Engine: Godot 4.7.2 stable (GL Compatibility), Windows 11 Home
- Source revision for the automated results below: `431f03f` (all generated art, music loop and
  four sound effects in place; re-run on the submitted revision if anything changes)

## Automated check

```bash
godot --headless --path godot --script res://tests/test_runner.gd
```

Result at `431f03f`: **94 checks in 18 tests, 0 failed**. At `0cdd8a7`, with placeholder art, it
was 78 checks. The suite steps the fight scene frame by
frame with scripted input (no real-time waiting):

| Area | Tests | What they assert |
|---|---|---|
| Movement and state images | 5 | walk distance and facing; a held attack button starts one attack; jump shows rise and fall; crossing over flips both fighters; every state has an image, the idle hurtbox reaches the feet, and **every state image shows a body** (at least 300 opaque pixels sampled; added after rembg erased Aotake's K.O. pose) |
| Combat and round flow | 9 | one punch = one hit and 8 damage; point-blank attacks connect; out-of-range attacks whiff; blocking takes no damage; the hurt fighter is pushed away from the attacker; one K.O., then result screen and rematch; every attack resolves exactly once (CPU vs scripted mix); the seeded CPU is deterministic; pause freezes everything |
| Sound and music | 4 | **each attack requests exactly one sound** (held punch, mashing every 3 frames, 3 kicks, 2 blocks, 2 whiffs → 13 attacks, 13 sounds); final hit plays SFX-HIT then SFX-KO once each; music starts on the title, ducks −12 dB with a low-pass on pause, stops at K.O., stays stopped on the result screen and restarts on rematch; **a seeded fight ends identically with both buses muted** |

Assertions that were wrong and how they were handled are in FRICTIONAL.md (2026-10-05 step 2 and
step 3 entries): two test *scenarios* were corrected after the failure was understood; no
assertion was weakened.

## Startup and controls

Fresh clone of the submitted revision → open `godot/project.godot` → F5. Record: runs without errors?
every control in README works?

- 2026-10-07, automated part: `git clone https://github.com/Zhaohui-Li111/walker-dusk-duel-zhaohui-li`
  at `9b0c696` into an empty folder, then `godot --headless --path godot --import` and the test run.
  Result: **94 checks, 0 failed**, and no "no file yet" warning, so every used art and audio file is
  present in the clone. This does not replace opening it with F5 and playing it.

- 2026-10-06: Zhaohui played the slice at `431f03f` and said in chat that it was fine overall
  ("还可以"). Details per control: see the next line.
- 2026-10-07, Zhaohui's playtest answer (in chat, translated from Chinese): asked whether move, jump, crouch, punch, kick, block, pause and the M/N mutes, Zhaohui answered "没问题，都正常着" ("no problems, everything works normally"). This is one overall confirmation, not a per-item log.

## Character against the sheet

In-engine captures of each state with F1 boxes on (`godot --path godot --script res://tests/capture_states.gd`
→ `evidence/states/`, contact sheet `evidence/states_contact.png` from `python tools/make_contact.py`),
compared with the CHARACTER-SHEET poses by Claude. Zhaohui has not re-judged them.

- **Boxes against the art:** in all 11 states both fighters' feet sit on the ground line and the
  hurtbox covers the body. The punch and kick hitboxes reach the fist and the foot.
- **Matches the sheet:** Akaken keeps the headband, topknot, wrapped fists and stocky build in every
  pose. Aotake keeps the straw hat, braid, teal robe and navy sash.
- **Mismatches, accepted:**
  - Akaken's top is a lighter orange than `#D9482B`.
  - RISE has no yellow belt.
  - FALL's belt is green, picked up from the background.
  - The accepted reference (s143) has a blank face, which barely reads at game size.
  - Aotake has 5 drawn poses; walk, jump and win reuse other images (CHARACTER-SHEET appendix).
- **Found and fixed:** Aotake vanished at K.O. because the background remover erased the lying
  pose. It was re-exported with a chroma key, and a test now guards this.

## Storyboard against the slice

`godot --path godot --script res://tests/capture_flow.gd` → `evidence/flow/` (scripted-input captures,
contact sheet `evidence/flow_contact.png`), compared with the panels by Claude.

| Panel | Capture | Match |
|---|---|---|
| 1 Title | `01_title` | yes: dusk courtyard, both fighters, "press Enter" |
| 2 Fighter intro | `02_round_call` | partly: the slice shows a round call over the stage rather than a separate intro card (design view) |
| 3 Jab meets block | `03_block` | yes: block spark, no health lost |
| 4 Kick lands | `04_hit` | yes: hit spark, Aotake's bar drops |
| 5 Player is hit | `05_player_hurt` | yes: Akaken's hurt pose, bar drops |
| 6 K.O. (loss) | none | **not captured:** the scripted run ends with Aotake knocked out (`07_ko`); the losing K.O. uses the same code path but has no capture (design view) |
| 7 Rematch | `09_rematch` | yes: "ROUND 2 - FIGHT", both bars full |
| 8 Victory | `07_ko`, `08_result` | yes: "AKAKEN WINS", Enter rematch / Esc quit |

Extra captures: `06_paused` (pause overlay) and `06b_muted_indicator` (both buses muted, shown in the HUD).

## Sound events

Play normally, then mash punch and hold punch: each whiff / hit / block / K.O. should be heard once.

- Automated: the one-sound-per-event tests pass with the real files loaded (no "no file yet" warning).
- Files: whiff 0.35 s, hit 0.40 s, block 0.40 s, K.O. 2.50 s; decoded peaks −1.0 to −1.5 dBFS.
  Picks were made by measurement, not by ear (FRICTIONAL 2026-10-06, sound effects).
- 2026-10-07, Zhaohui's playtest answer (in chat, translated from Chinese): asked whether hit, block, whiff and K.O. can be told apart, and each sounds once, Zhaohui answered "没问题，都正常着" ("no problems, everything works normally"). This is one overall confirmation, not a per-item log.

## Music

Loop heard at least three times round without a click or gap; pause muffles it; K.O. stops it;
rematch restarts it.

- Automated: `test_music_follows_the_round` passes with `loop.ogg` loaded.
- Seam, measured on the decoded OGG: the jump across the loop point (0.013) is below the 99th
  percentile of ordinary sample steps in the loop (0.014). A three-repeat check file is at
  `design/generations/audio/checks/MUS-RAW_s22_loop_x3.ogg`.
- 2026-10-07, Zhaohui's playtest answer (in chat, translated from Chinese): asked whether no click at the loop seam, music quieter and muffled on pause, music stops at K.O., Zhaohui answered "没问题，都正常着" ("no problems, everything works normally"). This is one overall confirmation, not a per-item log.

## Muted play

Full round with M and N both on; can whiff, hit, block and K.O. be told apart by sight alone?

- Automated: a seeded fight ends identically with both buses muted. Visually, hit and block have
  different sparks and only a hit moves the health bar (`03_block` against `04_hit`).
- 2026-10-07, Zhaohui's playtest answer (in chat, translated from Chinese): asked whether with M and N muted, the play is still understandable from the picture, Zhaohui answered "没问题，都正常着" ("no problems, everything works normally"). This is one overall confirmation, not a per-item log.

## Inspect-and-revise cycles (so far)

1. In-engine state capture showed the KO poses clipped by the canvas → KO legs folded (commit `46ac888`).
2. The block test showed point-blank kicks whiffing → hitboxes now cover the whole striking limb.
3. Flow capture showed the hurt image arriving after hitstop → hurt image now shown on the hit frame.
4. Five rounds of the Akaken reference (prompt truncation, colour binding, colour-block img2img) — see
   FRICTIONAL and ASSET-LOG.
5. Flow capture showed Aotake vanishing at K.O. → new "image shows a body" test failed on exactly
   that image → re-exported with a chroma key (commit `9099c9e`).
6. Music seam score rose after the crossfade → checked on the decoded file, judged not a click
   (pending a listen).

## Honest limitations

- Every selection after round 3 of the images, and every audio pick, was Claude's, made from
  measurements and a visual check, never by ear. Zhaohui delegated these and has not re-judged
  them one by one.
- The colour-block starting images were drawn by Claude's script and then repainted by the model
  at strength 0.75. ASSET-LOG records the starting image and strength for each row.
- The character mismatches listed above.
- The CPU was tuned by tests, not by playtesting.
- Storyboard panel 6 (losing K.O.) has no capture.
- Licences are non-commercial or limited: MusicGen weights are CC-BY-NC 4.0, and Stable Audio Open
  uses the Stability AI Community License.

---

# Assignment 3 — three 3D props

> Draft by Claude Code, 2026-10-16. Rows marked **TO DO (human)** need Zhaohui's own check or own
> words; Claude has only recorded what Zhaohui said in chat.

- **Versions:** Blender 5.2.2 LTS · mcp-for-blender 2.1.9 (add-on 1.8, protocol 13) · Godot 4.7.2
  stable (GL Compatibility) · Windows 11 Home. The chapter used Blender 5.1.2.
- **Route:** the MCP route for all three assets. No script-route fallback was needed.
- **Brief:** CHANGE-BRIEF.md, Assignment 3, committed before building (`30513a4` on `main`).
- **Code Claude ran:** `tools/blender/build_lantern.py`, `build_makiwara.py`, `build_taiko.py`
  (every `execute_blender_code` body, verbatim), plus `export_glb.py` and `check_blend.py`.
- **Commands on Windows:** Git Bash, with Godot run from
  `Downloads\Godot_v4.7.2-stable_win64.exe\Godot_v4.7.2-stable_win64_console.exe` (shortened to
  `godot` below). Git Bash provides `timeout`, so Homebrew coreutils is not needed.

## Automated checks

```bash
timeout 120 godot --headless --path godot --script res://tests/check_props3d.gd --fixed-fps 60
```

Result: **49 checks, 0 failed**, exit 0 (46 before the footprint-centre check was added). For each prop the script prints the AABB size, the scale
and rotation of every node, the tallest axis, the triangle count, the albedo hex of each surface,
and the gap between the prop's lowest point and the `Floor` node's top face.

**Proving the check can fail.** As a test, the taiko was raised by 0.05 m in `prop_room.tscn` and
the check was run again. Result: **46 checks, 1 failed** (`sits on the floor (gap 0.0500)`), exit 1.
The scene was then restored. The older "min y" assertion **still passed** with the taiko floating,
because it measures the lowest point relative to the prop's own node, not to the floor. That is
the same mistake as Module 3's floor check. The floor-gap assertion was added for that reason.

Blender-side check, headless, for each `.blend`:

```bash
/d/blender/blender.exe -b blender/prop_taiko.blend --factory-startup --python-exit-code 1 --python tools/blender/check_blend.py
```

**Reproducibility.** `tools/blender/reproduce.py` re-runs the three build files headless into a
scratch folder. The vertex fingerprints match the committed `.blend` files: lantern `7c537d4f8f3c`,
makiwara `a1091179bdeb`, taiko `dc819786cf3b`. The re-run also reproduces the taiko origin error
before call 2 fixes it.

The 2D game's suite is unchanged: `test_runner.gd` gives 94 checks, 0 failed.

## Results against the brief

| Check | PROP-LANTERN | PROP-MAKIWARA | PROP-TAIKO |
|---|---|---|---|
| Brief W × D × H (m) | 0.60 × 0.60 × 1.40 | 0.30 × 0.30 × 1.50 | 0.70 × 0.55 × 0.95 |
| Blender dimensions X × Y × Z (from `get_scene_info` and `check_blend.py`) | 0.60 × 0.60 × 1.40 | 0.30 × 0.30 × 1.50 | 0.70 × 0.55 × 0.95 |
| Godot AABB x × y × z (headless) | 0.600 × 1.400 × 0.600 | 0.300 × 1.500 × 0.300 | 0.700 × 0.950 × 0.550 |
| Upright: tallest axis is Godot Y | yes | yes | yes |
| Node scale after export | 1, 1, 1 | 1, 1, 1 | 1, 1, 1 |
| Node rotation after export | 0, 0, 0 | 0, 0, 0 | 0, 0, 0 (the drum's 90° turn was applied in Blender) |
| Origin: gap to the floor top in Godot | 0.0000 | 0.0000 | 0.0000 |
| Triangles (budget; course limit 500) | 100 (150) | 92 (120) | 168 (200) |
| Basic shapes (limit 6) | 6 | 5 | 6 |
| Albedo hex in Godot vs brief | 6e6680 f5c542 4e475c, exact | 8a5a3b d8b676 f2e6d0 6e6680, exact | d9482b f2e6d0 1e1b22, exact |
| Imports and appears | yes, `--import` printed no errors; visible in `evidence/props3d/prop_room_front.png` | yes | yes |

- **Scene Statistics (read by Claude, not by Zhaohui in the status bar):** each saved file,
  opened headless, returned `scene.statistics()`, the same string the status bar shows:
  - lantern `Verts:62 | Faces:46 | Tris:100`
  - makiwara `Verts:56 | Faces:38 | Tris:92`
  - taiko `Verts:96 | Faces:60 | Tris:168`

  These match the `loop_triangles` counts above.
- **Sidebar dimensions:** the "Blender dimensions" row is `object.dimensions`, the value the N-panel
  Item tab displays. Zhaohui's screenshot shows the Object Properties Transform panel (location 0,
  rotation 0°, scale 1.000), not the Item tab's Dimensions field. **Optional (human):** a screenshot
  of N → Item → Dimensions for one prop.

## HUMAN CHECK: look

- 2026-10-16, Zhaohui (in chat, after opening `prop_room.tscn` in the Godot editor and walking
  around): "我看了一一下，没问题" ("I had a look, no problems"). This is one overall
  confirmation, not a per-asset log.
- 2026-10-16, Zhaohui's answers to Claude's follow-up questions (translated from Chinese):
  - **Do the three props read as what they are?** "我觉得都挺像" ("I think they all look quite
    like what they're meant to be").
  - **Anything odd from behind or below (missing faces, wrong colours)?** "没有发现奇怪的地方"
    ("I didn't find anything strange").

  Zhaohui's own screenshots from below and from behind are in `evidence/blender/`. These are overall
  answers covering all three props. Zhaohui did not single out the one that reads best or worst.
- Claude's own observations from two still renders (not a substitute for the walk-around): no
  missing faces seen from front or back. The taiko stand is only 0.12 m deep, so from the side the
  drum looks as if it could tip; Zhaohui kept it as built.

## What Claude got wrong

1. **Taiko origin.** After joining the parts, the origin sat at Z 0.03, the centre of the base bar
   (failure case 3). Claude's own script output caught it; `get_scene_info` alone reported
   "on ground" because it measures the world box. Fixed by moving the mesh, not the object.
2. **A wrong option offered to Zhaohui.** For the makiwara, "squash the bands into a 0.20 × 0.18
   ellipse" was offered and chosen, but it could not enclose the pad. Claude checked before
   building, said so, and offered a chamfered ring instead.
3. **The first floor check proved less than it claimed** (see "Proving the check can fail").
4. **Overexposed first render.** The sun at 1.0 plus ambient 0.6 turned the cream drumhead pure
   white.
5. **The course prompt was not followed exactly.** The course asks for get_scene_info, then a
   proposed plan, then approval, then **one `execute_blender_code` call per object**. Claude built
   each asset in one call (all parts, join, apply) and asked for approval after each asset, not
   before. Each step was still checked with `get_scene_info` and `look`.

## Inspect-and-revise cycles (A3)

1. `look` on the makiwara showed the round bands standing out about 4 cm like collars. Zhaohui
   chose chamfered 0.19 × 0.17 rings, which now stand out 1.5 cm at the same 92 triangles.
2. A script check on the taiko showed the mesh running from Z −0.03 → origin moved to the
   underside, then re-checked headless.
3. The first Godot render showed the drumhead clipped to white → light lowered to 0.7 and ambient
   to 0.35, then re-rendered.
4. The prop-raising test showed the "min y" check could not fail → floor-gap check added; it fails
   when the prop is raised and passes on the real scene.
5. Zhaohui moved the whole taiko to X = 2 m (not saved). An export from a scratch copy carries a
   2 m node offset that no check measured → "origin at the footprint centre" check added.
6. Zhaohui's Edit Mode edit collapsed and twisted the front drumhead; red showed through it. Only
   an oblique `look` showed it; size (0.53 m) and topology still passed → Claude repaired the head
   (the first repair was partial and a vertex comparison caught that) → re-exported, 49/49.

## Honest limitations (A3)

- **Hand edit:** Zhaohui edited the taiko in Edit Mode with the mouse. The edit moved the body
  about 1.2 cm and collapsed the front drumhead to 0 m. Zhaohui asked Claude to repair it, so the
  repair is Claude's (FRICTIONAL.md). Zhaohui's own account, in BLENDER-NOTES.md, is that they
  changed the drumhead's colour using L and G, and learned that you can work with shortcuts. The
  saved file shows no colour change, only the geometry moved; both are recorded side by side there.
- **BLENDER-NOTES.md:** the six interface parts are Zhaohui's answers, translated by Claude with the
  Chinese originals kept, plus Zhaohui's screenshot.
- The checks show size, orientation, scale, floor contact, triangle count and colour values. They do
  not show that the props look right in the game's style or lighting, or that no face is flipped;
  those are the human look check.
- The prop room is not connected to the 2D game.
- The makiwara rope bands are not round cylinders as the brief first said (see CHANGE-BRIEF, build
  result).

---

# Assignment 5 — shaders and materials

Source revision for the results below: `74301ad` (plus the capture script in this commit). Godot
4.7.2-stable (official), **GL Compatibility** (`opengl3`, OpenGL 3.3, Intel UHD Graphics),
Windows 11. All tests through `scripts/run-test.sh` unless noted. Rows marked **HUMAN CHECK**
are Zhaohui's: Claude measured the numbers but has not judged how anything looks.

## Baseline (earlier suites, before and after A5)

| Suite | Before A5 (`a078642`) | After (fresh cache, `3560081`) |
|---|---|---|
| `test_runner.gd` at 60 | 94 checks, 0 failed | 94 checks, 0 failed |
| `check_props3d.gd` at 60 | 49 checks, 0 failed | 49 checks, 0 failed |

## Shaders parse

| Shader | Uniform list (`get_shader_uniform_list()`) | SHADER ERROR |
|---|---|---|
| `hurt_flash.gdshader` | `hurt_amount` float 0–1, `flash_color` Color | none |
| `granite.gdshader` | 3 samplers, groups `surface` / `detail`, 4 uniforms | none |
| `hint_experiment.gdshader` | 2 samplers, `read_as_color` bool | none |

## Mutations (each by Zhaohui in the shader, each restored)

| Mutation | Test | Result | Log |
|---|---|---|---|
| Delete the `;` on `hurt_flash.gdshader:3` | `test_hurt_flash.gd` 60 | exit 1, 7 of 69 failed, SHADER ERROR | `logs/mutation1_semicolon_60fps.log` |
| Rename `hurt_amount` in the shader only | `test_hurt_flash.gd` 60 | exit 1, 6 of 69 failed, no SHADER ERROR; all 23 behaviour checks still passed | `logs/mutation2_rename_60fps.log` |
| Delete `source_color` from `albedo_texture` | `test_materials.gd` 60 | exit 1, 1 of 96 failed, no SHADER ERROR | `logs/mutation3_source_color_60fps.log` |

## Driver (headless, real loop and real input)

`test_hurt_flash.gd`: **69 checks, 0 failed at 30, 60 and 144 fps** (`logs/test_hurt_flash_*fps.log`).
A punch by the J key: 1.0 on the hit tick, held 4 ticks, then stun / 18, 0.0 on tick 22 =
0.367 s of game time, and the same real time in frames at every rate. Pause freezes the value.
Retrigger and the mid-fade K.O. only by labelled SETUP (brief Revisions 6–7). P1 stays at 0.0
while P2 flashes. The first run failed 4 of 58 (rules 3 and 4); see Inspect-and-revise.

## Controlled values (in-engine capture, `godot/tests/capture_a5.gd`, windowed)

Captures from the rendered viewport at 1280 × 720 (`evidence/a5/hurt_flash_*.png`), driver
paused, P1 idle. The texel positions map to capture (449, 514) and (495, 448), one pixel above the
brief's estimate (449, 515) / (495, 449).

| Pixel | 0.0 predicted / measured | 0.5 predicted / measured | 1.0 predicted / measured |
|---|---|---|---|
| P-gi | (222, 89, 0) / (221, 89, 0) | (239, 45, 0) ± 1 / (238, 44, 0) | (255, 0, 0) / (254, 0, 0) |
| P-fist | (240, 230, 172) / (239, 230, 171) | (248, 115, 86) ± 1 / (247, 115, 86) | (255, 0, 0) / (254, 0, 0) |

Every value is within one step. The consistent −1 is the texels' alpha of 254: the brief predicted
that it would move each channel by "under one step"; measured, it moves the top of the range by one.

**Q7, does `hint_range` clamp a value set from code?** `hurt_amount = 2.0` reads back as 2.0.
With the red flash both 1.0 and 2.0 saturate to (254, 0, 0), so a second check used a grey
`flash_color` (128, 128, 128), in memory only: 1.0 → (128, 128, 128); **2.0 → (34, 167, 254)**,
which is `mix()` extrapolated (222 + 2 × (128 − 222) = 34; 89 + 2 × 39 = 167). **Not clamped**;
Zhaohui's prediction ("No") holds.

**HUMAN CHECK (Zhaohui), 2026-10-29:** looking at `hurt_flash_0_0/0_5/1_0.png`: "能看出来" (the
change from normal to red can be seen). *The comparison of one in-engine capture with an OS
screenshot was not done.*

## Time scale in a normal windowed run (no --fixed-fps)

`Engine.time_scale` 1.0: 59.2 physics ticks per real second; 0.5: 60.0. The fight is not
slowed, so the flash lasts 0.367 s either way, as brief Revision 7 says.

## Hint experiment (`evidence/a5/hint_experiment.png`)

| Band | Stored | Quad A predicted / measured | Quad B predicted / measured |
|---|---|---|---|
| 1 | 64 | 64 / **64** | 137 / **64** |
| 2 | 128 | 128 / **128** | 188 / **128** |
| 3 | 192 | 192 / **192** | 224 / **192** |

**Quad B does not match the prediction.** Finding and first explanation: giving quad B its own
texture object (in memory) changed nothing (`evidence/a5/hint_experiment_b_own_texture.png`), so
it is not the shared texture (MATERIALS.md finding 5). The Godot 4.7.2 Compatibility source shows
why: `drivers/gles3/shaders/scene.glsl:2398` decodes every `ALBEDO` with `srgb_to_linear()`
whatever the sampler's hint, and `:2798` encodes once on output, so both quads get decode then
encode. The prediction followed the Forward+/Mobile pipeline. *Zhaohui's explanation goes in
LANGUAGE-NOTES.md.*

**HUMAN CHECK (Zhaohui), 2026-10-29:** the two quads look the same: "一样".

## Interface sweep (floor material, in memory; `evidence/a5/granite_sweep_*.png`)

Floor pixel sampled at capture (589, 575), plinth top at (826, 401).

| Uniform | min | material value | max |
|---|---|---|---|
| `uv_scale` | 0.25: (135, 112, 89) | 6.0: (120, 97, 76) | 8.0: (103, 84, 69) |
| `roughness_scale` | 0.0: (115, 91, 68) | 1.0: (120, 97, 76) | (= material) |
| `normal_strength` | 0.0: (112, 90, 70) | 1.0: (120, 97, 76) | 2.0: (115, 93, 72) |
| `tint` | black: (26, 26, 26) | white: (120, 97, 76) | (= material) |

Each uniform changes the floor pixel; the plinth pixel stayed (10, 4, 6) throughout. Observed by
Claude in `granite_materials.png`: **the stretched floor reads as horizontal planks rather than
granite** (the 2.25 : 1 stretch, MATERIALS.md finding 1). The tint-black row shows (26, 26, 26),
not black: the ambient or reflected light still adds a little.

**HUMAN CHECK (Zhaohui), 2026-10-29:** "tint全黑不好看" — the tint at black breaks the look.

## One shader, two materials

- One value in one material (Claude, in memory): floor `tint` → (0.4, 0.8, 0.4) changed the floor
  pixel to (50, 78, 34); the plinth stayed (10, 4, 6). Only the floor changed.
- **HUMAN CHECK (Zhaohui), 2026-10-29:** edited one line of `granite.gdshader` (Claude suggested
  removing `* tint.rgb` on line 19) and restored it: both objects "变了" (changed). Afterwards
  `git status` was clean: the shader matches `25e6dd8` and `project.godot` is unchanged.
- **HUMAN CHECK (Zhaohui), 2026-10-29:** side by side in `granite_materials.png`, the granite
  "像木板" (looks like wooden planks), agreeing with MATERIALS.md finding 1. Not fixed in A5.

## Material wiring and texture data

- `test_materials.gd`: 96 / 0, also from an empty cache (`3560081`); `source_color` mutation exit 1.
- Curl ratio: `nor_gl` 0.3545 (OpenGL) / 1.6455 (DirectX); `nor_dx` the reverse; the albedo
  and random noise as controls 1.00. Threshold 1.0, set from the pair.
- Import settings: the fresh reimport rewrote no `.import` file; no editor session has yet.

## In play

**HUMAN CHECK (Zhaohui), 2026-10-29:** played with both buses muted: "可以看出" — who was hit can
be seen, so predicted failure case 8 (a weak flash on Akaken) was not seen in play. Boundaries: no
change to fight behaviour was reported; the headless baseline stays 94 / 0.

## Inspect-and-revise cycles (A5)

1. **Observation:** the first `test_hurt_flash.gd` runs failed 4 of 58 at 30, 60 and 144 fps.
   **Inspection:** the frame data makes a second hit during hurt impossible (T+23 vs T+22), and
   `time_scale` does not change the tick count. **Revision:** brief Revisions 6–7 (rules 3, 4, 5),
   decided by Zhaohui; the test's expectations changed with reasons, no assertion removed; 69 / 0.
2. **Observation:** the first capture run sampled every 3D pixel as background. **Inspection:**
   looking at the PNGs showed the images were right and the coordinates wrong (640 × 360 viewport
   vs 1280 × 720 capture). **Revision:** scaled coordinates; rerun.
3. **Observation:** quad B measured 64 / 128 / 192, not the predicted 137 / 188 / 224.
   **Inspection:** a separate texture object for B changed nothing; the GLES3 scene shader decodes
   every `ALBEDO` and encodes on output. **Revision:** the explanation in LANGUAGE-NOTES Q4; the
   prediction stays as written in the brief, beside the measurement here.
4. **Observation:** the granite floor reads as wooden planks (Zhaohui, and the capture).
   **Inspection:** MATERIALS.md findings 1–3 (BoxMesh UV stretch). **Revision:** brief Revision 8
   corrected the plan's text; the look itself is not fixed in A5 (a known limitation).

## What the agent got wrong (A5)

- The `claude -p` CLI was too old: exit 0 and `subtype: success`, but `is_error: true` and no
  CLAUDE.md. Caught by reading the result event.
- Agent sessions ran commands outside `--allowedTools` without a recorded denial (`wc -l`,
  `git show`), and tried to execute a probe during a plan-only step (denied).
- The first materials script saved two uniforms as `null` (a headless save does not know shader
  defaults). Caught by reading the `.tres`.
- The audit stated an unmeasured "costs nothing at draw time" and missed the RG-only normal map.
- **Claude's own wrong claim** that `hint_normal` rebuilds Z (MATERIALS.md finding 11), repeated
  into a draft answer; caught by reading the engine source while checking LANGUAGE-NOTES.
- Claude's capture script sampled 3D pixels at the wrong scale (cycle 2 above).

## Honest limitations (A5)

- The headless suites prove parsing, uniform names and types, driving and wiring, not looks; the
  look is the human checks above, which Zhaohui reported in a few words each.
- The OS-screenshot comparison was not done.
- The retrigger and the mid-fade K.O. are reachable only by labelled test setup.
- The granite looks like planks on this BoxMesh.
