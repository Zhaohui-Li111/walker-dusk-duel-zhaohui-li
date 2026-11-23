extends SceneTree
## Movie Maker capture of both A7 clips in the running game, on an isolated copy
## (capture/game, source revision 8049c54; nothing in the game is changed).
##   godot --path capture/game --write-movie <ABSOLUTE>/capture/a7_play.avi --fixed-fps 60
##         --disable-vsync --resolution 3840x2160 --script res://capture_a7.gd
## Adapted from the A6 reel's capture_a6.gd. SCRIPTED INPUT, labelled as such in the film:
##   - Enter (confirm), Esc (pause), D (p1_right) and K (p1_kick) are sent as InputEventAction
##     through Input.parse_input_event; main.gd's _unhandled_input and P1's real PlayerController
##     read them.
##   - P2 (Aotake) gets the game's own ScriptedController after round_started: it stands still,
##     and at a chosen tick it is given one kick ({"attack": "kick"} on its first frame). That is
##     how Aotake interrupts Akaken's kicks in startup, active and recovery.
## No position, health, phase, state, frame, clip or animation property is written by this script.
## P1 stands at a gap where Aotake's kick reaches Akaken but Akaken's kick does not reach Aotake
## (Aotake's kick hitbox is larger), so Akaken's own kicks always whiff and never interrupt Aotake.
## Timeline: title (lanterns already burning) -> Enter -> intro -> fight -> P1 walks to the gap ->
##   E1, E2 two whole kicks (whiff) -> E3 a kick paused at Fighter.frame 10 for 180 ticks (3 s) ->
##   E4 Aotake hits during Akaken's startup -> E5 during active -> E6 during recovery -> quit.
## Title held 360 ticks (6 s) so the lanterns can be watched before the round; 60 ticks between events.
## Every tick a kick or a pause is under way, one line per fighter is logged (state, frame, rig clip,
## rig time, Pivot visible) with both lanterns' clip times, so each interrupt is on record.

const GAP_HI := 70.0                 # from the dry run (BUILD-LOG): reach P1 52.6, P2 64.5; at a gap of
                                     # 69.5-70 P1's kick whiffs and P2's lands
const P2_LEAD_STARTUP := 4           # P2 kick starts 4 ticks before P1's: hit lands on P1 frame 8-4
const P1_LEAD_ACTIVE := 2            # P1 kick starts 2 ticks before P2's: hit on P1 frame 8+2
const P1_LEAD_RECOVERY := 12         # hit on P1 frame 8+12

var main: Node
var frame := 0
var held := {}
var step_name := "title"
var step_tick := 0
var events := ["whiff", "whiff2", "pause", "startup", "active", "recovery"]
var ev := -1
var sched := {}                      # tick -> [action strings]
var hits := []
var logging_until := -1


func _initialize() -> void:
	main = load("res://game/main.tscn").instantiate()
	root.add_child(main)
	_setup.call_deferred()


func _setup() -> void:
	main.round_started.connect(_on_round_started)
	for f in [main.p1, main.p2]:
		f.attack_resolved.connect(_on_attack_resolved)
		f.state_changed.connect(_on_state_changed)
	process_frame.connect(_tick)
	var r1: float = main.p1.reach("kick")
	var r2: float = main.p2.reach("kick")
	print("reach kick P1 %.1f P2 %.1f; half width P1 %.1f P2 %.1f" % [r1, r2, main.p1.body_half_width(),
			main.p2.body_half_width()])


func _on_round_started(_n: int) -> void:
	main.p2.controller = ScriptedController.new([{"frames": 100000}])


func _on_attack_resolved(f: Node, kind: String, result: String, point: Vector2) -> void:
	print("tick %d  t=%.3fs  %s by %s (%s) at (%.1f, %.1f) | P1 %s f%d  P2 %s f%d  P1 health %d" % [
			frame, frame / 60.0, result.to_upper(), f.name, kind, point.x, point.y, main.p1.state,
			main.p1.frame, main.p2.state, main.p2.frame, main.p1.health])
	if result == "hit":
		hits.append([frame, f.name, main.p1.state, main.p1.frame])


func _on_state_changed(f: Node, s: String) -> void:
	print("tick %d  t=%.3fs  STATE %s -> %s" % [frame, frame / 60.0, f.name, s])


func _send(action: String, pressed: bool) -> void:
	if held.get(action, false) == pressed:
		return
	var e := InputEventAction.new()
	e.action = action
	e.pressed = pressed
	Input.parse_input_event(e)
	held[action] = pressed


