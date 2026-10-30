# walker-dusk-duel

A one-on-one cartoon martial-arts duel at dusk, built as the **asset slice** for CSYE 7270
Assignment 2 (Generate Art, Sound, and Music for Your Game). You play **Akaken** (red gi, topknot,
big wrapped fists) against the CPU-controlled **Aotake** (teal robe, straw hat, long legs) in a stone
temple courtyard.

- **Started from:** an empty Godot 4.7 project. Project settings (640×360 viewport shown at 2×) match
  my earlier `walker-jumpman` checkout; no code was copied from it. See [SOURCES.md](SOURCES.md).
- **Engine:** Godot 4.7.2 stable (GL Compatibility renderer), tested on Windows 11.
- **Assignment 3 tools:** Blender 5.2.2 LTS · mcp-for-blender 2.1.9 (Blender add-on 1.8) · see
  [Assignment 3](#assignment-3-three-3d-props) below.
- **Design:** [CONCEPT.md](CONCEPT.md) · [STORYBOARD.md](STORYBOARD.md) ·
  [CHARACTER-SHEET.md](CHARACTER-SHEET.md) · [CHANGE-BRIEF.md](CHANGE-BRIEF.md)
- **Process:** [FRICTIONAL.md](FRICTIONAL.md) · [ASSET-LOG.md](ASSET-LOG.md) (one row per generation) ·
  [TEST-REPORT.md](TEST-REPORT.md)

## Run it

1. Install Godot 4.7.x.
2. Open `godot/project.godot` in the editor and press F5, or from a terminal:

```bash
godot --path godot
```

Automated checks (headless, ~10 s):

```bash
godot --headless --path godot --script res://tests/test_runner.gd
```

## Controls

| Action | Keyboard | Gamepad |
|---|---|---|
| Move | A / D or ← / → | D-pad / left stick |
| Jump / crouch | W / S or ↑ / ↓ | D-pad / left stick |
| Punch / kick / block | J / K / L | X / A / RB |
| Start, rematch | Enter or Space | — |
| Pause / resume (quit on the result screen) | Esc or P | Start |
| **Mute music / mute effects** | **M / N** | — |
| Show collision boxes | F1 | — |

## What the slice demonstrates

- One static image per state (idle, walk, crouch, rise, fall, punch, kick, block, hurt, K.O., win),
  swapped by the fighter state machine, facing the opponent, aligned to the planned hurt/hit boxes.
- A generated temple-courtyard background.
- Four event sounds — whiff, hit, block, K.O. — each played exactly once per event by an
  `AudioDirector` that only listens to game signals, and a music loop that starts on the title,
  ducks on pause, stops at K.O. and restarts on rematch.
- A full round: title → round call → fight → K.O. → winner pose → rematch.

## Generated assets and tools

Art: SDXL base 1.0 + xinsir OpenPose ControlNet + IP-Adapter, img2img from colour-block mannequins,
run on free Google Colab (`notebooks/generate_images.ipynb`). Audio: Stable Audio Open 1.0 and
MusicGen medium (`notebooks/generate_audio.ipynb`). Models, versions and licences: [SOURCES.md](SOURCES.md).
Code, prompts, pose skeletons and colour blocks were written by Claude Code; see SOURCES.md for the
split between Claude, the models and me.

## Known limitations

- Aotake has 5 poses, so its walk / jump / win reuse other images (see CHARACTER-SHEET appendix).
- The accepted Akaken reference has a blank face (no eyes); it barely reads at 112 px.
- The CPU opponent is simple and was tuned by automated tests, not yet by playtesting.
- Akaken's top is drawn lighter than the sheet's orange; the RISE image has lost the belt and the
  FALL belt is green.
- All audio picks were made by measurement (Claude cannot listen) and still need a human ear; see
  TEST-REPORT.
- Music is MusicGen (CC-BY-NC 4.0) and SFX are Stable Audio Open (Stability AI Community License):
  fine for coursework, not for commercial release.

## Assignment 3: three 3D props

Three low-poly props built in **Blender 5.2.2** through the **Blender MCP** (Claude Code drove
Blender with Python; no asset libraries or 3D generators were used), exported to glTF and set up
in a small separate Godot 3D scene. The 2D game does not use them yet.

| Prop | Size W × D × H (m) | Triangles (budget) |
|---|---|---|
| Stone lantern (`PROP-LANTERN`) | 0.60 × 0.60 × 1.40 | 100 (150) |
| Makiwara striking post (`PROP-MAKIWARA`) | 0.30 × 0.30 × 1.50 | 92 (120) |
| Taiko drum on a stand (`PROP-TAIKO`) | 0.70 × 0.55 × 0.95 | 168 (200) |

- **Spec and results:** [CHANGE-BRIEF.md](CHANGE-BRIEF.md), Assignment 3 (spec, predicted failure
  cases, build result). **Process log:** [FRICTIONAL.md](FRICTIONAL.md), Assignment 3.
  **Results:** [TEST-REPORT.md](TEST-REPORT.md), Assignment 3. **Interface notes:**
  [BLENDER-NOTES.md](BLENDER-NOTES.md).
- **Code Claude ran in Blender:** `tools/blender/build_<asset>.py` (verbatim), plus
  `export_glb.py`, `check_blend.py`, and `reproduce.py` (re-runs the builds into a scratch folder).
- **Files:** `blender/*.blend` (sources) → `godot/props3d/models/*.glb` →
  `godot/props3d/prop_room.tscn` (floor, one light, a camera and a 1.70 m reference box).
  Renders: [evidence/props3d/](evidence/props3d/).
- **Open the scene:** open `godot/project.godot` in the Godot editor and double-click
  `props3d/prop_room.tscn` in the FileSystem dock, or:

```bash
godot --editor --path godot res://props3d/prop_room.tscn
```

- **Check against the brief** (size ±0.02 m, transforms applied, tallest axis, gap to the floor,
  triangle budget, colours; 49 checks). Run `--import` once after cloning:

```bash
godot --headless --path godot --import
```

```bash
timeout 120 godot --headless --path godot --script res://tests/check_props3d.gd --fixed-fps 60
```

- **A3 film: "Dusk Duel, Measured".** A Brutalist explainer made with the `godot-gamedev` skill in
  walker mode. It is 5:22 long, 3840 × 2160, 30 fps.
  - **Link:** https://drive.google.com/file/d/1D2tbScAO8qrlzJBOb68VAFXHdIzu7u_f/view?usp=sharing
  - **File name:** `claude-liam-walker-dusk-duel-zhaohui-li-a3-gamedev.mp4`
  - **SHA-256:** `9331a6244a9c8e33ef414912a8e3d0a02cff78ce59994771401339ab61c771d2`. The copy on Drive was downloaded
    without signing in and gives the same hash (2026-10-16).
  - **Game source shown:** `godot/` at `1e88b83`.
  - **Film source and evidence:**
    [youtube/claude-liam-walker-dusk-duel-zhaohui-li-a3-gamedev/](youtube/claude-liam-walker-dusk-duel-zhaohui-li-a3-gamedev/).
    Start with BUILD-LOG.md, FACTCHECK.md and SOURCES.md.
- **A3 known limitations:** the checks prove numbers, not looks; the look check is the human
  one in TEST-REPORT. The makiwara rope bands are chamfered rings rather than the round cylinders
  the brief first said. The taiko stand is shallow (0.12 m) and looks tippy from the side. The
  prop room is not connected to the 2D game.

- Opening the project in the Godot editor re-saves `godot/project.godot` and drops the
  `[physics]` lines (60 is the default value). Run `git status` after an editor session.

## Assignment 5: shaders and materials

Two hand-written shaders and the materials that use them, plus a hint experiment. **Every
`.gdshader` file in `godot/shaders/` was typed by Zhaohui**; no agent session changed that
folder (`git log -- godot/shaders/` shows only Zhaohui's commits).

- **Shader from code — the hurt flash.** `godot/shaders/hurt_flash.gdshader` (canvas_item) tints a
  fighter's sprite red while that fighter is in `"hurt"`: `COLOR.rgb = mix(COLOR.rgb,
  flash_color.rgb, hurt_amount);`. The driver `godot/fighter/hurt_flash.gd` gives each fighter
  its own material and sets `hurt_amount = stun / HITSTUN` every physics tick, so the flash
  follows game time (0.367 s) at any frame rate.
- **Textured shader — granite.** `godot/shaders/granite.gdshader` (spatial) samples a colour texture
  with `source_color`, and a roughness map and an OpenGL normal map as data, with four uniforms in
  the groups `surface` and `detail`. Two materials use it in `godot/props3d/prop_room.tscn`: the
  floor (`granite_floor.tres`) and a new stone plinth (`granite_plinth.tres`). The A3 props have no
  UVs, which is why the floor and the plinth carry it.
- **Hint experiment.** `godot/hint_experiment/hint_experiment.tscn`: one 3 × 1 grey PNG (written by
  `write_hint_png.gd`) read by two samplers of `godot/shaders/hint_experiment.gdshader`, with and
  without `source_color`, on two unshaded quads.
- **Documents:** [CHANGE-BRIEF.md](CHANGE-BRIEF.md) (Assignment 5 and Revisions 2–8) ·
  [CLAUDE.md](CLAUDE.md) · [godot/MATERIALS.md](godot/MATERIALS.md) ·
  [TEST-REPORT.md](TEST-REPORT.md) (Assignment 5) · [FRICTIONAL.md](FRICTIONAL.md) ·
  texture credits in [godot/props3d/textures/ATTRIBUTION.md](godot/props3d/textures/ATTRIBUTION.md).
- **Controls added:** none. Play as before; the flash shows on whichever fighter is hit.

Run the A5 checks through the wrapper (set `GODOT` to the console build if `godot` is not on
PATH; run `--import` once after cloning):

```bash
./scripts/run-test.sh test_hurt_flash.gd 30
```

```bash
./scripts/run-test.sh test_hurt_flash.gd 60
```

```bash
./scripts/run-test.sh test_hurt_flash.gd 144
```

```bash
./scripts/run-test.sh test_materials.gd 60
```

```bash
./scripts/run-test.sh calibrate_normal_map.gd 60
```

Expected: 69 / 0 at each rate, 96 / 0, and exit 0. The earlier suites stay at 94 / 0
(`test_runner.gd`) and 49 / 0 (`check_props3d.gd`). In-engine captures need a window:

```bash
godot --path godot --script res://tests/capture_a5.gd
```

- **A5 known limitations:**
  - The headless tests prove that the shaders parse and are driven and wired as specified, not
    how anything looks; the look is the human checks in TEST-REPORT.
  - A second hit cannot land during hurt in real play, so the retrigger rule is checked only with
    labelled test setup (CHANGE-BRIEF Revisions 6–7).
  - `Engine.time_scale` does not slow the fight or the flash (Revision 7).
  - In the Compatibility renderer the hint experiment shows the same values on both quads; the
    Forward+ prediction does not apply (TEST-REPORT).
  - The BoxMesh UVs stretch the granite (2.25 : 1 on the floor), so it reads as planks
    (MATERIALS.md findings 1–3).
- **A5 film:** *to be added.*

## Final film

**"Dusk Duel, Generated"**: a Brutalist explainer made with the `godot-gamedev` skill in walker
mode. It is 5:13 long, 3840 × 2160, 30 fps.

- **Link:** https://drive.google.com/file/d/1p-VSLTgdrnx0TcIbniZmUvhgoe0bU3iV/view?usp=drive_link
- **File name:** `claude-liam-walker-dusk-duel-zhaohui-li-gamedev.mp4`
- **SHA-256:** `544bc91d9aeef43274419d6768ce84d1c7b81f412c091a2c9092511423928e39`
- **Source revision shown:** `4e0cf14`. Later commits add only film files and documentation;
  `godot/` is unchanged.
- **Film source and evidence:** the beat sheet, narration, prompts, captures, fact check and QC
  reports are in [youtube/claude-liam-walker-dusk-duel-zhaohui-li-gamedev/](youtube/claude-liam-walker-dusk-duel-zhaohui-li-gamedev/).
  Start with BUILD-LOG.md and CAPTURE.md.
- **Slice audio segment:** 3:24–3:42 (B13). It plays the game's own recorded sound, with no
  narration over it.
