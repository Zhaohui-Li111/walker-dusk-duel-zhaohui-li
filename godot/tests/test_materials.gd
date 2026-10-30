extends SceneTree
## Headless audit of the A5 materials (godot/MATERIALS.md). Run from the repo root:
##   ./scripts/run-test.sh test_materials.gd 60
## Pins what the audit found: the shaders' uniforms and hints (read from the source text and from
## get_shader_uniform_list()), each ShaderMaterial's values and texture paths, the import settings
## of every bound texture (ConfigFile on the .import files), the material wiring and the lights and
## environments of prop_room.tscn and hint_experiment.tscn, the BoxMesh texel scale per face, and
## the curl ratio of each normal map under both green conventions.
## One PASS/FAIL line per check; exit code 1 on any failure.
## What it does NOT show: any colour on screen. The dummy renderer draws nothing, so the hint
## experiment's measured greys, the granite's look, and how the importer's VRAM formats sample are
## human checks with a window.

const Check := preload("res://tests/normal_map_check.gd")

const GRANITE := "res://shaders/granite.gdshader"
const HINT := "res://shaders/hint_experiment.gdshader"
const TEX := "res://props3d/textures/granite_wall_%s_1k.png"
const GREY := "res://hint_experiment/hint_grey_3x1.png"

## Every uniform in each shader: type, hints and default exactly as written, and its group.
const SHADER_SOURCE := {
	GRANITE: {
		"albedo_texture": ["sampler2D", "source_color, repeat_enable", "", ""],
		"roughness_texture": ["sampler2D", "repeat_enable", "", ""],
		"normal_texture": ["sampler2D", "hint_normal, repeat_enable", "", ""],
		"tint": ["vec4", "source_color", "vec4(1.0, 1.0, 1.0, 1.0)", "surface"],
		"uv_scale": ["float", "hint_range(0.25, 8.0)", "1.0", "surface"],
		"roughness_scale": ["float", "hint_range(0.0, 1.0)", "1.0", "detail"],
		"normal_strength": ["float", "hint_range(0.0, 2.0)", "1.0", "detail"],
	},
	HINT: {
		"grey_as_color": ["sampler2D", "source_color, filter_nearest", "", ""],
		"grey_as_data": ["sampler2D", "filter_nearest", "", ""],
		"read_as_color": ["bool", "", "true", ""],
	},
}
const RENDER_MODE := {GRANITE: "", HINT: "unshaded"}

## get_shader_uniform_list() types, as Variant.Type.
const UNIFORM_TYPES := {
	GRANITE: {"albedo_texture": TYPE_OBJECT, "roughness_texture": TYPE_OBJECT,
		"normal_texture": TYPE_OBJECT, "tint": TYPE_COLOR, "uv_scale": TYPE_FLOAT,
		"roughness_scale": TYPE_FLOAT, "normal_strength": TYPE_FLOAT},
	HINT: {"grey_as_color": TYPE_OBJECT, "grey_as_data": TYPE_OBJECT, "read_as_color": TYPE_BOOL},
}

## Every parameter each material sets: a texture path, or a value (tint as hex).
const MATERIALS := {
	"res://props3d/materials/granite_floor.tres": {"shader": GRANITE, "params": {
		"albedo_texture": TEX % "diff", "roughness_texture": TEX % "rough",
		"normal_texture": TEX % "nor_gl", "tint": "ffffff", "uv_scale": 6.0,
		"roughness_scale": 1.0, "normal_strength": 1.0}},
	"res://props3d/materials/granite_plinth.tres": {"shader": GRANITE, "params": {
		"albedo_texture": TEX % "diff", "roughness_texture": TEX % "rough",
		"normal_texture": TEX % "nor_gl", "tint": "6e6680", "uv_scale": 1.0,
		"roughness_scale": 1.0, "normal_strength": 1.0}},
	"res://hint_experiment/hint_as_color.tres": {"shader": HINT, "params": {
		"grey_as_color": GREY, "grey_as_data": GREY, "read_as_color": true}},
	"res://hint_experiment/hint_as_data.tres": {"shader": HINT, "params": {
		"grey_as_color": GREY, "grey_as_data": GREY, "read_as_color": false}},
}

## [compress/mode, compress/normal_map, mipmaps/generate], CHANGE-BRIEF A5 material plan.
const IMPORTS := {
	TEX % "diff": [2, 2, true],
	TEX % "rough": [2, 2, true],
	TEX % "nor_gl": [2, 1, true],
	TEX % "nor_dx": [0, 2, false],
	GREY: [0, 2, false],
}

