# COMPONENTS — what this film explains, and where

Source: `godot/` at `8049c54`; ledger: `gamedev-evidence.json` (built by `tools/build_evidence.py`).
The A7 files are exactly `git diff a6 8049c54 -- godot` (without `.uid`), plus `fighter/fighter.gd`, the
unchanged state machine both clips are timed from.

| Component | Files | Beats | Mechanism, and one trade-off |
|---|---|---|---|
| lantern-sheet | `art/sheets/lantern_flame.png` (+ `.import`), `make_lantern_flame_sheet.gd`, `ATTRIBUTION.md` | B04 | 48 × 32 PNG, 12 × 16 cells, 4 × 2, flame base (6, 15) in every cell; written by code (MIT). *Trade-off:* no course art was available, so the sheet is generated; it is small (12 × 16) and reads as a candle flame above the lit window. |
| lantern-clip | `animations/lantern_flicker.tres`, `lantern_flame.tscn`, `lantern_flame.gd`, `game/main.tscn` | B03, B05, B06, B15 | `Sprite2D:frame` keys 0–7 at 0.1 s, `UPDATE_DISCRETE`, length 0.8, `LOOP_LINEAR`; the AnimationPlayer is the only writer; the script only `play()`s and `seek()`s once (offset 0.0 / 0.4). *Trade-off:* the flame reads no game state, so it burns through pause (Zhaohui's L1); the left lantern is hidden behind Akaken at the start position. |
| kick-arc-clip | `animations/kick_arc.tres`, `kick_rest.tres`, `fighter/fighter.tscn`, `previews/kick_arc_preview.gd/.tscn` | B08–B11 | `Pivot` visible / rotation / modulate keyed at frames 0, 7, 8, 12, 13, 27, 28 ÷ 60, step 1/60, `LOOP_NONE`, transitions 0.5 / 2.0 / 1 / 1 / 0.4; r1: key 0 alpha 0.25. *Trade-off:* the arc is beside the leg, not the leg itself, because `fighter.gd` owns the sprite. |
| kick-rig-controller | `fighter/kick_rig.gd` | B12–B14, B16 | Physics tick, priority 100: `kick` → `seek(frame / 60, true)` on a MANUAL player; any other state → `rest`. Measured gap 0 s. *Trade-off:* the arc can never run ahead of or behind the hit check, but it also cannot animate anything the state machine does not count. |
| fighter-state-machine | `fighter/fighter.gd` (unchanged) | B08, B14, B15 | Kick 7/5/16 constants counted as 8/5/15 frames; `check_hit` 7 < frame ≤ 12; `receive_hit` interrupts; `_update_sprite` writes the sprite. |
| a7-tests | `tests/anim_checks.gd`, `test_lantern_readback.gd`, `test_kick_readback.gd`, `test_anim_states.gd`, `test_kick_edges.gd`, `test_pins_a7.gd` | B07, B16–B18 | Read-backs 47 / 52, states 58, edges 38, pins 19 (all 0 failed); mutations 1–3 exit 1, 4 exit 0. *Limit:* interrupt edges use labelled SETUP hits; none of it sees the picture. |
