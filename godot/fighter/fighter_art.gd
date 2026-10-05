class_name FighterArt
extends RefCounted
## State images and collision boxes for one fighter, all derived from res://data/poses.json
## (written by tools/make_poses.py + tools/export_placeholders.py). Every state image shares one
## canvas, so the sprite offset is computed from the pose's hip and ground line: swapping states
## never makes the fighter jump on screen, and boxes line up with the art they were designed on.
##
## A generated image at res://art/<fighter>/<state>.png replaces the placeholder at
## res://art/placeholder/<fighter>/<state>.png. States a fighter has no image for fall back
## (Aotake has no walk/jump/punch/win poses, see CHARACTER-SHEET appendix).

const FALLBACK := {"walk": "idle", "crouch": "idle", "rise": "idle", "fall": "idle",
		"punch": "kick", "win": "idle"}

var fighter_id: String
var scale: float
var textures := {}        # state -> Texture2D
var sources := {}         # state -> "generated" | "placeholder"
var anchor := {}          # state -> Vector2 (canvas px of hip x, effective ground y)
var hurtboxes := {}       # state -> Rect2 in fighter space, facing right (missing = no hurtbox)
var hitboxes := {}        # state -> Rect2 in fighter space, facing right


static func load_for(id: String) -> FighterArt:
	var art := FighterArt.new()
	art.fighter_id = id
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/poses.json"))
	var f: Dictionary = data["fighters"][id]
	art.scale = f["canvas_to_screen_scale"]
	var ground: float = data["ground_y"]
	var states: Dictionary = f["states"]
	for state in states:
		var pose: Dictionary = f["poses"][states[state]]
		var kp: Array = pose["keypoints"]
		var hip_x: float = (kp[8][0] + kp[11][0]) / 2.0
		var ground_eff: float = ground - float(pose["angles"]["airborne_px"])
		art.anchor[state] = Vector2(hip_x, ground_eff)
		if pose["hurtbox"] != null:
			art.hurtboxes[state] = art._to_local(pose["hurtbox"], hip_x, ground_eff)
		if pose["hitbox"] != null:
			art.hitboxes[state] = art._to_local(pose["hitbox"], hip_x, ground_eff)
		var generated := "res://art/%s/%s.png" % [id, state]
		var placeholder := "res://art/placeholder/%s/%s.png" % [id, state]
		if ResourceLoader.exists(generated):
			art.textures[state] = load(generated)
			art.sources[state] = "generated"
		else:
			art.textures[state] = load(placeholder)
			art.sources[state] = "placeholder"
	return art


func _to_local(box: Array, hip_x: float, ground_eff: float) -> Rect2:
	var p0 := Vector2((box[0] - hip_x) * scale, (box[1] - ground_eff) * scale)
	var p1 := Vector2((box[2] - hip_x) * scale, (box[3] - ground_eff) * scale)
	return Rect2(p0, p1 - p0)


func resolve(state: String) -> String:
	var s := state
	while not textures.has(s) and FALLBACK.has(s):
		s = FALLBACK[s]
	return s


## Sprite offset (centered = false) that puts the pose's hip at x = 0 and its ground line at y = 0.
func offset_for(state: String, facing: int) -> Vector2:
	var s := resolve(state)
	var tex: Texture2D = textures[s]
	var a: Vector2 = anchor[s]
	var x := -a.x * scale
	if facing < 0:
		x = -(tex.get_width() - a.x * scale)
	return Vector2(x, -a.y * scale)


static func mirror(r: Rect2, facing: int) -> Rect2:
	if facing >= 0:
		return r
	return Rect2(Vector2(-r.end.x, r.position.y), r.size)
