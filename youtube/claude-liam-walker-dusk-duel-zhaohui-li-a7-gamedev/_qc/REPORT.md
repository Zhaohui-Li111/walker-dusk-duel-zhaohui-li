# QC report — "Dusk Duel, Animated"

| Check | Result | File |
|---|---|---|
| godot-gamedev --check (before / after export) | PASS / PASS | `gamedev_check.json`, `gamedev_check_after_export.json` |
| GATE T (final) | PASS, 0 FAILs (capture beats SKIP, no video) | `../TYPECHECK.md`, `final.log` |
| GATE T (masked copy) | PASS; capture labels 41 px = floor | `typecheck-masked/TYPECHECK.md` |
| Final export | ready, 23/23 slots, 459.7 s, 3840 × 2160, SHA-256 8496e357…674b | `../exports/landscape/*.verified.json` |
| Visual QC | no BLOCKER/MAJOR; MINOR listed in BUILD-LOG §5 | `contact_1..5.png` |
| Transcripts (faster-whisper base.en) | all 23 read back | `transcripts.json` |

## Transcript mismatches and what was done

| Beat | Heard | Action |
|---|---|---|
| B07 | "A mutation when" (In mutation one); "Enclawed code" (And Claude Code) | reworded, re-voiced; now read correctly |
| B08 | "75, 16" (seven, five, sixteen); ".133" | reworded ("seven, then five, then sixteen"; "zero point one three three three"), re-voiced; correct |
| B14 | "inactive" (in active) | "during active", re-voiced; correct |
| B18 | "after an interrupted disappears" | "after an interrupt, the arc disappears", re-voiced; correct. "Claude Coe" accepted |
| B19 | "Enclawed"; "polygon seemed" → "scene" | "Finally, Claude's …"; "an edge between polygons", re-voiced twice; correct |
| B20 | "you set up hits" | "inject their hits", re-voiced; correct. "hits stop" (hitstop) accepted |
| accepted | "Zhao Hui"/"Jowhui" (Jow-hway), "Akakan"/"Otake", "sells" (cells), "cash" (cache), "LAM in forbear" (B21 sign-off), "Dusk dual … Nick Bear Brown" (B22) | homophones / names, as in A6 |
