I've stopped: Effect B's hidden rule (rule 4) appears not to hold in Godot 4.7.2. The code and test are written; nothing is committed. Following your instruction, I did not run the remaining tests on your list. Godot never ran outside the wrapper.

## Step 1: controller
`main.tscn` diff, shown in full earlier:
- Two `ext_resource` lines for `embers.tscn` and `embers_controller.gd`; `load_steps` goes from 9 to 11.
- `[node name="Embers" parent="." instance=ExtResource("9_embers")]` sits right after `Stage` and before `P1`, so it draws behind the fighters.
- `[node name="EmbersController" type="Node" parent="."]` sits after `HitSparkPool`.

New file `godot/effects/embers_controller.gd`:
- Runs after `main` each physics tick and reads `main.phase` every tick.
- On entering `"fight"` it calls `restart()`. A code comment says this departs from rule 1's wording ("emitting = true") and why: so preprocess runs every round. It's marked as Claude Code's choice under your delegation.
- On leaving `"fight"` it only sets `emitting = false`.
- Every tick: `speed_scale = 0 if main.paused or main.hitstop > 0 else 1`.
- It never touches `visible`, `process_mode` or `amount`, and writes no game state. `main.gd` is unchanged.

Step 1 runs, all at 60 fps through the wrapper:
- `test_embers_config.gd 60`: **85 checks, 0 failed**
- `test_hit_spark_state.gd 60`: **57 checks, 0 failed**
- `test_runner.gd 60`: **94 checks, 0 failed**, plus `ERROR: 8 resources still in use at exit`. The committed log already has the same kind of line (10 then), and the wrapper doesn't count it as a failure.

## Step 2: `godot/tests/test_embers_state.gd`
`./scripts/run-test.sh test_embers_state.gd 60` (fixed 60 fps, no audio wait): **36 checks, 0 failed.** Full output is above and in `logs/test_embers_state_60fps.log`.

Rules the run's assertions cover, all driven by real input (Enter / P / D / J) through the real loop:
- **Rules 1 and 5:**
  - Not emitting on any title or intro tick.
  - Emitting turns on on the first `"fight"` tick (tick 103) and off on the first `"ko"` tick.
  - After Enter on the result screen, it turns on again on round 2's first fight tick.
  - Over the whole run, `emitting == (phase == "fight")` on every tick.
- **Rule 2 and hitstop:** `speed_scale` is 0 on every paused tick and frame and on all 52 hitstop ticks, and 1 on every other tick.
- **Rule 3:** the test sets `get_tree().paused` itself (labelled SETUP). While paused, neither Embers nor its controller can process, and `emitting` and `speed_scale` don't change.
- **`amount`** stays 48 on every tick. Effect B has no feedback loop and `CPUParticles2D` has no `amount_ratio`, so that requirement doesn't apply.

## The problem: rule 4 (Q4)
This is the observation you asked to be printed but not asserted: the number of ticks from the stop until `is_processing_internal()` turns false.

| Case | Ticks | Reading |
|---|---|---|
| C: plain stop | 153 | 150 (the 2.5 s lifetime) + the 4-tick K.O. hitstop at `speed_scale` 0 − 1 |
| E: tree paused 60 ticks during the fade | 215 | 153 + 60 + 2: tree pause stops the particle clock (rule 3 holds) |
| F: hidden for the whole fade | never, within 600 ticks | |

C and E fit "this flag tracks particle lifetime" closely. On that reading, F means **while `visible = false`, the particles stop aging**. That contradicts rule 4 ("keeps emitting and simulating, particles continue aging") and Short answer 5. I recall (not checked) that `CPUParticles2D`'s update returns early when the node isn't visible in the tree, which would explain it.

The test's rule-4 PASS line is weaker than it looks. It only shows that `emitting`, `can_process()` and `is_processing_internal()` stay true while hidden. That doesn't mean the particles are simulating, and it shouldn't count as evidence for rule 4.

## What headless can and can't prove
- **Can:** node state on every tick and frame (emitting, speed, visibility, process flags), and the internal-processing observation above.
- **Can't:**
  - Particle positions or count.
  - Whether `restart()` + preprocess actually fills the field at frame 10 (Q3).
  - Colour after the two ramps (Q5), contrast, size and drift.
  - What actually shows when the node is made visible again (Q4 visually).

  These need the frame strip and you looking at the running game.

## Not run
`test_hit_spark_config 60`, `test_hurt_flash 30/60/144`, `check_props3d 60`, `test_materials 60`, `calibrate_normal_map 60`, and a second run of `test_embers_config` after Step 2.

## Your decision
Rule 4 and Short answer 5 are yours to revise, in a dated revision (or check first with a windowed run). Then I can:
1. Change the test's rule-4 assertion to match the revised rule, for example asserting on this observation, and add a measurement of how many ticks it takes to finish fading after the node is shown again.
2. Run all the remaining tests.

The controller doesn't need to change for this. Nothing is committed.