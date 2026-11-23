# SUBMISSION — Assignment 7

> Prepared by Claude Code from the repository records. Earlier notes are kept unchanged in
> [SUBMISSION-A6.md](SUBMISSION-A6.md), [SUBMISSION-A5.md](SUBMISSION-A5.md),
> [SUBMISSION-A3.md](SUBMISSION-A3.md) and [SUBMISSION-A2.md](SUBMISSION-A2.md).

- **Assignment:** Assignment 7 - Doing Animation with Claude and Godot
- **Student:** Zhaohui Li
- **Project name:** walker-dusk-duel
- **GitHub repository URL:** https://github.com/Zhaohui-Li111/walker-dusk-duel-zhaohui-li
- **Git tag and submitted commit SHA:** tag `a7`. The commit SHA is the one the tag points at; it is
  entered in the Canvas note, because a file cannot contain its own commit hash. The source ZIP is
  `git archive` of that commit.
- **Game-source revision shown in the film:** **PENDING** (filled in when the film is rendered).
- **Godot version, renderer, and operating system:** Godot 4.7.2 stable, GL Compatibility,
  Windows 11 Home
- **Sprite clip: route, node, scene, frame rate:** Sprite2D + AnimationPlayer frame track;
  `LanternFlame/Sprite2D` (`frame`) driven by `LanternFlame/AnimationPlayer` playing
  `godot/animations/lantern_flicker.tres`; scene `godot/animations/lantern_flame.tscn`, two
  instances in `godot/game/main.tscn`; 10 fps (step 0.1 s).
- **Rig clip: route, rig source, node, scene, frame rate:** cutout rig keyed as resource text;
  rig `KickRig` → `Pivot` → `Trail`, `Core` (`Polygon2D`) in `godot/fighter/fighter.tscn`, clip
  `godot/animations/kick_arc.tres` (and `kick_rest.tres`) on `KickRig/AnimationPlayer`; 60 fps
  (step 1/60).
- **Which clip loops and which commits:** the lantern flame loops (`LOOP_LINEAR`, 8 frames); the
  kick arc commits (`LOOP_NONE`; startup frames 0–7, active 8–12, recovery 13–27).
- **The one authority over each animated node:** lantern `Sprite2D.frame`: that lantern's
  `AnimationPlayer`. Arc `Pivot` and its segments: the fighter's `KickRig/AnimationPlayer`,
  positioned each physics tick by `kick_rig.gd`'s `seek(Fighter.frame / 60, true)` from the state
  machine's `state` and `frame`. `KickRig`'s own transform: `kick_rig.gd`. The fighter's `Sprite2D`
  stays with `fighter.gd`; no clip keys it.
- **Sprite sheet source and licence (or model, version, and terms):** written by code in this
  repository (`godot/art/sheets/make_lantern_flame_sheet.gd`), MIT; `godot/art/sheets/ATTRIBUTION.md`.
  No generative model.
- **Final film URL and filename:** **PENDING**
- **Final film SHA-256:** **PENDING**
- **Summary of my work:** I chose to generate the sheet by code, chose both clips, their routes and
  objects, the lantern frame order and 10 fps, the kick's 8 / 5 / 15 phase table from the code,
  the interrupt rule, the rig's clock and the lanterns' behaviour, and wrote the brief's answers,
  predictions and short answers. I approved the wiring plan, ran both Movie Maker captures, gave
  the first look and both strip verdicts, approved revision r1 and kept it after play, did the
  four human checks in the running game, and wrote my own account in FRICTIONAL.md. Claude Code
  wrote the sheet generator, CLAUDE.md, the pins, the clips and scenes, the rig controller, the
  read-backs, the state and edge tests, the mutations, the preview, the strip readings and the
  documents' drafts; SOURCES.md has the full split.
- **Results (at `48a3b60` and after r1, every suite through `scripts/run-test.sh` at 60 unless
  noted):** `test_pins_a7` 19 / 0 before and after the change; `test_lantern_readback` 47 / 0;
  `test_kick_readback` 52 / 0; `test_anim_states` 58 / 0; `test_kick_edges` 38 / 0; earlier suites
  `test_runner` 94 / 0, `check_props3d` 49 / 0, `test_hurt_flash` 69 / 0 at 30, 60 and 144,
  `test_materials` 96 / 0, `test_hit_spark_config` 69 / 0, `test_hit_spark_state` 57 / 0,
  `test_embers_config` 85 / 0, `test_embers_state` 38 / 0. Mutations 1–3 exit 1; mutation 4 (empty
  cache) exit 0, as expected with no imported clip. No log has SHADER ERROR, SCRIPT ERROR or Failed
  loading resource. **To be re-run from a fresh clone of the `a7` tag before submission.**
- **Known limitations:** headless runs prove structure, not the look; interrupt edges use labelled
  test setup; the left lantern is hidden behind Akaken at the start position; the empty-cache
  mutation cannot fail without an imported clip; the one tuning revision came from Claude Code's
  strip reading, approved and judged by me; prompt-1 ran in the desktop session after two
  `claude -p` sign-in failures.
- **Changed games since Assignment 2:** no.
