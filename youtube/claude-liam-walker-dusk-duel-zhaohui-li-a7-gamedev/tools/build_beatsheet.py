#!/usr/bin/env python3
"""Write beat_sheet.json for the A7 gamedev film ("Dusk Duel, Animated").

Adapted from the A6 reel's builder. Code excerpts are read from the hashed source files at the line
ranges below, so the text on screen is the file's text byte for byte. Cue times are fractions of
each beat's measured narration once mp3/beat-Bxx.mp3 exists (audio is the clock), estimates before
that. Footage comes from capture/a7_play.avi (tools/capture_a7.gd, scripted input, 60 fps; movie
frame n shows the state after driver tick n + 1). Event ticks in capture/a7_play.log: Enter 360,
fight 420, kicks (whiff) from 571 and 662, kick paused at Fighter.frame 10 ticks 764-943, Aotake
hits Akaken on ticks 1031 (P1 frame 4), 1136 (frame 10), 1251 (frame 20), end 1436.
Footage beats list `segments` (seconds into the capture, speed 1 or a labelled slow replay); the
last segment absorbs the measured narration length (tools/build_media.py).
"""
import base64
import json
import pathlib
import subprocess

REEL = pathlib.Path(__file__).resolve().parent.parent
REPO = REEL.parent.parent
GAME = REPO / "godot"
SLUG = REEL.name
TITLE = "Dusk Duel, Animated"
SOURCE_REV = "8049c54"            # last commit touching godot/ when the film was built
PROJECT = "walker-dusk-duel"
FIG = REEL / "figures"
OLD = json.loads((REEL / "beat_sheet.json").read_text(encoding="utf-8")) if (REEL / "beat_sheet.json").exists() else None
LABEL_PLAY = "SCRIPTED-INPUT CAPTURE · Godot 4.7.2 · copy of 8049c54 · keys sent by script · Aotake scripted"
HANDLE = "@NikBearBrown"
CROP_FIGHT = [1230, 750, 1980, 1114]    # viewport x 205-535, y 125-311: both fighters, both lanterns, banner
CROP_LANTERN = [1200, 900, 1680, 945]   # viewport x 200-480, y 150-307.5: both lanterns


def t(tick):
    return round((tick - 1) / 60.0, 3)


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
RESPELL = {"Akaken": "Ah-kah-ken", "Aotake": "Ah-oh-tah-keh"}


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


def footage_beat(bid, act, segments, narration, est, show, crop=None, label_extra="", **extra):
    shot = {"type": "VIDEO", "class": "SHOW", "source": "capture", "motion": "none", "capture": "a7_play",
            "capture_file": "capture/a7_play.avi", "segments": segments, "show": show,
            "label": LABEL_PLAY + label_extra, "evidence_media": f"media/{bid}.mp4"}
    if crop:
        shot["crop"] = crop
    return beat(bid, act, narration, est, shot, **extra)


def cards4(*pairs):
    return [{"label": a, "text": b} for a, b in pairs]


def show4(first, labels):
    return [{"at": "0.05", "event": f"{first}; {labels[0]} card lights"}] + \
           [{"at": f"{tt:.2f}", "event": f"{lab} card lights"} for tt, lab in zip((0.3, 0.55, 0.8), labels[1:])]


