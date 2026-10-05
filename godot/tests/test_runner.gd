extends SceneTree
## Headless automated checks. Run from the repo root:
##   godot --headless --path godot --script res://tests/test_runner.gd
## Each test builds a fresh fight scene, drives the fighters with ScriptedController, and steps
## the scene frame by frame (no real-time waiting). Exit code 0 = all passed.

const DT := 1.0 / 60.0
var failures := 0
var checks := 0


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	for t in ["test_walk_and_facing", "test_held_attack_starts_once", "test_jump_arc_and_states",
			"test_cross_over_flips_facing", "test_every_state_has_art"]:
		var main: Node = load("res://game/main.tscn").instantiate()
		root.add_child(main)
		await process_frame
		main.set_physics_process(false)     # the test drives step() itself
		print("- ", t)
		await call(t, main)
		main.queue_free()
		await process_frame
	print("%d checks, %d failed" % [checks, failures])
	quit(1 if failures else 0)


func expect(cond: bool, msg: String) -> void:
	checks += 1
	if not cond:
		failures += 1
		print("    FAIL: ", msg)


func run_frames(main: Node, n: int) -> void:
	for i in n:
		main.step(DT)


func test_walk_and_facing(main: Node) -> void:
	var p1: Fighter = main.p1
	p1.controller = ScriptedController.new([{"frames": 30, "move": 1.0}])
	var x0 := p1.position.x
	run_frames(main, 15)
	expect(p1.state == "walk", "walking state, got %s" % p1.state)
	run_frames(main, 15)
	expect(is_equal_approx(p1.position.x - x0, Fighter.WALK_FORWARD * 30 * DT), "walked 45 px forward, got %.2f" % (p1.position.x - x0))
	expect(p1.facing == 1, "P1 faces right toward P2")
	run_frames(main, 1)
	expect(p1.state == "idle", "idle after input stops")


func test_held_attack_starts_once(main: Node) -> void:
	var p1: Fighter = main.p1
	var starts := []
	p1.attack_started.connect(func(_f, kind): starts.append(kind))
	# punch button held for 90 frames: one press, one attack
	p1.controller = ScriptedController.new([{"frames": 90, "attack": "punch"}])
	run_frames(main, 2)
	expect(p1.state == "punch", "punch state after press")
	run_frames(main, 88)
	expect(starts == ["punch"], "held punch starts exactly one attack, got %s" % [starts])
	expect(p1.state == "idle", "back to idle after punch")
	# five separate presses, each after the longest attack (kick = 28 frames) has recovered
	var segs := []
	for i in 5:
		segs.append({"frames": 30, "attack": "kick" if i % 2 else "punch"})
	p1.controller = ScriptedController.new(segs)
	starts.clear()
	run_frames(main, 150)
	expect(starts.size() == 5, "5 presses -> 5 attacks, got %d" % starts.size())
	# a press during an attack is ignored (no input buffer)
	p1.controller = ScriptedController.new([{"frames": 10, "attack": "kick"}, {"frames": 30, "attack": "punch"}])
	starts.clear()
	run_frames(main, 40)
	expect(starts == ["kick"], "punch pressed mid-kick is ignored, got %s" % [starts])


func test_jump_arc_and_states(main: Node) -> void:
	var p1: Fighter = main.p1
	var seen := {}
	p1.controller = ScriptedController.new([{"frames": 1, "jump": true}])
	for i in 60:
		main.step(DT)
		seen[p1.art_state()] = true
	expect(seen.has("rise") and seen.has("fall"), "jump shows rise and fall images, saw %s" % [seen.keys()])
	expect(p1.position.y == Fighter.GROUND_Y and p1.state == "idle", "lands back on the ground")
	expect(p1.position.y <= Fighter.GROUND_Y, "never below the floor")


func test_cross_over_flips_facing(main: Node) -> void:
	var p1: Fighter = main.p1
	var p2: Fighter = main.p2
	p1.position.x = p2.position.x - 30.0
	p1.controller = ScriptedController.new([{"frames": 50, "move": 1.0, "jump": true}, {"frames": 5}])
	run_frames(main, 55)
	expect(p1.position.x > p2.position.x, "P1 jumped over P2")
	expect(p1.facing == -1 and p2.facing == 1, "both turned to face each other after landing")
	expect(p1.sprite.flip_h and not p2.sprite.flip_h, "sprites flipped to match facing")


func test_every_state_has_art(main: Node) -> void:
	for f in [main.p1, main.p2]:
		for s in ["idle", "walk", "crouch", "rise", "fall", "punch", "kick", "block", "hurt", "ko", "win"]:
			var r: String = f.art.resolve(s)
			expect(f.art.textures.has(r) and f.art.textures[r] != null, "%s has an image for %s" % [f.display_name, s])
		# the standing hurtbox must sit on the ground line and match the sheet's on-screen height
		var hb: Rect2 = f.art.hurtboxes["idle"]
		expect(absf(hb.end.y) < 2.0, "%s idle hurtbox reaches the feet (end.y=%.1f)" % [f.display_name, hb.end.y])
