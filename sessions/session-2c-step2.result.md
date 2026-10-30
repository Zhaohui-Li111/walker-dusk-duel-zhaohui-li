## Stopped at 30 fps: 4 of 58 checks failed

I wrote `godot/tests/test_hurt_flash.gd` and ran it at 30 fps. Two spec rules fail, so I stopped as you asked: I did not run the 60 and 144 fps tests or the existing tests at 60. Nothing is committed, and no existing file or `.gdshader` was touched. The only new files are the test and the wrapper's log, `logs/test_hurt_flash_30fps.log`. Godot made no `.uid` for the test.

Final run: `58 checks, 4 failed`, exit 1. There are no `SHADER ERROR` or `SCRIPT ERROR` lines. At exit Godot printed `12 ObjectDB instances were leaked` and `6 resources still in use`; the wrapper doesn't count these as failures.

**I re-ran 30 fps twice, because of a bug in my test.** The first run read 40 fps from the first frames' delta (0.025 s). But it ran exactly 2 ticks per frame, which is 30 fps. That wrong value caused a false FAIL on rule 2's real-time check. Godot removes `--fixed-fps` from the script's arguments, so the test now reads the delta after 10 frames (0.033333 s). A new harness check confirms 2.000 ticks per frame. No assertion changed. All 3 runs printed the same rule 3 and time-scale failures.

### What fails

**1. Rule 4, time scale** — `FAIL [4] real time at time_scale 0.5: 11 frames / 30 fps = 0.3667 s, want 0.733`
- Under `Engine.time_scale = 0.5`, Godot 4.7.2 still ran 2 physics ticks per frame. It only scaled the delta, so the flash still lasted 22 ticks = 11 frames.
- The prediction in the brief (0.733 s of real time) is wrong for this engine under `--fixed-fps`. Without `--fixed-fps` it might behave differently; I can't test that headlessly.
- Game time is correct: 22 ticks = 0.367 s (PASS).

**2. Rule 3, retrigger** — 3 FAILs
- With the revision 6 setup, punch 2 still connects at T1+24, after hurt ended at T1+22.
- Moving the defender back into range can't make a retrigger happen. The limit is the attacker's recovery, not distance: P1 is idle at T+17, and the earliest second punch connects at T+23, one tick after P2 leaves hurt at T+22. At 30 fps the second press lands one tick later still.
- So the setup revision 6 allows can't satisfy revision 6's rule 3. Changing it (other setup, another case, or a further revision) is your decision.

### Which rule each assertion covers (at 30 fps)

| Label | What it checks | Result |
|---|---|---|
| parse | `get_shader_uniform_list()` on each fighter's own material is not empty (2 entries) | PASS |
| names/types | Exactly `hurt_amount` (float, range hint 0..1) and `flash_color` (Color) | PASS |
| defaults, brief | Read from the shader source text: both default values, the colour line, nothing assigns `COLOR` or `COLOR.a`, no `render_mode` | PASS |
| wiring | Each sprite's material uses `res://shaders/hurt_flash.gdshader`, with the file's code | PASS |
| 1 | 0.0 on the tick before the hit, 1.0 on the hit tick, 0.0 on the tick P2 leaves hurt (T+22) | PASS |
| 2 | 1.0 on ticks T..T+4, then down exactly 1/18 per tick | PASS |
| 2 | Game time 22 ticks / 60 = 0.367 s *(ticks)* | PASS |
| 2 | Real time 11 frames / 30 = 0.367 s ± 0.033 *(frames)* | PASS |
| 4, pause | P key pauses the fight; value frozen at 0.5556 for 46 ticks / 23 frames; resumes at 0.5000; 22 running ticks | PASS |
| 4, time scale | 22 ticks *(ticks)* | PASS |
| 4, time scale | 0.733 s real *(frames)* | **FAIL** |
| 3 | Punch 2 connects | PASS |
| 3 | Punch 2 lands during hurt; value back to 1.0; 22 ticks restart | **FAIL ×3** |
| 5 | Value 0.0 on the K.O. tick; P2 never in hurt; no flash on any tick or frame | PASS |
| 6 | P1 and P2 have different material instances | PASS |
| 6 | P1's value 0.0 on all 354 frames and 708 ticks while P2 flashed | PASS |
| sampling | Every frame sample equals the value set on that frame's last tick | PASS |

**How the test drives the fight:**
- `main._physics_process` stays on. Every action is a key event: Enter on the title, D to walk in, J to punch, P to pause.
- `Sampler` uses `process_priority = 1000` and records the frame, tick and value every frame. `TickLog` uses `process_physics_priority = 1000`, after main and the driver.
- The only setups are revision 6's two, printed as `SETUP (not input)`: P2 moved back into range (rule 3) and P2's health set to 5 (rule 5). `Engine.time_scale` is printed as `CONDITION`.
- **One thing for you to judge:** when each round starts, the test sets P2's controller to null so Aotake stands still. It's printed as `HARNESS`, and your approved plan had it. It writes no state, stun, health or position, but it does replace P2's controller.

### What headless proves and what it can't

**Proves:**
- The shader parses, and the names, types and defaults are as in the brief.
- Each fighter has its own material.
- The value over ticks and frames, at 30 fps only so far.

**Cannot prove:**
- Any pixel colour, or that the GPU blends as predicted.
- Whether `hint_range` clamps 2.0 (your Q7).
- How time scale behaves without `--fixed-fps`.
- The hurt → K.O. mid-fade case of rule 5, which is unreachable for the same reason as rule 3.
- Results at 60 and 144 fps, which I haven't run.

**Human checks still needed:**
1. Windowed captures at `hurt_amount` 0, 0.5 and 1.0. Compare P-gi (≈449, 515) and P-fist (≈495, 449) with your table, and confirm or correct those texel coordinates.
2. A capture with only P2 hit.
3. A capture at `hurt_amount = 2.0` for Q7.
4. A muted playtest, to decide failure case 8 (does Akaken's flash read?).
5. Whether time scale slows the flash in a normal windowed run.

To finish step 2, I need your decision on rule 3 and on the time-scale prediction for rule 4. After that I'd run 60, 144 and the two existing tests.