#!/usr/bin/env python3
"""Write beat_sheet.json for the A5 gamedev film ("Dusk Duel, Shaded").

Adapted from the A3 reel's builder. Code excerpts are read from the hashed source files at the line
ranges below, so the text on screen is the file's text byte for byte. Cue times are fractions of
each beat's measured narration once mp3/beat-Bxx.mp3 exists (audio is the clock), estimates before
that. Footage windows are seconds into capture/flash.avi (tools/capture_flash.gd: Aotake flashes at
about 1.05 s, Akaken at about 4.2 s; scripted input).
"""
import base64
import json
import pathlib
import subprocess

REEL = pathlib.Path(__file__).resolve().parent.parent
REPO = REEL.parent.parent
GAME = REPO / "godot"
SLUG = REEL.name
TITLE = "Dusk Duel, Shaded"
SOURCE_REV = "043df17"            # last commit touching godot/ when the film was built
PROJECT = "walker-dusk-duel"
FIG = REEL / "figures"
OLD = json.loads((REEL / "beat_sheet.json").read_text(encoding="utf-8")) if (REEL / "beat_sheet.json").exists() else None
LABEL_FLASH = "SCRIPTED-INPUT CAPTURE · Godot 4.7.2 · game/main.tscn · fighters placed in range by the script · native 4K"
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
RESPELL = {"Akaken": "Ah-kah-ken", "Aotake": "Ah-oh-tah-keh", "GLSL": "G L S L", "UVs": "U Vs", "UV ": "U V "}


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


