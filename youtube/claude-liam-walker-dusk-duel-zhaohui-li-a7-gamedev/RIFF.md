# RIFF — observations behind the commentary

Times are seconds into `capture/a7_play.avi` (60 fps; movie frame n ≈ driver tick n + 1; events in `capture/a7_play.log`).

| Artifact + range | Visible observation | Interpretation (source) | Narration | Next experiment |
|---|---|---|---|---|
| capture 0–18.8 s (B02) | Title with both small flames flickering above the lit lantern windows; Enter at 6 s; Akaken walks in; two kicks with a pale arc at the shin sweeping up to the foot; a third kick freezes under PAUSED. | Lanterns run from the title because `lantern_flame.gd` plays on `_ready`; the arc is `KickRig`, positioned from `Fighter.frame`. | "both lanterns already burn … the pale arc beside the leg is clip two" | Capture with the HUD hint bar hidden, so the arc is less crowded. |
| capture 1.5–18.3 s, lantern crop (B06) | On the title Akaken's raised fist sits over the left lantern; once he walks right both flames are visible and out of step. | start_offset 0.4 on LanternRight; TUNING A7 r0 noted the hidden left lantern. | "Akaken's raised arm covers the left lantern … still open" | Move P1's start x in a copy to see whether the left flame should be moved instead. |
| ticks 556–606 at 1/8, then 606–… (B13) | The arc fades in faint, winds back, sweeps bright and fades; later the kick pauses at frame 10: the arc holds for 3 s while the right flame keeps changing. | `seek(frame/60)` on a frozen frame; idle-tick lantern. | "the arc freezes, and the lantern behind it keeps burning" | Pause during hitstop to check both freezes stack. |
| ticks 1020–1040, 1122–1142, 1230–1258 at 1/8, then 1005–… (B14) | Aotake's arc sweeps into Akaken; Akaken flashes red (A5 hurt flash), the A6 spark appears, and Akaken's arc is gone on the hit frame in each phase. | `receive_hit` → hurt; `kick_rig.gd` plays rest that tick (log: clip rest, vis false). | "on that same tick the arc is gone" | Interrupt by a real P2 input in a test instead of SETUP. |
| captures/kick_arc/r1 frames 10–24 (B10) | Faint wind-up at 10, bright crescent at 14, upright at 16, fading 17, gone 23–24. | Keys at the phase boundaries, r1 alpha 0.25. | "Frame ten, startup begins: a faint wind-up …" | — |
