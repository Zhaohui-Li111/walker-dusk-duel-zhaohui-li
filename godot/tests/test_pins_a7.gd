extends SceneTree
## A7 step 2: behaviour pins, written before any A7 clip exists. They pass on the game as it is and
## must still pass after the clips are wired (CHANGE-BRIEF.md, "Boundaries": the state machine and
## its timings do not change, so no pin is predicted to change). Run from the repo root:
##   scripts/run-test.sh test_pins_a7.gd 60
## Like test_hurt_flash.gd, main's _physics_process stays on and P1 is driven by key events through
## Input.parse_input_event, which reaches PlayerController (Input.is_action_*) and main's
## _unhandled_input (pause). Input.action_press is never used.
## The only setup write is the A5 harness's: P2's controller is set to null when the round starts,
## so Aotake stands still and the run is deterministic. It is printed as HARNESS.
##
## Pins:
##   1  the state sequence of one scripted run, in order (walk, kick, punch, jump, crouch, block)
##   2  the timings the state machine already has: kick 28 ticks, punch 18, whiff on kick frame 13
##      and punch frame 9, the jump's measured airtime
##   3  the gameplay fact the kick arc is read against: a kick in range hits on its frame 8 (the
##      first active frame); hitstop holds P1's frame for 4 ticks; the kick ends 28 + 4 ticks after
##      it started
##   4  the game's pause during a kick freezes P1's state and frame; the kick ends 28 ticks of
##      unpaused play after it started
## A TickLog node records P1's state and frame once per physics tick, after main has stepped.

const HOLD_TICKS := 3
const WALL_LIMIT_MS := 100000
const KICK_TICKS := 28               # fighter.gd ATTACKS.kick 7 + 5 + 16
const PUNCH_TICKS := 18              # 4 + 4 + 10
const KICK_FIRST_ACTIVE := 8         # check_hit(): 7 < frame <= 12
const KICK_WHIFF_FRAME := 13         # frame > startup + active
const PUNCH_WHIFF_FRAME := 9
const HITSTOP := 4                   # main.gd HITSTOP_FRAMES
const JUMP_TICKS := 42               # measured by this test's first run, 2026-11-22 (a guessed 44
                                     # failed: 42); pinned as found

var checks := 0
var failures := 0
var main: Node
var ticklog: TickLog
var states := []                     # P1 state_changed: [tick, state]
var results := []                    # P1 attack_resolved: [tick, kind, result]
var started_ms := 0
var finished := false


class TickLog extends Node:
	var main: Node
	var recording := false
	var ticks := {}                  # physics tick -> {state, frame, hitstop, paused, p2}
	var last_tick := -1

	func _ready() -> void:
		process_physics_priority = 1000

	func _physics_process(_delta: float) -> void:
		if not (recording and is_instance_valid(main)):
			return
		last_tick = Engine.get_physics_frames()
		ticks[last_tick] = {"state": main.p1.state, "frame": main.p1.frame,
				"hitstop": main.hitstop, "paused": main.paused, "p2": main.p2.state}


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	started_ms = Time.get_ticks_msec()
	ticklog = TickLog.new()
	root.add_child(ticklog)
	print("A7 pins: Godot %s, %d physics ticks/s; headless, nothing is drawn" % [
		Engine.get_version_info().string, ProjectSettings.get_setting("physics/common/physics_ticks_per_second")])
	if not await start_fight():
		finish()
		return
	await pin_sequence()
	await pin_active_window()
	await pin_pause()
	finish()


func start_fight() -> bool:
	main = load("res://game/main.tscn").instantiate()
	main.round_started.connect(func(_n): main.p2.controller = null)
	root.add_child(main)
	ticklog.main = main
	main.p1.state_changed.connect(func(_f, s): states.append([Engine.get_physics_frames(), s]))
	main.p1.attack_resolved.connect(func(_f, kind, result, _p):
		results.append([Engine.get_physics_frames(), kind, result]))
	await process_frame
	check(main.is_physics_processing() and main.p1.controller is PlayerController, "harness",
			"main's _physics_process is on and P1 is driven by its PlayerController")
	await tap(KEY_ENTER, "Enter (title)")
	var ok := await wait_until(func(): return main.phase == "fight", 240)
	check(ok, "harness", "Enter on the title started round 1 and the intro ran into the fight (phase %s)" % main.phase)
	print("    HARNESS (writes no fight state): P2's controller set to null when the round starts")
	ticklog.recording = true
	await wait_ticks(5)
	states.clear()
	results.clear()
	return ok


