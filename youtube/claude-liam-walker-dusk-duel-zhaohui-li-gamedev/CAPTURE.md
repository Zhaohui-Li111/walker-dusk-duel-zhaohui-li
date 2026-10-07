# CAPTURE — engine evidence for "Dusk Duel, Generated"

All gameplay and engine images in the film come from Godot itself. Nothing was redrawn.

## Source

| | |
|---|---|
| Game folder | `godot/` (holds `project.godot`) |
| Git revision | `4e0cf14` (working tree clean for `godot/` at capture time) |
| Build id | `b640eef8ec014773c8679c3d229cc78b0532682f852a67ab4f3e50c18bb107e0` |
| Hash method | SHA-256 over `"<relpath>\0<sha256(file)>\n"` for all 95 files in `godot/` except `.godot/` and `*.uid`, paths sorted |
| Per-file manifest | [SOURCE-SNAPSHOT.json](SOURCE-SNAPSHOT.json) |
| Engine | Godot `4.7.2.stable.official.ed1daf0bf`, GL Compatibility |
| Host | Windows 11 Home China 10.0.26200 |

## Isolated copies, and the harness changes

Captures ran against copies, so the project itself was not touched. `tools/make_capture_copy.sh`
rebuilds them.

- **`capture/game/`**: a copy of `godot/` with two changes, both harness only:
  1. `tools/capture_driver.gd` is added as an autoload.
  2. The window override is raised from 1280 × 720 to 3840 × 2160.
- **`capture/game-states/`**: the same copy, with `tools/states_driver.gd` as the autoload instead.

Neither driver edits a game script. `capture_driver.gd` only sends `InputEventKey` events, the same
events a keyboard produces. Health, state and position are never set; Aotake is the game's own
seeded `CpuController`. `states_driver.gd` does stage poses (it sets states and positions, as
`godot/tests/capture_states.gd` does), so its image is labelled **staged pose** on screen.

## run-01: gameplay with the slice's own audio

```bash
godot --path capture/game --resolution 3840x2160 \
  --write-movie capture/run-01.avi --fixed-fps 60 --disable-vsync
```

| | |
|---|---|
| Output | `capture/run-01.avi`: MJPEG 3840 × 2160 at 60 fps, plus PCM s16le 48 kHz stereo (`ffprobe`) |
| SHA-256 | `0cb0be3808e3481627c3d9be408995ffd812cbe277446d88f7ea5c3e1e8d20d0` |
| Length | 1768 frames, 29.467 s |
| Method | scripted keyboard input (`tools/capture_driver.gd`), not a human playtest |
| Audio | the game's own mix (SFX bus + Music bus → Master), recorded by Movie Maker in the same file as the frames |
| Audio level | mean −15.3 dB, max 0.0 dBFS: the slice's master peaks at full scale when a sound effect lands on the music. This is the game's own mix and was not changed. |

**Offline rendering.** Movie Maker writes one frame per physics tick at a fixed 60 fps, however
long each frame takes to encode (about 14 minutes in total here). This is not a frame-rate
measurement. With `--fixed-fps 60` and 60 Hz physics, capture frame *n* is driver tick *n*.

**4K is native.** The HUD text in an extracted 3840 × 2160 frame has smooth glyph edges, so the
frame was rendered at 4K, not upscaled. The art itself is still the generated sprites at their
exported size (108 × 158 for Akaken), scaled by the 640 × 360 canvas stretch.

**What the driver does.**
1. On the title screen, waits 90 ticks, then presses Enter.
2. At fight tick 20, throws a punch from far away. This is the storyboard's opening whiff.
3. Walks in, then alternates punch and kick.
4. Blocks every other attack Aotake starts at close range, and takes the rest.
5. Pauses once (Esc at fight tick 640, resumed 100 ticks later).
6. After the K.O., waits on the result screen and presses Enter for a rematch.

Every press and release is in `capture/run-01-inputs.jsonl`.

