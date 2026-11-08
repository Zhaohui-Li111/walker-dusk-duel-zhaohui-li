extends SceneTree
## A6 Effect B (courtyard embers): headless state test of the start/stop code
## (res://effects/embers_controller.gd) against CHANGE-BRIEF.md, Effect B, observable rules 1-5.
## Run from the repo root, through the wrapper:
##   scripts/run-test.sh test_embers_state.gd 60
## As in test_hit_spark_state.gd, main's _physics_process stays on: the fight runs in the real loop
## and P1 is driven by key events read by its PlayerController. The controller is never called.
## Writes to game or engine state, each printed:
##   HARNESS  P2's controller is set to null when a round starts, so Aotake stands still and the
##            K.O. comes from P1's punches.
##   SETUP    get_tree().paused (rule 3) and Embers.visible (rule 4): no game input sets either,
##            so the test sets them, as the brief's rules describe.
## What a headless run sees: the emitter's node state (emitting, speed_scale, visible, amount,
## can_process(), is_processing_internal()) once per physics tick and once per frame. The dummy
## renderer draws nothing and CPUParticles2D has no live particle count, so the particles
## themselves (and whether preprocess filled the field) are not seen.
## Effect B has no feedback loop: its condition is phase == "fight", on or off, and CPUParticles2D
## has no amount_ratio. The test only asserts that amount stays 48.

const AMOUNT := 48                       # embers.tscn
const HITSTOP := 4                       # main.gd HITSTOP_FRAMES
const HOLD_TICKS := 3                    # how long each key is held down
const PAUSE_TICKS := 40                  # game pause (P)
const TREE_TICKS := 60                   # SETUP tree pause
const HIDE_TICKS := 60                   # SETUP hidden, before the K.O.
const FADE_WAIT := 600                   # ticks to watch is_processing_internal() after a stop
const WALL_LIMIT_MS := 100000            # watchdog, under the wrapper's 120 s

var checks := 0
var failures := 0
var finished_run := false
var main: Node
var embers: CPUParticles2D
var controller: Node
var ticklog: TickLog
var sampler: Sampler
var clocks := {}                         # observation: label -> ticks from stop to internal off


## Records the emitter once per physics tick, after main (0) and the controller (10). It runs while
## the tree is paused (PROCESS_MODE_ALWAYS), so rule 3's ticks are recorded too.
class TickLog extends Node:
	var main: Node
	var embers: CPUParticles2D
	var controller: Node
	var recording := false
	var ticks := {}
	var order := []
	var last_tick := -1

	func _ready() -> void:
		process_physics_priority = 1000
		process_mode = Node.PROCESS_MODE_ALWAYS

	func reset(m: Node) -> void:
		main = m
		embers = m.get_node("Embers")
		controller = m.get_node("EmbersController")
		ticks.clear()
		order.clear()

	func _physics_process(_delta: float) -> void:
		if not (recording and is_instance_valid(main)):
			return
		last_tick = Engine.get_physics_frames()
		ticks[last_tick] = {"phase": main.phase, "paused": main.paused, "hitstop": main.hitstop,
				"tree": get_tree().paused, "emitting": embers.emitting, "speed": embers.speed_scale,
				"visible": embers.visible, "amount": embers.amount, "can": embers.can_process(),
				"ctl_can": controller.can_process(), "internal": embers.is_processing_internal()}
		order.append(last_tick)


## Records speed_scale and emitting once per rendered frame, after every other _process.
class Sampler extends Node:
	var main: Node
	var embers: CPUParticles2D
	var recording := false
	var frames := []                     # [process frame, main.paused, speed_scale, emitting]
	var started_ms := 0
	var on_watchdog: Callable

	func _ready() -> void:
		process_priority = 1000
		process_mode = Node.PROCESS_MODE_ALWAYS
		started_ms = Time.get_ticks_msec()

	func _process(_delta: float) -> void:
		if Time.get_ticks_msec() - started_ms > WALL_LIMIT_MS:
			on_watchdog.call()
		if recording and is_instance_valid(main):
			frames.append([Engine.get_process_frames(), main.paused, embers.speed_scale, embers.emitting])


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	ticklog = TickLog.new()
	sampler = Sampler.new()
	sampler.on_watchdog = _watchdog
	root.add_child(ticklog)
	root.add_child(sampler)
	for i in 10:
		await process_frame
	print("embers state test: Godot %s, %d physics ticks/s; headless dummy renderer, nothing is drawn" % [
		Engine.get_version_info().string, ProjectSettings.get_setting("physics/common/physics_ticks_per_second")])
	await scenario_round()
	await scenario_tree_pause_fade()
	await scenario_hidden()
	print("\n== OBSERVATION (printed, not asserted): ticks from the stop tick until is_processing_internal() is false ==")
	for k in clocks:
		print("    %s: %s" % [k, clocks[k]])
	finish()


