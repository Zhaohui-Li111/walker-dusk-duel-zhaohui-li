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
  (`godot/fighter/fighter.gd:19`), emitted only by `_resolve()` (`:221-223`); `point` = centre of
  hitbox ∩ hurtbox (`:170-172`). A K.O. hit sends `"hit"` before `knocked_out` (`:173`).
  `main.gd` sets `hitstop = HITSTOP_FRAMES` (4) on `"hit"` (`godot/game/main.gd:16`, `:133-138`).
- **Effect B (embers), condition:** `main.phase == "fight"` (`godot/game/main.gd:24`), a plain
  variable with **no change signal**, so the effect code **polls it every physics tick**
  (Zhaohui's decision, 2026-11-08). `"fight"` is set at `:71-74` and `:120-123`, `"ko"` at `:145`.
- **Signals and state both effects read:** `round_started` (`main.gd:9`, emitted `:102`),
  `paused_changed` (`:11`, `:116`). `paused` (`:27`) and `hitstop` (`:28`, no signal) only make
  `step()` return early (`:56-57`, `:60-62`); nothing pauses the tree, so particle nodes keep
  running unless `speed_scale` is changed (`CHANGE-BRIEF.md:26-30`).
- **Scenes the effects appear in:** `godot/game/main.tscn`, root `Main` with children `Stage`,
  `P1`, `P2`, `Effects`, `HUD`, `AudioDirector` (`:10-42`). Effect A's emitters are parented to
  `Main` (`CHANGE-BRIEF.md:140-141`). Effect scenes go in `godot/effects/` (not created yet).
- **Wiring (Zhaohui's decision, 2026-11-08):** `main.tscn` gains controller node(s) whose scripts
  live in `godot/effects/` and connect to the signals and read `phase` themselves. `main.gd` is
  not edited.
- **Textures (Zhaohui's decision, 2026-11-08):** a committed GDScript draws each texture once and
  saves a PNG in `godot/effects/`; the effect scenes reference the PNG, so the texture is a scene
  setting the config test can read back.
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
  `capture_*.gd` need a window (`capture_a5.gd:2-3`). Run `godot --headless --path godot
  --import` once after cloning (`README.md:104-107`).

## Headless facts (this machine: Windows 11, Godot 4.7.2, Git Bash)

- A headless run uses a dummy renderer: it draws no particles and runs no GPU particle process.
  Node state (emitting, one_shot, amount_ratio, visibility, instance counts) is observable; the
  look is not. (A5: every headless run drew nothing; captures needed a window.)
- A GPU effect's headless CPU price is near zero by construction.
- Frame strips come from a windowed Movie Maker run, which Zhaohui starts.
- `--fixed-fps N` fixes the frame delta; physics still runs 60 ticks per game second, so a test
  of pause or hitstop goes through the real `_physics_process` loop.

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
- Confirmed on `CPUParticles2D` by `ClassDB` probes (`CHANGE-BRIEF.md:43-46`; review probe
  2026-11-08): `emitting`, `one_shot`, `explosiveness`, `lifetime`, `preprocess`,
  `local_coords`, `speed_scale`, `use_fixed_seed`, `seed`, `emission_shape`
  (`EMISSION_SHAPE_RECTANGLE` = 3), `emission_rect_extents`, `initial_velocity_min` / `_max`,
  `spread`, `gravity`, `damping_min` / `_max`, `angle_min` / `_max`, `color_ramp`,
  `color_initial_ramp`, `scale_amount_min` / `_max` / `_curve`, `hue_variation_min`; and
  `CanvasItemMaterial.blend_mode` (`BLEND_MODE_ADD` = 1). **Absent:** `amount_ratio`,
  `alpha_curve`, `scale_min`, `scale_max`, `turbulence_enabled`, `trail_enabled`, `sub_emitter`.
  Alpha goes in `color_ramp`; size in `scale_amount_*` (`CHANGE-BRIEF.md:127-129`). For any
  other property, check `ClassDB.class_get_property_list` first; if missing, report it.
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
  (stay on GL Compatibility, no `hdr_2d`, no new autoloads). `GPUParticles2D` only as Step 6's
  scratch node for reading the process shader, not kept (`CHANGE-BRIEF.md:384-386`).

## Unconfirmed

- The brief cites `main.gd:25` for `phase`; it is on `:24` (Claude Code's error in the brief's
  facts; to be fixed in a dated revision).
- The brief's open questions 1–5 (`CHANGE-BRIEF.md:316-337`): spark reach, spawning at
  `speed_scale` 0, `preprocess` after load, simulation while hidden, the two colour ramps.
- `blender/prop_taiko.blend` has an uncommitted change from before A5; never commit it with A6.
- There is no `AGENTS.md` at the repository root (Glob, 2026-11-08), so none is imported.
