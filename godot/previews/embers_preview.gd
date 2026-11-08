extends Node2D
## A6 Effect B preview (CHANGE-BRIEF.md, Effect B "The frame strip"). Not gameplay: the effect is
## not wired into main.tscn. The 640 x 360 root viewport with no Camera2D is the in-game camera
## scale (project.godot canvas_items stretch, 1280 x 720 window); bg.png is drawn 1:1 as stage.gd
## does, so the whole wall/sky, lantern and lower-wall area is behind the emitter rectangle.
## Holds one embers.tscn instance at the scene's own position (320, 215). The condition
## (phase == "fight") begins at process frame 10 (emitting = true) and ends at frame 100
## (emitting = false); live particles then finish their 2.5 s lifetime. No pause or hitstop.
## Command-line override, after `--`: --restart calls restart() at frame 10 instead of only setting
## emitting, for the brief's open question 3 (does preprocess run when emitting turns on later?).

const EMBERS := preload("res://effects/embers.tscn")
const START_FRAME := 10
const END_FRAME := 100

@export var use_restart := false

var fx: CPUParticles2D
var frame := 0


func _ready() -> void:
	if "--restart" in OS.get_cmdline_user_args():
		use_restart = true
	fx = EMBERS.instantiate() as CPUParticles2D
	# Fixed seed on the preview's instance only, never in embers.tscn, so before/after strips
	# compare the same randomness (A6 handout, "Controlled randomness").
	fx.use_fixed_seed = true
	fx.seed = 7270
	add_child(fx)
	print("embers_preview: start frame %d, end frame %d, restart %s, emitter at %s" % [START_FRAME,
			END_FRAME, use_restart, fx.position])


func _process(_delta: float) -> void:
	if frame == START_FRAME:
		fx.emitting = true
		if use_restart:
			fx.restart()
		print("embers_preview: frame %d, condition begins, emitting %s" % [frame, fx.emitting])
	elif frame == END_FRAME:
		fx.emitting = false
		print("embers_preview: frame %d, condition ends, emitting %s" % [frame, fx.emitting])
	frame += 1
