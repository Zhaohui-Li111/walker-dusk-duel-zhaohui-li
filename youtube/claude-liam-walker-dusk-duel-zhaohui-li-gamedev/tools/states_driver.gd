extends Node
## Harness for the film's staged-pose still (B07), used only in capture/game-states. Same steps
## as godot/tests/capture_states.gd (positions, states, collision boxes on), but run inside the
## main scene so Movie Maker renders the viewport at 3840x2160. Staged poses, labelled as such.

const STATES := ["idle", "punch", "kick", "block", "hurt", "ko"]
var main: Node
var i := 0
var wait := 0


func _physics_process(_delta: float) -> void:
	if main == null:
		main = get_tree().current_scene
		if main == null or not main.has_method("start_fight_now"):
			main = null
			return
		main.set_physics_process(false)
		main.start_fight_now()
		for f in [main.p1, main.p2]:
			f.controller = null
			f.show_boxes = true
		_pose()
		return
	wait += 1
	if wait < 4:
		return
	var out := ProjectSettings.globalize_path("res://").path_join("../evidence/states")
	DirAccess.make_dir_recursive_absolute(out)
	get_viewport().get_texture().get_image().save_png(out.path_join("%s.png" % STATES[i]))
	i += 1
	if i >= STATES.size():
		print("states driver: saved ", STATES.size(), " stills to ", out)
		get_tree().quit()
		return
	_pose()


func _pose() -> void:
	wait = 0
	main.p1.position = Vector2(250, Fighter.GROUND_Y)
	main.p2.position = Vector2(400, Fighter.GROUND_Y)
	for f in [main.p1, main.p2]:
		f.state = STATES[i]
		f.velocity = Vector2.ZERO
		f._update_sprite()
		f.queue_redraw()
