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

## 2026-10-05 — slice step 3: sound wiring before any sound exists

- **Wanted:** each of the four events to request exactly one sound, music to follow pause / K.O. /
  rematch, and muting to change nothing in the fight (CHANGE-BRIEF failure cases 2 and 5).
- **Observed:** Claude noticed while wiring that the K.O. signal fired before the final hit's result,
  which would have logged SFX-KO before SFX-HIT, the reverse of panel 8; fixed and tested.
- **Observed (test):** the first sound test expected "2 blocks, 2 whiffs" but got 1 block and 10
  whiffs. The one-to-one checks passed; the expectation was wrong because each hit or block pushes
  the dummy out of range. The scenario now puts the dummy back in range before each attack; the
  one-to-one assertions were not changed.
- **Result:** 78 automated checks pass, including a seeded CPU fight that ends identically with
  sound on and with both buses muted.
- **Human / Claude / model:** Claude wrote AudioDirector, the mute keys and the tests. No audio has
  been generated, so nothing has been listened to yet.
- **Still unresolved:** everything that needs ears: loudness balance, whether the loop seam clicks,
  whether the -12 dB pause duck is noticeable enough.

## 2026-10-05 / 06 — Akaken reference: five rounds to get one usable image

> Retrospective entry written by Claude Code the same evening from the Colab session. From round 4
> on, Zhaohui delegated the accept/reject decisions to Claude ("你后面就自己判断吧"); every review
> from then on is labelled "Decided by Claude" in ASSET-LOG. Zhaohui should re-judge them.

- **Setup friction (no images yet):** free Colab T4. (1) Model CPU offload crashed the session by
  running out of system RAM; (2) without offload, diffusers 0.40 / transformers 5.18 left some
  components in fp32 and the pipeline needed 14 GB of VRAM (OOM) until everything was cast to fp16 on
  the CPU (8.8 GB); (3) `pipe.enable_vae_tiling()` no longer exists in diffusers 0.40
  (`pipe.vae.enable_tiling()`); (4) later `StableDiffusionXLControlNetImg2ImgPipeline.from_pipe()`
  ran out of memory again, so the img2img pipeline is now built from the same component objects.
- **Prompt truncation:** the first Stage 1 run warned that CLIP keeps only 77 tokens. The prompts
  were ~110, so the entire style half (cel shading, outline, green background) was silently cut.
  Claude stopped the run, shortened the prompts with style first, and `check_prompt()` now refuses
  anything over 77 tokens.
- **Round 1 (seeds 101-104, prompt only):** cartoon style worked, but no red-orange gi on any image,
  bearded/bald older men, realistic proportions. Zhaohui agreed with Claude's assessment; all rejected.
- **Round 2 (111-114):** colour moved to the front, "beard, old man, bald, boxing gloves" added to the
  negative. Age and topknot fixed; still no headband; pants/belt colours random. All rejected
  (Zhaohui agreed).
- **Round 3 (121-124):** headband phrase moved first and made concrete. The headband became a turban
  once and was missing otherwise; colours landed on the wrong parts. All rejected (Zhaohui agreed).
  Conclusion: SDXL does not bind several colours to several garments from text alone.
- **Decision (Zhaohui chose plan B):** paint the CHARACTER-SHEET palette onto each pose as a
  colour-block mannequin (`tools/colorblock.py`, Claude-written) and start img2img from it, with the
  OpenPose skeleton still controlling the pose.
- **Round 4 (131-134, strength 0.6):** first time every image had the headband, topknot, red-orange
  top, dark pants, yellow belt and cream wraps. But Claude judged them too close to its own
  mannequin (tube limbs, little drawing by the model), which matters because Claude-drawn art does not
  count as a generated asset. All rejected (decided by Claude).
- **Round 5 (141-144, strength 0.75):** the model redraws limbs, folds and shading while the colours
  stay anchored. Accepted **s143** (decided by Claude): topknot, headband with tails, colours right,
  follows the skeleton. Known flaw: a blank face with no eyes; at the 112 px game size the face is
  ~12 px, so it barely reads. s142 had the best face but spiky hair instead of the topknot, and the
  topknot is what separates Akaken's silhouette from Aotake's hat.
- **Human / Claude / model:** generation by SDXL + xinsir OpenPose ControlNet (+ IP-Adapter from
  Stage 2). Prompts, the colour-block tool, the debugging and every Colab action were Claude's.
  Zhaohui chose the theme, agreed with rounds 1-3 and chose plan B; rounds 4-5 were Claude's call.
- **Still unresolved:** whether the strength-0.75 images are "generated enough" for the rubric
  (the colour block is a Claude drawing; the final pixels are the model's). The log records the
  starting image and strength for every row so a grader can judge.