def footage_beat(bid, act, start, narration, est, show, evidence=False, **extra):
    shot = {"type": "VIDEO", "class": "SHOW", "source": "capture", "motion": "none", "capture": "flash",
            "capture_file": "capture/flash.avi", "capture_start_s": start, "label": LABEL_FLASH, "show": show}
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
        "Ciao, this is Liam, in for Bear. Jow-hway Lee's Dusk Duel is a 2D fighting game. Assignment five adds "
        "two shaders Jow-hway typed by hand: a red flash on whichever fighter was just hit, and a granite "
        "surface in the 3D prop room. Claude wrote the driver, the tests and the audit. This film follows what "
        "the tests proved, and what only eyes could judge.", 22,
        {"type": "GRAPHIC", "class": "SHOW", "source": "remotion", "motion": "type-on",
         "show": [{"at": "0.02", "event": "composer card fades in on the cream page"},
                  {"at": "0.12", "event": "greeting 'Ciao, Liam' appears above the composer"},
                  {"at": "0.3", "event": "the reconstructed Walker ask types in"},
                  {"at": "0.66", "event": "send button arms terracotta"},
                  {"at": "0.78", "event": "three RESULT lines land beneath the card"}],
         "remotion": {"pattern": "ClaudeComposerAsk", "props": {
             "greeting": "Ciao, Liam", "topic": "WALKER · SHADERS AND MATERIALS", "segment": TITLE,
             "command": "Please use Walker to convert my game design document about Dusk Duel into a hurt "
                        "flash and a granite material: I write both shaders by hand from my spec, and you "
                        "write the driver, the tests and the audit, without touching godot/shaders/.",
             "runningText": "reconstructed ask · built step by step over several sessions",
             "folderLabel": HANDLE, "modelLabel": "Claude", "effortLabel": "High",
             "output": ["Hurt flash: 69 checks, 0 failed at 30, 60 and 144 fps.",
                        "Materials: 96 checks, 0 failed, also from an empty cache.",
                        "Three shader mutations: each test exits 1."]}}},
        role_note="COLD OPEN LAW, walker B00. The Walker prompt is an ILLUSTRATIVE RECONSTRUCTION: the work "
                  "was done over several sessions of many steps, not from one Walker run. RESULT lines are "
                  "real outcomes (TEST-REPORT A5). Liam named in first breath."))

    beats.append(beat("B01", "BLUF",
        "Two shaders, typed by hand. The headless tests prove they parse, and that they're driven and wired as "
        "the brief said. Not that they look right. That part needed eyes.", 11,
        {"type": "GRAPHIC", "class": "SHOW", "source": "remotion", "motion": "type-on-correct",
         "show": [{"at": "0.0", "event": "cream page; typing begins during the lead silence"},
                  {"at": "0.2", "event": "'The tests prove they look right.' types, then pauses"},
                  {"at": "0.45", "event": "'look' struck through in terracotta"},
                  {"at": "0.6", "event": "'parse' types in its place"},
                  {"at": "0.85", "event": "corrected overview settles before the cut"}],
         "remotion": {"pattern": "BrutalistHesitantWriter", "props": {
             "contextTitle": "BLUF",
             "text": "Two shaders, typed by hand.\nThe tests prove they look right.\nOnly eyes judged the picture.",
             "triggerWords": "look", "replacementWords": "parse",
             "fontSize": 80, "lineSpacing": 2.4, "align": "center", "seed": "7270-a5",
             "mistakeRate": 0, "hesitateWithin": 0, "hesitateBetween": 0, "charMs": 8,
             "ink": "#3D3929", "accent": "#D97757", "bg": "#FAF9F5", "brandLabel": HANDLE}}},
        lead_silence_s=0.8,
        role_note="EXECUTIVE-SUMMARY LAW. The corrected misconception is the assignment's own: a passing "
                  "headless run proves parsing, driving and wiring, not the look. 'look' appears once."))

    beats.append(footage_beat("B02", "OPEN", 0.3,
        "Here's the game. Akaken punches, and Aotake turns red for about a third of a second, then fades "
        "back. A moment later Aotake kicks, and this time only Akaken flashes.", 9,
        [{"at": "0.1", "event": "Akaken's punch lands; Aotake turns fully red, then fades"},
         {"at": "0.45", "event": "Aotake's kick lands; only Akaken flashes"}],
        role_note="Real Movie Maker capture of an isolated copy (capture/game). Scripted input: the script "
                  "places the fighters in range, presses p1_punch through Input, and gives Aotake a "
                  "ScriptedController kick. Labelled on screen."))

    beats.append(figure_beat("B03", "DESIGN", "fig_predict.png", "The Colour Line Came First",
        "DESIGN · CHANGE-BRIEF.md A5, committed 4c8d90a before either shader", "brief excerpt, verbatim",
        cards4(("Line", "mix toward red"), ("Pixels", "gi and hand wrap"), ("By hand", "6 predictions"),
               ("Also", "contrast, clamp")),
        [(0.05, 0), (0.3, 1), (0.55, 2), (0.8, 3)],
        "Before either shader existed, the brief named the colour line: mix each pixel's own colour toward "
        "red, by hurt amount. From that one line, Jow-hway worked out by hand what two pixels of Akaken "
        "become at zero, a half and one: the orange gi, and the pale hand wrap.", 16,
        "Source: CHANGE-BRIEF.md, Assignment 5, Version 1 and Revisions 2-5",
        show4("the colour line and the prediction table", ["Line", "Pixels", "By hand", "Also"])))

    beats.append(code_beat("B04", "shaders/hurt_flash.gdshader", 1, 8, "What A Shader Does",
        "So what is a shader? A small program the graphics card runs for every pixel of this sprite, all at "
        "once. Line one makes it a canvas item shader, for 2D. Lines three and four are uniforms: values the "
        "game can set. Line seven is the colour line, mixing the pixel's colour toward the flash colour.", 18,
        [{"label": "Type", "value": "canvas_item: 2D, COLOR"},
         {"label": "Uniforms", "value": "hurt_amount, flash_color"},
         {"label": "Line 7", "value": "Zhaohui's colour line"}],
        [(0.05, 1, "shader_type canvas_item"), (0.35, 3, "hurt_amount: set by game code"),
         (0.5, 4, "flash_color: pure red"), (0.72, 7, "the colour line")],
        ["godot/shaders/hurt_flash.gdshader", "typed by hand by Zhaohui (f13d617)"], "typed by Zhaohui"))

    beats.append(figure_beat("B05", "RESULT", "fig_controlled.png", "Within One Step",
        "OBSERVED · tests/capture_a5.gd · in-engine capture, driver paused", "Akaken at three values, cropped",
        cards4(("0.0", "as stored"), ("0.5", "halfway to red"), ("1.0", "red"), ("Off by 1", "alpha 254")),
        [(0.05, 0), (0.3, 1), (0.5, 2), (0.75, 3)],
        "Here's line seven's output, captured from the running engine with the value set from code. Every "
        "sampled pixel lands within one step of Jow-hway's arithmetic. The steady one-step shortfall is the "
        "sprite's alpha: two fifty-four, not two fifty-five.", 16,
        "Source: capture/evidence/a5/hurt_flash_0_0.png, _0_5.png, _1_0.png; TEST-REPORT.md A5",
        show4("three captures with sample rings", ["0.0", "0.5", "1.0", "Off by 1"]), evidence=True, still=True))

    beats.append(code_beat("B06", "fighter/hurt_flash.gd", 15, 28, "Material Holds The Value",
        "A shader remembers nothing, so game state has to arrive as a uniform. This driver is Claude's. Lines "
        "nineteen to twenty-one give each fighter its own material: the material holds the values, the shader "
        "is shared. Line twenty-seven reads the stun counter once per physics tick, so the flash lasts "
        "twenty-two ticks at any frame rate.", 20,
        [{"label": "Material", "value": "one per fighter"},
         {"label": "Line 27", "value": "stun / HITSTUN"},
         {"label": "Priority", "value": "after main steps"}],
        [(0.05, 18, "runs after the fight steps"), (0.25, 19, "a new material per fighter"),
         (0.45, 21, "set on this sprite only"), (0.75, 27, "the value from game state")],
        ["godot/fighter/hurt_flash.gd", "written by Claude Code (session 2b)"], "written by Claude"))

    beats.append(footage_beat("B07", "RESULT", 3.2,
        "That's why, when Aotake's kick lands, only Akaken flashes. One shader, two materials, two "
        "separate flash values.", 7,
        [{"at": "0.2", "event": "Aotake's kick lands; Akaken alone turns red and fades"}], evidence=True,
        role_note="Same scripted-input capture as B02, later window, reused with disclosure."))

    beats.append(figure_beat("B08", "PREDICT", "fig_clamp.png", "Does hint_range Clamp?",
        "OBSERVED · grey flash_color set in memory for this check only", "Akaken at 1.0 and 2.0, cropped",
        cards4(("Predicted", "no clamp"), ("Red", "can't tell"), ("Grey 2.0", "(34, 167, 254)"), ("Held", "not clamped")),
        [(0.05, 0), (0.3, 1), (0.55, 2), (0.82, 3)],
        "Jow-hway predicted that hint range would not clamp a value set from code. With the red flash you "
        "can't tell: one and two both saturate. With grey, two gives thirty-four, one sixty-seven: the mix, "
        "extrapolated. Not clamped. The prediction held.", 16,
        "Source: capture/evidence/a5/hurt_flash_grey_1_0.png, _2_0.png; LANGUAGE-NOTES.md Q5",
        show4("grey captures at 1.0 and 2.0", ["Predicted", "Red", "Grey 2.0", "Held"]), still=True))

    beats.append(figure_beat("B09", "TESTS", "fig_tests.png", "Revise The Brief, Not The Test",
        "HEADLESS · tests/test_hurt_flash.gd · recorded output", "first run vs after Revision 7",
        cards4(("Loop", "real input, J key"), ("First", "4 failed"), ("Revised", "rules 3 and 4"), ("Now", "69 / 0 ×3")),
        [(0.05, 0), (0.3, 1), (0.55, 2), (0.8, 3)],
        "The headless test drives the real game loop with the J key and samples the value every frame, at "
        "thirty, sixty and a hundred and forty-four frames per second. Its first run failed four checks: a "
        "second hit can't land during hurt in real play, and time scale doesn't slow the fight. Jow-hway "
        "revised the brief, not the assertions. Now sixty-nine pass at every rate.", 22,
        "Source: logs/test_hurt_flash_*fps.log; CHANGE-BRIEF.md Revisions 6-7",
        show4("first run and revised run side by side", ["Loop", "First", "Revised", "Now"])))

    beats.append(figure_beat("B10", "TESTS", "fig_mutations.png", "Break It On Purpose",
        "HEADLESS · each mutation made by Zhaohui, then restored", "recorded output of each run",
        cards4(("Semicolon", "empty list"), ("Rename", "still parses"), ("23 checks", "still passed"),
               ("source_color", "1 of 96 fails")),
        [(0.05, 0), (0.3, 1), (0.5, 2), (0.8, 3)],
        "Then Jow-hway broke the shaders on purpose. A missing semicolon: the uniform list comes back empty. "
        "A renamed uniform still parses, and all twenty-three behaviour checks still pass, because setting a "
        "name the shader doesn't have raises no error. Only the uniform list noticed. Deleting source colour "
        "fails the material test.", 20,
        "Source: logs/mutation1_semicolon_60fps.log, mutation2_rename_60fps.log, mutation3_source_color_60fps.log",
        show4("three mutations with what caught each", ["Semicolon", "Rename", "23 checks", "source_color"])))

    beats.append(code_beat("B11", "shaders/granite.gdshader", 1, 23, "A Texture Is Numbers",
        "Now a texture. Why is it information, not a picture? Lines three to five are three files of numbers. "
        "Line three says source colour: these numbers are colour, so they get decoded first. Line four has no such hint: "
        "roughness, read as stored. Line five marks a normal map. The uniforms below are Inspector controls, "
        "in two groups.", 20,
        [{"label": "Line 3", "value": "colour: source_color"},
         {"label": "Lines 4-5", "value": "data: roughness, normal"},
         {"label": "Groups", "value": "surface, detail"}],
        [(0.05, 3, "albedo: read as colour"), (0.4, 4, "roughness: read as data"),
         (0.55, 5, "normal map: hint_normal"), (0.78, 7, "Inspector groups")],
        ["godot/shaders/granite.gdshader", "typed by hand by Zhaohui (25e6dd8)"], "typed by Zhaohui"))

    beats.append(figure_beat("B12", "RESULT", "fig_materials.png", "One Shader, Two Materials",
        "OBSERVED · prop room, in-engine captures", "as saved · one value changed in memory",
        cards4(("Floor", "uv 6.0, white"), ("Plinth", "uv 1.0, #6E6680"), ("One value", "only floor changed"),
               ("Eyes", "looks like planks")),
        [(0.05, 0), (0.25, 1), (0.5, 2), (0.78, 3)],
        "Two materials share that shader: the floor at UV scale six, the plinth at one, tinted the A3 stone "
        "colour. Change one value in one material, and only the floor changes. Edit one shader line, Jow-hway "
        "checked, and both change. And Jow-hway's verdict on the granite: it looks like wooden planks. The box "
        "UVs stretch it.", 20,
        "Source: capture/evidence/a5/granite_materials.png, granite_one_material_changed.png; godot/MATERIALS.md",
        show4("the two captures side by side", ["Floor", "Plinth", "One value", "Eyes"]), evidence=True, still=True))

    beats.append(figure_beat("B13", "SWEEP", "fig_sweep.png", "Each Control To Its Ends",
        "OBSERVED · floor material, one uniform at a time, in memory", "six engine stills, cropped to the floor",
        cards4(("uv_scale", "grain size"), ("roughness", "light on it"), ("normal", "relief"), ("tint black", "breaks it")),
        [(0.05, 0), (0.3, 1), (0.5, 2), (0.78, 3)],
        "Each uniform swept to its ends. UV scale changes the grain; roughness and normal strength change how "
        "the light sits on it; and tint at black, Jow-hway said, isn't good-looking.", 13,
        "Source: capture/evidence/a5/granite_sweep_*.png; TEST-REPORT.md A5 interface sweep",
        show4("six sweep stills", ["uv_scale", "roughness", "normal", "tint black"]), still=True))

    beats.append(code_beat("B14", "shaders/hint_experiment.gdshader", 1, 15, "Same File, Two Hints",
        "The hint experiment asks what a hint does to the number the shader receives. One three-pixel file: "
        "greys sixty-four, one twenty-eight and one ninety-two. Line four reads it with source colour, line "
        "five without. The true-or-false switch on line seven picks which one writes albedo, on an unshaded quad.", 18,
        [{"label": "Line 2", "value": "unshaded: no light"},
         {"label": "Lines 4-5", "value": "one file, two hints"},
         {"label": "Line 7", "value": "picks the sampler"}],
        [(0.05, 2, "unshaded"), (0.35, 4, "with source_color"), (0.55, 5, "without"),
         (0.78, 7, "read_as_color picks one")],
        ["godot/shaders/hint_experiment.gdshader", "typed by hand by Zhaohui (e6c40a6)"], "typed by Zhaohui"))

    beats.append(figure_beat("B15", "RESULT", "fig_hint.png", "Predicted 137, Measured 64",
        "OBSERVED · hint_experiment.tscn, in-engine capture", "quad A above, quad B below",
        cards4(("Predicted B", "137 / 188 / 224"), ("Measured", "64 / 128 / 192"), ("Not", "the shared texture"),
               ("Why", "every ALBEDO decoded")),
        [(0.05, 0), (0.3, 1), (0.5, 2), (0.75, 3)],
        "Jow-hway predicted quad B would brighten, to one thirty-seven, one eighty-eight and two twenty-four. "
        "Both quads show the stored values. In Godot's Compatibility renderer, every albedo is decoded, "
        "whatever the hint, then encoded on output. The prediction followed the Forward-plus pipeline. This "
        "project had to measure first.", 20,
        "Source: capture/evidence/a5/hint_experiment.png; Godot 4.7.2 drivers/gles3/shaders/scene.glsl:2398, 2798",
        show4("capture beside the predicted and measured table", ["Predicted B", "Measured", "Not", "Why"]),
        evidence=True, still=True))

    beats.append(figure_beat("B16", "LANGUAGE", "fig_generated.png", "What The Language Gives You",
        "SOURCE · standard_generated.gdshader (Godot) beside granite.gdshader (Zhaohui)", "two lines each, verbatim",
        cards4(("Type", "no main()"), ("Hints", "shape the Inspector"), ("Line 7", "same as line 3"),
               ("Line 19", "hint_roughness_normal")),
        [(0.05, 0), (0.3, 1), (0.52, 2), (0.78, 3)],
        "And what is the Godot shading language? Close to GLSL, but you pick a shader type instead of writing "
        "main, and hints shape the Inspector. Here's the shader Godot generated for a standard material, beside "
        "Jow-hway's. The albedo lines match. The normal map uses hint roughness normal, which in the editor "
        "also feeds the roughness import.", 20,
        "Source: godot/shaders/standard_generated.gdshader:7, 19; godot/shaders/granite.gdshader:3, 5; LANGUAGE-NOTES.md",
        show4("two pairs of lines", ["Type", "Hints", "Line 7", "Line 19"])))

    beats.append(figure_beat("B17", "HUMAN CHECK", "fig_limits.png", "What No Headless Run Shows",
        "HEADLESS vs HUMAN · TEST-REPORT.md A5", "Zhaohui's answers, verbatim",
        cards4(("Proves", "parse, drive, wire"), ("Cannot", "how it looks"), ("Eyes", "Zhaohui's checks"),
               ("Not done", "OS screenshot")),
        [(0.05, 0), (0.3, 1), (0.5, 2), (0.82, 3)],
        "So what did the tests prove? That the shaders parse, that their uniforms are declared and driven, and "
        "that the materials are wired, even from an empty cache. Not how anything looks. Those are Jow-hway's "
        "checks, in Jow-hway's words: the flash can be seen, the quads are alike, the granite looks like wood. "
        "The screenshot comparison wasn't done.", 21,
        "Source: TEST-REPORT.md A5 (human checks recorded 2026-10-29)",
        show4("proves and cannot, side by side", ["Proves", "Cannot", "Eyes", "Not done"])))

    beats.append(beat("B18", "VERDICT",
        "Verdict. Checked: sixty-nine checks at three frame rates, ninety-six material checks from an empty "
        "cache, three mutations that fail, and pixels within one step of the hand predictions. Uncertain: the "
        "retrigger is reachable only by test setup, and the screenshot comparison wasn't done. Claude got four "
        "things wrong: an outdated command line tool, null material values, captures sampled at the wrong "
        "scale, and a wrong claim about hint normal. Jow-hway typed every shader line, predicted, broke and "
        "judged them; Claude wrote the driver, the tests, the audit and the captures. Next step: a UV scale "
        "per axis, so the granite stops looking like planks.", 36,
        {"type": "GRAPHIC", "class": "SHOW", "source": "remotion", "motion": "artifact-lines",
         "show": [{"at": "0.05", "event": "verdict page opens"}, {"at": "0.12", "event": "line 1: checked"},
                  {"at": "0.3", "event": "line 2: uncertain"}, {"at": "0.45", "event": "line 3: Claude got wrong"},
                  {"at": "0.68", "event": "line 4: who did what"}, {"at": "0.88", "event": "line 5: source and next step"}],
         "remotion": {"pattern": "ClaudeVerdictArtifact", "props": {
             "artifactTitle": "Verdict", "artifactHeading": "Two shaders, measured", "brandLabel": HANDLE,
             "artifactLines": [
                 "Checked: 69/0 at 30, 60, 144 fps; 96/0 from an empty cache; 3 mutations exit 1; pixels within one step.",
                 "Uncertain: retrigger only by test setup; OS-screenshot comparison not done; granite reads as planks.",
                 "Claude got wrong: an old CLI; null material values; captures sampled at the wrong scale; hint_normal.",
                 "Zhaohui: every shader line, predictions, mutations, the looks. Claude: driver, tests, audit, captures.",
                 f"Source shown: {SOURCE_REV} (godot/). Granite: Poly Haven, CC0. Next: UV scale per axis."]}}}))

    beats.append(beat("B19", "HANDOFF",
        "Your turn. Paste this: Please use Walker to add one uniform to my shader's brief before I write it: "
        "its type, hint and default, the game state that sets it, and one pixel I predict by hand at three "
        "values. Then write a test that fails if I rename it in the shader only. Predict the pixel before you "
        "look. A test you've never seen fail hasn't told you anything yet. Liam, in for Bear.", 26,
        {"type": "GRAPHIC", "class": "SHOW", "source": "remotion", "motion": "type-on",
         "show": [{"at": "0.05", "event": "composer opens with greeting 'Your turn.'"},
                  {"at": "0.2", "event": "the prompt types in"}, {"at": "0.6", "event": "send button arms"},
                  {"at": "0.75", "event": "three RESULT lines land"}],
         "remotion": {"pattern": "ClaudeComposerAsk", "props": {
             "greeting": "Your turn.", "topic": "WALKER · YOUR UNIFORM", "segment": "Predict, Then Rename",
             "command": "Please use Walker to add one uniform to my shader's brief before I write it: its type, "
                        "hint and default, the game state that sets it, and one pixel I predict by hand at three "
                        "values. Then write a test that fails if I rename it in the shader only.",
             "runningText": "paste this into Claude…", "folderLabel": HANDLE,
             "modelLabel": "Claude", "effortLabel": "High",
             "output": ["Brief committed before the shader.", "Pixel predicted at three values.",
                        "Rename in the shader only: the test fails."], "animateTyping": True}}}))

    beats.append(beat("B20", "OUTRO", f"{TITLE}. At Nik Bear Brown.", 5,
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
        "topic": "Two hand-written Godot shaders and their materials: what the tests proved and what only eyes judged",
        "kind": "godot-gamedev", "mode": "walker", "brand": "claude-liam", "channel": HANDLE,
        "channel_title": "Nik Bear Brown", "folderLabel": HANDLE, "persona": "Liam", "presenter": "Liam",
        "in_for_bear": True, "greeting": "Ciao, Liam",
        "greeting_note": "hello lexicon: Ciao (Italian), as in the author's A3 reel.",
        "tts_respelling": "Narration respells names for Kokoro (checked with faster-whisper base.en): Jow-hway Lee / "
                          "Jow-hway = Zhaohui Li, Ah-kah-ken = Akaken, Ah-oh-tah-keh = Aotake; G L S L and U V are "
                          "spelled out. On-screen text always uses the real spellings.",
        "audience": "practitioners and makers following the channel's Claude workflows",
        "register": "Teardown", "engine": "kokoro", "voice": "am_onyx", "voice_kokoro": "am_onyx",
        "palette": "claude", "aspect_ratio": "16:9", "fps": 30, "captions": False,
        "game": {"name": PROJECT, "author": "Zhaohui Li", "source_revision": SOURCE_REV,
                 "godot": "4.7.2.stable.official.ed1daf0bf", "project": "godot/project.godot",
                 "renderer": "gl_compatibility",
                 "started_from": "the A2 2D game and the A3 prop room; A5 adds godot/shaders/, the driver, "
                                 "the granite and hint materials and their tests"},
        "teaching_contract": "code-then-result-v1",
        "note": "Engine footage is a real Movie Maker capture of an isolated copy with scripted input (labelled). "
                "Figure stills are tests/capture_a5.gd captures of the same copy at 1924 x 1082 (the window is "
                "clamped to the screen); labels and sample rings are the only new pixels."},
        "beats": beats}
    (REEL / "beat_sheet.json").write_text(json.dumps(sheet, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {len(beats)} beats; words: " +
          ", ".join(f"{b['beat_id']}:{len(b['narration_text'].split())}" for b in beats))


if __name__ == "__main__":
    build()
