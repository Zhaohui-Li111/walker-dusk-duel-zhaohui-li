# CLAUDE.md — walker-dusk-duel

## Project context

- **Engine:** Godot 4.7.2 stable, `v4.7.2.stable.official.ed1daf0bf` (`README.md:10`,
  `logs/test_hurt_flash_60fps.log:1`), feature "4.7" (`godot/project.godot:15`), in `godot/`.
- **Renderer:** GL Compatibility, desktop and mobile (`godot/project.godot:35-36`).
- **Main scene:** `res://game/main.tscn` (`godot/project.godot:14`). Viewport 640 × 360, window
  1280 × 720, `canvas_items` stretch (`godot/project.godot:23-27`); physics 60 ticks/s (`:31`).
- **Node type per effect:** both effects are `CPUParticles2D` (`CHANGE-BRIEF.md:105`, `:223`).
  Effect A is a pool of four one-shot emitters × 20 particles (`CHANGE-BRIEF.md:136-139`);
  Effect B is one continuous rectangle emitter, 48 particles (`CHANGE-BRIEF.md:216-224`).
- **Effect A (hit spark), event:** `Fighter.attack_resolved(fighter, kind, result, point)`
  (`godot/fighter/fighter.gd:19`), emitted only by `_resolve()` (`:221-223`). `check_hit()` emits
  `"hit"` or `"blocked"` with `point` = centre of hitbox ∩ hurtbox (`:170-172`), then `flush_ko()`
  (`:173`), so a K.O. hit sends `"hit"` before `knocked_out` (`:21`, `:206-209`). `receive_hit()`
  emits `"interrupted"` with `Vector2.ZERO` (`:185-186`). `main.gd` connects both fighters
  (`godot/game/main.gd:42-44`); its handler drops `"interrupted"`, calls `effects.spawn()` and
  sets `hitstop = HITSTOP_FRAMES` (4) on `"hit"` (`:16`, `:133-138`).
- **Effect B (embers), condition:** `main.phase` (`godot/game/main.gd:24`), a plain variable with
  **no change signal**. It becomes `"intro"` in `start_round()` (`:98`), `"fight"` in `step()`
  after `INTRO_FRAMES` (`:13`, `:71-74`) or in `start_fight_now()` (`:120-123`), `"ko"` in
  `_on_knocked_out()` (`:145`), `"result"` after `KO_FRAMES` (`:14`, `:78-79`), `"title"` in
  `_show_title()` (`:127`).
- **Signals and state both effects read:** `round_started(round_number)` (`main.gd:9`, emitted
  `:102` after `effects.clear()` `:95`); `round_over(winner)` (`:10`, `:150`);
  `paused_changed(paused)` (`:11`, `:116`). `paused` (`:27`) and `hitstop` (`:28`) only make
  `step()` return early (`:56-57`, `:60-62`); nothing calls `get_tree().paused`, so particle nodes
  keep running unless `speed_scale` is changed (`CHANGE-BRIEF.md:26-30`). `hitstop` has no signal.
- **Scenes the effects appear in:** `godot/game/main.tscn` — root `Main` (`Node2D`, `main.gd`,
  `:10-11`) with children `Stage`, `P1`, `P2`, `Effects`, `HUD`, `AudioDirector` (`:13-42`).
  Effect A's emitters are parented to `Main` (`CHANGE-BRIEF.md:140-141`); Effect B sits at
  (320, 215) with extents (280, 90) (`CHANGE-BRIEF.md:229-230`). Effect scenes go in
  `godot/effects/`, which does not exist yet (Glob, 2026-11-08). Fighters are
  `godot/fighter/fighter.tscn` (`Node2D` → `Sprite2D` → `HurtFlash`, `:6-14`).
- **Existing hit feedback:** `godot/game/effects.gd` draws an 8-line spark for 10 ticks
  (`:9-10`, `:31-35`); it stays, and the particle burst is added beside it (`CHANGE-BRIEF.md:65-67`).
- **Tests** — from the repo root, always through the wrapper (`scripts/run-test.sh:2`):
  `scripts/run-test.sh <file in godot/tests/> <fps|realtime> [timeout-seconds]`. `GODOT` names
  the console build if `godot` is not on PATH (`:3-7`). Always `--headless`; a number adds
  `--fixed-fps N` and logs to `logs/<name>_<N>fps.log`; `realtime` adds no fps flag and logs to
  `logs/<name>_realtime.log` (`:9-14`). Timeout defaults to 120 s (`:15`; exit 124 = timeout).
  Exit 1 if the log has `SHADER ERROR` or `SCRIPT ERROR`, even when Godot exited 0 (`:16-18`).

  ```bash
  scripts/run-test.sh test_runner.gd 60           # 94 checks, 0 failed (logs/test_runner_60fps.log:24)
  scripts/run-test.sh check_props3d.gd 60         # 49 / 0 (logs/check_props3d_60fps.log:22)
  scripts/run-test.sh test_hurt_flash.gd 30       # 69 / 0 at 30, 60, 144 (logs/test_hurt_flash_*fps.log:172)
  scripts/run-test.sh test_materials.gd 60        # 96 / 0 (logs/test_materials_60fps.log:125)
  scripts/run-test.sh calibrate_normal_map.gd 60  # exit 1 if the gl/dx pair does not separate (:6-7)
  scripts/run-test.sh <new_test>.gd realtime 180  # real frame clock, still headless
  ```

  `test_runner.gd` turns physics off and calls `main.step()` itself (`godot/tests/test_runner.gd:48`);
  `test_hurt_flash.gd` keeps `_physics_process` on (`:5-6`), the model for pause/hitstop tests.
  `test_hit_spark_config.gd` (`CHANGE-BRIEF.md:154`) does not exist yet. `capture_*.gd` need a
  window (`capture_a5.gd:2-3`). Headless draws nothing: it proves properties and signals, never
  looks. Run `godot --headless --path godot --import` once after cloning (`README.md:104-107`).

