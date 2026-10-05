class_name CpuController
extends RefCounted
## Aotake's simple opponent logic. It re-decides every REACTION frames (so it reacts late, like a
## person) and holds that decision in between. The random generator is seeded, so a scripted run
## behaves the same every time.
##   - opponent attacking and close: block (BLOCK_CHANCE)
##   - out of kick range: walk in
##   - in range and cooled down: kick (KICK_CHANCE)
##   - too close: step back to kicking distance

const REACTION := 10
const BLOCK_CHANCE := 0.55
const KICK_CHANCE := 0.5
const KICK_COOLDOWN := 40

var rng := RandomNumberGenerator.new()
var plan := Intent.new()
var plan_frames := 0
var cooldown := 0
var attack_sent := false


func _init(seed_value := 7270) -> void:
	rng.seed = seed_value


func read(f: Fighter) -> Intent:
	cooldown = maxi(cooldown - 1, 0)
	if plan_frames <= 0:
		_decide(f)
	plan_frames -= 1
	var it := Intent.new()
	it.move = plan.move
	it.block = plan.block
	if plan.attack != "" and not attack_sent:   # one press per decision
		it.attack = plan.attack
		attack_sent = true
	return it


func _decide(f: Fighter) -> void:
	plan = Intent.new()
	plan_frames = REACTION
	attack_sent = false
	var o := f.opponent
	var dx := o.position.x - f.position.x
	var dist := absf(dx)
	var toward := signf(dx)
	var kick_range := f.reach("kick") + o.body_half_width() - 4.0
	if o.is_attacking() and dist < kick_range + 20.0 and rng.randf() < BLOCK_CHANCE:
		plan.block = true
		plan_frames = 20
	elif dist > kick_range:
		plan.move = toward
	elif dist < kick_range * 0.6:
		plan.move = -toward
	elif cooldown == 0 and rng.randf() < KICK_CHANCE:
		plan.attack = "kick"
		cooldown = KICK_COOLDOWN
