# BUILD-PROMPT — rebuild this film end to end

Paste into Claude Code from the repo root `walker-dusk-duel-zhaohui-li/`. The Brutalist toolkit is at
`D:\courses\7270\brutalist.art-main\brutalist.art-main`.

**Host setup (this Chinese-locale Windows machine, Git Bash):** `export PYTHONUTF8=1`; a `python3`
shim that runs Python 3.12 first on `PATH` (the Microsoft Store alias otherwise answers);
`GODOT=~/Downloads/Godot_v4.7.2-stable_win64.exe/Godot_v4.7.2-stable_win64_console.exe`;
`TEMP`/`TMP`/`TMPDIR` on `D:\tmp\remotion` for every Remotion render (C: is nearly full;
`tools/render_queue.sh` sets them).

```text
Rebuild youtube/claude-liam-walker-dusk-duel-zhaohui-li-a6-gamedev, a godot-gamedev walker film
("Dusk Duel, Sparked"), from source revision 840bcfd (godot/). Do not edit godot/ (never godot/shaders/).
No paid calls, no publishing, no git push, no commit.

1. Capture (isolated copy, scripted input):
   - bash tools/make_capture_copy.sh, then "$GODOT" --headless --path capture/game --import
   - "$GODOT" --path capture/game --write-movie <ABSOLUTE path>/capture/a6_play.avi --fixed-fps 60
     --disable-vsync --resolution 3840x2160 --script res://capture_a6.gd > capture/a6_play.log
     (must end "capture done, frames 1293; P1 health 100, P2 health 60, hits 18")
2. python tools/build_figures.py, then python tools/build_beatsheet.py.
3. Audio: from the toolkit, python runtime/scripts/generate_audio_kokoro.py <reel>; then
   python tools/pad_audio.py and python tools/build_beatsheet.py. Read every clip back with
   python tools/transcribe.py (faster-whisper base.en) and reword any misheard line.
4. Media: python tools/build_media.py (B02, B09, B15 from a6_play.avi). Remotion beats with
   bash tools/render_queue.sh <beats...> (one queue at a time is safest: parallel queues failed
   here); never rebuild beat_sheet.json while a render or the TTS generator is running.
5. Evidence: python tools/build_evidence.py; python tools/build_shotlist.py;
   ./art godot-gamedev --check <reel> --game godot (must PASS).
6. Visual QC on sampled frames of every beat; GATE T on the masked copy
   (python tools/build_figures.py --masked; python tools/build_masked_typecheck.py; render the
   STILL beats in _qc/typecheck-masked; runtime/scripts/type_check.py on it).
7. ./art final <reel> --height 2160 --fps 30 --out <reel>/exports/landscape. Record the SHA-256.
```
