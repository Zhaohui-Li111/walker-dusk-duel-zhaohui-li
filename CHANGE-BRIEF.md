# CHANGE-BRIEF — walker-dusk-duel asset slice

> Version 1 · 2026-10-05 · written before any generation. Predictions are recorded here and checked
> in TEST-REPORT.md; this file is appended to, not rewritten.

## Asset list

| ID | Asset | Category | Panels |
|---|---|---|---|
| CHAR-AK-REF | Akaken reference image (idle pose, solid green background), source of all poses | art (reference) | — |
| CHAR-AK-IDLE / WALK / CROUCH / RISE / FALL / PUNCH / KICK / BLOCK / HURT / KO / WIN | Akaken, 11 static state images | art | 01–08 |
| CHAR-AO-REF | Aotake reference image | art (reference) | — |
| CHAR-AO-IDLE / KICK / BLOCK / HURT / KO | Aotake, 5 static state images | art | 01, 03–05, 07, 08 |
| ENV-BG | Temple courtyard background at dusk (sky band, dark wall band, lanterns, floor) | art (environment) | all |
| SFX-WHIFF | Strike that hits nothing: short air swish | sound | 03, 05 |
| SFX-HIT | Strike that connects with a hurtbox: dry thud | sound | 04, 05, 08 |
| SFX-BLOCK | Strike that connects with a blocking fighter: wood/cloth knock | sound | 03 |
| SFX-KO | A fighter's health reaches 0: heavy low hit + gong | sound | 06, 08 |
| MUS-LOOP | Taiko + wood-flute loop, cut at a bar boundary | music | 01–05, 07 |

Hit spark, block flash, health bars and text are Claude-drawn/code UI, not counted as generated assets.

## Event-to-sound map

All sounds are played by an `AudioDirector` node that **only listens** to signals. Game state is
decided by the fight code; a missing or muted sound changes nothing.

| Sound | Exact triggering event | Double-trigger prevention |
|---|---|---|
| SFX-WHIFF | `attack_finished(attacker, connected=false)`, emitted once when an attack's active window closes with no contact | emitted from the attack state's exit, once per attack instance |
| SFX-HIT | `hit_landed(attacker, defender)`, emitted when a hitbox first overlaps a non-blocking hurtbox | each attack instance keeps a `hit_targets` set; a defender already in it is ignored, so one swing hits once even if the boxes overlap for several frames |
| SFX-BLOCK | `hit_blocked(attacker, defender)`, same overlap but defender is in `BLOCK` | same `hit_targets` set; a blocked swing cannot also hit |
| SFX-KO | `fighter_ko(fighter)`, emitted when health crosses from >0 to ≤0 | guarded by `is_ko`, so it fires once per fighter per round; the final hit plays SFX-HIT and then SFX-KO (panel 8), each exactly once |

Holding the attack button does **not** repeat attacks: a new attack starts only on `is_action_just_pressed`
while the fighter is not already attacking.

## Music behavior

| Situation | Behavior |
|---|---|
| Fight running | MUS-LOOP plays on the `Music` bus, looping with no gap |
| Pause (Esc / P) | Music bus ducks to −12 dB with a low-pass filter; SFX bus paused; resume restores both |
| Failure (player KO) | Music stops immediately on `fighter_ko` |
| Success (opponent KO) | Music stops immediately; stays stopped on the win screen |
| Rematch | Music restarts from position 0 |
| End of slice (Esc on win/KO screen) | Quit; nothing plays |
| Mute | `M` toggles the Music bus, `N` toggles the SFX bus (separately) |

## Predicted failure cases and how each will be checked

1. **Generated poses drift from the reference** (arms longer, fists smaller, headband on the wrong
   side, outfit color changes). *Check:* overlay each pose on its OpenPose skeleton at 50% opacity,
   compare against consistency rules 1–8 in CHARACTER-SHEET.md; reject on any rule failure.
2. **One swing plays SFX-HIT several times** because hitbox and hurtbox overlap across frames.
   *Check:* automated test that scripts 20 punches, 10 kicks and a held punch button against a dummy
   and asserts the counts of each signal and each sound call match the number of attacks.
3. **Music loop clicks at the seam.** *Check:* cut at a zero crossing on a bar boundary, listen to at
   least 3 repetitions in Godot, and inspect the waveform at the seam.
4. **Fighters disappear against the background** (red gi on dusk stone). *Check:* in-engine
   screenshot converted to grayscale, and the slice played at 1× from 2 m away; compare with the
   palette contrast table.
5. **The slice is unreadable muted.** *Check:* play a full round with both buses muted; confirm
   whiff / hit / block / KO can each be told apart by sight alone.
