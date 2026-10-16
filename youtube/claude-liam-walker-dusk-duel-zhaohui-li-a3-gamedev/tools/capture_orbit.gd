extends SceneTree
## Movie Maker driver for the film: loads props3d/prop_room.tscn unchanged and moves only its
## Camera along a fixed orbit, one step per rendered frame (deterministic at --fixed-fps 60).
## 0-24 s: one full turn round the props, eye height 1.40 m at the front, 0.35 m at the back
## (the low pass looks under the drum and the lantern roof). Quits after 24 s.
##   godot --path capture/game --write-movie capture/orbit.avi --fixed-fps 60 --disable-vsync \
##       --resolution 3840x2160 --script res://capture_orbit.gd

const FPS := 60
const SECONDS := 24.0
const TARGET := Vector3(0, 0.62, 0)
const RADIUS := 4.6
var cam: Camera3D
var frame := 0


func _initialize() -> void:
	root.size = Vector2i(3840, 2160)
	var room: Node3D = load("res://props3d/prop_room.tscn").instantiate()
	root.add_child(room)
	cam = room.get_node("Camera") as Camera3D
	_place(0.0)


func _place(t: float) -> void:
	var a := TAU * t / SECONDS                      # 0 = in front (+Z), as in the saved scene
	var h := 0.875 + 0.525 * cos(a)                  # 1.40 m in front, 0.35 m behind
	cam.look_at_from_position(Vector3(RADIUS * sin(a), h, RADIUS * cos(a)), TARGET)


func _process(_delta: float) -> bool:
	frame += 1
	_place(frame / float(FPS))
	if frame >= int(SECONDS * FPS):
		print("orbit done, frames ", frame)
		return true
	return false
