# BUILD-PROMPT — rebuild the A8 pitch film end to end

Paste the block below into Claude Code from the repo root `walker-dusk-duel-zhaohui-li/`. The
Brutalist toolkit is at `D:\courses\7270\brutalist.art-main\brutalist.art-main`.

**Host setup (Windows, Git Bash for the tools; PowerShell for the windowed capture):**
- `export PYTHONUTF8=1`;
- a `python3` shim for Python 3.12 first on `PATH` (`D:\tmp\py3shim`);
- `G=~/Downloads/Godot_v4.7.2-stable_win64.exe/Godot_v4.7.2-stable_win64_console.exe`;
- `TEMP`/`TMP`/`TMPDIR` set to `D:\tmp\remotion` for Remotion and FFmpeg (`tools/render_queue.sh`
  sets them).

**Toolkit patch this build needs:**
- `runtime/remotion/src/scenes/GodotDesignFigure.tsx` and `GodotDevWorkbench.tsx` take
  `handle: z.string().default('@NikBearBrown')`, and their footer renders `{p.handle}` instead of
  the literal `@NikBearBrown`.
- The beat sheet passes `"handle": ""`, because the A8 handout forbids the instructor's credit line.

```text
Rebuild youtube/walker-dusk-duel-zhaohui-li-a8-pitch ("Dusk Duel: Final Project Pitch") from
repository revision dff6cba (godot/ unchanged since 8049c54). Do not edit godot/ (never godot/shaders/).
No paid calls, no publishing, no git push, no commit. Narration speaks as Zhaohui; no Liam, no
"in for Bear", no @NikBearBrown anywhere.
All paths are relative to the reel unless stated.

1. Capture (isolated copy, scripted input):
   - bash tools/make_capture_copy.sh; then "$G" --headless --path capture/game --import
   - Dry run: "$G" --headless --path capture/game --fixed-fps 60 --script res://capture_a8.gd
     > capture/dryrun2.log. It must end "capture done, frames 1938; round 2".
   - Windowed take, started by Zhaohui in PowerShell. Nobody touches keyboard or mouse until the
     window closes (4K renders slower than real time):
     cmd /c "%USERPROFILE%\Downloads\Godot_v4.7.2-stable_win64.exe\Godot_v4.7.2-stable_win64_console.exe
       --path capture/game --write-movie <ABSOLUTE>/capture/a8_round.avi --fixed-fps 60 --disable-vsync
       --resolution 3840x2160 --script res://capture_a8.gd > capture\a8_round.log 2>&1"
   - Accept the take only if diff <(grep "^tick\|^capture" capture/dryrun2.log)
     <(grep "^tick\|^capture" capture/a8_round.log) is empty.
2. bash tools/extract_stills.sh; python tools/build_figures.py; python tools/build_beatsheet.py
3. Audio: from the toolkit, python runtime/scripts/generate_audio_kokoro.py <reel>; then
   python tools/pad_audio.py and python tools/build_beatsheet.py. Read every clip back with
   python tools/transcribe.py; reword any line whose meaning is misheard.
4. Media: python tools/build_media.py (B01, B02, B06). Remotion beats:
   bash tools/render_queue.sh B00 B03 B04 B05 B07 B08 and B09 B10 B11 B12 B13 B14, as two queues
   started a minute apart (the script passes --force).
5. Evidence: python tools/build_evidence.py; python tools/build_shotlist.py;
   ./art godot-gamedev --check <reel> --game godot (must PASS).
6. Visual QC: python tools/contact_sheet.py; confirm no footer handle on any frame.
   GATE T on the reel: runtime/scripts/type_check.py <reel>.
   Masked GATE T: python tools/build_figures.py --masked; python tools/build_masked_typecheck.py;
   re-render B00 and B12 in _qc/typecheck-masked with --force; run type_check.py on it.
7. ./art final <reel> --height 2160 --fps 30 --out <reel>/exports/landscape. Record the SHA-256 of
   the .mp4.
```
