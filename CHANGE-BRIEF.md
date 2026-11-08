# CHANGE-BRIEF — Assignment 6: particle effects

> **Version 1 · DRAFT · 2026-11-08.** This file replaces the A5 brief, which stays in history at
> tag `a5`. Zhaohui chose the two effects: **Effect A, a hit spark**, and **Effect B, courtyard
> embers/dust (ambience)**. Claude Code drafted the structure and filled in the **project facts**
> only (file references, measured hit heights, background luminance, which properties exist in
> Godot 4.7.2). The intent, every setting value, the rules' choices, every prediction, the budgets
> and the short answers are Zhaohui's. Commit this section before the first prompt. After that it
> is only appended to, with dated revisions.
>
> **Authorship (2026-11-08).** Zhaohui wrote the effect sections in two passes: a draft file
> (asked whether it was written with another AI, Zhaohui answered "I wrote it"), then corrections
> pasted in chat after Claude Code's review, in two rounds. The second round (spark speed and
> damping, the price predictions and budgets, the hidden rule) was asked about the same way;
> Zhaohui answered: "I wrote it myself". A third round (rotation ranges, Effect B's start colours,
> the exact ramp, curve, rect and position values, Q1, and revised price predictions) was pasted
> in chat the same way and was not asked about separately. Claude Code copied all of it in,
> translated one Chinese passage (original kept), and made factual and consistency edits, each
> marked inline as Claude Code's. Questions the build must answer are listed under
> "Unconfirmed"; they are not decisions.

## Project facts both effects depend on (Claude Code, checked 2026-11-08)

- **Engine and renderer:** Godot 4.7.2 stable, GL Compatibility (`godot/project.godot:35-36`).
  Viewport 640 × 360, window 1280 × 720, `canvas_items` stretch (`godot/project.godot:23-27`).
- **The game steps itself.** `main.gd` advances the fight in `step()` once per physics tick
  (`godot/game/main.gd:51-58`). The game's pause (`main.paused`, Esc / P) and the 4-tick hitstop
  only skip `step()` (`:56-57`, `:60-62`); **the scene tree is never paused** (`set_paused`,
  `:105-116`). Particle nodes advance on the engine's own clock, so a particle node keeps moving
  during the game's pause and hitstop unless the effect code changes its `speed_scale`.
- **Phases** (`main.gd:3-4`, `:25`): `"title"` → `"intro"` → `"fight"` → `"ko"` → `"result"`.
  `start_round()` resets both fighters, calls `effects.clear()` and emits `round_started`
  (`:90-102`; the signal is declared at `:9`).
- **Nothing is freed during play.** No `queue_free()` or `free()` exists in `godot/game/` or
  `godot/fighter/`; the fighters and `Effects` live for the whole scene (`godot/game/main.tscn`).
- **Existing code-drawn feedback.** `godot/game/effects.gd` already draws a white 8-line hit spark
  (10 ticks) at the same event (`:31-35`), spawned from `main.gd:133-136`. It is out of scope
  (`CLAUDE.md`, Out of scope).
- **Scale.** Akaken stands 112 px and Aotake 124 px in the 640 × 360 viewport
  (`CHARACTER-SHEET.md:8`, `:94`), so 224 px and 248 px in the 1280 × 720 window.
- **Property check, Godot 4.7.2 (`ClassDB`, headless probe, 2026-11-08).** `GPUParticles2D` has
  `amount_ratio`, `preprocess`, `local_coords`, `visibility_rect`, `use_fixed_seed`, `seed`,
  `trail_enabled`, `speed_scale`. `CPUParticles2D` has `use_fixed_seed`, `seed`,
  `emission_rect_extents`, `color_ramp`, `scale_amount_min` / `_max` / `_curve`, `damping_min` /
  `_max`, `hue_variation_min`, `angle_min`, but **no `amount_ratio`, `alpha_curve`, `scale_min`,
  `scale_max`, `turbulence_enabled`, `trail_enabled` or `sub_emitter`**. The class
  `ParticlesMaterial` does not exist. **Unexpected:** `ParticleProcessMaterial`'s property list
  also contains `initial_velocity` and `scale` (Godot 3 names). What they do is not known yet.