6. **Art does not line up with collision** (generated punch reaches further than the hitbox).
   *Check:* debug-draw collision shapes in Godot over every state image and screenshot them.

## Possible revisions already noted

- Extend the hurtbox along an attacking limb so whiffs can be punished (CHARACTER-SHEET collision note).
- A separate SFX-HURT for the player being hit, if playtesting shows SFX-HIT is ambiguous about who was hit.

---

## Revision 2 · 2026-10-05 · during slice step 2 (no generation yet)

- **Signals renamed and unified.** The three planned signals (`attack_finished`, `hit_landed`,
  `hit_blocked`) became one: `attack_resolved(fighter, kind, result, point)`, emitted **exactly once
  per attack** with `result` = `hit` / `blocked` / `whiff` / `interrupted`. SFX-HIT, SFX-BLOCK and
  SFX-WHIFF map to the first three; `interrupted` (attacker hit during startup) plays nothing.
  Whiff now fires when the active window ends, not after recovery, so the swish lines up with the
  swing. `knocked_out(fighter)` is unchanged and drives SFX-KO and the music stop.
- **Hitboxes cover the striking limb** (elbow→fist, knee→foot) instead of only the tip. Found by the
  automated block test: at touching distance a tip-only kick box passed beyond the opponent's hurtbox
  and whiffed. Regression test: `test_point_blank_attacks_connect`.
- **Hurt image appears on the hit frame.** The 4-frame hitstop delayed the hurt image; found in the
  flow capture (`evidence/flow/05_player_hurt.png`), fixed, and covered by `test_punch_hits_once`.
- **Design consequence noted:** each blocked hit pushes the defender back ~6 px, so repeated attacks
  on a blocker need the attacker to step in. Intentional (no infinite pressure), but to playtest.

## Revision 3 · 2026-10-05 · during slice step 3 (no audio generated yet)

- Music starts on the **title screen** (storyboard P1) and keeps playing into round 1; it restarts
  from 0 only when a round starts after it was stopped (the rematch, P7). Pause, K.O. and result
  behave as in the table above.
- On the final hit the K.O. is now emitted **after** the hit result, so the order is SFX-HIT then
  SFX-KO (P8). Before this change the K.O. signal fired first.
- Sound requests are counted even when the audio file does not exist yet, so the event-to-sound map
  is tested before any audio is generated. Real playback, loop seams and loudness still need
  listening once the files exist.

---

# Assignment 3 — three 3D props (Blender MCP → Godot)

> **Version 1 · DRAFT · 2026-10-16.** Claude Code drafted this from Zhaohui's choice of assets
> (stone lantern, makiwara, taiko drum). **Zhaohui: do the "Learn the window" session in Blender
> first, then edit the numbers below and commit before anything is built.** After that commit this
> section is only appended to, like the A2 brief above.

## Scale and conventions

- Dusk Duel is 2D, so these props live in a separate small 3D scene (`godot/props3d/prop_room.tscn`:
  floor, one light, one camera). Later assignments reuse it. It is not wired into the 2D game yet.
- **Scale reference:** Akaken stands 112 px on screen and Aotake 124 px (CHARACTER-SHEET.md). Taking
  Akaken as **1.70 m** gives about 1.52 cm per pixel, so Aotake is about **1.88 m**. A 1.70 m reference box
  goes into the 3D scene for the human look check.
- 1 Blender unit = 1 m = 1 Godot unit. Blender is Z-up; the glTF exporter's **+Y Up** converts to
  Godot's Y-up.
- Each asset is built around the world origin with its base on Z = 0, in its own `.blend` file.
  **Origin = centre of the underside** for all three, so placing a prop at floor height 0 in Godot
  makes it stand on the floor.
- Rotation and scale applied in Blender (rotation 0,0,0; scale 1,1,1) before export.
- Flat Principled BSDF base colours, mostly from the A2 palette so the props match the 2D art.
  Two are new (roof `#4E475C`, wood `#8A5A3B`) because A2 has no darker stone or wood tone.
- **Tolerance for "matches the brief":** ±0.02 m on each dimension.

## The three assets

### 1. PROP-LANTERN — stone lantern (tōrō)

- **In the game:** the courtyard in ENV-BG already shows lanterns (glowing paper ones in the
  generated image). This is a stone version of the same idea, set at the edges of the arena.
- **Size (W × D × H):** **0.60 × 0.60 × 1.40 m.** That's about shoulder height on Akaken (1.70 m),
  so it frames a fighter without hiding one.
- **Origin:** centre of the base, at floor level.
- **Look (6 shapes):** an octagonal base (cylinder, 8 segments), an octagonal shaft (cylinder, 8), a
  firebox (cube), a lit panel set into the firebox front (thin cube), a pyramid roof (cone, 6
  segments) and a small cone finial on top. It reads as a lantern because of the wide roof over a
  box sitting on a thin post.
