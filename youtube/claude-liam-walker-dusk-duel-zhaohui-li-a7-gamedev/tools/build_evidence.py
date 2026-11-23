#!/usr/bin/env python3
"""Write gamedev-evidence.json (schema 1, teaching contract code-then-result-v1) for the A7 film.

Adapted from the A6 reel. Every file in godot/ (except .godot/ and .uid) is hashed. The Assignment 7
files (git diff a6..8049c54 -- godot) go to the components this film explains, with fighter.gd (the
state machine both clips read, unchanged by A7); the rest of godot/ is the A2 2D game, the A3 props,
the A5 shaders and the A6 particles, unchanged by A7 and explained in the earlier films, so each is
listed as an exclusion with that reason. Excerpts are re-read from disk; result media are hashed as
rendered, so run this after media/ is complete.
"""
import hashlib
import json
import pathlib

REEL = pathlib.Path(__file__).resolve().parent.parent
GAME = REEL.parent.parent / "godot"
A2_FILM = "youtube/claude-liam-walker-dusk-duel-zhaohui-li-gamedev"
A3_FILM = "youtube/claude-liam-walker-dusk-duel-zhaohui-li-a3-gamedev"
A5_FILM = "youtube/claude-liam-walker-dusk-duel-zhaohui-li-a5-gamedev"
A6_FILM = "youtube/claude-liam-walker-dusk-duel-zhaohui-li-a6-gamedev"

COMPONENTS = {
    "lantern-sheet": {
        "explanation": "art/sheets/lantern_flame.png: a 48 x 32 sprite sheet (12 x 16 cells, 4 x 2, flame base at "
                       "(6, 15) in every cell) written by make_lantern_flame_sheet.gd (Claude Code, Zhaohui's choice); "
                       "MIT, credits in ATTRIBUTION.md; imported with nearest filtering.",
        "beat_ids": ["B04"],
        "match": lambda p: p.startswith("art/sheets/")},
    "lantern-clip": {
        "explanation": "animations/lantern_flicker.tres keys Sprite2D:frame 0-7 every 0.1 s, UPDATE_DISCRETE, length "
                       "0.8, LOOP_LINEAR; lantern_flame.tscn slices the sheet 4 x 2 with offset (-6, -15); "
                       "lantern_flame.gd only play()s and seek()s once (start_offset 0.0 / 0.4); two instances in "
                       "game/main.tscn after Embers. The AnimationPlayer is the one writer of the frame, on the idle tick.",
        "beat_ids": ["B03", "B05", "B06", "B15"],
        "match": lambda p: p.startswith("animations/lantern_") or p == "game/main.tscn"},
    "kick-arc-clip": {
        "explanation": "animations/kick_arc.tres keys Pivot:visible, rotation and modulate at Fighter.frame 0, 7, 8, "
                       "12, 13, 27, 28 over 60 (step 1/60, length 28/60, LOOP_NONE; transitions 0.5 / 2.0 / 1 / 1 / "
                       "0.4); kick_rest.tres hides the arc; fighter.tscn holds KickRig -> Pivot -> Trail, Core "
                       "(Polygon2D) and a MANUAL AnimationPlayer. The preview scene makes the fixture strips.",
        "beat_ids": ["B08", "B09", "B10", "B11"],
        "match": lambda p: p in ("animations/kick_arc.tres", "animations/kick_rest.tres", "fighter/fighter.tscn")
                           or p.startswith("previews/kick_arc_preview")},
    "kick-rig-controller": {
        "explanation": "fighter/kick_rig.gd: each physics tick at priority 100 (after Main), state kick -> "
                       "seek(Fighter.frame / 60, true) on kick_arc; any other state -> rest. Reads the state machine, "
                       "never writes it; writes only KickRig's own position and scale.",
        "beat_ids": ["B12", "B13", "B14", "B16"],
        "match": lambda p: p == "fighter/kick_rig.gd"},
    "fighter-state-machine": {
        "explanation": "fighter/fighter.gd (unchanged by A7): ATTACKS kick 7 / 5 / 16, frame counted from 0 on the "
                       "kick's first tick, check_hit while 7 < frame <= 12, whiff at 13, idle at 28; receive_hit "
                       "interrupts a kick (hurt); _update_sprite is the one writer of the fighter's Sprite2D.",
        "beat_ids": ["B08", "B14", "B15"],
        "match": lambda p: p == "fighter/fighter.gd"},
    "a7-tests": {
        "explanation": "tests/test_lantern_readback.gd (47 / 0), test_kick_readback.gd (52 / 0), test_anim_states.gd "
                       "(58 / 0, measured clock gap 0 s), test_kick_edges.gd (38 / 0), test_pins_a7.gd (19 / 0 before "
                       "and after) and the shared anim_checks.gd (track_problems); three mutations fail them.",
        "beat_ids": ["B07", "B16", "B17", "B18"],
        "match": lambda p: p in ("tests/anim_checks.gd", "tests/test_anim_states.gd", "tests/test_kick_edges.gd",
                                 "tests/test_kick_readback.gd", "tests/test_lantern_readback.gd",
                                 "tests/test_pins_a7.gd")},
}

