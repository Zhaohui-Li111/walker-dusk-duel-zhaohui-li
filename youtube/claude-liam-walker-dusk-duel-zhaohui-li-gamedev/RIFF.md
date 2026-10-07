# RIFF — commentary grounded in the captures

Times are seconds into each beat's clip, checked on extracted frames.

| Artifact + time | Visible observation | Interpretation (source) | Narration | Next experiment |
|---|---|---|---|---|
| B02 `run-01` 15.00–27.39 s | Mid-round exchanges up to the K.O.; the sparks and health bars change on contact | Real engine run with scripted keyboard input, not a person (CAPTURE.md) | "Here's the slice … the sparks and the health bars are drawn by code." | Have a person play it and log where they mash. |
| B07 `punch_4k.png` | Akaken's feet on the ground-line tick; green hurtbox over the body; faint red hitbox over the wrapped fist; Aotake shows his kick image (no punch pose) | Boxes come from `poses.json`, the same skeleton that steered ControlNet (`fighter_art.gd` 32–44) | "…the red hitbox, faint because nothing is attacking yet, sits on the wrapped fist." | Overlay the hitbox on all 11 states and flag any that miss the limb. |
| B09 `run-01` 4.50–13.08 s, +0.45 s | Jab connects; spark at the overlap; Aotake's bar drops; he slides back | One `attack_resolved("hit")` (`fighter.gd` 160–172; driver log tick 297) | "Watch the fist. The jab connects…" | Count frames from key press to spark. |
| B12 `run-01` 2.40–11.66 s | +0.6 s jab misses; +1.4 s block spark, no bar change; +2.6 s hit spark, bar drops | Three different results, one sound each (`audio_director.gd` 100–108) | "Watch for three results…" | Mute and replay: are the three still distinct by sight? |
| B13 `run-01` 12.20–29.40 s, with audio | Pause overlay with the music ducked; whiff swish, hit thud and block clack under the loop; K.O. sound; the music stops on the K.O. card | The slice's own mix, recorded by Movie Maker (CAPTURE.md) | none, by design | Zhaohui to listen: does the block read as a forearm block? Is the master too hot (peaks at 0 dBFS)? |
| B15 `evidence/test-run.txt` | "94 checks, 0 failed"; "attacks 13 -> sounds {…}"; the muted and unmuted tuples are identical | A recorded run, not a claim (`test_runner.gd`) | "The recorded run: ninety-four checks…" | Add a test that fails when two sounds overlap above full scale. |

The B13 observations come from the frames and the scripted event log. Claude cannot listen, so
the audio itself is described by the events that trigger it and by its measured level
(max 0.0 dBFS, mean −15.3 dB), not by its sound.
