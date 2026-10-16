extends SceneTree
## Renders 3840x2160 engine stills of props3d/prop_room.tscn from fixed cameras, into the folder
## given after "--". Needs a window (not --headless). Used on capture/game and capture/game-raised:
##   godot --path capture/game --resolution 3840x2160 --script res://capture_stills.gd -- <out dir> <prefix>

const VIEWS := {
	# low side view at the taiko's feet: shows whether it stands on the floor
	"taiko_floor": [Vector3(2.4, 0.22, 2.2), Vector3(0.5, 0.42, 0.0)],
	"front": [Vector3(0, 1.3, 4.5), Vector3(0, 0.7, 0)],
}


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	var args := OS.get_cmdline_user_args()
	var out: String = args[0]
	var prefix: String = args[1]
	root.size = Vector2i(3840, 2160)
	var room: Node3D = load("res://props3d/prop_room.tscn").instantiate()
	root.add_child(room)
	var cam := room.get_node("Camera") as Camera3D
	for view_name in VIEWS:
		var v: Array = VIEWS[view_name]
		cam.look_at_from_position(v[0], v[1])
		for i in 6:
			await process_frame
		await RenderingServer.frame_post_draw
		var path := out.path_join("%s_%s.png" % [prefix, view_name])
		var img := root.get_texture().get_image()
		print("saved ", path, " ", img.get_size(), " err ", img.save_png(path))
	quit(0)
