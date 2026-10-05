extends SceneTree
## Headless automated checks. Run from the repo root:
##   godot --headless --path godot --script res://tests/test_runner.gd
## Each test builds a fresh fight scene, skips the title/intro, drives the fighters with
## ScriptedController (or the CPU), and steps the scene frame by frame (no real-time waiting).
## Exit code 0 = all passed.

const DT := 1.0 / 60.0
const TESTS := [
	# step 1: movement and state images
	"test_walk_and_facing", "test_held_attack_starts_once", "test_jump_arc_and_states",
	"test_cross_over_flips_facing", "test_every_state_has_art",
	# step 2: combat and round flow
	"test_punch_hits_once", "test_point_blank_attacks_connect", "test_out_of_range_whiffs", "test_block_takes_no_damage",
	"test_hurt_pushes_away_from_attacker", "test_ko_once_then_result_and_rematch",
	"test_every_attack_resolves_exactly_once", "test_cpu_is_deterministic_and_attacks",
	"test_pause_freezes_the_fight",
]
var failures := 0
var checks := 0


func _initialize() -> void:
	# watchdog: a script error inside a test must not leave Godot running forever
	create_timer(120.0).timeout.connect(func(): print("TIMEOUT after 120 s"); quit(2))
	_run.call_deferred()


func _run() -> void:
	for t in TESTS:
		var main := await fresh()
		print("- ", t)
		await call(t, main)
		if is_instance_valid(main):
			main.queue_free()
		await process_frame
	print("%d checks, %d failed" % [checks, failures])
	quit(1 if failures else 0)


func fresh() -> Node:
	var main: Node = load("res://game/main.tscn").instantiate()
	root.add_child(main)
	await process_frame
	main.set_physics_process(false)     # the test drives step() itself
	main.start_fight_now()
	main.p1.controller = null
	main.p2.controller = null
	return main


func expect(cond: bool, msg: String) -> void:
	checks += 1
	if not cond:
		failures += 1
		print("    FAIL: ", msg)


func run_frames(main: Node, n: int) -> void:
	for i in n:
		main.step(DT)


## Distance between origins at which `kind` from `a` just reaches `b`.
func in_range(a: Fighter, b: Fighter, kind: String) -> float:
	return a.reach(kind) + b.body_half_width() - 4.0


func record(f: Fighter) -> Array:
	var log := []
	f.attack_started.connect(func(_f, kind): log.append(["start", kind]))
	f.attack_resolved.connect(func(_f, kind, result, _p): log.append([result, kind]))
	return log


# --- step 1 ------------------------------------------------------------------

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
		var hb: Rect2 = f.art.hurtboxes["idle"]
		expect(absf(hb.end.y) < 2.0, "%s idle hurtbox reaches the feet (end.y=%.1f)" % [f.display_name, hb.end.y])


# --- step 2 ------------------------------------------------------------------

func test_punch_hits_once(main: Node) -> void:
	var p1: Fighter = main.p1
	var p2: Fighter = main.p2
	p2.position.x = p1.position.x + in_range(p1, p2, "punch")
	var log := record(p1)
	var hurt_seen := [false]
	p2.state_changed.connect(func(_f, s): hurt_seen[0] = hurt_seen[0] or s == "hurt")
	# hitbox and hurtbox overlap for all 4 active frames: still one hit
	p1.controller = ScriptedController.new([{"frames": 60, "attack": "punch"}])
	for i in 60:
		main.step(DT)
		if log.size() == 2 and log[1][0] == "hit" and not hurt_seen.has("image"):
			hurt_seen.append("image")
			expect(p2.sprite.texture == p2.art.textures["hurt"], "hurt image shows on the hit frame, not after hitstop")
	expect(log == [["start", "punch"], ["hit", "punch"]], "one punch, one hit, got %s" % [log])
	expect(p2.health == Fighter.MAX_HEALTH - 8, "punch does 8 damage, health %d" % p2.health)
	expect(hurt_seen[0] and p2.state == "idle", "P2 showed hurt, then recovered to idle")

func test_point_blank_attacks_connect(main: Node) -> void:
	# Regression: tip-only hitboxes let a kick pass beyond a touching opponent and whiff.
	var p1: Fighter = main.p1
	var p2: Fighter = main.p2
	p2.position.x = p1.position.x + p1.body_half_width() + p2.body_half_width()
	var log := record(p1)
	p1.controller = ScriptedController.new([{"frames": 50, "attack": "kick"}, {"frames": 40, "attack": "punch"}])
	run_frames(main, 90)
	var results := log.filter(func(e): return e[0] != "start").map(func(e): return e[0])
	expect(results == ["hit", "hit"], "kick and punch at touching distance both hit, got %s" % [results])


func test_out_of_range_whiffs(main: Node) -> void:
	var p1: Fighter = main.p1
	var p2: Fighter = main.p2
	p2.position.x = p1.position.x + 200.0
	var log := record(p1)
	p1.controller = ScriptedController.new([{"frames": 30, "attack": "punch"}, {"frames": 30, "attack": "kick"}, {"frames": 30, "attack": "punch"}])
	run_frames(main, 90)
	var results := log.filter(func(e): return e[0] != "start").map(func(e): return e[0])
	expect(results == ["whiff", "whiff", "whiff"], "three whiffs, got %s" % [results])
	expect(p2.health == Fighter.MAX_HEALTH, "no damage")


