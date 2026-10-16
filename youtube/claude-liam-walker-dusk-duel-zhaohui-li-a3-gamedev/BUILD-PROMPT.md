# BUILD-PROMPT — rebuild this film end to end

Paste into Claude Code from the repo root `walker-dusk-duel-zhaohui-li/`. The Brutalist toolkit is at
`D:\courses\7270\brutalist.art-main\brutalist.art-main`.

**Host setup (this Chinese-locale Windows machine):**
- Set `PYTHONUTF8=1`.
- Put a `python3` shim that runs the real Python 3.12 first on `PATH`. The Microsoft Store alias
  answers `python3` otherwise.
- Godot is `Downloads\Godot_v4.7.2-stable_win64.exe\Godot_v4.7.2-stable_win64_console.exe`.

```text
Rebuild youtube/claude-liam-walker-dusk-duel-zhaohui-li-a3-gamedev, a godot-gamedev walker film, from
source revision 1e88b83 (godot/). Do not edit godot/ or blender/. No paid calls, no publishing, no git push.

1. Captures:
   - bash tools/make_capture_copy.sh, then godot --headless --path capture/game --import and the same
     for capture/game-raised.
   - godot --path capture/game --write-movie capture/orbit.avi --fixed-fps 60 --disable-vsync
     --resolution 3840x2160 --script res://capture_orbit.gd   (must print "orbit done, frames 1440")
   - godot --path capture/game --resolution 3840x2160 --script res://capture_stills.gd -- <reel>\capture\stills real
     and the same on capture/game-raised with prefix raised.
2. Check records:
   - timeout 120 godot --headless --path godot --script res://tests/check_props3d.gd --fixed-fps 60
     > evidence/check-props3d.txt; require "49 checks, 0 failed".
   - The same on capture/game-raised > evidence/check-props3d-raised-copy.txt; require
     "FAIL: sits on the floor (gap 0.0500)".
3. python tools/build_figures.py, then python tools/build_beatsheet.py.
4. Audio:
   - From the toolkit: python runtime/scripts/generate_audio_kokoro.py <reel>
   - Delete mp3/raw first if re-voicing. Then python tools/pad_audio.py and python tools/build_beatsheet.py.
   - Transcribe every mp3 with faster-whisper base.en and read it back.
5. Media:
   - python tools/build_media.py (B02 and B08 from orbit.avi).
   - From the toolkit: python runtime/scripts/remotion_scenes.py <reel> --only Bxx for each Remotion
     beat. It renders at --concurrency=1, about 30 min per beat on this machine. Separate --only queues
     can run in parallel, because they only race on the "rendered" stamps.
6. Evidence:
   - python tools/build_evidence.py
   - ./art godot-gamedev --check <reel> --game godot (must PASS)
7. GATE T on the reel, plus the masked copy: python tools/build_figures.py --masked, then
   python tools/build_masked_typecheck.py; re-render the STILL beats it names inside
   _qc/typecheck-masked, then run type_check.py on it.
8. Review cut: ./art run <reel>. Visual QC: sample frames at 2 fps plus each beat at 15/50/85 %,
   READ them, and log the result in _qc/REPORT.md. Fix the root cause and re-render until there
   are no BLOCKER or MAJOR defects.
9. Final: ./art final <reel> --height 2160 --fps 30 --out <reel>/exports/landscape
   Record the MP4's SHA-256.
10. Report: the absolute path of the MP4, the SHA-256, component coverage and limitations.
```
