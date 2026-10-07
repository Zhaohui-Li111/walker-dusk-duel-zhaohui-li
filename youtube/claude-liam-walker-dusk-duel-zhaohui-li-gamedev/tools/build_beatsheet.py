#!/usr/bin/env python3
"""Write beat_sheet.json for the gamedev film.

Code excerpts are read from the hashed source files at the line ranges below, so what is shown
on screen is the file's text byte for byte. Cue times are fractions of each beat's measured
narration once mp3/beat-Bxx.mp3 exists (audio is the clock), estimates before that.
Capture windows (seconds into capture/run-01.avi) come from tools/windows.json, which is
written after inspecting the capture's input log and frames.
"""
import base64
import json
import pathlib
import subprocess

REEL = pathlib.Path(__file__).resolve().parent.parent
REPO = REEL.parent.parent
GAME = REPO / "godot"
SLUG = REEL.name
TITLE = "Dusk Duel, Generated"
SOURCE_REV = "4e0cf14"
PROJECT = "walker-dusk-duel"
FIG = REEL / "figures"
WINDOWS = json.loads((REEL / "tools" / "windows.json").read_text(encoding="utf-8"))
OLD = json.loads((REEL / "beat_sheet.json").read_text(encoding="utf-8")) if (REEL / "beat_sheet.json").exists() else None


def measured(bid):
    for name in (f"beat-{bid}.mp3",):
        p = REEL / "mp3" / name
        if p.is_file():
            out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                  "-of", "default=nw=1:nk=1", str(p)], capture_output=True, text=True)
            return float(out.stdout.strip())
    return None


def excerpt(rel, start, end):
    lines = (GAME / rel).read_text(encoding="utf-8").splitlines()
    return "\n".join(lines[start - 1:end])


def data_uri(path):
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode()


def beat(bid, act, narration, est, shot, **extra):
    b = {"beat_id": bid, "act": act, "narration_text": narration, "voice": "am_onyx",
         "engine": "kokoro", "estimated_duration_s": est, "shot": shot}
    b.update(extra)
    if OLD:
        prev = next((o for o in OLD["beats"] if o["beat_id"] == bid), None)
        if prev and prev.get("narration_text") == narration:
            for k in ("audio_file", "actual_duration_s"):
                if k in prev:
                    b[k] = prev[k]
    return b


def dur(bid, est):
    return measured(bid) or est


def code_beat(bid, rel, start, end, title, narration, est, notes, cue_fracs, output):
    d = dur(bid, est)
    code = excerpt(rel, start, end)
    cues = [{"at": round(f * d, 2), "line": line, "label": label} for f, line, label in cue_fracs]
    shot = {"type": "GRAPHIC", "class": "SHOW", "source": "remotion", "motion": "line-highlight",
            "show": [{"at": f"{f:.2f}", "event": f"line {line} highlights: {label}"} for f, line, label in cue_fracs],
            "remotion": {"pattern": "GodotDevWorkbench", "props": {
                "mode": "code", "title": title, "project": PROJECT, "path": f"res://{rel}",
                "source": f"Godot editor reconstruction · godot/{rel} lines {start}-{end} · source {SOURCE_REV}",
                "code": code, "startLine": start, "codeFontSize": 24,
                "inspectorLabel": "Source notes — not Inspector values",
                "notes": notes, "cues": cues, "output": output, "durationSeconds": round(d + 0.2, 2)}}}
    return beat(bid, "MECHANISM", narration, est, shot, excerpt={"path": rel, "start_line": start, "end_line": end})


DOCUMENTARY_FIGURES = {"B04", "B05"}   # pages of real generation outputs; see BUILD-LOG section 7


