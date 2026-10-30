extends SceneTree
## Writes the two granite ShaderMaterials (CHANGE-BRIEF, A5 material plan) with ResourceSaver,
## so Godot assigns their UIDs. Both use Zhaohui's hand-written res://shaders/granite.gdshader and
## bind the same three textures; they differ in uv_scale and tint. Run from the repository root:
##   "$GODOT" --headless --path godot --script res://props3d/make_granite_materials.gd
## Re-running it overwrites both files with these values.

const SHADER := "res://shaders/granite.gdshader"
const TEX := "res://props3d/textures/granite_wall_%s_1k.png"
const OUT := "res://props3d/materials/"

## BoxMesh puts each face in a 3 x 2 grid of the UV square (probe, FRICTIONAL 2026-10-26), so the
## floor's 6 x 4 m top face shows uv_scale/3 x uv_scale/2 copies of the texture: 2 x 3 at 6.0.
## The 0.8 m plinth shows about one third of the texture per face at 1.0.
const MATERIALS := {
	"granite_floor.tres": {"uv_scale": 6.0, "tint": Color(1.0, 1.0, 1.0, 1.0)},
	# #6E6680, the A3 stone colour, so the plinth reads as a separate darker block.
	"granite_plinth.tres": {"uv_scale": 1.0, "tint": Color("6e6680")},
}
## Equal to the shader's own defaults, but written explicitly: a headless run does not know shader
## defaults, so ResourceSaver otherwise saves these two uniforms as null.
const SHARED := {"roughness_scale": 1.0, "normal_strength": 1.0}


func _initialize() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT))
	var shader := load(SHADER) as Shader
	var ok := shader != null
	for file in MATERIALS:
		var mat := ShaderMaterial.new()
		mat.shader = shader
		mat.set_shader_parameter("albedo_texture", load(TEX % "diff"))
		mat.set_shader_parameter("roughness_texture", load(TEX % "rough"))
		mat.set_shader_parameter("normal_texture", load(TEX % "nor_gl"))
		for key in SHARED:
			mat.set_shader_parameter(key, SHARED[key])
		for key in MATERIALS[file]:
			mat.set_shader_parameter(key, MATERIALS[file][key])
		var err := ResourceSaver.save(mat, OUT + file)
		print("%s err=%d uv_scale=%s tint=%s" % [OUT + file, err, mat.get_shader_parameter("uv_scale"),
				mat.get_shader_parameter("tint")])
		ok = ok and err == OK
	quit(0 if ok else 1)
