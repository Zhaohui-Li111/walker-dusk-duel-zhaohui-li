extends SceneTree
## A7: draws a lantern-flame flicker sprite sheet once and saves it as a PNG next to this script.
## The assignment allows sheets written by code ("commit the code"); this script is that code and
## the PNG it writes is the committed original. Written by Claude Code on 2026-11-22, after
## Zhaohui chose "generate the sheet by code". Re-run only to change the sheet, then re-import:
##   "$GODOT" --headless --path godot --script res://art/sheets/make_lantern_flame_sheet.gd
##   "$GODOT" --headless --path godot --import
##
## lantern_flame.png
##   cell 12 x 16 px, grid 4 x 2 (hframes 4, vframes 2), 8 cells, no padding, no margin.
##   Cell n is at column n % 4, row n / 4, which is Sprite2D.frame n for hframes 4, vframes 2.
##   Drawn 1:1 in viewport pixels (640 x 360), the scale bg.png is drawn at.
##   Registration: every cell's flame base sits on the same pixel, x 6, y 15 of the cell; only
##   the body above it changes, so a node offset is never needed between frames.
##   The 8 cells sample one periodic flicker: cell n is phase 2*pi*n/8. Cell 7 -> cell 0 is the
##   same phase step as any other pair, so cells 0..7 in order wrap with no repeated cell.
##   Which cells a clip uses, in what order and at what rate, is the brief's decision.
##
## An existing PNG is left alone when the new bytes are identical, and is not overwritten when
## they differ unless `-- --overwrite` is passed.

const OUT := "res://art/sheets/lantern_flame.png"
const CELL := Vector2i(12, 16)
const GRID := Vector2i(4, 2)
const FRAMES := 8
const BASE := Vector2(6.0, 15.0)     # flame base in cell pixels, same in every cell
const SUPERSAMPLE := 4

const CORE := Color8(255, 244, 194)  # pale yellow
const MID := Color8(255, 179, 71)    # orange
const OUTER := Color8(232, 100, 42)  # red-orange


func _initialize() -> void:
	var img := Image.create(CELL.x * GRID.x, CELL.y * GRID.y, false, Image.FORMAT_RGBA8)
	img.fill(Color(0, 0, 0, 0))
	for n in FRAMES:
		var origin := Vector2i((n % GRID.x) * CELL.x, (n / GRID.x) * CELL.y)
		_draw_flame(img, origin, TAU * n / FRAMES)
	_save(img)
	quit()


## Flame height and tip sway at phase p. Two harmonics, so the flicker is not a plain sine.
func _shape(p: float) -> Vector2:
	var height := 11.0 + 1.6 * sin(p) + 0.8 * sin(2.0 * p + 1.0)
	var sway := 1.3 * sin(p + 0.9) + 0.5 * sin(3.0 * p)
	return Vector2(height, sway)


func _draw_flame(img: Image, origin: Vector2i, p: float) -> void:
	var s := _shape(p)
	var height := s.x
	var sway := s.y
	for py in CELL.y:
		for px in CELL.x:
			var acc := Color(0, 0, 0, 0)   # premultiplied
			for sy in SUPERSAMPLE:
				for sx in SUPERSAMPLE:
					var x := px + (sx + 0.5) / SUPERSAMPLE
					var y := py + (sy + 0.5) / SUPERSAMPLE
					var c := _sample(x, y, height, sway)
					acc += Color(c.r * c.a, c.g * c.a, c.b * c.a, c.a)
			var n := float(SUPERSAMPLE * SUPERSAMPLE)
			var a := acc.a / n
			if a <= 0.0:
				continue
			img.set_pixel(origin.x + px, origin.y + py,
					Color(acc.r / n / a, acc.g / n / a, acc.b / n / a, a))


## Colour and alpha of the flame at a point in cell pixels; alpha 0 outside.
func _sample(x: float, y: float, height: float, sway: float) -> Color:
	var t := (BASE.y + 0.5 - y) / height          # 0 at the base, 1 at the tip
	if t < 0.0 or t > 1.0:
		return Color(0, 0, 0, 0)
	var centre := BASE.x + sway * t * t
	var half := 3.2 * pow(1.0 - t, 0.8) * minf(1.0, 0.45 + 3.0 * t)
	var d := absf(x - centre) / maxf(half, 0.001)
	if d > 1.0:
		return Color(0, 0, 0, 0)
	var r := maxf(d, t * 0.9)                     # 0 in the core, 1 at the edge and tip
	var col: Color
	if r < 0.4:
		col = CORE.lerp(MID, smoothstep(0.2, 0.4, r))
	else:
		col = MID.lerp(OUTER, smoothstep(0.45, 0.85, r))
	col.a = 1.0 - smoothstep(0.75, 1.0, t)
	return col


func _save(img: Image) -> void:
	var path := ProjectSettings.globalize_path(OUT)
	DirAccess.make_dir_recursive_absolute(path.get_base_dir())
	var bytes := img.save_png_to_buffer()
	var status := "written"
	if FileAccess.file_exists(path):
		if FileAccess.get_file_as_bytes(path) == bytes:
			status = "unchanged, not written"
		elif "--overwrite" in OS.get_cmdline_user_args():
			status = "changed, overwritten"
		else:
			print("%s: differs from the committed file; pass -- --overwrite to replace it" % OUT)
			return
	if status != "unchanged, not written":
		var f := FileAccess.open(path, FileAccess.WRITE)
		f.store_buffer(bytes)
		f.close()
	print("%s: %s (%d x %d, cell %d x %d, grid %d x %d, %d frames)" % [OUT, status,
			img.get_width(), img.get_height(), CELL.x, CELL.y, GRID.x, GRID.y, FRAMES])