- **Colours:** stone `#6E6680` (the first proposed mid-tone stone in A2; rejected
  for the 2D wall behind the fighters, but no contrast rule applies to a prop room), lit panel `#F5C542` (the belt accent,
  flat colour, not emissive), roof a little darker `#4E475C` (new).
- **Triangle budget: 150.** Estimate: 28 + 28 + 12 + 12 + 10 + 10 = 100. A default 32-segment
  cylinder alone would cost 124, so the segment counts must be set low.

### 2. PROP-MAKIWARA — wooden striking post

- **In the game:** a training post for Akaken, whose fighting style is punching. It stands in the
  prop room now and could be a target in a later tutorial or warm-up.
- **Size (W × D × H):** **0.30 × 0.30 × 1.50 m.** The straw pad's centre is at about **1.20 m**,
  roughly chest/fist height on a 1.70 m fighter.
- **Origin:** centre of the base, at floor level.
- **Look (5 shapes):** a square stone footing (cube 0.30 × 0.30 × 0.10), a tapered-looking post
  (cube 0.12 × 0.08 × 1.40, on top of the footing), a straw pad on the front face (cube 0.16 × 0.06
  × 0.30) and two rope bands around the pad (cylinders, 8 segments). It reads as a training post
  because of the pad and its rope bands at fist height.
- **Colours:** wood `#8A5A3B` (new), straw `#D8B676` (Aotake's hat colour), rope `#F2E6D0` (the hand-wrap
  cream), footing `#6E6680`.
- **Triangle budget: 120.** Estimate: 12 + 12 + 12 + 28 + 28 = 92.

### 3. PROP-TAIKO — taiko drum on a stand

- **In the game:** the music loop (MUS-LOOP) is taiko and wood flute, so the drum is the visible
  source of the soundtrack. It would sit at the back of the courtyard.
- **Size (W × D × H):** **0.70 × 0.55 × 0.95 m.** The drum is about **0.60 m across**, with heads
  facing ±Y (front and back) and its centre at about 0.62 m. The top of the drum is at about hip
  height on Akaken.
- **Origin:** centre of the stand's footprint, at floor level.
- **Look (6 shapes):** the drum body (cylinder, 12 segments, **rotated 90° about X** so the heads
  face front and back), two drumheads (thin cylinders, 12 segments), two angled stand legs (cubes)
  and a base bar (cube). It reads as a taiko because of the round red barrel with pale heads on a
  low cradle.
- **Colours:** lacquer body `#D9482B` (the gi red), heads `#F2E6D0`, stand `#1E1B22`.
- **Triangle budget: 200.** Estimate: 44 + 44 + 44 + 12 + 12 + 12 = 168. This is the one asset that
  needs a real rotation, so it tests "apply transforms".

## Predicted failure cases and how each will be checked

1. **The taiko arrives rotated or scaled in Godot,** because the 90° turn or a scale was left
   unapplied. *Check:* Blender's N panel shows rotation 0,0,0 and scale 1,1,1 on every object before
   export. The headless Godot script prints each node's scale and rotation and the AABB's tallest
   axis, which should be Y for all three.
2. **Wrong size, possibly by a factor of 10,** from a unit-scale or object-scale mistake. *Check:*
   the N-panel dimensions against the table above, then the Godot AABB size against both, within
   ±0.02 m.
3. **Origin at the centre, so the prop sinks halfway into the floor** (Blender's default primitives
   are centred on their origin). *Check:* the Godot AABB's minimum Y should be 0.00 ± 0.01, and each
   prop placed at y = 0 should be seen standing on the floor, not floating or sunk.
4. **Claude builds more detail than asked:** more than 6 shapes, default 32-segment cylinders or a
   UV sphere (960 triangles). *Check:* Blender Scene Statistics (status bar), and the headless script
   counts triangles per asset against the budget.
5. **The MCP will not connect on Windows.** The course's commands are written for macOS, and the
   add-on opens a socket that the firewall may prompt about. *Check:* `get_addon_status` and
   `get_scene_info` from Claude. Every step and its exact error goes into FRICTIONAL.md, with a
   2-hour time box before falling back to the script route.
6. **Colours shift or disappear on export** (sRGB vs linear, or a material lost). *Check:* the
   headless script prints each surface's albedo as hex to compare with the brief, and the human look
   check under the scene's single light.
7. **Missing or flipped faces** that only show from behind or below. *Check:* walk the camera around
   and under each prop in Godot (human check). Backface culling on the import would hide them from
   one side.

## Build result (appended 2026-10-16)

