Plan only. I haven't changed anything in the repo. I wrote one probe script in the scratchpad, but permissions blocked running Godot directly, so I learned nothing from it.

## Point 0: the feedback-loop rule doesn't apply
Effect B is ambience. Its condition is a single yes/no (`phase == "fight"`), so there's no game value to scale, and `CPUParticles2D` has no `amount_ratio` (CLAUDE.md lists it as absent). The test won't touch `amount_ratio` and won't add any amount control. It will only check that `amount` stays 48 the whole time, as a guard.

## Step 1: controller code (2 files)
**New `godot/effects/embers_controller.gd`** (`Node`, about 25 lines). It reads state and writes nothing except the Embers node's `emitting` and `speed_scale`:
- `process_physics_priority = 10`, the same as `hit_spark_pool.gd`. This makes it run after `main.step()`, so it sees the current tick's `phase` and `hitstop`.
- **Every physics tick**, it polls `main.phase` (your decision for CLAUDE.md). It changes `emitting` only when the phase crosses into or out of `"fight"`. Leaving the fight it only sets `emitting = false`, with no `restart()`, so existing particles fade out on their own (rule 1).
- **Every tick**, and also on `paused_changed`: `speed_scale = 0 if main.paused or main.hitstop > 0 else 1` (rule 2 and the settings table).
- It never touches `visible` or `process_mode`. The tscn already has `process_mode = 0` (INHERIT, rule 3).

**`godot/game/main.tscn`** gains an `Embers` instance (embers.tscn) and an `EmbersController` node. `main.gd` is not edited.

**Two decisions for you:**
1. **Draw order.** I recommend putting Embers right after `Stage` and before `P1`, so it draws behind the fighters (the brief says it "doesn't compete with the fighters"). The other option is after `Effects`, which draws it on top of them.
2. **How to start on entering the fight (affects Q3).**
   - (a) Set `emitting = true` exactly as rule 1 says.
   - (b) Call `restart()`, which also turns `emitting` on.

   From memory of the Godot source, and not verified: `preprocess` only runs while the internal time is still 0. Round 1 would get the preprocess either way. From round 2 on, (a) might not run it again, so the field would start empty. (b) resets the time, and it erases no leftover particles: there are always at least 2.5 s between a K.O. and the next fight (K.O. 1.5 s + the result screen + intro 1 s). Headless can't see whether preprocess actually ran, so either way the frame strip has to settle it.

## Step 2: new `godot/tests/test_embers_state.gd`
This follows the pattern of `test_hit_spark_state.gd`: physics stays on, P1 is driven by key events, and P2's controller is set to null and logged as HARNESS. A TickLog records each tick, and a Sampler records each frame: `phase`, `paused`, `hitstop`, and Embers' `emitting`, `speed_scale`, `visible`, `can_process()`, `is_processing_internal()` and `amount`. The test never calls the controller.

| Scenario | How it's driven | Assertion | Rule |
|---|---|---|---|
| A: load → title → intro | 30 ticks, Enter | `emitting` is false on every title and intro tick | 1, 5 (node state only) |
| A, continued | intro → fight | `emitting` turns true on the exact tick `phase` becomes `"fight"` | 1 |
| B: pause | P, held 40 ticks, P | `speed_scale == 0` on every paused tick and frame, back to 1 after; `emitting` stays true | 2 |
| B: hitstop | D to walk in, J to punch | `speed_scale == 0` on every tick with `hitstop > 0`, 1 on all others | settings table |
| C: K.O. → result → Enter → intro → fight | D + J repeated until K.O., then Enter | `emitting` turns false on the tick the phase becomes `"ko"`; false through ko, result and intro; true again on the next fight's first tick | 1, predicted failure 4 |
| D: tree pause | **SETUP** `get_tree().paused = true` for 60 ticks. No game input does this, so the log says so. | `process_mode == INHERIT`; `can_process()` is false while paused and true after; the controller doesn't run, so `emitting` and `speed_scale` don't change | 3 |
| E: hidden | **SETUP** `Embers.visible = false`, also through a K.O. | `can_process()` and `emitting` stay true while hidden; when the phase leaves the fight, `emitting` still turns false (`visible` is not a switch) | 4 |
| All scenarios | — | `amount == 48` on every tick | point 0 |

**Possible extra check (I'd like to try it during step 2).** After `emitting` goes false, `is_processing_internal()` may turn false once the last particles are gone. If so, that gives a clock headless can read:
- C: does it stay on for about 2.5 s after the stop? That would mean the particles weren't cleared early.
- D and B: are those seconds delayed by the paused time?
- E: is it **not** delayed while hidden? That would show the simulation keeps aging particles while hidden.

I couldn't check that this signal behaves this way. If it doesn't, I'll only print the observation, not assert on it, and tell you.

After writing it, I'll run the new test once with `./scripts/run-test.sh test_embers_state.gd 60`. It doesn't wait on audio, so it doesn't need realtime. Then I'll run all the existing tests as CLAUDE.md lists them, including `test_hit_spark_state` and both config tests, to confirm their counts don't change.

## What headless can't prove (a person has to check)
- Whether the field is already populated at frame 10, i.e. whether preprocess ran (Q3, predicted failure 5).
- Colour after the two ramps multiply (Q5), contrast against the background, 1–3 px particle size, whether the drift looks too uniform (like a conveyor belt), and whether embers clear within 2.5 s after the stop.
- Whether particles actually stop on screen while frozen, and what shows when the node becomes visible again (Q4). The test only sees node state, not particles.

Shall I start step 1? If so, please choose the draw order and (a) or (b).