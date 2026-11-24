#!/usr/bin/env python3
"""Write beat_sheet.json for the A8 pitch film ("Dusk Duel: Final Project Pitch").

Adapted from the A7 reel's builder. Narration is Claude Code's script from Zhaohui's answers in
pitch/PROJECT-BRIEF.md (Version 1, Revisions 2-3), approved by Zhaohui 2026-11-23 ("批准，开始做"),
and speaks AS Zhaohui (first person). The A8 handout forbids the instructor's name, persona or credit
line, so there is no "Liam, in for Bear" and no @NikBearBrown outro card (OUTRO-LOCK not applied;
FRICTIONAL.md). Footage: capture/a8_round.avi (tools/capture_a8.gd, scripted input, 60 fps; movie
frame n shows the state after driver tick n + 1). Event times from capture/a8_round.log (= dry run):
Enter 4.0 s, fight 5.0 s, CPU blocks from 5.9 s, Aotake's kick hits 11.1 s, K.O. 21.3 s, result
22.8 s, rematch 25.3 s, round 2 fight 26.3 s (capture input stops; Aotake walks in and kicks),
end 32.3 s. Cue times are fractions of each beat's measured narration once mp3/beat-Bxx.mp3 exists.
"""
import base64
import json
import pathlib
import subprocess

REEL = pathlib.Path(__file__).resolve().parent.parent
REPO = REEL.parent.parent
GAME = REPO / "godot"
SLUG = REEL.name
TITLE = "Dusk Duel: Final Project Pitch"
SOURCE_REV = "dff6cba"            # HEAD when the film was built; godot/ unchanged since 8049c54
PROJECT = "walker-dusk-duel"
FIG = REEL / "figures"
OLD = json.loads((REEL / "beat_sheet.json").read_text(encoding="utf-8")) if (REEL / "beat_sheet.json").exists() else None
LABEL_PLAY = "REAL CAPTURE · scripted input · Godot 4.7.2 · rev dff6cba · Akaken's keys sent by a capture bot · Aotake = the game's own CPU"
PROPOSED = "CONSTRUCTED · PROPOSED — does not exist yet"


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
RESPELL = {"Zhaohui Li": "Jow-hway Lee", "Akaken": "Ah-kah-ken", "Aotake": "Ah-oh-tah-keh"}


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


def figure_beat(bid, act, image, title, status, label, cards, cue_fracs, narration, est, source, show,
                still=False, **extra):
    d = dur(bid, est)
    shot = {"type": "STILL" if still else "GRAPHIC", "class": "SHOW", "source": "remotion",
            "motion": "card-cues", "show": show,
            "remotion": {"pattern": "GodotDesignFigure", "props": {
                "title": title, "status": status, "image": data_uri(FIG / image), "imageLabel": label,
                "source": source, "cards": cards,
                "cues": [{"at": round(f * d, 2), "card": c} for f, c in cue_fracs],
                "durationSeconds": round(d + 0.2, 2), "handle": ""}},
            "figure": f"figures/{image}"}
    return beat(bid, act, narration, est, shot, **extra)


def footage_beat(bid, act, segments, narration, est, show, label_extra="", **extra):
    shot = {"type": "VIDEO", "class": "SHOW", "source": "capture", "motion": "none", "capture": "a8_round",
            "capture_file": "capture/a8_round.avi", "segments": segments, "show": show,
            "label": LABEL_PLAY + label_extra, "evidence_media": f"media/{bid}.mp4"}
    return beat(bid, act, narration, est, shot, **extra)


