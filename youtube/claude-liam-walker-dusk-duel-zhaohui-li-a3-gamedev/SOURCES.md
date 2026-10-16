# SOURCES — "Dusk Duel, Measured" (godot-gamedev, walker mode)

## Source revision

- **Game source shown:** `godot/` at `1e88b83`, the last commit that changed `godot/` (the taiko
  re-exported after the hand edit). Captures were made from the working tree at `b9eab1c`, whose
  `godot/` is identical to `1e88b83`.
- **Blender sources:** `blender/*.blend` at the same revision. The code Claude ran is in
  `tools/blender/` (verbatim).
- **Versions:** Godot 4.7.2.stable.official.ed1daf0bf (GL Compatibility) · Blender 5.2.2 LTS ·
  mcp-for-blender 2.1.9 (add-on 1.8, protocol 13) · Windows 11 Home.

## Engine evidence (native, unretouched)

| File | SHA-256 | How it was made |
|---|---|---|
| capture/orbit.avi (gitignored) | `fbf5968dbedacea0e12230368d1626f29f64b11af44744ed0d259f27c8048433` | Movie Maker, `--fixed-fps 60 --resolution 3840x2160`, on `capture/game` (an isolated copy of `godot/`, window override 3840 × 2160). The camera is driven by `tools/capture_orbit.gd`; the scene is unchanged. 24.0 s, 1440 frames. |
| capture/stills/real_taiko_floor.png | `bb02ab2b2df70656f47bc2d5af22af4d3140b9a012e92af876fa5f6eb5e41b31` | `tools/capture_stills.gd` on `capture/game` |
| capture/stills/raised_taiko_floor.png | `d6c3634f6ebd5b8481ba8c3f7accd9f7ee12569da23cc41a6dc8550819b45ac7` | the same script on `capture/game-raised`, a test copy with the taiko instance at y = 0.05. **Labelled as a test copy in the film.** |
| evidence/check-props3d.txt | `65468c050982bdfaf6bc6f27b91eba6a186c8121b292330e9ec509ce29aacdf7` | `timeout 120 godot --headless --path godot --script res://tests/check_props3d.gd --fixed-fps 60`: 49 checks, 0 failed, exit 0 |
| evidence/check-props3d-raised-copy.txt | `ece2bc49fa0604df9eb794e88705780a3259ab840e40acb5583c5bad573d9581` | the same check on `capture/game-raised`: 49 checks, 1 failed, exit 1 |

## Blender evidence

| File | SHA-256 | What it is |
|---|---|---|
| evidence/blender/zhaohui_object_mode_taiko_selected.png | `f118a50d00776276bb02f9ac89b64697260c8a54f71f562baa021e55a23c9c43` | **Zhaohui's own screenshot** (Win + PrtScn, 16:40) |
| evidence/blender/zhaohui_bottom_view_taiko.png | `d9867a4e094238563924c471cb88f096676d98ba2f4f16f699a33b249f140d93` | Zhaohui's own screenshot, 16:41 |
| evidence/blender/zhaohui_back_view_taiko.png | `067a362e23d65ad9c8d067be8b7c4012f8023ba45a3a379ba4d2de971bffc660` | Zhaohui's own screenshot, 16:41 |
| capture/mcp_look/1552_taiko_angles.png | `5e80562f6c994d7aa0995d5d1697dbb13b8cdfaa8d9de429ee794e514e841d08` | Claude's MCP `look` render, 15:52, 644 px |
| capture/mcp_look/1549_makiwara_round_bands.png | `9aa3b843776e75211a320f9ae4f481bdf4deb9ef767c1f3e06d016622cf22929` | MCP `look`, 15:49 |
| capture/mcp_look/1550_makiwara_chamfered_bands.png | `dcfe7394de5999c6349ea19897c64bfcff5a6b4736950dd4372553895cc59dfb` | MCP `look`, 15:50 |
| capture/mcp_look/1629_taiko_after_hand_edit.png | `77a45ff7b8c235ab72fcd8c48ec7416f9588cf307955ed25ed1f6b2a7d658468` | MCP `look` of the saved hand edit, 16:29 |
| capture/mcp_look/1635_taiko_repaired.png | `3411c6a3a73caa9d87eb6a2b89f18020f0f0f69ed5ae10807f0c5475ef6c46c0` | MCP `look` after the repair, 16:35 |

The MCP renders are viewport images of Zhaohui's live Blender, taken by Claude. They are labelled
"MCP look render" on screen and are not Zhaohui's screenshots. The 644 px originals are enlarged.

## Figures

`tools/build_figures.py` lays out `figures/fig_*.png` from the files above, cropped and scaled; the
only new pixels are labels. Hashes of the figures and their sources: `figures/figures.json`.
Numbers on `fig_brief` come from CHANGE-BRIEF.md A3; numbers on `fig_numbers` come from the brief,
`tools/blender/check_blend.py` and `evidence/check-props3d.txt`.

## Prompts shown

- **B00 and B17:** Walker prompts written for the film. B00 is labelled a reconstruction.
- **B05:** the `user_prompt` actually passed to `execute_blender_code` for the build. It comes from
  the task brief the parent Claude Code session wrote, **not Zhaohui's words**, and is labelled so
  on screen. The English line is a translation.
- **B13:** Zhaohui's own words, verbatim ("我不太会改，你改吧"), with a translation.
- **Printouts in B05 and B13:** copied from the tool results of those calls, verbatim.

## Tools and models

Kokoro `am_onyx` (local, free) narrated; faster-whisper `base.en` checked the takes. Remotion
scenes come from the Brutalist toolkit at `D:\courses\7270\brutalist.art-main\brutalist.art-main`:
ClaudeComposerAsk, BrutalistHesitantWriter, GodotDesignFigure, GodotDevWorkbench,
ClaudeVerdictArtifact and ClaudeTitleOutro. No toolkit file was changed for this film. No paid service
was used.

## Corrections applied while scripting (DOUBLE-CHECK LAW)

- The build prompt had been logged as Zhaohui's words. It is the parent session's brief, so it was
  corrected in FRICTIONAL.md and labelled on screen.
- The hand-edit defect had been logged as z-fighting between coincident faces. The body had moved
  2.3 mm, so the faces were not coplanar. The film says only that red showed through a flattened,
  twisted head.
- "One call per prop": the lantern and the taiko each needed a second call (a save, and the origin
  fix), so the narration says the build was one call per prop, and the second calls are shown.
