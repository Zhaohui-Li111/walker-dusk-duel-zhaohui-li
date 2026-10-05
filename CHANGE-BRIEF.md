# CHANGE-BRIEF — walker-dusk-duel asset slice

> Version 1 · 2026-10-05 · written before any generation. Predictions are recorded here and checked
> in TEST-REPORT.md; this file is appended to, not rewritten.

## Asset list

| ID | Asset | Category | Panels |
|---|---|---|---|
| CHAR-AK-REF | Akaken reference image (idle pose, solid green background), source of all poses | art (reference) | — |
| CHAR-AK-IDLE / WALK / CROUCH / RISE / FALL / PUNCH / KICK / BLOCK / HURT / KO / WIN | Akaken, 11 static state images | art | 01–08 |
| CHAR-AO-REF | Aotake reference image | art (reference) | — |
| CHAR-AO-IDLE / KICK / BLOCK / HURT / KO | Aotake, 5 static state images | art | 01, 03–05, 07, 08 |
| ENV-BG | Temple courtyard background at dusk (sky band, dark wall band, lanterns, floor) | art (environment) | all |
| SFX-WHIFF | Strike that hits nothing: short air swish | sound | 03, 05 |
| SFX-HIT | Strike that connects with a hurtbox: dry thud | sound | 04, 05, 08 |
| SFX-BLOCK | Strike that connects with a blocking fighter: wood/cloth knock | sound | 03 |
| SFX-KO | A fighter's health reaches 0: heavy low hit + gong | sound | 06, 08 |
| MUS-LOOP | Taiko + wood-flute loop, cut at a bar boundary | music | 01–05, 07 |

Hit spark, block flash, health bars and text are Claude-drawn/code UI, not counted as generated assets.

## Event-to-sound map

All sounds are played by an `AudioDirector` node that **only listens** to signals. Game state is
decided by the fight code; a missing or muted sound changes nothing.

| Sound | Exact triggering event | Double-trigger prevention |
|---|---|---|
| SFX-WHIFF | `attack_finished(attacker, connected=false)`, emitted once when an attack's active window closes with no contact | emitted from the attack state's exit, once per attack instance |
| SFX-HIT | `hit_landed(attacker, defender)`, emitted when a hitbox first overlaps a non-blocking hurtbox | each attack instance keeps a `hit_targets` set; a defender already in it is ignored, so one swing hits once even if the boxes overlap for several frames |
| SFX-BLOCK | `hit_blocked(attacker, defender)`, same overlap but defender is in `BLOCK` | same `hit_targets` set; a blocked swing cannot also hit |
| SFX-KO | `fighter_ko(fighter)`, emitted when health crosses from >0 to ≤0 | guarded by `is_ko`, so it fires once per fighter per round; the final hit plays SFX-HIT and then SFX-KO (panel 8), each exactly once |

Holding the attack button does **not** repeat attacks: a new attack starts only on `is_action_just_pressed`
while the fighter is not already attacking.

## Music behavior

| Situation | Behavior |
|---|---|
| Fight running | MUS-LOOP plays on the `Music` bus, looping with no gap |
| Pause (Esc / P) | Music bus ducks to −12 dB with a low-pass filter; SFX bus paused; resume restores both |
| Failure (player KO) | Music stops immediately on `fighter_ko` |
| Success (opponent KO) | Music stops immediately; stays stopped on the win screen |
| Rematch | Music restarts from position 0 |
| End of slice (Esc on win/KO screen) | Quit; nothing plays |
| Mute | `M` toggles the Music bus, `N` toggles the SFX bus (separately) |

## Predicted failure cases and how each will be checked

1. **Generated poses drift from the reference** (arms longer, fists smaller, headband on the wrong
   side, outfit color changes). *Check:* overlay each pose on its OpenPose skeleton at 50% opacity,
   compare against consistency rules 1–8 in CHARACTER-SHEET.md; reject on any rule failure.
2. **One swing plays SFX-HIT several times** because hitbox and hurtbox overlap across frames.
   *Check:* automated test that scripts 20 punches, 10 kicks and a held punch button against a dummy
   and asserts the counts of each signal and each sound call match the number of attacks.
3. **Music loop clicks at the seam.** *Check:* cut at a zero crossing on a bar boundary, listen to at
   least 3 repetitions in Godot, and inspect the waveform at the seam.
4. **Fighters disappear against the background** (red gi on dusk stone). *Check:* in-engine
   screenshot converted to grayscale, and the slice played at 1× from 2 m away; compare with the
   palette contrast table.
5. **The slice is unreadable muted.** *Check:* play a full round with both buses muted; confirm
   whiff / hit / block / KO can each be told apart by sight alone.
6. **Art does not line up with collision** (generated punch reaches further than the hitbox).
   *Check:* debug-draw collision shapes in Godot over every state image and screenshot them.

## Possible revisions already noted

- Extend the hurtbox along an attacking limb so whiffs can be punished (CHARACTER-SHEET collision note).
- A separate SFX-HURT for the player being hit, if playtesting shows SFX-HIT is ambiguous about who was hit.

---

## Revision 2 · 2026-10-05 · during slice step 2 (no generation yet)

- **Signals renamed and unified.** The three planned signals (`attack_finished`, `hit_landed`,
  `hit_blocked`) became one: `attack_resolved(fighter, kind, result, point)`, emitted **exactly once
  per attack** with `result` = `hit` / `blocked` / `whiff` / `interrupted`. SFX-HIT, SFX-BLOCK and
  SFX-WHIFF map to the first three; `interrupted` (attacker hit during startup) plays nothing.
  Whiff now fires when the active window ends, not after recovery, so the swish lines up with the
  swing. `knocked_out(fighter)` is unchanged and drives SFX-KO and the music stop.
- **Hitboxes cover the striking limb** (elbow→fist, knee→foot) instead of only the tip. Found by the
  automated block test: at touching distance a tip-only kick box passed beyond the opponent's hurtbox
  and whiffed. Regression test: `test_point_blank_attacks_connect`.
- **Hurt image appears on the hit frame.** The 4-frame hitstop delayed the hurt image; found in the
  flow capture (`evidence/flow/05_player_hurt.png`), fixed, and covered by `test_punch_hits_once`.
- **Design consequence noted:** each blocked hit pushes the defender back ~6 px, so repeated attacks
  on a blocker need the attacker to step in. Intentional (no infinite pressure), but to playtest.
