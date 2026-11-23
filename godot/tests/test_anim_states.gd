extends SceneTree
## A7 step 5: the state machine plays each clip on the right states, through one authority each
## (CHANGE-BRIEF.md, "The state machine", "The two clocks", "Lantern decisions"). Run from the
## repo root:
##   scripts/run-test.sh test_anim_states.gd 60
## Structure: the state table against the resources (every clip the rig controller requests
## exists on both fighters; every fighter state maps to a clip); the lanterns placed as the brief
## says. Behaviour: main's real physics loop, P1 driven by key events through
## Input.parse_input_event. The kick arc's clip is read with current_animation and
## current_animation_position (AnimationPlayer route). Two SETUP writes, printed as such, as in A5:
## a hit on P1 through the game's own P2-side call (P1.receive_hit + flush_ko, from inside a physics
## tick where check_hit() would make it), and main.start_fight_now() for a round reset mid-kick.
## Headless: nothing is drawn; this proves which clip plays at which time, never how it looks.

const FPS := 60.0
const HOLD_TICKS := 3
const WALL_LIMIT_MS := 100000
const STATE_TABLE := {"idle": "rest", "walk": "rest", "crouch": "rest", "block": "rest",
		"jump": "rest", "punch": "rest", "kick": "kick_arc", "hurt": "rest", "ko": "rest", "win": "rest"}
const LANTERNS := {"LanternLeft": [Vector2(238, 218), 0.0], "LanternRight": [Vector2(439, 219), 0.4]}

var checks := 0
var failures := 0
var main: Node
var ticklog: TickLog
var setup_hit: SetupHit
var states := []                     # P1 state_changed: [tick, state]
var started_ms := 0


## Once per physics tick, after main (0), SetupHit (50) and the rig controllers (100).
class TickLog extends Node:
	var main: Node
	var recording := false
	var ticks := {}

	func _ready() -> void:
		process_physics_priority = 1000

	func _physics_process(_delta: float) -> void:
		if not (recording and is_instance_valid(main)):
			return
		var ap: AnimationPlayer = main.p1.get_node("KickRig/AnimationPlayer")
		var pivot: Node2D = main.p1.get_node("KickRig/Pivot")
		ticks[Engine.get_physics_frames()] = {"state": main.p1.state, "frame": main.p1.frame,
				"clip": ap.current_animation, "pos": ap.current_animation_position,
				"visible": pivot.visible, "rot": pivot.rotation, "paused": main.paused, "hitstop": main.hitstop,
				"lanterns": [main.get_node("LanternLeft/AnimationPlayer").current_animation_position,
						main.get_node("LanternRight/AnimationPlayer").current_animation_position]}


class SetupHit extends Node:
	var pending: Callable
	var done_tick := -1

	func _ready() -> void:
		process_physics_priority = 50

	func _physics_process(_delta: float) -> void:
		if pending.is_valid():
			var fn := pending
			pending = Callable()
			done_tick = Engine.get_physics_frames()
			fn.call()


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	started_ms = Time.get_ticks_msec()
	ticklog = TickLog.new()
	setup_hit = SetupHit.new()
	root.add_child(ticklog)
	root.add_child(setup_hit)
	print("A7 animation states: Godot %s; headless, nothing is drawn" % Engine.get_version_info().string)
	main = load("res://game/main.tscn").instantiate()
	main.round_started.connect(func(_n): main.p2.controller = null)
	root.add_child(main)
	ticklog.main = main
	main.p1.state_changed.connect(func(_f, s): states.append([Engine.get_physics_frames(), s]))
	await process_frame
	structure()
	await tap(KEY_ENTER, "Enter (title)")
	var ok := await wait_until(func(): return main.phase == "fight", 240)
	check(ok, "harness", "Enter started round 1 and the intro ran into the fight")
	print("    HARNESS (writes no fight state): P2's controller set to null when the round starts")
	ticklog.recording = true
	await wait_ticks(5)
	await kick_whiff()
	await kick_hit_hitstop()
	await kick_pause()
	await kick_interrupted()
	await kick_round_reset()
	finish()


