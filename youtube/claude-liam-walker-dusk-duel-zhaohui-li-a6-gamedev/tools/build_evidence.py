#!/usr/bin/env python3
"""Write gamedev-evidence.json (schema 1, teaching contract code-then-result-v1) for the A6 film.

Adapted from the A5 reel. Every file in godot/ (except .godot/ and .uid) is hashed. The Assignment 6
files (git diff a5..840bcfd -- godot) go to the components this film explains; the rest of godot/
is the A2 2D game, the A3 props or the A5 shaders and materials, unchanged by A6 and explained in
the earlier films, so each is listed as an exclusion with that reason. Excerpts are re-read from
disk; result media are hashed as rendered, so run this after media/ is complete.
"""
import hashlib
import json
import pathlib

REEL = pathlib.Path(__file__).resolve().parent.parent
GAME = REEL.parent.parent / "godot"
A2_FILM = "youtube/claude-liam-walker-dusk-duel-zhaohui-li-gamedev"
A3_FILM = "youtube/claude-liam-walker-dusk-duel-zhaohui-li-a3-gamedev"
A5_FILM = "youtube/claude-liam-walker-dusk-duel-zhaohui-li-a5-gamedev"

COMPONENTS = {
    "hit-spark-effect": {
        "explanation": "effects/hit_spark.tscn: a one-shot CPUParticles2D (20 particles, explosiveness 1, point "
                       "emission; spread 180, gravity (0, 25), speed 15-75 after tuning r1, damping, colour ramp, "
                       "scale curve; star texture, additive CanvasItemMaterial). Its texture is drawn by "
                       "effects/make_textures.gd; the preview scene in previews/ makes the fixture-capture strips.",
        "beat_ids": ["B03", "B04", "B05", "B06", "B07"],
        "match": lambda p: (p.startswith("effects/hit_spark") and not p.endswith("_pool.gd"))
                           or p == "effects/make_textures.gd" or p.startswith("previews/hit_spark_preview")},
    "hit-spark-pool": {
        "explanation": "effects/hit_spark_pool.gd starts one of four pooled HitSpark slots (children of Main in "
                       "game/main.tscn) on attack_resolved with result hit, at point, never restarting a live "
                       "burst; speed_scale 0 during the game's pause and hitstop; a round reset clears them.",
        "beat_ids": ["B08", "B09"],
        "match": lambda p: p in ("effects/hit_spark_pool.gd", "game/main.tscn")},
    "embers-effect": {
        "explanation": "effects/embers.tscn: a continuous CPUParticles2D (48 particles, rectangle emission 560 x 180 "
                       "px, preprocess 1.5 s, lifetime 2.5 s, two colour ramps, soft 4 x 4 texture, normal blend); "
                       "the preview scene makes the strips.",
        "beat_ids": ["B10", "B11", "B12", "B13"],
        "match": lambda p: (p.startswith("effects/embers") and p != "effects/embers_controller.gd")
                           or p.startswith("previews/embers_preview")},
    "embers-controller": {
        "explanation": "effects/embers_controller.gd polls main.phase each physics tick: restart() on entering the "
                       "fight (preprocess every round), emitting = false on leaving it, speed_scale 0 during pause "
                       "and hitstop; never touches visible (rule 4, revised after the state test).",
        "beat_ids": ["B14", "B15", "B16"],
        "match": lambda p: p == "effects/embers_controller.gd"},
    "process-shader": {
        "explanation": "shaders/particles_generated.gdshader: the particles shader Godot generated when Zhaohui "
                       "converted the hit spark to GPUParticles2D in the editor; nothing in the game uses it. Lines "
                       "137, 260, 307 and 320 implement the brief's speed, spread and gravity; the colour ramp and "
                       "scale curve were dropped (lines 348, 147).",
        "beat_ids": ["B17"],
        "match": lambda p: p == "shaders/particles_generated.gdshader"},
    "a6-tests": {
        "explanation": "tests/test_hit_spark_config.gd and test_embers_config.gd read every brief setting back "
                       "(69 / 0, 85 / 0); test_hit_spark_state.gd and test_embers_state.gd drive the real loop with "
                       "real input (57 / 0, 38 / 0), SETUP cases labelled.",
        "beat_ids": ["B16", "B18", "B20"],
        "match": lambda p: p in ("tests/test_hit_spark_config.gd", "tests/test_hit_spark_state.gd",
                                 "tests/test_embers_config.gd", "tests/test_embers_state.gd")},
    "a6-price": {
        "explanation": "tests/cost_effects.gd (headless CPU price with an empty-scene control), tests/gpu_price.gd "
                       "(windowed RenderingServer GPU time, run by Claude Code), previews/hit_spark_profile.tscn "
                       "(four bursts kept alive) and game/debug_vsync.gd (F9 toggles vsync).",
        "beat_ids": ["B19"],
        "match": lambda p: p in ("tests/cost_effects.gd", "tests/gpu_price.gd", "previews/hit_spark_profile.tscn",
                                 "game/debug_vsync.gd")},
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
    "B07": "In the committed fixture-capture strips (same seed), r0 (min speed 45) shows a hollow ring at frames "
           "12-15 and r1 (min 15, the value on line 30) a filled cluster; the widest extent falls from about 58 to "
           "48 px across (TUNING.md), smaller than Claude predicted.",
    "B09": "In the scripted-input capture, a punch lands and Esc pauses the game: the live sparks stay where they "
           "are for the 3 s pause (speed_scale 0, line 56) and finish after resume; later hits 0.5 s apart leave two "
           "bursts alive at once (lines 42-43: a free slot, no restart).",
    "B13": "In the committed embers strips (same seed), r1 (ramp alpha 0.70 / 0.50) changes 447 pixels at frame 10 "
           "against r0's 168 and 658 at frame 55 against 215 (TUNING.md); specks 1-3 px, dimmer than the spark.",
    "B15": "In the scripted-input capture, the K.O. turns emission off (line 30) and the remaining embers fade; "
           "after Enter starts round 2, the field is present as soon as the fight phase begins (restart, line 28).",
}

A5_FILES = ("fighter/hurt_flash.gd", "fighter/fighter.tscn", "props3d/make_granite_materials.gd",
            "props3d/prop_room.tscn", "tests/test_hurt_flash.gd", "tests/test_materials.gd", "tests/capture_a5.gd",
            "tests/normal_map_check.gd", "tests/calibrate_normal_map.gd", "MATERIALS.md", "LANGUAGE-NOTES.md")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exclusion_reason(rel):
    if rel.startswith("props3d/models/") or rel in ("tests/check_props3d.gd", "tests/capture_props3d.gd"):
        return f"A3 prop asset or check, unchanged by A6 (check_props3d.gd still 49 / 0); explained in {A3_FILM}"
    if (rel.startswith("shaders/") or rel.startswith("props3d/") or rel.startswith("hint_experiment/")
            or rel in A5_FILES):
        return (f"Assignment 5 shader/material work, unchanged by A6 (test_hurt_flash 69 / 0 at 30/60/144, "
                f"test_materials 96 / 0); explained in {A5_FILM}")
    return f"Assignment 2 2D game, unchanged in behaviour by A6 (test_runner.gd still 94 / 0); explained in {A2_FILM}"


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
