# CHECKS-REPORT — beat classification and teaching arc (written before the cut)

**19 beats: 18 SHOW / 1 justified HOLD / 0 PUNT-flagged.**

| Beat | Act | Class | What carries it |
|---|---|---|---|
| B00 | ASK | SHOW | ClaudeComposerAsk: the reconstructed Walker ask types in, three real RESULT lines land |
| B01 | BLUF | SHOW | BrutalistHesitantWriter: "designed" struck through, "drew" typed in |
| B02 | OPEN | SHOW | real 4K capture: the fight in the generated courtyard |
| B03 | DESIGN | SHOW | design figure: pose 06 and boxes, colour block, palette; the cards light on the words |
| B04 | FALSIFIABILITY | SHOW | four real reference rounds side by side: prompts fail, colour blocks hold |
| B05 | PIPELINE | SHOW | skeleton → colour block → two seeds with scores → exported sprite |
| B06 | MECHANISM | SHOW | GodotDevWorkbench: fighter_art.gd 32–44, lines highlight on the words |
| B07 | RESULT | **HOLD** | one real engine still held for the narration. Justified: a staged pose with boxes is the evidence, and motion would hide the box/limb relationship. Labelled "staged pose". |
| B08 | MECHANISM | SHOW | fighter.gd 160–172, highlights on active frames, intersect, defender, resolve |
| B09 | RESULT | SHOW | real capture: the jab connects, spark, bar drop |
| B10 | DESIGN | SHOW | 16 measured SFX spectrograms; the picks light as named |
| B11 | MECHANISM | SHOW | audio_director.gd 100–108 |
| B12 | RESULT | SHOW | real capture: whiff, block, hit |
| B13 | SLICE AUDIO | SHOW | real capture with the game's own audio, no narration |
| B14 | MECHANISM | SHOW | test_runner.gd 349–358, the hand-placed dummy highlighted |
| B15 | RESULT | SHOW | the recorded test output, lines highlighted in turn |
| B16 | VERDICT | SHOW | the verdict artifact: models / Zhaohui / Claude / limits |
| B17 | HANDOFF | SHOW | the Your Turn prompt types in and is read aloud |
| B18 | OUTRO | SHOW | locked ClaudeTitleOutro, spoken title |

## Teaching arc

| Item | | Where |
|---|---|---|
| FRAMEWORK | ✓ | B01, then B03: event first, file second; the sheet fixes, the model draws |
| WORKED EXAMPLE | ✓ | B03 → B09: one jab from the sheet to a landed hit |
| FALSIFIABILITY | ✓ | B04 (prompts alone failed), B07 ("if art and boxes disagreed you'd see it here"), B14 (what the test cannot prove) |
| SCAFFOLDED TASK | ✓ | B17: one bounded change with a prediction and a test |
| BOOKENDS | ✓ | B00 composer, B01 hesitant writer, B16 verdict, B17 Your Turn, B18 outro |
| NO-SOURCE-NO-VERDICT | ✓ | every verdict line traces to FRICTIONAL / ASSET-LOG / the test record (FACTCHECK.md) |

**Code → result adjacency** (teaching contract code-then-result-v1): B06→B07, B08→B09,
B11→B12, B14→B15. Checked by `./art godot-gamedev --check`.

**Smell check:**
- Two consecutive design figures, B04 → B05. Accepted: one shows failure across rounds, the next
  shows the pipeline that worked. They have different layouts, and B05 is followed at once by code.
- B03 and B04 are also consecutive figures, so this makes three in a row (B03–B05). This is the
  film's weakest stretch. Logged here rather than padded with a different visual that would
  not be evidence.