## The state table against the resources, and the lanterns as placed.
func structure() -> void:
	print("\n== structure ==")
	var src := FileAccess.get_file_as_string("res://fighter/kick_rig.gd")
	var requested := []
	var re := RegEx.create_from_string("play\\(\"([a-z_]+)\"\\)")
	for m in re.search_all(src):
		requested.append(m.get_string(1))
	check(requested.size() >= 2, "structure", "kick_rig.gd requests clips %s" % [requested])
	for f: Fighter in [main.p1, main.p2]:
		var rig := f.get_node_or_null("KickRig")
		var ap := f.get_node_or_null("KickRig/AnimationPlayer") as AnimationPlayer
		check(rig != null and rig.get_script() != null and (rig.get_script() as Script).resource_path == "res://fighter/kick_rig.gd",
				"structure", "%s's KickRig runs kick_rig.gd" % f.display_name)
		for c in requested:
			check(ap != null and ap.has_animation(c), "structure", "%s: requested clip `%s` exists" % [f.display_name, c])
		for s in STATE_TABLE:
			check(ap != null and ap.has_animation(STATE_TABLE[s]), "structure",
					"%s: state %s maps to an existing clip `%s`" % [f.display_name, s, STATE_TABLE[s]])
		check(rig != null and rig.process_physics_priority > main.process_physics_priority, "clock",
				"%s's rig controller runs after main in each physics tick (priority %d > %d)" % [
				f.display_name, rig.process_physics_priority, main.process_physics_priority])
	for name in LANTERNS:
		var l := main.get_node_or_null(name) as Node2D
		check(l != null and l.scene_file_path == "res://animations/lantern_flame.tscn", "lantern",
				"%s is an instance of lantern_flame.tscn" % name)
		if l == null:
			continue
		check(l.position == LANTERNS[name][0], "lantern", "%s at %s (got %s)" % [name, LANTERNS[name][0], l.position])
		check(is_equal_approx(l.start_offset, LANTERNS[name][1]), "lantern",
				"%s start_offset %.1f s (got %.2f)" % [name, LANTERNS[name][1], l.start_offset])
		check(l.get_index() == main.get_node("Embers").get_index() + 1 + (1 if name == "LanternRight" else 0)
				and l.get_index() < main.p1.get_index(), "lantern",
				"%s draws after Stage and Embers (A6 keeps Embers right after Stage) and behind the fighters" % name)
		var ap := l.get_node("AnimationPlayer") as AnimationPlayer
		check(ap.current_animation == "flicker" and ap.is_playing(), "lantern", "%s plays `flicker`" % name)
	var left_pos: float = main.get_node("LanternLeft/AnimationPlayer").current_animation_position
	var right_pos: float = main.get_node("LanternRight/AnimationPlayer").current_animation_position
	check(absf(fposmod(right_pos - left_pos, 0.8) - 0.4) < 0.05, "lantern",
			"the right lantern runs half a cycle (0.4 s) after the left (%.3f vs %.3f)" % [right_pos, left_pos])


## A whiffed kick: kick_arc on every kick tick, at Fighter.frame / 60; rest before and after.
func kick_whiff() -> void:
	print("\n== kick out of range: the clip follows Fighter.frame ==")
	var r: Dictionary = ticklog.ticks[ticklog.ticks.keys().max()]
	check(r["clip"] == "rest" and not r["visible"], "table", "idle: `rest`, the arc hidden")
	var p1rig: Node2D = main.p1.get_node("KickRig")
	var p2rig: Node2D = main.p2.get_node("KickRig")
	check(p1rig.scale.x > 0.0 and p2rig.scale.x < 0.0, "rig", "the arc faces each fighter's opponent (P1 scale.x %.3f, P2 %.3f)" % [
			p1rig.scale.x, p2rig.scale.x])
	check(absf(p1rig.scale.y - 38.3 / 38.0) < 0.01 and absf(p2rig.scale.y - 47.9 / 38.0) < 0.01, "rig",
			"sized to each kick hitbox: Akaken %.3f, Aotake %.3f" % [p1rig.scale.y, p2rig.scale.y])
	var k0 := await kick_and_wait()
	var worst := 0.0
	var all_ok := true
	for i in 28:
		var t: Dictionary = ticklog.ticks.get(k0 + i, {})
		if t.is_empty() or t["state"] != "kick" or t["clip"] != "kick_arc" or not t["visible"]:
			all_ok = false
			print("    tick k0+%d: %s" % [i, t])
			continue
		worst = maxf(worst, absf(t["pos"] - t["frame"] / FPS))
	check(all_ok, "table", "kick: `kick_arc`, the arc shown, on all 28 kick ticks")
	print("    MEASURED two clocks: largest |clip time - Fighter.frame / 60| over the kick = %.9f s" % worst)
	check(worst < 1e-4, "clock", "the clip time equals Fighter.frame / 60 on every physics tick (largest gap %.9f s)" % worst)
	var end: Dictionary = ticklog.ticks.get(k0 + 28, {})
	check(end.get("state") == "idle" and end.get("clip") == "rest" and not end.get("visible", true), "table",
			"frame 28: idle, `rest`, the arc hidden on the same tick")


## A kick in range: hitstop holds Fighter.frame, so the arc holds too.
func kick_hit_hitstop() -> void:
	print("\n== kick in range: hitstop freezes the arc ==")
	var gap: float = main.p1.reach("kick") + main.p2.body_half_width() - 8.0
	send_key(KEY_D, true)
	await wait_until(func(): return main.p2.position.x - main.p1.position.x <= gap, 600)
	send_key(KEY_D, false)
	await wait_until(func(): return main.p1.state == "idle", 10)
	await wait_ticks(5)
	var k0 := await kick_and_wait()
	var th := -1
	for i in 40:
		if ticklog.ticks.get(k0 + i, {}).get("hitstop", 0) > 0:
			th = k0 + i
			break
	check(th == k0 + 8, "clock", "the kick hits on frame 8 (hitstop from tick k0+%d)" % (th - k0))
	if th < 0:
		return
	var held := true
	for i in range(0, 5):
		var t: Dictionary = ticklog.ticks[th + i]
		held = held and t["frame"] == 8 and absf(t["pos"] - 8 / FPS) < 1e-4 and t["rot"] == ticklog.ticks[th]["rot"]
	check(held, "clock", "hitstop: the arc holds at frame 8 (clip time %.4f s, same rotation) for the hit tick and 4 more" % (8 / FPS))
	var after: Dictionary = ticklog.ticks[th + 5]
	check(after["frame"] == 9 and absf(after["pos"] - 9 / FPS) < 1e-4, "clock", "after hitstop the arc goes on at frame 9")
	await wait_until(func(): return main.p2.state == "idle", 120)


