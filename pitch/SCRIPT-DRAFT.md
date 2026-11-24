# SCRIPT-DRAFT — A8 pitch film, beat plan v1 (for Zhaohui's review)

> **Draft · 2026-11-23 · written by Claude Code** from Zhaohui's answers in `PROJECT-BRIEF.md`
> (Version 1, Revisions 2 and 3). The handout allows Claude to write the script; the narration
> speaks **as Zhaohui** in the first person and must say only what Zhaohui's answers say. Zhaohui
> approves or changes every line before audio is generated. Once approved, this becomes
> `pitch/beat_sheet.json`.

## Decisions this draft makes (Zhaohui to confirm)

- **Voice:** local Kokoro TTS speaking as Zhaohui ("I"). **No "Liam, in for Bear", no
  `@NikBearBrown` outro card or handle:** the A8 handout forbids the instructor's name, persona or
  credit line. The toolkit's `OUTRO-LOCK.md` requires that card for `claude-liam-*` reels, so this
  film leaves the lock and is **not** named `claude-liam-*`; the deviation goes in FRICTIONAL.md.
  A plain end card replaces it: title, name, "CSYE 7270 · Fall 2026".
- **Footage:** a **new scripted-input capture** of one full round (title → fight → K.O. → result →
  rematch) from revision `dff6cba` (`godot/` unchanged since `8049c54`), Movie Maker, 60 fps. The
  A7 capture ends before any K.O., so it does not cover the loop. Every gameplay shot carries the
  label **"Real capture · scripted input · rev dff6cba"**.
- **Constructed material** (Web build, CPU difficulty, plan) carries **"CONSTRUCTED · PROPOSED"**
  on screen. No King of Fighters footage or art is shown (no rights); it is named in text only.
- **Length target:** about 2 min 45 s, 14 beats, about 420 words.

## Beats

| # | ~s | Question | Narration (as Zhaohui) | Picture | Label |
|---|---|---|---|---|---|
| 1 | 12 | open | I'm Zhaohui Li. This is the pitch for my final project: Dusk Duel, a small fighting game I have been building in Godot since Assignment 2. | Title card over a still of the stage | — |
| 2 | 18 | 1 What | My final project will take Dusk Duel to a complete, playable vertical slice that runs in a web browser: one stage, one player against a CPU opponent, from the title screen to the knockout and a rematch. | Real capture: title screen → round call | Real capture · scripted input · rev dff6cba |
| 3 | 18 | exists | Much of that loop already exists. Today the game starts on a title screen, runs a full round against a CPU opponent, ends on a K.O., and offers a rematch. All of this runs on desktop now. | Real capture: fight → K.O. → result → rematch | Real capture · scripted input · rev dff6cba |
| 4 | 16 | 1 What (new) | What will be new is three things: a web build, a stronger CPU opponent with adjustable difficulty, and wider tests, with a test report a stranger can re-run. | Three cards: Web build · CPU · Tests | CONSTRUCTED · PROPOSED |
| 5 | 20 | 3 Different | My reference is The King of Fighters '97, which I played. I like its fast combat, attack timing and defence. Dusk Duel takes a smaller approach: one complete single-player match, for someone who wants a quick fight without installing a large game, finding an online opponent, or going through setup. | Text card: "The King of Fighters '97 (played)" vs "Dusk Duel: one match in a browser" — no KOF imagery | Browser half: CONSTRUCTED · PROPOSED |
| 6 | 16 | 3 CPU today | The CPU already walks in, kicks in range, blocks a close attack and steps back. It re-decides every ten ticks. Next, I want its choices to be more deliberate, not just more frequent. | Real capture: Aotake walking in, kicking, blocking; then `cpu_controller.gd` excerpt | Real capture · scripted input · rev dff6cba |
| 7 | 18 | 2 Who | I'm aiming at gameplay programmer roles. The reader is a technical lead or a recruiter. In the first sixty seconds they should open the page, press Enter, fight a round, and see the K.O. and the rematch, without reading any code. | 60-second timeline: open → Enter → fight → K.O. → rematch | CONSTRUCTED · PROPOSED (the web page does not exist) |
| 8 | 22 | 4 Proves | Behind the game is the evidence. Shaders and materials from Assignment 5, particle effects from Assignment 6, animation clips from Assignment 7, each with headless tests. The round itself is pinned by ninety-four checks, all passing. | Real test logs scrolling (`test_runner` 94 / 0, `test_hurt_flash` 69 / 0, `test_kick_edges` 38 / 0); hit spark and kick arc in real capture | Real output · logs at 8049c54 |
| 9 | 14 | 4 Profiling | I have measured cost before: on this laptop's Intel UHD Graphics, the hit sparks added about a hundredth of a millisecond of GPU time. I will measure desktop against the browser the same way. | The A6 GPU-price table | Real measurement · A6, Intel UHD Graphics |
| 10 | 14 | 5 Out | What it will not do: no online play, one stage only, no character select, no saves, and no big roster. | List card, items struck through | — |
| 11 | 22 | 5 First | The first new piece is Milestone 1: a full match in a web browser. I will check it on this machine, in Microsoft Edge: the game loads, I start from the title, the CPU approaches, attacks and blocks, the effects draw, the round reaches the K.O., and a rematch plays. A recording and a test report will show it ran. | Checklist of the seven criteria, all unticked | CONSTRUCTED · PROPOSED |
| 12 | 18 | 6 Risk | The risk is that the web build looks or runs differently from desktop: shader colour, particle blending, frame rate. So the web export comes first, not last; I will compare both in the same scene, and give any effect that fails a simpler fallback. | Split card: desktop still (real) │ browser (empty frame) | Left: real capture · Right: CONSTRUCTED |
| 13 | 22 | 7 Why | Why this project? Shaders, particles, animation and tests are skills I already have, and each has a tagged assignment behind it. What is new to me is a smarter CPU opponent, shipping a Godot game to the web, repeatable benchmarks, and wider gameplay tests. | Two columns: "Have (a5, a6, a7, 6317281)" │ "New" | — |
| 14 | 10 | close | Dusk Duel: a fighting game a stranger can open, play and verify. Godot 4.7.2, Compatibility renderer, exported to the web. | End card: title, Zhaohui Li, CSYE 7270 · Fall 2026 | — |

## Facts each line rests on (Claude Code)

- Beats 2–3, 6: commit `6317281`; `cpu_controller.gd` (REACTION 10, BLOCK_CHANCE 0.55, KICK_CHANCE 0.5).
- Beat 8: `logs/test_runner_60fps.log:24` (94 / 0), `SUBMISSION.md` A7 results; tags `a5`, `a6`, `a7`.
- Beat 9: `TEST-REPORT.md` "GPU price": Effect A (hit sparks) +0.012 ms median. Narration rounds to
  "about a hundredth of a millisecond".
- Beat 13: Zhaohui's Revision 2, question 7. The a3 Blender props are left out of the narration
  (they are not in the fight scene); **Zhaohui to say whether to add them back.**

## What I need from Zhaohui

1. Approve the beats as they are, or say which lines to change (Chinese is fine).
2. Confirm the plan to drop the Liam / @NikBearBrown outro and use a first-person voice.
3. Permission to make the new scripted capture (a windowed Movie Maker run that you start, as in A7).
