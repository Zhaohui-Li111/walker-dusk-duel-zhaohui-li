# TYPECHECK.md — GATE T

Reel: `claude-liam-walker-dusk-duel-zhaohui-li-gamedev`  |  Checked: 2026-10-06T21:12  |  Overall: **FAIL**  |  Beats checked: 19  |  FAILs: 6

Spec: `skills/make/kerning/reference/type-spec.md` §8.  Floor: 1.9% frame-height.  Contrast: 4.5:1 WCAG.  Kern threshold: 3.5× expected advance.  Wordy budget: 2 elements.

| beat | lane | polarity | worst finding | status | fix |
|------|------|----------|---------------|--------|-----|
| B00 | ? | light | min-size §8.1: min text-run height 52px >= floor 41px | PASS | — |
| B01 | ? | light | min-size §8.1: min text-run height 77px >= floor 41px | PASS | — |
| B02 | ? | light | min-size §8.1: no text-run blobs above noise threshold — the filter discarded every candid… | **FAIL** | Increase font_size in scenes.py or Remotion component |
| B03 | ? | light | min-size §8.1: min text-run height 43px >= floor 41px | PASS | — |
| B04 | ? | light | no-wordy-card §8.5: no prose payload found | PASS | — |
| B05 | ? | light | no-wordy-card §8.5: no prose payload found | PASS | — |
| B06 | ? | light | min-size §8.1: min text-run height 59px >= floor 41px | PASS | — |
| B07 | ? | light | min-size §8.1: min text-run height 43px >= floor 41px (individual-char fallback at 2×) | PASS | — |
| B08 | ? | light | min-size §8.1: min text-run height 41px >= floor 41px (individual-char fallback at 2×) | PASS | — |
| B09 | ? | light | min-size §8.1: no text-run blobs above noise threshold — the filter discarded every candid… | **FAIL** | Increase font_size in scenes.py or Remotion component |
| B10 | ? | light | contrast §8.3: terracotta accent #D97757 on cream 2.74:1 < 4.5:1 WCAG — accent text must s… | **FAIL** | Use INK on cream; add backing plate under accent text |
| B11 | ? | light | min-size §8.1: min text-run height 41px >= floor 41px (individual-char fallback at 2×) | PASS | — |
| B12 | ? | light | min-size §8.1: no text-run blobs above noise threshold — the filter discarded every candid… | **FAIL** | Increase font_size in scenes.py or Remotion component |
| B13 | ? | light | min-size §8.1: no text-run blobs above noise threshold — the filter discarded every candid… | **FAIL** | Increase font_size in scenes.py or Remotion component |
| B14 | ? | light | min-size §8.1: min text-run height 41px >= floor 41px (individual-char fallback at 2×) | PASS | — |
| B15 | ? | light | min-size §8.1: min text-run height 41px >= floor 41px (individual-char fallback at 2×) | PASS | — |
| B16 | ? | light | min-size §8.1: min text-run height 41px >= floor 41px (individual-char fallback at 2×) | PASS | — |
| B17 | ? | light | min-size §8.1: min text-run height 41px >= floor 41px (individual-char fallback at 2×) | PASS | — |
| B18 | ? | dark | contrast §8.3: terracotta #D97757 on dark bg (59, 55, 38) 3.82:1 < 4.5:1 WCAG — use lighte… | **FAIL** | Use INK on cream; add backing plate under accent text |

---

## Failures requiring action before cut

### B02 (?)
- **min-size §8.1**: no text-run blobs above noise threshold — the filter discarded every candidate, which is what sub-floor type looks like; cannot verify (SHOW-LESS.md)
- **Fix:** Increase font_size in scenes.py or Remotion component

### B09 (?)
- **min-size §8.1**: no text-run blobs above noise threshold — the filter discarded every candidate, which is what sub-floor type looks like; cannot verify (SHOW-LESS.md)
- **Fix:** Increase font_size in scenes.py or Remotion component

### B10 (?)
- **contrast §8.3**: terracotta accent #D97757 on cream 2.74:1 < 4.5:1 WCAG — accent text must switch to INK #3D3929 or carry a backing plate
- **Fix:** Use INK on cream; add backing plate under accent text

### B12 (?)
- **min-size §8.1**: no text-run blobs above noise threshold — the filter discarded every candidate, which is what sub-floor type looks like; cannot verify (SHOW-LESS.md)
- **Fix:** Increase font_size in scenes.py or Remotion component

### B13 (?)
- **min-size §8.1**: no text-run blobs above noise threshold — the filter discarded every candidate, which is what sub-floor type looks like; cannot verify (SHOW-LESS.md)
- **Fix:** Increase font_size in scenes.py or Remotion component

### B18 (?)
- **contrast §8.3**: terracotta #D97757 on dark bg (59, 55, 38) 3.82:1 < 4.5:1 WCAG — use lighter accent or backing plate on dark background
- **Fix:** Use INK on cream; add backing plate under accent text

---

## Check summary

| Check | Beats checked | FAILs |
|-------|---------------|-------|
| no-wordy-card §8.5 | 2 | 0 |
| min-size §8.1 | 19 | 4 |
| overflow §8.2 | 19 | 0 |
| contrast §8.3 | 19 | 2 |
| contrast-local §8.3b | 19 | 0 |
| bbox-overlap §8.6b | 19 | 0 |
| card-clip §8.13 | 19 | 0 |
| kerning §8.4 | 0 | 0 |
| redundancy §8.10 (advisory) | 1 | 0 (advisory — no exit effect) |

---

*GATE T: any FAIL blocks `./art run` and `./art final`. Fix the flagged beats and re-run `scripts/type_check.py` until green.*