func _tap(action: String) -> void:
	var e := InputEventAction.new()
	e.action = action
	e.pressed = true
	Input.parse_input_event(e)
	var up := InputEventAction.new()
	up.action = action
	up.pressed = false
	Input.parse_input_event.call_deferred(up)
	print("tick %d  t=%.3fs  INPUT %s" % [frame, frame / 60.0, action])


func _p2_kick() -> void:
	main.p2.controller = ScriptedController.new([{"frames": 1, "attack": "kick"}, {"frames": 100000}])
	print("tick %d  t=%.3fs  SCRIPTED P2 kick (ScriptedController)" % [frame, frame / 60.0])


func _rig(f: Node) -> String:
	var ap: AnimationPlayer = f.get_node("KickRig/AnimationPlayer")
	var pv: Node2D = f.get_node("KickRig/Pivot")
	return "%s %-5s f%-2d clip %-8s t %.4f vis %-5s" % [f.name, f.state, f.frame, ap.current_animation,
			ap.current_animation_position, pv.visible]


func _lanterns() -> String:
	return "lanterns %.3f %.3f" % [main.get_node("LanternLeft/AnimationPlayer").current_animation_position,
			main.get_node("LanternRight/AnimationPlayer").current_animation_position]


func _schedule(at: int, what: String) -> void:
	if not sched.has(at):
		sched[at] = []
	sched[at].append(what)


func _gap() -> float:
	return main.p2.position.x - main.p1.position.x


func _settled() -> bool:
	return main.p1.state == "idle" and main.p2.state == "idle"


func _tick() -> void:
	frame += 1
	for what in sched.get(frame, []):
		match what:
			"K": _tap("p1_kick")
			"P2K": _p2_kick()
			"ESC": _tap("pause")
	sched.erase(frame)
	var busy: bool = main.p1.state in ["kick", "hurt"] or main.p2.state in ["kick", "hurt"] or main.paused
	if busy or frame <= logging_until:
		print("tick %d  t=%.3fs  %s | %s | %s%s" % [frame, frame / 60.0, _rig(main.p1), _rig(main.p2),
				_lanterns(), "  PAUSED" if main.paused else ""])
		if busy:
			logging_until = frame + 2
	if frame == 360:
		print("tick %d  t=%.3fs  Enter (confirm) | %s" % [frame, frame / 60.0, _lanterns()])
		_tap("confirm")
	if main.phase != "fight":
		return
	match step_name:
		"title":
			step_name = "walk"
			print("tick %d  t=%.3fs  FIGHT | gap %.1f" % [frame, frame / 60.0, _gap()])
		"walk":
			if main.p1.state in ["idle", "walk"] and _gap() > GAP_HI:
				_send("p1_right", true)
			else:
				_send("p1_right", false)
				if _settled() and _gap() <= GAP_HI:
					step_name = "rest"
					step_tick = frame
		"rest":
			if frame - step_tick >= 60 and _settled():
				ev += 1
				if ev >= events.size():
					step_name = "end"
					step_tick = frame
					return
				print("tick %d  t=%.3fs  EVENT %s | gap %.1f P1 x %.1f P2 x %.1f" % [frame, frame / 60.0,
						events[ev], _gap(), main.p1.position.x, main.p2.position.x])
				match events[ev]:
					"whiff", "whiff2":
						_schedule(frame + 1, "K")
					"pause":
						_schedule(frame + 1, "K")
						step_name = "pause_wait"
						return
					"startup":
						_schedule(frame + 1, "P2K")
						_schedule(frame + 1 + P2_LEAD_STARTUP, "K")
					"active":
						_schedule(frame + 1, "K")
						_schedule(frame + 1 + P1_LEAD_ACTIVE, "P2K")
					"recovery":
						_schedule(frame + 1, "K")
						_schedule(frame + 1 + P1_LEAD_RECOVERY, "P2K")
				step_name = "after"
				step_tick = frame
		"pause_wait":
			if main.p1.state == "kick" and main.p1.frame == 9:
				_schedule(frame + 1, "ESC")
				_schedule(frame + 1 + 180, "ESC")
				step_name = "after"
				step_tick = frame
		"after":
			if frame - step_tick > 20 and _settled() and not main.paused:
				step_name = "walk"
		"end":
			if frame - step_tick >= 90:
				print("capture done, frames %d; P1 health %d, P2 health %d; hits %s" % [frame,
						main.p1.health, main.p2.health, str(hits)])
				quit()
	if frame >= 3000:
		print("capture TIMEOUT at 3000 frames")
		quit()
