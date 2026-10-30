#!/usr/bin/env python3
"""Write gamedev-evidence.json (schema 1, teaching contract code-then-result-v1) for the A5 film.

Adapted from the A3 reel. Every file in godot/ (except .godot/ and .uid) is hashed. The Assignment 5
files go to the components this film explains; the rest of godot/ is the A2 2D game or the A3 prop
assets, unchanged by A5 in what they do and explained in the earlier films, so each is listed as an
exclusion with that reason. Excerpts are re-read from disk; result media are hashed as rendered, so
run this after media/ is complete.
"""
import hashlib
import json
import pathlib

REEL = pathlib.Path(__file__).resolve().parent.parent
GAME = REEL.parent.parent / "godot"
A2_FILM = "youtube/claude-liam-walker-dusk-duel-zhaohui-li-gamedev"
A3_FILM = "youtube/claude-liam-walker-dusk-duel-zhaohui-li-a3-gamedev"

COMPONENTS = {
    "hurt-flash-shader": {
        "explanation": "shaders/hurt_flash.gdshader, typed by Zhaohui: a canvas_item shader with two uniforms "
                       "(hurt_amount, flash_color) and the colour line mix(COLOR.rgb, flash_color.rgb, hurt_amount).",
        "beat_ids": ["B02", "B04", "B05", "B08"],
        "match": lambda p: p == "shaders/hurt_flash.gdshader"},
    "hurt-flash-driver": {
        "explanation": "fighter/hurt_flash.gd, written by Claude: a node under each fighter's Sprite2D that builds "
                       "its own ShaderMaterial and sets hurt_amount = stun / HITSTUN every physics tick, after "
                       "main.gd steps the fight; fighter.tscn adds the node.",
        "beat_ids": ["B06", "B07"],
        "match": lambda p: p in ("fighter/hurt_flash.gd", "fighter/fighter.tscn")},
    "hurt-flash-tests": {
        "explanation": "tests/test_hurt_flash.gd drives the real loop with the J key and checks the uniform list, "
                       "defaults from source and rules 1-6 at 30/60/144 fps; tests/capture_a5.gd makes the "
                       "windowed in-engine captures.",
        "beat_ids": ["B09", "B10", "B17"],
        "match": lambda p: p in ("tests/test_hurt_flash.gd", "tests/capture_a5.gd")},
    "granite-shader-and-materials": {
        "explanation": "shaders/granite.gdshader, typed by Zhaohui (colour texture with source_color, roughness and "
                       "normal map as data, four uniforms in two groups); props3d/materials/*.tres from "
                       "props3d/make_granite_materials.gd; the floor and StonePlinth in prop_room.tscn; the Poly "
                       "Haven textures with explicit .import settings and ATTRIBUTION.md.",
        "beat_ids": ["B11", "B12", "B13"],
        "match": lambda p: p.startswith("shaders/granite") or p.startswith("props3d/materials/")
                           or p.startswith("props3d/textures/") or p in ("props3d/make_granite_materials.gd",
                                                                          "props3d/prop_room.tscn")},
    "material-tests": {
        "explanation": "tests/test_materials.gd pins the audit (MATERIALS.md): shader paths, hints from source, "
                       "material values, .import settings and curl ratios; tests/normal_map_check.gd (from the "
                       "handout) and tests/calibrate_normal_map.gd check the normal map.",
        "beat_ids": ["B10", "B17"],
        "match": lambda p: p in ("tests/test_materials.gd", "tests/normal_map_check.gd",
                                 "tests/calibrate_normal_map.gd", "MATERIALS.md")},
    "hint-experiment": {
        "explanation": "shaders/hint_experiment.gdshader, typed by Zhaohui: two samplers on one 3 x 1 grey PNG, "
                       "with and without source_color, picked by a bool on unshaded quads; the scene, its two "
                       "materials, and the scripts that write the PNG and the materials.",
        "beat_ids": ["B14", "B15"],
        "match": lambda p: p.startswith("shaders/hint_experiment") or p.startswith("hint_experiment/")},
    "generated-standard-shader": {
        "explanation": "shaders/standard_generated.gdshader: Godot's own code for a StandardMaterial3D with the "
                       "granite textures, converted in the editor by Zhaohui; nothing in the game uses it.",
        "beat_ids": ["B16"],
        "match": lambda p: p == "shaders/standard_generated.gdshader"},
}

ROLES = [
    (lambda p: p.endswith(".import"), "Godot import settings sidecar (authored)"),
    (lambda p: p.endswith(".gdshader"), "Godot shading language source"),
    (lambda p: p.endswith(".gd"), "GDScript source"),
    (lambda p: p.endswith(".tscn"), "scene"),
    (lambda p: p.endswith(".tres"), "ShaderMaterial resource"),
    (lambda p: p.endswith(".png"), "texture (PNG)"),
    (lambda p: p.endswith(".md"), "document"),
]

OBSERVATIONS = {
    "B05": "In-engine captures of Akaken with the driver paused and hurt_amount set from code: P-gi reads "
           "(221, 89, 0), (238, 44, 0), (254, 0, 0) and P-fist (239, 229, 171), (247, 115, 86), (254, 0, 0) at "
           "0.0, 0.5 and 1.0, each within one step of Zhaohui's hand prediction from the colour line.",
    "B07": "In the scripted-input capture, Aotake's kick lands and Akaken alone turns red and fades while "
           "Aotake keeps its own colours: each fighter's material carries its own hurt_amount.",
    "B12": "In the prop room capture, the floor (uv_scale 6.0, white) and the plinth (uv_scale 1.0, #6E6680) "
           "both use granite.gdshader; with only the floor's tint changed in memory the floor pixel moves "
           "from (115, 94, 75) to (48, 76, 35) and the plinth pixel stays (12, 7, 9).",
    "B15": "In the hint-experiment capture both quads read 64 / 128 / 192, the stored values, against "
           "Zhaohui's prediction of 137 / 188 / 224 for quad B; a separate texture object for B changes nothing.",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exclusion_reason(rel):
    if rel.startswith("props3d/models/"):
        return f"A3 prop asset, unchanged by A5 (the props have no UVs, so A5 does not texture them); explained in {A3_FILM}"
    if rel in ("tests/check_props3d.gd", "tests/capture_props3d.gd"):
        return f"A3 prop check, unchanged by A5 and still passing (49 / 0); explained in {A3_FILM}"
    return f"Assignment 2 2D game, unchanged in behaviour by A5 (test_runner.gd still 94 / 0); explained in {A2_FILM}"


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
            exclusions.append({"path": rel, "reason": exclusion_reason(rel)})
            continue
        role = next((r for test, r in ROLES if test(rel)), "file")
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