def code_beat(bid, rel, start, end, title, narration, est, notes, cue_fracs, output, author):
    d = dur(bid, est)
    code = excerpt(rel, start, end)
    cues = [{"at": round(f * d, 2), "line": line, "label": label} for f, line, label in cue_fracs]
    shot = {"type": "GRAPHIC", "class": "SHOW", "source": "remotion", "motion": "line-highlight",
            "show": [{"at": f"{f:.2f}", "event": f"line {line} highlights: {label}"} for f, line, label in cue_fracs],
            "remotion": {"pattern": "GodotDevWorkbench", "props": {
                "mode": "code", "title": title, "project": PROJECT, "path": f"res://{rel}",
                "source": f"Godot editor reconstruction · godot/{rel} lines {start}-{end} · source {SOURCE_REV} · {author}",
                "code": code, "startLine": start, "codeFontSize": 26,
                "inspectorLabel": "Source notes — not Inspector values",
                "notes": notes, "cues": cues, "output": output, "durationSeconds": round(d + 0.2, 2), "handle": ""}}}
    return beat(bid, "EXISTS", narration, est, shot, excerpt={"path": rel, "start_line": start, "end_line": end})


def cards(*pairs):
    return [{"label": a, "text": b} for a, b in pairs]


def show_cards(first, labels):
    fr = [0.05] + [round(0.05 + 0.85 * (i + 1) / len(labels), 2) for i in range(len(labels) - 1)]
    return [{"at": f"{fr[0]:.2f}", "event": f"{first}; {labels[0]} card lights"}] + \
           [{"at": f"{t:.2f}", "event": f"{lab} card lights"} for t, lab in zip(fr[1:], labels[1:])]


def cue(n):
    return [(round(0.05 + 0.85 * i / n, 2), i) for i in range(n)]


