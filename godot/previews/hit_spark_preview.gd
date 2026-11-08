extends Node2D
## A6 Effect A preview (CHANGE-BRIEF.md, Effect A "The frame strip"). Not gameplay: the effect is
## not wired into main.tscn. The 640 x 360 root viewport with no Camera2D is the in-game camera
## scale (project.godot canvas_items stretch, 1280 x 720 window); bg.png is drawn 1:1 as stage.gd does.
## Holds a pool of four hit_spark.tscn instances as children of this root (rule 4's stand-in for
## Main). Fires a burst at process frame 10, and at frame 22 when `retrigger` is on, into the next
## slot, so the second burst does not restart the first (rule 3). No hitstop in the preview.
## Command-line overrides, after `--`: --no-retrigger, --lantern.

const SPARK := preload("res://effects/hit_spark.tscn")
const SLOTS := 4
const FIRST_FRAME := 10
const RETRIGGER_FRAME := 22          # brief: 0.4 s after frame 10 at 30 fps
## Brief's preview background points in the hit band y 200-260.
const DARK_POINT := Vector2(364, 202)
const LANTERN_POINT := Vector2(510, 208)

@export var retrigger := true
@export var at_lantern := false
## GPU price (A6 "Use It"): keeps all four bursts alive (one new burst every lifetime / 4) so the
## Visual Profiler sees Effect A at its heaviest. Space toggles it on and off. Used by
## hit_spark_profile.tscn only; the strips never set it.
@export var profile_loop := false
var _profile_on := true
var _profile_clock := 0.0

var slots: Array[CPUParticles2D] = []
var fired := 0
var frame := 0


func _ready() -> void:
	var args := OS.get_cmdline_user_args()
	if "--no-retrigger" in args:
		retrigger = false
	if "--lantern" in args:
		at_lantern = true
	for i in SLOTS:
		var fx := SPARK.instantiate() as CPUParticles2D
		fx.name = "Slot%d" % i
		# Fixed seed on the preview's instances only, never in hit_spark.tscn, so before/after
		# strips compare the same randomness (A6 handout, "Controlled randomness").
		fx.use_fixed_seed = true
		fx.seed = 7270 + i
		add_child(fx)
		slots.append(fx)
	print("hit_spark_preview: retrigger %s, point %s" % [retrigger, _point()])


func _unhandled_input(event: InputEvent) -> void:
	if profile_loop and event is InputEventKey and event.pressed and not event.echo \
			and event.keycode == KEY_SPACE:
		_profile_on = not _profile_on
		print("hit_spark_preview: profile bursts %s" % ("on (4 alive)" if _profile_on else "off"))


func _process(delta: float) -> void:
	if profile_loop:
		_profile_clock += delta
		var step := slots[0].lifetime / SLOTS
		if _profile_on and _profile_clock >= step:
			_profile_clock = 0.0
			_fire(_point())
		return
	if frame == FIRST_FRAME or (retrigger and frame == RETRIGGER_FRAME):
		_fire(_point())
	frame += 1


func _point() -> Vector2:
	return LANTERN_POINT if at_lantern else DARK_POINT


## Next slot in turn: with one lifetime for every burst, that is the free one, or else the oldest.
func _fire(point: Vector2) -> void:
	var fx := slots[fired % SLOTS]
	fx.position = point
	fx.restart()
	print("hit_spark_preview: frame %d, burst %d in %s at %s" % [frame, fired, fx.name, point])
	fired += 1
