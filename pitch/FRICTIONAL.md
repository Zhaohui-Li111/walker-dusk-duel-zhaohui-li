# FRICTIONAL — A8 pitch

Dated entries, in order, of what went wrong or rubbed while the pitch was made, and what was done
about it. **Written by Claude Code** (Claude Opus 5.5) from the session record, at Zhaohui's request
("帮我写FRICTIONAL吧", 2026-11-24). Every entry names its evidence. Zhaohui's own words appear only
where Zhaohui said them, quoted as given. Claude Code does not describe how Zhaohui felt or what
Zhaohui thought. A short section for Zhaohui's own notes is at the end.

## Day 1 · 2026-11-23 · the brief

- **The first answers put existing work in the future.** Zhaohui's Version 1 answers described the
  title → fight → K.O. → rematch loop and the CPU opponent as things to build. Both already existed
  (commit `6317281`, 2026-10-05). Under the handout's honesty rule that is a misstatement in the
  other direction. Claude Code pointed it out. Zhaohui revised questions 3, 5 and 7 (Revision 2) and
  settled four points in chat (Revision 3): *The King of Fighters '97*, Edge on this machine,
  Gameplay Programmer, and what is new.
- **Claude Code supplied one wrong fact.** It first cited `94 / 0` as the count at `6317281`; it is
  the count logged at `8049c54`. Corrected in Revision 2 (`PROJECT-BRIEF.md`).
- **The answers read like advice to Zhaohui.** Both pastes contained lines addressed to "你" ("I
  suggest…", "keep this out of question 3"). Claude Code asked once per paste whether another AI
  wrote them. Zhaohui answered "我自己写的" ("I wrote it myself") both times, recorded as given
  (`PROJECT-BRIEF.md`).
- **The brief is longer than one page.** The handout asks for one page. The brief keeps every
  revision and the Chinese originals, and ends with the two lists. It has not been shortened, because
  shortening it would rewrite Zhaohui's answers.

## Day 1 · 2026-11-23 · the toolkit

- **Toolkit rule against assignment rule.** The Brutalist `godot-gamedev` skill and `OUTRO-LOCK.md`
  require "Liam, in for Bear" and a locked `@NikBearBrown` outro card for `claude-liam-*` reels. The
  A8 handout forbids the instructor's name, persona or credit line. The handout wins:
  - the reel is named `walker-dusk-duel-zhaohui-li-a8-pitch`;
  - the narration is first person, as Zhaohui;
  - there is no outro card.

  `compile.py` warns about the cold open and the outro (warnings, not failures).
- **No show-tell skill.** The handout suggests one; this checkout has none. The film uses
  `GodotDesignFigure` (one picture per beat) and `GodotDevWorkbench`, as in A7.
- **The A7 capture could not show the loop.** It ends before any K.O. A new scripted-input capture
  (`capture_a8.gd`) plays one full round and the start of a rematch. In the dry run Akaken wins 58–0
  at 21.3 s.

## Day 1 · 2026-11-23 · the capture

- **The first command did not run.** Claude Code gave Bash syntax (`&&`). Zhaohui's terminal is
  PowerShell 5.1, which stopped with a parse error, so nothing was written. Claude Code's error; the
  next command was written for PowerShell (`cmd /c "…"`).
- **"Why doesn't it close?"** At 4K, Movie Maker on this Intel UHD laptop renders slower than real
  time. The window stayed open for minutes, not the 33 s of game time. It was still rendering (the
  `.avi` kept growing), not stuck.
- **Take 1 had a real key press.** The title went to the round at tick 127, before the scripted
  Enter at tick 240, and the log stopped matching the dry run. Asked, Zhaohui answered "按过"
  ("I did press one"). Take 1 is kept locally as `capture/a8_round_take1_keypress.*` and not used.
- **Take 2 is clean.** Run without touching anything. Its log equals the dry run on every line
  (1938 frames, 32.3 s), so the label "scripted input" holds.

## Day 1–2 · 2026-11-23/24 · rendering and gates

- **The instructor's handle was hard-coded on screen.** The first render showed `@NikBearBrown` in
  the footer of every figure and code beat (`GodotDesignFigure.tsx`, `GodotDevWorkbench.tsx`).
  Claude Code made it a prop, with the default unchanged for other reels. This reel passes `""`.
- **The re-render silently did nothing.** `remotion_scenes.py` skips beats whose clip exists
  ("filled already (skip)"), so the first re-render took 0 s per beat and changed nothing. It was
  re-run with `--force`; the footer is gone on sampled frames.
- **GATE T skips most of the film.** On the real reel it skips the capture beats ("no video") and
  runs only the wordy-card check on STILL beats. A masked copy (game pixels painted out, every beat
  typed GRAPHIC) ran all checks: PASS, 0 FAILs. The capture labels measure exactly the 41 px floor.
- **GATE F blocked the final export.** `FACTCHECK.md` and `PROMPTS.md` were missing. Claude Code
  wrote both. FACTCHECK checks every claim against a file or log, and marks future claims **will**.
  Then `./art final` exported: 187.5 s, 3840 × 2160, SHA-256 `cd2fb89b…609f`.

## Day 2 · 2026-11-24 · review

- **Zhaohui watched the film.** Asked whether anything needed changing, Zhaohui answered
  "看完了，没问题" ("watched it, no problems"). This is one overall answer, not a beat-by-beat review.
- **What the checks cannot cover.** The gates check hashes, text size, contrast and paperwork, not
  whether the pitch is persuasive or whether the narration says exactly what Zhaohui means. That
  rests on Zhaohui's watch above. The AI voice speaks as Zhaohui, and Zhaohui may be asked to
  explain any line.

- **The film was uploaded.** Zhaohui uploaded the `.mp4` to Google Drive and sent the link. Claude Code
  opened it in a browser not signed in to Google: it opens, and the title is the filename (`README.md`).

## Zhaohui's own notes (optional)

Not written. If Zhaohui adds any (Chinese is fine; Claude Code translates and keeps the original),
they go here, in Zhaohui's words.
