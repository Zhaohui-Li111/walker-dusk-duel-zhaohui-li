All five runs pass, and none of the logs contains a SHADER ERROR or SCRIPT ERROR. The hurt-flash test now has 69 checks, 0 failed, at all three frame rates. Nothing is committed.

## Final lines of each run

**`test_hurt_flash.gd 30`**
```
PASS [5] no tail: hurt_amount 0.0 on all 32 ticks and 15 frames from the K.O. tick on (max 0.0000, 0.0000)

== rule 6 over all scenarios ==
PASS [6] P1's hurt_amount was 0.0 on all 421 frames and 842 ticks recorded, while P2 flashed on 79 frames (max P1 0.0000)
69 checks, 0 failed
WARNING: 8 ObjectDB instances were leaked at exit (run with `--verbose` for details).
   at: cleanup (core/object/object.cpp:2536)
ERROR: 4 resources still in use at exit (run with --verbose for details).
   at: clear (core/io/resource.cpp:822)
```
**`test_hurt_flash.gd 60`** and **`144`**: both end `69 checks, 0 failed`, followed by the same leak WARNING and ERROR lines.
**`test_runner.gd 60`**: `94 checks, 0 failed`, then `WARNING: 66 ObjectDB instances were leaked…` and `ERROR: 10 resources still in use at exit…`
**`check_props3d.gd 60`**: `49 checks, 0 failed`

The leak lines at exit are Godot's own shutdown messages, not SHADER or SCRIPT errors. `test_runner.gd`, which I did not touch, prints them too.

## Key results per rule
- **Rule 3:** The second hit is applied 13 ticks after punch 1, while P2 is in hurt with stun 10 and hurt_amount 0.5556. On that tick the value is 1.0 with stun 18. On ticks T2+1 to T2+17 it equals stun / 18. At T2+18 P2 is idle and the value is 0.0. The output prints why there is no 4-tick hold (hitstop is set only by `attack_resolved`, `main.gd:137-138`). This is the same at 30, 60 and 144 fps.
- **Rule 5, mid-fade (new case):** On the tick before, P2 is in hurt at 0.5556. On the K.O. tick it is in `ko` at 0.0, and it stays 0.0 on all 32 later ticks and every frame. The K.O.-from-idle case is unchanged and passes.
- **Rule 4, time scale:** The expected real time is now 0.367 s with the same per-fps tolerance, and the output prints the reason. Measured: 11 frames at 30 fps (0.3667 s), 22 at 60 (0.3667 s), 53 at 144 (0.3681 s, within ± 0.0069). The tick assertion and the ticks-per-frame check are unchanged.

## What changed and why
- **Where the second hit is applied.** A small `SetupHit` node calls `P2.receive_hit(P1, 8)` and then `P2.flush_ko()` inside a physics tick. It runs at priority 50, after `main` (0) and before the driver (100), which is where `check_hit()` calls them. If I had called them between frames instead, the next tick would lower stun to 17 before the driver read it, so "1.0 on that tick" could never be observed. Because the call happens after `main` has stepped, the SETUP line prints "stun 9", while the trace shows stun 10 on T2−1.
- **Removed checks.** Replacing punch 2 removed the old check "punch 2 (J pressed once P1 was back in idle) connects", since punch 2 no longer exists. Three harness checks were added: punch 1 hit, P2 is mid-fade, and the SETUP call ran inside a tick. The rule 3 end check changed from 22 to 18 ticks, as Revision 7 says. No other assertion changed. The test still never calls the driver or `main.step()`.
- **Files.** Only `godot/tests/test_hurt_flash.gd` was edited. The wrapper rewrote `logs/test_hurt_flash_{30,60,144}fps.log` and `logs/test_runner_60fps.log` during the runs. `blender/prop_taiko.blend` was already modified before this task. Neither the logs nor the `.blend` file should go into a commit for this change.

The full diff is in the `git diff` output above. In short: the header comment, the `SetupHit` class, a rewritten `scenario_retrigger`, the new `scenario_ko_mid_fade`, the helper `second_hit_in_hurt()`, the rule 4 `want` line plus its printed reason, and clearing the queued SETUP call in `end_fight()`.