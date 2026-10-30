# COMPONENTS — what this film explains, and where

Source: `godot/` at `043df17`; ledger: `gamedev-evidence.json` (built by `tools/build_evidence.py`).

| Component | Files | Beats | Mechanism, and one trade-off |
|---|---|---|---|
| hurt-flash-shader | `shaders/hurt_flash.gdshader` (Zhaohui) | B02, B04, B05, B08 | canvas_item; `fragment()` mixes each pixel's own `COLOR.rgb` toward `flash_color` by `hurt_amount`, leaving alpha alone. *Trade-off:* pure red reads as "hurt" but barely changes Akaken's orange gi (contrast 3.93 → 3.73). |
| hurt-flash-driver | `fighter/hurt_flash.gd` (Claude), `fighter/fighter.tscn` | B06, B07 | A node under each `Sprite2D` builds its own ShaderMaterial and sets `hurt_amount = stun / HITSTUN` each physics tick, after `main.gd` steps the fight. *Trade-off:* it follows game state exactly, so it also ignores `Engine.time_scale`, like the fight. |
| hurt-flash-tests | `tests/test_hurt_flash.gd`, `tests/capture_a5.gd` | B09, B10, B17 | The real loop with the J key, a sampler at `process_priority` 1000, uniform list and source-text defaults. *Trade-off:* the retrigger is reachable only with labelled setup. |
| granite-shader-and-materials | `shaders/granite.gdshader` (Zhaohui), `props3d/materials/*.tres`, `props3d/make_granite_materials.gd`, `props3d/prop_room.tscn`, `props3d/textures/*` | B11, B12, B13 | Colour with `source_color`, roughness and normal as data, four uniforms in two groups; two materials, one shader. *Trade-off:* BoxMesh UVs stretch one `uv_scale` 2.25 : 1, so it reads as planks. |
| material-tests | `tests/test_materials.gd`, `tests/normal_map_check.gd`, `tests/calibrate_normal_map.gd`, `MATERIALS.md` | B10, B17 | Pins the audit: shader paths, hints from source, values, `.import` settings, curl ratios. *Trade-off:* it cannot see any pixel. |
| hint-experiment | `shaders/hint_experiment.gdshader` (Zhaohui), `hint_experiment/*` | B14, B15 | One 3 × 1 file through two samplers that differ only in `source_color`, on unshaded quads. *Trade-off:* in Compatibility both quads read the same, so it shows the renderer's pipeline more than the hint. |
| generated-standard-shader | `shaders/standard_generated.gdshader` (Godot) | B16 | Godot's own code for a StandardMaterial3D with the same textures; read, not used. |

**Input → state → output trace (B04 → B06 → B07):**
1. **Input:** the J key; `PlayerController` reads `p1_punch`; the punch's hitbox meets Aotake.
2. **State:** `receive_hit()` sets `state = "hurt"`, `stun = 18`; hitstop holds it 4 ticks.
3. **Driver:** `hurt_flash.gd:27` sets Aotake's material's `hurt_amount` to 18 / 18 = 1.0.
4. **Shader:** `hurt_flash.gdshader:7` mixes every pixel of Aotake's sprite to red.
5. **Output:** Aotake is red on screen (B02, B07), and fades over 22 ticks.

Files outside these components are the A2 game and the A3 prop assets, listed as exclusions in the
ledger with that reason.
