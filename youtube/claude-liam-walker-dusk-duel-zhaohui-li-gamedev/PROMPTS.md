# PROMPTS — every prompt that appears in, or produced, this film

## On screen

**B00, cold open. An ILLUSTRATIVE RECONSTRUCTION, labelled "reconstructed ask" on screen.**

The slice was built over many Claude Code sessions, not from this single Walker prompt:

> Please use Walker to convert my game design document about a cartoon martial-arts duel at dusk
> (two fighters, one round, every hit felt) into a Godot asset slice: generate the fighters, the
> courtyard, four sound effects and a music loop with free models, and wire them in.

The three RESULT lines under it are real outcomes (ASSET-LOG; the test run at `4e0cf14`).

**B17, Your Turn. Read aloud verbatim, then discussed:**

> Please use Walker to add one new state image to my Godot fighter. Write its pose and hitbox on
> the character sheet first, predict where the box should land, generate it from a colour block,
> then show it in-engine with collision boxes on, and add a test that fails if the image has no
> body.

Why this prompt:
- It turns the film's method into one bounded change, with a prediction made before generating.
- The viewer judges the result against that prediction and an engine check, not against taste.

## Asset-generation prompts (shown as evidence, not re-run)

- **SDXL prompts and negatives:** every image row in the repo's `ASSET-LOG.md`.
- **Stable Audio Open and MusicGen prompts:** `tools/build_audio_notebook.py` (cell 3) and the
  SFX-* / MUS-* log rows.

## The build request

**Zhaohui's request (chat, 2026-10-06):** "你先把其他工作做完吧" ("finish the remaining work
first"), after a playtest. Then the toolkit path, D:\courses\7270\brutalist.art-main.

**The course instruction followed:** "Use the course-provided Brutalist godot-gamedev workflow with
the walker modifier. This film explains how your game's art and audio were designed, generated,
and wired in."

**Narration was written by Claude Code**, in the Teardown register, from the inspected captures
and files. It was voiced by Kokoro `am_onyx`.
