extends SceneTree
## Writes the hint experiment's two ShaderMaterials with ResourceSaver, so Godot assigns their ids.
## Both use Zhaohui's hand-written res://shaders/hint_experiment.gdshader and bind the same
## hint_grey_3x1.png to both samplers; they differ only in read_as_color. Run from the repo root:
##   "$GODOT" --headless --path godot --script res://hint_experiment/make_hint_materials.gd

const SHADER := "res://shaders/hint_experiment.gdshader"
const PNG := "res://hint_experiment/hint_grey_3x1.png"
const OUT := "res://hint_experiment/"

## Quad A reads the texture as colour (source_color sampler), quad B as data (no hint).
## read_as_color is written for both, not left to the shader default: a headless save writes null
## for parameters it was not given.
const MATERIALS := {
	"hint_as_color.tres": true,
	"hint_as_data.tres": false,
}


func _initialize() -> void:
	var shader := load(SHADER) as Shader
	var png := load(PNG) as Texture2D
	var ok := shader != null and png != null
	for file in MATERIALS:
		var mat := ShaderMaterial.new()
		mat.shader = shader
		mat.set_shader_parameter("grey_as_color", png)
		mat.set_shader_parameter("grey_as_data", png)
		mat.set_shader_parameter("read_as_color", MATERIALS[file])
		var err := ResourceSaver.save(mat, OUT + file)
		print("%s err=%d read_as_color=%s" % [OUT + file, err, mat.get_shader_parameter("read_as_color")])
		ok = ok and err == OK
	quit(0 if ok else 1)
