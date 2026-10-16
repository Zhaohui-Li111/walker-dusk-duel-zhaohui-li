# SUBMISSION — Assignment 3

> Prepared by Claude Code from the repository records. Lines in quotation marks are Zhaohui's own
> words, translated from Chinese. The Assignment 2 submission note is kept unchanged in
> [SUBMISSION-A2.md](SUBMISSION-A2.md).

- **Assignment:** Assignment 3 - Your First 3D Game Assets with Claude, the Blender MCP, and Blender
- **Student:** Zhaohui Li
- **Project name:** walker-dusk-duel
- **GitHub repository URL:** https://github.com/Zhaohui-Li111/walker-dusk-duel-zhaohui-li
- **Git tag and submitted commit SHA:** tag `a3`. The commit SHA is the one the tag points at; it is
  entered in the Canvas note, because a file cannot contain its own commit hash. The source ZIP is
  `git archive` of that commit.
- **Game-source revision shown in the film:** `1e88b83`, the last commit that changed `godot/`.
  Later commits add documentation, the film source, the Blender code record and this note.
  `godot/` is unchanged since then; the clone check below confirms it.
- **Godot version, Blender version, and operating system:** Godot 4.7.2 stable (GL Compatibility) ·
  Blender 5.2.2 LTS · Windows 11 Home
- **The three assets and what each is for:**
  - **PROP-LANTERN**, a stone lantern, 0.60 × 0.60 × 1.40 m, 100 triangles. It frames the edge of
    the arena, like the courtyard lanterns in the background art.
  - **PROP-MAKIWARA**, a wooden striking post, 0.30 × 0.30 × 1.50 m, 92 triangles. It is Akaken's
    punching post, with the pad at fist height (1.20 m).
  - **PROP-TAIKO**, a taiko drum on a stand, 0.70 × 0.55 × 0.95 m, 168 triangles. It is the visible
    source of the taiko music loop.

  All three stand in `godot/props3d/prop_room.tscn` beside a 1.70 m reference box (Akaken's
  height). The room is not connected to the 2D game yet.
- **MCP project and version, or "script route":** the MCP route for all three assets:
  mcp-for-blender 2.1.9 (Blender add-on 1.8, protocol 13), registered in Claude Code. Asset
  libraries, generators and telemetry were all off. Every `execute_blender_code` body is kept
  verbatim in `tools/blender/build_*.py`.
- **My hand edit in Blender:** "I changed the drumhead's colour, with L and G", on the taiko in
  Edit Mode. What it taught me: "you can work with keyboard shortcuts."
  - **From the records:** the saved file shows the edit moved geometry. It changed no colour: it
    flattened the front drumhead and moved the drum body about 1.2 cm.
  - **The repair:** I asked Claude to repair it ("我不太会改，你改吧"). The repair is Claude's, and the
    body move was kept. Details are in BLENDER-NOTES.md, FRICTIONAL.md and TEST-REPORT.md.
- **Checks run (command and result):**
  - `timeout 120 godot --headless --path godot --script res://tests/check_props3d.gd --fixed-fps 60`:
    **49 checks, 0 failed**. It covers size ±0.02 m, node scale and rotation, the tallest axis, the
    gap to the floor, the footprint centre, the triangle budget and the albedo hex. The same check
    on a test copy with the taiko raised 0.05 m reports 1 failure, which shows the check can fail.
  - `godot --headless --path godot --script res://tests/test_runner.gd`: **94 checks, 0 failed**
    (the 2D game is unaffected).
  - **Blender side, per `.blend`:** `blender -b <file> --factory-startup --python-exit-code 1
    --python tools/blender/check_blend.py`. Re-running the builds headless with
    `tools/blender/reproduce.py` matches the committed files vertex for vertex. The exception is the
    hand edit, because it was done with the mouse.
  - **Human look check:** "I think they all look quite like what they're meant to be"; "I didn't
    find anything strange" from behind or below.
  - **Clone of tag `a3`:** see "Verification" below.
- **Final film URL and filename:**
  https://drive.google.com/file/d/1D2tbScAO8qrlzJBOb68VAFXHdIzu7u_f/view?usp=sharing ·
  `claude-liam-walker-dusk-duel-zhaohui-li-a3-gamedev.mp4` ("Dusk Duel, Measured", 5:22, 3840 × 2160)
- **Final film SHA-256:** `9331a6244a9c8e33ef414912a8e3d0a02cff78ce59994771401339ab61c771d2`. The Drive
  copy was downloaded without signing in and gives the same hash.
- **Summary of my changes:**
  - **In this assignment** (prepared by Claude Code from the commits):
    - a numbers-first brief committed before any mesh (`30513a4`);
    - three low-poly props built in Blender through the MCP;
    - GLB export into a small Godot 3D prop room;
    - a headless check against the brief, strengthened twice after tests showed what it missed;
    - interface notes, a hand edit, and the A3 film.
  - **My own view:** "I think they all look quite like what they're meant to be" and "I think
    rendering the video was the hardest part."
  - **Who did what in detail:** SOURCES.md "Who did what in A3" and FRICTIONAL.md.
- **Known limitations:**
  - The checks prove numbers, not looks. The human look check is one overall answer, not a report
    per prop.
  - The makiwara rope bands are chamfered rings rather than the brief's round cylinders.
  - The taiko stand is shallow (0.12 m) and looks tippy from the side.
  - There is no recording of the hand edit itself, only its saved result.
  - Claude built each prop in one call per prop, not one call per object as the course prompt asks.
  - The prop room is not connected to the 2D game.
  - Claude cannot listen to the film. Whisper misheard B17's sign-off, so the narration's sound was
    checked only by transcript.

  See README "A3 known limitations" and TEST-REPORT A3 "Honest limitations".
- **Changed games since Assignment 2:** no.

## Verification

TO BE FILLED by the clone check.
