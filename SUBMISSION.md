# SUBMISSION — Assignment 5

> Prepared by Claude Code from the repository records. Earlier notes are kept unchanged in
> [SUBMISSION-A3.md](SUBMISSION-A3.md) and [SUBMISSION-A2.md](SUBMISSION-A2.md).

- **Assignment:** Assignment 5 - Shaders, Materials, and the Godot Shading Language
- **Student:** Zhaohui Li
- **Project name:** walker-dusk-duel
- **GitHub repository URL:** https://github.com/Zhaohui-Li111/walker-dusk-duel-zhaohui-li
- **Git tag and submitted commit SHA:** tag `a5`. The commit SHA is the one the tag points at; it is
  entered in the Canvas note, because a file cannot contain its own commit hash. The source ZIP is
  `git archive` of that commit.
- **Game-source revision shown in the film:** `043df17`, the last commit that changed `godot/`.
  Later commits add only the film source, documentation and this note; `godot/` is unchanged.
- **Godot version, renderer, and operating system:** Godot 4.7.2 stable, GL Compatibility,
  Windows 11 Home
- **Game state the shader from code communicates:** a fighter was just hit cleanly
  (`Fighter.state == "hurt"`). `godot/shaders/hurt_flash.gdshader` tints that fighter's sprite red,
  `hurt_amount = stun / HITSTUN`, for 22 physics ticks (0.367 s) at any frame rate.
- **3D object and scene given the textured shader:** the `Floor` and a new `StonePlinth` in
  `godot/props3d/prop_room.tscn`, with `granite_floor.tres` and `granite_plinth.tres`, both using
  `godot/shaders/granite.gdshader`. (The A3 props have no UVs; see CHANGE-BRIEF A5.)
- **Texture sources and licences:** Poly Haven *Granite Wall*, https://polyhaven.com/a/granite_wall,
  Dimitrios Savva, CC0 (`godot/props3d/textures/ATTRIBUTION.md`); `_nor_gl` used. The hint-experiment
  PNG is written by `godot/hint_experiment/write_hint_png.gd`.
- **Final film URL and filename:** *link to be added after upload to course media storage* · `claude-liam-walker-dusk-duel-zhaohui-li-a5-gamedev.mp4` ("Dusk Duel, Shaded", 5:35, 3840 × 2160, 30 fps, 26.4 MB)
- **Final film SHA-256:** `e04cbc986b195d4cb0f3a45b8427f1de4660bdb699ee7d2469c524e7519d3143`
- **Summary of my work:** I chose the effect and the colour, wrote the colour line, and typed all
  three shaders by hand (`hurt_flash`, `granite`, `hint_experiment`). I computed the pixel, hint and
  contrast predictions with a calculator, made the three shader mutations, decided every brief
  revision, did the Step 4 conversion in the editor, wrote LANGUAGE-NOTES, and did the human checks
  in TEST-REPORT. Claude Code wrote the driver, the tests, the audit, the capture tools, the
  documents' drafts and the film (SOURCES.md has the full split).
- **Results:** `test_hurt_flash.gd` 69 / 0 at 30, 60 and 144 fps; `test_materials.gd` 96 / 0, also
  from an empty cache; earlier suites 94 / 0 and 49 / 0; all three mutations exit 1.
- **Known limitations:** headless tests prove parsing, driving and wiring, not looks; a retrigger
  cannot happen in real play, so rule 3 is checked only with labelled test setup; `Engine.time_scale`
  does not slow the fight or the flash; in Compatibility both hint quads show the stored values; the
  BoxMesh UVs stretch the granite so it reads as planks; the OS-screenshot comparison was not done.
- **Changed games since Assignment 2:** no.

## Clone check (2026-10-29)

`git clone` of the repository at `52b1bbb` into a fresh folder, `godot --headless --path godot
--import` (exit 0), then every suite through `scripts/run-test.sh`: `test_runner.gd` 60 → 94 / 0;
`check_props3d.gd` 60 → 49 / 0; `test_hurt_flash.gd` 30, 60, 144 → 69 / 0 each;
`test_materials.gd` 60 → 96 / 0; `calibrate_normal_map.gd` 60 → PASS. No log contains SHADER ERROR or
SCRIPT ERROR. The counts match TEST-REPORT.md. (Run on the local clone; the GitHub copy is checked
after the push.)

## Film documentation added after the tag

The film was exported after tag `a5` (`532e0eb`). Its hash and this note were added in a later
commit, a documentation-only revision: `godot/` is unchanged, so the film shows the game source of `a5`
(`043df17`).
