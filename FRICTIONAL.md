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

## 2026-10-06 — poses, opponent, background and export (decisions delegated to Claude)

> Written by Claude Code from the Colab run. Every choice below is labelled "Decided by Claude
> (Zhaohui delegated the choice)" in ASSET-LOG; Zhaohui has not yet re-judged them.

- **Akaken poses (Stage 2):** 11 poses x 2 seeds, img2img from each pose's colour block (strength
  0.75) with the round-5 reference through IP-Adapter. All 22 kept the headband, topknot and wraps.
  To choose between seeds Claude added a **palette fidelity check** (mean RGB distance to the sheet
  colours on the colour-block masks) and picked the lower score after a visual check for broken
  anatomy. Known flaws accepted: the top is always drawn lighter orange than `#D9482B`; RISE lost the
  yellow belt in both seeds; FALL's belt picked up green from the background.
- **Aotake (Stage 3):** the colour-block method worked first time for the reference (4 seeds, best
  palette score 43.9 for s303). Poses picked by palette score; anatomy only spot-checked.
- **Background (Stage 4):** 4 seeds. Measured the band the fighters stand in: s501 was darkest and
  least busy, but its red-gi contrast was only 1.83 against the sheet's planned 2.82 (CHANGE-BRIEF
  failure case 4). Edit on export: brightness x0.7 so the band matches the planned wall.
- **Export bug found in the engine:** in the Godot flow capture Aotake vanished at K.O. The exported
  `aotake/ko.png` had 2 opaque pixels: rembg's `isnet-anime` model treated the lying figure as
  background. Claude added a test that every state image shows a body (it failed on exactly that
  image) and re-exported the pose with a green chroma key, which the plain-green prompts allow.
- **Human / Claude / model:** images by SDXL + ControlNet OpenPose + IP-Adapter; colour blocks,
  scores, selections, edits and the Colab operation by Claude; Zhaohui approved downloading the
  results and the Drive authorisation, and clicked the Drive consent popup.
- **Still unresolved:** whether a human eye agrees with the score-based picks; the green FALL belt.

## 2026-10-06 — music loop (decision delegated to Claude)

> Written by Claude Code from the Colab run. Claude cannot listen; the pick is labelled
> "Decided by Claude" in ASSET-LOG and Zhaohui must re-judge it by ear.

- **Run trouble:** the first audio run stopped with `NameError: MUSIC_PROMPT`. The pip cell had
  broken Colab's run queue, so the prompts and helper cells never ran. Fixed by re-running cells one
  at a time and waiting for pip to finish first.
- **Takes (seeds 21-23, 30 s each, about 2 min each on T4):** Claude replaced listening with
  measurements (tracked tempo, spread of beat spacing, spread of 1 s loudness, quiet seconds, mel
  spectrograms in `design/generations/audio/checks/`). s21 stops at about 20 s. s23 tracks at 163
  bpm (double time) and is the loudest. **s22 accepted:** 79.8 bpm against the 80 asked, beat
  spacing spread 1.0 %, loudness spread 0.9 dB.
- **Loop:** 8 bars, 2.017-26.017 s (24.0 s), zero-crossing cuts, 40 ms crossfade, decoded peak
  -1.32 dBFS. The notebook's seam score went *up* from 8.8 to 15.8, past the "> 10 likely click"
  rule of thumb written into the notebook. Checked on the decoded OGG: the seam jump (0.013) is
  smaller than the 99th percentile of ordinary sample steps in the loop (0.014) and smaller than the
  steps in the first 5 ms after the cut (max 0.034). The cut lands on a drum attack, where steep
  steps are normal. So the score is misleading here rather than showing a click. Still needs a listen.
- **Human / Claude / model:** music by MusicGen medium; measurements, pick, loop cut and Colab
  operation by Claude; Zhaohui re-signed in to Google so the run could continue.
- **Still unresolved:** whether s22 actually sounds right for "Dusk ritual"; the SFX stage (needs
  the Stable Audio Open licence accepted and `HF_TOKEN` in Colab Secrets).

## 2026-10-06 — sound effects (decisions delegated to Claude)

> Written by Claude Code from the Colab run. Claude cannot listen; every pick is labelled
> "Decided by Claude" in ASSET-LOG and Zhaohui must re-judge them by ear.