- **Not yet confirmed:** how the effects look on Compatibility. The first frame strip shows it.

---

## Effect A — hit spark

### The job

- **What it tells the player:** The hit spark provides immediate visual confirmation that an
  attack connected, making the exact contact point and impact strength easier to read. It
  supplements the existing code-drawn spark with a short, brighter burst of particles that
  communicates impact direction and energy.
- **Event:** `Fighter.attack_resolved(fighter, kind, result, point)` with `result == "hit"`
  (`godot/fighter/fighter.gd:19`, emitted in `_resolve()` at `:221-223`, called from
  `check_hit()` at `:172`). `point` is the centre of the hitbox ∩ hurtbox overlap (`:170`), in
  `Main`'s coordinates. `main.gd` already connects to this signal (`main.gd:42-43`, `:133`).
- **Relation to the existing spark:** Keep both. The existing `effects.gd` spark remains the
  immediate hit confirmation; the particle burst adds a second visual layer. This keeps
  `effects.gd` out of scope.

**Facts for the event (Claude Code, headless probe 2026-11-08):**
- **Where hits land.** Hit `point.y` sits between about **224 and 254** in the viewport, i.e.
  50–80 px above the ground line `GROUND_Y = 305` (`fighter.gd:26`): Akaken punch hitbox y
  224.6–236.3, kick 235.3–254.4; Aotake kick 239.1–248.5 (Aotake has no punch hitbox). In a
  3 000-tick CPU run, all 48 hits landed at y 243.8, x 148–227.
- **How often a hit can repeat.** The same attacker lands its next hit **23 ticks (0.383 s) apart
  at the earliest** (A5 probe, `logs/_probe_retrigger_direct.log`). The two fighters can also hit
  each other on consecutive ticks. A K.O. hit emits `"hit"` first, then `knocked_out`
  (`fighter.gd:172-173`).

### The intent block

- **Timing phases:**
  - First frame: a bright, compact flash appears immediately at the hit point.
  - Outward phase: sparks travel outward during approximately the first 0.2 seconds, making the
    impact direction and energy visible.
  - Dissipation: sparks slow down, shrink, and fade over the remainder of the 0.6-second
    lifetime.
- **Contrast:** use a cool white/cyan colour. The hit band is dark on average, but the design must
  remain distinguishable against the warm lantern at L = 0.2699. Approximate contrast for
  `#EAFBFF` is about 13.1:1 *(Claude Code corrected 13.8 → 13.1: L ≈ 0.937, (0.937 + 0.05) /
  (0.0256 + 0.05))* against the band mean and 3.0:1 against the brightest lantern pixel.
- **Scale:** the burst has an overall visual radius of approximately 15–30 px, or about 13–27% of
  Akaken's 112 px height. Individual particles remain small; the larger radius describes the full
  burst footprint rather than the size of a single spark. *(Revised 2026-11-08 from 8–12 px.)*
- **Change over life:** bright at birth, then gradually lower alpha and scale. The colour shifts
  from near-white at birth toward pale cyan before fading.
- **Variation:** randomize initial velocity, scale, and rotation so repeated hits do not look
  identical.
- **Emitters:** four pooled burst slots, each responsible for one independent hit event. Each
  slot emits 20 particles.

### The settings

