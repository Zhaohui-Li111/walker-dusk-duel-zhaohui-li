extends SceneTree
## A7 step 4: read-back of Clip 2, the kick arc rig (CHANGE-BRIEF.md, "The phase table", "The two
## clocks"). Run from the repo root:
##   scripts/run-test.sh test_kick_readback.gd 60
## Reads fighter.tscn's KickRig back: every track resolves (AnimChecks.track_problems, branching on
## track type), keys sit on the phase table's boundaries at 60 fps, step, length and loop mode match
## the brief, and no track writes outside the rig. Whether the arc reads, or the three phases look
## distinct, is a frame strip and Zhaohui's eyes.

const SCENE := "res://fighter/fighter.tscn"
const FPS := 60.0
const KEY_FRAMES := [0, 7, 8, 12, 13, 27, 28]   # phase boundaries 0 / 8 / 13 / 28 and the frames before them
const BOUNDARIES := {"startup": 0, "active": 8, "recovery": 13, "end": 28}
const LENGTH_FRAMES := 28

var checks := 0
var failures := 0


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	print("kick arc read-back: Godot %s" % Engine.get_version_info().string)
	var fighter: Node2D = (load(SCENE) as PackedScene).instantiate()
	root.add_child(fighter)
	await process_frame
	var rig := fighter.get_node_or_null("KickRig") as Node2D
	var player := fighter.get_node_or_null("KickRig/AnimationPlayer") as AnimationPlayer
	check(rig != null and player != null, "scene", "Fighter has KickRig and KickRig/AnimationPlayer")
	if player == null:
		return finish()
	check(player.get_node_or_null(player.root_node) == rig, "scene",
			"the player's root_node (%s) is KickRig" % player.root_node)
	for n in ["kick_arc", "rest"]:
		check(player.has_animation(n), "clip", "the AnimationPlayer has `%s`" % n)
	if not (player.has_animation("kick_arc") and player.has_animation("rest")):
		return finish()
	var clip := player.get_animation("kick_arc")
	var rest := player.get_animation("rest")
	check(clip.resource_path == "res://animations/kick_arc.tres" and rest.resource_path == "res://animations/kick_rest.tres",
			"clip", "both clips are resources in godot/animations/ (%s, %s)" % [clip.resource_path, rest.resource_path])

	var problems := AnimChecks.track_problems(player)
	for p in problems:
		print("    track problem: %s" % p)
	check(problems.is_empty(), "tracks", "every track resolves to a real node and property (%d problems)" % problems.size())

	# One authority: every track writes inside the rig, never the fighter or its Sprite2D.
	var sprite := fighter.get_node("Sprite2D")
	for name in ["kick_arc", "rest"]:
		var c := player.get_animation(name)
		for t in c.get_track_count():
			var target := rig.get_node_or_null(NodePath(c.track_get_path(t).get_concatenated_names()))
			check(target != null and target != rig and rig.is_ancestor_of(target) and target != sprite, "authority",
					"%s track %d (%s) writes inside KickRig, not the fighter or its Sprite2D" % [name, t, c.track_get_path(t)])
			if c.track_get_type(t) == Animation.TYPE_VALUE and c.track_get_path(t).get_subname(0) == "visible":
				check(c.value_track_get_update_mode(t) == Animation.UPDATE_DISCRETE, "update",
						"%s track %d (visible) is UPDATE_DISCRETE" % [name, t])

	# Step, length, loop mode.
	var tol := 0.5 / FPS
	check(is_equal_approx(clip.step, 1.0 / FPS) or absf(clip.step - 1.0 / FPS) < 1e-6, "step",
			"kick_arc step is one frame period at 60 fps, %.6f s (got %.6f)" % [1.0 / FPS, clip.step])
	check(absf(clip.length - LENGTH_FRAMES / FPS) < tol, "length",
			"kick_arc length is frame %d / 60 = %.4f s (got %.6f)" % [LENGTH_FRAMES, LENGTH_FRAMES / FPS, clip.length])
	check(clip.loop_mode == Animation.LOOP_NONE, "loop", "kick_arc loop_mode is Animation.LOOP_NONE (got %d)" % clip.loop_mode)
	check(rest.loop_mode == Animation.LOOP_NONE, "loop", "rest loop_mode is Animation.LOOP_NONE (got %d)" % rest.loop_mode)

	# Key times from the phase table, with a tolerance of half a frame period.
	for t in clip.get_track_count():
		var sub := clip.track_get_path(t).get_subname(0)
		if sub == "visible":
			check(clip.track_get_key_count(t) == 2 and absf(clip.track_get_key_time(t, 0)) < tol
					and absf(clip.track_get_key_time(t, 1) - LENGTH_FRAMES / FPS) < tol
					and clip.track_get_key_value(t, 0) == true and clip.track_get_key_value(t, 1) == false,
					"keys", "visible: shown from frame 0, hidden at frame %d" % LENGTH_FRAMES)
			continue
		var n := clip.track_get_key_count(t)
		check(n == KEY_FRAMES.size(), "keys", "%s: %d keys (got %d)" % [sub, KEY_FRAMES.size(), n])
		for k in mini(n, KEY_FRAMES.size()):
			var f: int = KEY_FRAMES[k]
			var time := clip.track_get_key_time(t, k)
			check(absf(time - f / FPS) < tol, "keys", "%s key %d at %.6f s = frame %d (%.6f)" % [sub, k, time, f, f / FPS])
		for phase in BOUNDARIES:
			var f: int = BOUNDARIES[phase]
			check(clip.find_track(clip.track_get_path(t), Animation.TYPE_VALUE) == t
					and _has_key_at(clip, t, f / FPS, tol), "boundary",
					"%s has a key where %s begins, frame %d" % [sub, phase, f])
		# Spacing: accelerate into the active frames, settle through recovery.
		var k7 := KEY_FRAMES.find(7)
		var k13 := KEY_FRAMES.find(13)
		check(clip.track_get_key_transition(t, k7) > 1.0, "spacing",
				"%s eases in (accelerates) from frame 7 into active (transition %.2f > 1)" % [sub, clip.track_get_key_transition(t, k7)])
		check(clip.track_get_key_transition(t, k13) < 1.0, "spacing",
				"%s eases out (settles) through recovery from frame 13 (transition %.2f < 1)" % [sub, clip.track_get_key_transition(t, k13)])
		if sub == "modulate":
			# TUNING.md A7 r1 (Zhaohui approved): the wind-up arc shows from frame 0.
			var a0: float = (clip.track_get_key_value(t, 0) as Color).a
			check(a0 > 0.0 and is_equal_approx(a0, 0.25), "r1",
					"modulate key 0: the arc is visible from frame 0 (alpha %.2f, r1 0.25)" % a0)

	# The clock and the authority's settings.
	check(player.callback_mode_process == AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL, "clock",
			"callback_mode_process is ANIMATION_CALLBACK_MODE_PROCESS_MANUAL (got %d)" % player.callback_mode_process)
	check(player.autoplay == "", "authority", "autoplay is empty")
	var players := fighter.find_children("*", "AnimationPlayer", true, false)
	check(players.size() == 1, "authority", "one AnimationPlayer in fighter.tscn (got %d)" % players.size())
	var pivot := rig.get_node("Pivot") as Node2D
	check(not pivot.visible, "rest", "the arc starts hidden")
	finish()


func _has_key_at(clip: Animation, t: int, time: float, tol: float) -> bool:
	for k in clip.track_get_key_count(t):
		if absf(clip.track_get_key_time(t, k) - time) < tol:
			return true
	return false


func check(cond: bool, rule: String, msg: String) -> void:
	checks += 1
	if not cond:
		failures += 1
	print("%s [%s] %s" % ["PASS" if cond else "FAIL", rule, msg])


func finish() -> void:
	print("%d checks, %d failed" % [checks, failures])
	quit(1 if failures else 0)
