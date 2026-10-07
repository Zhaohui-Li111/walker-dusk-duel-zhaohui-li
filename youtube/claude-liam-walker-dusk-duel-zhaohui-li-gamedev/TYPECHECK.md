# TYPECHECK.md — GATE T

Reel: `claude-liam-walker-dusk-duel-zhaohui-li-gamedev`  |  Checked: 2026-10-06T19:59  |  Overall: **FAIL**  |  Beats checked: 19  |  FAILs: 7

Spec: `skills/make/kerning/reference/type-spec.md` §8.  Floor: 1.9% frame-height.  Contrast: 4.5:1 WCAG.  Kern threshold: 3.5× expected advance.  Wordy budget: 2 elements.

| beat | lane | polarity | worst finding | status | fix |
|------|------|----------|---------------|--------|-----|
| B00 | ? | light | min-size §8.1: hand-drawn pattern (ClaudeComposerAsk) — §8.1 hachure/crossbar fragments ar… | PASS | — |
| B01 | ? | light | min-size §8.1: min text-run height 77px >= floor 41px | PASS | — |
| B02 | ? | light | contrast-local §8.3b: per-blob contrast 1.09:1 < 3.0:1 — text unreadable on actual local b… | **FAIL** | Use INK on cream; add backing plate under accent text |
| B03 | ? | light | no-wordy-card §8.5: no prose payload found | PASS | — |
| B04 | ? | light | contrast §8.3: mean fg/bg contrast 3.89:1 < 4.5:1 WCAG (fg≈(22, 144, 56), bg≈(250, 248, 24… | **FAIL** | Use INK on cream; add backing plate under accent text |
| B05 | ? | light | contrast-local §8.3b: per-blob contrast 2.25:1 < 3.0:1 — text unreadable on actual local b… | **FAIL** | Use INK on cream; add backing plate under accent text |
| B06 | ? | light | no-wordy-card §8.5: 2 element(s), 3 words — within budget. Detail: 2 output lines (3 words… | PASS | — |
| B07 | ? | light | contrast-local §8.3b: per-blob contrast 1.02:1 < 3.0:1 — text unreadable on actual local b… | **FAIL** | Use INK on cream; add backing plate under accent text |
| B08 | ? | light | no-wordy-card §8.5: 2 element(s), 2 words — within budget. Detail: 2 output lines (2 words… | PASS | — |
| B09 | ? | light | contrast-local §8.3b: per-blob contrast 1.09:1 < 3.0:1 — text unreadable on actual local b… | **FAIL** | Use INK on cream; add backing plate under accent text |
| B10 | ? | light | no-wordy-card §8.5: no prose payload found | PASS | — |
| B11 | ? | light | no-wordy-card §8.5: 2 element(s), 5 words — within budget. Detail: 2 output lines (5 words… | PASS | — |
| B12 | ? | light | contrast-local §8.3b: per-blob contrast 1.10:1 < 3.0:1 — text unreadable on actual local b… | **FAIL** | Use INK on cream; add backing plate under accent text |
| B13 | ? | light | contrast-local §8.3b: per-blob contrast 1.10:1 < 3.0:1 — text unreadable on actual local b… | **FAIL** | Use INK on cream; add backing plate under accent text |
| B14 | ? | light | no-wordy-card §8.5: 2 element(s), 2 words — within budget. Detail: 2 output lines (2 words… | PASS | — |
| B15 | ? | light | no-wordy-card §8.5: 2 element(s), 8 words — within budget. Detail: 2 output lines (8 words… | PASS | — |
| B16 | ? | light | min-size §8.1: hand-drawn pattern (ClaudeVerdictArtifact) — §8.1 hachure/crossbar fragment… | PASS | — |
| B17 | ? | light | min-size §8.1: hand-drawn pattern (ClaudeComposerAsk) — §8.1 hachure/crossbar fragments ar… | PASS | — |
| B18 | ? | dark | min-size §8.1: min text-run height 49px >= floor 41px | PASS | — |

---

## Failures requiring action before cut

### B02 (?)
- **contrast-local §8.3b**: per-blob contrast 1.09:1 < 3.0:1 — text unreadable on actual local background (blob@(916,824)–(1015,887) fg≈(122, 54, 84) bg≈(122, 46, 55)); move label off its background or change text color
- **Fix:** Use INK on cream; add backing plate under accent text

### B04 (?)
- **contrast §8.3**: mean fg/bg contrast 3.89:1 < 4.5:1 WCAG (fg≈(22, 144, 56), bg≈(250, 248, 241))
- **contrast-local §8.3b**: per-blob contrast 2.46:1 < 3.0:1 — text unreadable on actual local background (blob@(2873,754)–(2947,783) fg≈(83, 58, 53) bg≈(137, 123, 66)); move label off its background or change text color
- **Fix:** Use INK on cream; add backing plate under accent text

### B05 (?)
- **contrast-local §8.3b**: per-blob contrast 2.25:1 < 3.0:1 — text unreadable on actual local background (blob@(2539,772)–(2653,803) fg≈(63, 59, 46) bg≈(90, 120, 75)); move label off its background or change text color
- **Fix:** Use INK on cream; add backing plate under accent text

### B07 (?)
- **contrast-local §8.3b**: per-blob contrast 1.02:1 < 3.0:1 — text unreadable on actual local background (blob@(600,842)–(767,884) fg≈(38, 18, 32) bg≈(38, 15, 32)); move label off its background or change text color
- **Fix:** Use INK on cream; add backing plate under accent text

### B09 (?)
- **contrast-local §8.3b**: per-blob contrast 1.09:1 < 3.0:1 — text unreadable on actual local background (blob@(916,824)–(1011,887) fg≈(122, 54, 84) bg≈(121, 47, 58)); move label off its background or change text color
- **Fix:** Use INK on cream; add backing plate under accent text

### B12 (?)
- **contrast-local §8.3b**: per-blob contrast 1.10:1 < 3.0:1 — text unreadable on actual local background (blob@(916,824)–(1013,887) fg≈(122, 54, 84) bg≈(121, 46, 56)); move label off its background or change text color
- **Fix:** Use INK on cream; add backing plate under accent text

### B13 (?)
- **contrast-local §8.3b**: per-blob contrast 1.10:1 < 3.0:1 — text unreadable on actual local background (blob@(916,824)–(1013,887) fg≈(122, 54, 84) bg≈(121, 46, 56)); move label off its background or change text color
- **Fix:** Use INK on cream; add backing plate under accent text

---

## Check summary

| Check | Beats checked | FAILs |
|-------|---------------|-------|
| no-wordy-card §8.5 | 9 | 0 |
| min-size §8.1 | 19 | 0 |
| overflow §8.2 | 19 | 0 |
| contrast §8.3 | 19 | 1 |
| contrast-local §8.3b | 19 | 7 |
| bbox-overlap §8.6b | 19 | 0 |
| card-clip §8.13 | 19 | 0 |
| kerning §8.4 | 0 | 0 |
| redundancy §8.10 (advisory) | 1 | 0 (advisory — no exit effect) |

---

*GATE T: any FAIL blocks `./art run` and `./art final`. Fix the flagged beats and re-run `scripts/type_check.py` until green.*
