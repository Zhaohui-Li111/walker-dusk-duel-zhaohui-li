# FRICTIONAL — walker-dusk-duel

Dated log of the design as it happened. Each entry separates Zhaohui's decisions, Claude Code's
contributions, and generative-model outputs. Retrospective notes are labeled.

## 2026-10-05 — choosing the game and locking the design (no generation yet)

> Drafted by Claude Code from the chat transcript of this session; Zhaohui to edit into their own words
> and add what they actually thought.

- **Wanted:** a game I actually want to build this semester. Claude first suggested four themes
  (candle-spirit platformer, rain-delivery robot, mushroom jumper, paper-crane courier). I chose a
  **one-on-one fighting game in the spirit of classic arcade tournament fighters** instead.
- **Asked / got:** Claude searched for Godot 4 fighting-game starting points (GDQuest and CodingQuests
  hitbox demos, Fray, Castagne, Quiver beat-'em-up) and recommended a small own-code slice rather than
  a full framework. Claude also pointed out the rights rule: no franchise or character names in any
  prompt or reference.
- **Decided:** I said I did **not** want the realistic "digitized actor" look, only a **cartoon
  character with fighting moves**, and **two martial artists**. That removed the photo-a-real-person
  pose pipeline Claude had proposed.
- **Asked / got:** Claude checked my machine: Intel UHD integrated graphics, 16 GB RAM, no NVIDIA
  GPU. Local Stable Diffusion with ControlNet is not practical here, so image generation will run on
  Northeastern HPC or free Google Colab (to be confirmed).
- **Asked / got:** instead of photographing poses, Claude wrote `tools/make_poses.py`, which builds
  every pose from one fixed set of bone lengths and writes OpenPose skeletons, mannequin blocking,
  collision overlays and a silhouette test. I accepted Claude's proposal of Akaken (stocky, red,
  topknot, big fists) vs Aotake (tall, teal, straw hat, long legs), **5-head proportions**, and a dusk
  temple courtyard.
- **Observed:** the first silhouette pass cropped both KO poses at the canvas edge (legs too long when
  lying flat). Claude bent the knees and laid the arms along the body; re-checked in `blocking.png`.
- **Observed:** Claude's contrast script showed the red gi at 1.27:1 and teal robe at 1.80:1 against
  the first proposed mid-tone stone `#6E6680`. The fighters would have blended in, so the wall band
  behind them was darkened to `#3A3347` (red 2.82:1, teal 4.01:1). See CHARACTER-SHEET palette table.
- **Decided:** I asked Claude to draw the three design-view storyboard panels (01 high angle, 02 low
  angle, 06 Dutch close-up) instead of hand-sketching them. Claude's first P2 and P6 were plain
  silhouettes too large to read as a close-up; Claude added the eye, headband and wrapped fists and
  re-framed them. Panel images are Claude code drawings, not generated assets.
- **Human / Claude / model:** decisions on genre, cartoon style, two fighters and accepting the
  proposal were mine. Theme options, template search, the pose and storyboard scripts, the contrast
  numbers and the draft documents were Claude's. No generative model has been used yet.
- **Still unresolved:** whether the red gi at 2.82:1 is enough in motion; whether ControlNet
  OpenPose respects 5-head skeletons (it is trained mostly on realistic proportions); which GPU I
  will actually get.

## 2026-10-05 — KO poses clipped, found in-engine (before any generation)

- **Wanted:** every state image to fit the shared 832×1216 canvas, because the same canvas is the
  ControlNet input and the in-game sprite frame (CHANGE-BRIEF failure case 6, art vs collision).
- **Observed:** Claude's Godot state capture (`evidence/states_contact.png`, F1 boxes on) showed both
  KO poses cut at the canvas edge: Akaken's topknot and Aotake's hat tip were missing. Cause: the pose
  centring in `tools/make_poses.py` ignored the topknot/hat, and the legs lying flat made the pose
  wider than the canvas.
- **Changed:** knees folded further in both KO poses, and the head tip now counts for horizontal
  centring (not for grounding). Only the two KO skeletons changed; the other 14 are byte-identical.
  Re-checked in `evidence/ko_check.png`; 39 automated checks still pass.
- **Human / Claude / model:** I asked for the fix before generation; Claude found the clipping in the
  capture and changed the script. No generative model involved.
- **Still unresolved:** whether the model will draw a hat that is "beside the head" as the KO prompt says.

## 2026-10-05 — slice step 2: what the tests and captures caught

- **Wanted:** every attack to produce exactly one readable result (CHANGE-BRIEF failure case 2) and
  the slice to read without sound (pillar *Every hit is felt*).
- **Observed (automated test):** `test_block_takes_no_damage` failed: 5 kicks at a blocker gave
  `blocked, whiff, whiff, whiff, whiff`. Claude's first reading was the block push moving the
  defender out of range, so the test was changed to step in before each kick; it still failed
  (`blocked ×3, whiff ×2`). A debug print of the gaps showed the real cause: at touching distance the
  kick's tip-only hitbox was past the opponent's body. The test was right; the collision design was
  wrong. Hitboxes now cover the whole striking limb.
- **Observed (screenshot):** in the flow capture the player still showed the idle image during the
  4-frame hitstop after being kicked, so the hit read late. Fixed; a test now checks the hurt image
  is on screen on the hit frame.
- **Human / Claude / model:** I asked for step 2; Claude wrote the combat, CPU, round flow, tests and
  captures, and diagnosed both failures. No generative model involved. I have not playtested step 2
  myself yet.
- **Still unresolved:** whether the CPU (block chance 0.55, kick chance 0.5, 10-frame reaction) is
  fun or just annoying; whether the 6 px block push feels right.
