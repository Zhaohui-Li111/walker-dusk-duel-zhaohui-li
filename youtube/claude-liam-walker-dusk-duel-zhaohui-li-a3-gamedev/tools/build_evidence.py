#!/usr/bin/env python3
"""Write gamedev-evidence.json (schema 1, teaching contract code-then-result-v1) for the A3 film.

Every file in godot/ (except .godot/ and .uid) is hashed. The Assignment 3 files are assigned to the
three components this film explains; the rest of godot/ is the A2 2D game, unchanged by A3 and
explained in the A2 film, so each of those files is listed as an exclusion with that reason.
Excerpts are taken from the beat sheet's code beats and re-read from disk; result media are hashed
as rendered, so run this after media/ is complete.
"""
import hashlib
import json
import pathlib

REEL = pathlib.Path(__file__).resolve().parent.parent
GAME = REEL.parent.parent / "godot"
A2_FILM = "youtube/claude-liam-walker-dusk-duel-zhaohui-li-gamedev"

COMPONENTS = {
    "prop-assets": {
        "explanation": "The three props as binary glTF exported from blender/*.blend with +Y up and transforms "
                       "applied (tools/blender/export_glb.py), with Godot's default scene-import settings in the "
                       ".import sidecars (root scale 1.0).",
        "beat_ids": ["B02", "B06", "B11"],
        "match": lambda p: p.startswith("props3d/models/")},
    "prop-room-scene": {
        "explanation": "props3d/prop_room.tscn: a 6 x 4 m floor with its top at y = 0, one DirectionalLight3D, a "
                       "camera, ambient light, the three GLB instances at y = 0 with identity bases, and a 1.70 m "
                       "reference box. Not connected to the 2D game.",
        "beat_ids": ["B07", "B08"],
        "match": lambda p: p == "props3d/prop_room.tscn"},
    "prop-checks": {
        "explanation": "tests/check_props3d.gd measures each prop headless against the A3 brief (AABB size, node "
                       "scale/rotation, tallest axis, floor gap, footprint centre, triangles, albedo hex); "
                       "tests/capture_props3d.gd renders the room's evidence stills.",
        "beat_ids": ["B09", "B10", "B11"],
        "match": lambda p: p in ("tests/check_props3d.gd", "tests/capture_props3d.gd")},
}

ROLES = [
    (lambda p: p.endswith(".import"), "Godot import settings sidecar (authored defaults)"),
    (lambda p: p.endswith(".glb"), "3D asset (binary glTF)"),
    (lambda p: p.endswith(".gd"), "GDScript source"),
    (lambda p: p.endswith(".tscn"), "scene"),
]

OBSERVATIONS = {
    "B08": "In the engine capture's low pass round the back, the bases of all three props meet the floor's "
           "top face: none sunk, none floating, none on its side; the drumheads face front and back.",
    "B10": "With the taiko raised 0.05 m in a test copy, its shadow separates from the base and the check "
           "prints 'FAIL: sits on the floor (gap 0.0500)', 49 checks, 1 failed; the real scene prints 49 "
           "checks, 0 failed.",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    sheet = json.loads((REEL / "beat_sheet.json").read_text(encoding="utf-8"))
    files = sorted(p.relative_to(GAME).as_posix() for p in GAME.rglob("*")
                   if p.is_file() and not any(x in (".godot", ".git") for x in p.relative_to(GAME).parts)
                   and p.suffix != ".uid")
    records, exclusions = [], []
    comps = {cid: {"id": cid, "explanation": c["explanation"], "beat_ids": c["beat_ids"], "files": []}
             for cid, c in COMPONENTS.items()}
    for rel in files:
        owners = [cid for cid, c in COMPONENTS.items() if c["match"](rel)]
        if not owners:
            exclusions.append({"path": rel, "reason": "Assignment 2 2D game, unchanged by Assignment 3 and not used by "
                                                      f"the prop room; explained in the A2 film ({A2_FILM})"})
            continue
        role = next(r for test, r in ROLES if test(rel))
        records.append({"path": rel, "sha256": sha(GAME / rel), "role": role, "component_ids": owners})
        for cid in owners:
            comps[cid]["files"].append(rel)
    excerpts, pairs = [], []
    for i, b in enumerate(sheet["beats"]):
        e = b.get("excerpt")
        if not e:
            continue
        lines = (GAME / e["path"]).read_text(encoding="utf-8").splitlines()
        text = "\n".join(lines[e["start_line"] - 1:e["end_line"]])
        assert text == b["shot"]["remotion"]["props"]["code"], b["beat_id"]
        excerpts.append({"beat_id": b["beat_id"], "path": e["path"], "start_line": e["start_line"],
                         "end_line": e["end_line"], "text": text})
        result = sheet["beats"][i + 1]
        media = result["shot"]["evidence_media"]
        pairs.append({"code_beat": b["beat_id"], "result_beat": result["beat_id"],
                      "observation": OBSERVATIONS[result["beat_id"]],
                      "media": {"path": media, "sha256": sha(REEL / media)}})
    data = {"schema_version": 1, "game": "godot", "source_revision": sheet["metadata"]["game"]["source_revision"],
            "teaching_contract": "code-then-result-v1", "files": records,
            "components": list(comps.values()), "excerpts": excerpts, "exclusions": exclusions,
            "code_result_pairs": pairs}
    (REEL / "gamedev-evidence.json").write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8")
    print(f"{len(records)} files, {len(exclusions)} exclusions, {len(comps)} components, "
          f"{len(excerpts)} excerpts, {len(pairs)} pairs")


if __name__ == "__main__":
    main()