## Pin 1 and 2: one scripted run, P2 far away, so every attack whiffs.
func pin_sequence() -> void:
	print("\n== pin 1-2: scripted run (P1 x %.0f, P2 x %.0f) ==" % [main.p1.position.x, main.p2.position.x])
	await wait_ticks(10)
	await hold(KEY_D, 20, "D (walk right)")
	await wait_ticks(10)
	var k0 := await tap_and_find(KEY_K, "K (kick)", "kick")
	await wait_until(func(): return main.p1.state == "idle", 60)
	await wait_ticks(5)
	var p0 := await tap_and_find(KEY_J, "J (punch)", "punch")
	await wait_until(func(): return main.p1.state == "idle", 60)
	await wait_ticks(5)
	var j0 := await tap_and_find(KEY_W, "W (jump)", "jump")
	await wait_until(func(): return main.p1.state == "idle", 120)
	await wait_ticks(5)
	await hold(KEY_S, 10, "S (crouch)")
	await wait_ticks(5)
	await hold(KEY_L, 10, "L (block)")
	await wait_ticks(5)

	var seq := states.map(func(s): return s[1])
	print("    P1 states in order: %s" % [seq])
	check(seq == ["walk", "idle", "kick", "idle", "punch", "idle", "jump", "idle", "crouch", "idle", "block", "idle"],
			"1", "state sequence walk idle kick idle punch idle jump idle crouch idle block idle")
	check(k0 >= 0 and after(k0, "kick") - k0 == KICK_TICKS, "2",
			"kick lasts %d ticks (got %d)" % [KICK_TICKS, after(k0, "kick") - k0])
	check(p0 >= 0 and after(p0, "punch") - p0 == PUNCH_TICKS, "2",
			"punch lasts %d ticks (got %d)" % [PUNCH_TICKS, after(p0, "punch") - p0])
	check(j0 >= 0 and after(j0, "jump") - j0 == JUMP_TICKS, "2",
			"jump airtime %d ticks (got %d)" % [JUMP_TICKS, after(j0, "jump") - j0])
	var kw := result_after(k0, "kick")
	var pw := result_after(p0, "punch")
	check(kw.size() > 0 and kw[2] == "whiff" and kw[0] - k0 == KICK_WHIFF_FRAME, "2",
			"out of range, the kick whiffs on its frame %d (got %s)" % [KICK_WHIFF_FRAME, rel(kw, k0)])
	check(pw.size() > 0 and pw[2] == "whiff" and pw[0] - p0 == PUNCH_WHIFF_FRAME, "2",
			"out of range, the punch whiffs on its frame %d (got %s)" % [PUNCH_WHIFF_FRAME, rel(pw, p0)])
	check(frames_ok(k0, KICK_TICKS), "2", "during the kick P1.frame counts 0, 1, ... 27, one per tick")


## Pin 3: a kick in range hits on frame 8; hitstop holds the frame; the kick ends at 28 + 4.
func pin_active_window() -> void:
	var gap: float = main.p1.reach("kick") + main.p2.body_half_width() - 8.0
	print("\n== pin 3: kick in range (walk until the gap <= %.1f px) ==" % gap)
	send_key(KEY_D, true)
	await wait_until(func(): return main.p2.position.x - main.p1.position.x <= gap, 600)
	send_key(KEY_D, false)
	await wait_until(func(): return main.p1.state == "idle", 10)
	await wait_ticks(5)
	print("    P1 x %.1f, P2 x %.1f, gap %.1f" % [main.p1.position.x, main.p2.position.x,
			main.p2.position.x - main.p1.position.x])
	results.clear()
	var k0 := await tap_and_find(KEY_K, "K (kick)", "kick")
	await wait_until(func(): return main.p1.state == "idle", 80)
	await wait_ticks(2)
	var hit := result_after(k0, "kick")
	check(hit.size() > 0 and hit[2] == "hit", "3", "the kick in range hits (got %s)" % [hit])
	if hit.is_empty():
		return
	var th: int = hit[0]
	check(th - k0 == KICK_FIRST_ACTIVE, "3", "it hits on kick frame %d, the first active frame (got %d)" % [
			KICK_FIRST_ACTIVE, th - k0])
	check(frame_at(th) == KICK_FIRST_ACTIVE, "3", "P1.frame is %d on the hit tick (got %d)" % [
			KICK_FIRST_ACTIVE, frame_at(th)])
	var held := true
	for i in range(1, HITSTOP + 1):
		held = held and frame_at(th + i) == KICK_FIRST_ACTIVE and ticklog.ticks[th + i]["state"] == "kick"
	check(held, "3", "hitstop holds P1 on kick frame %d for the next %d ticks" % [KICK_FIRST_ACTIVE, HITSTOP])
	check(frame_at(th + HITSTOP + 1) == KICK_FIRST_ACTIVE + 1, "3",
			"after hitstop P1.frame goes on from %d (got %d)" % [KICK_FIRST_ACTIVE + 1, frame_at(th + HITSTOP + 1)])
	check(after(k0, "kick") - k0 == KICK_TICKS + HITSTOP, "3",
			"the kick ends %d + %d ticks after it started (got %d)" % [KICK_TICKS, HITSTOP, after(k0, "kick") - k0])
	check(ticklog.ticks[th]["p2"] == "hurt", "3", "P2 is in hurt on the hit tick")


