# BUILD-LOG — "Dusk Duel, Generated" (godot-gamedev, walker mode)

Every deviation, workaround and failure in building this reel. Built by Claude Code (Opus 5.5)
for Zhaohui Li on 2026-10-06.

Host: Windows 11 Home China 10.0.26200 · Python 3.12 · Node 22 · Godot 4.7.2 · ffmpeg 9.0.2 ·
Kokoro `am_onyx` (local, free).

The toolkit environment (ffmpeg, Kokoro model files, Remotion node modules, and the one-line
`npx` fix in `runtime/scripts/remotion_scenes.py`) was already installed on this machine from
Zhaohui's Assignment 1 reel. Its BUILD-LOG covers those. **No toolkit file was changed for this
reel.**

## 1. The slice's own audio: how it gets into the film

**The assignment says:** include at least one clearly labelled segment where the slice's own
audio is audible without narration. If the skill silences captured gameplay by default, ask for
the course-provided method rather than dubbing sounds in afterwards.

**What the toolkit does:**
- `compile.py` encodes every beat's video with `-an`, so captured video is silent.
- Each beat's sound comes from `audio_file`, or from `audio/<beat>.mp3` by default.
- Only a `source_report` beat (`audio_policy: "preserve"`) keeps its embedded sound.
- `godot-waikthrough/references/capture-and-coverage.md` forbids labelling gameplay as a
  `SOURCE_REPORT` to get around this.
- **So yes: gameplay is silent by default.**

**What was done:**
- Zhaohui was asked. They chose to proceed with the route below and, at the same time, ask the
  course for its method; the beat will be redone if the course names a different one.
- Movie Maker recorded the game's own audio mix in the same AVI as the frames.
- For B13 only, the beat's `audio_file` points at that recording's audio for exactly the same
  interval as its frames (`audio/B13-slice.wav`, 20 ms fades at the cuts, nothing else).
- `audio_file` is a per-beat input `compile.py` already reads. Its audibility and duration checks
  still apply.
- No sound was added, replaced, re-timed or mixed. B13 has no narration, and it is labelled
  "SLICE AUDIO · no narration" on screen.

**Still open:** whether this matches the course-provided method. Zhaohui is asking the course.

## 2. Silences the skill requires but the toolkit does not implement

- **The rules:**
  - ai-explainer asks for `lead_silence_s: 0.8` on the hesitant-writer beat.
  - OUTRO-LOCK asks for a 1.0 s silent tail hold on the title card.
- **The gap:** nothing in `runtime/` reads either field (`grep` finds no consumer).
- **The fix:**
  - `tools/pad_audio.py` adds those silences to the Kokoro takes with ffmpeg (`adelay`, `apad`).
  - It keeps the originals in `mp3/raw/`.
  - The beat durations come from the padded files.
  - B01: 10.52 → 11.32 s. B18: 3.39 → 4.39 s.

## 3. Hesitant writer cannot correct a phrase

- **The rule:** ai-explainer's EXECUTIVE-SUMMARY LAW says to put the whole misconception phrase in
  `triggerWords`.
- **The problem:** `BrutalistHesitantWriter.tsx` matches single whitespace-separated tokens
  (`triggers.indexOf(core.toLowerCase())`). The first pilot, with the phrase
  "made this game's art and sound", typed the sentence but never corrected it (seen on a rendered
  frame).
- **The fix:**
  - The overview now reads "Free models **designed** this game's art and sound."
  - The writer corrects the one word that carries the misconception, "designed" → "drew".
  - The corrected sentence stands alone as the reel's claim.

## 4. Capture

See [CAPTURE.md](CAPTURE.md).

- **Early stop.** The recorded run stopped at frame 1768, four ticks before the scripted rematch.
  The driver summary therefore comes from the deterministic headless probe. The footage was checked
  frame by frame against that log. Accepted, because the film needs nothing after the result screen.
