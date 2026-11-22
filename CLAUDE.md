# CLAUDE.md — walker-dusk-duel

## Project context

- **Engine:** Godot 4.7.2 stable (`README.md:10`), feature "4.7" (`godot/project.godot:15`), project
  in `godot/`. **Renderer:** GL Compatibility, desktop and mobile (`godot/project.godot:35-36`).
- **Main scene:** `res://game/main.tscn` (`godot/project.godot:14`). Viewport 640 × 360, window
  1280 × 720, `canvas_items` stretch (`:23-27`); physics 60 ticks/s (`:31`).
- **State machine:** `godot/fighter/fighter.gd`, shared by both fighters: `state` and `frame`
  (ticks in the state, `:48-49`), reset by `_set_state()` (`:231-236`). `main.gd` steps both
  fighters on the physics tick (`godot/game/main.gd:51-52`, `:64-65`) and checks hits after
  (`:67-68`); `paused` and `hitstop` skip that step (`:56-62`). P1 Akaken is the player
  (`PlayerController`), P2 Aotake the CPU (`main.gd:36-37`).
- **Kick, from the code** (`CHANGE-BRIEF.md:26-35`): frame 0–7 startup, 8–12 active
  (`check_hit()`, `fighter.gd:164-165`), 13–27 recovery, `idle` on frame 28 (`:106-108`).
- **Clip 1, lantern flame (cycle):** route Sprite2D + AnimationPlayer frame track
  (`CHANGE-BRIEF.md:59`). One scene, `godot/animations/lantern_flame.tscn`: `Sprite2D`,
  `AnimationPlayer` with `flicker`, root script that only `play()`s and `seek()`s a per-instance
  start offset (`CHANGE-BRIEF.md:283-287`). Two instances in `main.tscn` after `Stage`
  (`godot/game/main.tscn:18`; `CHANGE-BRIEF.md:176`). Sheet
  `godot/art/sheets/lantern_flame.png`, 12 × 16 cells, 4 × 2 (`CHANGE-BRIEF.md:90-99`).
  None of this exists yet.
- **Clip 2, kick arc (committing):** route cutout rig keyed as resource text (`CHANGE-BRIEF.md:59`):
  a `Node2D` pivot with `Polygon2D` segments, its `AnimationPlayer` and a rig controller, all in
  `godot/fighter/fighter.tscn` (`CHANGE-BRIEF.md:60`), so on P1 and P2 (`main.tscn:23`, `:28`).
  Does not exist yet.
- **Scenes:** `main.tscn` children `Stage`, `Embers`, `P1`, `P2`, `Effects`, `HitSpark0-3`,
  `HitSparkPool`, `EmbersController`, `HUD`, `AudioDirector`, `DebugVsync` (`:15-65`);
  `fighter.tscn` = `Fighter` → `Sprite2D` → `HurtFlash` (`godot/fighter/fighter.tscn:6-13`).
- **Tests** — from the repo root, only through the wrapper:
  `scripts/run-test.sh <file in godot/tests/> <fps|realtime> [timeout-seconds]`
  (`scripts/run-test.sh:2`). `GODOT` names the console build when `godot` is not on PATH (`:4-8`).
  Always `--headless`; a number adds `--fixed-fps N` and logs to `logs/<name>_<N>fps.log`;
  `realtime` adds no fps flag and logs to `logs/<name>_realtime.log` (`:10-16`). Timeout defaults
  to 120 s (`:16`, exit 124 = timeout). Exit 1 if the log has `SHADER ERROR`, `SCRIPT ERROR` or
  `Failed loading resource` (`:18`).

  ```bash
  scripts/run-test.sh test_runner.gd 60            # 94 / 0 (logs/test_runner_60fps.log:24)
  scripts/run-test.sh check_props3d.gd 60          # 49 / 0 (logs/check_props3d_60fps.log:22)
  scripts/run-test.sh test_hurt_flash.gd 30        # 69 / 0 at 30, 60, 144 (logs/test_hurt_flash_*fps.log:172)
  scripts/run-test.sh test_materials.gd 60         # 96 / 0 (logs/test_materials_60fps.log:125)
  scripts/run-test.sh test_hit_spark_config.gd 60  # 69 / 0 (logs/test_hit_spark_config_60fps.log:77)
  scripts/run-test.sh test_hit_spark_state.gd 60   # 57 / 0 (logs/test_hit_spark_state_60fps.log:112)
  scripts/run-test.sh test_embers_config.gd 60     # 85 / 0 (logs/test_embers_config_60fps.log:93)
  scripts/run-test.sh test_embers_state.gd 60      # 38 / 0 (logs/test_embers_state_60fps.log:75)
  scripts/run-test.sh <new_test>.gd realtime 180   # real frame clock, still headless
  ```

  `test_runner.gd` turns physics off and calls `main.step()` itself (`godot/tests/test_runner.gd:48`);
  `test_hurt_flash.gd` keeps `_physics_process` on and presses keys with
  `Input.parse_input_event` (`godot/tests/test_hurt_flash.gd:5-6`, `:548`): the model for pins,
  state and edge tests. Run `godot --headless --path godot --import` once after cloning
  (`README.md:105-108`).

