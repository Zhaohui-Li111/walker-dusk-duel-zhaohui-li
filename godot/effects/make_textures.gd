extends SceneTree
## A6: draws the particle textures once and saves them as PNGs next to this script, so the effect
## scenes reference a file and the texture is a scene setting a test can read back
## (CLAUDE.md, "Textures"). Re-run only to change a texture, then re-import:
##   "$GODOT" --headless --path godot --script res://effects/make_textures.gd
##   "$GODOT" --headless --path godot --import
##
## hit_spark_star.png (Effect A, CHANGE-BRIEF.md settings table "Texture"): 8 x 8 eight-point star,
## wide at the centre with thin tips. White, shape in alpha, so color_ramp sets the colour.

const OUT_DIR := "res://effects/"
const SUPERSAMPLE := 4               # samples per pixel side, for anti-aliased edges


func _initialize() -> void:
	# r_in 1.25 -> 1.0, sharp 3 -> 6 (2026-11-08, Zhaohui chose "sharpen the texture"): the first
	# star's tips did not separate on 8 x 8 (tip/gap alpha 7.72 / 5.46 < 2).
	_save(_star(8, 4.0, 1.0, 6.0), "hit_spark_star.png")
	quit()


func _save(img: Image, file: String) -> void:
	var path := ProjectSettings.globalize_path(OUT_DIR + file)
	var err := img.save_png(path)
	print("make_textures: %s %dx%d -> %s (%s)" % [file, img.get_width(), img.get_height(), path,
			error_string(err)])


## Star outline in polar form: radius r_out on the 8 tips, r_in between them; `sharp` > 1 narrows
## the tips. Alpha is the covered fraction of each pixel, so the centre is solid and the tips thin.
func _star(size: int, r_out: float, r_in: float, sharp: float) -> Image:
	var img := Image.create_empty(size, size, false, Image.FORMAT_RGBA8)
	var c := size / 2.0
	var n := SUPERSAMPLE * SUPERSAMPLE
	for y in size:
		for x in size:
			var hit := 0
			for sy in SUPERSAMPLE:
				for sx in SUPERSAMPLE:
					var p := Vector2(x + (sx + 0.5) / SUPERSAMPLE - c, y + (sy + 0.5) / SUPERSAMPLE - c)
					var edge := r_in + (r_out - r_in) * pow(absf(cos(4.0 * p.angle())), sharp)
					if p.length() <= edge:
						hit += 1
			img.set_pixel(x, y, Color(1, 1, 1, float(hit) / n))
	return img