def figure_beat(bid, act, image, title, status, label, cards, cue_fracs, narration, est, source, show):
    d = dur(bid, est)
    shot = {"type": "STILL" if bid in DOCUMENTARY_FIGURES else "GRAPHIC", "class": "SHOW", "source": "remotion", "motion": "card-cues", "show": show,
            "remotion": {"pattern": "GodotDesignFigure", "props": {
                "title": title, "status": status, "image": data_uri(FIG / image), "imageLabel": label,
                "source": source, "cards": cards,
                "cues": [{"at": round(f * d, 2), "card": c} for f, c in cue_fracs],
                "durationSeconds": round(d + 0.2, 2)}},
            "figure": f"figures/{image}"}
    return beat(bid, act, narration, est, shot)


def footage_beat(bid, act, window, narration, est, show, label, evidence=False, **extra):
    w = WINDOWS[window]
    # VIDEO / STILL: raw engine output, which GATE T exempts from pixel typography checks (its
    # contents are diegetic). The labels burned on by build_media.py are checked separately on a
    # masked copy (_qc/typecheck-masked, BUILD-LOG section 7).
    shot = {"type": "VIDEO", "class": "SHOW", "source": "capture", "motion": "none", "capture": "run-01",
            "capture_start_s": w.get("start"), "capture_end_s": w.get("end"), "label": label, "show": show}
    if "state" in w:                      # an engine screenshot from tests/capture_states.gd
        shot.update({"type": "STILL", "capture": "states", "state": w["state"],
                     "capture_file": f"capture/evidence/states/{w['state']}_4k.png"})
        shot.pop("capture_start_s"); shot.pop("capture_end_s")
    if evidence:
        shot["evidence_media"] = f"media/{bid}.mp4"
    return beat(bid, act, narration, est, shot, **extra)


LABEL_FOOT = "SCRIPTED INPUT · native 4K Godot capture of the slice · not a human playtest"