Zhaohui confirmed the numbers above as final, and this section was committed unchanged (`30513a4`)
before anything was built. All three props match it: deviation 0.00 m on every dimension, origin
at the underside centre, rotation and scale applied, 100 / 92 / 168 triangles, albedo hex exact
after the glTF round trip. `godot/tests/check_props3d.gd` runs 43 checks, 0 failed. Zhaohui did
the walk-around check in the Godot editor and found no problems.

**Differences from the spec above:**
- PROP-MAKIWARA's rope bands are chamfered 8-vertex rings (0.19 × 0.17 m), not round 8-segment
  cylinders, so they sit close to the pad. Zhaohui chose this; the triangle count is unchanged.
- The prop room adds a WorldEnvironment (ambient light only) next to the floor, the light and the
  camera.

Failure cases seen: **3** (taiko origin at Z 0.03 after the join; caught and fixed in Blender).
Not seen: 1, 2, 4, 5, 6, 7. See FRICTIONAL.md, Assignment 3.

---

# Assignment 5 — shaders and materials

> **Version 1 · 2026-10-26.** Claude Code drafted the state, rules, boundaries, evidence
> split and material plan from Zhaohui's choices (hurt flash, keep Compatibility, stone lantern;
> the lantern was replaced by the floor and a plinth before commit, see the material plan).
> Claude Code also filled the project facts (pixel coordinates and stored values read from the
> sprite and background files, importer enum values read from the Godot 4.7.2 source).
> **Every line marked TO DO (Zhaohui) is Zhaohui's to write: the colour line, the uniform defaults
> Zhaohui wants, every hand-computed prediction and the short answers.** Edit anything else that is
> wrong, then commit this section before writing either shader or sending prompt-1. After that
> commit this section is only appended to, with dated revisions.
>
> **At commit (2026-10-26):** Zhaohui wrote the colour line, chose the red flash colour, and
> computed the six pixel predictions by hand. Zhaohui chose to commit now with these still open:
> the **hint-experiment predictions**, the **short answers**, the **contrast ratio**, and
> confirming the hurt-flash `render_mode` and the granite uniform table. They will be added below
> in a dated revision **before** the hint experiment is measured, before the driver is run, and
> before either shader is written.

## The state

- **What it communicates:** "this fighter was just hit cleanly." The hurt image already changes the
  pose, but in a fast exchange the player can miss which of the two fighters took the hit. A flash
  on the hit fighter's sprite answers it in the first frame, even muted.
- **Where it lives:** `Fighter.state == "hurt"` (`godot/fighter/fighter.gd`, `_set_state("hurt")`
  in the hit handler), with `Fighter.stun` counting down from `HITSTUN = 18` physics ticks.
  `main.gd` freezes both fighters for `HITSTOP_FRAMES = 4` ticks first, and stun does not count
  down during hitstop. A K.O. hit goes to `"ko"`, never `"hurt"`, so it does not flash.
- Two instances exist: `P1` (Akaken) and `P2` (Aotake) in `godot/game/main.tscn`, both from
  `godot/fighter/fighter.tscn`, drawn by its `Sprite2D`.

## Effect specification — hurt flash

**The shader:** `godot/shaders/hurt_flash.gdshader`, `shader_type canvas_item;`, no render_mode
(TO DO (Zhaohui): confirm, or name one). On a ShaderMaterial set as the `Sprite2D`'s `material`.
No sampler uniforms; the sprite texture arrives in `COLOR`.

