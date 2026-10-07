extends Node
## Capture harness for the gamedev film (added as an autoload to the isolated copy in capture/game
## only; the game's own scripts are not changed). It plays Akaken by sending keyboard events, the
## same InputEventKey a player's keyboard produces, and never sets fighter state, health or
## position. Aotake is the game's own seeded CpuController.
##
## The route reads the screen state each tick (distance, whether Aotake is attacking) the way a
## player watching would, so it is a scripted bot, not a human playtest; the film labels it so.
## Every key press and release is logged to run-01-inputs.jsonl, and the outcomes the film
## narrates are asserted into run-01-driver.json.

const TITLE_WAIT := 90                  # ticks on the title screen before Enter
const RESULT_WAIT := 150                # ticks on the result screen before the rematch
const AFTER_REMATCH := 110
const PAUSE_AT := 640                   # fight tick at which the bot pauses, and for how long
const PAUSE_LEN := 100

var tick := 0
var fight_tick := 0
var held := {}                          # keycode -> ticks left to hold
var main: Node
var log_lines: PackedStringArray = []
var events := {"whiff": 0, "hit": 0, "blocked": 0, "ko": 0}
var p1_hits_taken := 0
var paused_once := false
var rematch_tick := -1
var cooldown := 0
var block_left := 0
var attacks_seen := 0
var next_attack := "punch"
var opened_with_whiff := false
var done := false


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS


func _physics_process(_delta: float) -> void:
	if done:
		return
	if main == null:
		main = get_tree().current_scene
		if main == null or not main.has_method("confirm"):
			main = null
			return
		for f in [main.p1, main.p2]:
			f.attack_resolved.connect(_on_resolved)
		main.p1.health_changed.connect(func(_f, _h): p1_hits_taken += 1)
		main.p2.knocked_out.connect(func(_f): events["ko"] += 1)
	tick += 1
	_release_expired()
	match main.phase:
		"title":
			if tick == TITLE_WAIT:
				_tap(KEY_ENTER, 3)
		"fight":
			fight_tick += 1
			_fight()
		"result":
			if rematch_tick < 0:
				rematch_tick = tick + RESULT_WAIT
			elif tick == rematch_tick:
				_tap(KEY_ENTER, 3)
	if rematch_tick > 0 and main.round_number == 2 and tick >= rematch_tick + AFTER_REMATCH:
		_finish()


func _fight() -> void:
	if main.paused:
		return
	var p1: Fighter = main.p1
	var p2: Fighter = main.p2
	if fight_tick == PAUSE_AT and not paused_once:
		paused_once = true
		_tap(KEY_ESCAPE, 3)
		_schedule_resume()
		return
	cooldown = maxi(cooldown - 1, 0)
	var dist := absf(p2.position.x - p1.position.x)
	var toward := KEY_D if p2.position.x > p1.position.x else KEY_A
	var punch_range := p1.reach("punch") + p2.body_half_width() - 2.0
	# 1. Open with a punch thrown from far away: the whiff the storyboard starts with.
	if not opened_with_whiff and fight_tick == 20:
		opened_with_whiff = true
		_tap(KEY_J, 3)
		cooldown = 40
		return
	# 2. Block every other attack Aotake starts while close; take the rest.
	if block_left > 0:
		block_left -= 1
		_hold(KEY_L, 2)
		return
	if p2.is_attacking() and p2.frame == 1:
		attacks_seen += 1
		if attacks_seen % 2 == 1 and dist < 130.0:
			block_left = 22
			_hold(KEY_L, 2)
			return
	if cooldown > 0 or p1.is_attacking() or p1.state == "hurt" or p1.state == "block":
		return
	# 3. Walk in, then alternate punch and kick.
	if dist > punch_range:
		_hold(toward, 2)
	else:
		_tap(KEY_J if next_attack == "punch" else KEY_K, 3)
		next_attack = "kick" if next_attack == "punch" else "punch"
		cooldown = 34


func _schedule_resume() -> void:
	await get_tree().create_timer(PAUSE_LEN / 60.0, true, true).timeout
	_tap(KEY_ESCAPE, 3)


func _on_resolved(f: Fighter, kind: String, result: String, _point: Vector2) -> void:
	if events.has(result):
		events[result] += 1
	log_lines.append(JSON.stringify({"tick": tick, "fight_tick": fight_tick, "fighter": f.name,
		"attack": kind, "result": result}))


func _tap(key: Key, ticks: int) -> void:
	_send(key, true)
	held[key] = ticks


func _hold(key: Key, ticks: int) -> void:
	if not held.has(key):
		_send(key, true)
	held[key] = maxi(held.get(key, 0), ticks)


func _release_expired() -> void:
	for key in held.keys():
		held[key] -= 1
		if held[key] <= 0:
			held.erase(key)
			_send(key, false)


func _send(key: Key, pressed: bool) -> void:
	var e := InputEventKey.new()
	e.physical_keycode = key
	e.keycode = key
	e.pressed = pressed
	Input.parse_input_event(e)
	log_lines.append(JSON.stringify({"tick": tick, "key": OS.get_keycode_string(key),
		"pressed": pressed, "phase": main.phase if main else ""}))


func _finish() -> void:
	done = true
	var dir := ProjectSettings.globalize_path("res://").path_join("..")
	var inputs := FileAccess.open(dir.path_join("run-01-inputs.jsonl"), FileAccess.WRITE)
	inputs.store_string("\n".join(log_lines) + "\n")
	inputs.close()
	var checks := {
		"opened_with_whiff": events["whiff"] >= 1,
		"akaken_hit_aotake": events["hit"] >= 1,
		"a_block_happened": events["blocked"] >= 1,
		"akaken_was_hurt": p1_hits_taken >= 1,
		"aotake_knocked_out": events["ko"] == 1,
		"paused_once": paused_once,
		"rematch_started": main.round_number == 2,
	}
	var ok := true
	for k in checks:
		ok = ok and checks[k]
	var summary := FileAccess.open(dir.path_join("run-01-driver.json"), FileAccess.WRITE)
	summary.store_string(JSON.stringify({"ticks": tick, "events": events,
		"p1_health_changes": p1_hits_taken, "checks": checks, "all_passed": ok}, "  "))
	summary.close()
	print("capture driver: ", "PASS" if ok else "FAIL", " ", checks, " ", events)
	get_tree().quit(0 if ok else 1)
