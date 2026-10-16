# PROMPTS — every prompt in or behind the film

## On screen

| Beat | Prompt | Status |
|---|---|---|
| B00 | "Please use Walker to turn my Dusk Duel brief into three low-poly 3D props, a stone lantern, a makiwara and a taiko drum, built in Blender through the Blender MCP to the sizes, origins and triangle budgets I committed, then exported to a small Godot 3D prop room and checked." | **Reconstruction** written for the film (labelled). The work was done step by step in one session. |
| B05 | "严格按 CHANGE-BRIEF.md 的 A3 规格，一个一个建（PROP-LANTERN → PROP-MAKIWARA → PROP-TAIKO），每个一个 .blend 文件" | The `user_prompt` actually passed to `execute_blender_code`. It comes from the parent Claude Code session's task brief, **not Zhaohui's words** (labelled). |
| B13 | "我不太会改，你改吧" | Zhaohui's own words, verbatim, passed as `user_prompt` to the repair calls. |
| B17 | "Please use Walker to add one simple 3D prop to my game through the Blender MCP. First write its size in metres, its origin, a triangle budget and three predicted failures in my brief, and commit it. Build it one object per call, then write a Godot check that measures it against the floor, and prove that check fails when I raise the prop." | Handoff prompt written for the viewer. |

## Behind the film

- **The build code:** every `execute_blender_code` body, verbatim, in `tools/blender/build_*.py`.
- **The film:** built by Claude Code from Zhaohui's request "在这里完成此任务：A3 Brutalist explainer
  film (after hand edit)", following the godot-gamedev SKILL.md (walker mode) and the documents it
  references.
