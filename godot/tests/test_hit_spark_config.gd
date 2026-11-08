extends SceneTree
## A6 Effect A (hit spark): reads every setting in CHANGE-BRIEF.md's Effect A settings table back
## from the loaded scene and its resources. Expected values are the brief's. Run from the repo root:
##   scripts/run-test.sh test_hit_spark_config.gd 60
## Also checks that every property the scene file sets exists on its class in this Godot build, so a
## Godot 3 name (predicted failure 6) fails here instead of being dropped on load.
## One value is not from the brief and is marked as such: the scale curve's tangents (linear).

const SCENE := "res://effects/hit_spark.tscn"
const TEXTURE := "res://effects/hit_spark_star.png"
const EPS := 1e-4
const COLOR_EPS := 0.5 / 255.0

## Brief, Effect A settings table: property -> expected value.
const EXPECTED := {
	"amount": 20,
	"one_shot": true,
	"explosiveness": 1.0,
	"lifetime": 0.6,
	"emission_shape": CPUParticles2D.EMISSION_SHAPE_POINT,
	"initial_velocity_min": 45.0,
	"initial_velocity_max": 75.0,
	"spread": 180.0,
	"gravity": Vector2(0, 25),
	"damping_min": 28.0,
	"damping_max": 40.0,
	"angle_min": -180.0,
	"angle_max": 180.0,
	"scale_amount_min": 0.7,
	"scale_amount_max": 1.2,
	"local_coords": true,
	"preprocess": 0.0,
	"speed_scale": 1.0,
	"emitting": false,               # rule 1: never fires on scene load
}
## color_ramp: offset, colour, alpha.
const RAMP := [[0.00, "EAFBFF", 1.00], [0.35, "83DFF2", 0.75], [1.00, "83DFF2", 0.00]]
## scale_amount_curve points.
const CURVE := [Vector2(0.00, 1.00), Vector2(0.70, 0.65), Vector2(1.00, 0.00)]
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
	print("   info: CPUParticles2D has visibility_rect = %s (brief: not applicable to this CPU design)"
			% _has_property("CPUParticles2D", "visibility_rect"))

	var fx := packed.instantiate() as CPUParticles2D
	print("-- settings table")
	for p in EXPECTED:
		_check_value(fx, p, EXPECTED[p])
	_check_ramp(fx)
	_check_curve(fx)
	_check_texture(fx)
	_check_material(fx)

	print("-- in the tree")
	root.add_child(fx)
	for i in 5:
		await process_frame
	check(not fx.emitting, "still not emitting after 5 frames in the tree (rule 1)")
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


func _check_ramp(fx: CPUParticles2D) -> void:
	var g := fx.color_ramp
	check(g != null, "color_ramp is a Gradient")
	if g == null:
		return
	check(g.get_point_count() == RAMP.size(), "color_ramp has %d stops (got %d)" % [RAMP.size(), g.get_point_count()])
	for i in mini(RAMP.size(), g.get_point_count()):
		var want := Color(RAMP[i][1])
		want.a = RAMP[i][2]
		var got := g.get_color(i)
		var off := g.get_offset(i)
		var ok := absf(off - RAMP[i][0]) < EPS and absf(got.r - want.r) < COLOR_EPS \
				and absf(got.g - want.g) < COLOR_EPS and absf(got.b - want.b) < COLOR_EPS \
				and absf(got.a - want.a) < COLOR_EPS
		check(ok, "color_ramp stop %d: %.2f #%s alpha %.2f (brief %.2f #%s alpha %.2f)" % [i, off,
				got.to_html(false).to_upper(), got.a, RAMP[i][0], RAMP[i][1], RAMP[i][2]])


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
	for x in [0.35, 0.85]:
		var want: float = 1.0 + (0.65 - 1.0) * x / 0.7 if x < 0.7 else 0.65 * (1.0 - x) / 0.3
		check(absf(c.sample(x) - want) < 1e-3,
				"scale_amount_curve(%.2f) = %.4f, linear between points %.4f (Claude Code's tangent choice)"
				% [x, c.sample(x), want])


func _check_texture(fx: CPUParticles2D) -> void:
	var t := fx.texture
	check(t != null and t.resource_path == TEXTURE, "texture is %s (got %s)" % [TEXTURE,
			t.resource_path if t else "null"])
	if t == null:
		return
	check(t.get_width() == 8 and t.get_height() == 8, "texture is 8 x 8 (got %d x %d)" % [t.get_width(), t.get_height()])
	# The shape, read from the PNG (the dummy renderer keeps no texture pixels).
	var img := Image.load_from_file(ProjectSettings.globalize_path(TEXTURE))
	img.convert(Image.FORMAT_RGBA8)
	var centre := [img.get_pixel(3, 3), img.get_pixel(4, 3), img.get_pixel(3, 4), img.get_pixel(4, 4)]
	var solid := centre.all(func(c: Color) -> bool: return c.a > 0.99 and c.r > 0.99 and c.g > 0.99 and c.b > 0.99)
	check(solid, "texture centre 2 x 2 is opaque white (wide at the centre)")
	# Eight tips: pixels near the 8 tip directions (every 45 deg) carry more alpha than pixels between.
	var tip := 0.0
	var gap := 0.0
	for y in 8:
		for x in 8:
			var p := Vector2(x + 0.5 - 4.0, y + 0.5 - 4.0)
			if p.length() < 2.0:
				continue
			var a := fposmod(rad_to_deg(p.angle()), 45.0)
			if a < 11.25 or a > 33.75:
				tip += img.get_pixel(x, y).a
			else:
				gap += img.get_pixel(x, y).a
	check(tip > 2.0 * gap, "texture is an eight-point star: outer alpha on tips %.2f > 2 x between tips %.2f" % [tip, gap])


func _check_material(fx: CPUParticles2D) -> void:
	var m := fx.material as CanvasItemMaterial
	check(m != null, "material is a CanvasItemMaterial (got %s)" % fx.material)
	if m == null:
		return
	check(_has_property("CanvasItemMaterial", "blend_mode"), "CanvasItemMaterial.blend_mode exists")
	check(m.blend_mode == CanvasItemMaterial.BLEND_MODE_ADD, "blend_mode = BLEND_MODE_ADD (got %d)" % m.blend_mode)