| Setting | Value | Why |
|---|---|---|
| Node type | `CPUParticles2D` | Chosen CPU implementation |
| `amount` | 20 per slot | Keeps each burst readable |
| `one_shot` | `true` | One burst per hit |
| `explosiveness` | 1.0 | Emits the burst immediately |
| `lifetime` | 0.60 s | Allows two events to overlap |
| Emission shape | Point | Impact originates at the contact point |
| `initial_velocity_min` / `_max` | 45 / 75 px/s *(revised from 75 / 155)* | Gives sparks visible outward motion |
| `spread` | 180° | Full radial spread |
| `gravity` | (0, 25) | Slight downward arc |
| `damping_min` / `_max` | 28 / 40 *(revised from 18 / 32)* | Slows particles during dissipation |
| `angle_min` / `angle_max` | −180° / 180° | Random spark rotation, so repeated bursts look natural |
| `color_ramp` | 0.00 `#EAFBFF` α 1.00; 0.35 `#83DFF2` α 0.75; 1.00 `#83DFF2` α 0.00 | High contrast and clear impact feedback; the last stop keeps the cyan and only fades, so particles do not vanish abruptly |
| Alpha | Defined in `color_ramp` | `CPUParticles2D` has no `alpha_curve` |
| `scale_amount_min` / `_max` | 0.7 / 1.2 | Small variation in spark size |
| `scale_amount_curve` | (0.00, 1.00), (0.70, 0.65), (1.00, 0.00) | Makes particles dissipate |
| Texture | Code-drawn 8 × 8 eight-point star spark, wide at the centre with thin tips | Reads more like an impact spark than a round dot |
| Draw material | `CanvasItemMaterial`, additive blend | Brightens the impact without a solid sprite |
| `local_coords` | `true` | Particles remain in parent-local coordinates |
| `visibility_rect` | Not applicable to this CPU design | GPU-specific visibility configuration is not used |
| `preprocess` | 0 | A hit should appear at the event, not pre-exist |
| `speed_scale` | 0 during game pause/hitstop; 1 otherwise | Scene tree is not paused by the game's custom pause |

Godot property correction (Zhaohui): use `scale_amount_min`, `scale_amount_max` and
`scale_amount_curve`. Put transparency into `color_ramp`; do not configure `alpha_curve`,
`scale_min` or `scale_max`.

### Observable rules

1. **Fires on every hit, never otherwise.** Trigger only when `result == "hit"`; never on scene
   load, `"blocked"`, `"whiff"` or `"interrupted"`.
2. **At the event's position:** spawn at `point`, within 1 px in `Main` coordinates.
3. **Retrigger rule: overlap.** A fixed pool of four one-shot `CPUParticles2D` slots × 20
   particles = 80 particles maximum. A new event uses another available slot rather than
   restarting an active burst. If all four are active, reuse the oldest slot as a bounded
   fallback.
4. **Freed parent:** parent the pooled emitters to the persistent `Main` scene root, not to either
   fighter. If `Main` is freed, its child emitters and their particles are freed with it.
5. **Game pause and hitstop:** set `speed_scale = 0` during both custom pause and hitstop; restore
   it to 1 afterward, because neither state pauses the scene tree.
6. **Round reset:** when `round_started` is emitted, the particle pool is reset by the
   presentation/effects controller. All active burst slots are stopped and cleared before the
   next round begins. This does not require modifying `effects.gd`, which remains out of scope.
   The implementation listens to the round-start signal rather than assuming the particle pool
   lives inside `effects.gd`.

### Evidence split

| Rule | Check |
|---|---|
| Settings | Headless: `test_hit_spark_config.gd` reads every configured property back. |
| 1–6 | Headless tests assert the hit-only signal filter, event position, pool/retrigger behaviour, persistent parent, pause/hitstop freeze and round-reset clearing. |
| Reads as intended | Running-game frame strip and visual inspection at both dark and lantern-lit hit locations. |

### The frame strip

- **Preview background:** the hit band y = 200–260, including the warm lantern crop around
  x ≈ 510, y ≈ 208 and the dark sample around x ≈ 364, y ≈ 202.
- **Triggers:** frame 10, and again at **frame 22**, 0.4 s after frame 10. This is within the
  first burst's 0.6 s lifetime, and it respects the measured 0.383 s earliest repeat interval
  for the same attacker.