- **Run trouble:**
  - Stable Audio Open would not import. diffusers 0.41 imports `FqnToConfig` from torchao, and
    Colab's preinstalled torchao is too old to have it. The install cell now uninstalls torchao,
    which diffusers only needs for quantization, and then the session is restarted.
  - The first download was refused with HTTP 403 (gated model) until Zhaohui accepted the licence
    on Hugging Face.
- **Takes:** 4 events x seeds 11-14, about 29 s each on T4. Claude measured each take instead of
  listening: lead-in before the sound reaches -20 dB of peak, length above -30 dB, share of energy
  inside the kept window, energy below 250 Hz, spectral centroid, and spectrograms
  (`design/generations/audio/checks/SFX_candidates_spectrograms.png`). The onset counter was too
  noisy in near-silent tails to be useful.
- **Picks:**
  - whiff s12: brightest, at 5792 Hz.
  - hit s12: 0 ms lead-in and the most low end, 92.7 % below 250 Hz.
  - block s14: a bright clack at 2780 Hz. It was picked mainly because it differs most from the
    hit, for the pillar *Read the opponent*.
  - K.O. s13: the ring ends at 2.36 s, inside the 2.5 s kept window, so the fade-out does not cut it.
  - Two hit and two block takes were rejected for a lead-in of more than 100 ms.
- **Human / Claude / model:** sounds by Stable Audio Open; measurements, picks, trims and the Colab
  operation by Claude; Zhaohui accepted the model licence and added `HF_TOKEN` to Colab Secrets.
- **Still unresolved:** whether the picks sound right in play, especially whether the block clack
  reads as a forearm block and whether the K.O. tone sounds like a gong.

---

# Assignment 3 — Blender MCP

## 2026-10-16 — MCP setup on Windows 11 (recorded by Claude Code as it happened)

> The commands and outputs below are copied from the session. Zhaohui adds their own experience
> (Blender install, enabling the add-on, the window session) underneath.

- **Starting state:** Blender was not installed. `uv`/`uvx` were not installed. Godot 4.7.2 sat in
  `Downloads\Godot_v4.7.2-stable_win64.exe` and was not on PATH.
- **uv:** the course says `brew install uv` (macOS). On Windows I used the PowerShell installer
  instead: `irm https://astral.sh/uv/install.ps1 | iex`. It installed **uv 0.13.1** to
  `C:\Users\rockefeller\.local\bin`, which is not on PATH until the shell restarts.
- **Registering the server: the chapter's line failed.**
  `claude mcp add -e DISABLE_TELEMETRY=true blender -- uvx mcp-for-blender` gave
  `Invalid environment variable format: blender, environment variables should be added as: -e KEY1=value1 -e KEY2=value2`.
  Claude Code 2.1.237's `-e` takes several values, so it read the server name as a second variable.
  **Working form:** put the name first:
  `claude mcp add blender -e DISABLE_TELEMETRY=true -- uvx mcp-for-blender`. `claude mcp get blender`
  then showed local scope, `DISABLE_TELEMETRY=true`, status "Connected". That status only means the
  `uvx` process started; it says nothing about Blender, which was not running or installed.
- **Server version:** `mcp-for-blender` **2.1.9**, the same version as the README the assignment
  quotes. Its subcommands are `install-addon`, `addon-paths`, `setup` and `update`.
- **Add-on:** `uvx mcp-for-blender install-addon` gave `Could not find a Blender user addons directory.
  Set BLENDERMCP_ADDONS_DIR to your Blender scripts/addons path, or install addon.py manually from
  the repo.` That is expected, because Blender was not installed yet. To retry after the install.
- **Not run on purpose:** `uvx mcp-for-blender setup` and the one-line installer, because they
  configure every MCP client on the machine.

## 2026-10-16 — Blender installed, add-on installed (recorded by Claude Code)

