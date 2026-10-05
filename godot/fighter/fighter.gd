class_name Fighter
extends Node2D
## One fighter. Movement, timing and hits are stepped by main.gd once per physics tick (fixed
## 60 Hz) with simple custom kinematics instead of the physics engine, so a scripted test can
## step it frame by frame and get the same result every run.
##
## The origin is the point between the feet on the ground; art and boxes are placed relative to it
## by FighterArt. Each state shows one static image.
##
## Every attack is resolved exactly once, by attack_resolved(result):
##   "hit"         hitbox met a hurtbox that was not blocking
##   "blocked"     hitbox met a fighter blocking toward the attacker
##   "whiff"       the active window ended without contact
##   "interrupted" the attacker was hit before the attack resolved
## Sounds and effects listen to this signal; they never decide anything themselves.

signal state_changed(fighter: Fighter, state: String)
signal attack_started(fighter: Fighter, kind: String)
signal attack_resolved(fighter: Fighter, kind: String, result: String, point: Vector2)
signal health_changed(fighter: Fighter, health: int)
signal knocked_out(fighter: Fighter)

@export var fighter_id := "akaken"
@export var display_name := "AKAKEN"

const GROUND_Y := 305.0
const ARENA_LEFT := 24.0
const ARENA_RIGHT := 616.0
const WALK_FORWARD := 90.0     # px/s
const WALK_BACK := 70.0
const JUMP_SPEED := 330.0
const GRAVITY := 900.0
const MAX_HEALTH := 100

## Frame data at 60 fps. The state image is shown for the whole attack.
const ATTACKS := {
	"punch": {"startup": 4, "active": 4, "recovery": 10, "damage": 8},
	"kick": {"startup": 7, "active": 5, "recovery": 16, "damage": 14},
}
const HITSTUN := 18
const BLOCKSTUN := 10
const HIT_PUSH := 120.0        # px/s away from the attacker, decays during stun
const BLOCK_PUSH := 70.0

var controller = null           # anything with read(fighter) -> Intent
var opponent: Fighter
var art: FighterArt
var state := "idle"
var frame := 0                  # frames spent in the current state
var facing := 1                 # 1 = facing right, -1 = facing left
var velocity := Vector2.ZERO
var health := MAX_HEALTH
var stun := 0                   # frames left in hitstun or blockstun
var attack_kind := ""           # attack in progress, "" if none
var attack_done := false        # this attack already resolved
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


func reset(x: float, face: int) -> void:
	position = Vector2(x, GROUND_Y)
	facing = face
	velocity = Vector2.ZERO
	health = MAX_HEALTH
	stun = 0
	attack_kind = ""
	_set_state("idle")
	health_changed.emit(self, health)
	_update_sprite()


## One frame of movement and timing. Hits are checked afterwards by check_hit(), once both
## fighters have moved. allow_input = false during intros, KO and results.
func step(delta: float, allow_input := true) -> void:
	var it: Intent = controller.read(self) if (controller and allow_input) else Intent.new()
	frame += 1
	match state:
		"idle", "walk", "crouch":
			_ground_control(it)
		"block":
			if stun > 0:
				stun -= 1
				velocity.x *= 0.85
			else:
				_ground_control(it)
		"punch", "kick":
			velocity.x = 0.0
			var a: Dictionary = ATTACKS[state]
			if not attack_done and frame > a["startup"] + a["active"]:
				var reach_box: Variant = _box(art.hitboxes)
				_resolve("whiff", (reach_box as Rect2).get_center() if reach_box != null else position)
			if frame >= a["startup"] + a["active"] + a["recovery"]:
				attack_kind = ""
				_set_state("idle")
		"hurt":
			stun -= 1
			velocity.x *= 0.85
			if stun <= 0:
				_set_state("idle")
		"ko", "win":
			velocity.x = 0.0
	_move(delta)
	_update_sprite()


func _ground_control(it: Intent) -> void:
	_face_opponent()
	if it.attack != "":
		velocity.x = 0.0
		attack_kind = it.attack
		attack_done = false
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


## Called by main.gd after both fighters have stepped. Resolves at most once per attack.
func check_hit() -> void:
	if attack_kind == "" or attack_done or state != attack_kind:
		return
	var a: Dictionary = ATTACKS[attack_kind]
	if frame <= a["startup"] or frame > a["startup"] + a["active"]:
		return
	var hb: Variant = hitbox()
	var hurt: Variant = opponent.hurtbox()
	if hb == null or hurt == null or not (hb as Rect2).intersects(hurt):
		return
	var point: Vector2 = (hb as Rect2).intersection(hurt).get_center()
	var blocked := opponent.receive_hit(self, a["damage"])
	_resolve("blocked" if blocked else "hit", point)


## Returns true if the hit was blocked. Health and state change here; nothing else does.
func receive_hit(attacker: Fighter, damage: int) -> bool:
	var away := -1.0 if attacker.position.x > position.x else 1.0
	var facing_attacker := (attacker.position.x - position.x) * facing > 0.0
	if state == "block" and facing_attacker:
		stun = BLOCKSTUN
		frame = 0
		velocity.x = away * BLOCK_PUSH
		return true
	if attack_kind != "" and not attack_done:
		_resolve("interrupted", Vector2.ZERO)
	attack_kind = ""
	health = maxi(health - damage, 0)
	health_changed.emit(self, health)
	if state == "jump":
		position.y = GROUND_Y          # knocked out of the air: land at once
	if health == 0:
		velocity = Vector2.ZERO
		_set_state("ko")
		knocked_out.emit(self)
	else:
		stun = HITSTUN
		velocity = Vector2(away * HIT_PUSH, 0.0)
		state = ""                      # force state_changed even when already hurt
		_set_state("hurt")
		_face_opponent()
	_update_sprite()                    # show hurt/KO at once, even during hitstop
	return false


func win() -> void:
	if state != "ko":
		attack_kind = ""
		position.y = GROUND_Y
		velocity = Vector2.ZERO
		_set_state("win")
		_update_sprite()


func _resolve(result: String, point: Vector2) -> void:
	attack_done = true
	attack_resolved.emit(self, attack_kind, result, point)


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


func is_attacking() -> bool:
	return attack_kind != ""


## The image shown for the current state; jump splits into rising and falling.
func art_state() -> String:
	if state == "jump":
		return "rise" if velocity.y < 0.0 else "fall"
	return state


func hurtbox() -> Variant:
	return _box(art.hurtboxes)


## Only during an attack's active frames.
func hitbox() -> Variant:
	if attack_kind == "":
		return null
	var a: Dictionary = ATTACKS[attack_kind]
	if frame <= a["startup"] or frame > a["startup"] + a["active"]:
		return null
	return _box(art.hitboxes)


func _box(boxes: Dictionary) -> Variant:
	var s := art.resolve(art_state())
	if not boxes.has(s):
		return null
	var r := FighterArt.mirror(boxes[s], facing)
	return Rect2(r.position + position, r.size)


func body_half_width() -> float:
	return art.hurtboxes["idle"].size.x / 2.0


## Horizontal reach of an attack from this fighter's origin, for the CPU.
func reach(kind: String) -> float:
	var s := art.resolve(kind)
	return art.hitboxes[s].end.x if art.hitboxes.has(s) else 0.0


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
		var live := hitbox() != null
		draw_rect(FighterArt.mirror(art.hitboxes[s], facing),
				Color(0.9, 0.15, 0.15) if live else Color(0.9, 0.15, 0.15, 0.35), false, 1.0)
	draw_line(Vector2(-4, 0), Vector2(4, 0), Color.WHITE, 1.0)
