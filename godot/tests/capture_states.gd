extends SceneTree
## Renders every state of both fighters with collision boxes on (F1 view) and saves screenshots,
## for the "character against the sheet" check. Needs a window (not --headless):
##   godot --path godot --script res://tests/capture_states.gd
## Output: evidence/states/<fighter>_<state>.png in the repo (one level above godot/).

const STATES := ["idle", "walk", "crouch", "rise", "fall", "punch", "kick", "block", "hurt", "ko", "win"]


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	var out := ProjectSettings.globalize_path("res://").path_join("../evidence/states")
	DirAccess.make_dir_recursive_absolute(out)
	var main: Node = load("res://game/main.tscn").instantiate()
	root.add_child(main)
	await process_frame
	main.set_physics_process(false)
	main.start_fight_now()            # no title overlay over the fighters
	var p1: Fighter = main.p1
	var p2: Fighter = main.p2
	p1.position = Vector2(250, Fighter.GROUND_Y)
	p2.position = Vector2(400, Fighter.GROUND_Y)
	for f in [p1, p2]:
		f.controller = null
		f.show_boxes = true
	for s in STATES:
		for f in [p1, p2]:
			f.state = "jump" if s in ["rise", "fall"] else s
			f.velocity.y = -1.0 if s == "rise" else (1.0 if s == "fall" else 0.0)
			f.position.y = Fighter.GROUND_Y - (40.0 if s in ["rise", "fall"] else 0.0)
			f._update_sprite()
		await process_frame
		await process_frame
		var img := root.get_viewport().get_texture().get_image()
		img.save_png(out.path_join("%s.png" % s))
	print("saved ", STATES.size(), " screenshots to ", out)
	quit()
