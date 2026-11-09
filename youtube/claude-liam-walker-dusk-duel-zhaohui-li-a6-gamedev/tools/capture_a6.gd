extends SceneTree
## Movie Maker capture of both A6 particle effects in the running game, on an isolated copy
## (capture/game, source revision 840bcfd; nothing in the game is changed).
##   godot --path capture/game --write-movie <ABSOLUTE>/capture/a6_play.avi --fixed-fps 60
##         --disable-vsync --resolution 3840x2160 --script res://capture_a6.gd
## SCRIPTED INPUT, labelled as such in the film:
##   - Enter (confirm) and Esc (pause) are sent as InputEventAction through Input.parse_input_event,
##     so main.gd's own _unhandled_input handles them.
##   - P1 (Akaken) is the real PlayerController; this script presses p1_right to walk in and
##     p1_punch to punch, the same way.
##   - P2 (Aotake) gets the game's own ScriptedController instead of the CPU after round_started:
##     it stands still, never blocks, and kicks every 110 ticks. That is the only harness change.
## No position, health, phase or particle property is written by this script.
## Timeline: title until tick 90 -> Enter -> 60-tick intro -> fight (embers start) -> P1 walks in
## and punches whenever in range (rapid repeats; P2's kicks hit back) -> Esc 3 ticks after the 4th
## spark, held 180 ticks (3 s), Esc again -> fight to K.O. -> embers stop, fade -> result screen -> Enter (rematch) at K.O. + 200 ticks -> round 2 intro
## -> fight (embers start again) -> quit 240 ticks into round 2's fight.

var main: Node
var frame := 0
var p1_cool := 0
var hits := 0
var pause_at := -1
var resume_at := -1
var ko_frame := -1
var fight2_frame := -1
var held := {}
var last_phase := ""


func _initialize() -> void:
	main = load("res://game/main.tscn").instantiate()
	root.add_child(main)
	_setup.call_deferred()


func _setup() -> void:
	main.round_started.connect(_on_round_started)
	for f in [main.p1, main.p2]:
		f.attack_resolved.connect(_on_attack_resolved)
	process_frame.connect(_tick)


func _on_round_started(_n: int) -> void:
	var segs: Array = [{"frames": 120}]
	for i in 30:
		segs.append({"frames": 1, "attack": "kick"})
		segs.append({"frames": 109})
	main.p2.controller = ScriptedController.new(segs)


func _on_attack_resolved(f: Node, kind: String, result: String, point: Vector2) -> void:
	if result == "hit":
		hits += 1
		print("tick %d  t=%.3fs  HIT #%d by %s (%s) at (%.1f, %.1f)  P1 %d  P2 %d" % [frame, frame / 60.0, hits,
				f.name, kind, point.x, point.y, main.p1.health, main.p2.health])
		if hits == 4 and pause_at < 0:
			pause_at = frame + 3
			resume_at = pause_at + 180
	else:
		print("tick %d  t=%.3fs  %s by %s (%s)" % [frame, frame / 60.0, result, f.name, kind])


func _send(action: String, pressed: bool) -> void:
	if held.get(action, false) == pressed:
		return
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = pressed
	Input.parse_input_event(ev)
	held[action] = pressed


func _tap(action: String) -> void:
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = true
	Input.parse_input_event(ev)
	var up := InputEventAction.new()
	up.action = action
	up.pressed = false
	Input.parse_input_event.call_deferred(up)


func _status() -> String:
	var busy := 0
	for i in 4:
		if main.get_node("HitSpark%d" % i).emitting:
			busy += 1
	var em: CPUParticles2D = main.get_node("Embers")
	return "phase %s paused %s hitstop %d sparks_emitting %d embers_emitting %s embers_speed %.0f" % [
		main.phase, main.paused, main.hitstop, busy, em.emitting, em.speed_scale]


func _tick() -> void:
	frame += 1
	if main.phase != last_phase:
		print("tick %d  t=%.3fs  PHASE -> %s  | %s" % [frame, frame / 60.0, main.phase, _status()])
		last_phase = main.phase
		if main.phase == "ko" and ko_frame < 0:
			ko_frame = frame
	if frame == 90:
		print("tick %d  t=%.3fs  Enter (confirm)" % [frame, frame / 60.0])
		_tap("confirm")
	if frame == pause_at or frame == resume_at:
		print("tick %d  t=%.3fs  Esc (pause toggle)  | before: %s" % [frame, frame / 60.0, _status()])
		_send("p1_right", false)
		_tap("pause")
	if frame % 30 == 0:
		print("tick %d  t=%.3fs  status | %s  P1 x %.1f P2 x %.1f" % [frame, frame / 60.0, _status(),
				main.p1.position.x, main.p2.position.x])
	if main.phase == "fight" and not main.paused:
		var p1: Fighter = main.p1
		var p2: Fighter = main.p2
		var gap: float = p2.position.x - p1.position.x
		var need: float = p1.reach("punch") + p2.body_half_width() - 8.0
		p1_cool -= 1
		if p1.state in ["idle", "walk"]:
			if gap > need:
				_send("p1_right", true)
			else:
				_send("p1_right", false)
				if p1_cool <= 0:
					_tap("p1_punch")
					p1_cool = 22
	else:
		_send("p1_right", false)
	if ko_frame > 0 and frame == ko_frame + 200 and main.phase == "result":
		print("tick %d  t=%.3fs  Enter (confirm, rematch)" % [frame, frame / 60.0])
		_tap("confirm")
	if main.round_number >= 2 and main.phase == "fight" and fight2_frame < 0:
		fight2_frame = frame
	if fight2_frame > 0 and frame >= fight2_frame + 240:
		print("capture done, frames %d; P1 health %d, P2 health %d, hits %d | %s" % [frame, main.p1.health,
				main.p2.health, hits, _status()])
		quit()
	if frame >= 3600:
		print("capture TIMEOUT at 3600 frames")
		quit()
