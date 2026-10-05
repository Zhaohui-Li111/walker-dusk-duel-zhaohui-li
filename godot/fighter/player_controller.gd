class_name PlayerController
extends RefCounted
## Reads the p1_* actions registered by game/controls.gd.


func read(_fighter: Fighter) -> Intent:
	var it := Intent.new()
	it.move = Input.get_axis("p1_left", "p1_right")
	it.jump = Input.is_action_just_pressed("p1_jump")
	it.crouch = Input.is_action_pressed("p1_crouch")
	it.block = Input.is_action_pressed("p1_block")
	# just_pressed only: holding the button never repeats an attack.
	if Input.is_action_just_pressed("p1_punch"):
		it.attack = "punch"
	elif Input.is_action_just_pressed("p1_kick"):
		it.attack = "kick"
	return it
