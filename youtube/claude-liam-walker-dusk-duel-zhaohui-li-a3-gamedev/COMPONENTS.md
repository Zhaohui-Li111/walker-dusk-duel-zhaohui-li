# COMPONENTS — what this film explains, and where

Source: `godot/` at `1e88b83`; ledger: `gamedev-evidence.json` (built by `tools/build_evidence.py`).

| Component | Files | Beats | Mechanism, and one trade-off |
|---|---|---|---|
| prop-assets | `props3d/models/prop_{lantern,makiwara,taiko}.glb` + `.import` | B02, B06, B11 | Binary glTF exported headless from `blender/*.blend` with +Y up and transforms applied (`tools/blender/export_glb.py`), imported with Godot's default scene settings (root scale 1.0). Each prop is one joined mesh with its origin at the underside centre, so a node at y = 0 stands on the floor. *Trade-off:* joining makes placement trivial, but a part can no longer be selected in Godot, and the join is where the origin error came from (B06). |
| prop-room-scene | `props3d/prop_room.tscn` | B07, B08 | A hand-written scene: a floor box with its top at y = 0, one DirectionalLight3D, a camera, ambient light, the three GLB instances with identity bases, and a 1.70 m reference box. *Trade-off:* nothing is corrected in Godot, so every fix has to happen in Blender. That is honest, but slower to iterate on. |
| prop-checks | `tests/check_props3d.gd`, `tests/capture_props3d.gd` | B09, B10, B11 | Headless `SceneTree` script. Per prop it reads the merged world AABB, every node's scale and rotation, the tallest axis, the gap to the Floor node's top, the footprint offset, the triangle count and the albedo hex. *Trade-off:* it proves numbers, not looks. Its own weaker min-y line passed on a floating prop (B10). |

**Input → state → output trace (B07 → B08 → B09 → B10):**
1. **Input:** the scene file puts the taiko instance at y = 0.
2. **State:** the GLB's lowest vertex is at local y 0, so the world AABB starts at 0.0000.
3. **Output:** the check prints gap 0.0000 and passes, and the capture shows the base on the floor.
4. **The same trace with the input changed to y = 0.05:** gap 0.0500, FAIL, and a visible shadow gap.

**Excluded:** the A2 2D game (every other file in `godot/`). It is unchanged by A3, not used by the
prop room, and explained in `youtube/claude-liam-walker-dusk-duel-zhaohui-li-gamedev`. Each file is
listed with that reason in `exclusions`.

**Outside `godot/`, shown but not in the ledger** (the checker only accepts files under the folder
holding `project.godot`): the Blender side. The B05 and B13 printouts come from
`tools/blender/build_taiko.py`. The figures use Zhaohui's screenshots and the MCP renders (see SOURCES.md).
