extends SceneTree
## Renders props3d/prop_room.tscn from the front and from behind, below the floor line, into
## evidence/props3d/. Needs a window (not --headless):
##   godot --path godot --script res://tests/capture_props3d.gd

const OUT := "res://../evidence/props3d/"
const VIEWS := {
	"prop_room_front": [Vector3(0, 1.3, 4.5), Vector3(0, 0.7, 0)],
	"prop_room_back_low": [Vector3(0.8, 0.25, -3.8), Vector3(0, 0.6, 0)],
}


func _initialize() -> void:
	create_timer(30.0).timeout.connect(func(): print("TIMEOUT after 30 s"); quit(2))
	_run.call_deferred()


func _run() -> void:
	root.size = Vector2i(1280, 720)
	var room: Node3D = load("res://props3d/prop_room.tscn").instantiate()
	root.add_child(room)
	var cam := room.get_node("Camera") as Camera3D
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT))
	for view_name in VIEWS:
		var v: Array = VIEWS[view_name]
		cam.look_at_from_position(v[0], v[1])
		for i in 5:
			await process_frame
		await RenderingServer.frame_post_draw
		var path := ProjectSettings.globalize_path(OUT + view_name + ".png")
		var err := root.get_texture().get_image().save_png(path)
		print("saved ", path, " err ", err)
	quit(0)
