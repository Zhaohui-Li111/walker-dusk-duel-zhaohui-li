extends Node
## Hurt flash driver (A5). A child of the fighter's Sprite2D. Gives that sprite its own
## ShaderMaterial of hurt_flash.gdshader, so a hit on one fighter never flashes the other, and
## sets hurt_amount once per physics tick from the fighter's state. Presentation only: it reads
## state and stun and never writes game state. flash_color keeps the shader's default.

const SHADER := preload("res://shaders/hurt_flash.gdshader")

var material: ShaderMaterial

@onready var sprite: Sprite2D = get_parent()
@onready var fighter: Fighter = sprite.get_parent()


func _ready() -> void:
	# main.gd steps the fighters at the default priority 0; a higher value runs after it, so the
	# value set here is the one for the state of this same tick.
	process_physics_priority = 100
	material = ShaderMaterial.new()
	material.shader = SHADER
	sprite.material = material


func _physics_process(_delta: float) -> void:
	var amount := 0.0
	if fighter.state == "hurt":
		amount = float(fighter.stun) / float(Fighter.HITSTUN)
	material.set_shader_parameter("hurt_amount", amount)