func test_block_takes_no_damage(main: Node) -> void:
	var p1: Fighter = main.p1
	var p2: Fighter = main.p2
	p2.position.x = p1.position.x + in_range(p1, p2, "kick")
	p2.controller = ScriptedController.new([{"frames": 400, "block": true}])
	var log := record(p1)
	# block pushes the defender back a few px, so the attacker steps in before each kick, as a player would
	var segs := []
	for i in 5:
		segs.append({"frames": 10, "move": 1.0})
		segs.append({"frames": 34, "attack": "kick"})
	p1.controller = ScriptedController.new(segs)
	run_frames(main, 5 * 44)
	var results := log.filter(func(e): return e[0] != "start").map(func(e): return e[0])
	expect(results == ["blocked", "blocked", "blocked", "blocked", "blocked"], "5 kicks blocked, got %s" % [results])
	expect(p2.health == Fighter.MAX_HEALTH, "blocking takes no damage, health %d" % p2.health)


func test_hurt_pushes_away_from_attacker(main: Node) -> void:
	var p1: Fighter = main.p1
	var p2: Fighter = main.p2
	p1.position.x = p2.position.x - in_range(p2, p1, "kick")
	p2.controller = ScriptedController.new([{"frames": 40, "attack": "kick"}])
	var x0 := p1.position.x
	run_frames(main, 20)
	expect(p1.state == "hurt", "P1 is in hurt after Aotake's kick, got %s" % p1.state)
	expect(p1.position.x < x0, "P1 pushed left, away from the kick (%.1f -> %.1f)" % [x0, p1.position.x])
	expect(p1.health == Fighter.MAX_HEALTH - 14, "kick does 14 damage, health %d" % p1.health)


func test_ko_once_then_result_and_rematch(main: Node) -> void:
	var p1: Fighter = main.p1
	var p2: Fighter = main.p2
	p2.position.x = p1.position.x + in_range(p1, p2, "punch")
	p2.health = 5
	var kos := []
	p2.knocked_out.connect(func(f): kos.append(f.display_name))
	var log := record(p1)
	p1.controller = ScriptedController.new([{"frames": 30, "attack": "punch"}, {"frames": 30, "attack": "punch"}])
	run_frames(main, 60)
	expect(kos == ["AOTAKE"], "one K.O., got %s" % [kos])
	expect(p2.state == "ko" and p2.hurtbox() == null, "K.O. fighter has no hurtbox")
	expect(main.phase == "ko", "phase is ko, got %s" % main.phase)
	expect(log.count(["start", "punch"]) == 1, "input locked after K.O.: second punch not started")
	run_frames(main, Fighter.ATTACKS["punch"]["startup"] + main.KO_FRAMES)
	expect(main.phase == "result" and p1.state == "win", "result screen with the winner posing (%s, %s)" % [main.phase, p1.state])
	main.confirm()
	expect(main.round_number == 2 and main.phase == "intro", "Enter starts round 2")
	expect(p1.health == Fighter.MAX_HEALTH and p2.health == Fighter.MAX_HEALTH and p2.state == "idle", "both reset to full health and idle")


func test_every_attack_resolves_exactly_once(main: Node) -> void:
	# CPU Aotake against a scripted Akaken that mixes punches, kicks, walking and blocking.
	var p1: Fighter = main.p1
	var p2: Fighter = main.p2
	p2.controller = CpuController.new(42)
	var segs := []
	for i in 40:
		segs.append({"frames": 8, "move": 1.0})
		segs.append({"frames": 26 + i % 7, "attack": ["punch", "kick"][i % 2]})
		if i % 5 == 0:
			segs.append({"frames": 20, "block": true})
	p1.controller = ScriptedController.new(segs)
	var logs := [record(p1), record(p2)]
	run_frames(main, 2400)
	for i in 2:
		var log: Array = logs[i]
		var ok := true
		for j in log.size():
			var expect_start := j % 2 == 0
			if (log[j][0] == "start") != expect_start or (j % 2 == 1 and log[j][1] != log[j - 1][1]):
				ok = false
		var open: bool = log.size() % 2 == 1 and main.phase == "fight"   # one attack may still be running
		expect(ok and (log.size() % 2 == 0 or open or main.phase != "fight"), "%s: start/result strictly alternate (%d events)" % [["P1", "P2"][i], log.size()])
	var results: Array = (logs[0] + logs[1]).map(func(e): return e[0])
	print("    results: hit %d, blocked %d, whiff %d, interrupted %d, phase %s" % [
		results.count("hit"), results.count("blocked"), results.count("whiff"), results.count("interrupted"), main.phase])
	expect(results.count("hit") > 0 and results.count("whiff") > 0, "the mix produced hits and whiffs")


func test_cpu_is_deterministic_and_attacks(main: Node) -> void:
	var healths := []
	for run in 2:
		var m: Node = main if run == 0 else await fresh()
		m.p2.controller = CpuController.new(99)
		var log := record(m.p2)
		run_frames(m, 600)
		healths.append(m.p1.health)
		expect(log.count(["start", "kick"]) > 0, "CPU kicked at least once (run %d)" % run)
		if run == 1:
			m.queue_free()
	expect(healths[0] == healths[1] and healths[0] < Fighter.MAX_HEALTH, "same seed, same result: %s" % [healths])


func test_pause_freezes_the_fight(main: Node) -> void:
	var p1: Fighter = main.p1
	p1.controller = ScriptedController.new([{"frames": 200, "move": 1.0}])
	run_frames(main, 10)
	main.set_paused(true)
	var x := p1.position.x
	run_frames(main, 60)
	expect(p1.position.x == x and main.hud.message == "PAUSED", "nothing moves while paused")
	main.set_paused(false)
	run_frames(main, 10)
	expect(p1.position.x > x and main.hud.message == "", "resumes and clears the message")