ROLES = [
    (lambda p: p.endswith(".import"), "Godot import settings sidecar (authored)"),
    (lambda p: p.endswith(".gdshader"), "Godot shading language source"),
    (lambda p: p.endswith(".gd"), "GDScript source"),
    (lambda p: p.endswith(".tscn"), "scene"),
    (lambda p: p.endswith(".tres"), "resource"),
    (lambda p: p.endswith(".png"), "texture (PNG)"),
    (lambda p: p.endswith(".md"), "document"),
]

OBSERVATIONS = {
    "B06": "In the scripted-input capture (cropped to both lanterns), each flame changes cell every 0.1 s and the "
           "right one is half a cycle ahead (start_offset 0.4); on the title Akaken's arm covers the left lantern, "
           "which shows once he walks in. The frame track on lines 11-18 is what flips the cells.",
    "B10": "In the committed fixture-capture strip r1, capture frames 10, 13, 14, 16, 17, 23, 24 (Fighter.frame 0, "
           "6, 8, 12, 14, 26, 28) show the faint wind-up, the wound-back arc, the full-strength sweep, its head on the "
           "foot, the fade and no arc: the keys on lines 35-38 at the phase boundaries.",
    "B13": "In the scripted-input capture, a whole kick replayed at 1/8 (frames held) shows the arc wind back, sweep "
           "and fade; a later kick paused at Fighter.frame 10 keeps its arc fixed for 3 s (line 35 seeks the same "
           "frame every tick) while the right lantern flame keeps changing (its own idle clock).",
}

A7_FILES = set()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exclusion_reason(rel):
    if rel.startswith("props3d/models/") or rel in ("tests/check_props3d.gd", "tests/capture_props3d.gd"):
        return f"A3 prop asset or check, unchanged by A7 (check_props3d.gd still 49 / 0); explained in {A3_FILM}"
    if (rel.startswith("shaders/") or rel.startswith("props3d/") or rel.startswith("hint_experiment/")
            or rel in ("fighter/hurt_flash.gd", "tests/test_hurt_flash.gd", "tests/test_materials.gd",
                       "tests/capture_a5.gd", "tests/normal_map_check.gd", "tests/calibrate_normal_map.gd",
                       "MATERIALS.md", "LANGUAGE-NOTES.md")):
        return (f"Assignment 5 shader/material work, unchanged by A7 (test_hurt_flash 69 / 0, test_materials "
                f"96 / 0); explained in {A5_FILM}")
    if (rel.startswith("effects/") or rel.startswith("previews/hit_spark") or rel.startswith("previews/embers")
            or rel in ("tests/test_hit_spark_config.gd", "tests/test_hit_spark_state.gd", "tests/test_embers_config.gd",
                       "tests/test_embers_state.gd", "tests/cost_effects.gd", "tests/gpu_price.gd",
                       "game/debug_vsync.gd")):
        return (f"Assignment 6 particle work, unchanged by A7 (69 / 0, 57 / 0, 85 / 0, 38 / 0); explained in "
                f"{A6_FILM}")
    return f"Assignment 2 2D game, unchanged in behaviour by A7 (test_runner.gd still 94 / 0); explained in {A2_FILM}"


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
    (REEL / "gamedev-evidence.json").write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{len(records)} files, {len(exclusions)} exclusions, {len(comps)} components, "
          f"{len(excerpts)} excerpts, {len(pairs)} pairs")


if __name__ == "__main__":
    main()
