extends Control
## Health bars, names and the centre message (title, round call, K.O., result, pause).

const BAR := Color("f5c542")
const TEXT := Color("f0ece4")

var p1: Fighter
var p2: Fighter
var message := ""
var sub_message := ""
var hint := ""
var audio: Node                 # AudioDirector, for the mute indicator


func _process(_delta: float) -> void:
	queue_redraw()


func _draw() -> void:
	var font := get_theme_default_font()
	if p1 and p2:
		_bar(Rect2(20, 14, 250, 12), p1.health, false)
		_bar(Rect2(370, 14, 250, 12), p2.health, true)
		draw_string(font, Vector2(20, 40), p1.display_name, HORIZONTAL_ALIGNMENT_LEFT, -1, 11, TEXT)
		draw_string(font, Vector2(370, 40), p2.display_name, HORIZONTAL_ALIGNMENT_RIGHT, 250, 11, TEXT)
	if message != "":
		draw_rect(Rect2(0, 120, 640, 64), Color(0, 0, 0, 0.45))
		draw_string(font, Vector2(0, 160), message, HORIZONTAL_ALIGNMENT_CENTER, 640, 30, TEXT)
		if sub_message != "":
			draw_string(font, Vector2(0, 178), sub_message, HORIZONTAL_ALIGNMENT_CENTER, 640, 11, TEXT)
	if audio:
		var off := []
		if audio.is_muted("Music"):
			off.append("music off (M)")
		if audio.is_muted("SFX"):
			off.append("effects off (N)")
		if off:
			draw_string(font, Vector2(0, 40), "  ·  ".join(PackedStringArray(off)), HORIZONTAL_ALIGNMENT_CENTER, 640, 10, Color(TEXT, 0.85))
	if hint != "":
		draw_string(font, Vector2(6, 354), hint, HORIZONTAL_ALIGNMENT_LEFT, 628, 9, Color(TEXT, 0.7))


func _bar(r: Rect2, hp: int, from_right: bool) -> void:
	draw_rect(r, Color(0, 0, 0, 0.5))
	var w := r.size.x * hp / float(Fighter.MAX_HEALTH)
	var fill := Rect2(r.position + Vector2(r.size.x - w, 0), Vector2(w, r.size.y)) if from_right \
			else Rect2(r.position, Vector2(w, r.size.y))
	draw_rect(fill, BAR)
	draw_rect(r, TEXT, false, 1.0)
