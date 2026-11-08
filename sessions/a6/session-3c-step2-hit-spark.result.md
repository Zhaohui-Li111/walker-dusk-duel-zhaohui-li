Step 2 is done: the new state test `godot/tests/test_hit_spark_state.gd` passes with **57 checks, 0 failed**. It found no brief rule the trigger code misses. The trigger code and the effect's settings are unchanged, and nothing is committed.

Mode: every run went through `./scripts/run-test.sh` as its own command, at fixed fps (`--fixed-fps`). The new test runs at 60 because it doesn't wait on audio.

## Results

| Command | Result |
|---|---|
| `test_hit_spark_state.gd 60` (new) | **57 / 0** |
| `test_hit_spark_config.gd 60` | 69 / 0 |
| `test_runner.gd 60` | 94 / 0 |
| `test_hurt_flash.gd 30` / `60` / `144` | 69 / 0 each |
| `check_props3d.gd 60` | 49 / 0 |
| `test_materials.gd 60` | 96 / 0 |
| `calibrate_normal_map.gd 60` | `PASS: each file scores lower in its own convention` |

Every count matches the numbers in `CLAUDE.md`. The full output of each run is above.

Several runs end with "N ObjectDB instances were leaked at exit" and "N resources still in use". That comes from Godot at exit, not from the checks, and does not change the exit code. For `test_runner` and `test_hurt_flash` at 30 fps the lines are the same as in the committed logs. At 144 fps the committed log ends without them; this run adds 12 / 6. I did not look into the cause.

## What each scenario showed

- **A, scene load → title → intro → fight:** no slot emitted on any of 121 ticks (rule 1). There are 4 slots, all children of `Main`, 80 particles in all, and none under P1 or P2 (rules 3, 4).
- **B, one punch (input only):**
  - One slot fired, on the hit tick, at exactly the hit point (rules 1, 2).
  - The slot stayed there while Aotake was pushed back 10.7 px (rule 4).
  - Emitting went false 39 ticks after the hit: the 36-tick lifetime plus 3–4 ticks held by hitstop (rule 5).
- **C, two punches 23 ticks apart, Aotake against the wall:**
  - The second hit used slot 1. Slot 0 kept emitting at its own point the whole time (rule 3).
  - Slot 0 stopped at T2+20, before slot 1 at T2+39. A restart would have pushed it past T2+36.
- **D, a full round against the game's own CPU:**
  - 16 fires for 16 hits (13 by P1, 3 by P2), each on its hit tick and at its point.
  - Zero fires on the 31 other results: 18 blocked, 9 whiff, 4 interrupted.
  - After pressing Enter on the result screen, nothing was emitting on the `round_started` tick and nothing fired during the intro. This only shows the real path; the last burst had ended 90 ticks earlier.
- **E, P pressed for 44 ticks:** `speed_scale` was 0 on every paused tick and every paused frame. The burst lasted 83 ticks, which is the 39 from B plus the 44 paused, so its clock really stopped (rule 5).
- **F, SETUP `main.start_fight_now()` 11 ticks into a burst:** every slot stopped emitting on that tick and nothing fired for the next 46 ticks. The next hit fired normally (rule 6).
- **Every scenario:** `speed_scale` was 0 on every tick with `paused` or `hitstop > 0` and 1 on every other tick. Freeing `Main` freed all 4 slots.

## Things the test found but does not assert

- **4.7.2 behaviour:** `CPUParticles2D` has a `finished` signal. A one-shot burst turns `emitting` false on its own when its lifetime ends, and `finished` arrives on the same tick.
- **Signal noise:** all 4 slots send `finished` once when the scene loads, and again 35 ticks after a round reset. Neither causes a wrong trigger.
- **Possible weak spot in rule 3:** the pool marks a slot free when `finished` arrives. So a hit within 35 ticks of a round reset could start a burst that the late `finished` then marks free, and a later hit could restart it. In real play the 60-tick intro has no hits, so I don't count this as a broken rule and left the code unchanged. Freeing slots when `emitting` goes false instead would remove it; that's your call.
- **The all-four-busy fallback never happened** in any scenario, so it is still untested. Each scenario prints this.

## What a headless run cannot prove

It sees node state, not particles. The dummy renderer draws nothing, and `CPUParticles2D` has no count of live particles. So it cannot show:
- how the burst looks
- the actual spread (question 1)
- whether a burst spawns while `speed_scale` is 0 (question 2)
- draw order

Those need a human:
- the frame strip, including frame 22 with two bursts at once
- checking the look in the running game against both the dark area and the lantern
- GPU time in the Visual Profiler