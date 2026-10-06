# TEST-REPORT — walker-dusk-duel asset slice

> Draft started 2026-10-06 by Claude Code. Sections marked **TO DO (human)** need Zhaohui's own
> playtest and listening; nothing in them is filled in until that happens.

- Engine: Godot 4.7.2 stable (GL Compatibility), Windows 11 Home
- Source revision for the automated results below: `0cdd8a7` (placeholder art and no audio files yet;
  re-run on the final revision before submission)

## Automated check

```bash
godot --headless --path godot --script res://tests/test_runner.gd
```

Result at `0cdd8a7`: **78 checks, 0 failed** (exit code 0). The suite steps the fight scene frame by
frame with scripted input (no real-time waiting):

| Area | Tests | What they assert |
|---|---|---|
| Movement and state images | 5 | walk distance and facing; a held attack button starts one attack; jump shows rise and fall; crossing over flips both fighters; every state has an image and the idle hurtbox reaches the feet |
| Combat and round flow | 9 | one punch = one hit and 8 damage; point-blank attacks connect; out-of-range attacks whiff; blocking takes no damage; the hurt fighter is pushed away from the attacker; one K.O., then result screen and rematch; every attack resolves exactly once (CPU vs scripted mix); the seeded CPU is deterministic; pause freezes everything |
| Sound and music | 4 | **each attack requests exactly one sound** (held punch, mashing every 3 frames, 3 kicks, 2 blocks, 2 whiffs → 13 attacks, 13 sounds); final hit plays SFX-HIT then SFX-KO once each; music starts on the title, ducks −12 dB with a low-pass on pause, stops at K.O., stays stopped on the result screen and restarts on rematch; **a seeded fight ends identically with both buses muted** |

Assertions that were wrong and how they were handled are in FRICTIONAL.md (2026-10-05 step 2 and
step 3 entries): two test *scenarios* were corrected after the failure was understood; no
assertion was weakened.

## Startup and controls — TO DO (human)

Fresh clone of the submitted revision → open `godot/project.godot` → F5. Record: runs without errors?
every control in README works?

## Character against the sheet — TO DO

In-engine captures of each state with F1 boxes on (`godot --path godot --script res://tests/capture_states.gd`
→ `evidence/states/`) beside the CHARACTER-SHEET poses, once the generated art is in. Note any
mismatch with the collision boxes.

## Storyboard against the slice — TO DO

`godot --path godot --script res://tests/capture_flow.gd` → `evidence/flow/` (scripted-input captures)
beside panels 01–08. Panels 02 and 06 are design views, not gameplay camera shots.

## Sound events — TO DO (human listening)

Play normally, then mash punch and hold punch: each whiff / hit / block / K.O. should be heard once.

## Music — TO DO (human listening)

Loop heard at least three times round without a click or gap; pause muffles it; K.O. stops it;
rematch restarts it.

## Muted play — TO DO (human)

Full round with M and N both on; can whiff, hit, block and K.O. be told apart by sight alone?

## Inspect-and-revise cycles (so far)

1. In-engine state capture showed the KO poses clipped by the canvas → KO legs folded (commit `46ac888`).
2. The block test showed point-blank kicks whiffing → hitboxes now cover the whole striking limb.
3. Flow capture showed the hurt image arriving after hitstop → hurt image now shown on the hit frame.
4. Five rounds of the Akaken reference (prompt truncation, colour binding, colour-block img2img) — see
   FRICTIONAL and ASSET-LOG.

## Honest limitations

*(to be completed after the human playtest)*
