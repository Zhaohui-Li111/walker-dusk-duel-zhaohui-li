extends SceneTree
## A5 in-engine captures. Needs a window (not --headless), because a headless run draws nothing:
##   "$GODOT" --path godot --script res://tests/capture_a5.gd
## Saves PNGs from the rendered viewport (real engine output, not an OS screenshot) to
## evidence/a5/ and prints the sampled pixel values, which go beside the brief's predictions in
## TEST-REPORT.md. The numbers are measured; whether the result looks right is the human check.
##
## 1. Hurt flash: P1 idle at round start, driver paused (as in the handout's capture()), hurt_amount
##    set from code to 0.0, 0.5, 1.0 and 2.0 (the Q7 clamp question); P-gi and P-fist sampled.
## 2. Hint experiment: both quads; the three bands of each sampled.
## 3. Granite: the prop room at the materials' values, then each uniform at min / default / max
##    on the floor material only, then one value changed on the floor material only, with a plinth
##    pixel sampled to show that only the floor changed. Nothing is saved to the .tres files.
## 4. Time scale in a normal windowed run (no --fixed-fps): physics ticks per real second at
##    Engine.time_scale 1.0 and 0.5.

const OUT := "res://../evidence/a5/"
const TEXELS := {"P-gi": Vector2(52, 101), "P-fist": Vector2(75, 68)}
const PREDICTED_CAPTURE := {"P-gi": Vector2i(449, 515), "P-fist": Vector2i(495, 449)}

var out_dir: String


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	out_dir = ProjectSettings.globalize_path("res://").path_join("../evidence/a5")
	DirAccess.make_dir_recursive_absolute(out_dir)
	print("capture_a5: Godot %s, renderer %s, window %s" % [Engine.get_version_info().string,
			RenderingServer.get_current_rendering_driver_name(), DisplayServer.window_get_size()])
	await hurt_flash()
	await hint_experiment()
	await granite()
	await time_scale()
	print("capture_a5: done, files in ", out_dir)
	quit()


func grab(name: String) -> Image:
	await RenderingServer.frame_post_draw
	var img := root.get_viewport().get_texture().get_image()
	img.save_png(out_dir.path_join(name + ".png"))
	return img


func px(img: Image, p: Vector2i) -> String:
	var c := img.get_pixelv(p)
	return "(%d, %d, %d)" % [c.r8, c.g8, c.b8]


## Camera3D.unproject_position() gives 640x360 viewport coordinates (canvas_items stretch); the
## capture is the window size, so scale up before sampling.
func at3d(cam: Camera3D, img: Image, world: Vector3) -> Vector2i:
	return Vector2i((cam.unproject_position(world) * img.get_width() / 640.0).floor())


func hurt_flash() -> void:
	print("== 1. hurt flash")
	var main: Node = load("res://game/main.tscn").instantiate()
	root.add_child(main)
	await process_frame
	main.start_fight_now()
	main.p2.controller = null
	main.p1.controller = null
	for i in 5:
		await process_frame
	var sprite: Sprite2D = main.p1.get_node("Sprite2D")
	var driver: Node = sprite.get_node("HurtFlash")
	var mat := sprite.material as ShaderMaterial
	driver.set_physics_process(false)    # otherwise the driver overwrites the value every tick
	var first := true
	for v in [0.0, 0.5, 1.0, 2.0]:
		mat.set_shader_parameter("hurt_amount", v)
		await process_frame
		var img := await grab("hurt_flash_%s" % str(v).replace(".", "_"))
		var scale := img.get_width() / 640.0
		if first:
			print("  capture size %dx%d (scale %.2f from the 640x360 viewport); P1 state '%s' at %s" % [
					img.get_width(), img.get_height(), scale, main.p1.state, main.p1.position])
			first = false
		for name in TEXELS:
			var local: Vector2 = sprite.offset + TEXELS[name] + Vector2(0.5, 0.5)
			var at: Vector2 = sprite.get_global_transform_with_canvas() * local * scale
			var p := Vector2i(at.floor())
			print("  hurt_amount %.1f  %-6s texel %s -> capture %s (brief predicted %s): %s  read back %s" % [
					v, name, TEXELS[name], p, PREDICTED_CAPTURE[name], px(img, p),
					mat.get_shader_parameter("hurt_amount")])
	# Q7: with pure red both 1.0 and 2.0 saturate to (255, 0, 0), so they cannot tell a clamp from
	# no clamp. A grey flash_color, set in memory only for this check, makes 2.0 land inside 0..1
	# if the value is not clamped: P-gi R = 222 + 2 * (128 - 222) = 34, against 128 if clamped.
	var keep: Variant = mat.get_shader_parameter("flash_color")
	mat.set_shader_parameter("flash_color", Color8(128, 128, 128))
	for v in [1.0, 2.0]:
		mat.set_shader_parameter("hurt_amount", v)
		await process_frame
		var img := await grab("hurt_flash_grey_%s" % str(v).replace(".", "_"))
		var local: Vector2 = sprite.offset + TEXELS["P-gi"] + Vector2(0.5, 0.5)
		var p := Vector2i((sprite.get_global_transform_with_canvas() * local * (img.get_width() / 640.0)).floor())
		print("  clamp check, flash_color (128,128,128), hurt_amount %.1f: P-gi %s" % [v, px(img, p)])
	mat.set_shader_parameter("flash_color", keep)
	mat.set_shader_parameter("hurt_amount", 0.0)
	driver.set_physics_process(true)
	main.queue_free()
	await process_frame