# --- scenarios ---------------------------------------------------------------

func scenario_round() -> void:
	print("\n== A-D: load -> title -> Enter -> fight, P pause, SETUP tree pause, K.O. by punches, Enter -> round 2 (rules 1, 2, 3, 5) ==")
	open_main()
	await physics_frame
	await physics_frame
	var t0: int = ticklog.order[0]
	check(not tk(t0)["emitting"] and tk(t0)["phase"] == "title", "5",
			"first recorded tick after the scene loads (%d): phase title, not emitting" % t0)
	var e_i := main.get_children().find(embers)
	check(embers.get_parent() == main and e_i == main.get_children().find(main.get_node("Stage")) + 1
			and e_i < main.get_children().find(main.p1), "draw order",
			"Embers is a child of Main right after Stage and before P1 (drawn behind the fighters; child %d)" % e_i)
	check(embers.process_mode == Node.PROCESS_MODE_INHERIT, "3", "Embers' process_mode is INHERIT (%d)" % embers.process_mode)
	await wait_ticks(30)
	if not await enter_fight():
		await close_main()
		return
	var t_fight := first_tick(func(r): return r["phase"] == "fight")
	var pre: Array = ticklog.order.filter(func(t): return t < t_fight)
	check(pre.size() >= 90 and pre.all(func(t): return not tk(t)["emitting"]), "1, 5",
			"not emitting on any of the %d title and intro ticks before the fight" % pre.size())
	check(tk(t_fight)["emitting"] and not tk(t_fight - 1).get("emitting", true), "1",
			"emitting turned on on tick %d, the first tick with phase == \"fight\"" % t_fight)

	# B: game pause, by input.
	await wait_ticks(20)
	await tap(KEY_P, "P (pause)")
	await wait_ticks(PAUSE_TICKS)
	await tap(KEY_P, "P (resume)")
	await wait_ticks(10)
	var gp: Array = ticklog.order.filter(func(t): return tk(t)["paused"])
	var pf: Array = sampler.frames.filter(func(s): return s[1])
	var frozen := gp.all(func(t): return tk(t)["speed"] == 0.0 and tk(t)["emitting"])
	var frozen_f := pf.all(func(s): return s[2] == 0.0 and s[3])
	check(gp.size() >= PAUSE_TICKS and frozen and pf.size() >= PAUSE_TICKS and frozen_f, "2",
			"speed_scale 0 and still emitting on all %d paused ticks and %d paused frames" % [gp.size(), pf.size()])
	var after_pause: int = gp[-1] + 1 if not gp.is_empty() else -1
	check(after_pause > 0 and tk(after_pause).get("speed", 0.0) == 1.0, "2",
			"speed_scale back to 1 on the first tick after the pause (%d)" % after_pause)

	# D1: tree pause during the fight (SETUP).
	var s := Engine.get_physics_frames()
	print("    SETUP (not input): get_tree().paused = true after tick %d, for %d ticks" % [ticklog.last_tick, TREE_TICKS])
	paused = true
	await wait_ticks(TREE_TICKS)
	paused = false
	print("    SETUP (not input): get_tree().paused = false after tick %d" % ticklog.last_tick)
	await wait_ticks(5)
	var tp: Array = ticklog.order.filter(func(t): return tk(t)["tree"])
	var before := tk(tp[0] - 1) if not tp.is_empty() else {}
	check(tp.size() >= TREE_TICKS - 1 and tp.all(func(t): return not tk(t)["can"] and not tk(t)["ctl_can"]), "3",
			"while the tree was paused (%d ticks) neither Embers nor its controller could process" % tp.size())
	var same := func(t): return tk(t)["emitting"] == before["emitting"] and tk(t)["speed"] == before["speed"] and tk(t)["phase"] == "fight"
	check(not tp.is_empty() and tp.all(same), "3",
			"while the tree was paused, emitting (%s) and speed_scale (%s) did not change; phase stayed fight" % [
			before.get("emitting"), before.get("speed")])
	var after_tree: Array = ticklog.order.filter(func(t): return t > s and not tk(t)["tree"])
	check(not after_tree.is_empty() and tk(after_tree[0])["can"] and tk(after_tree[0])["emitting"], "3",
			"after the tree resumed, Embers processes again and is still emitting")

	# C: K.O. by input.
	if not await punch_to_ko():
		await close_main()
		return
	var t_ko := first_tick(func(r): return r["phase"] == "ko")
	check(not tk(t_ko)["emitting"] and tk(t_ko - 1)["emitting"], "1",
			"emitting turned off on tick %d, the first tick with phase == \"ko\" (on just before)" % t_ko)
	var watched := await watch_fade(t_ko, "C: plain stop after a K.O.")
	clocks["C: plain stop after a K.O."] = watched
	await wait_until(func(): return main.phase == "result", 200)
	var ended: Array = ticklog.order.filter(func(t): return t >= t_ko)
	check(ended.size() > 90 and ended.all(func(t): return not tk(t)["emitting"]), "1",
			"not emitting on any of the %d ko and result ticks" % ended.size())

	# Round 2 by input.
	await tap(KEY_ENTER, "Enter (rematch on the result screen)")
	await wait_until(func(): return main.phase == "fight", 120)
	await wait_ticks(10)
	var t_f2 := first_tick(func(r): return r["phase"] == "fight", t_ko)
	var intro2: Array = ticklog.order.filter(func(t): return t > t_ko and t < t_f2 and tk(t)["phase"] == "intro")
	check(t_f2 > 0 and intro2.size() >= 50 and intro2.all(func(t): return not tk(t)["emitting"]), "1",
			"round 2: not emitting on any of the %d intro ticks" % intro2.size())
	check(t_f2 > 0 and tk(t_f2)["emitting"], "1",
			"round 2: emitting on again on tick %d, the first tick with phase == \"fight\" (restart())" % t_f2)
	await close_main()