def build():
    B = []
    B.append(figure_beat("B00", "OPEN", "fig_title.png", "Dusk Duel",
        "PITCH · Zhaohui Li · CSYE 7270 Assignment 8", "the title screen, real capture",
        cards(("Game", "Dusk Duel"), ("Since", "Assignment 2"), ("Engine", "Godot 4.7.2")), cue(3),
        "I'm Zhaohui Li. This is the pitch for my final project: Dusk Duel, a small fighting game I have been "
        "building in Godot since Assignment 2.", 10,
        "Source: capture/a8_round.avi (title screen); README.md", show_cards("title card", ["Game", "Since", "Engine"]),
        still=True))

    B.append(footage_beat("B01", "WHAT", [{"start": 0.0, "speed": 1}],
        "My final project will take Dusk Duel to a complete, playable vertical slice that runs in a web browser: "
        "one stage, one player against a CPU opponent, from the title screen to the knockout and a rematch.", 14,
        [{"at": "0.05", "event": "title screen: DUSK DUEL, press Enter"},
         {"at": "0.3", "event": "Enter: ROUND 1 - FIGHT"},
         {"at": "0.4", "event": "Akaken walks in; the fight starts"}],
        role_note="Real Movie Maker capture of an isolated copy (capture/game, dff6cba), scripted input. This is "
                  "the desktop game as it is; the browser part of the sentence is a 'will'."))

    B.append(footage_beat("B02", "EXISTS", [{"start": 17.0, "end": 23.5, "speed": 1}, {"start": 23.5, "speed": 1}],
        "Much of that loop already exists. Today the game starts on a title screen, runs a full round against a "
        "CPU opponent, ends on a K.O., and offers a rematch. All of this runs on desktop now.", 15,
        [{"at": "0.05", "event": "late round 1: punches, blocks, Aotake's health low"},
         {"at": "0.3", "event": "K.O.: Aotake falls"},
         {"at": "0.45", "event": "result screen: AKAKEN WINS, Enter: rematch"},
         {"at": "0.75", "event": "Enter: ROUND 2 - FIGHT"}],
        role_note="Same capture: K.O. at 21.3 s, result 22.8 s, rematch 25.3 s, round 2 at 26.3 s."))

    B.append(figure_beat("B03", "NEW", "fig_new.png", "What Will Be New",
        "PROPOSED · PROJECT-BRIEF.md Revision 3, question 1", PROPOSED,
        cards(("Web build", "a full match in Edge"), ("Stronger CPU", "adjustable difficulty"),
              ("Wider tests", "a report anyone can re-run")), cue(3),
        "What will be new is three things: a web build, a stronger CPU opponent with adjustable difficulty, and "
        "wider tests, with a test report a stranger can re-run.", 11,
        "Source: pitch/PROJECT-BRIEF.md, Revisions 2 and 3", show_cards("three proposed cards",
        ["Web build", "Stronger CPU", "Wider tests"]), still=True))

    B.append(figure_beat("B04", "DIFFERENT", "fig_compare.png", "Smaller, On Purpose",
        "COMPARABLE · The King of Fighters '97, played by Zhaohui · named only, no images", "comparison; browser half proposed",
        cards(("KOF '97", "fast combat, timing, defence"), ("Dusk Duel", "one complete match"),
              ("Will", "no install, no setup")), cue(3),
        "My reference is The King of Fighters '97, which I played. I like its fast combat, attack timing and "
        "defence. Dusk Duel takes a smaller approach: one complete single-player match, for someone who wants a "
        "quick fight without installing a large game, finding an online opponent, or going through setup.", 20,
        "Source: pitch/PROJECT-BRIEF.md Revision 2 question 3, Revision 3 item 1",
        show_cards("two-column comparison", ["KOF '97", "Dusk Duel", "Will"]), still=True))

    B.append(code_beat("B05", "fighter/cpu_controller.gd", 49, 59, "The CPU Today",
        "Here's the CPU today, in cpu controller dot G D. On line fifty, if I attack close by, it often blocks. "
        "Line fifty-three: out of kick range, it walks in. Line fifty-five: too close, it steps back. Line "
        "fifty-seven: in range, it kicks. It makes a new decision every ten ticks.", 18,
        [{"label": "Re-decides", "value": "every 10 ticks (REACTION)"},
         {"label": "Block", "value": "55 % of close attacks"},
         {"label": "Kick", "value": "50 %, then a 40-tick cooldown"}],
        [(0.12, 50, "opponent attacking and close: block"), (0.38, 53, "out of kick range: walk in"),
         (0.58, 55, "too close: step back"), (0.78, 57, "in range, cooled down: kick")],
        ["godot/fighter/cpu_controller.gd", "Claude Code, A2 slice step 2 (6317281)"],
        "the CPU that exists today; commit 6317281"))

    B.append(footage_beat("B06", "EXISTS", [{"start": 6.0, "end": 14.0, "speed": 1}, {"start": 26.0, "speed": 1}],
        "And here it is in the capture. Aotake blocks Akaken's punches, then kicks. In round two the capture stops "
        "sending keys, so Aotake walks in and kicks a standing Akaken. Next, I want its choices to be more "
        "deliberate, not just more frequent.", 16,
        [{"at": "0.05", "event": "Aotake blocks Akaken's punches (BLOCKED)"},
         {"at": "0.2", "event": "Aotake's kick hits Akaken"},
         {"at": "0.3", "event": "cut to round 2: Akaken stands, Aotake walks in"},
         {"at": "0.6", "event": "Aotake kicks the standing Akaken"}],
        role_note="Real capture, two segments: 6.0-14.0 s (blocks at 10.1, 10.6 s; Aotake's kick hits at 11.1 s) "
                  "and round 2 from 26.0 s, where the capture bot sends nothing."))

    B.append(figure_beat("B07", "WHO", "fig_sixty.png", "The First Sixty Seconds",
        "PROPOSED · role: gameplay programmer · reader: technical lead or recruiter", PROPOSED,
        cards(("Role", "gameplay programmer"), ("Reader", "tech lead, recruiter"), ("60 s", "Enter, fight, K.O.")),
        cue(3),
        "I'm aiming at gameplay programmer roles. The reader is a technical lead or a recruiter. In the first sixty "
        "seconds they should open the page, press Enter, fight a round, and see the K.O. and the rematch, without "
        "reading any code.", 16,
        "Source: pitch/PROJECT-BRIEF.md question 2, Revision 3 item 3",
        show_cards("proposed 60-second timeline", ["Role", "Reader", "60 s"]), still=True))

    B.append(figure_beat("B08", "PROVES", "fig_tests.png", "Behind The Game",
        "RECORDED OUTPUT · headless tests, logs in the repo · tags a5, a6, a7", "real test logs",
        cards(("Shaders", "a5"), ("Particles", "a6"), ("Animation", "a7"), ("Round", "94 / 0")), cue(4),
        "Behind the game is the evidence. Shaders and materials from Assignment 5, particle effects from "
        "Assignment 6, animation clips from Assignment 7, each with headless tests. The round itself is pinned by "
        "ninety-four checks, all passing.", 18,
        "Source: logs/test_runner_60fps.log:24, test_hurt_flash, test_hit_spark_state, test_embers_state, "
        "test_kick_edges, test_pins_a7 (60 fps logs); SUBMISSION.md (A7)",
        show_cards("six real log lines", ["Shaders", "Particles", "Animation", "Round"]), still=True))

    B.append(figure_beat("B09", "PROVES", "fig_gpu.png", "Measured, Not Felt",
        "RECORDED OUTPUT · A6 GPU price, Intel UHD Graphics, 2026-11-08", "real measurement",
        cards(("Machine", "Intel UHD, OpenGL 3.3"), ("Hit sparks", "+0.012 ms"), ("Next", "desktop vs browser")),
        cue(3),
        "I have measured cost before. On this laptop's Intel UHD Graphics, the hit sparks added about a hundredth "
        "of a millisecond of GPU time. I will measure desktop against the browser the same way.", 13,
        "Source: TEST-REPORT.md “GPU price”; logs/gpu_price_windowed.log; godot/tests/gpu_price.gd",
        show_cards("the A6 table", ["Machine", "Hit sparks", "Next"]), still=True))

    B.append(figure_beat("B10", "OUT", "fig_out.png", "Deliberately Out",
        "SCOPE · PROJECT-BRIEF.md question 4", "what the project will not do",
        cards(("No", "online play"), ("One", "stage only"), ("No", "saves")), cue(3),
        "What it will not do: no online play, one stage only, no character select, no saves, and no big roster.", 9,
        "Source: pitch/PROJECT-BRIEF.md question 4", show_cards("struck-through list", ["No", "One", "No"]),
        still=True))

    B.append(figure_beat("B11", "FIRST", "fig_milestone.png", "Milestone 1",
        "PROPOSED · PROJECT-BRIEF.md Revision 2 question 5, Revision 3 item 2", PROPOSED,
        cards(("Where", "this laptop, Edge"), ("Checks", "seven criteria"), ("Proof", "recording + report")), cue(3),
        "The first new piece is milestone one: a full match in a web browser. I will check it on this machine, in "
        "Microsoft Edge. The game loads, I start from the title, the CPU approaches, attacks and blocks, the effects "
        "draw, the round reaches the K.O., and a rematch plays. A recording and a test report will show it ran.", 22,
        "Source: pitch/PROJECT-BRIEF.md Revision 2 question 5; Revision 3 item 2",
        show_cards("unticked checklist", ["Where", "Checks", "Proof"]), still=True))

    B.append(figure_beat("B12", "RISK", "fig_risk.png", "What Could Sink It",
        "RISK · PROJECT-BRIEF.md question 6", "left: real capture · right: constructed, proposed",
        cards(("Risk", "web differs from desktop"), ("First", "export early"), ("Fallback", "simpler effect")),
        cue(3),
        "The risk is that the web build looks or runs differently from desktop: shader colour, particle blending, "
        "frame rate. So the web export comes first, not last. I will compare both in the same scene, and give any "
        "effect that fails a simpler fallback.", 16,
        "Source: pitch/PROJECT-BRIEF.md question 6; capture/a8_round.avi",
        show_cards("desktop vs empty browser frame", ["Risk", "First", "Fallback"]), still=True))

    B.append(figure_beat("B13", "WHY", "fig_why.png", "Why This Project",
        "WHY · PROJECT-BRIEF.md Revision 2 question 7", "existing skills with tags; new skills",
        cards(("Have", "a5 · a6 · a7"), ("New", "CPU, web, benchmarks, tests")), cue(2),
        "Why this project? Shaders, particles, animation and tests are skills I already have, and each has a tagged "
        "assignment behind it. What is new to me is a smarter CPU opponent, shipping a Godot game to the web, "
        "repeatable benchmarks, and wider gameplay tests.", 17,
        "Source: pitch/PROJECT-BRIEF.md Revision 2 question 7; tags a5, a6, a7; commit 6317281",
        show_cards("two columns", ["Have", "New"]), still=True))

    B.append(figure_beat("B14", "CLOSE", "fig_end.png", "Dusk Duel",
        "END · Zhaohui Li · CSYE 7270 · Fall 2026", "end card",
        cards(("Open", "in a browser"), ("Play", "one match"), ("Verify", "tests anyone can run")), cue(3),
        "Dusk Duel: a fighting game a stranger can open, play and verify. Godot 4.7.2, Compatibility renderer, "
        "exported to the web.", 9,
        "Source: pitch/PROJECT-BRIEF.md", show_cards("end card", ["Open", "Play", "Verify"]), still=True,
        tail_hold_s=1.0))

    for b in B:
        m = measured(b["beat_id"])
        if m:
            b["actual_duration_s"] = round(m, 2)
            b["audio_file"] = f"mp3/beat-{b['beat_id']}.mp3"
    sheet = {"metadata": {
        "title": TITLE, "slug": SLUG,
        "topic": "Final project pitch: Dusk Duel taken to a playable web vertical slice with a stronger CPU and "
                 "re-runnable tests",
        "kind": "pitch", "mode": "walker", "brand": "student-pitch", "persona": "Zhaohui Li (AI voice)",
        "presenter": "Zhaohui Li", "in_for_bear": False,
        "voice_note": "Local Kokoro am_onyx speaks as Zhaohui in the first person (A8 allows AI narration that "
                      "speaks as the student). No instructor name, persona, handle or credit line (A8 rule); the "
                      "toolkit's claude-liam outro lock is therefore not applied.",
        "tts_respelling": "Narration respells Zhaohui Li as Jow-hway Lee, Akaken and Aotake phonetically for Kokoro. "
                          "On-screen text always uses the real spellings.",
        "audience": "a studio technical lead or recruiter; the course staff",
        "register": "plain pitch", "engine": "kokoro", "voice": "am_onyx", "voice_kokoro": "am_onyx",
        "palette": "claude", "aspect_ratio": "16:9", "fps": 30, "captions": False,
        "game": {"name": PROJECT, "author": "Zhaohui Li", "source_revision": SOURCE_REV,
                 "godot": "4.7.2.stable.official.ed1daf0bf", "project": "godot/project.godot",
                 "renderer": "gl_compatibility",
                 "started_from": "the game as tagged a7 (godot/ unchanged since 8049c54); nothing in the game is "
                                 "changed for the pitch"},
        "teaching_contract": "code-then-result-v1",
        "honesty": "Past tense only for what exists and is shown. Gameplay is a real Movie Maker capture with "
                   "scripted input (labelled on every frame). Everything that does not exist is on a panel stamped "
                   "CONSTRUCTED · PROPOSED. No King of Fighters imagery; no Claude response is shown."},
        "beats": B}
    (REEL / "beat_sheet.json").write_text(json.dumps(sheet, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    words = sum(len(b["narration_text"].split()) for b in B)
    print(f"wrote {len(B)} beats, {words} words")


if __name__ == "__main__":
    build()
