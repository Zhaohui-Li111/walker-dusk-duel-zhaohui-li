# PROMPTS — every prompt in or behind the film

## On screen

| Beat | Prompt | Status |
|---|---|---|
| B00 | "Please use Walker to convert my game design document about Dusk Duel into two particle effects: a hit spark on every clean hit, and courtyard embers while the fight runs. I write the brief, the settings and the predictions; you build the scenes, controllers and tests." | **Reconstruction** written for the film (labelled "reconstructed ask" on screen). The A6 work was done step by step in one day of sessions, not from one Walker run. |
| B23 | "Please use Walker to add one particle effect to my game's brief before anything is built: its job, the event or condition that drives it, every setting, and a frame strip with what each frame should show. Then predict one change and its strip before you capture it." | Handoff prompt written for the viewer. |

## Behind the work (in the repo)

- `prompts/a6/prompt-1.txt` (CLAUDE.md), `prompt-2-build-hit-spark.txt`, `prompt-3-plan-hit-spark.txt`,
  `prompt-3b-step1-hit-spark.txt`, `prompt-3c-step2-hit-spark.txt`, `prompt-5-build-embers.txt`,
  `prompt-6-plan-embers.txt`, `prompt-6b-implement-embers.txt`, `prompt-7-cost.txt`.
- Transcripts and results: `sessions/a6/session-*.jsonl` and `session-*.result.md`.
- After the hit spark Step 1, Zhaohui delegated the rest ("你把剩下的任务自己做完吧"); Claude Code
  approved the later agent steps on that basis and said so in each prompt (FRICTIONAL.md A6).

## Behind the film

The reel was built by Claude Code (Opus 5.5) as a subagent, from a build request written by the
main Claude Code session for Zhaohui (the A6 film task). No prompt was sent to any paid service.
See BUILD-PROMPT.md to rebuild it.
