# SOURCES — A8 pitch film ("Dusk Duel: Final Project Pitch")

Reel folder: `youtube/walker-dusk-duel-zhaohui-li-a8-pitch/` (source and tools in Git; capture,
audio, clips and the rendered film stay local, see `.gitignore`).

## What Zhaohui made

- **The project and its seven answers**: `pitch/PROJECT-BRIEF.md`, Version 1 and Revisions 2–3, in
  Zhaohui's words. Chinese originals are kept in its appendix. Zhaohui wrote the English of
  Revision 2 themself. Asked whether the answers were written with another AI, Zhaohui answered
  "我自己写的" ("I wrote it myself") both times; this is recorded as given.
- **Decisions:** the project (Dusk Duel as a web vertical slice), the target role (gameplay
  programmer), the comparable (*The King of Fighters '97*, which Zhaohui played), the first milestone
  (a full match in Edge on this machine), and the go-ahead for the script ("批准，开始做", 2026-11-23).
- **The windowed capture run:** Zhaohui started the Movie Maker run (take 2). Take 1 had a real key
  press in the game window, and Zhaohui said so ("按过"), so it is not used. It is kept locally as
  `capture/a8_round_take1_keypress.*`.
- **The game itself**, from earlier assignments: tags `a3`, `a5`, `a6`, `a7` and the earlier
  commits named in `PROJECT-BRIEF.md`. The shaders in `godot/shaders/` are hand-written by Zhaohui.

## What Claude Code contributed (Claude Opus 5.5, in Claude Code, 2026-11-23)

- **Translation** of Zhaohui's Chinese answers. The inline *(Claude Code)* notes and corrections in
  `PROJECT-BRIEF.md`. The "Exists today" table, checked against the repository.
- **The script:** `SCRIPT-DRAFT.md` and the narration in `beat_sheet.json`. Claude Code wrote both
  from Zhaohui's answers; the narration speaks as Zhaohui. After approval, one beat was split into
  code (B05) and result (B06) for the toolkit's code-then-result check, with small wording changes
  (BUILD-LOG.md).
- **Build tools** in `youtube/walker-dusk-duel-zhaohui-li-a8-pitch/tools/`, adapted from the A7
  reel:
  - `capture_a8.gd`: the capture bot that sends Akaken's keys;
  - `build_figures.py`, `build_beatsheet.py`, `build_media.py`, `build_evidence.py`;
  - the QC helpers.
- **All figure layouts.** Their only new pixels are text, frames, dashed "CONSTRUCTED · PROPOSED"
  panels and lines.
- **A toolkit patch:** `GodotDesignFigure.tsx` and `GodotDevWorkbench.tsx` drew a hard-coded
  `@NikBearBrown` footer. Claude Code made it a `handle` prop (default unchanged) and passed `""`,
  because the A8 handout forbids the instructor's credit line.

## What is real and what is constructed

| On screen | Kind | Origin |
|---|---|---|
| Gameplay in B01, B02, B06; stills in B00, B12 | **Real capture, scripted input** | `capture/a8_round.avi`: Movie Maker, 3840 × 2160, 60 fps, 1938 frames, Godot 4.7.2, an isolated copy of `godot/` at `dff6cba` (unchanged since `8049c54`). Akaken's keys are sent by `capture_a8.gd`; Aotake is the game's own `CpuController`. Log `capture/a8_round.log` is identical to the dry run (`capture/dryrun2.log`), line for line. |
| Code in B05 | Real source | `godot/fighter/cpu_controller.gd:49-59`, byte for byte (checked by `godot-gamedev --check`) |
| Test lines in B08 | Real output | the six committed logs named on screen |
| GPU table in B09 | Real measurement | `TEST-REPORT.md` "GPU price" (A6, 2026-11-08, Intel UHD Graphics) |
| B03, B07, B11, right half of B04 and B12 | **Constructed, proposed** | Claude Code's layouts of Zhaohui's plans, stamped "CONSTRUCTED · PROPOSED" |
| B10, B13, B14 | Text cards | Zhaohui's answers |

No Claude response is shown in the film. No King of Fighters footage, art, logo or music is used;
the game is named only.

## Tools and licences

| Tool | Version | Use | Licence |
|---|---|---|---|
| Godot Engine | 4.7.2 stable | game, Movie Maker capture | MIT |
| Brutalist toolkit (`brutalist.art`) | local checkout `D:\courses\7270\brutalist.art-main` | Remotion scenes, compile, GATE T, `godot-gamedev --check` | per its repository |
| Kokoro TTS, voice `am_onyx` | local | narration (AI voice speaking as Zhaohui; no clone of any real person) | Apache-2.0 |
| faster-whisper `base.en` | local | narration read-back | MIT |
| Remotion, FFmpeg, Pillow | local | rendering, cutting, figures | per their licences |

The game's own art and audio are listed in the repository `SOURCES.md` (A2: SDXL and Stable
Audio/MusicGen generations; A7: the code-generated lantern sheet). No paid service, API key or
upload was used.
