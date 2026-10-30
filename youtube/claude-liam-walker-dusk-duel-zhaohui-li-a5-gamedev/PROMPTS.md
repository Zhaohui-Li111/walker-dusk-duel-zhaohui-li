# PROMPTS — every prompt in or behind the film

## On screen

| Beat | Prompt | Status |
|---|---|---|
| B00 | "Please use Walker to convert my game design document about Dusk Duel into a hurt flash and a granite material: I write both shaders by hand from my spec, and you write the driver, the tests and the audit, without touching godot/shaders/." | **Reconstruction** written for the film (labelled). The work was done step by step over several sessions. |
| B19 | "Please use Walker to add one uniform to my shader's brief before I write it: its type, hint and default, the game state that sets it, and one pixel I predict by hand at three values. Then write a test that fails if I rename it in the shader only." | Handoff prompt written for the viewer. |

## Behind the work (in the repo)

- `prompts/prompt-1.txt`, `prompt-2-plan.txt`, `prompt-3-audit.txt`: the handout's prompts, verbatim.
- `prompts/prompt-2b-step1.txt`, `prompt-2c-step2.txt`, `prompt-2d-revision7.txt`: written by Claude
  from Zhaohui's approvals and decisions.
- Transcripts: `sessions/session-1.jsonl`, `session-2-plan.jsonl`, `session-2b-step1.jsonl`,
  `session-2c-step2.jsonl`, `session-2d-revision7.jsonl`, `session-3-audit.jsonl`.

## Behind the film

The reel was built by Claude Code (Opus 5.5) in the session that did the A5 work, after Zhaohui
said "Start the film". See BUILD-PROMPT.md to rebuild it.