## Headless facts (this machine: Windows 11, Godot 4.7.2, Git Bash)

- A headless run uses a dummy renderer and draws nothing; node state is observable, the look is not.
- `--fixed-fps N` fixes the frame delta; physics still runs 60 ticks per game second.

## Current change

@CHANGE-BRIEF.md

## Ownership

- Every file in `godot/shaders/` is hand-written by Zhaohui. An agent never creates, edits,
  reformats or "fixes" these files. If a shader looks wrong, report it and stop.
- Clips live as resources in `godot/animations/` or in the scene that owns them (`.tscn`/`.tres`),
  and are never built in code at runtime. Scripts only play, stop and `seek()` clips.
- The brief's intent, phase table, cycle spec, predictions and verdicts are Zhaohui's
  (`CHANGE-BRIEF.md:3-15`). The brief is only appended to, with dated revisions.

## One authority

Exactly one node writes to each animated node. Never add a second writer to a node that already
has one; if a change needs one, stop and say so.

| Animated node | Its one writer |
|---|---|
| Lantern `Sprite2D.frame` (each instance) | that lantern's `AnimationPlayer` (`CHANGE-BRIEF.md:61`) |
| Arc pivot and `Polygon2D` segments (each fighter) | that fighter's rig `AnimationPlayer`, positioned by the rig controller's `seek()` (`CHANGE-BRIEF.md:61`, `:162`) |
| Fighter `Sprite2D` (`texture`, `flip_h`, `offset`) | `fighter.gd` `_update_sprite()` (`fighter.gd:286-291`); no clip keys it |
| Fighter `Sprite2D.material` / `hurt_amount` | `HurtFlash` (`godot/fighter/hurt_flash.gd:21`, `:28`) |

## Godot 4 names

- Use Godot 4.7.2 names only: `AnimationPlayer`, `Animation`, `Sprite2D`, `Node2D`, `Polygon2D`,
  `Animation.loop_mode` (`LOOP_NONE`, `LOOP_LINEAR`), `Animation.step`, `Animation.length`,
  `AnimationPlayer.speed_scale`, `current_animation`, `callback_mode_process`
  (`ANIMATION_CALLBACK_MODE_PROCESS_IDLE` / `_PHYSICS` / `_MANUAL`), `Animation.UPDATE_DISCRETE`.
  Never Godot 3 names: a boolean `loop` (absent, `CHANGE-BRIEF.md:46-47`), `playback_speed`
  (absent), `AnimatedSprite`, `frames` or a settable `playing`.
- Confirmed by the 2026-11-22 probe (`CHANGE-BRIEF.md:44-48`): `Animation` has `loop_mode`, `step`,
  `length`; `AnimationPlayer` has `speed_scale`, `current_animation`, `callback_mode_process`.
  Not yet probed: `ANIMATION_CALLBACK_MODE_PROCESS_MANUAL` and `value_track_get_update_mode` in
  4.7.2. For any other property, check `ClassDB.class_get_property_list` first; if missing, say so.

## Out of scope

- Fight logic: collision, movement, input, the state machine and its timings in `fighter.gd` and
  `main.gd`. Presentation code reads `state`, `frame`, `paused`, `hitstop` and signals; it never
  writes game state.
- A5 and A6 work: `godot/shaders/`, `hurt_flash.gd`, the granite and hint materials, the prop room,
  `godot/effects/` and the A6 previews. Also `effects.gd`, `audio_director.gd`, the HUD,
  `stage.gd`, `art/env/bg.png`, sprite images, `data/poses.json`.
- The sheet as committed (`godot/art/sheets/lantern_flame.png`) and its generator.
- Existing tests and their counts (new checks go in new files); project settings and renderer.

## Unconfirmed

- Whether `seek(t, true)` on a `MANUAL` player applies keys on the same physics tick (brief's
  0 s clock disagreement, `CHANGE-BRIEF.md:166-168`); a state test must measure it.
- Physics order: the rig controller must run after `main.step()` in each tick; not yet checked.
- `blender/prop_taiko.blend` has an uncommitted change from before A5; never commit it with A7.
- There is no `AGENTS.md` at the repository root (checked 2026-11-22), so none is imported.