## Which node carries which material.
const WIRING := {
	"res://props3d/prop_room.tscn": {
		"Floor": "res://props3d/materials/granite_floor.tres",
		"StonePlinth": "res://props3d/materials/granite_plinth.tres"},
	"res://hint_experiment/hint_experiment.tscn": {
		"QuadA_source_color": "res://hint_experiment/hint_as_color.tres",
		"QuadB_no_hint": "res://hint_experiment/hint_as_data.tres"},
}

## Environment properties that change the look; unwritten ones are Godot's defaults.
const ENVIRONMENTS := {
	"res://props3d/prop_room.tscn": {"tonemap_mode": 0, "tonemap_exposure": 1.0,
		"background_mode": 1, "background_color": "5a4766", "ambient_light_source": 2,
		"ambient_light_color": "8c8599", "ambient_light_energy": 0.35,
		"reflected_light_source": 0, "glow_enabled": false, "fog_enabled": false,
		"ssao_enabled": false, "adjustment_enabled": false},
	"res://hint_experiment/hint_experiment.tscn": {"tonemap_mode": 0, "tonemap_exposure": 1.0,
		"background_mode": 1, "background_color": "1a1a1a", "ambient_light_source": 1,
		"reflected_light_source": 1, "glow_enabled": false, "fog_enabled": false,
		"ssao_enabled": false, "adjustment_enabled": false},
}

## Metres of surface per copy of the texture along each in-plane axis, from the BoxMesh UVs and the
## material's uv_scale. Face: [node, outward normal, axis a, axis b, expected m/copy a, b].
const FACES := [
	["Floor", Vector3.UP, Vector3.AXIS_X, Vector3.AXIS_Z, 3.0, 4.0 / 3.0],
	["StonePlinth", Vector3.UP, Vector3.AXIS_X, Vector3.AXIS_Z, 2.4, 1.6],
	["StonePlinth", Vector3.BACK, Vector3.AXIS_X, Vector3.AXIS_Y, 2.4, 0.6],
]

var failures := 0
var checks := 0


func _initialize() -> void:
	create_timer(60.0).timeout.connect(func(): print("TIMEOUT after 60 s"); quit(2))
	_run.call_deferred()


func _run() -> void:
	print("-- shader source")
	for path in SHADER_SOURCE:
		_check_source(path)
	print("-- get_shader_uniform_list()")
	for path in UNIFORM_TYPES:
		_check_uniform_list(path)
	print("-- materials")
	for path in MATERIALS:
		_check_material(path)
	var floor_mat := load("res://props3d/materials/granite_floor.tres") as ShaderMaterial
	var plinth_mat := load("res://props3d/materials/granite_plinth.tres") as ShaderMaterial
	check(floor_mat.shader.resource_path == plinth_mat.shader.resource_path
			and floor_mat.shader.resource_path == GRANITE,
			"both granite materials name the same shader %s" % GRANITE)
	var bound_dx := false
	for path in MATERIALS:
		var mat := load(path) as ShaderMaterial
		for p in MATERIALS[path]["params"]:
			var v = mat.get_shader_parameter(p)
			if v is Texture2D and v.resource_path == TEX % "nor_dx":
				bound_dx = true
	check(not bound_dx, "no material binds %s (calibration only)" % (TEX % "nor_dx"))
	print("-- import settings")
	for path in IMPORTS:
		_check_import(path)
	print("-- scenes: wiring, lights, environment")
	for scene_path in WIRING:
		var scene: Node3D = load(scene_path).instantiate()
		root.add_child(scene)
		await process_frame
		_check_scene(scene_path, scene)
		if scene_path == "res://props3d/prop_room.tscn":
			_check_prop_room(scene)
		scene.queue_free()
	print("-- normal maps (curl ratio; ~0 right convention, ~2 wrong, ~1 no surface)")
	for file in ["nor_gl", "nor_dx"]:
		_check_normal_map(file)
	print("%d checks, %d failed" % [checks, failures])
	quit(1 if failures > 0 else 0)


func check(ok: bool, what: String) -> void:
	checks += 1
	if not ok:
		failures += 1
	print("%s: %s" % ["PASS" if ok else "FAIL", what])


## Parses `uniform <type> <name> [: <hints>] [= <default>];` lines and the group each sits in.
func _parse_uniforms(src: String) -> Dictionary:
	var out := {}
	var group := ""
	var re := RegEx.create_from_string(
			"^uniform\\s+(\\w+)\\s+(\\w+)\\s*(?::\\s*([^=;]*?))?\\s*(?:=\\s*([^;]*?))?\\s*;")
	for line in src.split("\n"):
		var l := line.strip_edges()
		if l.begins_with("group_uniforms"):
			group = l.trim_prefix("group_uniforms").trim_suffix(";").strip_edges()
			continue
		var m := re.search(l)
		if m:
			out[m.get_string(2)] = [m.get_string(1), m.get_string(3), m.get_string(4), group]
	return out


