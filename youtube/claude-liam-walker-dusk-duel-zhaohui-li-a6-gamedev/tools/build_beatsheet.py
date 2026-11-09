#!/usr/bin/env python3
"""Write beat_sheet.json for the A6 gamedev film ("Dusk Duel, Sparked").

Adapted from the A5 reel's builder. Code excerpts are read from the hashed source files at the line
ranges below, so the text on screen is the file's text byte for byte. Cue times are fractions of
each beat's measured narration once mp3/beat-Bxx.mp3 exists (audio is the clock), estimates before
that. Footage windows are seconds into capture/a6_play.avi (tools/capture_a6.gd, scripted input;
event times in capture/a6_play.log: Enter 1.50 s, fight 2.50 s, hits every 0.5 s from 4.17 s,
pause 5.72-8.72 s, K.O. 13.20 s, result 14.72 s, rematch 16.55 s, round 2 fight 17.55 s, end 21.55 s).
"""
import base64
import json
import pathlib
import subprocess

REEL = pathlib.Path(__file__).resolve().parent.parent
REPO = REEL.parent.parent
GAME = REPO / "godot"
SLUG = REEL.name
TITLE = "Dusk Duel, Sparked"
SOURCE_REV = "840bcfd"            # last commit touching godot/ when the film was built
PROJECT = "walker-dusk-duel"
FIG = REEL / "figures"
OLD = json.loads((REEL / "beat_sheet.json").read_text(encoding="utf-8")) if (REEL / "beat_sheet.json").exists() else None
LABEL_PLAY = "SCRIPTED-INPUT CAPTURE · Godot 4.7.2 · copy of 840bcfd · keys sent by script · Aotake scripted"
HANDLE = "@NikBearBrown"


def measured(bid):
    p = REEL / "mp3" / f"beat-{bid}.mp3"
    if p.is_file():
        out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                              "-of", "default=nw=1:nk=1", str(p)], capture_output=True, text=True)
        return float(out.stdout.strip())
    return None


def dur(bid, est):
    return measured(bid) or est


def excerpt(rel, start, end):
    lines = (GAME / rel).read_text(encoding="utf-8").splitlines()
    return "\n".join(lines[start - 1:end])


def data_uri(path):
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode()


# Kokoro respellings (checked with faster-whisper after generation); on-screen text keeps the real names
RESPELL = {"Akaken": "Ah-kah-ken", "Aotake": "Ah-oh-tah-keh", "preprocess": "pree-process"}


def respell(text):
    for word, say in RESPELL.items():
        text = text.replace(word, say)
    return text


def beat(bid, act, narration, est, shot, **extra):
    narration = respell(narration)
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


def code_beat(bid, rel, start, end, title, narration, est, notes, cue_fracs, output, author):
    d = dur(bid, est)
    code = excerpt(rel, start, end)
    cues = [{"at": round(f * d, 2), "line": line, "label": label} for f, line, label in cue_fracs]
    shot = {"type": "GRAPHIC", "class": "SHOW", "source": "remotion", "motion": "line-highlight",
            "show": [{"at": f"{f:.2f}", "event": f"line {line} highlights: {label}"} for f, line, label in cue_fracs],
            "remotion": {"pattern": "GodotDevWorkbench", "props": {
                "mode": "code", "title": title, "project": PROJECT, "path": f"res://{rel}",
                "source": f"Godot editor reconstruction · godot/{rel} lines {start}-{end} · source {SOURCE_REV} · {author}",
                "code": code, "startLine": start, "codeFontSize": 23,
                "inspectorLabel": "Source notes — not Inspector values",
                "notes": notes, "cues": cues, "output": output, "durationSeconds": round(d + 0.2, 2)}}}
    return beat(bid, "MECHANISM", narration, est, shot, excerpt={"path": rel, "start_line": start, "end_line": end})


def figure_beat(bid, act, image, title, status, label, cards, cue_fracs, narration, est, source, show,
                evidence=False, still=False, **extra):
    d = dur(bid, est)
    shot = {"type": "STILL" if still else "GRAPHIC", "class": "SHOW", "source": "remotion",
            "motion": "card-cues", "show": show,
            "remotion": {"pattern": "GodotDesignFigure", "props": {
                "title": title, "status": status, "image": data_uri(FIG / image), "imageLabel": label,
                "source": source, "cards": cards,
                "cues": [{"at": round(f * d, 2), "card": c} for f, c in cue_fracs],
                "durationSeconds": round(d + 0.2, 2)}},
            "figure": f"figures/{image}"}
    if evidence:
        shot["evidence_media"] = f"media/{bid}.mp4"
    return beat(bid, act, narration, est, shot, **extra)


