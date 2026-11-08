extends SceneTree
## A6 Effect B (courtyard embers / dust): reads every setting in CHANGE-BRIEF.md's Effect B settings
## table back from the loaded scene and its resources. Expected values are the brief's. Run from the
## repo root:
##   scripts/run-test.sh test_embers_config.gd 60
## Also checks that every property the scene file sets exists on its class in this Godot build, so a
## Godot 3 name (predicted failure 6) fails here instead of being dropped on load, and that the
## feature Effect A doesn't use (rectangle emission, non-zero preprocess) is set here and not there.
## Rules 3 and 5 are read as settings: process_mode INHERIT, and not emitting after load.
## One value is not from the brief and is marked as such: the scale curve's tangents (linear).

const SCENE := "res://effects/embers.tscn"
const TEXTURE := "res://effects/embers_soft.png"
const EFFECT_A := "res://effects/hit_spark.tscn"
const EPS := 1e-4
const COLOR_EPS := 0.5 / 255.0

## Brief, Effect B settings table and rules: property -> expected value.
const EXPECTED := {
	"amount": 48,
	"one_shot": false,
	"explosiveness": 0.0,
	"lifetime": 2.5,
	"emission_shape": CPUParticles2D.EMISSION_SHAPE_RECTANGLE,
	"emission_rect_extents": Vector2(280, 90),
	"position": Vector2(320, 215),
	"initial_velocity_min": 4.0,
	"initial_velocity_max": 14.0,
	"spread": 180.0,
	"gravity": Vector2(0, -2),
	"damping_min": 1.0,
	"damping_max": 3.0,
	"angle_min": 0.0,
	"angle_max": 360.0,
	"scale_amount_min": 0.6,
	"scale_amount_max": 1.2,
	"local_coords": false,
	"preprocess": 1.5,
	"speed_scale": 1.0,
	"process_mode": Node.PROCESS_MODE_INHERIT,   # rule 3: freezes when the tree is paused
	"emitting": false,               # rule 5: phase is "title" when the scene loads
	"visible": true,                 # rule 4: visibility is not a phase switch
}
## color_initial_ramp: offset, colour, alpha.
const INITIAL_RAMP := [[0.00, "C58A55", 1.00], [1.00, "E8C49A", 1.00]]
## color_ramp: offset, colour, alpha.
const RAMP := [[0.00, "C58A55", 0.00], [0.20, "C58A55", 0.28], [0.75, "E8C49A", 0.20], [1.00, "E8C49A", 0.00]]
## scale_amount_curve points.
const CURVE := [Vector2(0.00, 0.75), Vector2(0.20, 1.00), Vector2(1.00, 0.70)]
## Brief's property correction: these must not exist on CPUParticles2D (nothing can set them).
const ABSENT := ["alpha_curve", "scale_min", "scale_max", "amount_ratio"]

var failures := 0
var checks := 0


func _initialize() -> void:
	create_timer(60.0).timeout.connect(func(): print("TIMEOUT after 60 s"); quit(2))
	_run.call_deferred()


func _run() -> void:
	print("-- scene")
	var packed := load(SCENE) as PackedScene
	check(packed != null, "%s loads as a PackedScene" % SCENE)
	if packed == null:
		_finish()
		return
	var state := packed.get_state()
	check(state.get_node_count() == 1, "scene has one node, the emitter (node count %d)" % state.get_node_count())
	check(state.get_node_type(0) == &"CPUParticles2D",
			"root node type is CPUParticles2D (got %s)" % state.get_node_type(0))

	print("-- every property the scene file sets exists in Godot %s" % Engine.get_version_info().string)
	_check_saved_properties(state)
	for p in ABSENT:
		check(not _has_property("CPUParticles2D", p), "CPUParticles2D has no '%s' (brief's correction)" % p)

	var fx := packed.instantiate() as CPUParticles2D
	print("-- settings table")
	for p in EXPECTED:
		_check_value(fx, p, EXPECTED[p])
	_check_ramp(fx.color_initial_ramp, "color_initial_ramp", INITIAL_RAMP)
	_check_ramp(fx.color_ramp, "color_ramp", RAMP)
	_check_curve(fx)
	_check_texture(fx)
	_check_material(fx)

	print("-- the feature Effect A doesn't use")
	_check_not_in_effect_a(fx)

	print("-- in the tree")
	root.add_child(fx)
	for i in 5:
		await process_frame
	check(not fx.emitting, "still not emitting after 5 frames in the tree (rule 5)")
	fx.queue_free()
	_finish()


func _finish() -> void:
	print("%d checks, %d failed" % [checks, failures])
	quit(1 if failures > 0 else 0)


func check(ok: bool, what: String) -> void:
	checks += 1
	if not ok:
		failures += 1
	print("%s: %s" % ["PASS" if ok else "FAIL", what])


func _has_property(cls: StringName, prop: String) -> bool:
	for d in ClassDB.class_get_property_list(cls):
		if d["name"] == prop:
			return true
	return false


func _check_saved_properties(state: SceneState) -> void:
	var cls := state.get_node_type(0)
	for i in state.get_node_property_count(0):
		var p := String(state.get_node_property_name(0, i))
		check(_has_property(cls, p), "%s.%s exists" % [cls, p])


func _same(a: Variant, b: Variant) -> bool:
	if typeof(b) == TYPE_FLOAT:
		return absf(float(a) - b) < EPS
	if typeof(b) == TYPE_VECTOR2:
		return (a as Vector2).distance_to(b) < EPS
	return a == b


func _check_value(fx: CPUParticles2D, p: String, want: Variant) -> void:
	var got: Variant = fx.get(p)
	check(_same(got, want), "%s = %s (brief %s)" % [p, got, want])


