extends Node2D
## Fight scene and round flow. Steps both fighters once per physics tick, resolves hits after both
## have moved, keeps grounded fighters apart, and runs the phases from the storyboard:
##   title (P1) -> intro "ROUND n - FIGHT" (P2) -> fight (P3-P5) -> ko (P6) -> result (P8)
##   -> confirm = rematch (P7), Esc on the result screen = quit.
## Pause (Esc/P) freezes the fight. Everything is stepped by step(), so tests can drive it.

signal round_started(round_number: int)
signal round_over(winner: Fighter)       # null on a double K.O.
signal paused_changed(paused: bool)

const INTRO_FRAMES := 60
const KO_FRAMES := 90           # input locked after K.O.; the winner poses at WIN_POSE_FRAME
const WIN_POSE_FRAME := 60
const HITSTOP_FRAMES := 4       # both fighters freeze briefly on a clean hit

@onready var p1: Fighter = $P1
@onready var p2: Fighter = $P2
@onready var effects: Node2D = $Effects
@onready var hud: Control = $HUD/Overlay

var phase := "title"
var phase_frame := 0
var round_number := 0
var paused := false
var hitstop := 0
var winner: Fighter = null
var _message_before_pause := ["", ""]


func _ready() -> void:
	p1.opponent = p2
	p2.opponent = p1
	p1.controller = PlayerController.new()
	p2.controller = CpuController.new()
	hud.p1 = p1
	hud.p2 = p2
	for f in [p1, p2]:
		f.attack_resolved.connect(_on_attack_resolved)
		f.knocked_out.connect(_on_knocked_out)
	p1.reset(220.0, 1)
	p2.reset(420.0, -1)
	_show_title()


func _physics_process(delta: float) -> void:
	step(delta)


func step(delta: float) -> void:
	if paused:
		return
	phase_frame += 1
	effects.step()
	if hitstop > 0:
		hitstop -= 1
		return
	var allow := phase == "fight"
	p1.step(delta, allow)
	p2.step(delta, allow)
	if phase == "fight" or phase == "ko":
		p1.check_hit()
		p2.check_hit()
	_separate()
	match phase:
		"intro":
			if phase_frame >= INTRO_FRAMES:
				phase = "fight"
				hud.message = ""
		"ko":
			if phase_frame == WIN_POSE_FRAME and winner:
				winner.win()
			if phase_frame >= KO_FRAMES:
				phase = "result"
				hud.message = "%s WINS" % winner.display_name if winner else "DOUBLE K.O."
				hud.sub_message = "Enter: rematch     Esc: quit"


## Enter on the title or result screen.
func confirm() -> void:
	if phase == "title" or phase == "result":
		start_round()


func start_round() -> void:
	round_number += 1
	p1.reset(220.0, 1)
	p2.reset(420.0, -1)
	p2.controller = CpuController.new(7270 + round_number)
	effects.clear()
	winner = null
	hitstop = 0
	phase = "intro"
	phase_frame = 0
	hud.message = "ROUND %d  -  FIGHT" % round_number
	hud.sub_message = ""
	round_started.emit(round_number)


func set_paused(value: bool) -> void:
	if value == paused or (value and phase != "fight" and phase != "intro"):
		return
	paused = value
	if paused:
		_message_before_pause = [hud.message, hud.sub_message]
		hud.message = "PAUSED"
		hud.sub_message = "Esc / P: resume"
	else:
		hud.message = _message_before_pause[0]
		hud.sub_message = _message_before_pause[1]
	paused_changed.emit(paused)


## For tests and the state capture: skip the title and intro.
func start_fight_now() -> void:
	start_round()
	phase = "fight"
	hud.message = ""


func _show_title() -> void:
	phase = "title"
	hud.message = "DUSK DUEL"
	hud.sub_message = "press Enter"
	hud.hint = "A/D move  W jump  S crouch  J punch  K kick  L block  Esc pause  M/N mute  F1 boxes"


func _on_attack_resolved(f: Fighter, _kind: String, result: String, point: Vector2) -> void:
	if result == "interrupted":
		return
	effects.spawn(result, point, f.facing)
	if result == "hit":
		hitstop = HITSTOP_FRAMES


func _on_knocked_out(_loser: Fighter) -> void:
	if phase == "ko":
		winner = null if (p1.state == "ko" and p2.state == "ko") else winner
		return
	phase = "ko"
	phase_frame = 0
	winner = p2 if p1.state == "ko" else p1
	hud.message = "K.O."
	hud.sub_message = ""
	round_over.emit(winner)


## Grounded fighters push each other apart; jumping over the opponent is allowed.
func _separate() -> void:
	if not (p1.is_grounded() and p2.is_grounded()) or p1.state == "ko" or p2.state == "ko":
		return
	var min_gap := p1.body_half_width() + p2.body_half_width()
	var dx := p2.position.x - p1.position.x
	if absf(dx) >= min_gap:
		return
	var push := (min_gap - absf(dx)) / 2.0
	var dir := signf(dx) if dx != 0.0 else 1.0
	p1.position.x = clampf(p1.position.x - dir * push, Fighter.ARENA_LEFT, Fighter.ARENA_RIGHT)
	p2.position.x = clampf(p2.position.x + dir * push, Fighter.ARENA_LEFT, Fighter.ARENA_RIGHT)


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("confirm"):
		confirm()
	elif event.is_action_pressed("pause"):
		if phase == "result":
			get_tree().quit()
		else:
			set_paused(not paused)
	elif event.is_action_pressed("debug_boxes"):
		for f in [p1, p2]:
			f.show_boxes = not f.show_boxes
			f.queue_redraw()
