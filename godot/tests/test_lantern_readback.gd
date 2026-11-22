extends SceneTree
## A7 step 3: read-back of Clip 1, the lantern flame (CHANGE-BRIEF.md, "The sheet", "The cycle
## spec", "Lantern decisions"). Run from the repo root:
##   scripts/run-test.sh test_lantern_readback.gd 60
## Reads the scene and its clip back and compares them with the brief. It proves the structure;
## whether the flame reads, wraps without a visible seam or sits well on the lantern is a frame
## strip and Zhaohui's eyes in the running game.

const SCENE := "res://animations/lantern_flame.tscn"
const CLIP_PATH := "res://animations/lantern_flicker.tres"
const SHEET := "res://art/sheets/lantern_flame.png"
const FPS := 10.0                    # brief: 10 fps
const FRAMES := 8                    # all 8 cells, order 0..7
const ORDER := [0, 1, 2, 3, 4, 5, 6, 7]
const HFRAMES := 4
const VFRAMES := 2
const CELL := Vector2i(12, 16)

var checks := 0
var failures := 0


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	print("lantern read-back: Godot %s" % Engine.get_version_info().string)
	var packed: PackedScene = load(SCENE)
	check(packed != null, "scene", "%s loads" % SCENE)
	if packed == null:
		return finish()
	var lantern: Node2D = packed.instantiate()
	root.add_child(lantern)
	await process_frame
	var sprite := lantern.get_node_or_null("Sprite2D") as Sprite2D
	var player := lantern.get_node_or_null("AnimationPlayer") as AnimationPlayer
	check(sprite != null and player != null, "scene", "LanternFlame has a Sprite2D and an AnimationPlayer")
	if sprite == null or player == null:
		return finish()

	# The sheet and its slicing.
	var tex := sprite.texture
	check(tex != null and tex.resource_path == SHEET, "sheet", "Sprite2D.texture is %s (got %s)" % [
			SHEET, tex.resource_path if tex else "null"])
	check(sprite.hframes == HFRAMES and sprite.vframes == VFRAMES, "sheet",
			"sliced hframes %d x vframes %d (got %d x %d)" % [HFRAMES, VFRAMES, sprite.hframes, sprite.vframes])
	if tex:
		check(tex.get_width() == CELL.x * HFRAMES and tex.get_height() == CELL.y * VFRAMES, "sheet",
				"sheet %d x %d = cell %d x %d times the grid (got %d x %d)" % [CELL.x * HFRAMES,
				CELL.y * VFRAMES, CELL.x, CELL.y, tex.get_width(), tex.get_height()])
	check(sprite.offset == Vector2(-6, -15) and not sprite.centered, "sheet",
			"registration: the cells' flame base (6, 15) sits on the node origin (offset %s)" % sprite.offset)

	# The clip lives as a resource, not built in code.
	check(player.has_animation("flicker"), "clip", "the AnimationPlayer has `flicker`")
	if not player.has_animation("flicker"):
		return finish()
	var clip := player.get_animation("flicker")
	check(clip.resource_path == CLIP_PATH, "clip", "`flicker` is the resource %s (got '%s')" % [
			CLIP_PATH, clip.resource_path])

	# Every track resolves.
	var problems := AnimChecks.track_problems(player)
	for p in problems:
		print("    track problem: %s" % p)
	check(problems.is_empty(), "tracks", "every track resolves to a real node and property (%d problems)" % problems.size())
	check(clip.get_track_count() == 1, "tracks", "one track (got %d)" % clip.get_track_count())
	var t := 0
	check(clip.track_get_type(t) == Animation.TYPE_VALUE and clip.track_get_path(t) == NodePath("Sprite2D:frame"),
			"tracks", "track 0 is a value track on Sprite2D:frame (got %s)" % clip.track_get_path(t))
	if clip.track_get_type(t) == Animation.TYPE_VALUE:
		check(clip.value_track_get_update_mode(t) == Animation.UPDATE_DISCRETE, "update",
				"the frame track uses Animation.UPDATE_DISCRETE (got %d)" % clip.value_track_get_update_mode(t))

	# Key times, values, frame range: compared with a tolerance of half a frame period.
	var tol := 0.5 / FPS
	var n := clip.track_get_key_count(t)
	check(n == FRAMES, "keys", "%d keys (got %d)" % [FRAMES, n])
	for k in mini(n, FRAMES):
		var time := clip.track_get_key_time(t, k)
		var value: int = clip.track_get_key_value(t, k)
		check(absf(time - k / FPS) < tol, "keys", "key %d at %.4f s, brief %.4f s" % [k, time, k / FPS])
		check(value == ORDER[k], "order", "key %d shows cell %d (brief %d)" % [k, value, ORDER[k]])
		check(value >= 0 and value < sprite.hframes * sprite.vframes, "range",
				"key %d's cell %d is inside the sheet (< %d)" % [k, value, sprite.hframes * sprite.vframes])

	# Step, length, loop mode, seam.
	check(is_equal_approx(clip.step, 1.0 / FPS), "step", "step is one frame period, %.4f s (got %.6f)" % [1.0 / FPS, clip.step])
	check(absf(clip.length - FRAMES / FPS) < tol, "length", "length %.2f s (got %.4f)" % [FRAMES / FPS, clip.length])
	check(clip.loop_mode == Animation.LOOP_LINEAR, "loop", "loop_mode is Animation.LOOP_LINEAR (got %d)" % clip.loop_mode)
	if n >= 2:
		var last := clip.track_get_key_time(t, n - 1)
		var interval := clip.track_get_key_time(t, 1) - clip.track_get_key_time(t, 0)
		check(absf((clip.length - last) - interval) < tol, "seam",
				"gap from the last key to length (%.4f s) equals the key interval (%.4f s)" % [clip.length - last, interval])
		check(clip.track_get_key_value(t, n - 1) != clip.track_get_key_value(t, 0), "seam",
				"no duplicate across the wrap: last cell %d, first cell %d" % [
				clip.track_get_key_value(t, n - 1), clip.track_get_key_value(t, 0)])

	# The one authority, and its clock.
	check(player.autoplay == "", "authority", "autoplay is empty; the root script starts the clip once")
	check(player.callback_mode_process == AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_IDLE, "clock",
			"callback_mode_process is ANIMATION_CALLBACK_MODE_PROCESS_IDLE (got %d)" % player.callback_mode_process)
	var players := lantern.find_children("*", "AnimationPlayer", true, false)
	check(players.size() == 1, "authority", "one AnimationPlayer in the lantern scene (got %d)" % players.size())
	var code := ""                   # the script's code, with comments stripped
	for line in FileAccess.get_file_as_string((lantern.get_script() as Script).resource_path).split("\n"):
		code += line.get_slice("#", 0) + "\n"
	check(not code.contains("frame") and not code.to_lower().contains("sprite"), "authority",
			"lantern_flame.gd's code (comments stripped) never names the sprite or its frame")
	check(player.is_playing() and player.current_animation == "flicker", "authority",
			"after _ready, `flicker` is playing (current_animation '%s')" % player.current_animation)
	finish()


func check(cond: bool, rule: String, msg: String) -> void:
	checks += 1
	if not cond:
		failures += 1
	print("%s [%s] %s" % ["PASS" if cond else "FAIL", rule, msg])


func finish() -> void:
	print("%d checks, %d failed" % [checks, failures])
	quit(1 if failures else 0)