func _check_ramp(g: Gradient, label: String, stops: Array) -> void:
	check(g != null, "%s is a Gradient" % label)
	if g == null:
		return
	check(g.get_point_count() == stops.size(), "%s has %d stops (got %d)" % [label, stops.size(), g.get_point_count()])
	for i in mini(stops.size(), g.get_point_count()):
		var want := Color(stops[i][1])
		want.a = stops[i][2]
		var got := g.get_color(i)
		var off := g.get_offset(i)
		var ok := absf(off - stops[i][0]) < EPS and absf(got.r - want.r) < COLOR_EPS \
				and absf(got.g - want.g) < COLOR_EPS and absf(got.b - want.b) < COLOR_EPS \
				and absf(got.a - want.a) < COLOR_EPS
		check(ok, "%s stop %d: %.2f #%s alpha %.2f (brief %.2f #%s alpha %.2f)" % [label, i, off,
				got.to_html(false).to_upper(), got.a, stops[i][0], stops[i][1], stops[i][2]])


func _check_curve(fx: CPUParticles2D) -> void:
	var c := fx.scale_amount_curve
	check(c != null, "scale_amount_curve is a Curve")
	if c == null:
		return
	check(c.point_count == CURVE.size(), "scale_amount_curve has %d points (got %d)" % [CURVE.size(), c.point_count])
	for i in mini(CURVE.size(), c.point_count):
		var got := c.get_point_position(i)
		check(got.distance_to(CURVE[i]) < EPS, "scale_amount_curve point %d = %s (brief %s)" % [i, got, CURVE[i]])
	# Not from the brief (Claude Code's choice): straight segments between the brief's points.
	for x in [0.10, 0.60]:
		var want: float = 0.75 + 0.25 * x / 0.2 if x < 0.2 else 1.0 - 0.3 * (x - 0.2) / 0.8
		check(absf(c.sample(x) - want) < 1e-3,
				"scale_amount_curve(%.2f) = %.4f, linear between points %.4f (Claude Code's tangent choice)"
				% [x, c.sample(x), want])


func _check_texture(fx: CPUParticles2D) -> void:
	var t := fx.texture
	check(t != null and t.resource_path == TEXTURE, "texture is %s (got %s)" % [TEXTURE,
			t.resource_path if t else "null; run effects/make_textures.gd, then --import"])
	if t == null:
		return
	check(t.get_width() == 4 and t.get_height() == 4, "texture is 4 x 4 (got %d x %d)" % [t.get_width(), t.get_height()])
	# The shape, read from the PNG (the dummy renderer keeps no texture pixels).
	var img := Image.load_from_file(ProjectSettings.globalize_path(TEXTURE))
	img.convert(Image.FORMAT_RGBA8)
	var white := true
	for y in 4:
		for x in 4:
			var c := img.get_pixel(x, y)
			white = white and c.r > 0.99 and c.g > 0.99 and c.b > 0.99
	check(white, "texture is white in every pixel (colour comes from the ramps)")
	# Soft round dot: centre 2 x 2 > edge pixels > corners, with the corners nearly clear.
	var centre := minf(minf(img.get_pixel(1, 1).a, img.get_pixel(2, 1).a), minf(img.get_pixel(1, 2).a, img.get_pixel(2, 2).a))
	var edge_max := 0.0
	var edge_min := 1.0
	for p in [Vector2i(1, 0), Vector2i(2, 0), Vector2i(0, 1), Vector2i(3, 1), Vector2i(0, 2), Vector2i(3, 2), Vector2i(1, 3), Vector2i(2, 3)]:
		edge_max = maxf(edge_max, img.get_pixel(p.x, p.y).a)
		edge_min = minf(edge_min, img.get_pixel(p.x, p.y).a)
	var corner := maxf(maxf(img.get_pixel(0, 0).a, img.get_pixel(3, 0).a), maxf(img.get_pixel(0, 3).a, img.get_pixel(3, 3).a))
	check(centre > edge_max and edge_min > corner and corner < 0.1,
			"texture is a soft dot: centre alpha %.2f > edge %.2f-%.2f > corner %.2f (< 0.10)" % [centre, edge_min, edge_max, corner])


func _check_material(fx: CPUParticles2D) -> void:
	var m := fx.material as CanvasItemMaterial
	check(m != null, "material is a CanvasItemMaterial (got %s)" % fx.material)
	if m == null:
		return
	check(_has_property("CanvasItemMaterial", "blend_mode"), "CanvasItemMaterial.blend_mode exists")
	check(m.blend_mode == CanvasItemMaterial.BLEND_MODE_MIX, "blend_mode = BLEND_MODE_MIX, normal (got %d)" % m.blend_mode)


## Brief, Effect B "Feature Effect A doesn't use": rectangle emission and non-zero preprocess here,
## point emission and zero preprocess in Effect A's scene.
func _check_not_in_effect_a(fx: CPUParticles2D) -> void:
	var a_packed := load(EFFECT_A) as PackedScene
	check(a_packed != null, "%s loads for the comparison" % EFFECT_A)
	if a_packed == null:
		return
	var a := a_packed.instantiate() as CPUParticles2D
	check(fx.emission_shape == CPUParticles2D.EMISSION_SHAPE_RECTANGLE
			and a.emission_shape != CPUParticles2D.EMISSION_SHAPE_RECTANGLE,
			"rectangle emission: Effect B %d, Effect A %d (RECTANGLE = %d)" % [fx.emission_shape,
			a.emission_shape, CPUParticles2D.EMISSION_SHAPE_RECTANGLE])
	check(fx.preprocess > 0.0 and is_zero_approx(a.preprocess),
			"preprocess: Effect B %.2f s, Effect A %.2f s" % [fx.preprocess, a.preprocess])
	a.free()