def footage_beat(bid, act, start, narration, est, show, evidence=False, crop=None, **extra):
    shot = {"type": "VIDEO", "class": "SHOW", "source": "capture", "motion": "none", "capture": "a6_play",
            "capture_file": "capture/a6_play.avi", "capture_start_s": start, "label": LABEL_PLAY, "show": show}
    if crop:
        shot["crop"] = crop
        shot["label"] = LABEL_PLAY + " · cropped 1.5×"
    if evidence:
        shot["evidence_media"] = f"media/{bid}.mp4"
    return beat(bid, act, narration, est, shot, **extra)


def cards4(*pairs):
    return [{"label": a, "text": b} for a, b in pairs]


def show4(first, labels):
    return [{"at": "0.05", "event": f"{first}; {labels[0]} card lights"}] + \
           [{"at": f"{t:.2f}", "event": f"{lab} card lights"} for t, lab in zip((0.3, 0.55, 0.8), labels[1:])]


def build():
    beats = []
    beats.append(beat("B00", "ASK",
        "Ciao, this is Liam, in for Bear. Jow-hway Lee's Dusk Duel is a 2D fighting game. Assignment six adds two "
        "particle effects: a hit spark where a punch lands, and faint embers drifting through the courtyard while "
        "the fight runs. Jow-hway wrote the brief, every setting and every prediction. Claude Code and its agents "
        "built the scenes, the controllers and the tests.", 22,
        {"type": "GRAPHIC", "class": "SHOW", "source": "remotion", "motion": "type-on",
         "show": [{"at": "0.02", "event": "composer card fades in on the cream page"},
                  {"at": "0.12", "event": "greeting 'Ciao, Liam' appears above the composer"},
                  {"at": "0.3", "event": "the reconstructed Walker ask types in"},
                  {"at": "0.66", "event": "send button arms terracotta"},
                  {"at": "0.78", "event": "three RESULT lines land beneath the card"}],
         "remotion": {"pattern": "ClaudeComposerAsk", "props": {
             "greeting": "Ciao, Liam", "topic": "WALKER · PARTICLE EFFECTS", "segment": TITLE,
             "command": "Please use Walker to convert my game design document about Dusk Duel into two particle "
                        "effects: a hit spark on every clean hit, and courtyard embers while the fight runs. I write "
                        "the brief, the settings and the predictions; you build the scenes, controllers and tests.",
             "runningText": "reconstructed ask · built step by step over one day of sessions",
             "folderLabel": HANDLE, "modelLabel": "Claude", "effortLabel": "High",
             "output": ["Config tests: 69 / 0 and 85 / 0.",
                        "State tests, real loop and input: 57 / 0 and 38 / 0.",
                        "Both effects far under their CPU and GPU budgets."]}}},
        role_note="COLD OPEN LAW, walker B00. The Walker prompt is an ILLUSTRATIVE RECONSTRUCTION: the A6 work was "
                  "done in many steps and claude -p sessions (prompts/a6/), not one Walker run. RESULT lines are "
                  "real outcomes (TEST-REPORT A6)."))

    beats.append(beat("B01", "BLUF",
        "Two particle effects, from a hand-written brief. The headless tests prove they fire when they should, "
        "freeze when they should, and cost almost nothing. Not how they look. That took frame strips, and eyes.", 11,
        {"type": "GRAPHIC", "class": "SHOW", "source": "remotion", "motion": "type-on-correct",
         "show": [{"at": "0.0", "event": "cream page; typing begins during the lead silence"},
                  {"at": "0.2", "event": "'The tests prove they look right.' types, then pauses"},
                  {"at": "0.45", "event": "'look' struck through in terracotta"},
                  {"at": "0.6", "event": "'fire' types in its place"},
                  {"at": "0.85", "event": "corrected overview settles before the cut"}],
         "remotion": {"pattern": "BrutalistHesitantWriter", "props": {
             "contextTitle": "BLUF",
             "text": "Two particle effects, from a hand-written brief.\nThe tests prove they look right.\nOnly strips and eyes judged the picture.",
             "triggerWords": "look", "replacementWords": "fire",
             "fontSize": 76, "lineSpacing": 2.4, "align": "center", "seed": "7270-a6",
             "mistakeRate": 0, "hesitateWithin": 0, "hesitateBetween": 0, "charMs": 8,
             "ink": "#3D3929", "accent": "#D97757", "bg": "#FAF9F5", "brandLabel": HANDLE}}},
        lead_silence_s=0.8,
        role_note="EXECUTIVE-SUMMARY LAW. The corrected misconception: a passing headless run proves firing, "
                  "freezing and price, not the look. 'look' appears once."))

    beats.append(footage_beat("B02", "OPEN", 0.6,
        "Here's the game, an engine capture with scripted input. On the title screen, no embers. Enter starts the "
        "round, and the moment the fight begins, a thin field of embers is already there. Every punch that lands "
        "throws a burst of cyan particles around the white star, which is the old code-drawn spark the game "
        "already had.", 12,
        [{"at": "0.05", "event": "title screen, no embers"},
         {"at": "0.15", "event": "Enter: ROUND 1 - FIGHT intro"},
         {"at": "0.3", "event": "fight begins; ember field present at once (faint)"},
         {"at": "0.55", "event": "Akaken's punches land; cyan particles around effects.gd's white star at each contact point"}],
        role_note="Real Movie Maker capture of an isolated copy (capture/game, 840bcfd). Scripted input: Enter, D, J "
                  "and Esc sent by tools/capture_a6.gd; Aotake on the game's ScriptedController. Labelled."))

    beats.append(figure_beat("B03", "DESIGN", "fig_intent_a.png", "Effect A: The Hit Spark",
        "DESIGN · CHANGE-BRIEF.md A6, Effect A, committed efa8d71 before any build", "bg.png hit band, enlarged 3×",
        cards4(("Event", "attack_resolved, hit"), ("Timing", "flash, 0.2 s, 0.6 s"), ("Contrast", "13.1 : 1 · 3.0 : 1"),
               ("Pool", "4 slots × 20")),
        [(0.05, 0), (0.35, 1), (0.6, 2), (0.85, 3)],
        "Effect A, the hit spark. Its job, in Jow-hway's brief: confirm that an attack connected, at the exact "
        "contact point. The event is attack resolved, with result hit, at the overlap of hitbox and hurtbox. The "
        "intent: a compact flash, sparks outward for a fifth of a second, faded by point six. Cool white against a "
        "dark band, still three to one beside the brightest lantern. Four pooled slots of twenty.", 24,
        "Source: CHANGE-BRIEF.md (A6), Effect A: The job, The intent block; background table; godot/art/env/bg.png",
        show4("brief excerpt beside the real hit band", ["Event", "Timing", "Contrast", "Pool"]), still=True))

    beats.append(figure_beat("B04", "STRIP", "fig_strip_a_r0.png", "The First Strip",
        "OBSERVED · captures/hit_spark/r0 and r0-lantern · fixture capture", "frames 10–50, dark wall and lantern",
        cards4(("Fixture", "preview, fixed seed"), ("Fires", "frames 10 and 22"), ("First look", "Zhaohui's words"),
               ("Corrected", "5 s → 0.6 s")),
        [(0.05, 0), (0.3, 1), (0.55, 2), (0.82, 3)],
        "The first frame strip is a fixture capture: a preview scene with a fixed seed, firing at frame ten and "
        "again at twenty-two. Jow-hway's first look: much smaller than the character, bright, easy to see, lasting "
        "about five seconds. Claude noted the lifetime is point six seconds. Jow-hway corrected it to point six, "
        "and the original line stays in the record.", 22,
        "Source: captures/hit_spark/r0/, r0-lantern/ (Movie Maker, 30 fps); TUNING.md Effect A r0",
        show4("both r0 strips and the first look", ["Fixture", "Fires", "First look", "Corrected"]), still=True))

    beats.append(figure_beat("B05", "PREDICT", "fig_revise_a.png", "It Reads As A Ring",
        "PREDICT · TUNING.md Effect A r1 · Claude's reading and prediction", "r0 frames 12 and 15, enlarged",
        cards4(("Reading", "a hollow ring"), ("Not independent", "Claude's option"), ("Change", "min 45 → 15"),
               ("Prediction", "filled, same edge")),
        [(0.05, 0), (0.35, 1), (0.6, 2), (0.82, 3)],
        "Claude's reading of that strip, which is a claim, not a verdict: at frames twelve to fifteen the sparks sit on one "
        "ring with an empty middle, because they all leave at nearly the same speed. Jow-hway picked: it reads as a "
        "ring, from Claude's options, so this revision depends on that reading. One change: minimum speed, "
        "forty-five down to fifteen. Claude predicted a filled cluster, with the same outer edge.", 24,
        "Source: TUNING.md, Effect A r1 (reading, change, prediction); commit 1a1e60e",
        show4("the ring, the change, the prediction", ["Reading", "Not independent", "Change", "Prediction"]), still=True))

    beats.append(code_beat("B06", "effects/hit_spark.tscn", 17, 30, "Emission, Process, Draw",
        "Here is the whole effect as a scene file, and the three parts of any particle system. Emission: line "
        "nineteen, twenty particles; line twenty-two, one shot; line twenty-five, all at once, from a point. "
        "Process, how each particle moves: line twenty-eight spreads them all ways, line twenty-nine adds gravity, "
        "line thirty is the revised minimum speed. Draw: line twenty, the star texture, and line seventeen, the "
        "additive material.", 26,
        [{"label": "Emission", "value": "amount, one_shot, explosiveness, point"},
         {"label": "Process", "value": "spread, gravity, speed, damping, ramp"},
         {"label": "Draw", "value": "star texture, additive blend"}],
        [(0.1, 19, "emission: 20 particles"), (0.18, 22, "emission: one burst"), (0.26, 25, "emission: all at once"),
         (0.45, 28, "process: spread 180°"), (0.55, 29, "process: gravity"), (0.64, 30, "process: min speed, revised"),
         (0.8, 20, "draw: star texture"), (0.9, 17, "draw: additive material")],
        ["godot/effects/hit_spark.tscn", "built by an agent (0ac83ee), values from Zhaohui's brief"],
        "settings from Zhaohui's brief; scene by a Claude Code agent"))

    beats.append(figure_beat("B07", "RESULT", "fig_r1_a.png", "Ring Gone, Edge Smaller",
        "OBSERVED · captures/hit_spark/r0 vs r1 · fixture capture, same seed", "before and after, dark wall",
        cards4(("Matched", "filled cluster"), ("Wrong", "58 → 48 px"), ("Why", "min slows all"), ("Verdict", "Keep")),
        [(0.05, 0), (0.3, 1), (0.55, 2), (0.82, 3)],
        "And this is what those lines draw, before and after. The ring is gone: frames twelve and fifteen are a "
        "filled cluster. But Claude's prediction about the edge was wrong. The burst shrank, from fifty-eight "
        "pixels across to forty-eight, because each spark's speed is drawn between the minimum and the maximum, so "
        "lowering the minimum slows nearly all of them. Still inside the brief. Jow-hway's verdict: yes, I saw the ring. Keep.", 24,
        "Source: captures/hit_spark/r0/, r1/; TUNING.md Effect A r1; CHANGE-BRIEF.md Revision 3",
        show4("r0 and r1 strips with the comparison", ["Matched", "Wrong", "Why", "Verdict"]), evidence=True, still=True))

    beats.append(code_beat("B08", "effects/hit_spark_pool.gd", 43, 56, "Four Slots, Never Restarted",
        "In the game, a pool script starts a spark on every hit. Line forty-three takes the first slot that isn't "
        "still emitting, so a second hit never restarts a live burst; if all four are busy, line forty-five takes "
        "the oldest. Line forty-seven puts it at the contact point. Line fifty-six freezes all four during pause "
        "and hitstop, because neither pauses the scene tree.", 20,
        [{"label": "Rule 3", "value": "overlap: a free slot"},
         {"label": "Rule 2", "value": "at the contact point"},
         {"label": "Rule 5", "value": "speed_scale 0 when paused"}],
        [(0.15, 43, "take a slot that is not emitting"), (0.42, 45, "all four busy: the oldest"),
         (0.6, 47, "at the contact point"), (0.8, 56, "frozen in pause and hitstop")],
        ["godot/effects/hit_spark_pool.gd", "agent (607f5d1); slot fix by Claude Code (e96c916)"],
        "agent, slot fix by Claude Code"))

    beats.append(footage_beat("B09", "RESULT", 5.4,
        "Pause, mid-burst: the sparks hang in the air until the game resumes. Then hits land every half second, "
        "faster than a burst's lifetime, so two bursts overlap instead of one cutting the other short.", 11,
        [{"at": "0.03", "event": "a punch lands; Esc: PAUSED; the live sparks stop where they are for 3 s"},
         {"at": "0.3", "event": "resume; the frozen sparks finish their fade"},
         {"at": "0.5", "event": "punches land every 0.5 s; two bursts alive at once"}], evidence=True,
        role_note="Same scripted-input capture as B02, later window (pause at 5.72-8.72 s), reused with disclosure; "
                  "cropped to the contact area (4K source x 1500-3520, y 620-1756, scaled 1.52x), labelled.",
        crop=[1500, 620, 2020, 1136]))

    beats.append(figure_beat("B10", "DESIGN", "fig_intent_b.png", "Effect B: Courtyard Embers",
        "DESIGN · CHANGE-BRIEF.md A6, Effect B", "bg.png at 3×, emission rect drawn from embers.tscn",
        cards4(("Job", "ambience"), ("Condition", "phase == fight"), ("Rect", "560 × 180 px"), ("Preprocess", "1.5 s")),
        [(0.05, 0), (0.3, 1), (0.55, 2), (0.8, 3)],
        "Effect B, courtyard embers. Its job is ambience: air and warmth, never competing with the fighters. The "
        "condition: run only while the phase is fight. And it uses two things the hit spark doesn't: a rectangular "
        "emission area, five hundred sixty by one eighty pixels over the arena, and a preprocess of one and a half "
        "seconds, so the field already exists when it starts.", 22,
        "Source: CHANGE-BRIEF.md (A6), Effect B: The job, The intent block, The settings",
        show4("brief excerpt beside the emission rect", ["Job", "Condition", "Rect", "Preprocess"]), still=True))

    beats.append(figure_beat("B11", "STRIP", "fig_strip_b_r0.png", "Too Faint",
        "OBSERVED · captures/embers/r0 · fixture capture", "frames 10–175; frame 55 enlarged; diagnostic panel",
        cards4(("Condition", "on 10, off 100"), ("First look", "multiple choice"), ("Count", "~200 px"),
               ("Preprocess", "runs on emitting")),
        [(0.05, 0), (0.3, 1), (0.55, 2), (0.8, 3)],
        "The first strip turns the condition on at frame ten and off at a hundred. Jow-hway's first look came as "
        "three multiple-choice answers to Claude's questions: already filled, too faint, faded out slowly. Claude's "
        "count agreed: about two hundred changed pixels out of nine hundred thousand. And frame ten was already "
        "populated, so preprocess runs when emitting turns on.", 22,
        "Source: captures/embers/r0/, r0-restart/; TUNING.md Effect B r0",
        show4("the r0 strip and the first look", ["Condition", "First look", "Count", "Preprocess"]), still=True))

    beats.append(code_beat("B12", "effects/embers.tscn", 21, 34, "Rectangle And Preprocess",
        "Here is that scene. Line twenty-nine, the preprocess. Line thirty-three, emission shape three, the "
        "rectangle, and line thirty-four, its half extents. Line twenty-seven, a two-and-a-half second lifetime, "
        "which is how long the field takes to clear after it stops. The tuning change lives just above this view, "
        "in the colour ramp's alpha on line eighteen.", 20,
        [{"label": "Line 29", "value": "preprocess 1.5"},
         {"label": "Lines 33-34", "value": "rectangle, extents (280, 90)"},
         {"label": "Line 18", "value": "ramp alpha 0.70 / 0.50 (r1)"}],
        [(0.08, 29, "preprocess: an established field"), (0.25, 33, "emission shape 3: rectangle"),
         (0.38, 34, "half extents: 560 x 180 px"), (0.55, 27, "lifetime 2.5 s")],
        ["godot/effects/embers.tscn", "agent (220b5a8); alpha r1 by Claude Code, approved by Zhaohui (6f0c304)"],
        "settings from Zhaohui's brief; scene by a Claude Code agent"))

    beats.append(figure_beat("B13", "RESULT", "fig_r1_b.png", "About Right",
        "OBSERVED · captures/embers/r0 vs r1 · fixture capture, same seed", "frame 55 enlarged; diagnostic below",
        cards4(("Change", "alpha up"), ("Predicted", "400–600 px"), ("Measured", "447 at frame 10"), ("Verdict", "kept")),
        [(0.05, 0), (0.3, 1), (0.52, 2), (0.82, 3)],
        "The revision raised the ramp's alpha from point two eight to point seven, and point two to point five. "
        "Claude predicted four to six hundred changed pixels at frame ten; the strip gave four hundred forty-seven, "
        "and a little above the prediction later on. Still one to three pixels per ember, still far dimmer than "
        "the spark. Jow-hway's verdict: recorded, I feel it's about right. Kept.", 22,
        "Source: captures/embers/r0/, r1/; TUNING.md Effect B r1; CHANGE-BRIEF.md Revision 2",
        show4("r0 and r1 with counts and the verdict", ["Change", "Predicted", "Measured", "Verdict"]),
        evidence=True, still=True))

    beats.append(code_beat("B14", "effects/embers_controller.gd", 20, 33, "Start And Stop",
        "Embers are started and stopped by a small controller that polls the phase every physics tick. Line "
        "twenty-eight: entering the fight calls restart, so preprocess runs again every round. Line thirty: "
        "leaving the fight stops emitting, and live embers finish their lifetime. Like the pool, it also sets "
        "speed scale to zero during pause and hitstop.", 18,
        [{"label": "Rule 1", "value": "start on fight, stop after"},
         {"label": "Rule 5", "value": "restart: preprocess each round"},
         {"label": "Rule 2", "value": "speed_scale 0 when paused (line 37)"}],
        [(0.1, 21, "poll the phase"), (0.3, 28, "enter fight: restart"), (0.6, 30, "leave fight: stop emitting"),
         (0.85, 32, "then apply speed_scale")],
        ["godot/effects/embers_controller.gd", "agent (6b55ff8), under Zhaohui's delegation"],
        "agent, approved by Claude Code under Zhaohui's delegation"))

    beats.append(footage_beat("B15", "RESULT", 12.7,
        "Here's the K.O. Emission stops, and the last embers fade out. Then the rematch, and the field is back at "
        "once.", 7,
        [{"at": "0.1", "event": "final punch; K.O.; emission stops"},
         {"at": "0.4", "event": "the remaining embers fade; result screen"},
         {"at": "0.75", "event": "Enter: round 2; the field is present again when the fight starts"}], evidence=True,
        role_note="Same scripted-input capture as B02, window near the end (K.O. at 13.20 s, round 2 fight at 17.55 s)."))

    beats.append(figure_beat("B16", "STATES", "fig_states_b.png", "Three Ways To Stop Time",
        "HEADLESS · tests/test_embers_state.gd · CHANGE-BRIEF Revision 4", "recorded output, indirect",
        cards4(("Pause", "speed_scale 0"), ("Tree pause", "node stops"), ("Hidden", "freezes"), ("Revised", "option 1")),
        [(0.05, 0), (0.25, 1), (0.45, 2), (0.75, 3)],
        "Three ways to stop time, and they're different. The game's pause and hitstop: speed scale zero, frozen on "
        "every tick. Pausing the scene tree: the node stops by itself. Hidden: the brief said particles keep "
        "ageing, but the test found they freeze, and never finish while hidden. Jow-hway chose option one: revise "
        "the rule to what Godot actually does. The evidence is indirect: node flags over time.", 24,
        "Source: TEST-REPORT.md A6 (state tests, open finding); CHANGE-BRIEF.md Revision 4; logs/test_embers_state_60fps.log",
        show4("three states and the hidden finding", ["Pause", "Tree pause", "Hidden", "Revised"])))

    beats.append(figure_beat("B17", "SHADER", "fig_shader.png", "The Generated Process Shader",
        "SOURCE · godot/shaders/particles_generated.gdshader beside the brief", "lines verbatim",
        cards4(("Line 137", "min/max speed"), ("Line 260", "spread"), ("307 / 320", "gravity"), ("Dropped", "ramp, curve")),
        [(0.08, 0), (0.42, 1), (0.58, 2), (0.8, 3)],
        "Now the process step as a GPU shader. Jow-hway converted the hit spark to a GPU node in the editor and "
        "saved the shader Godot generated. Line one thirty-seven mixes the minimum and maximum speed per particle: "
        "the brief's fifteen to seventy-five. Line two sixty sends it in a random direction inside the spread. "
        "Lines three oh seven and three twenty turn gravity into velocity. And a finding: the conversion dropped "
        "the colour ramp and the scale curve. Every particle gets one constant colour.", 28,
        "Source: godot/shaders/particles_generated.gdshader:137, 260, 307, 320, 348, 147; TEST-REPORT.md A6",
        show4("four lines beside four brief settings", ["Line 137", "Line 260", "307 / 320", "Dropped"])))

    beats.append(figure_beat("B18", "TESTS", "fig_tests.png", "What The Tests Proved",
        "HEADLESS · recorded output · logs/*_60fps.log", "suite results and both mutations",
        cards4(("Config", "69 / 0 · 85 / 0"), ("State", "57 / 0 · 38 / 0"), ("Godot 3 name", "silent, exit 1"),
               ("Drift", "exit 1")),
        [(0.05, 0), (0.3, 1), (0.6, 2), (0.88, 3)],
        "What did the tests prove? The config tests read every setting back from the scene files: sixty-nine and "
        "eighty-five checks, none failed. The state tests drive the real loop with real input: a burst for each of "
        "sixteen hits, none for thirty-one blocks and whiffs, frozen in pause and hitstop. Then Jow-hway broke the "
        "scene twice. A Godot three property name loads with no error at all, and the sparks just got slower. Only "
        "the read-back caught it, and a drifted amount too.", 28,
        "Source: TEST-REPORT.md A6; logs/test_hit_spark_*, test_embers_*, mutation_a6_1_*, mutation_a6_2_*",
        show4("suites and mutations", ["Config", "State", "Godot 3 name", "Drift"])))

    beats.append(figure_beat("B19", "PRICE", "fig_price.png", "Both Prices, Under Budget",
        "MEASURED · cost_effects.gd (headless CPU) · gpu_price.gd (windowed GPU, Claude Code)", "medians per frame",
        cards4(("CPU", "0.010 · 0.006 ms"), ("Headless GPU", "≈ 0: no shader runs"), ("Profiler", "read 0"),
               ("GPU", "+0.012 · +0.004 ms")),
        [(0.05, 0), (0.33, 1), (0.6, 2), (0.82, 3)],
        "And the price. Measured headless on the CPU, medians: the spark costs about a hundredth of a millisecond "
        "per frame, the embers six thousandths, against budgets of a quarter and a half. A GPU particle effect "
        "would read near zero headless, because its process is a shader and the dummy renderer runs none. These "
        "are CPU nodes, but the GPU still draws them, so GPU time counts too. The Visual Profiler read zero here, "
        "so Claude Code measured GPU render time in a window instead: plus twelve and plus four thousandths. Far "
        "under budget.", 30,
        "Source: TEST-REPORT.md A6 (Headless CPU price, GPU price); CHANGE-BRIEF.md short answer 4; logs/cost_effects_60fps.log, gpu_price_windowed.log",
        show4("the price table and the two notes", ["CPU", "Headless GPU", "Profiler", "GPU"])))

    beats.append(figure_beat("B20", "HUMAN CHECK", "fig_limits.png", "What No Headless Run Shows",
        "HEADLESS vs HUMAN · TEST-REPORT.md A6", "Zhaohui's report, verbatim",
        cards4(("Proves", "fires, freezes, costs"), ("Cannot", "how it looks"), ("In play", "one sentence"),
               ("Never reached", "4-busy fallback")),
        [(0.05, 0), (0.25, 1), (0.5, 2), (0.85, 3)],
        "What no headless run can show is what a particle looks like: whether it reads on the lantern glow, or "
        "whether the embers are too faint. That's the strips and Jow-hway's eyes. Jow-hway's whole in-play report: "
        "when I ran the game, everything was normal, no problems. Recorded as given; it doesn't name rapid repeats "
        "or the lantern one by one. And the pool's all-four-busy fallback was never reached in a test.", 24,
        "Source: TEST-REPORT.md A6 (In play, HUMAN CHECK); README.md A6 known limitations",
        show4("proves and cannot, and the in-play report", ["Proves", "Cannot", "In play", "Never reached"])))

    beats.append(figure_beat("B21", "MISTAKES", "fig_mistakes.png", "Mistakes The Checks Caught",
        "RECORD · FRICTIONAL.md A6, TEST-REPORT.md A6, TUNING.md", "Claude Code's factual log",
        cards4(("Cost", "measured itself"), ("Wrapper", "log deleted"), ("Pool", "late finished"), ("Claude", "edge wrong")),
        [(0.05, 0), (0.25, 1), (0.55, 2), (0.85, 3)],
        "The agents made mistakes, and the checks caught them. The first cost script measured itself, until an "
        "empty-scene control showed every case reading the same. An agent ran the texture generator through the "
        "test wrapper, then deleted that log. Its star-shape check failed its own texture. The pool trusted a late "
        "finished signal after a round reset. And several commands were denied. And Claude read one strip wrong: it "
        "predicted the spark's edge would stay put.", 26,
        "Source: FRICTIONAL.md A6 (steps 2, 3/5, 7, tuning); TEST-REPORT.md A6; TUNING.md Effect A r1",
        show4("seven caught mistakes", ["Cost", "Wrapper", "Pool", "Claude"])))

    beats.append(beat("B22", "VERDICT",
        "Verdict. Checked: every setting read back, one spark per hit, embers only during the fight, both frozen in "
        "pause, two mutations that fail, and both prices far under budget. Uncertain: hidden embers freeze only by "
        "indirect evidence, the round reset needs test setup, the GPU price isn't from the profiler, and the spark "
        "still has no impact direction. Jow-hway wrote the brief, the predictions and the verdicts, ran every "
        "capture and made the mutations. Claude Code built the scenes, controllers and tests and read the strips, "
        "and approved the later agent steps after Jow-hway said: do the rest yourself. Both textures are drawn by "
        "code. Next step: give the spark a direction.", 42,
        {"type": "GRAPHIC", "class": "SHOW", "source": "remotion", "motion": "artifact-lines",
         "show": [{"at": "0.05", "event": "verdict page opens"}, {"at": "0.1", "event": "line 1: checked"},
                  {"at": "0.3", "event": "line 2: uncertain"}, {"at": "0.5", "event": "line 3: who did what"},
                  {"at": "0.75", "event": "line 4: delegation"}, {"at": "0.88", "event": "line 5: textures, source, next step"}],
         "remotion": {"pattern": "ClaudeVerdictArtifact", "props": {
             "artifactTitle": "Verdict", "artifactHeading": "Two effects, measured", "brandLabel": HANDLE,
             "artifactLines": [
                 "Checked: 69/0, 85/0, 57/0, 38/0; 2 mutations exit 1; CPU 0.010 / 0.006 ms, GPU +0.012 / +0.004 ms.",
                 "Uncertain: hidden freeze (indirect); rule 6 by SETUP; GPU not from the profiler; no impact direction.",
                 "Zhaohui: brief, settings, predictions, first looks, verdicts, captures, mutations, process shader.",
                 "Claude Code: scenes, controllers, tests, strip readings; later agent steps approved under delegation.",
                 f"Textures: make_textures.gd (code). Source shown: {SOURCE_REV} (godot/). Next: a spark with direction."]}}}))

    beats.append(beat("B23", "HANDOFF",
        "Your turn. Paste this: Please use Walker to add one particle effect to my game's brief before anything is "
        "built: its job, the event or condition that drives it, every setting, and a frame strip with what each "
        "frame should show. Then predict one change and its strip before you capture it. A prediction you can be "
        "wrong about is the only kind that teaches you anything. This was Liam, in for Bear.", 26,
        {"type": "GRAPHIC", "class": "SHOW", "source": "remotion", "motion": "type-on",
         "show": [{"at": "0.05", "event": "composer opens with greeting 'Your turn.'"},
                  {"at": "0.2", "event": "the prompt types in"}, {"at": "0.6", "event": "send button arms"},
                  {"at": "0.75", "event": "three RESULT lines land"}],
         "remotion": {"pattern": "ClaudeComposerAsk", "props": {
             "greeting": "Your turn.", "topic": "WALKER · YOUR EFFECT", "segment": "Predict The Strip",
             "command": "Please use Walker to add one particle effect to my game's brief before anything is built: "
                        "its job, the event or condition that drives it, every setting, and a frame strip with what "
                        "each frame should show. Then predict one change and its strip before you capture it.",
             "runningText": "paste this into Claude…", "folderLabel": HANDLE,
             "modelLabel": "Claude", "effortLabel": "High",
             "output": ["Brief committed before the build.", "Strip read against the prediction.",
                        "One change, one verdict."], "animateTyping": True}}}))

    beats.append(beat("B24", "OUTRO", f"{TITLE}. At Nik Bear Brown.", 5,
        {"type": "GRAPHIC", "class": "SHOW", "source": "remotion", "motion": "mascot-title",
         "show": [{"at": "0.0", "event": f"title '{TITLE}.' on cream"},
                  {"at": "0.3", "event": "@NikBearBrown beneath"},
                  {"at": "0.5", "event": "slug-seeded crisp-safe mascot under the handle"},
                  {"at": "0.85", "event": "1 s silent tail hold"}],
         "remotion": {"pattern": "ClaudeTitleOutro", "props": {"title": TITLE, "slug": SLUG}}},
        kind="outro_voice", tail_hold_s=1.0,
        role_note="OUTRO LOCK: exact title, hardcoded @NikBearBrown, slug-seeded mascot, no subline, spoken, "
                  "no jingle, no game audio."))

    # B15's window must end inside the capture (21.55 s): slide it earlier if the measured line is long
    for b in beats:
        if b["beat_id"] == "B15":
            d15 = dur("B15", 7)
            b["shot"]["capture_start_s"] = round(min(12.7, 21.45 - d15), 2)

    for b in beats:
        if b.get("audio_file"):
            m = measured(b["beat_id"])
            if m:
                b["actual_duration_s"] = round(m, 2)
                b["audio_file"] = f"mp3/beat-{b['beat_id']}.mp3"
    sheet = {"metadata": {
        "title": TITLE, "slug": SLUG,
        "topic": "Two CPU particle effects in a Godot fighting game: briefed by hand, built by agents, tuned by strips",
        "kind": "godot-gamedev", "mode": "walker", "brand": "claude-liam", "channel": HANDLE,
        "channel_title": "Nik Bear Brown", "folderLabel": HANDLE, "persona": "Liam", "presenter": "Liam",
        "in_for_bear": True, "greeting": "Ciao, Liam",
        "greeting_note": "hello lexicon: Ciao (Italian), as in the author's A3 and A5 reels.",
        "tts_respelling": "Narration respells Zhaohui Li as Jow-hway Lee for Kokoro (checked with faster-whisper "
                          "base.en). On-screen text always uses the real spellings.",
        "audience": "practitioners and makers following the channel's Claude workflows",
        "register": "Teardown", "engine": "kokoro", "voice": "am_onyx", "voice_kokoro": "am_onyx",
        "palette": "claude", "aspect_ratio": "16:9", "fps": 30, "captions": False,
        "game": {"name": PROJECT, "author": "Zhaohui Li", "source_revision": SOURCE_REV,
                 "godot": "4.7.2.stable.official.ed1daf0bf", "project": "godot/project.godot",
                 "renderer": "gl_compatibility",
                 "started_from": "the A2 2D game (A5 shaders unchanged); A6 adds godot/effects/, godot/previews/, "
                                 "the A6 tests and price scripts, and the generated process shader"},
        "teaching_contract": "code-then-result-v1",
        "note": "Engine footage is a real Movie Maker capture of an isolated copy with scripted input (labelled). "
                "Strip figures are the committed fixture captures in captures/ (preview scenes, fixed seed); labels, "
                "frames, rings, the drawn emission rect and one labelled diagnostic panel are the only new pixels."},
        "beats": beats}
    (REEL / "beat_sheet.json").write_text(json.dumps(sheet, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {len(beats)} beats; words: " +
          ", ".join(f"{b['beat_id']}:{len(b['narration_text'].split())}" for b in beats))


if __name__ == "__main__":
    build()
