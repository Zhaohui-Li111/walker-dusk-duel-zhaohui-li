# TYPECHECK.md — GATE T

Reel: `claude-liam-walker-dusk-duel-zhaohui-li-a5-gamedev`  |  Checked: 2026-10-29T23:27  |  Overall: PASS  |  Beats checked: 21  |  FAILs: 0

Spec: `skills/make/kerning/reference/type-spec.md` §8.  Floor: 1.9% frame-height.  Contrast: 4.5:1 WCAG.  Kern threshold: 3.5× expected advance.  Wordy budget: 2 elements.

| beat | lane | polarity | worst finding | status | fix |
|------|------|----------|---------------|--------|-----|
| B00 | ? | light | min-size §8.1: hand-drawn pattern (ClaudeComposerAsk) — §8.1 hachure/crossbar fragments ar… | PASS | — |
| B01 | ? | light | min-size §8.1: min text-run height 77px >= floor 41px | PASS | — |
| B02 | ? | — | no video | SKIP | — |
| B03 | ? | light | no-wordy-card §8.5: no prose payload found | PASS | — |
| B04 | ? | light | no-wordy-card §8.5: 2 element(s), 7 words — within budget. Detail: 2 output lines (7 words… | PASS | — |
| B05 | ? | — | no-wordy-card §8.5: no prose payload found | PASS | — |
| B06 | ? | light | no-wordy-card §8.5: 2 element(s), 7 words — within budget. Detail: 2 output lines (7 words… | PASS | — |
| B07 | ? | — | no video | SKIP | — |
| B08 | ? | — | no-wordy-card §8.5: no prose payload found | PASS | — |
| B09 | ? | light | no-wordy-card §8.5: no prose payload found | PASS | — |
| B10 | ? | light | no-wordy-card §8.5: no prose payload found | PASS | — |
| B11 | ? | light | no-wordy-card §8.5: 2 element(s), 7 words — within budget. Detail: 2 output lines (7 words… | PASS | — |
| B12 | ? | — | no-wordy-card §8.5: no prose payload found | PASS | — |
| B13 | ? | — | no-wordy-card §8.5: no prose payload found | PASS | — |
| B14 | ? | light | no-wordy-card §8.5: 2 element(s), 7 words — within budget. Detail: 2 output lines (7 words… | PASS | — |
| B15 | ? | — | no-wordy-card §8.5: no prose payload found | PASS | — |
| B16 | ? | light | no-wordy-card §8.5: no prose payload found | PASS | — |
| B17 | ? | light | no-wordy-card §8.5: no prose payload found | PASS | — |
| B18 | ? | light | min-size §8.1: hand-drawn pattern (ClaudeVerdictArtifact) — §8.1 hachure/crossbar fragment… | PASS | — |
| B19 | ? | light | min-size §8.1: hand-drawn pattern (ClaudeComposerAsk) — §8.1 hachure/crossbar fragments ar… | PASS | — |
| B20 | ? | light | min-size §8.1: min text-run height 49px >= floor 41px | PASS | — |

---

## Failures requiring action before cut

*None — GATE T PASS.*
---

## Check summary

| Check | Beats checked | FAILs |
|-------|---------------|-------|
| no-wordy-card §8.5 | 14 | 0 |
| min-size §8.1 | 14 | 0 |
| overflow §8.2 | 14 | 0 |
| contrast §8.3 | 14 | 0 |
| contrast-local §8.3b | 14 | 0 |
| bbox-overlap §8.6b | 14 | 0 |
| card-clip §8.13 | 14 | 0 |
| kerning §8.4 | 0 | 0 |
| redundancy §8.10 (advisory) | 1 | 0 (advisory — no exit effect) |

---

*GATE T: any FAIL blocks `./art run` and `./art final`. Fix the flagged beats and re-run `scripts/type_check.py` until green.*