| Uniform | Type | Hint | Default | Set by |
|---|---|---|---|---|
| `hurt_amount` | `float` | `hint_range(0.0, 1.0)` | `0.0` | the driver, every physics tick, from `stun` (below) |
| `flash_color` | `vec4` | `source_color` | `vec4(1.0, 0.0, 0.0, 1.0)` (pure red, Zhaohui's choice: red reads as "hurt") | the material only; never code |

**The colour line** (inside `fragment()`), written by Zhaohui:

```glsl
COLOR.rgb = mix(COLOR.rgb, flash_color.rgb, hurt_amount);
```

It blends each pixel's own colour toward `flash_color` by `hurt_amount`, and leaves `COLOR.a`
alone, so transparent pixels stay transparent and the 254 alpha of the sprite is kept.

**The driver rule** (presentation only, reads state, never writes it):
`hurt_amount = float(stun) / float(HITSTUN)` while `state == "hurt"`, else `0.0`.

### Observable rules

1. **Begin / end values.** `hurt_amount` is `1.0` on the tick the fighter enters `"hurt"` and
   `0.0` on the tick it leaves (to `"idle"`, or to `"ko"` if hit again).
2. **Duration.** Held at `1.0` for the 4 hitstop ticks, then falls by 1/18 per tick, reaching `0.0`
   at tick 22 after the hit: 22 / 60 = **0.367 s of game time**, tolerance ± one frame period
   (± 0.033 s at 30 fps, ± 0.017 s at 60, ± 0.007 s at 144). The same at 30, 60 and 144 fps,
   because it counts physics ticks (`physics_ticks_per_second = 60`), not rendered frames.
3. **Retrigger: restart.** A second hit during hurt sets `stun = HITSTUN` again (the hit handler
   forces a fresh `"hurt"`), so `hurt_amount` jumps back to `1.0` and the 0.367 s starts over.
4. **Time scale and pause.** Scaled: under `Engine.time_scale = 0.5` the flash lasts 0.733 s of
   real time. The fight's pause (`main.paused`, Esc / P) stops stepping, so the value is frozen at
   whatever it was; it resumes from there. The tree itself is never paused by the game.
5. **State ends early.** If hurt ends before the fade finishes (hit into K.O.), the value is `0.0`
   on that tick, with no tail.
6. **Instances.** Each fighter gets its own ShaderMaterial instance (duplicated in code, or
   `resource_local_to_scene`), so a hit on P2 changes only P2's `hurt_amount`; P1's stays `0.0`.

### Boundaries

Unchanged: collision boxes, movement, input, the state machine and every timing in `fighter.gd`
and `main.gd`, `effects.gd`, `audio_director.gd`, the HUD, the background, the existing tests
(`test_runner.gd` 94 checks, `check_props3d.gd` 49 checks) and their expectations. The driver may
read `state`, `stun` and `HITSTUN`; it never writes them.

### Evidence split

| Rule | Check |
|---|---|
| Shader parses; uniform names and types | headless: `get_shader_uniform_list()`, not a set-then-get round trip |
| Defaults | headless: read from the shader source text |
| 1, 2, 3, 5 | headless: real hits through the real game loop and input, uniform sampled each frame from a high `process_priority` node, at 30, 60, 144 fps |
| 4 | headless: the same test under `Engine.time_scale = 0.5`; pause: value unchanged across paused frames |
| 6 | headless: P1's value stays 0.0 while P2 flashes |
| The colour on screen | human: in-engine captures at the controlled values, sampled pixels vs the table below |
| Reads in play | human: playtest, several hits each way, muted |

### Controlled inputs and predicted values

Background: the courtyard (`ENV-BG`, `godot/art/env/bg.png`, drawn 1:1 at 640 × 360 by
`stage.gd`). The flash changes sprite pixels only; transparent pixels stay background.
Compatibility renderer, `rendering/viewport/hdr_2d` not set, so 2D arithmetic is on the sRGB values
as stored. Fighter sprites are unlit (no `Light2D` in `main.tscn`).

**Capture setup:** Akaken in `idle` at the start of round 1 (`reset(220.0, 1)`), facing right. The
sprite (`godot/art/akaken/idle.png`, 108 × 158, linear filter, lossless import) has its top-left
at viewport (172.1, 156.0) = (220 − 369.55 × 0.1296, 305 − 1150 × 0.1296). The window is
1280 × 720 with `canvas_items` stretch, so a capture is 1280 × 720 and viewport coordinates double.
The two texels below were chosen where every neighbour in a 3 × 3 block is within 2 steps per
channel, so bilinear filtering at the fractional position cannot move them by more than that.

| Pixel | Texel in idle.png | Viewport (≈) | Capture (≈) | Sprite RGBA as stored | Background under it |
|---|---|---|---|---|---|
| **P-gi**: orange gi, lower torso | (52, 101) | (224.6, 257.5) | (449, 515) | (222, 89, 0, 254) | (48, 35, 47) |
| **P-fist**: pale hand wrap, front fist | (75, 68) | (247.6, 224.5) | (495, 449) | (240, 230, 172, 254) | (66, 37, 60) |

Note 1: the generated sprite is orange (222, 89, 0), not the palette's gi red `#D9482B`, so the
prediction starts from the stored texel, not the palette. Note 2: these texels have alpha 254,
not 255, so the background shows through by 1/255. That is under one 8-bit step, but say whether
your colour line keeps `COLOR.a`. Coordinates are confirmed or corrected from the first capture.

| Pixel | `hurt_amount = 0.0` | `0.5` | `1.0` |
|---|---|---|---|
| P-gi | (222, 89, 0) | (238.5, 44.5, 0) → (239, 45, 0) ± 1 | (255, 0, 0) |
| P-fist | (240, 230, 172) | (247.5, 115, 86) → (248, 115, 86) ± 1 | (255, 0, 0) |

Computed by hand by Zhaohui from the colour line, `mix(a, b, t) = a + (b − a)·t` per channel with
`flash_color` = (255, 0, 0). Values ending in .5 may land on either neighbour when the GPU
converts to 8 bits, hence ± 1. The background term is ignored: alpha 254 moves each channel by
under one step.

TO DO (Zhaohui): if the flash colour changes contrast against the background, the ratio.

### Hint experiment predictions

3 × 1 PNG with greys 64, 128, 192, unshaded quads, Linear tonemap, exposure 1.0.
**This project uses the Compatibility renderer, not Forward+/Mobile, so these are predictions to
be measured before they are explained.**

| Band | Stored | Quad A: `source_color` | Quad B: no hint |
|---|---|---|---|
| 1 | 64 | TO DO (Zhaohui) | TO DO |
| 2 | 128 | TO DO | TO DO |
| 3 | 192 | TO DO | TO DO |

Which quad shows the file's values unchanged, and why: TO DO (Zhaohui).

## Material plan — granite floor and stone plinth

**Why not the lantern (decided before this section was committed):** the first draft put the
shader on PROP-LANTERN. A headless probe found that none of the three A3 props has UVs:
`surface_get_arrays()` returns no `ARRAY_TEX_UV` on any surface of the lantern, makiwara or taiko.
Adding UVs would change the source models, which this assignment keeps unchanged, and projecting
UVs inside the shader would make the hand-written shader much harder. Zhaohui chose to texture
the prop room's floor and a new stone plinth instead; both are Godot `BoxMesh`es, which have UVs.

- **Objects:** in `godot/props3d/prop_room.tscn`, the existing `Floor` (BoxMesh 6 × 0.1 × 4 m,
  top at y = 0) and a new `StonePlinth` (BoxMesh 0.8 × 0.3 × 0.8 m), standing on the floor at
  x = 1.0, z = −1.0, clear of the three props and the 1.70 m reference box. No prop is moved.
- **Material wiring:** these meshes are not imported, so there is no importer **Use External**
  step; each `MeshInstance3D` takes its material as `material_override`, pointing at a `.tres`
  file. The A3 props keep their imported materials.
- **Lighting to judge under:** the prop room's `Sun` (DirectionalLight3D, energy 0.7, shadows) and
  ambient 0.35. No SSAO, glow or fog.
- **Shader:** `godot/shaders/granite.gdshader`, `shader_type spatial;`.
- **Materials:** `godot/props3d/materials/granite_floor.tres` and `granite_plinth.tres`, both
  ShaderMaterials of that one shader.
- **UV layout to keep in mind:** `BoxMesh` lays its six faces into a 3 × 2 grid of the 0–1 UV
  square (to be confirmed with a probe), so each face shows about a third by a half of the texture
  at `uv_scale = 1`.

| Texture | Source | What the numbers mean | Sampled as | compress/mode | compress/normal_map | mipmaps/generate |
|---|---|---|---|---|---|---|
| `granite_wall_diff_1k.png` | Poly Haven *Granite Wall* | sRGB-encoded surface colour | colour, `source_color` | 2 VRAM Compressed | 2 Disabled | true |
| `granite_wall_rough_1k.png` | same | roughness 0–1, linear | data, no `source_color` | 2 VRAM Compressed | 2 Disabled | true |
| `granite_wall_nor_gl_1k.png` | same, **OpenGL** convention | tangent-space normal, xyz = rgb·2−1 | data, `hint_normal` | 2 VRAM Compressed | 1 Enable | true |
| `granite_wall_nor_dx_1k.png` | same, DirectX convention | calibration only, no material uses it | — | 0 Lossless | 2 Disabled | false |
| `hint_grey_3x1.png` | written by a committed GDScript | greys 64, 128, 192 | both (hint experiment) | 0 Lossless | 2 Disabled | false |

Enum values are positional in the importer's `PROPERTY_HINT_ENUM` strings, read from Godot
4.7.2-stable `editor/import/resource_importer_texture.cpp`: `compress/mode` =
"Lossless,Lossy,VRAM Compressed,VRAM Uncompressed,Basis Universal" (0–4), `compress/normal_map` =
"Detect,Enable,Disabled" (0–2); `mipmaps/generate` is a bool.

Source: `https://polyhaven.com/a/granite_wall`, authors Dimitrios Savva (all roles, per the Poly
Haven API), licence CC0. Files: 1k PNG from `dl.polyhaven.org`. Date checked: 2026-10-26.
Credits and SHA-256 per file: `godot/props3d/textures/ATTRIBUTION.md`.

Uniforms (at least four, at least two `group_uniforms`). TO DO (Zhaohui): confirm names, ranges
and defaults.

| Group | Uniform | Type | Hint | Default | Expected on screen across the range |
|---|---|---|---|---|---|
| `surface` | `tint` | `vec4` | `source_color` | white | multiplies albedo; the plinth darker |
| `surface` | `uv_scale` | `float` | `hint_range(0.25, 8.0)` | `1.0` | how many times the granite repeats across a face |
| `detail` | `roughness_scale` | `float` | `hint_range(0.0, 1.0)` | `1.0` | 0 = glossy highlight, 1 = as scanned |
| `detail` | `normal_strength` | `float` | `hint_range(0.0, 2.0)` | `1.0` | 0 = flat, 2 = exaggerated relief |

**What differs between the two materials:** `uv_scale` (the 6 × 4 m floor repeats the granite
several times; the 0.8 m plinth about once) and `tint` (the plinth toward `#6E6680`, the A3 stone
colour, so it reads as a separate block on the floor).

### Predicted failure cases

1. **One flash on both fighters** (a shared material). *Check:* the rule 6 assertion; a capture
   with only P2 hit.
2. **Duration changes with frame rate or time scale** (the driver counts frames or uses `TIME`).
   *Check:* the 30/60/144 runs and the `time_scale = 0.5` run.
3. **Retrigger ignored** (the driver latches on the first `state_changed`). *Check:* a second hit
   during hurt must read `1.0` again.
4. **Roughness or normal map sampled with `source_color`.** *Check:* `test_materials.gd` reads the
   hints from the source; the look check at `roughness_scale` minimum and maximum.
5. **Normal map in DirectX convention, or not a real normal map.** *Check:* `normal_map_check.gd`
   curl ratio, calibrated on the gl/dx pair.
6. **The object has no usable UVs.** *Already seen* on the lantern before this section was
   committed (see the material plan); it is why the floor and plinth are used. *Check for the
   new objects:* the BoxMesh UV arrays read headlessly; the floor in the editor at `uv_scale = 1`.
7. **The material is saved embedded in the scene instead of as the `.tres` file,** so the two
   materials stop being shared resources of one shader. *Check:* `test_materials.gd` asserts each
   `material_override.resource_path` and that both name the same shader path, after deleting
   `godot/.godot` and reimporting.
8. **The red flash is weak on Akaken,** whose gi is already orange-red (222, 89, 0): red can add at
   most 33 to R and leaves B at 0, so only G carries most of the change. Aotake should read more
   clearly. *Check:* the P-gi capture at `hurt_amount = 0.5` against P-fist, and the muted
   playtest: can the player tell Akaken was hit? If not, revise `flash_color` with a dated entry.

### Short answers

TO DO (Zhaohui), each in a sentence or two:
- The renderer project.godot names (`renderer/rendering_method="gl_compatibility"`, line 35) and
  what it rules out.
- What colour arrives in `fragment()` before you change it, and the tempting alternative.
- What `texture(TEXTURE, UV)` would give instead of `COLOR`.
- For spatial: `ALBEDO` if never written, and what `COLOR` holds.
- A frame-counting version's duration at 30, 60 and 144 fps.
- Which resource holds the default, which the current value, and what sharing a material does.
- Does `hint_range` clamp a value the driver sets from code? (a prediction)

## Revision 2 · 2026-10-28 · hint-experiment predictions (before any shader or measurement)

Computed by hand by Zhaohui with a calculator, from the handout's encode function
encode(x) = 1.055·x^(1/2.4) − 0.055 (x > 0.0031308), with x = stored / 255. The three
stored greys are all above the linear-segment threshold.

| Band | Stored | Quad A: `source_color` | Quad B: no hint |
|---|---|---|---|
| 1 | 64 | 64 | 137 |
| 2 | 128 | 128 | 188 |
| 3 | 192 | 192 | 224 |

Claude's check of the arithmetic: 64 → 137.2 and 128 → 187.84 agree. 192 → 224.9998, which
rounds to 225, so band 3 on Quad B may measure 224 or 225.

**Which quad shows the file's values unchanged, and why** (Zhaohui's words): Quad A 显示原值，因为
source_color 让 Godot 先将 sRGB 解码为线性值，再编码回 sRGB，两个互逆操作抵消，还原原始数值。
(Quad A shows the stored values, because source_color makes Godot decode sRGB to linear and then
encode back to sRGB; the two inverse operations cancel and give back the original numbers.)

