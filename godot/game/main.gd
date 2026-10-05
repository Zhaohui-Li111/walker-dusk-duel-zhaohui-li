extends Node2D
## Fight scene. Steps both fighters once per physics tick, keeps them from overlapping on the
## ground, and toggles the collision debug view (F1).
## Step 1 of the slice plan: movement and state images only; no hits, CPU or sound yet.

@onready var p1: Fighter = $P1
@onready var p2: Fighter = $P2


func _ready() -> void:
	p1.opponent = p2
	p2.opponent = p1
	p1.controller = PlayerController.new()
	p2.controller = null          # stands still until the CPU controller exists (step 2)
	p1.facing = 1
	p2.facing = -1


func _physics_process(delta: float) -> void:
	step(delta)


func step(delta: float) -> void:
	p1.step(delta)
	p2.step(delta)
	_separate()


## Grounded fighters push each other apart; jumping over the opponent is allowed.
func _separate() -> void:
	if not (p1.is_grounded() and p2.is_grounded()):
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
	if event.is_action_pressed("debug_boxes"):
		for f in [p1, p2]:
			f.show_boxes = not f.show_boxes
			f.queue_redraw()
