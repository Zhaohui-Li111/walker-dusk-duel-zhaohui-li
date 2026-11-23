extends SceneTree
## A7 step 6: edges of the kick at every phase boundary (CHANGE-BRIEF.md, "The phase table":
## startup begins 0, active 8, recovery 13, end 28), with an interrupt one frame before, on and one
## frame after each. Run from the repo root:
##   scripts/run-test.sh test_kick_edges.gd 60
## "Frame f" is the tick k0 + f, where k0 is the tick the kick started (Fighter.frame 0). Kicks are
## out of range, so no hitstop shifts the count.
## Two interrupts:
##   hit    the only thing that interrupts a kick (fighter.gd receive_hit). SETUP, printed: on tick
##          k0 + f, inside the physics tick after main has stepped (priority 50, where check_hit()
##          would call it): P1.receive_hit(P2, 1) and P1.flush_ko(). Brief (Zhaohui's choice): the
##          arc returns to rest at once -> on that tick P1 is hurt and the clip is `rest`, hidden.
##   K key  real input through Input.parse_input_event, sent so that the tick k0 + f is the first
##          to read it. Brief: input during the kick does nothing; the kick and the arc go on.
## The rig controller runs at priority 100, after both; TickLog at 1000 reads the result.

const FPS := 60.0
const WALL_LIMIT_MS := 110000
const HIT_FRAMES := [0, 1, 7, 8, 9, 12, 13, 14, 27, 28]
const KEY_FRAMES := [7, 8, 9, 12, 13, 14, 27, 28, 29]

var checks := 0
var failures := 0
var main: Node
var ticklog: TickLog
var setup_hit: SetupHit
var states := []
var started_ms := 0


class TickLog extends Node:
	var main: Node
	var ticks := {}
	var last := -1

	func _ready() -> void:
		process_physics_priority = 1000

	func _physics_process(_delta: float) -> void:
		if not is_instance_valid(main) or main.phase != "fight":
			return
		var ap: AnimationPlayer = main.p1.get_node("KickRig/AnimationPlayer")
		last = Engine.get_physics_frames()
		ticks[last] = {"state": main.p1.state, "frame": main.p1.frame, "clip": ap.current_animation,
				"pos": ap.current_animation_position, "visible": main.p1.get_node("KickRig/Pivot").visible,
				"hitstop": main.hitstop}


## Fires once, inside a physics tick: on tick `at_tick`, or (armed before the kick starts, so frames
## 0 and 1 are reachable) on the first tick P1 is in kick with Fighter.frame == `at_frame`.
class SetupHit extends Node:
	var main: Node
	var at_tick := -1
	var at_frame := -1
	var done := false
	var tick := -1

	func _ready() -> void:
		process_physics_priority = 50

	func _physics_process(_delta: float) -> void:
		var now := Engine.get_physics_frames()
		var due: bool = (at_tick >= 0 and now == at_tick) or (at_frame >= 0 and main.p1.state == "kick" and main.p1.frame == at_frame)
		if due:
			at_tick = -1
			at_frame = -1
			tick = now
			print("    SETUP (not input): tick %d, P1 %s frame %d: P1.receive_hit(P2, 1), P1.flush_ko()" % [
					Engine.get_physics_frames(), main.p1.state, main.p1.frame])
			main.p1.receive_hit(main.p2, 1)
			main.p1.flush_ko()
			done = true


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	started_ms = Time.get_ticks_msec()
	ticklog = TickLog.new()
	setup_hit = SetupHit.new()
	root.add_child(ticklog)
	root.add_child(setup_hit)
	print("A7 kick edges: Godot %s; headless" % Engine.get_version_info().string)
	main = load("res://game/main.tscn").instantiate()
	main.round_started.connect(func(_n): main.p2.controller = null)
	root.add_child(main)
	ticklog.main = main
	setup_hit.main = main
	main.p1.state_changed.connect(func(_f, s): states.append([Engine.get_physics_frames(), s]))
	await process_frame
	await tap(KEY_ENTER)
	check(await wait_until(func(): return main.phase == "fight", 240), "harness", "round 1 started")
	print("    HARNESS (writes no fight state): P2's controller set to null when the round starts")
	await wait_ticks(5)
	for f in HIT_FRAMES:
		await hit_case(f)
	for f in KEY_FRAMES:
		await key_case(f)
	print("    P1 health after the SETUP hits: %d" % main.p1.health)
	finish()


