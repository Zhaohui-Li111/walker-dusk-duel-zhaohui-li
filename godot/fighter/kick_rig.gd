extends Node2D
## A7 Clip 2, the kick arc's controller (CHANGE-BRIEF.md, "The state machine", "The two clocks").
## The fighter's state machine (fighter.gd) is read, never written. Each physics tick, after main
## has stepped the fighters, this positions the clip from the fighter's own frame counter:
##   state "kick"      -> kick_arc at Fighter.frame / 60   (seek(t, true) applies the keys at once)
##   any other state   -> rest (the arc hidden): an interrupted kick or a round reset returns here
## The player is on ANIMATION_CALLBACK_MODE_PROCESS_MANUAL, so it never advances by itself: hitstop
## and the game's pause stop Fighter.frame and so freeze the arc on the same tick.
## One authority (CLAUDE.md): the AnimationPlayer is the only writer to Pivot and its segments;
## this script is the only writer to KickRig's own position and scale (hip pivot, size from this
## fighter's kick hitbox, flipped with facing). It never touches the fighter's Sprite2D.

const FPS := 60.0                    # the phase table's frame rate; Fighter.frame counts 60 Hz ticks
const CLIP_RADIUS := 38.0            # the arc's radius in kick_arc's polygons
const PIVOT_ABOVE_HITBOX := 10.0     # pivot = (0, kick hitbox centre y + 10): at the hip

@onready var fighter: Fighter = get_parent()
@onready var player: AnimationPlayer = $AnimationPlayer

var _size := 0.0                     # set on the first tick: fighter.art loads in Fighter._ready


func _ready() -> void:
	process_physics_priority = 100   # after Main (0), which steps the fighters and checks hits, and
	                                 # after a test harness's in-tick SETUP hit (priority 50)


func _physics_process(_delta: float) -> void:
	if _size == 0.0:
		_fit()
	scale = Vector2(fighter.facing * _size, _size)
	if fighter.state == "kick":
		if player.current_animation != "kick_arc":
			player.play("kick_arc")
		player.seek(fighter.frame / FPS, true)
	elif player.current_animation != "rest":
		player.play("rest")
		player.seek(0.0, true)


## Pivot at the hip, size so the arc's leading edge reaches this fighter's kick hitbox centre.
func _fit() -> void:
	var hb: Rect2 = fighter.art.hitboxes[fighter.art.resolve("kick")]
	var centre := hb.get_center()
	position = Vector2(0.0, centre.y + PIVOT_ABOVE_HITBOX)
	_size = Vector2(centre.x, -PIVOT_ABOVE_HITBOX).length() / CLIP_RADIUS