def build():
    beats = []
    beats.append(beat("B00", "ASK",
        "Ciao, this is Liam, in for Bear. Jow-hway Lee's Dusk Duel is a 2D fighting game, and assignment seven adds "
        "two animation clips: a lantern flame that loops on the background, and an arc that sweeps beside every kick "
        "and commits. Jow-hway chose the clips, the routes and the frame counts, and judged every strip. Claude Code "
        "built the clips, the scenes and the tests.", 24,
        {"type": "GRAPHIC", "class": "SHOW", "source": "remotion", "motion": "type-on",
         "show": [{"at": "0.02", "event": "composer card fades in on the cream page"},
                  {"at": "0.12", "event": "greeting 'Ciao, Liam' appears above the composer"},
                  {"at": "0.3", "event": "the reconstructed Walker ask types in"},
                  {"at": "0.66", "event": "send button arms terracotta"},
                  {"at": "0.78", "event": "three RESULT lines land beneath the card"}],
         "remotion": {"pattern": "ClaudeComposerAsk", "props": {
             "greeting": "Ciao, Liam", "topic": "WALKER · ANIMATION", "segment": TITLE,
             "command": "Please use Walker to convert my game design document about Dusk Duel into two animation "
                        "clips: a lantern flame that loops, and a kick arc timed from the kick's own frame data. I "
                        "choose the routes, the frame counts and the clocks; you build the clips, scenes and tests.",
             "runningText": "reconstructed ask · built step by step in one day of sessions",
             "folderLabel": HANDLE, "modelLabel": "Claude", "effortLabel": "High",
             "output": ["Read-backs: 47 / 0 and 52 / 0.",
                        "States 58 / 0, edges 38 / 0, pins 19 / 0.",
                        "Clip time vs Fighter.frame / 60: 0 s apart."]}}},
        role_note="COLD OPEN LAW, walker B00. The Walker prompt is an ILLUSTRATIVE RECONSTRUCTION: the A7 work was "
                  "done in steps (prompts/a7/, desktop session), not one Walker run. RESULT lines are real (TEST-REPORT A7)."))

    beats.append(beat("B01", "BLUF",
        "Two clips, each with exactly one authority. The headless tests prove the keys and the timing, not the "
        "picture. The picture took frame strips, and eyes.", 11,
        {"type": "GRAPHIC", "class": "SHOW", "source": "remotion", "motion": "type-on-correct",
         "show": [{"at": "0.0", "event": "cream page; typing begins during the lead silence"},
                  {"at": "0.2", "event": "'The read-backs prove the picture.' types, then pauses"},
                  {"at": "0.45", "event": "'picture' struck through in terracotta"},
                  {"at": "0.6", "event": "'timing' types in its place"},
                  {"at": "0.85", "event": "corrected overview settles before the cut"}],
         "remotion": {"pattern": "BrutalistHesitantWriter", "props": {
             "contextTitle": "BLUF",
             "text": "Two clips, one authority each.\nThe read-backs prove the picture.\nOnly strips and eyes judged the look.",
             "triggerWords": "picture", "replacementWords": "timing",
             "fontSize": 76, "lineSpacing": 2.4, "align": "center", "seed": "7270-a7",
             "mistakeRate": 0, "hesitateWithin": 0, "hesitateBetween": 0, "charMs": 8,
             "ink": "#3D3929", "accent": "#D97757", "bg": "#FAF9F5", "brandLabel": HANDLE}}},
        lead_silence_s=0.8,
        role_note="EXECUTIVE-SUMMARY LAW. The corrected misconception: a passing headless read-back proves keys and "
                  "timing, not the picture. 'picture' appears once in the typed text before the correction."))

    beats.append(footage_beat("B02", "OPEN", [{"start": 0.0, "speed": 1}],
        "Here's the running game: a Movie Maker capture of an isolated copy, with scripted input. On the title "
        "screen, both lanterns already burn. That's clip one, a sprite sheet flipped frame by frame, and it loops. "
        "Then the round starts, Akaken walks in and kicks, and the pale arc beside the leg is clip two, a cutout "
        "rig. It plays once per kick, and commits.", 20,
        [{"at": "0.05", "event": "title screen; both lantern flames flicker"},
         {"at": "0.3", "event": "Enter: ROUND 1 - FIGHT intro"},
         {"at": "0.4", "event": "Akaken walks right"},
         {"at": "0.5", "event": "two whole kicks with the pale arc"},
         {"at": "0.7", "event": "a third kick, paused (PAUSED banner), shown again in B13"}],
        role_note="Real Movie Maker capture of an isolated copy (capture/game, 8049c54). Scripted input: Enter, D, K, "
                  "Esc sent by tools/capture_a7.gd; Aotake on the game's ScriptedController. Full frame, labelled."))

    beats.append(figure_beat("B03", "DESIGN", "fig_clips.png", "Two Clips, Two Routes",
        "DESIGN · CHANGE-BRIEF.md A7, “The two clips”, Zhaohui's choices", "the brief's table, with the wiring of Revision 3",
        cards4(("Clip 1", "lantern flame: loops"), ("Clip 2", "kick arc: commits"), ("Authority", "one writer each"),
               ("Clocks", "idle vs physics")),
        [(0.05, 0), (0.35, 1), (0.65, 2), (0.85, 3)],
        "In the brief, these are Jow-hway's choices. The lantern flame is a cycle: a Sprite 2D with an animation "
        "player frame track, set to loop. The kick arc is a committing action: two polygons on a pivot, keyed as "
        "resource text, with no loop. Each animated property has one authority, and each clip has its own clock.", 20,
        "Source: CHANGE-BRIEF.md (A7) “The two clips”, “The two clocks”, Revision 3; SUBMISSION.md; godot/game/main.tscn, godot/fighter/fighter.tscn",
        show4("the two-clip table", ["Clip 1", "Clip 2", "Authority", "Clocks"]), still=True))

    beats.append(figure_beat("B04", "ASSET", "fig_sheet.png", "The Sheet",
        "SOURCE · godot/art/sheets/lantern_flame.png, enlarged 20× · generated by code, MIT", "the committed PNG and its slicing",
        cards4(("Size", "48 × 32 px"), ("Slicing", "4 × 2 cells, 12 × 16"), ("Base", "(6, 15) every cell"),
               ("Licence", "code, MIT")),
        [(0.05, 3), (0.4, 0), (0.55, 1), (0.8, 2)],
        "The sheet comes first. Jow-hway chose to generate it by code, and Claude Code wrote the generator, so "
        "there's no downloaded art, and the licence is the repository's MIT. Forty-eight by thirty-two pixels: four "
        "columns and two rows of twelve by sixteen cells. Cell n is frame n. Every flame's base sits on the same "
        "pixel, six, fifteen, so the sprite is offset by minus six, minus fifteen, and the flame stands still.", 24,
        "Source: godot/art/sheets/lantern_flame.png, make_lantern_flame_sheet.gd:9-16, ATTRIBUTION.md; godot/animations/lantern_flame.tscn:15-21",
        show4("the sheet with its grid", ["Licence", "Size", "Slicing", "Base"]), still=True))

    beats.append(code_beat("B05", "animations/lantern_flicker.tres", 5, 18, "The Frame Track",
        "Here's the frame track that reads it. Line eleven: the track writes the sprite's frame. Line fifteen: eight "
        "keys, a tenth of a second apart, ten frames a second, matching the step on line seven. Line eighteen: cells "
        "zero to seven, in order. Line seventeen: update one, discrete, so the frame jumps from cell to cell. Line "
        "five, length point eight: one more interval after the last key, so seven wraps straight to zero. And line "
        "six turns the loop on.", 26,
        [{"label": "Reads the sheet", "value": "Sprite2D:frame, cells 0–7"},
         {"label": "Rate", "value": "keys 0.1 s apart = step = 10 fps"},
         {"label": "Seam", "value": "length 0.8 − last key 0.7 = 0.1"}],
        [(0.07, 11, "the track writes Sprite2D.frame"), (0.18, 15, "8 keys, 0.1 s apart"), (0.3, 7, "step 0.1 s"),
         (0.42, 18, "cells 0 to 7, in order"), (0.55, 17, "update 1: UPDATE_DISCRETE"),
         (0.72, 5, "length 0.8: the seam gap = one interval"), (0.9, 6, "loop_mode 1: LOOP_LINEAR")],
        ["godot/animations/lantern_flicker.tres", "agent (867ad72), values from Zhaohui's cycle spec"],
        "values from Zhaohui's brief; clip by a Claude Code agent"))

    beats.append(footage_beat("B06", "RESULT", [{"start": 1.5, "speed": 1}],
        "And here's what it draws, at real speed. Each flame changes cell every tenth of a second, and the right one "
        "runs half a cycle ahead, so the two never flicker together. On the title, Akaken's raised arm covers the left "
        "lantern. Claude noted that, and it's still open. Once Akaken walks in, both flames show.", 18,
        [{"at": "0.05", "event": "both lantern flames, cropped; the left one behind Akaken's arm"},
         {"at": "0.5", "event": "the round starts; Akaken walks right, uncovering the left flame"},
         {"at": "0.8", "event": "both flames visible, out of step"}],
        crop=CROP_LANTERN, label_extra=" · cropped 1.8×",
        role_note="Same capture as B02, earlier part, cropped to both lanterns (4K source x 1200-2880, y 900-1845)."))

    beats.append(figure_beat("B07", "QUESTION 1", "fig_clip_data.png", "What A Clip Is",
        "SOURCE + RECORDED OUTPUT · kick_arc.tres, logs/mutation_a7_1_subname_60fps.log, TEST-REPORT A7",
        "a track path, and the mutation that broke it",
        cards4(("A clip", "tracks: path, keys"), ("Mutation 1", "rotaton"), ("Silent", "no engine error"),
               ("The probe", "moved nothing")),
        [(0.05, 0), (0.3, 1), (0.5, 2), (0.8, 3)],
        "Question one: what is a clip? Not a movie. A list of tracks, each a node path, a property, and keys at "
        "times. Nothing checks that path while the clip plays. Mutation one removed a single letter from the rotation "
        "track's property. The log shows no engine error at all: the arc would simply never turn. Only the read-back, which "
        "asks every track to resolve, failed. Claude Code met the same silence too, in its own probe: a track that "
        "moved nothing and printed nothing.", 26,
        "Source: godot/animations/kick_arc.tres:31-38; logs/mutation_a7_1_subname_60fps.log:9-10, 56; TEST-REPORT.md A7 Findings 3; CLAUDE.md:61-62",
        show4("the clip as data, the mutation, the probe", ["A clip", "Mutation 1", "Silent", "The probe"])))

    beats.append(figure_beat("B08", "QUESTION 4", "fig_phase.png", "Feel, Counted In Frames",
        "DESIGN · CHANGE-BRIEF.md A7 “The phase table”, measured from fighter.gd", "phase table beside the key times",
        cards4(("Constants", "7 / 5 / 16"), ("Counted", "8 / 5 / 15"), ("Key times", "0 · .1333 · .2167"),
               ("Length", "28 / 60 = .4667 s")),
        [(0.05, 0), (0.3, 1), (0.7, 2), (0.9, 3)],
        "Question four: designing feel in frames. The constants in the code say seven, then five, then sixteen. But the tick a kick starts "
        "is frame zero, and the hit check runs only while frame is above seven and at most twelve. Counted from the "
        "code: startup, eight frames; active, five; recovery, fifteen; idle on frame twenty-eight. Jow-hway chose the "
        "measured counts. Divide by sixty, and the keys go at zero, zero point one three three three, zero point two "
        "one six seven, and zero point four six six seven seconds, the clip's length.", 28,
        "Source: CHANGE-BRIEF.md (A7) project facts, “The phase table”, Revision 4; godot/fighter/fighter.gd:35-38, 90, 103-108, 164-165",
        show4("the phase table and the timeline", ["Constants", "Counted", "Key times", "Length"]), still=True))

    beats.append(code_beat("B09", "animations/kick_arc.tres", 31, 44, "Those Keys, As Text",
        "Those keys, as text. Line thirty-five: seven key times, on every phase boundary and the frame before it. "
        "Line thirty-eight: the pivot's angle, wound back to a hundred degrees during startup, then sweeping down to "
        "minus fifteen at the hitbox. Line thirty-six, the spacing: a transition of two accelerates into the active "
        "frames, and point four settles through recovery. Line forty-three: a second track fades the arc in and out.", 24,
        [{"label": "Keys", "value": "frames 0, 7, 8, 12, 13, 27, 28 ÷ 60"},
         {"label": "Angle", "value": "85° → 100° → 70° → −15° → −20°"},
         {"label": "Spacing", "value": "2.0 in, 1.0 sweep, 0.4 out"}],
        [(0.08, 35, "7 key times on the phase boundaries"), (0.32, 38, "angles in radians: wind-up, sweep, settle"),
         (0.6, 36, "transitions: 2.0 eases in, 0.4 settles"), (0.88, 43, "track 2: Pivot:modulate")],
        ["godot/animations/kick_arc.tres", "agent (cfdc572); key 0 alpha r1 (8049c54), approved by Zhaohui"],
        "phase table from Zhaohui's choice; clip by a Claude Code agent"))

    beats.append(figure_beat("B10", "RESULT", "fig_strip.png", "The Strip, Boundary By Boundary",
        "OBSERVED · captures/kick_arc/r1 · fixture capture by Zhaohui", "capture frames 10, 13, 14, 16, 17, 23, 24",
        cards4(("Startup", "10, 13"), ("Active", "14, 16"), ("Recovery", "17, 23"), ("Idle", "24")),
        [(0.15, 0), (0.42, 1), (0.66, 2), (0.9, 3)],
        "And the committed strip, a fixture capture at thirty frames a second, two ticks per frame. Frame ten, "
        "startup begins: a faint wind-up. Thirteen, wound back. Fourteen, active opens at full strength. Sixteen, the "
        "last active frame, its head on the foot. Seventeen, recovery, fading. Twenty-three, nearly gone. "
        "Twenty-four, idle: no arc.", 22,
        "Source: captures/kick_arc/r1/frame000000{10,13,14,16,17,23,24}.png; logs/kick_arc_preview_frames.log; CHANGE-BRIEF.md (A7) “Frame strips”",
        show4("seven boundary frames", ["Startup", "Active", "Recovery", "Idle"]), evidence=True, still=True))

    beats.append(figure_beat("B11", "TUNING", "fig_tuning.png", "Revision r1",
        "PREDICT + OBSERVED · TUNING.md A7 · Claude's reading, Zhaohui's approval and verdict", "frame 10, r0 and r1",
        cards4(("Reading", "Claude's, no arc"), ("Change", "alpha 0 → 0.25"), ("Prediction", "only 10–11 change"),
               ("Verdict", "能看的出来，刚好")),
        [(0.05, 0), (0.45, 1), (0.65, 2), (0.85, 3)],
        "That faint arc on frame ten is revision r one. In r zero it wasn't there: the fade began at alpha zero. That "
        "was Claude's reading. Jow-hway's own first look said just right, and the first verdict was nothing to "
        "change. Then Jow-hway asked for Claude's points to be fixed, and approved one change: alpha zero to point "
        "two five. Claude predicted that only the first frames would change, and the strip agreed. Jow-hway's verdict "
        "after play: it can be seen, just right.", 26,
        "Source: TUNING.md (A7) r0, reading, verdict, r1, comparison; CHANGE-BRIEF.md Revision 5; commits a82293f, 8049c54, fd041ac, b580d17",
        show4("r0 and r1 frame 10, the change and the verdict", ["Reading", "Change", "Prediction", "Verdict"]), still=True))

    beats.append(code_beat("B12", "fighter/kick_rig.gd", 28, 38, "Who Moves The Arc",
        "Now, who moves the arc? Kick rig dot gd, on every physics tick, after Main has stepped the fighters and "
        "checked hits. Line thirty-two: if the state is kick, line thirty-five seeks the clip to the fighter's own "
        "frame over sixty. Any other state, line thirty-seven plays rest, and the arc is hidden. The player itself is "
        "on manual, so it never moves on its own.", 20,
        [{"label": "When", "value": "physics tick, priority 100 (line 24)"},
         {"label": "Reads", "value": "state, frame; writes neither"},
         {"label": "Clock", "value": "MANUAL: only seek() moves it"}],
        [(0.08, 28, "every physics tick"), (0.35, 32, "state kick?"), (0.48, 35, "seek(frame / 60, true)"),
         (0.7, 37, "any other state: rest, arc hidden")],
        ["godot/fighter/kick_rig.gd", "agent (a0161d6), plan approved by Zhaohui (“Approve plan”)"],
        "agent; wiring plan approved by Zhaohui"))

    beats.append(footage_beat("B13", "RESULT",
        [{"start": t(556), "end": t(606), "speed": 0.125}, {"start": t(606), "speed": 1}],
        "In play: one kick at an eighth of real speed, every captured frame held, none added. Then two more at real "
        "speed, the second paused in its active frames. The frame stops, so the arc freezes, and the lantern behind "
        "it keeps burning.", 13,
        [{"at": "0.05", "event": "REPLAY 1/8: a whole kick, arc winds back, sweeps, fades"},
         {"at": "0.5", "event": "real speed: a kick, then a kick paused at Fighter.frame 10"},
         {"at": "0.7", "event": "PAUSED: the arc stays put; the right lantern flame keeps changing"}],
        crop=CROP_FIGHT, label_extra=" · cropped 1.55×",
        role_note="Same capture, ticks 556-606 replayed at 1/8 (each 60 fps frame held 4 output frames, labelled), then "
                  "real speed from tick 606 (kick 662-689; kick from 753 paused ticks 764-943 at Fighter.frame 10)."))

    beats.append(footage_beat("B14", "STATES",
        [{"start": t(1020), "end": t(1040), "speed": 0.125}, {"start": t(1122), "end": t(1142), "speed": 0.125},
         {"start": t(1230), "end": t(1258), "speed": 0.125}, {"start": t(1005), "speed": 1}],
        "Now the interrupts, one per phase. Aotake's longer kick lands on Akaken's frame four, in startup; frame ten, "
        "during active; and frame twenty, in recovery. Each time the state turns to hurt, and on that same tick the arc "
        "is gone. Then all three, at real speed.", 15,
        [{"at": "0.03", "event": "REPLAY 1/8: Aotake's kick lands on Akaken's startup (frame 4); arc gone, red hurt flash"},
         {"at": "0.2", "event": "REPLAY 1/8: hit on Akaken's active frame 10; arc gone"},
         {"at": "0.38", "event": "REPLAY 1/8: hit on recovery frame 20; arc gone"},
         {"at": "0.6", "event": "real speed: the three interrupts in sequence"}],
        crop=CROP_FIGHT, label_extra=" · cropped 1.55×",
        role_note="Hits at ticks 1031, 1136, 1251 (capture/a7_play.log): P1 Fighter.frame 4, 10, 20; P1 -> hurt and "
                  "KickRig rest on the hit tick (logged clip rest, vis false the next line)."))

    beats.append(figure_beat("B15", "QUESTION 2", "fig_authority.png", "One Authority",
        "SOURCE · fighter.gd:286-291, kick_rig.gd, lantern_flame.gd · test_kick_readback", "one writer per property",
        cards4(("Lantern", "its own player"), ("Arc", "the rig's player"), ("Sprite", "fighter.gd only"),
               ("Two writers", "last write wins")),
        [(0.08, 0), (0.3, 1), (0.42, 2), (0.62, 3)],
        "Question two: one authority. Every animated property has exactly one writer. The lantern's frame: only its "
        "own animation player; its script just calls play and seek, once. The arc: the rig's player. The fighter's "
        "sprite already has a writer, fighter dot gd, every step. If a clip keyed that sprite too, the two would "
        "overwrite each other every tick, and the last write would win. The read-back checks that no track touches "
        "it. This film argues that from the code; no two-writer run was staged.", 28,
        "Source: godot/fighter/fighter.gd:286-291; godot/fighter/kick_rig.gd:1-11; godot/animations/lantern_flame.gd; logs/test_kick_readback_60fps.log:10-17; CHANGE-BRIEF predicted failure 4",
        show4("writers table and the two-writer case", ["Lantern", "Arc", "Sprite", "Two writers"])))

    beats.append(figure_beat("B16", "QUESTION 3", "fig_clocks.png", "Two Clocks",
        "MEASURED · tests/test_anim_states.gd · logs/test_anim_states_60fps.log", "idle tick vs physics tick",
        cards4(("Lantern", "idle tick"), ("Arc", "physics, MANUAL"), ("Hit check", "physics tick"), ("Gap", "0.000000000 s")),
        [(0.05, 0), (0.35, 1), (0.6, 2), (0.85, 3)],
        "Question three: the two clocks. The lanterns advance on the idle tick and read nothing from the game, which "
        "is why they burned through the pause. The arc never advances by itself: it's placed on the physics tick, "
        "the same tick where the hit check reads the active window. Measured across a whole kick, the largest gap "
        "between clip time and the fighter's frame over sixty: zero seconds.", 22,
        "Source: logs/test_anim_states_60fps.log:57-58, 65, 71-72; CHANGE-BRIEF.md (A7) “The two clocks”, short answer 5 (revision 2)",
        show4("both clocks and the measured gap", ["Lantern", "Arc", "Hit check", "Gap"])))

    beats.append(figure_beat("B17", "TESTS", "fig_tests.png", "What The Tests Proved",
        "HEADLESS · recorded output · logs/test_*_60fps.log, logs/mutation_a7_*", "suites and mutations",
        cards4(("Read-backs", "47 / 0 · 52 / 0"), ("States, edges", "58 / 0 · 38 / 0"), ("Pins", "19 / 0, before and after"),
               ("Mutations", "3 × exit 1, 1 × exit 0")),
        [(0.05, 0), (0.45, 1), (0.6, 2), (0.78, 3)],
        "What did the tests prove? The lantern read-back, forty-seven checks: slicing, discrete keys a tenth apart, "
        "the loop, and a clean seam. The kick read-back, fifty-two: keys on every boundary, a sixtieth step, no loop, "
        "and no track on the fighter's sprite. States, fifty-eight; edges, thirty-eight; and the nineteen behaviour "
        "pins held before and after. Three mutations failed them. The fourth, an empty import cache, couldn't fail: "
        "neither clip is imported.", 28,
        "Source: TEST-REPORT.md (A7); logs/test_lantern_readback_60fps.log:51, test_kick_readback:56, test_anim_states, test_kick_edges, test_pins_a7:44; logs/mutation_a7_1..4",
        show4("suites and mutations", ["Read-backs", "States, edges", "Pins", "Mutations"])))

    beats.append(figure_beat("B18", "HUMAN CHECK", "fig_human.png", "What No Headless Run Shows",
        "HEADLESS vs HUMAN · TEST-REPORT.md A7, Human checks", "Zhaohui's words, verbatim",
        cards4(("Seam", "没有卡顿"), ("Interrupt", "打断后消失"), ("Drift", "没有漂移"), ("Background", "看得清")),
        [(0.15, 0), (0.35, 1), (0.6, 2), (0.75, 3)],
        "What no headless run can show is the look. Those were Jow-hway's checks in the running game. The seam, over "
        "five wraps: no stutter. The kick: the phases can be told apart, and after an interrupt, the arc disappears. The "
        "flame: same place, no drift. On dark and lantern-lit stone: clearly visible. Recorded as given; Claude Code "
        "did not watch.", 22,
        "Source: TEST-REPORT.md (A7) Human checks (source b580d17); README.md A7 known limitations",
        show4("proves and cannot, and the four checks", ["Seam", "Interrupt", "Drift", "Background"])))

    beats.append(figure_beat("B19", "MISTAKES", "fig_mistakes.png", "Mistakes The Checks Caught",
        "RECORD · FRICTIONAL.md A7, TEST-REPORT.md A7, TUNING.md A7", "Claude Code's factual log",
        cards4(("Pin", "44 → 42"), ("A6 test", "draw order"), ("Brief", "28 → 29"), ("Claude", "seam guess wrong")),
        [(0.08, 0), (0.25, 1), (0.4, 2), (0.82, 3)],
        "The agent made mistakes, and checks caught them. It guessed the jump lasts forty-four ticks; the pin said "
        "forty-two. Its lanterns broke an assignment six draw-order test. It wrote that input returns on kick frame "
        "twenty-eight; the edge test found twenty-nine. A probe track moved nothing. Four harness bugs, and two "
        "failed sign-ins. Finally, Claude's strip reading guessed that a thin line was an edge between polygons; its own renders showed "
        "it was the old whiff streak.", 26,
        "Source: FRICTIONAL.md (A7) setup, Step 1, Steps 2–6, Tuning; TEST-REPORT.md A7 Pins, Findings, Claude against you; TUNING.md A7",
        show4("seven caught mistakes", ["Pin", "A6 test", "Brief", "Claude"])))

    beats.append(beat("B20", "VERDICT",
        "Verdict. Checked: both clips read back, every state plays the right clip, the arc freezes in hitstop and "
        "pause, vanishes on an interrupt, and sits zero seconds from the hit check. Uncertain: the left lantern is "
        "hidden at the start position; the empty-cache mutation cannot fail; the interrupt tests inject their hits; and "
        "revision r one came from Claude's reading, approved and judged by Jow-hway. Jow-hway chose the clips, routes, "
        "counts and clocks, wrote the answers, ran the strips and judged them. Claude Code built the rest. The sheet "
        "is generated by code, under MIT. Next step: a mutation that keys the fighter's sprite, to watch two "
        "authorities fight.", 44,
        {"type": "GRAPHIC", "class": "SHOW", "source": "remotion", "motion": "artifact-lines",
         "show": [{"at": "0.05", "event": "verdict page opens"}, {"at": "0.1", "event": "line 1: checked"},
                  {"at": "0.3", "event": "line 2: uncertain"}, {"at": "0.55", "event": "line 3: who did what"},
                  {"at": "0.75", "event": "line 4: Claude Code"}, {"at": "0.88", "event": "line 5: sheet, source, next step"}],
         "remotion": {"pattern": "ClaudeVerdictArtifact", "props": {
             "artifactTitle": "Verdict", "artifactHeading": "Two clips, one authority each", "brandLabel": HANDLE,
             "artifactLines": [
                 "Checked: 47/0, 52/0, 58/0, 38/0, pins 19/0 before and after; 3 mutations exit 1; clock gap 0 s.",
                 "Uncertain: left lantern hidden at start; empty-cache mutation can't fail; SETUP hits; r1 from Claude's reading.",
                 "Zhaohui: clips, routes, 8/5/15, clocks, answers, approved r1, ran both strips, verdicts, human checks.",
                 "Claude Code: sheet generator, clips, rig, controller, read-backs, state and edge tests, mutations, readings.",
                 f"Sheet: code-generated, MIT. Source shown: {SOURCE_REV} (godot/). Next: a two-writer mutation."]}}}))

    beats.append(beat("B21", "HANDOFF",
        "Your turn. Paste this: Please use Walker to add one animation clip to my game's brief before anything is "
        "built: its route, its one authority, its clock, and a phase table counted from the code. Then predict the "
        "frame strip at every phase boundary before you capture it. Count from the code, not the constants. This "
        "was Liam, in for Bear.", 24,
        {"type": "GRAPHIC", "class": "SHOW", "source": "remotion", "motion": "type-on",
         "show": [{"at": "0.05", "event": "composer opens with greeting 'Your turn.'"},
                  {"at": "0.2", "event": "the prompt types in"}, {"at": "0.6", "event": "send button arms"},
                  {"at": "0.75", "event": "three RESULT lines land"}],
         "remotion": {"pattern": "ClaudeComposerAsk", "props": {
             "greeting": "Your turn.", "topic": "WALKER · YOUR CLIP", "segment": "Count The Frames",
             "command": "Please use Walker to add one animation clip to my game's brief before anything is built: "
                        "its route, its one authority, its clock, and a phase table counted from the code. Then "
                        "predict the frame strip at every phase boundary before you capture it.",
             "runningText": "paste this into Claude…", "folderLabel": HANDLE,
             "modelLabel": "Claude", "effortLabel": "High",
             "output": ["Phase table counted from the code.", "Strip read against the prediction.",
                        "One writer per property."], "animateTyping": True}}}))

    beats.append(beat("B22", "OUTRO", f"{TITLE}. At Nik Bear Brown.", 5,
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
        if b.get("audio_file"):
            m = measured(b["beat_id"])
            if m:
                b["actual_duration_s"] = round(m, 2)
                b["audio_file"] = f"mp3/beat-{b['beat_id']}.mp3"
    sheet = {"metadata": {
        "title": TITLE, "slug": SLUG,
        "topic": "Two animation clips in a Godot fighting game: a looping sprite-sheet flame and a kick arc timed "
                 "from the state machine's frames",
        "kind": "godot-gamedev", "mode": "walker", "brand": "claude-liam", "channel": HANDLE,
        "channel_title": "Nik Bear Brown", "folderLabel": HANDLE, "persona": "Liam", "presenter": "Liam",
        "in_for_bear": True, "greeting": "Ciao, Liam",
        "greeting_note": "hello lexicon: Ciao (Italian), as in the author's A3, A5 and A6 reels.",
        "tts_respelling": "Narration respells Zhaohui Li as Jow-hway Lee, Akaken and Aotake phonetically for Kokoro "
                          "(checked with faster-whisper base.en). On-screen text always uses the real spellings.",
        "audience": "practitioners and makers following the channel's Claude workflows",
        "register": "Teardown", "engine": "kokoro", "voice": "am_onyx", "voice_kokoro": "am_onyx",
        "palette": "claude", "aspect_ratio": "16:9", "fps": 30, "captions": False,
        "game": {"name": PROJECT, "author": "Zhaohui Li", "source_revision": SOURCE_REV,
                 "godot": "4.7.2.stable.official.ed1daf0bf", "project": "godot/project.godot",
                 "renderer": "gl_compatibility",
                 "started_from": "the A2 2D game with the A5 shaders and A6 particles unchanged; A7 adds "
                                 "godot/animations/, godot/art/sheets/, the KickRig in fighter.tscn, two lanterns in "
                                 "main.tscn, the kick preview and the A7 tests"},
        "teaching_contract": "code-then-result-v1",
        "note": "Engine footage is a real Movie Maker capture of an isolated copy with scripted input (labelled; slow "
                "replays labelled, frames held, none added). Strip figures are the committed fixture captures in "
                "captures/kick_arc/ (Zhaohui's Movie Maker runs); labels, frames, grid lines and the dark backdrop "
                "behind the transparent sheet are the only new pixels."},
        "beats": beats}
    (REEL / "beat_sheet.json").write_text(json.dumps(sheet, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {len(beats)} beats; words: " +
          ", ".join(f"{b['beat_id']}:{len(b['narration_text'].split())}" for b in beats))


if __name__ == "__main__":
    build()