## Pin 4: the game's pause during a kick freezes P1's state and frame.
func pin_pause() -> void:
	print("\n== pin 4: pause during a kick ==")
	await wait_until(func(): return main.p2.state == "idle" and main.p1.state == "idle", 120)
	send_key(KEY_A, true)                           # step back out of range so the kick whiffs
	await wait_ticks(40)
	send_key(KEY_A, false)
	await wait_until(func(): return main.p1.state == "idle", 10)
	await wait_ticks(5)
	var k0 := await tap_and_find(KEY_K, "K (kick)", "kick")
	await wait_until(func(): return main.p1.frame >= 5, 20)
	await tap(KEY_P, "P (pause)")
	var ok := await wait_until(func(): return main.paused, 10)
	check(ok, "4", "P pauses the game during the kick")
	var tp := ticklog.last_tick
	var f0: int = main.p1.frame
	await wait_ticks(30)
	check(main.p1.state == "kick" and main.p1.frame == f0, "4",
			"30 ticks of pause: P1 still kick on frame %d (got %s %d)" % [f0, main.p1.state, main.p1.frame])
	await tap(KEY_P, "P (unpause)")
	await wait_until(func(): return not main.paused, 10)
	var tu := ticklog.last_tick
	await wait_until(func(): return main.p1.state == "idle", 60)
	await wait_ticks(2)
	var paused_ticks := 0
	for t in range(k0, after(k0, "kick")):
		if ticklog.ticks.has(t) and ticklog.ticks[t]["paused"]:
			paused_ticks += 1
	print("    kick start tick %d, pause from about %d to %d, %d paused ticks" % [k0, tp, tu, paused_ticks])
	check(paused_ticks >= 30 and after(k0, "kick") - k0 == KICK_TICKS + paused_ticks, "4",
			"the kick ends after %d unpaused ticks (%d in all, %d paused)" % [KICK_TICKS,
			after(k0, "kick") - k0, paused_ticks])


# --- helpers ---------------------------------------------------------------------------------

func tap_and_find(code: Key, label: String, state: String) -> int:
	var n := states.size()
	await tap(code, label)
	await wait_until(func(): return states.size() > n and states.slice(n).any(func(s): return s[1] == state), 10)
	for s in states.slice(n):
		if s[1] == state:
			return s[0]
	check(false, "harness", "%s did not start %s" % [label, state])
	return -1


## The tick P1 left `state` after `t0`, or -1.
func after(t0: int, state: String) -> int:
	for s in states:
		if s[0] > t0 and s[1] != state:
			return s[0]
	return -1


func result_after(t0: int, kind: String) -> Array:
	for r in results:
		if r[0] >= t0 and r[1] == kind:
			return r
	return []


func rel(r: Array, t0: int) -> String:
	return "nothing" if r.is_empty() else "%s on frame %d" % [r[2], r[0] - t0]


func frame_at(t: int) -> int:
	return ticklog.ticks[t]["frame"] if ticklog.ticks.has(t) else -1


func frames_ok(t0: int, n: int) -> bool:
	for i in n:
		if frame_at(t0 + i) != i:
			print("    tick %d: frame %d, want %d" % [t0 + i, frame_at(t0 + i), i])
			return false
	return true


func send_key(code: Key, pressed: bool) -> void:
	var ev := InputEventKey.new()
	ev.keycode = code
	ev.physical_keycode = code
	ev.pressed = pressed
	Input.parse_input_event(ev)


func tap(code: Key, label: String) -> void:
	send_key(code, true)
	print("    INPUT: %s pressed after tick %d" % [label, ticklog.last_tick])
	await wait_ticks(HOLD_TICKS)
	send_key(code, false)
	await process_frame


func hold(code: Key, n: int, label: String) -> void:
	send_key(code, true)
	print("    INPUT: %s held from tick %d for %d ticks" % [label, ticklog.last_tick, n])
	await wait_ticks(n)
	send_key(code, false)
	await process_frame


func wait_until(cond: Callable, max_ticks: int) -> bool:
	var limit := Engine.get_physics_frames() + max_ticks
	while not cond.call():
		if Engine.get_physics_frames() > limit or Time.get_ticks_msec() - started_ms > WALL_LIMIT_MS:
			return false
		await process_frame
	return true


func wait_ticks(n: int) -> void:
	var limit := Engine.get_physics_frames() + n
	while Engine.get_physics_frames() < limit:
		await process_frame


func check(cond: bool, pin: String, msg: String) -> void:
	checks += 1
	if not cond:
		failures += 1
	print("%s [pin %s] %s" % ["PASS" if cond else "FAIL", pin, msg])


func finish() -> void:
	if finished:
		return
	finished = true
	print("%d checks, %d failed" % [checks, failures])
	quit(1 if failures else 0)