func scenario_tree_pause_fade() -> void:
	print("\n== E: K.O. by punches, then SETUP tree pause for %d ticks while the embers fade (rule 3, observation) ==" % TREE_TICKS)
	open_main()
	if not await enter_fight():
		await close_main()
		return
	if not await punch_to_ko():
		await close_main()
		return
	var t_ko := first_tick(func(r): return r["phase"] == "ko")
	await wait_ticks(10)
	print("    SETUP (not input): get_tree().paused = true on tick K.O.+%d, for %d ticks" % [ticklog.last_tick - t_ko, TREE_TICKS])
	paused = true
	await wait_ticks(TREE_TICKS)
	paused = false
	var tp: Array = ticklog.order.filter(func(t): return tk(t)["tree"])
	check(tp.size() >= TREE_TICKS - 1 and tp.all(func(t): return not tk(t)["can"] and not tk(t)["emitting"]), "3",
			"after the stop, Embers could not process on any of the %d tree-paused ticks, and stayed off" % tp.size())
	clocks["E: tree paused %d ticks during the fade" % TREE_TICKS] = await watch_fade(t_ko, "E")
	await close_main()


func scenario_hidden() -> void:
	print("\n== F: SETUP visible = false in the fight, K.O. by punches while hidden (rule 4, observation) ==")
	open_main()
	if not await enter_fight():
		await close_main()
		return
	await wait_ticks(10)
	var h0 := Engine.get_physics_frames()
	print("    SETUP (not input): Embers.visible = false after tick %d" % ticklog.last_tick)
	embers.visible = false
	await wait_ticks(HIDE_TICKS)
	var hid: Array = ticklog.order.filter(func(t): return t > h0 and not tk(t)["visible"])
	check(hid.size() >= HIDE_TICKS - 1 and hid.all(func(t): return tk(t)["emitting"] and tk(t)["can"] and tk(t)["internal"]), "4",
			"hidden in the fight for %d ticks: still emitting, can_process() and is_processing_internal() true on every tick" % hid.size())
	if not await punch_to_ko():
		await close_main()
		return
	var t_ko := first_tick(func(r): return r["phase"] == "ko")
	check(not tk(t_ko)["visible"] and not tk(t_ko)["emitting"] and tk(t_ko - 1)["emitting"], "4, 1",
			"while hidden, the phase still decides: emitting turned off on the K.O. tick %d" % t_ko)
	clocks["F: hidden for the whole fade"] = await watch_fade(t_ko, "F")
	check(not embers.visible, "4", "the controller never set visible (still false after the fade)")
	embers.visible = true
	print("    SETUP (not input): Embers.visible = true after tick %d" % ticklog.last_tick)
	await close_main()


# --- checks over every scenario ---------------------------------------------

