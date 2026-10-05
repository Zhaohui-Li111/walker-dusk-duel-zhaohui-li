extends SceneTree
## Renders the storyboard moments the slice covers, with scripted input, and saves screenshots to
## evidence/flow/. These are scripted-input captures (label them so in the report and film).
##   godot --path godot --script res://tests/capture_flow.gd

var main: Node
var out: String


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	out = ProjectSettings.globalize_path("res://").path_join("../evidence/flow")
	DirAccess.make_dir_recursive_absolute(out)
	main = load("res://game/main.tscn").instantiate()
	root.add_child(main)
	await process_frame
	main.set_physics_process(false)
	var p1: Fighter = main.p1
	var p2: Fighter = main.p2
	await shot("01_title")
	main.start_round()
	p1.controller = null
	p2.controller = null
	steps(10)
	await shot("02_round_call")
	steps(60)
	# P3: jab meets block
	p2.position.x = p1.position.x + p1.reach("punch") + p2.body_half_width() - 4.0
	p2.controller = ScriptedController.new([{"frames": 40, "block": true}])
	p1.controller = ScriptedController.new([{"frames": 30, "attack": "punch"}])
	await until_result(p1, "blocked")
	await shot("03_block")
	steps(40)
	# P4: kick lands (the block pushed Aotake back, so step her into range again)
	p2.controller = null
	p2.position.x = p1.position.x + p1.reach("kick") + p2.body_half_width() - 4.0
	p1.controller = ScriptedController.new([{"frames": 30, "attack": "kick"}])
	await until_result(p1, "hit")
	steps(2)
	await shot("04_hit")
	steps(40)
	# P5: player is hit by the long kick
	p1.position.x = p2.position.x - p2.reach("kick") - p1.body_half_width() + 4.0
	p1.controller = null
	p2.controller = ScriptedController.new([{"frames": 30, "attack": "kick"}])
	await until_result(p2, "hit")
	steps(4)
	await shot("05_player_hurt")
	steps(40)
	# pause overlay
	main.set_paused(true)
	await shot("06_paused")
	main.set_paused(false)
	main.audio.toggle_mute("Music")
	main.audio.toggle_mute("SFX")
	await shot("06b_muted_indicator")
	main.audio.toggle_mute("Music")
	main.audio.toggle_mute("SFX")
	# P8: final hit, K.O., result
	p2.health = 5
	p2.controller = null
	p2.position.x = p1.position.x + p1.reach("punch") + p2.body_half_width() - 4.0
	p1.controller = ScriptedController.new([{"frames": 30, "attack": "punch"}])
	await until_result(p1, "hit")
	steps(6)
	await shot("07_ko")
	steps(main.KO_FRAMES)
	await shot("08_result")
	main.confirm()
	steps(5)
	await shot("09_rematch")
	print("saved flow screenshots to ", out)
	quit()


func steps(n: int) -> void:
	for i in n:
		main.step(1.0 / 60.0)


func until_result(f: Fighter, want: String) -> void:
	var got := [""]
	var cb := func(_f, _k, r, _p): got[0] = r
	f.attack_resolved.connect(cb)
	for i in 120:
		main.step(1.0 / 60.0)
		if got[0] != "":
			break
	f.attack_resolved.disconnect(cb)
	if got[0] != want:
		push_error("expected %s, got %s" % [want, got[0]])


func shot(name: String) -> void:
	await process_frame
	await process_frame
	root.get_viewport().get_texture().get_image().save_png(out.path_join(name + ".png"))
