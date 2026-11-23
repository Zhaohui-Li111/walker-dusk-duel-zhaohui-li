extends Node2D
## A7 preview for the frame strips (CHANGE-BRIEF.md, "Frame strips"). A fixture, not gameplay
## capture: the real main.tscn (stage, both lanterns, both fighters, HUD) with the title skipped,
## P2 standing still, and P1 driven by a ScriptedController so the kick starts on a known tick.
## Run windowed with Movie Maker at 30 fps (2 physics ticks per captured frame):
##   godot --path godot res://previews/kick_arc_preview.tscn --write-movie "$PWD/captures/kick_arc/r0/frame.png" --fixed-fps 30 --quit-after 90
## The kick is read on the second physics tick of capture frame KICK_FRAME, so that frame shows
## Fighter.frame 0 and capture frame n shows Fighter.frame 2 * (n - KICK_FRAME): 13 -> 6, 14 -> 8
## (active), 16 -> 12, 17 -> 14 (recovery), 23 -> 26, 24 -> 28 (idle). P1 is out of range, so the
## kick whiffs and no hitstop shifts the count. The lanterns are in the same shot.
## Every frame writes one line to logs/kick_arc_preview_frames.log, so capture frame N lines up
## with log line N + 1 (line 1 is the header). The preview writes no game state after setup.

const KICK_FRAME := 10
const REPEAT_FRAMES := 45            # then again every 1.5 s, for watching it play; frames 0-24 unchanged

var main: Node
var frame := 0
var log_lines := PackedStringArray()


func _ready() -> void:
	main = load("res://game/main.tscn").instantiate()
	add_child(main)
	_setup.call_deferred()


func _setup() -> void:
	main.start_fight_now()           # SETUP: skip the title and intro, as the capture tools do
	main.p2.controller = null        # SETUP: Aotake stands still
	main.p1.controller = ScriptedController.new([])
	log_lines.append("capture_frame physics_tick p1_state p1_frame rig_clip rig_time pivot_visible pivot_rot_deg lantern_left_t lantern_right_t")


func _process(_delta: float) -> void:
	if frame >= KICK_FRAME - 1 and (frame - (KICK_FRAME - 1)) % REPEAT_FRAMES == 0:
		# Read from the next iteration's physics ticks: idle on the first, kick on the second.
		main.p1.controller = ScriptedController.new([{"frames": 1}, {"frames": 1, "attack": "kick"}, {"frames": 600}])
	var ap: AnimationPlayer = main.p1.get_node("KickRig/AnimationPlayer")
	var pivot: Node2D = main.p1.get_node("KickRig/Pivot")
	log_lines.append("%d %d %s %d %s %.4f %s %.1f %.3f %.3f" % [frame, Engine.get_physics_frames(),
			main.p1.state, main.p1.frame, ap.current_animation, ap.current_animation_position,
			pivot.visible, rad_to_deg(pivot.rotation),
			main.get_node("LanternLeft/AnimationPlayer").current_animation_position,
			main.get_node("LanternRight/AnimationPlayer").current_animation_position])
	frame += 1


func _exit_tree() -> void:
	var path := ProjectSettings.globalize_path("res://").path_join("../logs/kick_arc_preview_frames.log")
	var f := FileAccess.open(path, FileAccess.WRITE)
	if f:
		f.store_string("\n".join(log_lines) + "\n")
		f.close()
		print("kick_arc_preview: %d frames logged to %s" % [log_lines.size() - 1, path])
