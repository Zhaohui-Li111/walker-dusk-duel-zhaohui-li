extends SceneTree
## Calibrates normal_map_check.gd on a known pair: Poly Haven Granite Wall _nor_gl and _nor_dx
## (the same surface in both green conventions). Expected from the handout: the GL file low with
## directx = false and near 2 with directx = true; the DX file the other way round.
## Also runs two controls that have no surface behind them, so the "~1" end is measured too.
## Run: ./scripts/run-test.sh calibrate_normal_map.gd 60
## Exit 1 if the pair does not separate (each file's right convention must be below its wrong one).

const Check := preload("res://tests/normal_map_check.gd")
const DIR := "res://props3d/textures/"


func _initialize() -> void:
	var gl := _load("granite_wall_nor_gl_1k.png")
	var dx := _load("granite_wall_nor_dx_1k.png")
	var ok := gl != null and dx != null
	if ok:
		var gl_gl := Check.curl_ratio(gl, false)
		var gl_dx := Check.curl_ratio(gl, true)
		var dx_gl := Check.curl_ratio(dx, false)
		var dx_dx := Check.curl_ratio(dx, true)
		print("nor_gl  directx=false %.4f  directx=true %.4f" % [gl_gl, gl_dx])
		print("nor_dx  directx=false %.4f  directx=true %.4f" % [dx_gl, dx_dx])
		print("format nor_gl %d, nor_dx %d (Image.Format)" % [gl.get_format(), dx.get_format()])
		ok = gl_gl < gl_dx and dx_dx < dx_gl
		print("%s: each file scores lower in its own convention" % ("PASS" if ok else "FAIL"))
		# Controls with no surface behind them: the albedo read as if it were a normal map, and
		# random noise. Both should land near 1.
		var diff := _load("granite_wall_diff_1k.png")
		if diff:
			print("control albedo-as-normal  %.4f" % Check.curl_ratio(diff, false))
		var noise := Image.create(256, 256, false, Image.FORMAT_RGB8)
		var rng := RandomNumberGenerator.new()
		rng.seed = 7270
		for y in 256:
			for x in 256:
				noise.set_pixel(x, y, Color(rng.randf(), rng.randf(), 0.5 + 0.5 * rng.randf()))
		print("control random noise      %.4f" % Check.curl_ratio(noise, false, 1))
	quit(0 if ok else 1)


func _load(file: String) -> Image:
	var img := Image.load_from_file(ProjectSettings.globalize_path(DIR + file))
	if img == null:
		print("FAIL: could not decode %s" % file)
	return img
