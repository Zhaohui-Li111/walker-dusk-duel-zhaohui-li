# TEST-REPORT — walker-dusk-duel asset slice

> Draft by Claude Code, updated 2026-10-06 with the generated art and audio. Sections marked
> **TO DO (human)** need Zhaohui's own words; Claude has only recorded what Zhaohui said in chat.

- Engine: Godot 4.7.2 stable (GL Compatibility), Windows 11 Home
- Source revision for the automated results below: `431f03f` (all generated art, music loop and
  four sound effects in place; re-run on the submitted revision if anything changes)

## Automated check

```bash
godot --headless --path godot --script res://tests/test_runner.gd
```

Result at `431f03f`: **94 checks in 18 tests, 0 failed**. At `0cdd8a7`, with placeholder art, it
was 78 checks. The suite steps the fight scene frame by
frame with scripted input (no real-time waiting):

| Area | Tests | What they assert |
|---|---|---|
| Movement and state images | 5 | walk distance and facing; a held attack button starts one attack; jump shows rise and fall; crossing over flips both fighters; every state has an image, the idle hurtbox reaches the feet, and **every state image shows a body** (at least 300 opaque pixels sampled; added after rembg erased Aotake's K.O. pose) |
| Combat and round flow | 9 | one punch = one hit and 8 damage; point-blank attacks connect; out-of-range attacks whiff; blocking takes no damage; the hurt fighter is pushed away from the attacker; one K.O., then result screen and rematch; every attack resolves exactly once (CPU vs scripted mix); the seeded CPU is deterministic; pause freezes everything |
| Sound and music | 4 | **each attack requests exactly one sound** (held punch, mashing every 3 frames, 3 kicks, 2 blocks, 2 whiffs → 13 attacks, 13 sounds); final hit plays SFX-HIT then SFX-KO once each; music starts on the title, ducks −12 dB with a low-pass on pause, stops at K.O., stays stopped on the result screen and restarts on rematch; **a seeded fight ends identically with both buses muted** |

Assertions that were wrong and how they were handled are in FRICTIONAL.md (2026-10-05 step 2 and
step 3 entries): two test *scenarios* were corrected after the failure was understood; no
assertion was weakened.

## Startup and controls — TO DO (human)

Fresh clone of the submitted revision → open `godot/project.godot` → F5. Record: runs without errors?
every control in README works?

- 2026-10-06: Zhaohui played the slice at `431f03f` and said in chat that it was fine overall
  ("还可以"). Details per control: *(to fill in Zhaohui's words)*

## Character against the sheet

In-engine captures of each state with F1 boxes on (`godot --path godot --script res://tests/capture_states.gd`
→ `evidence/states/`, contact sheet `evidence/states_contact.png` from `python tools/make_contact.py`),
compared with the CHARACTER-SHEET poses by Claude. Zhaohui has not re-judged them.

- **Boxes against the art:** in all 11 states both fighters' feet sit on the ground line and the
  hurtbox covers the body. The punch and kick hitboxes reach the fist and the foot.
- **Matches the sheet:** Akaken keeps the headband, topknot, wrapped fists and stocky build in every
  pose. Aotake keeps the straw hat, braid, teal robe and navy sash.
- **Mismatches, accepted:**
  - Akaken's top is a lighter orange than `#D9482B`.
  - RISE has no yellow belt.
  - FALL's belt is green, picked up from the background.
  - The accepted reference (s143) has a blank face, which barely reads at game size.
  - Aotake has 5 drawn poses; walk, jump and win reuse other images (CHARACTER-SHEET appendix).
- **Found and fixed:** Aotake vanished at K.O. because the background remover erased the lying
  pose. It was re-exported with a chroma key, and a test now guards this.

## Storyboard against the slice

`godot --path godot --script res://tests/capture_flow.gd` → `evidence/flow/` (scripted-input captures,
contact sheet `evidence/flow_contact.png`), compared with the panels by Claude.

| Panel | Capture | Match |
|---|---|---|
| 1 Title | `01_title` | yes: dusk courtyard, both fighters, "press Enter" |
| 2 Fighter intro | `02_round_call` | partly: the slice shows a round call over the stage rather than a separate intro card (design view) |
| 3 Jab meets block | `03_block` | yes: block spark, no health lost |
| 4 Kick lands | `04_hit` | yes: hit spark, Aotake's bar drops |
| 5 Player is hit | `05_player_hurt` | yes: Akaken's hurt pose, bar drops |
| 6 K.O. (loss) | none | **not captured:** the scripted run ends with Aotake knocked out (`07_ko`); the losing K.O. uses the same code path but has no capture (design view) |
| 7 Rematch | `09_rematch` | yes: "ROUND 2 - FIGHT", both bars full |
| 8 Victory | `07_ko`, `08_result` | yes: "AKAKEN WINS", Enter rematch / Esc quit |

Extra captures: `06_paused` (pause overlay) and `06b_muted_indicator` (both buses muted, shown in the HUD).

## Sound events — TO DO (human listening)

Play normally, then mash punch and hold punch: each whiff / hit / block / K.O. should be heard once.

- Automated: the one-sound-per-event tests pass with the real files loaded (no "no file yet" warning).
- Files: whiff 0.35 s, hit 0.40 s, block 0.40 s, K.O. 2.50 s; decoded peaks −1.0 to −1.5 dBFS.
  Picks were made by measurement, not by ear (FRICTIONAL 2026-10-06, sound effects).
- Zhaohui's listening: *(to fill)*

## Music — TO DO (human listening)

Loop heard at least three times round without a click or gap; pause muffles it; K.O. stops it;
rematch restarts it.

- Automated: `test_music_follows_the_round` passes with `loop.ogg` loaded.
- Seam, measured on the decoded OGG: the jump across the loop point (0.013) is below the 99th
  percentile of ordinary sample steps in the loop (0.014). A three-repeat check file is at
  `design/generations/audio/checks/MUS-RAW_s22_loop_x3.ogg`.
- Zhaohui's listening: *(to fill)*

## Muted play — TO DO (human)

Full round with M and N both on; can whiff, hit, block and K.O. be told apart by sight alone?

- Automated: a seeded fight ends identically with both buses muted. Visually, hit and block have
  different sparks and only a hit moves the health bar (`03_block` against `04_hit`).
- Zhaohui's muted round: *(to fill)*

## Inspect-and-revise cycles (so far)

1. In-engine state capture showed the KO poses clipped by the canvas → KO legs folded (commit `46ac888`).
2. The block test showed point-blank kicks whiffing → hitboxes now cover the whole striking limb.
3. Flow capture showed the hurt image arriving after hitstop → hurt image now shown on the hit frame.
4. Five rounds of the Akaken reference (prompt truncation, colour binding, colour-block img2img) — see
   FRICTIONAL and ASSET-LOG.
5. Flow capture showed Aotake vanishing at K.O. → new "image shows a body" test failed on exactly
   that image → re-exported with a chroma key (commit `9099c9e`).
6. Music seam score rose after the crossfade → checked on the decoded file, judged not a click
   (pending a listen).

## Honest limitations

- Every selection after round 3 of the images, and every audio pick, was Claude's, made from
  measurements and a visual check, never by ear. Zhaohui delegated these and has not re-judged
  them one by one.
- The colour-block starting images were drawn by Claude's script and then repainted by the model
  at strength 0.75. ASSET-LOG records the starting image and strength for each row.
- The character mismatches listed above.
- The CPU was tuned by tests, not by playtesting.
- Storyboard panel 6 (losing K.O.) has no capture.
- Licences are non-commercial or limited: MusicGen weights are CC-BY-NC 4.0, and Stable Audio Open
  uses the Stability AI Community License.
