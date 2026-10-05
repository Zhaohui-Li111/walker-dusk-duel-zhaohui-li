class_name ScriptedController
extends RefCounted
## Plays back a list of input segments for automated tests. A segment holds its inputs for
## `frames` frames, like a player holding keys. "attack" and "jump" count as pressed only on the
## segment's first frame, matching is_action_just_pressed for a held button.
##   ScriptedController.new([{"frames": 30, "move": 1.0}, {"frames": 60, "attack": "punch"}])

var segments: Array
var index := 0
var frame_in_segment := 0


func _init(segs: Array = []) -> void:
	segments = segs


func done() -> bool:
	return index >= segments.size()


func read(_fighter: Fighter) -> Intent:
	var it := Intent.new()
	if done():
		return it
	var seg: Dictionary = segments[index]
	it.move = seg.get("move", 0.0)
	it.crouch = seg.get("crouch", false)
	it.block = seg.get("block", false)
	if frame_in_segment == 0:
		it.jump = seg.get("jump", false)
		it.attack = seg.get("attack", "")
	frame_in_segment += 1
	if frame_in_segment >= int(seg["frames"]):
		index += 1
		frame_in_segment = 0
	return it
