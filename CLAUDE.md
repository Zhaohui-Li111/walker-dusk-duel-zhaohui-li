# CLAUDE.md — walker-dusk-duel

## Project context

- **Engine:** Godot 4.7.2 stable (`README.md:10`, `scripts/run-test.sh:3`); the project declares
  feature "4.7" (`godot/project.godot:15`). The project lives in `godot/`.
- **Renderer:** GL Compatibility, `renderer/rendering_method="gl_compatibility"`, also for mobile
  (`godot/project.godot:35-36`). No Forward+/Mobile-only features.
- **Main scene:** `res://game/main.tscn` (`godot/project.godot:14`). Viewport 640 × 360, window
  1280 × 720, `canvas_items` stretch (`godot/project.godot:23-27`). Physics 60 ticks/s
  (`godot/project.godot:31`).
- **How the shaded object is drawn:** each fighter is `godot/fighter/fighter.tscn`, a `Node2D`
  with a child `Sprite2D` (`centered = false`, no material yet) (`godot/fighter/fighter.tscn:5-10`).
  `Fighter._update_sprite()` sets its `texture`, `flip_h` and `offset` from the current state
  (`godot/fighter/fighter.gd:286-291`), using images and offsets from `FighterArt`
  (`godot/fighter/fighter_art.gd:24-50`, `:67-74`). Two instances, `P1` (akaken) and `P2`
  (aotake), live in `godot/game/main.tscn:16-24`.
- **Game state that drives the effect:** `godot/fighter/fighter.gd` owns `state` and `stun`
  (`:48`, `:53`) and `HITSTUN := 18` (`:40`). `receive_hit()` sets `stun = HITSTUN` and forces a
  fresh `"hurt"` (`:196-200`), or `"ko"` at 0 health (`:192-195`); `step()` counts `stun` down in
  `"hurt"` and returns to `"idle"` (`:109-113`). `godot/game/main.gd` steps both fighters
  (`:55-69`), freezes them for `HITSTOP_FRAMES := 4` after a hit (`:16`, `:60-62`, `:137-138`) and
  stops stepping while `paused` (`:56-57`).
- **3D object for the textured shader:** in `godot/props3d/prop_room.tscn`, the `Floor`
  `MeshInstance3D` (BoxMesh 6 × 0.1 × 4, `:11-13`, `:35-37`) and a `StonePlinth` the brief
  plans to add (`CHANGE-BRIEF.md:373-375`). Today the floor's material is an embedded
  `StandardMaterial3D` sub-resource on the BoxMesh's `material` (`prop_room.tscn:7-13`). The brief
  plans `material_override` → `godot/props3d/materials/granite_floor.tres` and
  `granite_plinth.tres`, both ShaderMaterials of `godot/shaders/granite.gdshader`
  (`CHANGE-BRIEF.md:376-383`). Textures: `godot/props3d/textures/granite_wall_*_1k.png`, credits
  in `godot/props3d/textures/ATTRIBUTION.md`.
- **Tests** — run from the repo root, always through the wrapper
  (`scripts/run-test.sh <file in godot/tests/> <fps>`, `scripts/run-test.sh:2`). It needs
  `GODOT` set to the console build if `godot` is not on PATH (`:3-6`), runs headless with a 120 s
  timeout, writes `logs/<name>_<fps>fps.log` and fails on `SHADER ERROR` or `SCRIPT ERROR`
  (`:7-12`):

  ```bash
  scripts/run-test.sh test_runner.gd 60           # fight, sound, music (godot/tests/test_runner.gd:9-21)
  scripts/run-test.sh check_props3d.gd 60         # A3 props vs brief (godot/tests/check_props3d.gd:1-10)
  scripts/run-test.sh calibrate_normal_map.gd 60  # curl check on gl/dx pair (godot/tests/calibrate_normal_map.gd:6)
  ```

  Rule 2 of the brief asks for 30, 60 and 144 fps runs (`CHANGE-BRIEF.md:281-284`, `:308`): pass
  `30` / `144` as the second argument. `godot/tests/normal_map_check.gd` is a library
  (`extends RefCounted`, `:1`), not a runnable test. `capture_states.gd`, `capture_flow.gd` and
  `capture_props3d.gd` need a window (`godot/tests/capture_states.gd:3`,
  `capture_props3d.gd:3`), so they do not run through the headless wrapper.