- **4K staged still.** `tests/capture_states.gd` produced 1924 × 1082 images on this display, so
  the staged pose for B07 was re-rendered inside the main scene through Movie Maker at 3840 × 2160.

## 5. Narration: TTS respelling and a one-word change to the hello

- **How it was checked:** every Kokoro take was transcribed with faster-whisper (`base.en`) and
  read back.
- **What it found:**
  - "Zhaohui Li" came back as "J. Huey lied".
  - Akaken and Aotake came back garbled.
  - The Swedish hello "Hej" came back as "hedge".
- **What was changed:**
  - The narration text respells the names: Jow-hway Lee, Ah-kah-ken, Ow-tah-keh. This is recorded
    in the beat sheet's `tts_respelling` field.
  - The greeting became "Hola, Liam".
  - "s201" became "seed two-oh-one", and "K.O." became "knockout".
  - The changed beats were re-voiced and re-checked.
- **On screen:** text always uses the real spellings.

## 6. Visual QC found and fixed before the full render

Single-frame previews were rendered with `npx remotion still` (inspection only; every final
clip went through `runtime/scripts/remotion_scenes.py`).

- **Code excerpts:**
  - At the default size, B06 showed only 13 of 18 lines.
  - The Source notes column overflowed its cards.
  - Fix: excerpts shortened to what fits at 24 px (B06 32–44, B08 160–172, B11 100–108,
    B14 349–358), and notes cut to two or three short cards.
- **Figures:**
  - The first figures were 3200 × 1500 inside a panel of about 2.75:1, so they letterboxed small
    and the palette text was tiny.
  - Fix: rebuilt at 3200 × 1160 with 52–72 px labels.
- **Gameplay labels:**
  - The labels first sat over the bottom edge of the game frame and were 23 px effective at 1080p.
  - Fix: moved into the 180 px bands inside the 5% safe area, at 52 px.
- **B15:** the mute test's output line overflowed its card, so it is now shown verbatim in the
  wide bottom bar.

## 7. GATE T: what it flagged in captures and figures, and how the typography was checked

The first type check failed 7 beats on contrast: B02, B04, B05, B07, B09, B12 and B13. Every
flagged "text blob" was image content, checked on crops:
- **Gameplay frames:** the lanterns, temple and fighters in the engine capture.
- **B04/B05 figures:** a fighter's hair and belt against the green or yellow generation backgrounds.

The checker already has a category for this: shot types `video`, `still` and `screen` skip the
pixel checks, because their content is diegetic. So:

- **Classification.** The capture beats B02, B09, B12 and B13 are now `VIDEO`. B07, the engine
  screenshot, is `STILL`. The B04 and B05 figures are `STILL`; they are pages of real generation
  outputs. `compile.py` decides how a beat is filled from the file in `media/`, not from this
  field, so the cut is unchanged.
- **Masked check.** These seven beats also carry our own labels and cards, so they were not simply
  waved through. A masked copy was built in `_qc/typecheck-masked/`:
  - The game area of each capture clip was filled with the page colour (ffmpeg `drawbox`).
  - B04 and B05 were re-rendered with a blank image.
  - What is left is only our designed typography, and GATE T was run on it with every pixel check
    on. Result: `_qc/typecheck-masked/TYPECHECK.md`.
- **No toolkit change.** The checker was not edited, and `--skip-pixels` was not used.

`./art` calls `python3`, which on this Windows host is the Microsoft Store alias. The toolkit
was not edited. For this session only, a two-line `python3` shim that runs `python` was
prepended to `PATH`.

## 8. Contributions

| Who | What |
|---|---|
| **Zhaohui Li** | Chose the game and the film workflow. Asked for this film and found the toolkit. Decided the slice-audio route (§1). Playtested the slice ("还可以"). |
| **Claude Code** | Wrote the beat sheet, narration and every tool in `tools/`. Ran the captures and the renders. Made the QC judgements. |
| **Local models** | Kokoro voiced the narration. faster-whisper checked it. |

The game assets shown are the generated ones documented in the repo's ASSET-LOG.