func _check_source(path: String) -> void:
	var src := FileAccess.get_file_as_string(path)
	check(not src.is_empty(), "%s readable" % path)
	var found := _parse_uniforms(src)
	var want: Dictionary = SHADER_SOURCE[path]
	check(found.keys().size() == want.keys().size(),
			"%s declares %d uniforms (found %s)" % [path.get_file(), want.size(), found.keys()])
	for name in want:
		var got: Array = found.get(name, ["?", "?", "?", "?"])
		var w: Array = want[name]
		check(got == w, "%s %s: type %s, hints '%s', default '%s', group '%s' (found %s)"
				% [path.get_file(), name, w[0], w[1], w[2], w[3], got])
	var mode := ""
	for line in src.split("\n"):
		if line.strip_edges().begins_with("render_mode"):
			mode = line.strip_edges().trim_prefix("render_mode").trim_suffix(";").strip_edges()
	check(mode == RENDER_MODE[path], "%s render_mode '%s'" % [path.get_file(), RENDER_MODE[path]])


func _check_uniform_list(path: String) -> void:
	var shader := load(path) as Shader
	var list := shader.get_shader_uniform_list()
	var got := {}
	for u in list:
		got[u["name"]] = u["type"]
		print("    %s %s type=%d hint=%d hint_string='%s'"
				% [path.get_file(), u["name"], u["type"], u["hint"], u["hint_string"]])
	check(not list.is_empty(), "%s parses (uniform list not empty)" % path.get_file())
	check(got == UNIFORM_TYPES[path], "%s uniform names and types %s" % [path.get_file(), got])


func _check_material(path: String) -> void:
	var mat := load(path) as ShaderMaterial
	check(mat != null, "%s loads as ShaderMaterial" % path)
	if mat == null:
		return
	var spec: Dictionary = MATERIALS[path]
	check(mat.shader != null and mat.shader.resource_path == spec["shader"],
			"%s shader %s" % [path.get_file(), spec["shader"]])
	for p in spec["params"]:
		var want = spec["params"][p]
		var v = mat.get_shader_parameter(p)
		var shown: String
		if v is Texture2D:
			shown = v.resource_path
		elif v is Color:
			shown = (v as Color).to_html(false)
		else:
			shown = str(v)
		var ok: bool
		if want is float:
			ok = (v is float or v is int) and is_equal_approx(float(v), want)
		else:
			ok = shown == str(want)
		check(ok, "%s %s = %s (read %s)" % [path.get_file(), p, want, shown])


func _check_import(path: String) -> void:
	var cfg := ConfigFile.new()
	var err := cfg.load(path + ".import")
	check(err == OK, "%s.import readable" % path.get_file())
	var got := [cfg.get_value("params", "compress/mode", -1),
			cfg.get_value("params", "compress/normal_map", -1),
			cfg.get_value("params", "mipmaps/generate", null)]
	check(got == IMPORTS[path], "%s compress/mode, compress/normal_map, mipmaps/generate = %s (read %s)"
			% [path.get_file(), IMPORTS[path], got])
	print("    %s imported_formats %s" % [path.get_file(),
			cfg.get_value("remap", "metadata", {}).get("imported_formats", "(none)")])


func _check_scene(scene_path: String, scene: Node3D) -> void:
	for node_name in WIRING[scene_path]:
		var mi := scene.get_node(node_name) as MeshInstance3D
		var mo := mi.material_override
		check(mo != null and mo.resource_path == WIRING[scene_path][node_name],
				"%s material_override is the file %s (read '%s')" % [node_name,
				WIRING[scene_path][node_name], mo.resource_path if mo else "null"])
	var env := (scene.get_node("Environment") as WorldEnvironment).environment
	var want: Dictionary = ENVIRONMENTS[scene_path]
	for prop in want:
		var v = env.get(prop)
		var shown := (v as Color).to_html(false) if v is Color else str(v)
		var ok: bool = is_equal_approx(float(v), want[prop]) if want[prop] is float \
				else shown == str(want[prop])
		check(ok, "%s env %s = %s (read %s)" % [scene_path.get_file(), prop, want[prop], shown])
	var lights := scene.find_children("*", "Light3D", true, false)
	print("    %s lights: %d" % [scene_path.get_file(), lights.size()])
	for l in lights:
		print("    %s %s energy %.2f colour %s shadow %s rot %s" % [l.name, l.get_class(),
				l.light_energy, l.light_color.to_html(false), l.shadow_enabled, l.rotation_degrees])


