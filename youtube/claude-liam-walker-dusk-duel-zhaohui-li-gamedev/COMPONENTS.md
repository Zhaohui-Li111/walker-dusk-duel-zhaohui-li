# COMPONENTS — what the film explains, and where it lives

All 95 files in `godot/` are inventoried and hashed in `gamedev-evidence.json`. Each file belongs
to one component below. There are no exclusions.

## How the film covers each component

**1. generated-art.** Files: `art/akaken/*`, `art/aotake/*`, `art/env/*` (PNG and `.import`).
Beats B02, B03, B05, B07.
- What comes in: Colab exports, on one canvas per fighter, at `canvas_to_screen_scale`.
- What the player sees: the fighters and the courtyard.
- Why it's done this way: one shared canvas keeps every state on the same anchor.
- Trade-off: no animation, one still image per state.

**2. placeholder-art.** Files: `art/placeholder/**`. Beat B06.
- These are fallback images drawn by `tools/export_placeholders.py`.
- They are used only when no generated image exists for a state. In this build, none is used.

**3. pose-data-and-art-loader.** Files: `data/poses.json`, `fighter/fighter_art.gd`. Beats B06, B07.
- `poses.json` is written by `tools/make_poses.py`.
- FighterArt anchors each image by its hip (keypoints 8 and 11) and the ground line, and builds the
  hurtbox and hitbox from the same pose.
- Trade-off: the boxes follow the design, not the pixels. A generated image that drifts from its
  skeleton still gets the designed boxes, which is why B07 checks them in the engine.

**4. fighter-combat.** Files: `fighter/fighter.gd`, `intent.gd`, `player_controller.gd`,
`cpu_controller.gd`, `scripted_controller.gd`, `fighter.tscn`. Beats B08, B09, B02.
- Custom 60 Hz kinematics and frame data.
- `check_hit()` runs after both fighters have moved. It resolves each attack exactly once and emits
  `attack_resolved`.
- Input comes from the keyboard, the seeded CPU, or the test scripts.

**5. round-flow-and-stage.** Files: `game/main.gd`, `main.tscn`, `hud.gd`, `effects.gd`,
`stage.gd`, `controls.gd`, `project.godot`. Beats B02, B09, B12.
- The phases are title → intro → fight → K.O. → result.
- Also here: hitstop, the code-drawn sparks and HUD, the generated background, and the input map
  (including M and N to mute).

**6. audio-wiring.** Files: `game/audio_director.gd`, `audio/sfx/*`, `audio/music/*`.
Beats B10, B11, B12, and B13 (heard, no narration).
- AudioDirector listens to four signals and maps each result to one sound on the SFX and Music buses.
- It never writes game state.

**7. tests-and-captures.** Files: `tests/test_runner.gd`, `capture_states.gd`, `capture_flow.gd`.
Beats B14, B15, B07.
- The test runner steps the fight headless: 94 checks.
- The capture scripts render the engine evidence images.

## Code → visible result pairs (teaching contract code-then-result-v1)

| Code beat | Excerpt | Result beat | What you see |
|---|---|---|---|
| B06 | `fighter/fighter_art.gd` 32–44 | B07 | the 4K staged punch with F1 boxes: feet on the ground line, faint hitbox on the fist |
| B08 | `fighter/fighter.gd` 160–172 | B09 | the jab connects in play: spark at the overlap, Aotake's bar drops, push-back |
| B11 | `game/audio_director.gd` 100–108 | B12 | whiff, block and hit in play, each one resolved attack |
| B14 | `tests/test_runner.gd` 349–358 | B15 | the recorded test output, verbatim |

## One complete input → state → output trace

The film follows this chain across B08, B09, B11, B12 and B13:

1. The J key (`controls.gd`) is read by `PlayerController.read()` as `attack = "punch"`.
2. `Fighter._ground_control()` sets the state to `punch`.
3. In the active frames, `check_hit()` finds that the hitbox meets the opponent's hurtbox.
4. `receive_hit()` subtracts 8 from health and sets `hurt`, so the HUD bar drops.
5. `_resolve("hit")` emits `attack_resolved`.
6. `main.gd` responds with a spark and 4 frames of hitstop. `AudioDirector` plays `SFX-HIT`,
   which you hear in B13.

## What the tests cannot prove (B14)

- The sound test places the dummy by hand (`p2.position.x = …`). It proves the signal-to-sound
  wiring, not that a player reaches those spacings in play.
- No test judges whether a sound is good. Every audio pick was made by measurement, not by ear.