## Current change

@CHANGE-BRIEF.md

## Ownership

- Every file in `godot/shaders/` (e.g. `hurt_flash.gdshader`, `granite.gdshader`) is hand-written
  by the human (Zhaohui). An agent never creates, edits, reformats or "fixes" these files. If a
  shader looks wrong, report it and stop.
- Lines marked "TO DO (Zhaohui)" in `CHANGE-BRIEF.md` are Zhaohui's to write. The A5 section is
  only appended to, with dated revisions (`CHANGE-BRIEF.md:229-233`).

## Out of scope

- The fight itself: collision boxes, movement, input, the state machine, every frame count and
  timing constant in `fighter.gd` and `main.gd`. The flash driver only reads `state`, `stun` and
  `HITSTUN`; it never writes them or adds game logic.
- `effects.gd`, `audio_director.gd`, the HUD, the background (`stage.gd`, `art/env/bg.png`), and
  the sprite images and `data/poses.json`.
- The existing tests and their expectations (`test_runner.gd`, `check_props3d.gd`); new checks
  go in new test files.
- The three A3 props: their `.glb` models, imported materials, positions, and the `.blend`
  sources. No UVs are added to them; the textured shader goes on the floor and plinth only.
- The 1.70 m reference box, the camera, the `Sun` and the environment of the prop room
  (no SSAO, glow or fog is added).
- The renderer: stay on GL Compatibility; do not set `hdr_2d` or change project settings.
- One material per fighter: never one shared hurt-flash material on both sprites.

## Unconfirmed

- Check counts: the brief says `test_runner.gd` has 94 checks and `check_props3d.gd` 49
  (`CHANGE-BRIEF.md:299`), `README.md:103-104` says 49, but the A3 build result says 43
  (`CHANGE-BRIEF.md:209`). Not run here, so none of these is confirmed.
- Whether `--fixed-fps` changes anything for `test_runner.gd`: it drives `main.step(DT)` itself
  with `DT = 1/60` and turns off `_physics_process` (`godot/tests/test_runner.gd:8`, `:48`), so
  the 30/144 fps runs the brief wants probably need a new test that uses the real loop.
- Whether a fresh clone needs `godot --headless --path godot --import` before the wrapper
  (`README.md:103-108`); `run-test.sh` does not import.
- Where the hurt-flash driver will live (a new node, or code in `fighter.gd`) and how each
  fighter gets its own material; the brief leaves both open (`CHANGE-BRIEF.md:274-275`, `:292-293`).
- The hurt-flash `render_mode`, the contrast ratio, the granite uniform table and the hint
  experiment predictions are still TO DO (`CHANGE-BRIEF.md:256-257`, `:348`, `:356-362`, `:405`).
- BoxMesh UV layout (3 × 2 grid) is "to be confirmed with a probe" (`CHANGE-BRIEF.md:384-386`).
- `godot/shaders/` and `godot/props3d/materials/` do not exist yet; `StonePlinth` is not in
  `prop_room.tscn`. The hint-experiment scene (`godot/hint_experiment/hint_experiment.tscn`) has
  two quads with no material yet.
- The sprite texel coordinates in the brief are to be "confirmed or corrected from the first
  capture" (`CHANGE-BRIEF.md:336`).
- Whether `timeout` and `tee` in `run-test.sh` work in the shell used on this Windows machine
  (Git Bash assumed).
- There is no `AGENTS.md` at the repository root, so this file does not import one.
