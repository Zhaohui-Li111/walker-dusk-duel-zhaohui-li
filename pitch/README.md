# Final project pitch (A8) — Dusk Duel

- **Name:** Zhaohui Li
- **Working title:** Dusk Duel — A Complete Playable Fighting Game Vertical Slice
- **Target role:** Gameplay Programmer
- **Runtime:** Godot 4.7.2 stable, GDScript, GL Compatibility renderer. Desktop (Windows 11) today;
  Web export planned (Milestone 1, checked in Microsoft Edge). No export preset exists yet.
- **Film:** `walker-dusk-duel-zhaohui-li-a8-pitch.mp4` · 3:07.5 (187.5 s) · 3840 × 2160, 30 fps
  - SHA-256 `cd2fb89b6e86c1676de49fdffa9203326e728a2113d02558a24c752129dd609f`
  - **Link:** https://drive.google.com/file/d/1coFR34SapqT3u37gkpSLxUUe6tmP5WfL/view?usp=sharing
    (Google Drive, uploaded by Zhaohui). Checked 2026-11-24 in a browser not signed in to Google: it
    opens without sign-in, and the page title is the filename.
- **Film source:** `youtube/walker-dusk-duel-zhaohui-li-a8-pitch/`. The game footage was built
  from revision `dff6cba` (`godot/` unchanged since `8049c54`, tag `a7`).

## What is in this folder

| File | What |
|---|---|
| [PROJECT-BRIEF.md](PROJECT-BRIEF.md) | the seven answers (Zhaohui's, with translation and fact notes), ending with **Exists today** and **Will exist** |
| [beat_sheet.json](beat_sheet.json) | narration and visual plan, 15 beats (copy of the reel's) |
| [SCRIPT-DRAFT.md](SCRIPT-DRAFT.md) | the beat plan Zhaohui approved before the build |
| [BUILD-PROMPT.md](BUILD-PROMPT.md) | prompts and commands that rebuild the film |
| [SOURCES.md](SOURCES.md) | what Zhaohui made, what Claude contributed, what is real and what is constructed, tools and licences |
| [FRICTIONAL.md](FRICTIONAL.md) | dated entries |
| [gate-reports/](gate-reports/) | the toolkit's reports, listed below |

The gate reports:
- `godot-gamedev --check`: PASS, before and after export;
- GATE T: PASS, both on the reel and on the masked copy;
- `FACTCHECK.md`;
- the final export's `verified.json`;
- the QC summary.

## How the film shows what exists and what does not

- **Real:** gameplay is a Movie Maker capture of the real game. Akaken's keys are sent by a small
  capture bot, and Aotake is the game's own CPU. Every frame is labelled "REAL CAPTURE · scripted
  input · rev dff6cba". The code, test logs and the A6 GPU measurement are shown as recorded.
- **Constructed:** everything that does not exist yet sits on a dashed panel stamped
  "CONSTRUCTED · PROPOSED". This covers the web build, the CPU upgrade, the first-60-seconds
  plan, Milestone 1 and the browser side of the risk.
- **Not shown:** no Claude response, and no King of Fighters imagery (the game is named only).

## Rebuild the film

Follow [BUILD-PROMPT.md](BUILD-PROMPT.md). In short:
1. scripted capture;
2. figures and beat sheet;
3. local Kokoro narration;
4. clips and Remotion beats;
5. the gates;
6. `./art final`.

The rendered `.mp4`, the capture `.avi`, the audio and the clips are kept out of Git.
