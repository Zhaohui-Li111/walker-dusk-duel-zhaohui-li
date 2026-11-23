# PROMPTS — every prompt in or behind the film

## On screen

| Beat | Prompt | Status |
|---|---|---|
| B00 | "Please use Walker to convert my game design document about Dusk Duel into two animation clips: a lantern flame that loops, and a kick arc timed from the kick's own frame data. I choose the routes, the frame counts and the clocks; you build the clips, scenes and tests." | **Reconstruction** written for the film (labelled "reconstructed ask" on screen). The A7 work was done step by step in one day of sessions, not from one Walker run. |
| B21 | "Please use Walker to add one animation clip to my game's brief before anything is built: its route, its one authority, its clock, and a phase table counted from the code. Then predict the frame strip at every phase boundary before you capture it." | Handoff prompt written for the viewer. |

## Behind the work (in the repo)

- `prompts/a7/prompt-1.txt` (CLAUDE.md step). Its two `claude -p` attempts stopped on "OAuth session
  expired" (`sessions/a7/session-1-attempt1-auth-expired.*`, `attempt2`); on Zhaohui's choice ("Do it
  here") the prompt was carried out in the desktop session (FRICTIONAL.md A7, Step 1). Steps 2–6 and
  tuning were done in the desktop session; the commits are listed in FRICTIONAL.md A7.

## Behind the film

The reel was built by Claude Code (Opus 5.5) as a subagent, from a build request written by the main
Claude Code session for Zhaohui (the A7 film task). No prompt was sent to any paid service. See
BUILD-PROMPT.md to rebuild it.
