extends Node
## A6 debug key for the GPU price: F9 toggles vsync at run time, so an FPS comparison can run
## uncapped without changing a project setting (A6 handout, "The GPU price"). Presentation only:
## touches no game state. Prints the new mode so the run's console records it.


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_F9:
		var off := DisplayServer.window_get_vsync_mode() == DisplayServer.VSYNC_DISABLED
		DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_ENABLED if off else DisplayServer.VSYNC_DISABLED)
		print("debug_vsync: vsync %s" % ("on" if off else "off"))
