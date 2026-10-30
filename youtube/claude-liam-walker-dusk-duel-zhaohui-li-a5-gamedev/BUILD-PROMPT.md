# BUILD-PROMPT — rebuild this film end to end

Paste into Claude Code from the repo root `walker-dusk-duel-zhaohui-li/`. The Brutalist toolkit is at
`D:\courses\7270\brutalist.art-main\brutalist.art-main`.

**Host setup (this Chinese-locale Windows machine):** set `PYTHONUTF8=1`; Godot is
`Downloads\Godot_v4.7.2-stable_win64.exe\Godot_v4.7.2-stable_win64_console.exe` (`$GODOT`).

```text
Rebuild youtube/claude-liam-walker-dusk-duel-zhaohui-li-a5-gamedev, a godot-gamedev walker film,
from source revision 043df17 (godot/). Do not edit godot/. No paid calls, no publishing, no git push.

1. Captures:
   - bash tools/make_capture_copy.sh, then "$GODOT" --headless --path capture/game --import
   - "$GODOT" --path capture/game --write-movie <absolute path>/capture/flash.avi --fixed-fps 60
     --disable-vsync --resolution 3840x2160 --script res://capture_flash.gd
     (must print "flash capture done, frames 900; P1 health 86, P2 health 92")
   - "$GODOT" --path capture/game --resolution 3840x2160 --script res://tests/capture_a5.gd
     > capture/capture_a5_4k.log   (stills land in capture/evidence/a5)
2. python tools/build_figures.py, then python tools/build_beatsheet.py.
3. Audio: from the toolkit, python runtime/scripts/generate_audio_kokoro.py <reel>. It regenerates
   every beat; then python tools/pad_audio.py and python tools/build_beatsheet.py. Transcribe every
   mp3 with faster-whisper base.en and read it back.
4. Media: python tools/build_media.py (B02 and B07 from flash.avi). Then the Remotion beats with
   tools/render_queue.sh (several queues in parallel are fine).
5. Evidence: python tools/build_evidence.py; ./art godot-gamedev --check <reel> --game godot (must PASS).
6. Review cut, visual QC on sampled frames, then ./art final <reel> --height 2160 --fps 30
   --out <reel>/exports/landscape. Record the MP4's SHA-256.
```
