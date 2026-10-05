# Character sheet — Akaken (P1, the player)

> Version 1 · 2026-10-05 · written before any generation. Images under `design/character/` are
> **design specifications** produced by `tools/make_poses.py` (written by Claude Code), not game art.

- **Concept in one sentence:** a short, stocky young brawler in a sleeveless red-orange gi whose
  oversized wrapped fists and topknot keep the fighter readable in any pose.
- **Viewport:** 640×360 (shown 2× at 1280×720). Standing height on screen: **112 px**.
- **Silhouette at on-screen size:** [design/character/silhouette.png](design/character/silhouette.png)
  shows both fighters solid black at 1:1, plus a 4× magnified copy. Read test: at 1:1 the topknot,
  headband tails and big fists separate Akaken from Aotake's hat brim and long legs.
- **Orientation:** drawn **facing right** only, in a three-quarter side view (chest slightly toward
  camera). Facing left = `flip_h` at runtime. The fighter always faces the opponent, so flipping
  happens when they cross over, not on every left/right input.
- **Proportions reference:** fixed bone lengths in [design/character/poses.json](design/character/poses.json)
  (head radius 86, torso 285, upper arm 118, forearm 108, thigh 172, shin 162, on an 832×1216 canvas).
  A full turnaround is **not** generated because the game only shows the right-facing 3/4 view.

## Poses (11, each a single static image for one game state)

All derived from one skeleton set, so bone lengths are identical. Blocking:
[akaken/blocking.png](design/character/akaken/blocking.png) · ControlNet inputs:
[akaken/openpose/](design/character/akaken/openpose/) · one-canvas sheet:
[akaken/openpose_sheet.png](design/character/akaken/openpose_sheet.png)

| # | Pose | Game state | Asset ID |
|---|---|---|---|
| 1 | Idle fighting stance | `IDLE` (no input) | CHAR-AK-IDLE |
| 2 | Walk forward (one stride) | `WALK` (left/right held) | CHAR-AK-WALK |
| 3 | Crouch | `CROUCH` (down held) | CHAR-AK-CROUCH |
| 4 | Jump rising (knees tucked) | `JUMP` while velocity.y < 0 | CHAR-AK-RISE |
| 5 | Jump falling (arms out) | `JUMP` while velocity.y ≥ 0 | CHAR-AK-FALL |
| 6 | Punch, lead-arm jab extended | `PUNCH` active frames | CHAR-AK-PUNCH |
| 7 | High kick, lead leg | `KICK` active frames | CHAR-AK-KICK |
| 8 | Block, forearms up | `BLOCK` (block held) | CHAR-AK-BLOCK |
| 9 | Hurt, leaning back away from attacker | `HURT` hitstun | CHAR-AK-HURT |
| 10 | KO, lying on back | `KO` (health 0) | CHAR-AK-KO |
| 11 | Victory, fist raised | `WIN` (opponent KO) | CHAR-AK-WIN |

Walk is reused for walking backward (the fighter keeps facing the opponent); it is not counted twice.

## Collision overlay

[akaken/collision.png](design/character/akaken/collision.png): green = hurtbox (can be hit),
red = hitbox (deals damage), same scale as the poses.

- **Hurtbox:** one rectangle per state covering head and torso core down to the feet, ≈2.1 head radii
  wide. Crouch and jump use their own shorter rectangles; KO has none.
- **Hitbox:** only in `PUNCH` (around the lead fist) and `KICK` (around the lead foot), only during
  active frames.
- **Art beyond the shape, and why it is fair:** the guard fists, the extended punching arm or kicking
  leg, the headband tails and topknot all sit outside the hurtbox. They are cosmetic and cannot be
  hit. Aotake follows the same rule (hat brim and braid cannot be hit), so neither fighter gains an
  advantage. *Known simplification:* real fighting games often extend the hurtbox along an attacking
  limb so that whiffs can be punished; listed as a possible revision in CHANGE-BRIEF.

## Palette (checked against the environment)

| Role | Hex | Contrast vs wall #3A3347 | vs floor #2B2733 |
|---|---|---|---|
| Gi (main body) | `#D9482B` | 2.82 | 3.41 |
| Hand wraps / headband | `#F2E6D0` | 9.75 | 11.80 |
| Belt accent | `#F5C542` | 7.42 | 8.99 |
| Skin | `#E8B27A` | — | — |
| Outline / pants | `#1E1B22` | 1.41 | 1.17 |

**Finding from the check (2026-10-05, WCAG luminance contrast computed by a Claude-written script):**
against the first proposed mid-tone stone (`#6E6680`), the red gi scored only 1.27:1 and the teal robe
1.80:1, so the fighters would blend into the wall. The wall band where the fighters stand was
therefore darkened to `#3A3347`, keeping the lighter dusk sky
(`#5A4766`) only above head height. The dark outline does **not** separate the fighter from this dark
wall (1.41:1), so separation must come from the bright fills; this is listed as a failure case to
test in-engine.

## Consistency rules (judge every generated pose against these)

1. Head-to-body ratio about 1 : 5; head width ≈ shoulder width.
2. Fists are larger than the head's eye-to-chin height and always wrapped in cream `#F2E6D0`.
3. Topknot on top of the head, cream headband with two tails flowing **behind** the head.
4. Sleeveless red-orange gi top, yellow belt, dark pants, bare feet.
5. Eyes sit on the head's horizontal midline; no visible teeth except in KO/hurt.
6. One outline weight (about 3 px at the 112 px game size) in every pose.
7. Faces right, three-quarter side view; no pose may show the back.
8. Bone lengths match `poses.json`; a generated pose whose arm or leg is clearly longer or shorter is rejected.

---

## Appendix — opponent Aotake (CPU), reduced sheet

Not the main character, so only the poses the slice needs (5). Same rules for outline, flat color and
orientation (drawn facing right, flipped to face left at runtime).

- **Concept:** tall, lean kicker in a teal robe and a wide straw hat with a long braid.
- **Standing height on screen:** 124 px. Bone lengths in `poses.json`.
- **Poses:** idle stance (CHAR-AO-IDLE), front kick (CHAR-AO-KICK), block (CHAR-AO-BLOCK),
  hurt (CHAR-AO-HURT), KO (CHAR-AO-KO). Blocking: [aotake/blocking.png](design/character/aotake/blocking.png),
  collision: [aotake/collision.png](design/character/aotake/collision.png).
- **Palette:** robe `#2FA3B0` (4.01 vs wall), straw hat `#D8B676` (6.23), sash `#17324D`, skin `#D9A27A`,
  outline `#1E1B22`.
- **Must differ from Akaken:** hat brim wider than the shoulders; no topknot; cool body color; legs
  visibly longer.
