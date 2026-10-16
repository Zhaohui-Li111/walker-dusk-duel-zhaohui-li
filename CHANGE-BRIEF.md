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