func _check_prop_room(scene: Node3D) -> void:
	var sun := scene.get_node("Sun") as DirectionalLight3D
	check(is_equal_approx(sun.light_energy, 0.7) and sun.shadow_enabled
			and sun.light_color == Color.WHITE, "Sun: energy 0.7, white, shadows on")
	check(scene.find_children("*", "Light3D", true, false).size() == 1, "prop room has one light")
	# Finding: the floor's BoxMesh still carries its old embedded StandardMaterial3D, unused under
	# the override.
	var floor_mesh := (scene.get_node("Floor") as MeshInstance3D).mesh as BoxMesh
	check(floor_mesh.material is StandardMaterial3D
			and floor_mesh.material.resource_path.contains("::"),
			"Floor BoxMesh still has an embedded StandardMaterial3D (hidden by material_override), "
			+ "path '%s'" % (floor_mesh.material.resource_path if floor_mesh.material else "null"))
	for f in FACES:
		_check_face(scene, f)


func _check_face(scene: Node3D, f: Array) -> void:
	var mi := scene.get_node(f[0]) as MeshInstance3D
	var mesh := mi.mesh as BoxMesh
	var uv_scale: float = (mi.material_override as ShaderMaterial).get_shader_parameter("uv_scale")
	var arr := mesh.surface_get_arrays(0)
	var verts: PackedVector3Array = arr[Mesh.ARRAY_VERTEX]
	var normals: PackedVector3Array = arr[Mesh.ARRAY_NORMAL]
	var uvs: PackedVector2Array = arr[Mesh.ARRAY_TEX_UV]
	var a: int = f[2]
	var b: int = f[3]
	var face: Array[int] = []
	for i in verts.size():
		if normals[i].dot(f[1]) > 0.99:
			face.append(i)
	if face.size() < 4:
		check(false, "%s face %s: found %d vertices of %d (normals %d, uvs %d)"
				% [f[0], f[1], face.size(), verts.size(), normals.size(), uvs.size()])
		return
	# corner with min a, min b; then the corner that differs only in a, and only in b
	var lo := face[0]
	for i in face:
		if verts[i][a] < verts[lo][a] - 1e-4 or (absf(verts[i][a] - verts[lo][a]) < 1e-4
				and verts[i][b] < verts[lo][b] - 1e-4):
			lo = i
	var per_copy := []
	for axis in [a, b]:
		var other: int = b if axis == a else a
		var far := lo
		for i in face:
			if absf(verts[i][other] - verts[lo][other]) < 1e-4 and verts[i][axis] > verts[far][axis]:
				far = i
		var metres := verts[far][axis] - verts[lo][axis]
		var copies := (uvs[far] - uvs[lo]).length() * uv_scale
		per_copy.append(metres / copies if copies > 0.0 else INF)
	var ratio: float = maxf(per_copy[0], per_copy[1]) / minf(per_copy[0], per_copy[1])
	var axes := "XYZ"
	check(absf(per_copy[0] - f[4]) < 0.01 and absf(per_copy[1] - f[5]) < 0.01,
			"%s face %s at uv_scale %.1f: %.3f m per copy along %s, %.3f m along %s (stretch %.2f : 1)"
			% [f[0], f[1], uv_scale, per_copy[0], axes[a], per_copy[1], axes[b], ratio])


func _check_normal_map(file: String) -> void:
	var path: String = TEX % file
	var img := Image.load_from_file(ProjectSettings.globalize_path(path))
	check(img != null, "%s decodes with Image.load_from_file" % path.get_file())
	if img == null:
		return
	var gl := Check.curl_ratio(img, false)
	var dx := Check.curl_ratio(img, true)
	print("    %s %dx%d format %d: curl_ratio directx=false %.4f, directx=true %.4f"
			% [path.get_file(), img.get_width(), img.get_height(), img.get_format(), gl, dx])
	# Threshold 1.0 from the gl/dx calibration (FRICTIONAL.md: the 8-bit decode pulls both to 1).
	if file == "nor_gl":
		check(gl < 1.0 and dx > 1.0, "%s is an OpenGL-convention normal map (gl < 1 < dx)" % path.get_file())
	else:
		check(dx < 1.0 and gl > 1.0, "%s is a DirectX-convention normal map (dx < 1 < gl)" % path.get_file())
