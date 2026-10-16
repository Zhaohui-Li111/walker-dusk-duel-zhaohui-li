#!/usr/bin/env python3
"""Write beat_sheet.json for the A3 gamedev film ("Dusk Duel, Measured").

Code excerpts are read from the hashed source files at the line ranges below, so what is shown on
screen is the file's text byte for byte. Cue times are fractions of each beat's measured narration
once mp3/beat-Bxx.mp3 exists (audio is the clock), estimates before that. Capture windows are
seconds into capture/orbit.avi (tools/capture_orbit.gd: 0 s front, 12 s behind and low, 24 s front).
MCP printouts shown in the ask beats are copied from the session's tool results, verbatim; they are
also in tools/blender/build_taiko.py as the print() calls that produced them.
"""
import base64
import json
import pathlib
import subprocess

REEL = pathlib.Path(__file__).resolve().parent.parent
REPO = REEL.parent.parent
GAME = REPO / "godot"
SLUG = REEL.name
TITLE = "Dusk Duel, Measured"
SOURCE_REV = "1e88b83"            # last commit touching godot/ (props re-exported after the hand edit)
PROJECT = "walker-dusk-duel"
FIG = REEL / "figures"
OLD = json.loads((REEL / "beat_sheet.json").read_text(encoding="utf-8")) if (REEL / "beat_sheet.json").exists() else None
LABEL_ORBIT = "ENGINE CAPTURE · Godot 4.7.2 · props3d/prop_room.tscn · scripted camera orbit · native 4K"
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


RESPELL = {"taiko": "tie-koh", "makiwara": "mah-kee-wah-rah"}   # Kokoro read these as "take-o", "macuara"


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


def code_beat(bid, rel, start, end, title, narration, est, notes, cue_fracs, output, lang_note=""):
    d = dur(bid, est)
    code = excerpt(rel, start, end)
    cues = [{"at": round(f * d, 2), "line": line, "label": label} for f, line, label in cue_fracs]
    shot = {"type": "GRAPHIC", "class": "SHOW", "source": "remotion", "motion": "line-highlight",
            "show": [{"at": f"{f:.2f}", "event": f"line {line} highlights: {label}"} for f, line, label in cue_fracs],
            "remotion": {"pattern": "GodotDevWorkbench", "props": {
                "mode": "code", "title": title, "project": PROJECT, "path": f"res://{rel}",
                "source": f"Godot editor reconstruction · godot/{rel} lines {start}-{end} · source {SOURCE_REV}{lang_note}",
                "code": code, "startLine": start, "codeFontSize": 23,
                "inspectorLabel": "Source notes — not Inspector values",
                "notes": notes, "cues": cues, "output": output, "durationSeconds": round(d + 0.2, 2)}}}
    return beat(bid, "MECHANISM", narration, est, shot, excerpt={"path": rel, "start_line": start, "end_line": end})


# figures whose picture is diegetic (screenshots, engine stills, MCP renders): GATE T skips pixel checks
# on them; our own labels on them are checked on the masked copy (_qc/typecheck-masked)
DOCUMENTARY = {"fig_session.png", "fig_zhaohui_views.png", "fig_taiko_build.png", "fig_floor_check.png",
               "fig_hand_edit.png", "fig_makiwara.png"}