def build():
    beats = []
    beats.append(beat("B00", "ASK",
        "Hola, this is Liam, in for Bear. Jow-hway Lee designed Dusk Duel: two cartoon martial artists, "
        "one round, at dusk. Its fighters, its courtyard, its sound effects and its music all came out of free models. "
        "This film follows one punch and one hit sound from the design sheet into the running game, "
        "and says who decided what.", 20,
        {"type": "GRAPHIC", "class": "SHOW", "source": "remotion", "motion": "type-on",
         "show": [{"at": "0.02", "event": "composer card fades in on the cream page"},
                  {"at": "0.12", "event": "greeting 'Hola, Liam' appears above the composer"},
                  {"at": "0.3", "event": "the reconstructed Walker ask types in"},
                  {"at": "0.66", "event": "send button arms terracotta"},
                  {"at": "0.78", "event": "three RESULT lines land beneath the card"}],
         "remotion": {"pattern": "ClaudeComposerAsk", "props": {
             "greeting": "Hola, Liam", "topic": "WALKER · GODOT GAMEDEV", "segment": TITLE,
             "command": "Please use Walker to convert my game design document about a cartoon martial-arts "
                        "duel at dusk (two fighters, one round, every hit felt) into a Godot asset slice: "
                        "generate the fighters, the courtyard, four sound effects and a music loop with free "
                        "models, and wire them in.",
             "runningText": "reconstructed ask · the slice was built step by step",
             "folderLabel": "@NikBearBrown", "modelLabel": "Claude", "effortLabel": "High",
             "output": ["16 state images + background: SDXL on a free Colab T4.",
                        "4 sound effects: Stable Audio Open. Loop: MusicGen.",
                        "Godot test run: 94 checks, 0 failed."]}}},
        role_note="COLD OPEN LAW, walker B00. The Walker prompt is an ILLUSTRATIVE RECONSTRUCTION: the slice "
                  "was built over many sessions, not from one Walker run. RESULT lines are real outcomes "
                  "(ASSET-LOG, test run at 4e0cf14). Liam named in first breath."))

    beats.append(beat("B01", "BLUF",
        "Free models drew this game's art and sound. A design sheet fixed every pose, colour and event "
        "first, and Godot tests checked the fit. The model is the hand; the sheet is the brief.", 12,
        {"type": "GRAPHIC", "class": "SHOW", "source": "remotion", "motion": "type-on-correct",
         "show": [{"at": "0.0", "event": "cream page; typing begins during the lead silence"},
                  {"at": "0.2", "event": "'Free models designed this game's art and sound.' types, then pauses"},
                  {"at": "0.45", "event": "'designed' struck through in terracotta"},
                  {"at": "0.6", "event": "'drew' types in its place"},
                  {"at": "0.85", "event": "corrected overview settles before the cut"}],
         "remotion": {"pattern": "BrutalistHesitantWriter", "props": {
             "contextTitle": "BLUF",
             "text": "Free models designed this game's art and sound.\nA design sheet fixed every pose,\ncolour and event first;\nGodot tests checked the fit.",
             "triggerWords": "designed",
             "replacementWords": "drew",
             "fontSize": 80, "lineSpacing": 2.4, "align": "center", "seed": "4417",
             "mistakeRate": 2, "hesitateWithin": 0, "hesitateBetween": 1, "charMs": 8,
             "ink": "#3D3929", "accent": "#D97757", "bg": "#FAF9F5", "brandLabel": "@NikBearBrown"}}},
        lead_silence_s=0.8,
        role_note="EXECUTIVE-SUMMARY LAW. The corrected misconception is the reel's own: 'the models designed "
                  "the art' -> they drew it to a spec the design fixed. BrutalistHesitantWriter matches single tokens only, so the one word carrying the misconception ('designed') is the trigger."))

    beats.append(footage_beat("B02", "OPEN", "open",
        "Here's the slice: Ah-kah-ken in red, a scripted keyboard driver, against Ow-tah-keh, the game's "
        "seeded opponent. Three pillars: every hit is felt, read the opponent, a quiet dusk ritual. The "
        "fighters and courtyard are generated; the sparks and health bars are code.", 13,
        [{"at": "0.05", "event": "round 1 fight underway in the dusk courtyard"},
         {"at": "0.5", "event": "Akaken closes in and trades strikes with Aotake"}], LABEL_FOOT,
        role_note="Real engine capture (Movie Maker), silent under narration; the slice's own audio is "
                  "heard unnarrated in B13."))

    beats.append(figure_beat("B03", "DESIGN", "fig_design_punch.png", "The Jab, Before Any Model",
        "DESIGN · CHARACTER-SHEET pose 06 and palette", "design/character/akaken/collision.png + colorblock/06_punch_jab.png",
        [{"label": "Skeleton", "text": "pose 06, one canvas"}, {"label": "Hurtbox", "text": "green: where he is hit"},
         {"label": "Hitbox", "text": "red: elbow to fist"}, {"label": "Palette", "text": "five colours, fixed"}],
        [(0.05, 0), (0.3, 1), (0.48, 2), (0.7, 3)],
        "The trace starts on paper. The character sheet fixed the jab before any model ran: the skeleton, "
        "the green box where Ah-kah-ken can be hit, the red box from elbow to fist that does the hitting, and "
        "five colours. The colour block on the right paints exactly those colours onto that skeleton. It "
        "is the brief, not the art.", 18,
        "Source: CHARACTER-SHEET.md; tools/make_poses.py and tools/colorblock.py outputs (repo, rev 4e0cf14)",
        [{"at": "0.05", "event": "pose 06 with its boxes appears; Skeleton card lights"},
         {"at": "0.3", "event": "Hurtbox card lights on 'green box'"},
         {"at": "0.48", "event": "Hitbox card lights on 'red box'"},
         {"at": "0.7", "event": "Palette card lights; swatches beside the colour block"}]))

    beats.append(figure_beat("B04", "FALSIFIABILITY", "fig_rounds_reference.png", "Prompts Alone Failed",
        "OBSERVED · five reference rounds, ASSET-LOG CHAR-AK-REF", "design/generations/sheets/CHAR-AK-REF_*.png",
        [{"label": "Rounds 1-3", "text": "prompt only: wrong gi"}, {"label": "Why", "text": "text won't bind 5 colours"},
         {"label": "Round 4", "text": "strength 0.6: too close"}, {"label": "Round 5", "text": "0.75: s143 kept"}],
        [(0.05, 0), (0.35, 1), (0.55, 2), (0.78, 3)],
        "It didn't start that way. Rounds one to three were prompts alone. The style was right, the "
        "character wasn't: no red gi, beards, a turban where the headband should be. SDXL won't bind five "
        "colours to five garments from text. Round four started from the colour block at strength 0.6, "
        "and stayed too close to the mannequin. Round five, at 0.75, let the model redraw.", 22,
        "Source: ASSET-LOG.md rows CHAR-AK-REF_s101-s144; FRICTIONAL.md 2026-10-05/06",
        [{"at": "0.05", "event": "rounds 1 and 3: off-model fighters, Rounds 1-3 card lights"},
         {"at": "0.35", "event": "Why card lights"},
         {"at": "0.55", "event": "round 4 row: colours right, tube limbs"},
         {"at": "0.78", "event": "round 5 row: model-drawn limbs, Round 5 card lights"}]))

    beats.append(figure_beat("B05", "PIPELINE", "fig_pipeline_punch.png", "One Jab Through The Pipeline",
        "OBSERVED · CHAR-AK-PUNCH, SDXL + ControlNet + IP-Adapter, Colab T4", "seeds 201 and 202, ASSET-LOG",
        [{"label": "Pose", "text": "OpenPose ControlNet 0.9"}, {"label": "Start", "text": "colour block, 0.75"},
         {"label": "Pick", "text": "palette 47.4 vs 51.8"}, {"label": "Export", "text": "108x158 PNG"}],
        [(0.04, 0), (0.18, 1), (0.5, 2), (0.82, 3)],
        "Then the jab itself. The skeleton steers the pose through ControlNet, the colour block is the "
        "starting image, and the round-five reference holds the look through IP-Adapter. Two seeds came "
        "back. Claude, deciding for Jow-hway, kept seed two-oh-one: its colours measured closer to the sheet, 47.4 "
        "against 51.8. Then the background was cut away and the canvas scaled to 108 by 158 pixels.", 22,
        "Source: ASSET-LOG.md rows CHAR-AK-PUNCH_s201/s202 (model commits in SOURCES.md)",
        [{"at": "0.04", "event": "skeleton panel; Pose card lights"},
         {"at": "0.18", "event": "colour block panel; Start card lights"},
         {"at": "0.5", "event": "s201 and s202 with scores; s202 struck; Pick card lights"},
         {"at": "0.82", "event": "exported punch.png on a checkerboard; Export card lights"}]))

    beats.append(code_beat("B06", "fighter/fighter_art.gd", 32, 44, "FighterArt Anchors Every Image",
        "In Godot, FighterArt reads the same poses file the sheet was drawn from. For each state it takes "
        "the hip from keypoints eight and eleven, and the ground line, so every image hangs from one "
        "anchor. Hurtbox and hitbox come from the pose, not from the picture. If a generated PNG exists "
        "it wins; otherwise the placeholder loads.", 20,
        [{"label": "Data in", "value": "res://data/poses.json"},
         {"label": "Anchor", "value": "hip x, ground line"},
         {"label": "Image", "value": "generated, else placeholder"}],
        [(0.05, 32, "one entry per state in poses.json"), (0.25, 35, "hip x from keypoints 8 and 11"),
         (0.42, 38, "boxes come from the pose"), (0.7, 44, "generated image wins over the placeholder")],
        ["godot/fighter/fighter_art.gd", "static FighterArt.load_for(id)"]))

    beats.append(footage_beat("B07", "RESULT", "states_punch",
        "Here that is in the running engine, collision boxes on, in a staged pose. The generated jab "
        "stands on the ground line, the green hurtbox covers its body, and the red hitbox, faint because "
        "nothing is attacking yet, sits on the wrapped fist. Both were drawn on the skeleton the model was "
        "steered by. If art and boxes disagreed, you'd see it here first.", 18,
        [{"at": "0.05", "event": "both fighters in punch/kick state with F1 boxes on"},
         {"at": "0.4", "event": "red hitbox over Akaken's wrapped fist"},
         {"at": "0.7", "event": "feet on the ground line, hurtbox over the body"}],
        "ENGINE CAPTURE · collision boxes on (F1) · staged pose, not gameplay", evidence=True,
        role_note="Result of B06: actual engine screenshot from tests/capture_states.gd run on the isolated "
                  "copy at 3840x2160. The pose is staged (labelled), the boxes are the game's own."))

    beats.append(code_beat("B08", "fighter/fighter.gd", 160, 172, "The Jab Lands In check_hit",
        "The punch lands in check_hit. Only during the active frames does the hitbox have to meet the "
        "opponent's hurtbox. receive_hit then says blocked or not, and the attack resolves exactly once: "
        "hit or blocked here, whiff if the window ends empty. Sound decides nothing; it only listens to "
        "that one signal.", 18,
        [{"label": "Punch frames", "value": "startup 4, active 4, recovery 10"},
         {"label": "Damage", "value": "8"},
         {"label": "Signal", "value": "attack_resolved"}],
        [(0.05, 160, "called after both fighters moved"), (0.22, 164, "active frames only"),
         (0.42, 168, "hitbox must meet the hurtbox"), (0.62, 171, "blocked or not is decided by the defender"),
         (0.8, 172, "resolved exactly once")],
        ["godot/fighter/fighter.gd", "Fighter.check_hit()"]))

    beats.append(footage_beat("B09", "RESULT", "hit",
        "Watch the fist. The jab connects, a spark lands on the overlap, Ow-tah-keh's bar drops and he's "
        "pushed back. One resolved attack, one result.", 8,
        [{"at": "0.2", "event": "Akaken's jab connects; hit spark at the box overlap"},
         {"at": "0.5", "event": "Aotake's health bar drops; he is pushed away"}], LABEL_FOOT, evidence=True))

    beats.append(figure_beat("B10", "DESIGN", "fig_sfx_candidates.png", "Sound: Event First, File Second",
        "OBSERVED · 16 Stable Audio Open takes, measured not heard", "design/generations/audio/checks/SFX_candidates_spectrograms.png",
        [{"label": "Events", "text": "whiff, hit, block, K.O."}, {"label": "Hit s12", "text": "0 ms lead-in, heaviest"},
         {"label": "Block s14", "text": "bright clack, no lead-in"}, {"label": "Judge", "text": "Claude can't listen"}],
        [(0.05, 0), (0.4, 1), (0.6, 2), (0.82, 3)],
        "Sound followed the same rule: event first, file second. The change brief names four events, and "
        "Stable Audio Open made four takes of each. Claude can't listen, so it measured: how fast each "
        "take starts, how long it rings, how much low end it has. The hit with no lead-in and the most "
        "weight won. The block was picked for its bright clack, so the two stay apart.", 22,
        "Source: ASSET-LOG.md SFX-* rows; FRICTIONAL.md 2026-10-06 sound effects",
        [{"at": "0.05", "event": "4 x 4 spectrogram grid appears; Events card lights"},
         {"at": "0.4", "event": "Hit s12 card lights"}, {"at": "0.6", "event": "Block s14 card lights"},
         {"at": "0.82", "event": "Judge card lights"}]))

    beats.append(code_beat("B11", "game/audio_director.gd", 100, 108, "AudioDirector Only Listens",
        "AudioDirector is the whole wiring. One result maps to one sound; a knockout plays the knockout "
        "sound and stops the MusicGen loop. It never touches health or state, so a missing or muted file "
        "can't change the fight.", 14,
        [{"label": "RESULT_SOUND", "value": "hit, blocked, whiff -> one SFX each"},
         {"label": "Never", "value": "changes health or state"}],
        [(0.05, 101, "listens to attack_resolved"), (0.3, 103, "one result, one sound"),
         (0.55, 106, "knockout: the K.O. sound"), (0.75, 108, "and the music loop stops")],
        ["godot/game/audio_director.gd", "connected in main.gd _ready()"]))

    beats.append(footage_beat("B12", "RESULT", "three_results",
        "Watch for three results: the whiff that opens the round, a block, and a clean hit. Each one fires "
        "exactly one sound. Next, you'll hear them, with no voice over the top.", 10,
        [{"at": "0.1", "event": "Akaken's opening jab misses: whiff"},
         {"at": "0.5", "event": "a strike meets a raised guard: block spark"},
         {"at": "0.8", "event": "a clean hit spark"}], LABEL_FOOT, evidence=True))

    w = WINDOWS["slice_audio"]
    beats.append({"beat_id": "B13", "act": "SLICE AUDIO", "narration_text": "",
        "role_note": "The slice's own audio, unnarrated: the isolated copy's Movie Maker recording carries the "
                     "game's mixed output (SFX + music) in the same AVI as the frames. This beat's audio_file is "
                     "that recording's audio for the same interval as its frames, unedited apart from a 20 ms "
                     "fade at each cut. Labelled on screen. See BUILD-LOG for why this route was used.",
        "estimated_duration_s": round(w["end"] - w["start"], 3),
        "actual_duration_s": round(w["end"] - w["start"], 3),
        "audio_file": "audio/B13-slice.wav",
        "shot": {"type": "VIDEO", "class": "SHOW", "source": "capture", "motion": "none", "capture": "run-01",
                 "capture_start_s": w["start"], "capture_end_s": w["end"],
                 "label": "SLICE AUDIO · the game's own sound, no narration · scripted input, native 4K capture",
                 "show": [{"at": "0.0", "event": "label: the slice's own audio, no narration"},
                          {"at": "0.3", "event": "hits, blocks and whiffs, each with its sound, over the loop"},
                          {"at": "0.85", "event": "K.O.: the K.O. sound, the music stops"}]}})

    beats.append(code_beat("B14", "tests/test_runner.gd", 349, 358, "One Attack, One Sound, Tested",
        "The tests check that wiring frame by frame, with no waiting. Before these lines the test throws "
        "a held punch, mashing, kicks and blocks; here, two whiffs, then it asserts one sound per resolved "
        "attack. Notice it places the dummy by hand. That proves the wiring, not that a player reaches "
        "those spacings, and not that the sounds are any good.", 20,
        [{"label": "Shortcut", "value": "dummy placed by hand"},
         {"label": "Cannot prove", "value": "that the sounds are good"}],
        [(0.05, 349, "E: two attacks far out of range"), (0.3, 351, "the dummy is placed by hand"),
         (0.55, 354, "expected sounds from the attack log"), (0.75, 358, "one sound per attack")],
        ["godot/tests/test_runner.gd", "test_one_sound_per_event"]))

    test_log = (REEL / "evidence" / "test-run.txt").read_text(encoding="utf-8").splitlines()
    sound_line = next(l.strip() for l in test_log if l.strip().startswith("attacks "))
    mute_line = next(l.strip() for l in test_log if l.strip().startswith("with sound"))
    total_line = next(l.strip() for l in test_log if "checks," in l)
    d15 = dur("B15", 20)
    beats.append(beat("B15", "RESULT",
        "The recorded run: ninety-four checks, none failed. Thirteen attacks, thirteen sound requests. "
        "With both buses muted, a seeded fight ends with the same health, positions and phase. And one check "
        "came from a bug: background removal erased Ow-tah-keh's knockout pose, so now any state image "
        "without a body fails.", 20,
        {"type": "GRAPHIC", "class": "SHOW", "source": "remotion", "motion": "cue-lines",
         "evidence_media": "media/B15.mp4",
         "show": [{"at": "0.05", "event": "test list and recorded output appear"},
                  {"at": "0.2", "event": "'94 checks, 0 failed' highlighted"},
                  {"at": "0.4", "event": "sound counts line highlighted"},
                  {"at": "0.6", "event": "muted run line highlighted"},
                  {"at": "0.8", "event": "every-state-has-art test highlighted"}],
         "remotion": {"pattern": "GodotDevWorkbench", "props": {
             "mode": "trace", "title": "The Recorded Test Run", "project": PROJECT,
             "source": f"Recorded output: godot --headless --path godot --script res://tests/test_runner.gd at {SOURCE_REV} (evidence/test-run.txt)",
             "treeLabel": "tests/test_runner.gd · 18 tests",
             "tree": ["test_every_state_has_art", "test_punch_hits_once", "test_every_attack_resolves_exactly_once",
                      "test_one_sound_per_event", "test_final_hit_sounds_hit_then_ko",
                      "test_music_follows_the_round", "test_mute_never_changes_the_fight"],
             "inspectorLabel": "Recorded output, verbatim",
             "notes": [{"label": "Result", "value": total_line}, {"label": "Sound test", "value": sound_line}],
             "cues": [{"at": round(0.2 * d15, 2), "line": 4, "label": total_line},
                      {"at": round(0.4 * d15, 2), "line": 4, "label": sound_line},
                      {"at": round(0.6 * d15, 2), "line": 7, "label": mute_line},
                      {"at": round(0.8 * d15, 2), "line": 1, "label": "every state image must show a body (>= 300 sampled px)"}],
             "output": ["exit code 0", "headless, stepped frame by frame"], "durationSeconds": round(d15 + 0.2, 2)}}},
        role_note="Result of B14: the actual recorded test output, shown verbatim (no invented lines)."))

    beats.append(beat("B16", "VERDICT",
        "Verdict. The models drew the pixels and made the sounds on a free T4: SDXL for the art, Stable "
        "Audio Open for the effects, MusicGen for the loop. Jow-hway chose the theme, the design and the "
        "switch to colour blocks, and played it. Claude wrote the code and prompts and made every pick "
        "after round three, by measurement. Tested: ninety-four checks at this revision, and the author's "
        "playtest. Not settled: whether the sounds are right by ear. Next step: give Ow-tah-keh his "
        "missing walk, jump and win poses from the same reference.", 30,
        {"type": "GRAPHIC", "class": "SHOW", "source": "remotion", "motion": "artifact-lines",
         "show": [{"at": "0.05", "event": "verdict page opens"}, {"at": "0.15", "event": "line 1: models"},
                  {"at": "0.3", "event": "line 2: Zhaohui"}, {"at": "0.48", "event": "line 3: Claude"},
                  {"at": "0.62", "event": "line 4: limits"}, {"at": "0.8", "event": "line 5: next step"}],
         "remotion": {"pattern": "ClaudeVerdictArtifact", "props": {
             "artifactTitle": "Verdict", "artifactHeading": "Dusk Duel asset slice", "brandLabel": "@NikBearBrown",
             "artifactLines": [
                 "Models: SDXL + ControlNet + IP-Adapter (art), Stable Audio Open (SFX), MusicGen (loop). Free Colab T4.",
                 "Zhaohui: theme, design, plan B, playtest. Claude: docs, code, prompts, picks after round 3.",
                 "Tested: 94 checks at 4e0cf14 + author playtest. Uncertain: sounds judged by measurement.",
                 "Limits: lighter top, blank face, 5 Aotake poses, non-commercial licences.",
                 "Next step: Aotake's walk, jump and win poses from the same reference."]}}}))

    beats.append(beat("B17", "HANDOFF",
        "Your turn. Paste this: Please use Walker to add one new state image to my Godot fighter. Write "
        "its pose and hitbox on the character sheet first, predict where the box should land, generate it "
        "from a colour block, then show it in-engine with collision boxes on, and add a test that fails if "
        "the image has no body. The order is the point: you judge the image against a prediction, not "
        "your hopes. If the box misses the limb, fix the sheet, not the picture. Liam, in for Bear.", 30,
        {"type": "GRAPHIC", "class": "SHOW", "source": "remotion", "motion": "type-on",
         "show": [{"at": "0.05", "event": "composer opens with greeting 'Your turn.'"},
                  {"at": "0.2", "event": "the prompt types in"}, {"at": "0.6", "event": "send button arms"},
                  {"at": "0.75", "event": "three RESULT lines land"}],
         "remotion": {"pattern": "ClaudeComposerAsk", "props": {
             "greeting": "Your turn.", "topic": "WALKER · YOUR FIGHTER", "segment": "Predict The Box",
             "command": "Please use Walker to add one new state image to my Godot fighter. Write its pose and "
                        "hitbox on the character sheet first, predict where the box should land, generate it "
                        "from a colour block, then show it in-engine with collision boxes on, and add a test "
                        "that fails if the image has no body.",
             "runningText": "paste this into Claude…", "folderLabel": "@NikBearBrown",
             "modelLabel": "Claude", "effortLabel": "High",
             "output": ["Pose and box written before generation.", "In-engine capture with boxes on.",
                        "Check: does the box land on the limb?"], "animateTyping": True}}}))

    beats.append(beat("B18", "OUTRO", f"{TITLE}. At Nik Bear Brown.", 5,
        {"type": "GRAPHIC", "class": "SHOW", "source": "remotion", "motion": "mascot-title",
         "show": [{"at": "0.0", "event": f"title '{TITLE}.' on cream"},
                  {"at": "0.3", "event": "@NikBearBrown beneath"},
                  {"at": "0.5", "event": "slug-seeded crisp-safe mascot under the handle"},
                  {"at": "0.85", "event": "1 s silent tail hold"}],
         "remotion": {"pattern": "ClaudeTitleOutro", "props": {"title": TITLE, "slug": SLUG}}},
        kind="outro_voice", tail_hold_s=1.0,
        role_note="OUTRO LOCK: exact title, hardcoded @NikBearBrown, slug-seeded mascot, no subline, spoken, "
                  "no jingle, no game audio."))

    for b in beats:
        # only for beats whose narration is unchanged (beat() kept their audio_file); a changed
        # line must be re-voiced before its old mp3 is trusted again
        if b["beat_id"] != "B13" and b.get("audio_file"):
            m = measured(b["beat_id"])
            if m:
                b["actual_duration_s"] = round(m, 2)
                b["audio_file"] = f"mp3/beat-{b['beat_id']}.mp3"
    sheet = {"metadata": {
        "title": TITLE, "slug": SLUG, "topic": "How a Godot slice's art and audio were designed, generated and wired in",
        "kind": "godot-gamedev", "mode": "walker", "brand": "claude-liam", "channel": "@NikBearBrown",
        "channel_title": "Nik Bear Brown", "folderLabel": "@NikBearBrown", "persona": "Liam", "presenter": "Liam",
        "in_for_bear": True, "greeting": "Hola, Liam",
        "greeting_note": "hello lexicon: Hola (Spanish); the author's earlier reel used Namaste. Hej was tried first and Kokoro read it as 'hedge'.",
        "tts_respelling": "Narration respells names for Kokoro (checked with Whisper): Jow-hway Lee = Zhaohui Li, Ah-kah-ken = Akaken, Ow-tah-keh = Aotake.",
        "audience": "practitioners and makers following the channel's Claude workflows",
        "register": "Teardown", "engine": "kokoro", "voice": "am_onyx", "voice_kokoro": "am_onyx",
        "palette": "claude", "aspect_ratio": "16:9", "fps": 30, "captions": False,
        "game": {"name": PROJECT, "author": "Zhaohui Li", "source_revision": SOURCE_REV,
                 "godot": "4.7.2.stable.official.ed1daf0bf", "project": "godot/project.godot",
                 "started_from": "an empty Godot 4.7 project (no starter code)"},
        "teaching_contract": "code-then-result-v1",
        "note": "Gameplay beats are real Movie Maker captures of an isolated copy driven by scripted keyboard "
                "input, labelled on screen. B13 carries the slice's own recorded audio with no narration."},
        "beats": beats}
    (REEL / "beat_sheet.json").write_text(json.dumps(sheet, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {len(beats)} beats; words: " +
          ", ".join(f"{b['beat_id']}:{len(b['narration_text'].split())}" for b in beats))


if __name__ == "__main__":
    build()