**The recorded run ended early. Accepted and disclosed.** The movie stopped at frame 1768, on
the "AKAKEN WINS" result screen. That is four ticks before the driver's scripted rematch press,
so the driver never reached its end. As a result, `run-01-driver.json` and `run-01-inputs.jsonl`
were not rewritten by this run; they are from the headless probe run of the same driver:

```bash
godot --headless --path capture/game --fixed-fps 60
```

The probe uses the same seed and the same inputs, so it is deterministic, and its assertions
passed: opening whiff, a hit, a block, Akaken hurt, one K.O. of Aotake, one pause, rematch started.
The film needs nothing after the result screen.

The recorded footage was checked against the probe log by extracting frames at the logged ticks
(time ≈ tick / 60):

| Probe log | Frame in run-01 |
|---|---|
| tick 180, P1 punch whiff | 3.0 s: Akaken's jab extended, no contact |
| ticks 790–890, pause | 13.5 s: PAUSED overlay |
| tick 1531, last hit | 25.6 s: K.O. banner, Aotake down |
| result phase | 29.3 s: "AKAKEN WINS" |

The cause of the early stop was not found; Movie Maker exited with code 0.

## states-run: staged pose with collision boxes (B07)

```bash
godot --path capture/game-states --resolution 3840x2160 \
  --write-movie capture/states-run.avi --fixed-fps 60
```

- `godot/tests/capture_states.gd` saves the viewport texture. On this 1536 × 960 display, that
  texture was clamped to 1924 × 1082 even with `--resolution`.
- So the staged poses were rendered inside the main scene by `states_driver.gd`, where Movie Maker
  renders 3840 × 2160.
- Frame 6 (the punch pose, F1 boxes on) was extracted unchanged as
  `capture/evidence/states/punch_4k.png`.
  - SHA-256: `c10e40e555083ce4e8a7f658742c723d6b4bf7c3a11163bfe8a12969408bef33`
  - `states-run.avi` SHA-256: `c63c35b6f33e67a8abb5476eeeb2897d832ea7418579357161654477db622c69`
- In this staged pose the hitbox is drawn faint, because no attack is active. Aotake has no punch
  image, so his state falls back to kick (CHARACTER-SHEET appendix).

## How the clips were cut (tools/build_media.py)

- **Real speed.** No `setpts`, no retiming. The 60 fps capture is written at the film's 30 fps by
  dropping alternate frames.
- **Length.** Each narrated clip is exactly its narration's measured length, starting at the
  window in `tools/windows.json`.
- **Framing.** The gameplay is inset at 3200 × 1800 (5× the 640 × 360 canvas) on the cream page.
- **Labels.** A persistent label sits in the bottom band:
  - "SCRIPTED INPUT · native 4K Godot capture of the slice · not a human playtest"
  - "ENGINE CAPTURE · collision boxes on (F1) · staged pose, not gameplay"
  - B13 also carries "SLICE AUDIO · no narration" in the top band.

| Beat | Source interval | What happens (verified on extracted frames) |
|---|---|---|
| B02 | 15.00–27.39 s | mid-round exchanges up to the K.O. |
| B07 | punch_4k.png, held | staged punch pose, boxes on |
| B09 | 4.50–13.08 s | Akaken's jab hits at about +0.45 s: spark, Aotake's bar drops |
| B12 | 2.40–11.66 s | opening whiff (+0.6 s), a block (+1.4 s), a clean hit (+2.6 s) |
| B13 | 12.20–29.40 s | pause → hits, blocks, whiffs → K.O. → music stops → result screen, **with the game's audio** |

## B13 audio route

- `audio/B13-slice.wav` is `capture/run-01.avi`'s own audio over the same 12.20–29.40 s interval as
  B13's frames.
- It is cut with ffmpeg (`-ss`/`-t`), with a 20 ms fade at each cut and no other processing.
- SHA-256: `3b0c50a2dfa7f0c01fc249800e8b61be938412c3e91abb45215b155268149aeb`
- The beat's `audio_file` names it, a per-beat audio input that `compile.py` supports. Why this
  route was used is in [BUILD-LOG.md](BUILD-LOG.md) §1.
