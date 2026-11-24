"""Write gamedev-evidence.json (schema 1, teaching contract code-then-result-v1) for the A8 pitch film.

Adapted from the A7 reel. Every file in godot/ (except .godot/ and .uid) is hashed. The pitch explains
the parts it shows: the round flow (game/main.gd, main.tscn), the CPU opponent (fighter/cpu_controller.gd,
excerpted in B05, its result in the capture in B06), the player controller the capture bot drives, and the
test suites whose logs B08 shows. Everything else is unchanged, already explained in the A2-A7 films, and
listed as an exclusion with that reason. Run after media/ is complete (result media are hashed).
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
A7_FILM = "youtube/claude-liam-walker-dusk-duel-zhaohui-li-a7-gamedev"

COMPONENTS = {
    "round-flow": {
        "explanation": "game/main.gd and game/main.tscn: title -> intro -> fight -> ko -> result -> rematch on the "
                       "physics tick; both fighters stepped, then hits checked. The loop B01-B02 show, as it exists "
                       "on desktop (commit 6317281 onward; test_runner.gd 94 / 0).",
        "beat_ids": ["B01", "B02"],
        "match": lambda p: p in ("game/main.gd", "game/main.tscn")},
    "cpu-opponent": {
        "explanation": "fighter/cpu_controller.gd: re-decides every 10 ticks with a seeded generator; blocks a close "
                       "attack at 55 %, walks in out of kick range, steps back when too close, kicks in range at 50 % "
                       "with a 40-tick cooldown. Its Intent drives fighter.gd like the player's keys.",
        "beat_ids": ["B05", "B06"],
        "match": lambda p: p in ("fighter/cpu_controller.gd", "fighter/intent.gd")},
    "player-input": {
        "explanation": "fighter/player_controller.gd reads the p1_* actions (game/controls.gd); the capture bot sends "
                       "those actions with Input.parse_input_event, so the capture is real input handling.",
        "beat_ids": ["B01", "B06"],
        "match": lambda p: p in ("fighter/player_controller.gd", "game/controls.gd")},
    "tests": {
        "explanation": "tests/test_runner.gd (94 / 0) and the A5-A7 suites whose logs B08 shows: test_hurt_flash "
                       "(69 / 0), test_hit_spark_state (57 / 0), test_embers_state (38 / 0), test_kick_edges (38 / 0), "
                       "test_pins_a7 (19 / 0).",
        "beat_ids": ["B08"],
        "match": lambda p: p in ("tests/test_runner.gd", "tests/test_hurt_flash.gd", "tests/test_hit_spark_state.gd",
                                 "tests/test_embers_state.gd", "tests/test_kick_edges.gd", "tests/test_pins_a7.gd")},
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
    "B06": "In the scripted-input capture, Aotake blocks Akaken's punches (BLOCKED at 10.1 and 10.6 s) and its kick "
           "hits at 11.1 s; in round 2, where the capture sends no keys, Aotake walks in (line 53-54) and kicks the "
           "standing Akaken (line 57-59) about every 0.7 s.",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exclusion_reason(rel):
    if rel.startswith("props3d/models/") or rel in ("tests/check_props3d.gd", "tests/capture_props3d.gd"):
        return f"A3 prop asset or check, unchanged; not shown in the pitch; explained in {A3_FILM}"
    if (rel.startswith("shaders/") or rel.startswith("props3d/") or rel.startswith("hint_experiment/")
            or rel in ("fighter/hurt_flash.gd", "tests/test_materials.gd", "tests/capture_a5.gd",
                       "tests/normal_map_check.gd", "tests/calibrate_normal_map.gd", "MATERIALS.md", "LANGUAGE-NOTES.md")):
        return f"Assignment 5 shader/material work, unchanged; cited by tag in B08; explained in {A5_FILM}"
    if (rel.startswith("effects/") or rel.startswith("previews/hit_spark") or rel.startswith("previews/embers")
            or rel in ("tests/test_hit_spark_config.gd", "tests/test_embers_config.gd", "tests/cost_effects.gd",
                       "tests/gpu_price.gd", "game/debug_vsync.gd")):
        return f"Assignment 6 particle work, unchanged; cited in B08-B09; explained in {A6_FILM}"
    if (rel.startswith("animations/") or rel.startswith("art/sheets/") or rel.startswith("previews/kick_arc")
            or rel in ("fighter/kick_rig.gd", "tests/anim_checks.gd", "tests/test_anim_states.gd",
                       "tests/test_kick_readback.gd", "tests/test_lantern_readback.gd")):
        return f"Assignment 7 animation work, unchanged; cited by tag in B08; explained in {A7_FILM}"
    return f"Assignment 2 2D game, unchanged (test_runner.gd 94 / 0); seen in the capture; explained in {A2_FILM}"


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
