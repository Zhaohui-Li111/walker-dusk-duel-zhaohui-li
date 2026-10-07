# walker-dusk-duel

A one-on-one cartoon martial-arts duel at dusk, built as the **asset slice** for CSYE 7270
Assignment 2 (Generate Art, Sound, and Music for Your Game). You play **Akaken** (red gi, topknot,
big wrapped fists) against the CPU-controlled **Aotake** (teal robe, straw hat, long legs) in a stone
temple courtyard.

- **Started from:** an empty Godot 4.7 project. Project settings (640×360 viewport shown at 2×) match
  my earlier `walker-jumpman` checkout; no code was copied from it. See [SOURCES.md](SOURCES.md).
- **Engine:** Godot 4.7.2 stable (GL Compatibility renderer), tested on Windows 11.
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
