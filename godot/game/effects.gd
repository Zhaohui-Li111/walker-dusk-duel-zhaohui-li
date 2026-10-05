extends Node2D
## Visible feedback for attack results, so the slice reads with the sound muted:
## hit = white spark, block = pale blue flash bars, whiff = faint motion streak.
## Stepped by main.gd (not real time) like everything else.

var items := []   # {pos, kind, ttl, dir}


func spawn(kind: String, pos: Vector2, dir: int) -> void:
	items.append({"pos": pos, "kind": kind, "ttl": 10, "dir": dir})
	queue_redraw()


func step() -> void:
	for it in items:
		it["ttl"] -= 1
	items = items.filter(func(it): return it["ttl"] > 0)
	queue_redraw()


func clear() -> void:
	items.clear()
	queue_redraw()


func _draw() -> void:
	for it in items:
		var p: Vector2 = it["pos"]
		var a: float = it["ttl"] / 10.0
		match it["kind"]:
			"hit":
				var r: float = 10.0 + (10 - it["ttl"]) * 1.2
				for i in 8:
					var v := Vector2.from_angle(i * PI / 4.0)
					draw_line(p + v * 3.0, p + v * r, Color(1, 1, 1, a), 2.0)
			"blocked":
				for i in 3:
					var x: float = p.x - it["dir"] * (4.0 + i * 4.0)
					draw_line(Vector2(x, p.y - 12), Vector2(x, p.y + 12), Color(0.75, 0.85, 1.0, a), 2.0)
			"whiff":
				draw_line(p - Vector2(it["dir"] * 14.0, 0), p, Color(1, 1, 1, a * 0.35), 1.0)
