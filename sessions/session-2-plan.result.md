Running Godot needs approval, so I won't retry. Here is the plan. The retrigger question below comes from my own hand arithmetic, not from a run; the probe I wrote can settle it once you approve it.

## Shader check (read only)

`godot/shaders/hurt_flash.gdshader` matches the brief:
- `canvas_item` with no `render_mode` (Revision 3).
- `hurt_amount : hint_range(0.0, 1.0) = 0.0`.
- `flash_color : source_color = vec4(1,0,0,1)`.
- Your colour line, which leaves `COLOR.a` untouched.

I found nothing wrong with it and won't touch it.

## One problem first: rule 3 (retrigger) may almost never happen in this game

Rule 3 says a second hit during hurt restarts the flash. Counting physics ticks from `fighter.gd` and `main.gd`, with T as the tick of the first hit:

- **The defender leaves hurt at T+22.** That's 4 hitstop ticks plus 18 stun ticks.
- **The attacker is slower.** If a punch connects on its first active frame (frame 5), it recovers at T+17. A new press at T+18 connects at T+23, one tick after the defender is already back in idle.
- **The narrow case.** A retrigger only happens if the first punch connects on active frame 7 or 8, for example when the defender walks into it late. Kicks never retrigger: the second kick lands at T+29 or later.
- **The narrow case probably fails too.** If the first hit only just grazes the hurtbox, `HIT_PUSH` then moves the defender about 11 px away. The second punch probably whiffs, unless the defender is pinned against the arena wall.

So a retrigger that goes only through real input and the real loop may be impossible or need a very specific setup. I can't change fight timing (out of scope). Step 0 decides how to proceed:

- **Step 0 (needs your approval to run Godot): run the probe.** It's a throwaway script, `C:\Users\ROCKEF~1\AppData\Local\Temp\claude\D--courses-7270-walker-dusk-duel-zhaohui-li\d20f3775-787d-41a6-88c9-753837607124\scratchpad\probe_retrigger.gd`, and touches nothing in the repo. It tries every combination of start distance, defender walking or standing, mid-stage or wall, punch or kick, and the timing of the second press.
  - **If it finds a case**, the test uses that setup.
  - **If it finds none**, I'd report rule 3 as unreachable through real input. Your options would then be:
    - (a) Check rule 3 with the real loop, but put the defender back in range between the two hits. That's test setup, not input.
    - (b) Revise the rule with a dated brief entry.

## Step 1: material and driver (one new file, a one-line scene change)

- **New `godot/fighter/hurt_flash.gd`**, a `Node` that is a child of `Sprite2D` in `fighter.tscn`. That's one node added to the scene, and `fighter.gd` is not edited.
  - In `_ready()` it creates its own `ShaderMaterial` with `load("res://shaders/hurt_flash.gdshader")` and sets it as the sprite's `material`. Each fighter instance builds its own, so the two are never shared (rule 6).
  - In `_physics_process` it sets `hurt_amount = float(f.stun) / float(Fighter.HITSTUN) if f.state == "hurt" else 0.0`. It only reads `state` and `stun` and never writes game state.
  - `process_physics_priority` is set high so it runs after `main._physics_process` steps the fighters. Values on the same tick are then current.
  - Pause and hitstop need no code: `stun` is frozen, so the value is frozen too (rule 4).
- **`flash_color` is never set from code.** It keeps the shader default.

This answers the open question in CLAUDE.md about where the driver lives: a separate node, with no game logic in `fighter.gd`.

## Step 2: new test `godot/tests/test_hurt_flash.gd`

**Uniforms and material wiring, asserted on the material each fighter actually has:**

| Assertion | Rule |
|---|---|
| `get_shader_uniform_list()` gives exactly `hurt_amount: TYPE_FLOAT` and `flash_color: TYPE_COLOR` (`vec4` with `source_color` shows as COLOR), and the list is not empty, which shows the shader parses | parse, names, types |
| The shader source text contains `hint_range(0.0, 1.0) = 0.0` and `source_color = vec4(1.0, 0.0, 0.0, 1.0)` | defaults |
| The P1 and P2 materials are different objects and both use `res://shaders/hurt_flash.gdshader` | 6 (wiring) |

**Behaviour, through the real loop:**
- The test calls `change_scene_to_file("res://game/main.tscn")` and lets `_physics_process` run at the wrapper's `--fixed-fps`.
- P1 is driven by `Input.parse_input_event(InputEventKey J)` and its release, through the real `PlayerController`.
- P2's controller is set to null, so it stands as a dummy.
- A sampler node with `process_priority = 1000` reads both materials in `_process` every frame and records the physics tick (`Engine.get_physics_frames()`) and the real time.

| Assertion | Rule |
|---|---|
| P2's value is 1.0 on the tick it enters hurt, and 0.0 on the tick it returns to idle | 1 |
| Held at 1.0 for 4 ticks, then falls 1/18 per tick, 0.0 at tick 22; ≈0.367 s ± one frame period, at 30, 60 and 144 fps | 2 |
| A second hit during hurt goes back to 1.0 and the 22 ticks start over (setup depends on step 0) | 3 |
| A hit that K.O.s goes straight to `"ko"` and the value is 0.0 on that tick (P2 health set low first) | 5 |
| With `Engine.time_scale = 0.5`, the fade lasts about 0.733 s of real time. With `main.set_paused(true)`, the value is the same across many frames and continues from there after resume | 4 |
| P1's value stays 0.0 on every sampled frame while P2 flashes | 6 |

**Runs:** the existing `test_runner.gd` and `check_props3d.gd` at 60, and `test_hurt_flash.gd` at 30, 60 and 144, all through `scripts/run-test.sh`, with full output.

## What headless proves and what it doesn't

**It proves:**
- The shader parses.
- The uniform names and types, and the defaults as written in the source.
- Each fighter has its own material.
- The uniform value over time follows rules 1–6 at three frame rates.

**It cannot prove:**
- Any pixel colour, because the dummy renderer draws nothing.
- That the GPU blends as predicted.
- That the flash reads well in play.
- Whether `hint_range` clamps a value of 2.0 (your Q7). Reading the value back from the material doesn't show what the GPU uses.

**Human checks (windowed):**
1. Captures at `hurt_amount` 0, 0.5 and 1.0. Sample P-gi near (449, 515) and P-fist near (495, 449) against your table, ± 1. Confirm or correct those texel coordinates.
2. A capture where only P2 is hit, to confirm visually that P1 doesn't flash.
3. A capture at `hurt_amount = 2.0` for Q7.
4. A muted playtest with several hits each way, to decide failure case 8 (is Akaken's flash readable?).

Which do you approve: step 0 (running Godot for the probe), or straight to step 1?