func hit_case(f: int) -> void:
	await wait_until(func(): return main.p1.state == "idle" and main.p2.state == "idle", 120)
	setup_hit.done = false
	if f <= 27:
		setup_hit.at_frame = f       # armed before the kick starts
	var k0 := await start_kick()
	if k0 < 0:
		return
	if f > 27:
		setup_hit.at_tick = k0 + f
	await wait_until(func(): return setup_hit.done and ticklog.last >= k0 + f, 40)
	check(setup_hit.tick == k0 + f, "harness", "the SETUP hit ran on tick k0 + %d (got k0 + %d)" % [f, setup_hit.tick - k0])
	var t: Dictionary = ticklog.ticks.get(k0 + f, {})
	var phase := phase_of(f)
	check(t.get("state") == "hurt" and t.get("clip") == "rest" and t.get("visible") == false, "edge",
			"hit on frame %2d (%s): P1 hurt, `rest`, arc hidden on that tick (got %s, %s, visible %s)" % [
			f, phase, t.get("state"), t.get("clip"), t.get("visible")])
	if f >= 1 and f <= 27:
		var before: Dictionary = ticklog.ticks.get(k0 + f - 1, {})
		check(before.get("clip") == "kick_arc" and absf(before.get("pos", -1.0) - (f - 1) / FPS) < 1e-4, "edge",
				"  the tick before (frame %d): `kick_arc` at %.4f s" % [f - 1, (f - 1) / FPS])
	await wait_until(func(): return main.p1.state == "idle", 60)
	await wait_ticks(3)


func key_case(f: int) -> void:
	var k0 := await start_kick()
	if k0 < 0:
		return
	# Send K after tick k0 + f - 1 has been logged, so tick k0 + f is the first to read it.
	await wait_until(func(): return ticklog.last >= k0 + f - 1, 40)
	var n := states.size()
	send_key(KEY_K, true)
	await wait_ticks(3)
	send_key(KEY_K, false)
	await wait_until(func(): return ticklog.last >= k0 + f + 2, 10)
	var new_kick := -1
	for s in states.slice(n):
		if s[1] == "kick":
			new_kick = s[0]
			break
	var t: Dictionary = ticklog.ticks.get(k0 + f, {})
	if f <= 27:
		check(new_kick < 0 and t.get("state") == "kick" and t.get("clip") == "kick_arc"
				and absf(t.get("pos", -1.0) - f / FPS) < 1e-4, "edge",
				"K read on frame %2d (%s): ignored, the kick and the arc go on (kick_arc at %.4f s)" % [f, phase_of(f), f / FPS])
	elif f == 28:
		check(new_kick < 0 and t.get("state") == "idle" and t.get("clip") == "rest", "edge",
				"K read on frame 28 (the kick ends that tick, input not read): no new kick, `rest` (new kick at %d)" % new_kick)
	else:
		var nt: Dictionary = ticklog.ticks.get(new_kick, {})
		check(new_kick == k0 + f and nt.get("clip") == "kick_arc" and absf(nt.get("pos", -1.0)) < 1e-4, "edge",
				"K read on frame %d (idle, input read again): a new kick that tick, `kick_arc` from 0 (tick +%d)" % [
				f, new_kick - k0])
	await wait_until(func(): return main.p1.state == "idle", 80)
	await wait_ticks(3)


func phase_of(f: int) -> String:
	if f <= 7:
		return "startup"
	if f <= 12:
		return "active"
	if f <= 27:
		return "recovery"
	return "after the end"


func start_kick() -> int:
	await wait_until(func(): return main.p1.state == "idle" and main.p2.state == "idle", 120)
	var n := states.size()
	await tap(KEY_K)
	await wait_until(func(): return states.slice(n).any(func(s): return s[1] == "kick"), 10)
	for s in states.slice(n):
		if s[1] == "kick":
			return s[0]
	check(false, "harness", "K did not start a kick")
	return -1


func send_key(code: Key, pressed: bool) -> void:
	var ev := InputEventKey.new()
	ev.keycode = code
	ev.physical_keycode = code
	ev.pressed = pressed
	Input.parse_input_event(ev)


func tap(code: Key) -> void:
	send_key(code, true)
	await wait_ticks(3)
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


func check(cond: bool, rule: String, msg: String) -> void:
	checks += 1
	if not cond:
		failures += 1
	print("%s [%s] %s" % ["PASS" if cond else "FAIL", rule, msg])


func finish() -> void:
	print("%d checks, %d failed" % [checks, failures])
	quit(1 if failures else 0)
