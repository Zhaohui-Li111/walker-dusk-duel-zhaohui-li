extends Node2D
## A7 Clip 1, lantern flame (CHANGE-BRIEF.md, "Lantern decisions"). Starts the `flicker` clip once,
## at this instance's start offset (0.0 left, 0.4 right). That is all it does: the AnimationPlayer
## is the only writer to Sprite2D.frame (CLAUDE.md, "One authority"); this script never touches
## the sprite, reads no game state, and keeps burning through the game's pause and hitstop (L1).

@export var start_offset := 0.0      # seconds into `flicker`; set per instance in main.tscn

@onready var player: AnimationPlayer = $AnimationPlayer


func _ready() -> void:
	player.play("flicker")
	player.seek(start_offset, true)