Still open from Version 1: the short answers, the contrast ratio, the hurt-flash `render_mode`
and the granite uniform table. Measured values go in TEST-REPORT.md, not here.

## Revision 3 · 2026-10-28 · two confirmations (before any shader)

- **Hurt-flash `render_mode`: none.** Zhaohui agreed with Claude's suggestion: the fighter
  sprites are unlit and the default blend (alpha mix) is what the flash needs, so the shader
  declares no `render_mode`.
- **Granite uniform table: confirmed as written in Version 1** by Zhaohui, unchanged: `tint`
  (`vec4`, `source_color`, white), `uv_scale` (`float`, `hint_range(0.25, 8.0)`, 1.0) in group
  `surface`; `roughness_scale` (`float`, `hint_range(0.0, 1.0)`, 1.0) and `normal_strength`
  (`float`, `hint_range(0.0, 2.0)`, 1.0) in group `detail`.
- From here on, entries in this file are written in English only (Zhaohui's request). Revision 2
  keeps Zhaohui's sentence as written, with its English translation beside it.

Still open: the short answers and the contrast ratio.

## Revision 4 · 2026-10-28 · short answers (before any shader or measurement)

Q5 and Q7 are Zhaohui's (Q5 computed with a calculator; Q7 in Zhaohui's own words). Q1–Q4 and
Q6 were drafted by Claude Code after Zhaohui asked for help; Zhaohui read them and asked for no
changes.