- **Frames to read, at 30 fps, and what each should show:**
  - 10: new burst appears.
  - 12: bright outward motion.
  - 15: sparks spread.
  - 20: first burst is slowing and fading.
  - 22: second burst appears while the first is still alive.
  - 24: both bursts are visible.
  - 28: first burst reaches the end of its lifetime.
  - 30: second burst is still dissipating.
  - 40: second burst has disappeared.
  - 50: nothing left (both bursts ended at frames 28 and 40). *(Claude Code added frame 50, which
    the handout's list requires; the expected content follows from the 0.6 s lifetime above.)*


---

## Effect B — courtyard embers / dust (ambience)

### The job

- **What it tells the player:** The courtyard embers and dust establish a quiet, atmospheric
  environment around the fight. Their slow, irregular movement adds depth and a sense of air and
  warmth without competing with the fighters or hit effects.
- **Job:** ambience.
- **Condition:** run only during `phase == "fight"`. Start on entry to `"fight"` and stop emitting
  when the phase changes to `"ko"` or any other non-fight phase.
- **Feature Effect A doesn't use:** a rectangular emission region and non-zero `preprocess`, so
  the ambience begins as an established field. Effect A uses a point emission shape and zero
  preprocess.

### The intent block

- **Timing:**
  - Fade in: individual particles fade in over approximately 0.5 seconds of their own lifetime.
  - Steady state: a preprocessed particle field is already established when the effect becomes
    visible.
  - Fade out: when the fight phase ends, emission stops. Existing particles remain visible and
    fade out naturally, with a maximum remaining lifetime of 2.5 seconds.
  - `preprocess = 1.5` pre-simulates the particle system; it is not the same thing as a
    0.5-second alpha fade. The first visible field can already be populated while individual
    particles still follow their own alpha curves.
- **Contrast:** muted warm amber (`#C58A55`) with low alpha, plus a small number of pale neutral
  dust particles. Keep it subdued against the lantern-lit wall and never brighter than the hit
  spark.
- **Scale against the character:** individual particles about 1–3 px wide in the 640 × 360
  viewport, far below 3% of Akaken's height; avoid large blobs.
- **Change over life:** embers fade in quickly, drift, then fade to zero; dust remains low-alpha
  and shrinks slightly near the end of life.
- **Variation:** randomize position across the rectangular region, slow upward/downward drift,
  horizontal velocity, scale and rotation. Keep velocity low and avoid a uniform conveyor-belt
  appearance.
- **Emitters:** one continuous rectangular emitter is sufficient for this ambience pass. A
  separate emitter is not justified until the single-emitter result is visually evaluated.

### The settings

| Setting | Value | Why |
|---|---|---|
| Node type | `CPUParticles2D` | Consistent CPU implementation |
| `amount` | 48 | Low-density ambience |
| `one_shot` | `false` | Continuous emission during the fight |
| `explosiveness` | 0 | Distributes emission over time |
| `lifetime` | 2.5 s | Sets the maximum remaining life after emission stops |
| Emission shape | Rectangle | Spreads particles across the courtyard |
| `emission_rect_extents` | (280, 90), i.e. a full 560 × 180 px rectangle | Covers the visible arena ambience area |
| Node `position` | (320, 215) | Centres the rectangle so it spans x 40–600, y 125–305: the fighting area, not below the ground |
| `initial_velocity_min` / `_max` | 4 / 14 px/s | Slow, drifting movement |
| `spread` | 180° | Allows movement in varied directions |
| `gravity` | (0, −2) | Slight upward drift |
| `damping_min` / `_max` | 1 / 3 | Keeps movement gentle |
| `angle_min` / `angle_max` | 0° / 360° | Random angle; barely visible on a soft round particle, kept for variation |
| `color_initial_ramp` | `#C58A55` → `#E8C49A` | Each particle starts somewhere between deeper and lighter amber, so they are not identical |
| `color_ramp` | 0.00 `#C58A55` α 0.00; 0.20 `#C58A55` α 0.28; 0.75 `#E8C49A` α 0.20; 1.00 `#E8C49A` α 0.00 | Transparent start, fade-in by 20% of the lifetime (not 0.2 s), slow fade-out |
| Alpha | Defined in `color_ramp` | Includes a per-particle fade-in and fade-out |
| `scale_amount_min` / `_max` | 0.6 / 1.2 | Adds size variation |
| `scale_amount_curve` | (0.00, 0.75), (0.20, 1.00), (1.00, 0.70) | With `scale_amount_min` / `_max` 0.6 / 1.2, sizes differ without abrupt changes |
| Texture | Code-drawn 4 × 4 soft circle/diamond | Subtle dust and ember appearance |
| Draw material | `CanvasItemMaterial`, normal blend | Avoids an overly bright additive field |
| `local_coords` | `false` | Particles remain in world coordinates |
| `preprocess` | 1.5 s | Pre-simulates an established particle field |
| `speed_scale` | 0 during game pause/hitstop; 1 otherwise | Matches the game's custom pause behaviour |

### Observable rules

1. **Starts when the condition begins and stops when it ends.** Set `emitting = true` on entry to
   `"fight"`; on exit set `emitting = false` and let existing particles finish their lifetime
   naturally.
2. **Game pause (`main.paused`):** set `speed_scale = 0` while custom pause is active; restore 1
   when unpaused.
3. **Tree paused (`get_tree().paused`):** use inherited pause behaviour
   (`process_mode = INHERIT`); particles freeze when the scene tree is paused.
4. **Hidden (`visible = false`):** hiding the node only suppresses rendering. It does not
   automatically stop emission or freeze particle simulation. The emitter continues processing
   while hidden, and particles continue aging. When the node becomes visible again, the current
   particle state is rendered. `visible` is not a phase switch; emission is still decided by the
   phase logic in rule 1.
5. **First frame after the scene loads:** the node starts non-emitting because the phase is
   `"title"`, so the first frame is empty either way. On entering `"fight"`, `preprocess = 1.5`
   gives an established field; with preprocess set to 0, particles build up gradually.

**Summary of the three paused/hidden cases (Zhaohui):**

| State | Expected behaviour |
|---|---|
| `main.paused` / hitstop | frozen by `speed_scale = 0` |
| `get_tree().paused` | follows the node's process mode; stops processing while the tree is paused |
| `visible = false` | not drawn, but keeps emitting and simulating |

### Evidence split

Settings: headless configuration test reads back every configured property. Rules: headless
tests cover phase start/stop, pause, tree pause, visibility and initial state. Visual intent:
frame strip plus inspection in the running game.

### The frame strip

- **Preview background:** the wall/sky and lower-wall regions across the arena, including both
  the dark wall sample and the warm lantern region.
- **Condition begins at frame 10 and ends at frame 100.**
- **Frames to read, and what each should show:**
  - 10: the preprocessed ambience field appears populated.
  - 25: particles continue their slow movement.
  - 55: steady-state ambience.
  - 100: fight phase ends and emission stops.
  - 115: existing particles remain and begin clearing out.
  - 145: only a small number of particles remain.
  - 175: the 2.5-second maximum fade-out window has elapsed; no particles remain.

---

## Background where the effects appear (Claude Code, measured 2026-11-08)

Relative luminance L of `godot/art/env/bg.png` (640 × 360, drawn 1:1 by `stage.gd:23`), sampled
every 2 px over the arena x 24–616 (`fighter.gd:27-28`). WCAG decode as in the A5 brief's
Revision 5.

| Band (y) | What it is | Mean L | Darkest (x, y) colour | Lightest (x, y) colour |
|---|---|---:|---|---|
| 0–100 | sky | 0.0434 | 0.0021 (32, 56) `#140209` | 0.2188 (506, 98) `#b1724a` |
| 100–200 | wall, lanterns | 0.0537 | 0.0006 (250, 148) `#070008` | 0.2091 (150, 104) `#af6f45` |
| **200–260** | **where hits land** | **0.0256** | 0.0040 (364, 202) `#1a070d` | **0.2699 (510, 208) `#b18651`** |
| 260–305 | lower wall | 0.0377 | 0.0074 (610, 284) `#1f101b` | 0.2081 (342, 290) `#a9705d` |
| 305–360 | floor | 0.0614 | 0.0037 (602, 329) `#0f0a13` | 0.2027 (324, 323) `#a76f57` |

Zhaohui: the hit band is mostly very dark, so the worst case for a bright spark is the warm
lantern glow, L ≈ 0.27. Using the opaque near-white core `#EAFBFF` (approximate relative
luminance 0.94), the contrast is approximately 13.1:1 *(Claude Code corrected 13.8 → 13.1)*
against the hit-band mean L = 0.0256 and 3.0:1 against the lightest pixel L = 0.2699. The
lantern-lit pixel is the limiting case; judge readability from the bright core and motion, not
from a claim of 4.5:1 compliance.

## Unconfirmed — to be checked by tests or strips (Claude Code, 2026-11-08)

Open questions, not decisions. Each is answered by the named check, and the answer goes in a
dated revision.

1. **Spark reach.** With 45–75 px/s and damping 28–40, d = v·t − ½·a·t² gives about 8–14 px at
   0.2 s and 20–40 px at 0.6 s: the fastest sparks end about 10 px beyond the intended 15–30 px,
   when the ramp and scale curve have nearly faded them. *Check:* Effect A's first strip.
2. **Hitstop starts on the hit tick.** `main.gd:137-138` sets hitstop on the same event that fires
   the spark, so with `speed_scale = 0` during hitstop every in-game burst is held for its first
   4 ticks (0.067 s, 2 frames at 30 fps). Not known: whether a one-shot `CPUParticles2D` spawns
   at all while `speed_scale` is 0. The preview has no hitstop. *Check:* Effect A's state test.
3. **`preprocess` after load.** Not known whether `preprocess` runs when `emitting` turns on after
   the scene has loaded, or only on entering the tree or `restart()`. If the latter, frame 10 of
   Effect B's strip is empty unless the code calls `restart()`. *Check:* Effect B's state test
   or first strip.
4. **Hidden.** Not known whether `CPUParticles2D` in 4.7.2 keeps simulating while
   `visible = false` (rule 4). *Check:* Effect B's state test.
5. **Two colour ramps on Effect B.** As far as Claude Code knows, `CPUParticles2D` multiplies the
   `color_initial_ramp` sample by the `color_ramp` sample, so amber × amber comes out darker than
   either stop (e.g. R 197/255 × 232/255 ≈ 179). Not confirmed for 4.7.2. *Check:* Effect B's
   first strip against the intended `#C58A55`–`#E8C49A` range.

## Boundaries

Unchanged: collision, movement, input, state machine, timings, existing tests and counts, A5
shaders, background, sprites, `effects.gd`, `audio_director.gd` and HUD. Presentation code may
read game state but never writes it. Confirmed; no exception is required.

## Predicted failures

1. **Custom pause/hitstop does not freeze particles.** Test particle positions while toggling
   pause and hitstop; assert `speed_scale == 0` and no movement.
2. **A retrigger restarts and erases an active one-shot burst.** Catch with the frame-22
   retrigger strip and a pool test that asserts two active bursts remain visible. *(Claude Code:
   frame 21 → 22 to match the corrected strip.)*
3. **The burst is parented to a fighter.** Assert the emitter parent is `Main`; move the fighter
   after the hit and verify the burst stays at the event location.
4. **Ambience runs outside the fight or fails to stop after KO.** Test title → fight → ko →
   result and assert the emitter state at each transition.
5. **Preprocess does not establish the expected ambience.** Compare the first active frame with
   and without preprocess in a frame strip.
6. **A Godot 3 property or unsupported renderer feature is used.** Catch with the Godot 4.7.2
   headless configuration read-back test.

## Price predictions and budget

Zhaohui (original): 这里需要特别区分预测和实测。既然作业要求 CPU 粒子也测 GPU time，就不能再写
N/A — CPU node。CPU 节点仍然需要 GPU 绘制，所以 GPU time 必须测。Step 6 可以临时创建一个 GPU 粒子节点
来生成 process shader，但要明确记录：这是为了取得 GPU 对比数据，不代表最终效果改用 GPU 节点。

(Translation: predictions and measurements must be kept apart. Since the assignment asks for GPU
time for CPU particles too, "N/A — CPU node" can no longer be written. A CPU node still needs the
GPU to draw, so GPU time must be measured. Step 6 may create a temporary GPU particle node to
generate the process shader, but the record must say clearly that it is there to obtain the GPU
comparison data, and that the final effects do not switch to GPU nodes.)

| Effect | Peak particles | Predicted headless CPU price | Predicted GPU time | Budget | Compared on |
|---|---|---|---|---|---|
| A | 80 | 0.08 ms / frame | 0.04 ms / frame | CPU ≤ 0.25 ms; GPU ≤ 0.25 ms | Both CPU and GPU |
| B | 48 | 0.05 ms / frame | 0.02 ms / frame | CPU ≤ 0.50 ms; GPU ≤ 0.50 ms | Both CPU and GPU |

*(Revised 2026-11-08 after Claude review P, before any build: A 0.05 / 0.05 → 0.08 / 0.04 ms,
B 0.08 / 0.08 → 0.05 / 0.02 ms. Budgets unchanged.)*

These are pre-implementation estimates, not measured results. The headless CPU estimates
represent particle simulation overhead and may vary by machine. GPU time must be measured in the
Visual Profiler for both CPU particle effects because their particles are still drawn by the GPU.
A temporary GPU particle node may be used to generate and read a GPU process shader as required
by Step 6; it is a scratch node for reading the shader, not a change to the selected CPU
implementation, and the GPU times above are measured on the CPU effects. *(Claude Code: "compare"
→ "read" and "measurement prototype" → "scratch node for reading the shader", to match Step 6.)* Record
the actual profiler measurements separately after implementation.

**Why these numbers** (per frame, at each effect's heaviest state):
- **CPU:** A has more particles alive at its peak (80 vs. 48), so its per-frame simulation cost
  is predicted higher.
- **GPU:** A uses the eight-point star texture and additive blending; B uses a simple 4 × 4 soft
  texture and normal blending, so A's draw cost is predicted slightly higher.
- **B's looser budget:** headroom for an effect that runs continuously; it does not mean B is
  predicted to cost more than A.

(An earlier reason, "B runs all fight, so its average cost is higher", was dropped: Claude review
P pointed out that Step 7 measures each effect per frame at its peak, not averaged over a fight.
Claude Code had offered that reason as an option.)

## Short answers

1. Both effects use `CPUParticles2D`. Compared with `GPUParticles2D`, this design does not use
   GPU-only controls such as `amount_ratio`, GPU visibility configuration, or GPU particle
   trails. It also uses the CPU particle class's scale and colour properties rather than assuming
   GPU-only properties exist. `CPUParticles2D` does not provide several advanced GPU particle
   features listed in the assignment, including turbulence, attractors, particle collision,
   sub-emitters, and particle trails. These capabilities are available through the GPU particle
   workflow rather than the CPU particle node used in these two effects.
2. With `local_coords = true`, live particles remain in the parent's local coordinate space. If
   the parent moves after the hit, the existing particles move with it. Parenting the emitter to
   the stable `Main` node avoids unintended movement during normal gameplay.
3. Four pooled burst slots can be alive simultaneously, with 20 particles per slot, giving a peak
   of 80 particles.
4. A headless run may report a GPU particle processing cost close to zero because the particle
   process runs as a GPU shader, which the dummy renderer does not execute. With VSync enabled,
   FPS should read approximately the display refresh rate both with and without the effect, as
   long as the frame budget is not exceeded.
5. With `preprocess = 1.5`, the particle system is pre-simulated and can appear as an already
   established field when it is first rendered. Without preprocess, it begins empty and gradually
   fills through normal emission. When the scene tree is paused, the CPU particle node follows
   its inherited process mode and stops processing if that mode is pausable. Setting
   `visible = false` hides the particle rendering, but does not automatically stop emission or
   freeze simulation. The emitter continues processing and particles continue aging while
   hidden. When visibility is restored, the current state is rendered.
6. Emission: `amount`, `one_shot`, `explosiveness`, `lifetime`, emission shape. Process: initial
   velocity, spread, gravity, damping, colour ramp, scale amount and scale curve, preprocess,
   speed scale, local coordinates. Draw: texture and draw material / blend mode. *(Revised
   2026-11-08, Zhaohui's choice after Claude review N: initial velocity and spread moved from
   emission to process, because they set how each particle moves.)*

## Revision 2 · 2026-11-08 · Effect B tuning r1 kept; one fact corrected

- **Effect B `color_ramp` alpha** (settings table): offset 0.20 alpha 0.28 → **0.70**; offset
  0.75 alpha 0.20 → **0.50**. Colours and offsets unchanged. Driven by Zhaohui's first look in
  the preview ("too faint"); r1 captured and kept by Zhaohui ("我感觉差不多", "about right").
  Prediction, strips and comparison: TUNING.md, Effect B r1. The scene and
  `test_embers_config.gd` already carry these values (commit 6f0c304). Appended by Claude Code.
- **Fact correction (Claude Code's error in the project facts):** `phase` is declared at
  `godot/game/main.gd:24`, not `:25`.