## The game's pause freezes the arc; the lanterns keep burning (L1).
func kick_pause() -> void:
	print("\n== pause during a kick ==")
	send_key(KEY_A, true)
	await wait_ticks(40)
	send_key(KEY_A, false)
	await wait_until(func(): return main.p1.state == "idle", 10)
	await wait_ticks(5)
	await tap(KEY_K, "K (kick)")
	await wait_until(func(): return main.p1.frame >= 10, 30)
	await tap(KEY_P, "P (pause)")
	await wait_until(func(): return main.paused, 10)
	var t0: int = ticklog.ticks.keys().max()
	await wait_ticks(30)
	var t1: int = ticklog.ticks.keys().max()
	var a: Dictionary = ticklog.ticks[t0]
	var b: Dictionary = ticklog.ticks[t1]
	check(a["paused"] and b["paused"] and a["pos"] == b["pos"] and a["rot"] == b["rot"] and b["clip"] == "kick_arc",
			"clock", "30 paused ticks: the arc stays at %.4f s, rotation %.4f" % [b["pos"], b["rot"]])
	check(a["lanterns"][0] != b["lanterns"][0] and a["lanterns"][1] != b["lanterns"][1], "lantern",
			"the lanterns keep burning through the pause (left %.2f -> %.2f s)" % [a["lanterns"][0], b["lanterns"][0]])
	await tap(KEY_P, "P (unpause)")
	await wait_until(func(): return main.p1.state == "idle", 60)
	await wait_ticks(3)


## A hit in the middle of a kick: rest on the same tick (Zhaohui's interrupt choice).
func kick_interrupted() -> void:
	print("\n== kick interrupted by a hit (SETUP) ==")
	var k0 := await kick_and_wait(false)
	await wait_until(func(): return main.p1.frame >= 9, 20)
	setup_hit.pending = func():
		print("    SETUP (not input): on P1 kick frame %d, P1.receive_hit(P2, 8) then P1.flush_ko(), as P2's check_hit() does" % main.p1.frame)
		main.p1.receive_hit(main.p2, 8)
		main.p1.flush_ko()
	await wait_until(func(): return setup_hit.done_tick >= 0 and ticklog.ticks.has(setup_hit.done_tick), 20)
	var t: Dictionary = ticklog.ticks.get(setup_hit.done_tick, {})
	check(t.get("state") == "hurt" and t.get("clip") == "rest" and not t.get("visible", true), "interrupt",
			"on the hit tick: P1 hurt, `rest`, the arc hidden (got %s, %s, visible %s)" % [t.get("state"), t.get("clip"), t.get("visible")])
	setup_hit.done_tick = -1
	await wait_until(func(): return main.p1.state == "idle", 60)
	await wait_ticks(3)


## A round reset in the middle of a kick: rest on the next tick.
func kick_round_reset() -> void:
	print("\n== round reset during a kick (SETUP) ==")
	await kick_and_wait(false)
	await wait_until(func(): return main.p1.frame >= 4, 20)
	print("    SETUP (not input): main.start_fight_now() on P1 kick frame %d" % main.p1.frame)
	main.start_fight_now()
	var tr := Engine.get_physics_frames()
	await wait_ticks(2)
	var t: Dictionary = ticklog.ticks.get(tr + 1, {})
	check(t.get("state") == "idle" and t.get("clip") == "rest" and not t.get("visible", true), "reset",
			"the tick after the reset: P1 idle, `rest`, the arc hidden (got %s, %s)" % [t.get("state"), t.get("clip")])


# --- helpers ---------------------------------------------------------------------------------

func kick_and_wait(to_end := true) -> int:
	var n := states.size()
	await tap(KEY_K, "K (kick)")
	await wait_until(func(): return states.slice(n).any(func(s): return s[1] == "kick"), 10)
	var k0 := -1
	for s in states.slice(n):
		if s[1] == "kick":
			k0 = s[0]
			break
	check(k0 >= 0, "harness", "K started a kick (tick %d)" % k0)
	if to_end:
		await wait_until(func(): return main.p1.state != "kick", 80)
		await wait_ticks(2)
	return k0


func send_key(code: Key, pressed: bool) -> void:
	var ev := InputEventKey.new()
	ev.keycode = code
	ev.physical_keycode = code
	ev.pressed = pressed
	Input.parse_input_event(ev)


func tap(code: Key, label: String) -> void:
	send_key(code, true)
	print("    INPUT: %s" % label)
	await wait_ticks(HOLD_TICKS)
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