- **Q1 — renderer** *(Claude-drafted)*. `godot/project.godot:35` names `gl_compatibility`, and
  line 36 uses it for mobile too. That rules out decals, compute shaders, VoxelGI, SDFGI and
  SSIL. It also means the hint-experiment predictions, which the handout derives for
  Forward+/Mobile, must be measured before they are explained.
- **Q2 — the colour arriving in `fragment()`** *(Claude-drafted)*. `COLOR` arrives as the
  sprite's texture sample multiplied by the node's modulate (the vertex colour), alpha included.
  The tempting alternative, `COLOR = flash_color;`, overwrites alpha too, so the whole transparent
  rectangle around the fighter would turn solid red; even `COLOR.rgb = flash_color.rgb;` would
  erase the sprite's shading.
- **Q3 — `texture(TEXTURE, UV)` instead of `COLOR`** *(Claude-drafted)*. It gives the raw texel
  without the modulate. The fighters set no modulate today, so the pixels would match now, but the
  shader would silently ignore any modulate added later (for example a fade-out on K.O.).
- **Q4 — spatial `ALBEDO` and `COLOR`** *(Claude-drafted)*. `ALBEDO` is white, `vec3(1.0)`, if
  never written. `COLOR` in `fragment()` holds the vertex colour interpolated from `vertex()`;
  it is neither a texture nor the output.
