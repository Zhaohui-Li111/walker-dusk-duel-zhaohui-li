# TYPECHECK.md — GATE T

Reel: `walker-dusk-duel-zhaohui-li-a8-pitch`  |  Checked: 2026-11-23T23:59  |  Overall: PASS  |  Beats checked: 15  |  FAILs: 0

Spec: `skills/make/kerning/reference/type-spec.md` §8.  Floor: 1.9% frame-height.  Contrast: 4.5:1 WCAG.  Kern threshold: 3.5× expected advance.  Wordy budget: 2 elements.

| beat | lane | polarity | worst finding | status | fix |
|------|------|----------|---------------|--------|-----|
| B00 | ? | — | no-wordy-card §8.5: no prose payload found | PASS | — |
| B01 | ? | — | no video | SKIP | — |
| B02 | ? | — | no video | SKIP | — |
| B03 | ? | — | no-wordy-card §8.5: no prose payload found | PASS | — |
| B04 | ? | — | no-wordy-card §8.5: no prose payload found | PASS | — |
| B05 | ? | light | no-wordy-card §8.5: 2 element(s), 8 words — within budget. Detail: 2 output lines (8 words… | PASS | — |
| B06 | ? | — | no video | SKIP | — |
| B07 | ? | — | no-wordy-card §8.5: no prose payload found | PASS | — |
| B08 | ? | — | no-wordy-card §8.5: no prose payload found | PASS | — |
| B09 | ? | — | no-wordy-card §8.5: no prose payload found | PASS | — |
| B10 | ? | — | no-wordy-card §8.5: no prose payload found | PASS | — |
| B11 | ? | — | no-wordy-card §8.5: no prose payload found | PASS | — |
| B12 | ? | — | no-wordy-card §8.5: no prose payload found | PASS | — |
| B13 | ? | — | no-wordy-card §8.5: no prose payload found | PASS | — |
| B14 | ? | — | no-wordy-card §8.5: no prose payload found | PASS | — |

---

## Failures requiring action before cut

*None — GATE T PASS.*
---

## Check summary

| Check | Beats checked | FAILs |
|-------|---------------|-------|
| no-wordy-card §8.5 | 12 | 0 |
| min-size §8.1 | 1 | 0 |
| overflow §8.2 | 1 | 0 |
| contrast §8.3 | 1 | 0 |
| contrast-local §8.3b | 1 | 0 |
| bbox-overlap §8.6b | 1 | 0 |
| card-clip §8.13 | 1 | 0 |
| kerning §8.4 | 0 | 0 |
| redundancy §8.10 (advisory) | 0 | 0 (advisory — no exit effect) |

---

*GATE T: any FAIL blocks `./art run` and `./art final`. Fix the flagged beats and re-run `scripts/type_check.py` until green.*
