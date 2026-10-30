extends SceneTree
## Movie Maker capture of the hurt flash in the running game, on an isolated copy (capture/game).
##   godot --path capture/game --write-movie capture/flash.avi --fixed-fps 60 --disable-vsync
##         --resolution 3840x2160 --script res://capture_flash.gd
## SCRIPTED INPUT, labelled as such in the film: the fighters are placed in punch range by this
## script, P1's punches are Input.action_press("p1_punch") (the real PlayerController reads them),
## and P2's kick comes from the game's own ScriptedController. Nothing in the game is changed; the
## flash is the committed driver (fighter/hurt_flash.gd) and Zhaohui's shader.
## Timeline (frames at 60): 0-59 settle; 60 P1 punch -> Aotake flashes; 180 P1 punch again;
## 300 Aotake kicks -> Akaken flashes; quit at 900 (15 s).

var main: Node
var frame := 0


func _initialize() -> void:
	main = load("res://game/main.tscn").instantiate()
	root.add_child(main)
	_setup.call_deferred()


func _setup() -> void:
	main.start_fight_now()
	var p1: Fighter = main.p1
	var p2: Fighter = main.p2
	p1.position.x = 280.0
	p2.position.x = p1.position.x + p1.reach("punch") + p2.body_half_width() - 8.0
	p2.controller = ScriptedController.new([{"frames": 240}, {"frames": 1, "attack": "kick"}, {"frames": 400}])
	process_frame.connect(_tick)


func _tick() -> void:
	frame += 1
	if frame == 60 or frame == 180:
		Input.action_press("p1_punch")
	elif frame == 62 or frame == 182:
		Input.action_release("p1_punch")
	if frame >= 900:
		print("flash capture done, frames ", frame, "; P1 health ", main.p1.health, ", P2 health ", main.p2.health)
		quit()
