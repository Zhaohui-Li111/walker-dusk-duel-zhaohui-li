extends SceneTree
## Writes the hint experiment's texture: a 3 × 1 RGB8 PNG whose texels are the greys 64, 128, 192.
## Run from the repository root, then reimport:
##   "$GODOT" --headless --path godot --script res://hint_experiment/write_hint_png.gd
## The PNG is imported lossless with no mipmaps (hint_grey_3x1.png.import), so the shader samples
## exactly these bytes.

const PATH := "res://hint_experiment/hint_grey_3x1.png"
const GREYS := [64, 128, 192]


func _initialize() -> void:
	var img := Image.create(GREYS.size(), 1, false, Image.FORMAT_RGB8)
	for i in GREYS.size():
		var g: float = GREYS[i] / 255.0
		img.set_pixel(i, 0, Color(g, g, g))
	var err := img.save_png(ProjectSettings.globalize_path(PATH))
	# Read it back from disk to prove the stored bytes, not the in-memory image.
	var back := Image.load_from_file(ProjectSettings.globalize_path(PATH))
	var bytes := []
	for i in back.get_width():
		bytes.append(back.get_pixel(i, 0).r8)
	print("wrote %s err=%d size=%dx%d format=%d greys=%s" % [PATH, err, back.get_width(),
			back.get_height(), back.get_format(), bytes])
	quit(0 if err == OK and bytes == GREYS else 1)