def figure_beat(bid, act, image, title, status, label, cards, cue_fracs, narration, est, source, show,
                evidence=False, **extra):
    d = dur(bid, est)
    shot = {"type": "STILL" if image in DOCUMENTARY else "GRAPHIC", "class": "SHOW", "source": "remotion",
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


def footage_beat(bid, act, start, narration, est, show, evidence=False, **extra):
    shot = {"type": "VIDEO", "class": "SHOW", "source": "capture", "motion": "none", "capture": "orbit",
            "capture_file": "capture/orbit.avi", "capture_start_s": start, "label": LABEL_ORBIT, "show": show}
    if evidence:
        shot["evidence_media"] = f"media/{bid}.mp4"
    return beat(bid, act, narration, est, shot, **extra)


def ask_beat(bid, act, narration, est, command, running, output, segment, show, spark, **extra):
    """An inner ask micro-beat (ASK -> RESULT LAW): the command is already typed."""
    shot = {"type": "GRAPHIC", "class": "SHOW", "source": "remotion", "motion": "ask-result",
            "show": show,
            "remotion": {"pattern": "ClaudeComposerAsk", "props": {
                "greeting": spark, "topic": "BLENDER MCP · EXECUTE_BLENDER_CODE", "segment": segment,
                "command": command, "runningText": running, "folderLabel": HANDLE,
                "modelLabel": "Claude", "effortLabel": "High", "output": output, "animateTyping": False}}}
    return beat(bid, act, narration, est, shot, **extra)


def build():
    beats = []
    beats.append(beat("B00", "ASK",
        "Ciao, this is Liam, in for Bear. Jow-hway Lee's Dusk Duel is a 2D fighting game. Assignment three "
        "gives it three simple 3D props: a stone lantern, a training post and a taiko drum. Claude built them "
        "in Blender through the Blender M C P, and Godot measured them. This film follows what the numbers "
        "proved, and what only an eye caught.", 22,
        {"type": "GRAPHIC", "class": "SHOW", "source": "remotion", "motion": "type-on",
         "show": [{"at": "0.02", "event": "composer card fades in on the cream page"},
                  {"at": "0.12", "event": "greeting 'Ciao, Liam' appears above the composer"},
                  {"at": "0.3", "event": "the reconstructed Walker ask types in"},
                  {"at": "0.66", "event": "send button arms terracotta"},
                  {"at": "0.78", "event": "three RESULT lines land beneath the card"}],
         "remotion": {"pattern": "ClaudeComposerAsk", "props": {
             "greeting": "Ciao, Liam", "topic": "WALKER · BLENDER MCP → GODOT", "segment": TITLE,
             "command": "Please use Walker to turn my Dusk Duel brief into three low-poly 3D props, a stone "
                        "lantern, a makiwara and a taiko drum, built in Blender through the Blender MCP to the "
                        "sizes, origins and triangle budgets I committed, then exported to a small Godot 3D "
                        "prop room and checked.",
             "runningText": "reconstructed ask · built step by step in one session",
             "folderLabel": HANDLE, "modelLabel": "Claude", "effortLabel": "High",
             "output": ["3 props: 100, 92 and 168 triangles.",
                        "Blender 5.2.2 · mcp-for-blender 2.1.9 · generators off.",
                        "Godot check: 49 checks, 0 failed."]}}},
        role_note="COLD OPEN LAW, walker B00. The Walker prompt is an ILLUSTRATIVE RECONSTRUCTION: the props "
                  "were built over one session of many steps, not from one Walker run. RESULT lines are real "
                  "outcomes (TEST-REPORT A3, evidence/check-props3d.txt). Liam named in first breath."))

    beats.append(beat("B01", "BLUF",
        "Claude built three props in Blender, and the checks prove they measure right. Not that they look "
        "right. The brief fixed every number first; the defects the numbers missed, an eye had to catch.", 12,
        {"type": "GRAPHIC", "class": "SHOW", "source": "remotion", "motion": "type-on-correct",
         "show": [{"at": "0.0", "event": "cream page; typing begins during the lead silence"},
                  {"at": "0.2", "event": "'The checks prove they look right.' types, then pauses"},
                  {"at": "0.45", "event": "'look' struck through in terracotta"},
                  {"at": "0.6", "event": "'measure' types in its place"},
                  {"at": "0.85", "event": "corrected overview settles before the cut"}],
         "remotion": {"pattern": "BrutalistHesitantWriter", "props": {
             "contextTitle": "BLUF",
             "text": "Claude built three props.\nThe checks prove they look right.\nThe brief set the numbers;\neyes caught the rest.",
             "triggerWords": "look", "replacementWords": "measure",
             "fontSize": 80, "lineSpacing": 2.4, "align": "center", "seed": "7270-a3",
             "mistakeRate": 0, "hesitateWithin": 0, "hesitateBetween": 0, "charMs": 8,
             "ink": "#3D3929", "accent": "#D97757", "bg": "#FAF9F5", "brandLabel": HANDLE}}},
        lead_silence_s=0.8,
        role_note="EXECUTIVE-SUMMARY LAW. The corrected misconception is the assignment's own warning: a "
                  "passing check shows the props arrived at the measured size, not that they look right. "
                  "BrutalistHesitantWriter replaces every matching token, so 'look' appears once in the text."))

    beats.append(footage_beat("B02", "OPEN", 0.0,
        "Here they are in Godot, in a small 3D room beside the 2D game. The lantern frames the arena's edge, "
        "like the courtyard's lanterns. The makiwara is Ah-kah-ken's punching post, its pad at fist height. "
        "The taiko is the drum you hear in the music loop. The grey box is Ah-kah-ken: one point seven metres.", 16,
        [{"at": "0.05", "event": "front view: lantern, makiwara, taiko, 1.70 m box on the floor"},
         {"at": "0.5", "event": "the camera swings round the side"}],
        role_note="Real Movie Maker capture of an isolated copy (capture/game), camera driven by "
                  "tools/capture_orbit.gd; the scene and assets are unchanged."))

    beats.append(figure_beat("B03", "DESIGN", "fig_brief.png", "Numbers Before Any Mesh",
        "DESIGN · CHANGE-BRIEF.md, committed 30513a4 before anything was built", "the three specs, verbatim",
        [{"label": "Size", "text": "±0.02 m per axis"}, {"label": "Origin", "text": "underside, Z = 0"},
         {"label": "Budget", "text": "150 / 120 / 200 tris"}, {"label": "Predicted", "text": "7 failure cases"}],
        [(0.05, 0), (0.3, 1), (0.5, 2), (0.75, 3)],
        "Before Blender held a single prop, the brief was committed: width, depth and height in metres, the "
        "origin at the centre of the underside, a triangle budget, base colours, and seven ways it could go "
        "wrong. A default thirty-two segment cylinder alone costs a hundred and twenty-four triangles, so "
        "every segment count is written down.", 20,
        "Source: CHANGE-BRIEF.md, Assignment 3 (repo commit 30513a4)",
        [{"at": "0.05", "event": "three spec cards; Size card lights"},
         {"at": "0.3", "event": "Origin card lights"}, {"at": "0.5", "event": "Budget card lights"},
         {"at": "0.75", "event": "Predicted card lights"}]))

    beats.append(figure_beat("B04", "SETUP", "fig_session.png", "Zhaohui's Blender, Connected",
        "ZHAOHUI'S OWN SCREENSHOT · Blender 5.2.2 LTS · 16:40", "Win + PrtScn, cropped to the MCP and Transform panels",
        [{"label": "Port", "text": "localhost 9876"}, {"label": "Libraries", "text": "all unticked"},
         {"label": "Generators", "text": "all unticked"}, {"label": "Transform", "text": "0 · 0° · 1.000"}],
        [(0.05, 0), (0.45, 1), (0.6, 2), (0.82, 3)],
        "This is Jow-hway's own screenshot. On Windows, the course's registration line failed: Claude Code "
        "read the server name as a second environment variable, and putting the name first fixed it. The "
        "add-on shows the connection on port ninety-eight seventy-six, with every download and generator "
        "unticked. So every shape had to be built from code.", 20,
        "Source: evidence/blender/zhaohui_object_mode_taiko_selected.png; FRICTIONAL.md A3 setup",
        [{"at": "0.05", "event": "Zhaohui's screenshot; Port card lights on the MCP panel"},
         {"at": "0.45", "event": "Libraries card lights"}, {"at": "0.6", "event": "Generators card lights"},
         {"at": "0.82", "event": "Transform card lights"}]))

    beats.append(ask_beat("B05", "ASK",
        "The build was one execute-blender-code call per prop, from a task brief the parent Claude session "
        "wrote: low segment counts, colours set on the shader node, the drum turned ninety degrees, then "
        "applied. The printout says the size is right. Now read the second line: the mesh starts three "
        "centimetres below zero.", 16,
        "严格按 CHANGE-BRIEF.md 的 A3 规格，一个一个建（PROP-LANTERN → PROP-MAKIWARA → PROP-TAIKO），每个一个 .blend 文件"
        "\n(Strictly to the A3 spec in CHANGE-BRIEF.md, one at a time, one .blend file each.)",
        "task brief from the parent Claude session · build PROP-TAIKO",
        ["joined tris 168 dims [0.7, 0.55, 0.95]",
         "x -0.35 0.35 y -0.275 0.275 z -0.03 0.92",
         "Info: Saved as \"prop_taiko.blend\""],
        "Build The Taiko",
        [{"at": "0.05", "event": "composer with the brief already typed; running line"},
         {"at": "0.55", "event": "RESULT lines land: tris and size"},
         {"at": "0.8", "event": "the z -0.03 line is the one the narration points at"}],
        "Starts below zero.",
        role_note="Ask micro-beat. The command is the user_prompt actually passed to execute_blender_code "
                  "(the parent session's brief, NOT Zhaohui's words; see FRICTIONAL correction). RESULT lines "
                  "are the call's printout, verbatim (session tool result; print() in build_taiko.py call 1)."))

    beats.append(figure_beat("B06", "RESULT", "fig_taiko_build.png", "The Origin Sat 3 cm Up",
        "OBSERVED · the join kept the base bar's origin (Z 0.03); fixed in call 2", "left: MCP look · right: engine still",
        [{"label": "Cause", "text": "join keeps active origin"}, {"label": "Missed by", "text": "scene info: on ground"},
         {"label": "Fix", "text": "move mesh, not object"}, {"label": "After", "text": "Z 0.00 to 0.95"}],
        [(0.05, 0), (0.35, 1), (0.6, 2), (0.82, 3)],
        "That's failure case three, predicted in the brief. Joining the parts kept the base bar's origin, three "
        "centimetres up. Blender's scene report still said on ground, because it measures the world box. Claude "
        "moved the mesh, not the object, so the origin sits at the centre of the underside. Left, Blender after "
        "the fix. Right, the same mesh in Godot.", 20,
        "Source: tools/blender/build_taiko.py calls 1-2; capture/mcp_look/1552_taiko_angles.png; capture/stills/real_taiko_floor.png",
        [{"at": "0.05", "event": "MCP look render and engine still; Cause card lights"},
         {"at": "0.35", "event": "Missed by card lights"}, {"at": "0.6", "event": "Fix card lights"},
         {"at": "0.82", "event": "After card lights"}]))

    beats.append(code_beat("B07", "props3d/prop_room.tscn", 49, 60, "The Room Places Each GLB At Zero",
        "In Godot, the prop room is a plain scene file. Each G L B comes in as an instance at y zero, the top of "
        "the floor, spaced along x. Nothing is scaled or rotated here, so any fix had to happen in Blender. The "
        "last node is the one point seven metre reference box, centred at point eight five.", 16,
        [{"label": "Instances", "value": "3 GLB scenes, x -1.6 / -0.6 / 0.5"},
         {"label": "Height", "value": "y = 0, the floor's top"},
         {"label": "Basis", "value": "identity: no scale, no turn"}],
        [(0.05, 49, "the lantern GLB, instanced"), (0.25, 50, "placed at y = 0"),
         (0.5, 56, "the taiko: same identity basis"), (0.75, 59, "1.70 m box, centre y 0.85")],
        ["godot/props3d/prop_room.tscn", "written by Claude Code"], lang_note=" · scene file"))

    beats.append(footage_beat("B08", "RESULT", 9.0,
        "Watch the bases as the camera drops low and round the back. All three stand on the floor: nothing "
        "sunk, nothing floating, nothing on its side. The drum's heads still face front and back after the "
        "export.", 12,
        [{"at": "0.1", "event": "the camera drops behind the props"},
         {"at": "0.5", "event": "low view: every base meets the floor"},
         {"at": "0.85", "event": "the drumheads face the camera's path, front and back"}], evidence=True))

    beats.append(code_beat("B09", "tests/check_props3d.gd", 72, 81, "Two Ways To Ask: On The Floor?",
        "The headless check takes the bounding box of each prop. Line seventy-two measures the lowest point "
        "from the prop's own node, so it can never fail just because the prop floats. Line seventy-nine "
        "measures from the floor's top face, read from the Floor node itself, and line eighty-one keeps that "
        "gap within a centimetre.", 18,
        [{"label": "Line 72", "value": "from the prop's own node"},
         {"label": "Line 79", "value": "from the Floor's top face"},
         {"label": "Tolerance", "value": "0.01 m"}],
        [(0.05, 72, "min y: relative to the prop itself"), (0.3, 78, "checked within 1 cm"),
         (0.5, 79, "relative to the floor"), (0.78, 81, "gap within 1 cm")],
        ["timeout 120 godot --headless --path godot --script res://tests/check_props3d.gd --fixed-fps 60"]))

    beats.append(figure_beat("B10", "RESULT", "fig_floor_check.png", "Raise It 5 cm And See",
        "OBSERVED · test copy with the taiko raised 0.05 m (capture/game-raised)", "engine stills, 4K, cropped",
        [{"label": "Real scene", "text": "49 checks, 0 failed"}, {"label": "Raised copy", "text": "1 failed: gap 0.0500"},
         {"label": "Line 72", "text": "passed anyway"}, {"label": "Proves", "text": "floor contact, not looks"}],
        [(0.05, 0), (0.3, 1), (0.55, 2), (0.8, 3)],
        "To prove it could fail, Claude raised the taiko five centimetres in a copy of the scene. The shadow "
        "comes off the base, and the check fails: gap point zero five. The older line seventy-two assertion "
        "passed anyway. That's the trap this assignment warns about: a check can prove less than it claims.", 18,
        "Source: evidence/check-props3d.txt and check-props3d-raised-copy.txt (recorded output)",
        [{"at": "0.05", "event": "real and raised stills side by side; Real scene card lights"},
         {"at": "0.3", "event": "Raised copy card lights; the shadow gap under the base"},
         {"at": "0.55", "event": "Line 72 card lights"}, {"at": "0.8", "event": "Proves card lights"}],
        evidence=True))

    beats.append(figure_beat("B11", "RESULT", "fig_numbers.png", "Brief, Blender, Godot",
        "HEADLESS · tests/check_props3d.gd · recorded output", "brief vs Blender vs Godot AABB",
        [{"label": "Size", "text": "0 deviation"}, {"label": "Axes", "text": "Blender Z = Godot Y"},
         {"label": "Transforms", "text": "scale 1, rotation 0"}, {"label": "Colours", "text": "hex exact"}],
        [(0.05, 0), (0.3, 1), (0.5, 2), (0.7, 3)],
        "Here's the whole headless run against the brief. Every dimension lands with zero deviation. "
        "Blender's Z becomes Godot's Y through the exporter's plus-Y-up setting, scale is one, rotation zero, "
        "and every base colour comes back as the brief's exact hex. Forty-nine checks, none failed. None of "
        "that says the props look right.", 18,
        "Source: evidence/check-props3d.txt; CHANGE-BRIEF.md; tools/blender/check_blend.py",
        [{"at": "0.05", "event": "three rows, brief beside Blender beside Godot; Size card lights"},
         {"at": "0.3", "event": "Axes card lights"}, {"at": "0.5", "event": "Transforms card lights"},
         {"at": "0.7", "event": "Colours card lights"}]))

    beats.append(figure_beat("B12", "INSPECT", "fig_makiwara.png", "What Look Saw: Collars",
        "OBSERVED · MCP look renders, before and after the revision", "Claude's look tool, 644 px originals",
        [{"label": "Numbers", "text": "all in budget"}, {"label": "Look", "text": "bands 4 cm out"},
         {"label": "Claude's slip", "text": "an ellipse that couldn't fit"}, {"label": "Fix", "text": "chamfered, 92 tris"}],
        [(0.05, 0), (0.28, 1), (0.52, 2), (0.78, 3)],
        "The first eye was Blender's look tool. The makiwara passed every number, but its round rope bands "
        "stood four centimetres out: more collar than rope. Claude then offered an ellipse that could never "
        "enclose the pad, and caught that before building. Jow-hway chose chamfered rings instead: same "
        "ninety-two triangles, one and a half centimetres out.", 20,
        "Source: capture/mcp_look/1549_*.png, 1550_*.png; FRICTIONAL.md makiwara entries",
        [{"at": "0.05", "event": "round bands vs chamfered rings; Numbers card lights"},
         {"at": "0.28", "event": "Look card lights on the round bands"},
         {"at": "0.52", "event": "Claude's slip card lights"}, {"at": "0.78", "event": "Fix card lights"}]))

    beats.append(ask_beat("B13", "ASK",
        "Then the hand edit. Jow-hway edited the taiko with the mouse, in Edit Mode. It nudged the drum body "
        "about a centimetre, and flattened the front drumhead onto the body. Asked to fix it, Jow-hway typed "
        "this: I can't really fix it, you fix it. Claude put the head back, in two calls, because the first "
        "only fixed half.", 18,
        "我不太会改，你改吧\n(I can't really fix it. You fix it.)",
        "Zhaohui's own prompt, verbatim · repair the front drumhead",
        ["front head cap: normal (0.0, -1.0, -0.0) y -0.255",
         "outer caps 1 inner caps 1",
         "dims [0.7, 0.55, 0.95] z 0.0 0.95"],
        "Repair The Hand Edit",
        [{"at": "0.05", "event": "composer with Zhaohui's prompt already typed"},
         {"at": "0.55", "event": "RESULT lines land: the outer cap found, the repaired size"}],
        "You fix it.",
        role_note="Ask micro-beat with Zhaohui's own words (passed verbatim as user_prompt). RESULT lines are "
                  "the printouts of build_taiko.py calls 3 and 4, verbatim."))

    beats.append(figure_beat("B14", "RESULT", "fig_hand_edit.png", "Zero Thickness, Every Check Passing",
        "OBSERVED · MCP look renders at 16:29 (hand edit saved 16:28) and 16:35 (repaired)", "Claude's look tool, oblique views",
        [{"label": "Depth", "text": "0.53 m, in tolerance"}, {"label": "Topology", "text": "0 non-manifold"},
         {"label": "Eye", "text": "red through the head"}, {"label": "Repair", "text": "24 vertices restored"}],
        [(0.05, 0), (0.25, 1), (0.5, 2), (0.78, 3)],
        "Left is the saved hand edit. Depth fifty-three centimetres, inside tolerance, and no non-manifold "
        "edges, so by the numbers it passes. From an angle, red shows through the cream: the head is "
        "flattened and its faces twisted. Claude restored the head's twenty-four vertices and kept Jow-hway's nudge to the "
        "body. Right is after the repair.", 20,
        "Source: capture/mcp_look/1629_*.png, 1635_*.png; tools/blender/build_taiko.py calls 3-4",
        [{"at": "0.05", "event": "broken and repaired drum side by side; Depth card lights"},
         {"at": "0.25", "event": "Topology card lights"}, {"at": "0.5", "event": "Eye card lights on the red patches"},
         {"at": "0.78", "event": "Repair card lights"}]))

    beats.append(figure_beat("B15", "HUMAN CHECK", "fig_zhaohui_views.png", "Below And Behind",
        "ZHAOHUI'S OWN SCREENSHOTS · Blender, Bottom and Back Orthographic · 16:41", "Win + PrtScn, cropped to the drum",
        [{"label": "Below", "text": "no hole underneath"}, {"label": "Behind", "text": "back head intact"},
         {"label": "Godot", "text": "walked round in the editor"}, {"label": "Said", "text": "\"no problems\""}],
        [(0.05, 0), (0.25, 1), (0.5, 2), (0.75, 3)],
        "The last check is human. Jow-hway looked from below and from behind in Blender, walked round the room "
        "in the Godot editor, and said: no problems. That's one overall judgement, not a report per prop, and "
        "it's the only evidence here that the props read as what they are.", 16,
        "Source: evidence/blender/zhaohui_bottom_view_taiko.png, zhaohui_back_view_taiko.png; TEST-REPORT.md A3 human check",
        [{"at": "0.05", "event": "Zhaohui's bottom and back views; Below card lights"},
         {"at": "0.25", "event": "Behind card lights"}, {"at": "0.5", "event": "Godot card lights"},
         {"at": "0.75", "event": "Said card lights"}]))

    beats.append(beat("B16", "VERDICT",
        "Verdict. Checked: size within two centimetres, origin, transforms, budget and colours, forty-nine "
        "headless checks with none failed, plus one human look. Uncertain: whether the props suit the game's "
        "style and lighting. Claude got four things wrong: the taiko origin, an ellipse that couldn't fit, a "
        "floor check that couldn't fail, and one call per prop where the course asked for one per object. "
        "Jow-hway chose the props, approved the numbers, edited by hand and looked; Claude built, checked and "
        "repaired. Next step: deepen the taiko's stand.", 32,
        {"type": "GRAPHIC", "class": "SHOW", "source": "remotion", "motion": "artifact-lines",
         "show": [{"at": "0.05", "event": "verdict page opens"}, {"at": "0.12", "event": "line 1: checked"},
                  {"at": "0.3", "event": "line 2: uncertain"}, {"at": "0.45", "event": "line 3: Claude got wrong"},
                  {"at": "0.68", "event": "line 4: who did what"}, {"at": "0.88", "event": "line 5: source and next step"}],
         "remotion": {"pattern": "ClaudeVerdictArtifact", "props": {
             "artifactTitle": "Verdict", "artifactHeading": "Three props, measured", "brandLabel": HANDLE,
             "artifactLines": [
                 "Checked: ±0.02 m, origin, transforms, budget, colours. 49 headless checks, 0 failed. One human look.",
                 "Uncertain: fit with the game's style and dusk lighting; one overall look, not per prop.",
                 "Claude got wrong: taiko origin; an ellipse that couldn't fit; a floor check that couldn't fail; one call per prop.",
                 "Zhaohui: chose the props, approved the numbers, hand edit, looked. Claude: built, checked, repaired.",
                 "Source shown: 1e88b83 (godot/). Next step: a deeper taiko stand."]}}}))

    beats.append(beat("B17", "HANDOFF",
        "Your turn. Paste this: Please use Walker to add one simple 3D prop to my game through the Blender MCP. "
        "First write its size in metres, its origin, a triangle budget and three predicted failures in my "
        "brief, and commit it. Build it one object per call, then write a Godot check that measures it against "
        "the floor, and prove that check fails when I raise the prop. The last step is the point: a check you "
        "have never seen fail hasn't shown you anything yet. Liam, in for Bear.", 30,
        {"type": "GRAPHIC", "class": "SHOW", "source": "remotion", "motion": "type-on",
         "show": [{"at": "0.05", "event": "composer opens with greeting 'Your turn.'"},
                  {"at": "0.2", "event": "the prompt types in"}, {"at": "0.6", "event": "send button arms"},
                  {"at": "0.75", "event": "three RESULT lines land"}],
         "remotion": {"pattern": "ClaudeComposerAsk", "props": {
             "greeting": "Your turn.", "topic": "WALKER · YOUR PROP", "segment": "Make The Check Fail",
             "command": "Please use Walker to add one simple 3D prop to my game through the Blender MCP. First "
                        "write its size in metres, its origin, a triangle budget and three predicted failures in "
                        "my brief, and commit it. Build it one object per call, then write a Godot check that "
                        "measures it against the floor, and prove that check fails when I raise the prop.",
             "runningText": "paste this into Claude…", "folderLabel": HANDLE,
             "modelLabel": "Claude", "effortLabel": "High",
             "output": ["Brief committed before the first mesh.", "Check measured against the floor node.",
                        "Raised copy: the check fails."], "animateTyping": True}}}))

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
        if b.get("audio_file"):
            m = measured(b["beat_id"])
            if m:
                b["actual_duration_s"] = round(m, 2)
                b["audio_file"] = f"mp3/beat-{b['beat_id']}.mp3"
    sheet = {"metadata": {
        "title": TITLE, "slug": SLUG,
        "topic": "Three Blender MCP props for a 2D Godot game: what the numbers proved and what an eye caught",
        "kind": "godot-gamedev", "mode": "walker", "brand": "claude-liam", "channel": HANDLE,
        "channel_title": "Nik Bear Brown", "folderLabel": HANDLE, "persona": "Liam", "presenter": "Liam",
        "in_for_bear": True, "greeting": "Ciao, Liam",
        "greeting_note": "hello lexicon: Ciao (Italian); the author's earlier reels used Namaste (A1) and Hola (A2).",
        "tts_respelling": "Narration respells names for Kokoro (checked with faster-whisper base.en): Jow-hway Lee / Jow-hway = Zhaohui Li, "
                          "Ah-kah-ken = Akaken, tie-koh = taiko, mah-kee-wah-rah = makiwara; M C P and G L B are spelled out. "
                          "On-screen text always uses the real spellings.",
        "audience": "practitioners and makers following the channel's Claude workflows",
        "register": "Teardown", "engine": "kokoro", "voice": "am_onyx", "voice_kokoro": "am_onyx",
        "palette": "claude", "aspect_ratio": "16:9", "fps": 30, "captions": False,
        "game": {"name": PROJECT, "author": "Zhaohui Li", "source_revision": SOURCE_REV,
                 "godot": "4.7.2.stable.official.ed1daf0bf", "project": "godot/project.godot",
                 "blender": "5.2.2 LTS", "mcp": "mcp-for-blender 2.1.9, add-on 1.8, protocol 13",
                 "started_from": "the A2 2D game; A3 adds godot/props3d/ and tests/check_props3d.gd"},
        "teaching_contract": "code-then-result-v1",
        "note": "Engine beats are real Movie Maker captures/stills of isolated copies (capture/game, and "
                "capture/game-raised for the labelled failing-check still). Blender images are Zhaohui's own "
                "screenshots or Claude's MCP look renders, each labelled."},
        "beats": beats}
    (REEL / "beat_sheet.json").write_text(json.dumps(sheet, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {len(beats)} beats; words: " +
          ", ".join(f"{b['beat_id']}:{len(b['narration_text'].split())}" for b in beats))


if __name__ == "__main__":
    build()
