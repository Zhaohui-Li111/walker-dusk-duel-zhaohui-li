# QC report — "Dusk Duel: Final Project Pitch"

| Check | Result | File |
|---|---|---|
| godot-gamedev --check (before / after export) | PASS / PASS: 12 sources, 162 exclusions, 4 components, 1 exact excerpt, 1 code/result pair | `gamedev_check.json`, `gamedev_check_after_export.json` |
| GATE T (in `./art final`) | PASS, 0 FAILs. The three capture beats are SKIP ("no video"); STILL beats get the wordy-card check only | `../TYPECHECK.md`, `final.log` |
| GATE T (masked copy, every beat typed GRAPHIC, game pixels painted out) | PASS, 0 FAILs, 15 beats. The capture labels measure 41 px, exactly the floor | `typecheck-masked/TYPECHECK.md` |
| GATE F (paperwork) | FACTCHECK.md, SHOTLIST.md, PROMPTS.md present | `../FACTCHECK.md` |
| Final export | ready, 15/15 slots, 187.5 s, 3840 × 2160, 30 fps, SHA-256 `cd2fb89b…609f` | `../exports/landscape/*.verified.json` |
| Skin lint (warnings) | B00 is not `ClaudeComposerAsk`, and B14 is not `ClaudeTitleOutro`. This is intended: the A8 handout forbids the instructor's credit line | `final.log` |
| Footer handle | none on any sampled frame (after the toolkit patch) | `frames/`, `contact_*.png` |
| Transcripts (faster-whisper base.en) | all 15 read back; only homophones (BUILD-LOG §3) | `transcripts.json` |
| Loudness (ffmpeg ebur128, informational) | integrated −24.5 LUFS | — |
