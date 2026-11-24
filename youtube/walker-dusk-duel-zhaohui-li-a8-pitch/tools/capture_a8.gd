extends SceneTree
## A8 pitch: Movie Maker capture of one full round on an isolated copy (capture/game, source
## revision dff6cba; godot/ unchanged since 8049c54; nothing in the game is changed).
##   godot --path capture/game --write-movie <ABSOLUTE>/capture/a8_round.avi --fixed-fps 60
##         --disable-vsync --resolution 3840x2160 --script res://capture_a8.gd
## Adapted from the A7 reel's capture_a7.gd. SCRIPTED INPUT, labelled as such in the film:
##   - P1 (Akaken) is driven by a small capture bot in this file. It only sends InputEventActions
##     (p1_right, p1_punch, p1_kick, p1_block, confirm) through Input.parse_input_event; P1's real
##     PlayerController reads them. The bot reads positions and states; it writes nothing.
##   - P2 (Aotake) is the game's own CpuController, untouched (seeded 7270 + round number).
## Timeline: title held 240 ticks (4 s) -> Enter -> intro -> fight until K.O. -> result screen held
##   150 ticks -> Enter (rematch) -> round 2 intro and 360 fight ticks -> quit.
## Every phase change, hit, block, whiff and K.O. is logged with its tick.

const TITLE_HOLD := 240
const RESULT_HOLD := 150
const ROUND2_HOLD := 360
const ATTACK_GAP := 26              # ticks between P1 attacks
const BLOCK_TICKS := 18

var main: Node
var frame := 0
var held := {}
var last_phase := ""
var phase_tick := 0
var cooldown := 0
var block_left := 0
var attack_count := 0
var p2_attacks_seen := 0
var p2_was_attacking := false
var confirmed_rematch := false


func _initialize() -> void:
	main = load("res://game/main.tscn").instantiate()
	root.add_child(main)
	_setup.call_deferred()


func _setup() -> void:
	for f in [main.p1, main.p2]:
		f.attack_resolved.connect(_on_attack_resolved)
		f.knocked_out.connect(_on_ko.bind(f))
	process_frame.connect(_tick)
	print("reach punch P1 %.1f kick P1 %.1f; P2 half width %.1f" % [main.p1.reach("punch"),
			main.p1.reach("kick"), main.p2.body_half_width()])


func _on_attack_resolved(f: Node, kind: String, result: String, _point: Vector2) -> void:
	print("tick %d  t=%.3fs  %s by %s (%s) | P1 health %d  P2 health %d" % [frame, frame / 60.0,
			result.to_upper(), f.name, kind, main.p1.health, main.p2.health])


func _on_ko(_a = null, f: Node = null) -> void:
	print("tick %d  t=%.3fs  K.O. %s" % [frame, frame / 60.0, f.name if f else "?"])


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


func _release_all() -> void:
	for a in ["p1_right", "p1_block"]:
		_send(a, false)


func _bot() -> void:
	var p1: Fighter = main.p1
	var p2: Fighter = main.p2
	cooldown = maxi(cooldown - 1, 0)
	var gap: float = p2.position.x - p1.position.x
	var punch_range: float = p1.reach("punch") + p2.body_half_width() - 2.0
	# Block every second CPU attack that starts close by (deterministic, so the run repeats).
	var attacking: bool = p2.is_attacking()
	if attacking and not p2_was_attacking:
		p2_attacks_seen += 1
		if gap < 110.0 and p2_attacks_seen % 2 == 0:
			block_left = BLOCK_TICKS
	p2_was_attacking = attacking
	if block_left > 0:
		block_left -= 1
		_send("p1_right", false)
		_send("p1_block", true)
		return
	_send("p1_block", false)
	if gap > punch_range:
		_send("p1_right", true)
		return
	_send("p1_right", false)
	if cooldown == 0 and p1.state == "idle":
		attack_count += 1
		_tap("p1_kick" if attack_count % 3 == 0 else "p1_punch")
		cooldown = ATTACK_GAP


func _tick() -> void:
	frame += 1
	if main.phase != last_phase:
		print("tick %d  t=%.3fs  PHASE %s -> %s | P1 health %d  P2 health %d" % [frame, frame / 60.0,
				last_phase, main.phase, main.p1.health, main.p2.health])
		last_phase = main.phase
		phase_tick = frame
	match main.phase:
		"title":
			if frame == TITLE_HOLD:
				_tap("confirm")
		"fight":
			if main.round_number == 1:
				_bot()
			else:
				_release_all()
				if frame - phase_tick >= ROUND2_HOLD:
					print("capture done, frames %d; round %d" % [frame, main.round_number])
					quit()
		"ko":
			_release_all()
		"result":
			if not confirmed_rematch and frame - phase_tick >= RESULT_HOLD:
				confirmed_rematch = true
				_tap("confirm")
	if frame >= 7200:
		print("capture TIMEOUT at 7200 frames; P1 health %d, P2 health %d" % [main.p1.health,
				main.p2.health])
		quit()