## Rules 1 and 2 on every recorded tick; amount never changes.
func check_scene() -> void:
	var bad_e: Array = ticklog.order.filter(func(t): return tk(t)["emitting"] != (tk(t)["phase"] == "fight"))
	check(bad_e.is_empty(), "1",
			"scene: emitting == (phase == \"fight\") on all %d recorded ticks%s" % [ticklog.order.size(),
			"" if bad_e.is_empty() else ": wrong on ticks %s" % [bad_e.slice(0, 5)]])
	var run: Array = ticklog.order.filter(func(t): return not tk(t)["tree"])
	var bad_s: Array = run.filter(func(t): return tk(t)["speed"] != (0.0 if (tk(t)["paused"] or tk(t)["hitstop"] > 0) else 1.0))
	var held: int = run.filter(func(t): return tk(t)["hitstop"] > 0).size()
	check(bad_s.is_empty() and held > 0, "2",
			"scene: speed_scale 0 on every tick with main.paused or main.hitstop > 0 (%d hitstop ticks), 1 on the rest, over %d ticks with the tree running%s" % [
			held, run.size(), "" if bad_s.is_empty() else ": wrong on ticks %s" % [bad_s.slice(0, 5)]])
	var bad_a: Array = ticklog.order.filter(func(t): return tk(t)["amount"] != AMOUNT)
	check(bad_a.is_empty(), "no feedback loop", "scene: amount stayed %d on every tick" % AMOUNT)


# --- helpers -----------------------------------------------------------------

func open_main() -> void:
	main = load("res://game/main.tscn").instantiate()
	embers = main.get_node("Embers")
	controller = main.get_node("EmbersController")
	ticklog.reset(main)
	sampler.main = main
	sampler.embers = embers
	sampler.frames.clear()
	main.round_started.connect(func(_n): main.p2.controller = null)
	ticklog.recording = true
	sampler.recording = true
	root.add_child(main)


func enter_fight() -> bool:
	await process_frame
	check(main.is_physics_processing() and main.p1.controller is PlayerController, "harness",
			"main's _physics_process is on and P1 is driven by its PlayerController")
	await tap(KEY_ENTER, "Enter (title)")
	var ok := await wait_until(func(): return main.phase == "fight", 120)
	check(ok, "harness", "Enter on the title started round 1; the intro ran into the fight (phase %s)" % main.phase)
	print("    HARNESS (writes no fight state): P2's controller set to null when the round starts, so Aotake stands still")
	return ok


func close_main() -> void:
	for k in [KEY_D, KEY_J, KEY_P, KEY_ENTER]:
		send_key(k, false)
	paused = false
	ticklog.recording = false
	sampler.recording = false
	if is_instance_valid(main):
		check_scene()
		main.queue_free()
		await process_frame
		await process_frame


## D held and J tapped every 24 ticks until the K.O.: P1 pushes Aotake to the wall and punches.
func punch_to_ko() -> bool:
	send_key(KEY_D, true)
	print("    INPUT: D held and J tapped every 24 ticks from after tick %d, until a K.O." % ticklog.last_tick)
	var limit := Engine.get_physics_frames() + 3000
	while main.phase == "fight" and Engine.get_physics_frames() < limit:
		send_key(KEY_J, true)
		await wait_ticks(HOLD_TICKS)
		send_key(KEY_J, false)
		await wait_ticks(21)
	send_key(KEY_D, false)
	var ok: bool = main.phase == "ko"
	check(ok, "harness", "the punches ended the fight in a K.O. (phase %s, P2 health %d)" % [main.phase, main.p2.health])
	return ok


## Waits until is_processing_internal() turns false after the stop tick, or FADE_WAIT ticks.
## Returns the tick count, or -1. Printed only: whether this flag tracks the particles' life is not
## confirmed for 4.7.2.
func watch_fade(t_stop: int, label: String) -> int:
	await wait_until(func(): return not embers.is_processing_internal(), FADE_WAIT)
	await physics_frame
	var off := first_tick(func(r): return not r["internal"], t_stop)
	var n := off - t_stop if off > 0 else -1
	print("    OBSERVE (%s): is_processing_internal() went false %s ticks after the stop tick" % [label, n])
	return n


func first_tick(cond: Callable, after := -1) -> int:
	for t in ticklog.order:
		if t > after and cond.call(ticklog.ticks[t]):
			return t
	return -1


func tk(t: int) -> Dictionary:
	return ticklog.ticks.get(t, {})


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


func wait_until(cond: Callable, max_ticks: int) -> bool:
	var limit := Engine.get_physics_frames() + max_ticks
	while not cond.call():
		if Engine.get_physics_frames() > limit:
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


func _watchdog() -> void:
	if finished_run:
		return
	check(false, "harness", "watchdog: not finished after %d s of wall-clock time" % (WALL_LIMIT_MS / 1000))
	finish()


func finish() -> void:
	if finished_run:
		return
	finished_run = true
	print("%d checks, %d failed" % [checks, failures])
	quit(1 if failures else 0)
