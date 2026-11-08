# SUBMISSION — Assignment 6

> Prepared by Claude Code from the repository records. Earlier notes are kept unchanged in
> [SUBMISSION-A5.md](SUBMISSION-A5.md), [SUBMISSION-A3.md](SUBMISSION-A3.md) and
> [SUBMISSION-A2.md](SUBMISSION-A2.md).

- **Assignment:** Assignment 6 - Creating Particle Effects with Godot and Claude
- **Student:** Zhaohui Li
- **Project name:** walker-dusk-duel
- **GitHub repository URL:** https://github.com/Zhaohui-Li111/walker-dusk-duel-zhaohui-li
- **Git tag and submitted commit SHA:** tag `a6`. The commit SHA is the one the tag points at; it is
  entered in the Canvas note, because a file cannot contain its own commit hash. The source ZIP is
  `git archive` of that commit.
- **Game-source revision shown in the film:** TO DO (after the film is made).
- **Godot version, renderer, and operating system:** Godot 4.7.2 stable, GL Compatibility,
  Windows 11 Home
- **GPU used for the GPU price:** Intel(R) UHD Graphics (OpenGL 3.3, driver build 31.0.101.4502)
- **Effect A: event, node type, retrigger rule:** hit spark on `Fighter.attack_resolved` with
  result `"hit"`, at the contact point; `CPUParticles2D` (`godot/effects/hit_spark.tscn`), a pool of
  four one-shot slots in `main.tscn`; retrigger rule **overlap** (a new hit takes a free slot and
  never restarts a live burst; peak 4 × 20 = 80 particles).
- **Effect B: job, condition, node type, feature Effect A doesn't use:** ambience (courtyard embers)
  while `main.phase == "fight"`; `CPUParticles2D` (`godot/effects/embers.tscn`); a rectangle
  emission shape and `preprocess` 1.5 s. Frozen during the game's pause and hitstop and while the
  tree is paused; frozen while hidden (CHANGE-BRIEF Revision 4).
- **Budgets, and the price each is compared on:** A: CPU ≤ 0.25 ms and GPU ≤ 0.25 ms per frame;
  B: CPU ≤ 0.50 ms and GPU ≤ 0.50 ms; CPU nodes, so both prices. Measured (medians): CPU A ≈ 0.010 ms,
  B ≈ 0.006 ms (`cost_effects.gd`, empty-scene control); GPU A +0.012 ms, B +0.004 ms. All under
  budget. The editor's Visual Profiler read 0 for GPU time here, so the GPU numbers come from
  `RenderingServer` GPU time in a windowed run by Claude Code (TEST-REPORT).
- **Texture sources and licences (or model, version, and terms):** both textures are written by
  code in this repository (`godot/effects/make_textures.gd`): `hit_spark_star.png` and
  `embers_soft.png`. No sourced image and no generative model.
- **Final film URL and filename:** TO DO
- **Final film SHA-256:** TO DO
- **Summary of my work:** I chose the two effects and their jobs, wrote the A6 brief's intent,
  settings, rules, predictions, budgets and short answers, and revised them after Claude's review.
  I decided the CLAUDE.md questions, rule 6's test setup, the star texture fix and rule 4's
  revision. I ran every frame-strip capture, gave the first looks, made both config mutations,
  approved and judged both tuning revisions (embers alpha; spark minimum speed), generated the
  process shader in the editor and wrote its line references and answer, and ran the game for the
  in-play check. Claude Code and its `claude -p` sessions wrote CLAUDE.md, the effect scenes,
  controllers, previews, tests and cost script, the strip readings and predictions, and the
  documents' drafts; I delegated the later agent steps to it (SOURCES.md has the full split).
- **Results (fresh clone of `840bcfd`, `--import`, every suite through `scripts/run-test.sh`):**
  `test_hit_spark_config` 69 / 0, `test_hit_spark_state` 57 / 0, `test_embers_config` 85 / 0,
  `test_embers_state` 38 / 0, `cost_effects` 24 / 0 (all at 60); earlier suites `test_runner`
  94 / 0, `test_hurt_flash` 69 / 0 at 30, 60 and 144, `check_props3d` 49 / 0, `test_materials`
  96 / 0, `calibrate_normal_map` PASS. No log has SHADER ERROR or SCRIPT ERROR. Both config
  mutations exit 1.
- **Known limitations:** headless runs see node state, not particles; the all-four-busy fallback was
  never reached in a test; rules 6 (round reset) and 4 (hidden) are checked only with labelled test
  setup; the spark has no impact direction (`spread` 180°); the CPU→GPU conversion for Step 6
  dropped the colour ramp and scale curve, so those two line references are missing; the GPU price
  is not from the Visual Profiler (it read 0); the in-play human check was reported in one sentence;
  no FPS comparison with vsync off.
- **Changed games since Assignment 2:** no.