func hint_experiment() -> void:
	print("== 2. hint experiment")
	var scene: Node = load("res://hint_experiment/hint_experiment.tscn").instantiate()
	root.add_child(scene)
	for i in 3:
		await process_frame
	var img := await grab("hint_experiment")
	var cam := scene.get_node("Camera") as Camera3D
	for q in [["QuadA_source_color", 0.4], ["QuadB_no_hint", -0.4]]:
		var vals := []
		for x in [-0.4, 0.0, 0.4]:      # band centres of the 1.2 m quad (three texels)
			vals.append(px(img, at3d(cam, img, Vector3(x, q[1], 0.0))))
		print("  %-19s bands 64 / 128 / 192 -> %s" % [q[0], " / ".join(vals)])
	# Diagnostic (MATERIALS.md finding 5): both materials bind one texture object to both samplers.
	# Give quad B, in memory only, a separate ImageTexture made from the same file's image, so the
	# no-hint sampler has a texture object of its own. If B changes, the shared object was the cause.
	var mat_b := (scene.get_node("QuadB_no_hint") as MeshInstance3D).material_override as ShaderMaterial
	var keep: Variant = mat_b.get_shader_parameter("grey_as_data")
	var own := ImageTexture.create_from_image(Image.load_from_file(
			ProjectSettings.globalize_path("res://hint_experiment/hint_grey_3x1.png")))
	mat_b.set_shader_parameter("grey_as_data", own)
	await process_frame
	img = await grab("hint_experiment_b_own_texture")
	var vals_b := []
	for x in [-0.4, 0.0, 0.4]:
		vals_b.append(px(img, at3d(cam, img, Vector3(x, -0.4, 0.0))))
	print("  QuadB_no_hint with its own texture object -> %s" % " / ".join(vals_b))
	mat_b.set_shader_parameter("grey_as_data", keep)
	scene.queue_free()
	await process_frame


func granite() -> void:
	print("== 3. granite")
	var room: Node = load("res://props3d/prop_room.tscn").instantiate()
	root.add_child(room)
	for i in 3:
		await process_frame
	var cam := room.get_node("Camera") as Camera3D
	var floor_mat := (room.get_node("Floor") as MeshInstance3D).material_override as ShaderMaterial
	var img := await grab("granite_materials")
	var floor_p := at3d(cam, img, Vector3(-0.2, 0.0, 1.2))
	var plinth_p := at3d(cam, img, Vector3(1.2, 0.3, -1.0))   # lit top face, right of the taiko
	print("  as saved: floor %s at %s, plinth front %s at %s" % [px(img, floor_p), floor_p, px(img, plinth_p), plinth_p])
	var sweep := {"uv_scale": [0.25, 6.0, 8.0], "roughness_scale": [0.0, 1.0, 1.0],
			"normal_strength": [0.0, 1.0, 2.0], "tint": [Color(0, 0, 0), Color(1, 1, 1), Color(1, 1, 1)]}
	var names := ["min", "material", "max"]
	for key in sweep:
		var keep: Variant = floor_mat.get_shader_parameter(key)
		for i in 3:
			if i == 2 and sweep[key][2] == sweep[key][1]:
				continue                # max equals the material value: nothing new to show
			floor_mat.set_shader_parameter(key, sweep[key][i])
			img = await grab("granite_sweep_%s_%s" % [key, names[i]])
			print("  floor %-15s %-8s = %-22s floor %s  plinth %s" % [key, names[i], str(sweep[key][i]),
					px(img, floor_p), px(img, plinth_p)])
		floor_mat.set_shader_parameter(key, keep)
	# One value in one material: the floor's tint only. The plinth must not change.
	floor_mat.set_shader_parameter("tint", Color(0.4, 0.8, 0.4))
	img = await grab("granite_one_material_changed")
	print("  floor tint -> (0.4, 0.8, 0.4): floor %s  plinth %s (plinth must equal 'as saved')" % [
			px(img, floor_p), px(img, plinth_p)])
	floor_mat.set_shader_parameter("tint", Color(1, 1, 1))
	room.queue_free()
	await process_frame


func time_scale() -> void:
	print("== 4. time scale, windowed, no --fixed-fps")
	for s in [1.0, 0.5]:
		Engine.time_scale = s
		await process_frame
		var t0 := Time.get_ticks_usec()
		var f0 := Engine.get_physics_frames()
		while Time.get_ticks_usec() - t0 < 2000000:
			await process_frame
		var secs := (Time.get_ticks_usec() - t0) / 1e6
		print("  time_scale %.1f: %d physics ticks in %.3f s of real time = %.1f ticks/s" % [
				s, Engine.get_physics_frames() - f0, secs, (Engine.get_physics_frames() - f0) / secs])
	Engine.time_scale = 1.0
