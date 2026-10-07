#!/usr/bin/env python3
"""Write gamedev-evidence.json (schema 1, teaching contract code-then-result-v1).

Every file in godot/ (except .godot/ and .uid) is hashed and assigned to a component. Excerpts are
taken from the beat sheet's code beats and re-read from disk; result media are hashed as rendered.
Run after media/ is complete (the result clips must exist).
"""
import hashlib
import json
import pathlib

REEL = pathlib.Path(__file__).resolve().parent.parent
GAME = REEL.parent.parent / "godot"

COMPONENTS = {
    "generated-art": {
        "explanation": "Generated state images and background: each fighter state is one PNG on a shared "
                       "canvas, exported from the Colab SDXL pipeline at canvas_to_screen_scale; .import "
                       "sidecars keep Godot's default 2D texture import.",
        "beat_ids": ["B02", "B03", "B05", "B07"],
        "match": lambda p: p.startswith(("art/akaken/", "art/aotake/", "art/env/"))},
    "placeholder-art": {
        "explanation": "Code-drawn placeholder images (tools/export_placeholders.py) that FighterArt falls "
                       "back to when no generated image exists for a state.",
        "beat_ids": ["B06"],
        "match": lambda p: p.startswith("art/placeholder/")},
    "pose-data-and-art-loader": {
        "explanation": "poses.json (written by tools/make_poses.py) is the single source for anchors and "
                       "boxes; FighterArt loads images, anchors them by hip and ground line, and builds "
                       "hurtboxes and hitboxes from the same pose.",
        "beat_ids": ["B06", "B07"],
        "match": lambda p: p in ("data/poses.json", "fighter/fighter_art.gd")},
    "fighter-combat": {
        "explanation": "Fighter steps movement and frame data each tick; check_hit resolves every attack "
                       "exactly once (hit/blocked/whiff/interrupted) and emits attack_resolved. Input comes "
                       "from PlayerController, the seeded CpuController, or ScriptedController in tests.",
        "beat_ids": ["B08", "B09", "B02"],
        "match": lambda p: p.startswith("fighter/") and p != "fighter/fighter_art.gd"},
    "round-flow-and-stage": {
        "explanation": "main.gd runs title -> intro -> fight -> ko -> result and steps both fighters; HUD, "
                       "hit/block sparks, the background stage and the input bindings (including M/N mute) "
                       "live beside it; project.godot sets the 640x360 canvas and 60 Hz ticks.",
        "beat_ids": ["B02", "B09", "B12"],
        "match": lambda p: (p.startswith("game/") and p != "game/audio_director.gd") or p == "project.godot"},
    "audio-wiring": {
        "explanation": "AudioDirector listens to attack_resolved, knocked_out, round_started and "
                       "paused_changed and plays the generated SFX and MusicGen loop on the SFX and Music "
                       "buses; it never changes game state.",
        "beat_ids": ["B10", "B11", "B12"],
        "match": lambda p: p == "game/audio_director.gd" or p.startswith("audio/")},
    "tests-and-captures": {
        "explanation": "test_runner.gd steps the fight headless with scripted controllers (94 checks); "
                       "capture_states.gd and capture_flow.gd render the engine evidence images.",
        "beat_ids": ["B14", "B15", "B07"],
        "match": lambda p: p.startswith("tests/")},
}

ROLES = [
    (lambda p: p.endswith(".import"), "Godot import settings sidecar (authored defaults)"),
    (lambda p: p.endswith(".png"), "image asset"),
    (lambda p: p.endswith(".ogg"), "audio asset"),
    (lambda p: p.endswith(".gd"), "GDScript source"),
    (lambda p: p.endswith(".tscn"), "scene"),
    (lambda p: p.endswith(".json"), "data"),
    (lambda p: p == "project.godot", "project configuration"),
]

OBSERVATIONS = {
    "B07": "In the running engine with F1 boxes on, the generated punch image stands on the ground line, "
           "the hurtbox covers its body and the red hitbox sits on the wrapped fist.",
    "B09": "Akaken's jab meets Aotake's hurtbox during its active frames: one hit spark at the overlap, "
           "Aotake's health bar drops and he is pushed back.",
    "B12": "The opening jab whiffs, a later strike is blocked (block spark, no health lost) and a clean hit "
           "lands (hit spark, bar drops): three attack_resolved results, each with its sound in the capture.",
    "B15": "The recorded run prints 94 checks, 0 failed; 13 attacks produce 13 sound requests; the muted "
           "and unmuted seeded fights end identically.",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    sheet = json.loads((REEL / "beat_sheet.json").read_text(encoding="utf-8"))
    files = sorted(p.relative_to(GAME).as_posix() for p in GAME.rglob("*")
                   if p.is_file() and not any(x in (".godot", ".git") for x in p.relative_to(GAME).parts)
                   and p.suffix != ".uid")
    records, comps = [], {cid: {"id": cid, "explanation": c["explanation"], "beat_ids": c["beat_ids"], "files": []}
                          for cid, c in COMPONENTS.items()}
    for rel in files:
        owners = [cid for cid, c in COMPONENTS.items() if c["match"](rel)]
        if not owners:
            raise SystemExit(f"no component for {rel}")
        role = next(r for test, r in ROLES if test(rel))
        records.append({"path": rel, "sha256": sha(GAME / rel), "role": role, "component_ids": owners})
        for cid in owners:
            comps[cid]["files"].append(rel)
    excerpts, pairs = [], []
    order = [b["beat_id"] for b in sheet["beats"]]
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
            "components": list(comps.values()), "excerpts": excerpts, "exclusions": [],
            "code_result_pairs": pairs}
    (REEL / "gamedev-evidence.json").write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8")
    print(f"{len(records)} files, {len(comps)} components, {len(excerpts)} excerpts, {len(pairs)} pairs")


if __name__ == "__main__":
    main()
