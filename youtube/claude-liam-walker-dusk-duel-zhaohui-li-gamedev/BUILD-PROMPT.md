# BUILD-PROMPT — rebuild this film end to end

Paste into Claude Code from the repo root `walker-dusk-duel-zhaohui-li/`. The Brutalist toolkit is
at `D:\courses\7270\brutalist.art-main\brutalist.art-main`. Set `PYTHONUTF8=1` on this
Chinese-locale Windows host.

```text
Rebuild youtube/claude-liam-walker-dusk-duel-zhaohui-li-gamedev, a godot-gamedev walker film, from
source revision 4e0cf14. Do not edit godot/. No paid calls, no publishing, no git push.

1. Captures:
   - bash tools/make_capture_copy.sh
   - Probe headless: godot --headless --path capture/game --fixed-fps 60, and require
     run-01-driver.json "all_passed": true.
   - Record: godot --path capture/game --resolution 3840x2160 --write-movie capture/run-01.avi
     --fixed-fps 60 --disable-vsync
   - Re-make capture/game-states and record states-run.avi. Extract frame 6 to
     capture/evidence/states/punch_4k.png.
   - Extract frames at the logged ticks and confirm tools/windows.json still matches.
2. Test record: godot --headless --path godot --script res://tests/test_runner.gd >
   evidence/test-run.txt, and require "94 checks, 0 failed".
3. python tools/build_figures.py, then python tools/build_beatsheet.py.
4. Audio:
   - From the toolkit: python runtime/scripts/generate_audio_kokoro.py <reel>
   - python tools/pad_audio.py, then python tools/build_beatsheet.py
   - Transcribe every mp3 with faster-whisper and read it back.
5. Media:
   - python tools/build_media.py
   - From the toolkit: python runtime/scripts/remotion_scenes.py <reel> --force
6. Evidence:
   - python tools/build_evidence.py
   - ./art godot-gamedev --check <reel> --game godot (must PASS)
7. Review cut: ./art run <reel>. Visual QC: sample frames at 2 fps plus each beat at 15/50/85 %,
   READ them, and log the result in _qc/REPORT.md. Fix the root cause and re-render until there
   are no BLOCKER or MAJOR defects.
8. Final: ./art final <reel> --height 2160 --fps 30 --out <reel>/exports/landscape
   - Watch and listen to the master. B13 must carry the slice's own audio with no narration.
   - Record its SHA-256.
9. Report: the absolute path of the MP4, the SHA-256, component coverage and limitations.
```