- **Blender:** Zhaohui installed it to `D:\blender\`. `blender.exe --version` reports
  **Blender 5.2.2 LTS** (built 2026-09-15). That is not the 5.1.2 the chapter used; recorded as a
  difference to watch, for example in glTF exporter defaults.
- `uvx mcp-for-blender addon-paths` found
  `%APPDATA%\Blender Foundation\Blender\5.2\scripts\addons` and marked it "(missing)". This time
  `install-addon` created it and wrote `blender_mcp.py` there. The earlier failure was only because
  Blender had not been installed.
- **What the installed add-on file says, read before enabling it:**
  - `bl_info` version **(1, 8)**, while the server package is 2.1.9. They are versioned separately.
  - The socket binds to `localhost`, port **9876**.
  - **Allow Telemetry** defaults to `False`.
  - Poly Haven, Sketchfab, Poly Pizza, Hyper3D, Hunyuan3D and Tripo are all controlled by
    `blendermcp_use_*` scene toggles.
  - The start button in this file is labelled **"Connect to Claude"**, not "Connect to MCP server"
    as the assignment says the code labels it. Another README/code difference.
  - A `load_post` handler restarts the server whenever a file loads, so the add-on really is
    always on while enabled. Turn it off in Preferences when not in use.

## 2026-10-16 — Connection test from Claude Code (recorded by Claude Code)

- The Claude Code session had started before `blender` was registered. Its tools only appeared
  partway through, as deferred tools ("still connecting", then listed), without a restart.
- `get_addon_status`: `up_to_date: true`, protocol **13** (expected 13), add-on **(1, 8)**,
  Blender **5.2.2 LTS**, source "native", `telemetry_consent: false`. Libraries Poly Haven,
  Sketchfab and Poly Pizza **off**; generators Hunyuan3D and Hyper3D **off**, Tripo "off (Premium
  only)". So the add-on was enabled and its server started, and nothing can be downloaded or
  generated; every shape has to be built with `execute_blender_code`.
- `get_scene_info`: unsaved default scene, EEVEE, unit scale **1.0**; Cube 2.0 × 2.0 × 2.0 at the
  origin, Light, Camera. The default cube is centred on its origin, which is failure case 3 in the
  brief before anything is built.
- The connection worked on the first call, so failure case 5 (no connection on Windows) did not
  happen. Whether Windows showed a firewall prompt is for Zhaohui to add; Claude cannot see it.

## 2026-10-16 — Second connection check before modelling (recorded by Claude Code)

- A new Claude Code session re-ran `get_addon_status` and `get_scene_info`. Every value matched
  the entry above: Blender 5.2.2 LTS, add-on (1, 8), protocol 13/13, `up_to_date: true`, all three
  libraries and all three generators off, `telemetry_consent: false`, unsaved default scene with
  the 2 m Cube at the origin ("below ground by 1.0"), Light and Camera, unit scale 1.0.
- Before building, Claude asked Zhaohui whether "Learn the window" was done and the numbers were
  final. Zhaohui answered "done, numbers final" and asked for the brief to be committed first:
  commit `780f39c` holds the A3 brief exactly as drafted, before any mesh was built.

## 2026-10-16 — PROP-LANTERN built (recorded by Claude Code)

- **Prompt passed to the MCP tool (`user_prompt`):** Zhaohui's instruction, verbatim: "严格按
  CHANGE-BRIEF.md 的 A3 规格，一个一个建（PROP-LANTERN → PROP-MAKIWARA → PROP-TAIKO），每个一个
  .blend 文件".
- **How:** one `execute_blender_code` script. It deleted the default Cube, built the six parts with
  `bmesh.ops.create_cone` / `create_cube` (segment counts set explicitly: base and shaft 8, roof
  and finial 6, `cap_tris=False` so caps stay n-gons), joined them into one object named
  `PROP-LANTERN`, and applied rotation and scale. No `bpy.ops` primitive was used, so no default
  32-segment cylinder appeared.
- **Part layout (Z ranges):** base r 0.30, 0.00–0.15 · shaft r 0.09, 0.15–0.70 · firebox
  0.36 × 0.36, 0.70–1.00 · lit panel 0.20 × 0.02 × 0.18 on the −Y face · roof r 0.30, 1.00–1.25 ·
  finial r 0.05, 1.25–1.40.
- **Colours:** three Principled BSDF materials, found by node type `BSDF_PRINCIPLED`, Base Color set
  on the node input. The hex values were converted from sRGB to linear first, because the node
  input is linear; typing the hex digits straight in as 0–1 floats would make the colour lighter in
  render than in the brief (part of failure case 6). Roughness 0.8. `diffuse_color` set too, but
  only for the viewport.
- **Check (`get_scene_info` + script):** size **0.60 × 0.60 × 1.40 m** (deviation 0.00 on all
  three), "on ground", min Z 0.0000, location (0, 0, 0), rotation (0, 0, 0), scale (1, 1, 1).
  **100 triangles** (budget 150; per part 28 + 28 + 12 + 12 + 10 + 10, exactly the brief's
  estimate). 46 faces: 28 quads, 12 tris, 6 n-gons; 0 non-manifold, 0 boundary edges, 0 loose
  verts. Materials Stone_6E6680, LitPanel_F5C542, Roof_4E475C.
- **Something the brief did not say:** a 6-segment cone is a hexagon, so its footprint is not
  square. With radius 0.30 the roof measures 0.52 (X) × 0.60 (Y). The whole lantern is still
  0.60 × 0.60 because the base octagon sets X.
- **`look` (angles, material shading):** reads as a lantern: wide roof over a box on a thin post,
  yellow panel visible from the front only.
- **Saved:** `blender/prop_lantern.blend` (97 573 bytes). The folder is new; the brief did not name
  one.

## 2026-10-16 — PROP-MAKIWARA built (recorded by Claude Code)

- Zhaohui confirmed PROP-LANTERN ("确认，建 MAKIWARA") before this was started.
- **Prompt passed to the MCP tool:** the same verbatim instruction as for the lantern.
- **How:** one `execute_blender_code` script, same helper functions as the lantern. It removed the
  lantern object and its now-unused meshes and materials from the open scene (the lantern was
  already saved in its own file), built the five parts, joined them into `PROP-MAKIWARA`, applied
  rotation and scale, and saved with "Save As" to a new file.
- **Part layout:** footing 0.30 × 0.30 × 0.10, Z 0.00–0.10 · post 0.12 × 0.08 × 1.40, Z 0.10–1.50 ·
  straw pad 0.16 × 0.06 × 0.30 on the −Y face, centre Z **1.20** · two rope bands, 8-segment
  cylinders r 0.12, 0.03 high, at Z 1.11 and 1.29, centred on the post+pad cross-section (Y −0.03).
- **Check:** size **0.30 × 0.30 × 1.50 m** (deviation 0.00), on ground, min Z 0.0000, rotation
  (0, 0, 0), scale (1, 1, 1). **92 triangles** (budget 120; 12 + 12 + 12 + 28 + 28, the brief's
  estimate). 38 faces: 34 quads, 4 n-gons; 0 non-manifold, 0 boundary edges, 0 loose verts.
  Materials Stone_6E6680, Wood_8A5A3B, Straw_D8B676, Rope_F2E6D0.
- **What `look` showed that the numbers did not:** an 8-segment cylinder is round, but the pad and
  post are a 0.16 × 0.14 box. To enclose that box the bands need r ≈ 0.12, so they stick out
  about 4 cm past the pad on each side and read more like **flat collars than tight rope**. The
  brief's shape list ("cylinders, 8 segments") allows it. Raised with Zhaohui rather than changed.
- **Saved:** `blender/prop_makiwara.blend` (98 228 bytes).

## 2026-10-16 — PROP-MAKIWARA rope bands reshaped (recorded by Claude Code)

- Zhaohui first picked "squash the bands into an ellipse about 0.20 × 0.18". **That option was
  Claude's mistake.** Checking before building showed that a squashed regular octagon cuts its
  corners, so at 0.20 × 0.18 the pad's four corners would poke through the rope. Enclosing the
  0.16 × 0.14 cross-section takes about 0.23 × 0.20, barely smaller than the 0.24 × 0.24 already
  there. Claude told Zhaohui and asked again. Zhaohui chose a **chamfered rectangle 0.19 × 0.17**.
- **Prompt passed to the MCP tool:** "倒角矩形 0.19×0.17" (Zhaohui's answer, verbatim).
- **How:** edited the saved mesh with bmesh. It deleted the faces that use the Rope material, then
  built each band from 8 hand-placed vertices (half-extents 0.095 × 0.085, 0.02 m chamfers,
  centred at Y −0.03): 8 side quads + two 8-gon caps, the same topology as an 8-segment cylinder.
  The chamfer line has x + y = 0.160 and the pad corner has 0.150, so the rope clears the corners
  by about 7 mm. Normals recalculated.
- **Check:** size still 0.30 × 0.30 × 1.50 m, on ground, rotation (0, 0, 0), scale (1, 1, 1),
  **92 triangles**, 38 faces (34 quads, 4 n-gons), 0 non-manifold, 0 boundary edges. The rope
  now sticks out 1.5 cm past the pad instead of 4 cm.
- **Recorded difference from the brief:** the brief says "cylinders, 8 segments" for the bands.
  They keep the segment count and triangle cost but are no longer round.
- **Mistake along the way:** a `look` with `distance=0.9` framed the object's centre (Z 0.75), not
  the pad, so all four tiles showed only the post. The default framing worked.
- File re-saved in place: `blender/prop_makiwara.blend` (98 211 bytes).

## 2026-10-16 — PROP-TAIKO built (recorded by Claude Code)

- Zhaohui confirmed PROP-MAKIWARA ("确认，建 TAIKO") before this was started.
- **Prompt passed to the MCP tool:** the same verbatim instruction as for the lantern.
- **How:** unlike the first two, each part was its own object with its position and rotation set
  on the object, so the rotation step could be checked. The drum body and both heads were built
  as Z-axis 12-segment cylinders with object **rotation X = 90°** (printed as 90.0 before apply);
  the legs lean ±14.4° about Y. `transform_apply(rotation, scale)` on all six printed rotation
  (0, 0, 0) for every part; then they were joined into `PROP-TAIKO` and applied again.
- **Part layout:** base bar 0.70 × 0.12 × 0.06, Z 0.00–0.06 · drum body r 0.30, 0.51 long on Y,
  centre Z **0.62** · two heads r 0.33, 0.02 thick, at Y ±0.265 (faces ±Y) · two legs
  0.06 × 0.10 × 0.42 from the bar ends up under the drum. The 0.95 height comes from the heads
  (0.62 + 0.33); the body is 0.60 across as in the brief.
- **Error, caught by the script's own check (failure case 3 happened):** after the join the mesh
  ran Z **−0.03 to 0.92**, and the object sat at location (0, 0, 0.03). `get_scene_info` alone
  would have said "size 0.7x0.55x0.95, on ground" and hidden it, because it measures the world box.
  The cause: `join` keeps the *active* object's origin, and the active part was the base bar, whose
  origin was at its own centre (Z 0.03). The lantern and makiwara had not hit this because there
  every part's offset was baked into the mesh and each object sat at the origin.
  **Fix:** moved the mesh up by the object's location (`mesh.transform(Translation(location))`) and
  set location to (0, 0, 0). After: mesh Z 0.0000–0.9500, object at (0, 0, 0).
- **Check:** size **0.70 × 0.55 × 0.95 m** (deviation 0.00), on ground, min Z 0.0000, rotation
  (0, 0, 0), scale (1, 1, 1). **168 triangles** (budget 200; 44 + 44 + 44 + 12 + 12 + 12, the
  brief's estimate). 60 faces: 54 quads, 6 n-gons; 0 non-manifold, 0 boundary edges, 0 loose
  verts. Tallest axis is Z (Y in Godot), as failure case 1 requires. Materials Stand_1E1B22,
  Lacquer_D9482B, Head_F2E6D0.
- **What `look` showed:** reads as a taiko (red barrel, pale heads facing front and back, dark
  cradle). From the side the stand is only 0.12 m deep under a 0.55 m drum, so it looks like a
  single post and the drum looks as if it could tip. The brief's shape list (one bar, two legs)
  allows it. Raised with Zhaohui.
- **Saved:** `blender/prop_taiko.blend` (98 300 bytes).

## 2026-10-16 — All three props confirmed; files re-checked headless (recorded by Claude Code)

- Zhaohui kept the taiko stand as built ("保持原样，确认").
- Each saved file was reopened in a separate headless Blender
  (`blender.exe -b <file> --factory-startup --python chk.py`), not in the live session, because the
  add-on's `load_post` handler restarts the MCP server when a file is opened.

  | File | Object | Size (m) | min Z | loc / rot / scale | Tris (budget) |
  |---|---|---|---|---|---|
  | prop_lantern.blend | PROP-LANTERN | 0.60 × 0.60 × 1.40 | 0.0 | 0 / 0 / 1 | 100 (150) |
  | prop_makiwara.blend | PROP-MAKIWARA | 0.30 × 0.30 × 1.50 | 0.0 | 0 / 0 / 1 | 92 (120) |
  | prop_taiko.blend | PROP-TAIKO | 0.70 × 0.55 × 0.95 | 0.0 | 0 / 0 / 1 | 168 (200) |

- Not done yet: glTF export and the Godot `prop_room` scene. Nothing committed after `780f39c`.

## 2026-10-16 — glTF export and the Godot prop room (recorded by Claude Code)

- Zhaohui: "你就看着做吧，不需要问我", so the export and the Godot side went ahead without
  further questions.
- **Export:** headless Blender, one run per `.blend`, `export_scene.gltf` with `export_format='GLB'`,
  `use_selection=True` (only the prop mesh), `export_yup=True` (the default), `export_apply=True`,
  cameras and lights off. Before that, the exporter options were read from 5.2.2's RNA, because
  the brief warned that its defaults might differ from 5.1.2. `export_yup` defaults to True and
  `export_apply` to False; `export_format`'s enum list came back **empty** from RNA (it is filled in
  dynamically), so 'GLB' was passed inside try/except. It was accepted.
  Output: `godot/props3d/models/prop_lantern.glb` (7 840 B), `prop_makiwara.glb` (7 608 B),
  `prop_taiko.glb` (10 580 B).
- **Godot:** Godot 4.7.2 is not on PATH, and `Downloads\Godot_v4.7.2-stable_win64.exe` is a
  **folder** (the unzipped archive), not the program. The console build inside it worked:
  `...\Godot_v4.7.2-stable_win64.exe\Godot_v4.7.2-stable_win64_console.exe --headless --path godot --import`.
  `godot/project.godot` had SHA-1 `d3999dd…` before and after every Godot run, so the import did
  not drop the `[physics]` lines this time (unlike the editor save behind `4f0c644`).
- **Scene** `godot/props3d/prop_room.tscn`, written by hand: a 6 × 4 m floor with its top at y = 0,
  one DirectionalLight3D with shadows, one Camera3D, a WorldEnvironment for ambient light only,
  the three GLBs placed at y = 0 (x −1.6, −0.6, 0.5), and a 0.3 × 1.70 × 0.2 m grey reference box
  at x 1.6. The brief says "floor, one light, one camera". The WorldEnvironment is an addition
  (ambient light, not a second light) so faces turned away from the sun are not black.
- **Headless check** `godot/tests/check_props3d.gd` (failure cases 1, 2, 3, 4, 6):
  `--headless --path godot --script res://tests/check_props3d.gd` printed **43 checks, 0 failed**.

  | Prop | AABB x × y × z (m) | min y | node scale / rot | tris (budget) | albedo |
  |---|---|---|---|---|---|
  | PROP-LANTERN | 0.600 × 1.400 × 0.600 | 0.0000 | 1 / 0 | 100 (150) | 6e6680 f5c542 4e475c |
  | PROP-MAKIWARA | 0.300 × 1.500 × 0.300 | 0.0000 | 1 / 0 | 92 (120) | 6e6680 8a5a3b d8b676 f2e6d0 |
  | PROP-TAIKO | 0.700 × 0.950 × 0.550 | 0.0000 | 1 / 0 | 168 (200) | 1e1b22 d9482b f2e6d0 |

  The tallest axis is Y for all three. The albedo hex matches the brief exactly, so converting the
  colours from sRGB to linear in Blender survived the round trip (failure case 6 did not happen).
  The 2D game's own suite still passes (94 checks, 0 failed).
- **Renders** `godot/tests/capture_props3d.gd` (needs a window) → `evidence/props3d/prop_room_front.png`
  and `prop_room_back_low.png`. **First render:** the taiko's `#F2E6D0` head came out pure white and
  the lantern panel very saturated, because the sun at energy 1.0 plus ambient 0.6 clipped pale
  colours facing it. **Fix:** sun 0.7, ambient 0.35; after that the head reads cream. From behind:
  no missing faces, and the lantern panel and makiwara pad face +Z (the camera) as built
  (Blender −Y → Godot +Z). This is Claude looking at two still images, not the walk-around check in
  failure case 7, which stays Zhaohui's.