## Current change

@CHANGE-BRIEF.md

## Ownership

- Every file in `godot/shaders/` (e.g. `hurt_flash.gdshader`, `granite.gdshader`) is hand-written
  by the human (Zhaohui). An agent never creates, edits, reformats or "fixes" these files. If a
  shader looks wrong, report it and stop.
- Effect settings live in scene files in `godot/effects/`, not in code. Every value in the brief's
  settings tables (`CHANGE-BRIEF.md:103-125`, `:221-245`) is set in a `.tscn`; scripts only start,
  stop, position, pool and set `speed_scale` at run time.
- The intent, setting values, rules, predictions, budgets and short answers are Zhaohui's
  (`CHANGE-BRIEF.md:7-8`). The brief is only appended to, with dated revisions (`:8-9`).

## Godot 4 names

- Use Godot 4.7.2 names: `CPUParticles2D`, `GPUParticles2D`, `ParticleProcessMaterial`,
  `CanvasItemMaterial`, `Gradient`, `Curve`. Never Godot 3 names such as `Particles2D` or
  `ParticlesMaterial` (that class does not exist, `CHANGE-BRIEF.md:46-47`).
- Confirmed on `CPUParticles2D` by the brief's `ClassDB` probe (`CHANGE-BRIEF.md:43-46`):
  `use_fixed_seed`, `seed`, `emission_rect_extents`, `color_ramp`, `scale_amount_min` / `_max` /
  `_curve`, `damping_min` / `_max`, `hue_variation_min`, `angle_min`. **Absent:** `amount_ratio`,
  `alpha_curve`, `scale_min`, `scale_max`, `turbulence_enabled`, `trail_enabled`, `sub_emitter`.
  Alpha goes in `color_ramp`; size in `scale_amount_*` (`CHANGE-BRIEF.md:127-129`).
- Not in that probe, so **not confirmed for 4.7.2 from the files**: `color_initial_ramp`,
  `initial_velocity_min` / `_max`, `angle_max`, `spread`, `gravity`, `emission_shape` and its
  rectangle value, `explosiveness`, `one_shot`, `lifetime`, `preprocess`, `local_coords`,
  `speed_scale`, `CanvasItemMaterial.blend_mode`. Check each with `ClassDB.class_get_property_list`
  in a headless test before relying on it; if one is missing, report it, do not substitute.
- `ParticleProcessMaterial` also lists `initial_velocity` and `scale` (Godot 3 names, effect
  unknown, `CHANGE-BRIEF.md:47-48`). Do not use them.

## Out of scope

- Fight logic: collisions, movement, input, the state machine, frame data and timing constants
  in `fighter.gd` and `main.gd`. Effect code reads `phase`, `paused`, `hitstop` and signals; it
  never writes game state or adds rules.
- `effects.gd` and its spark, `audio_director.gd`, the HUD, `stage.gd` and `art/env/bg.png`,
  sprite images, `data/poses.json`.
- All A5 work: `godot/shaders/`, `hurt_flash.gd`, the granite and hint materials, the prop room
  and the A3 props and `.blend` sources.
- Existing tests and their counts (new checks go in new files); project settings and renderer
  (stay on GL Compatibility, no `hdr_2d`, no new autoloads).
- `GPUParticles2D` in the final effects: a GPU node may exist only as a scratch node for reading
  the process shader in Step 6, and is not kept (`CHANGE-BRIEF.md:384-386`).

## Unconfirmed

- Which file wires the effects into `main.tscn`, and whether `main.gd` may gain any line: the
  brief parents Effect A to `Main` (`:140-141`) but does not say. Ask before editing `main.gd`.
- The textures are "code-drawn" (`CHANGE-BRIEF.md:120`, `:241`), which conflicts with "settings
  in scene files"; a texture saved once as a resource would satisfy both. Zhaohui decides.
- Effect B has no phase signal (`main.gd:24`); polling each tick keeps `main.gd` unchanged.
  Not decided.
- The brief cites `main.gd:25` for `phase`; it is on `:24`.
- The brief's open questions 1–5 (`CHANGE-BRIEF.md:316-337`): spark reach, spawning at
  `speed_scale` 0, `preprocess` after load, simulation while hidden, the two colour ramps.
- `blender/prop_taiko.blend` has an uncommitted change from before A5; never commit it with A6.
- There is no `AGENTS.md` at the repository root (Glob, 2026-11-08), so none is imported.
