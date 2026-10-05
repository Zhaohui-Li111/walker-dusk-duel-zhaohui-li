class_name Fighter
extends Node2D
## One fighter. Movement and timing are stepped by main.gd once per physics tick (fixed 60 Hz)
## with simple custom kinematics instead of the physics engine, so a scripted test can step it
## frame by frame and get the same result every run.
##
## The origin is the point between the feet on the ground; art and boxes are placed relative to it
## by FighterArt. Each state shows one static image.

signal state_changed(fighter: Fighter, state: String)
signal attack_started(fighter: Fighter, kind: String)

@export var fighter_id := "akaken"
@export var display_name := "AKAKEN"

const GROUND_Y := 305.0
const ARENA_LEFT := 24.0
const ARENA_RIGHT := 616.0
const WALK_FORWARD := 90.0     # px/s
const WALK_BACK := 70.0
const JUMP_SPEED := 330.0
const GRAVITY := 900.0

## Frame data at 60 fps. The state image is shown for the whole attack.
const ATTACKS := {
	"punch": {"startup": 4, "active": 4, "recovery": 10, "damage": 8},
	"kick": {"startup": 7, "active": 5, "recovery": 16, "damage": 14},
}

var controller = null           # anything with read(fighter) -> Intent
var opponent: Fighter
var art: FighterArt
var state := "idle"
var frame := 0                  # frames spent in the current state
var facing := 1                 # 1 = facing right, -1 = facing left
var velocity := Vector2.ZERO
var show_boxes := false

@onready var sprite: Sprite2D = $Sprite2D


func _ready() -> void:
	art = FighterArt.load_for(fighter_id)
	var placeholders := []
	for s in art.sources:
		if art.sources[s] == "placeholder":
			placeholders.append(s)
	if placeholders:
		print("%s: placeholder art for %s" % [display_name, ", ".join(placeholders)])
	_update_sprite()


func step(delta: float) -> void:
	var it: Intent = controller.read(self) if controller else Intent.new()
	frame += 1
	match state:
		"idle", "walk", "crouch", "block":
			_ground_control(it)
		"punch", "kick":
			velocity.x = 0.0
			var a: Dictionary = ATTACKS[state]
			if frame >= a["startup"] + a["active"] + a["recovery"]:
				_set_state("idle")
	_move(delta)
	_update_sprite()


func _ground_control(it: Intent) -> void:
	_face_opponent()
	if it.attack != "":
		velocity.x = 0.0
		_set_state(it.attack)
		attack_started.emit(self, it.attack)
	elif it.block:
		velocity.x = 0.0
		_set_state("block")
	elif it.jump:
		velocity = Vector2(it.move * WALK_FORWARD, -JUMP_SPEED)
		_set_state("jump")
	elif it.crouch:
		velocity.x = 0.0
		_set_state("crouch")
	elif absf(it.move) > 0.1:
		var forward := signf(it.move) == float(facing)
		velocity.x = signf(it.move) * (WALK_FORWARD if forward else WALK_BACK)
		_set_state("walk")
	else:
		velocity.x = 0.0
		_set_state("idle")


func _move(delta: float) -> void:
	if state == "jump":
		velocity.y += GRAVITY * delta
		position += velocity * delta
		if position.y >= GROUND_Y:
			position.y = GROUND_Y
			velocity = Vector2.ZERO
			_set_state("idle")
	else:
		position.x += velocity.x * delta
	position.x = clampf(position.x, ARENA_LEFT, ARENA_RIGHT)


func _face_opponent() -> void:
	if opponent and absf(opponent.position.x - position.x) > 1.0:
		facing = 1 if opponent.position.x > position.x else -1


func _set_state(s: String) -> void:
	if s == state:
		return
	state = s
	frame = 0
	state_changed.emit(self, s)


func is_grounded() -> bool:
	return state != "jump"


## The image shown for the current state; jump splits into rising and falling.
func art_state() -> String:
	if state == "jump":
		return "rise" if velocity.y < 0.0 else "fall"
	return state


func hurtbox() -> Variant:
	var s := art.resolve(art_state())
	if not art.hurtboxes.has(s):
		return null
	var r := FighterArt.mirror(art.hurtboxes[s], facing)
	return Rect2(r.position + position, r.size)


func body_half_width() -> float:
	return art.hurtboxes["idle"].size.x / 2.0


func _update_sprite() -> void:
	var s := art_state()
	sprite.texture = art.textures[art.resolve(s)]
	sprite.flip_h = facing < 0
	sprite.offset = art.offset_for(s, facing)
	queue_redraw()


func _draw() -> void:
	if not show_boxes:
		return
	var s := art.resolve(art_state())
	if art.hurtboxes.has(s):
		draw_rect(FighterArt.mirror(art.hurtboxes[s], facing), Color(0, 0.8, 0.3), false, 1.0)
	if art.hitboxes.has(s):
		draw_rect(FighterArt.mirror(art.hitboxes[s], facing), Color(0.9, 0.15, 0.15), false, 1.0)
	draw_line(Vector2(-4, 0), Vector2(4, 0), Color.WHITE, 1.0)