- **Q5 — a frame-counting version** *(Zhaohui)*. 22 frames last 22 ÷ 30 ≈ 0.733 s at 30 fps,
  22 ÷ 60 ≈ 0.367 s at 60 fps and 22 ÷ 144 ≈ 0.153 s at 144 fps. Only at 60 fps does it match
  rule 2's 0.367 s, which is why the driver reads `stun` (physics ticks) instead of counting
  frames.
- **Q6 — default, current value, sharing** *(Claude-drafted)*. The default lives in the shader
  source (the `= 0.0` on the `hurt_amount` uniform line); the current value lives in the
  ShaderMaterial resource. If both fighters shared one material, setting `hurt_amount` for P2
  would flash P1 too, so each fighter gets its own material (rule 6).
- **Q7 — does `hint_range` clamp a value set from code? (prediction)** *(Zhaohui)*. No.
  `hint_range` primarily controls the range shown in the Inspector and does not necessarily clamp
  values assigned from code. *To be checked in Use It with a capture at `hurt_amount = 2.0`.*

Still open: the contrast ratio.

## Revision 5 · 2026-10-28 · contrast ratio (before any shader or measurement)

WCAG contrast of P-gi against the background beneath it, computed by hand by Zhaohui with a
calculator: decode each channel (c = v / 255, ((c + 0.055) / 1.055)^2.4), L = 0.2126 R +
0.7152 G + 0.0722 B, ratio = (L_light + 0.05) / (L_dark + 0.05).

| Colour | RGB | L | Ratio against the background |
|---|---|---|---|
| Background under P-gi | (48, 35, 47) | 0.02036 | — |
| P-gi, `hurt_amount = 0.0` | (222, 89, 0) | 0.22674 | 3.93 : 1 |
| P-gi, `hurt_amount = 1.0` | (255, 0, 0) | 0.21260 | **3.73 : 1** |

Zhaohui first wrote 3.93 for the full-red row as well; Claude's check gave 0.2626 / 0.07036 ≈
3.73, and Zhaohui accepted the correction. The other values agree with Claude's check.

**Finding:** the red flash *lowers* Akaken's gi contrast slightly (3.93 → 3.73), because red takes
G from 89 to 0 and G carries the largest luminance weight. The flash is visible through the hue
change, not a brightness change. This supports predicted failure case 8; the capture and the
muted playtest decide it.

All TO DO items of Version 1 are now filled. The next step is the hand-written shader.
