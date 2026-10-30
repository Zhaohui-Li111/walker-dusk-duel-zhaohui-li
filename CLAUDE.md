# CLAUDE.md — walker-dusk-duel

## Project context

- **Engine:** Godot 4.7.2 stable (`README.md:10`; the run itself prints "Godot Engine
  v4.7.2.stable.official.ed1daf0bf", `logs/test_runner_60fps.log:1`); the project declares
  feature "4.7" (`godot/project.godot:15`). The project lives in `godot/`.
- **Renderer:** GL Compatibility, `renderer/rendering_method="gl_compatibility"`, also for mobile
  (`godot/project.godot:35-36`). This rules out decals, compute shaders, VoxelGI, SDFGI and SSIL
  (A5 handout, Step 1 questions).
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
  `MeshInstance3D` (BoxMesh 6 × 0.1 × 4) and the `StonePlinth` (BoxMesh 0.8 × 0.3 × 0.8), each
  with `material_override` → `godot/props3d/materials/granite_floor.tres` and
  `granite_plinth.tres`, both ShaderMaterials of `godot/shaders/granite.gdshader`
  (`prop_room.tscn:43`, `:48`; audit in `godot/MATERIALS.md`). The floor's old embedded
  `StandardMaterial3D` is still on the BoxMesh, hidden by the override (MATERIALS.md finding 4). Textures: `godot/props3d/textures/granite_wall_*_1k.png`, credits
  in `godot/props3d/textures/ATTRIBUTION.md`. BoxMesh UVs are a 3 × 2 grid; the top face uses
  UV (⅓–⅔, ½–1) (probe, `FRICTIONAL.md:724`).
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
  `capture_props3d.gd:3`; `capture_flow.gd:4` gives its command without `--headless`), so they
  do not run through the headless wrapper. Baseline at 60 fps: `test_runner.gd` 94 checks,
  0 failed (`logs/test_runner_60fps.log:24`); `check_props3d.gd` 49, 0 failed
  (`logs/check_props3d_60fps.log:22`). Run `godot --headless --path godot --import` once
  after cloning (`README.md:104-107`).

## Headless facts (this machine: Windows 11, Godot 4.7.2, Git Bash)

- A headless run uses the dummy renderer and draws nothing. It can prove that a shader parses,
  that its uniforms are declared and driven, and that materials are wired. It cannot prove how
  anything looks. Captures need a real window (`capture_*.gd`, `capture_flow.gd:4`).
- Exit code 0 does not mean no errors. `scripts/run-test.sh:11` fails on `SHADER ERROR` /
  `SCRIPT ERROR`; exit 124 means the 120 s timeout hit (`:9`).
- `--fixed-fps N` fixes the frame delta; physics still runs 60 ticks per game second
  (`project.godot:31`). `test_runner.gd` turns physics off and calls `main.step(1/60)` itself
  (`test_runner.gd:8`, `:48`), so its result is the same at any fps. A test for rule 2 must go
  through the real `_physics_process` loop.
- `get_shader_uniform_list()` gives names and types; defaults are read from the shader source text.
  To confirm by the Step 2 mutations: a shader that fails to parse returns an empty list, and
  `set_shader_parameter` with an undeclared name raises no error and reads its value back.

## Current change

@CHANGE-BRIEF.md

## Ownership

- Every file in `godot/shaders/` (e.g. `hurt_flash.gdshader`, `granite.gdshader`) is hand-written
  by the human (Zhaohui). An agent never creates, edits, reformats or "fixes" these files. If a
  shader looks wrong, report it and stop.
- Lines marked "TO DO (Zhaohui)" in `CHANGE-BRIEF.md` are Zhaohui's to write. The A5 section is
  only appended to, with dated revisions (`CHANGE-BRIEF.md:232-233`).

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

- *Settled since the draft (review, 2026-10-29):* the driver is `godot/fighter/hurt_flash.gd`, a
  node under each fighter's `Sprite2D` that builds its own material; the brief's TO DOs were
  filled in Revisions 2–5; all three shaders, both granite materials, the `StonePlinth` and both
  hint materials exist (`godot/MATERIALS.md`).
- The sprite texel coordinates in the brief are to be "confirmed or corrected from the first
  capture" (`CHANGE-BRIEF.md:336`).
- `blender/prop_taiko.blend` already had an uncommitted change before A5 began (git status at the
  start of A5); it is not part of this change and must not be committed with it.
- There is no `AGENTS.md` at the repository root, so this file does not import one.
