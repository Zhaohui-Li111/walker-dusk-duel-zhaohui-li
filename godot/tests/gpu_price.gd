extends SceneTree
## A6 GPU price, WINDOWED (needs a real GPU; not for the headless wrapper). Written by Claude Code
## after the editor's Visual Profiler showed 0 for GPU frame time on this machine (Compatibility
## renderer). It reads RenderingServer.viewport_get_measured_render_time_gpu / _cpu for the root
## viewport, the measurement Movie Maker's "GPU render time" line also reports.
##
## Run from the repository root (Zhaohui starts it; a window opens and closes by itself, ~30 s):
##   & $env:GODOT --path godot --script res://tests/gpu_price.gd
##
## Cases, each 90 warm-up frames then 300 measured frames:
##   A on   res://previews/hit_spark_profile.tscn, four hit-spark bursts kept alive
##   A off  same scene, bursts stopped (profile toggle off), last bursts allowed to end
##   B on   res://game/main.tscn in the fight, embers field full. SETUP: main.start_fight_now()
##          and P2's controller set to null so no attack adds hit sparks.
##   B off  the same fight with the Embers node hidden (SETUP), so only the embers' drawing goes.

const WARM := 90
const MEASURE := 300

var vp: RID
var results := []


func _initialize() -> void:
	_run()


func _run() -> void:
	vp = root.get_viewport_rid()
	RenderingServer.viewport_set_measure_render_time(vp, true)
	print("gpu_price: %s, %s / %s, adapter: %s, vsync mode %d" % [Engine.get_version_info().string,
			RenderingServer.get_current_rendering_driver_name(),
			RenderingServer.get_current_rendering_method(),
			RenderingServer.get_video_adapter_name(), DisplayServer.window_get_vsync_mode()])

	var preview: Node = (load("res://previews/hit_spark_profile.tscn") as PackedScene).instantiate()
	root.add_child(preview)
	await _measure("A on   (4 hit-spark bursts alive)")
	preview.set("_profile_on", false)
	for i in 60:
		await process_frame
	await _measure("A off  (bursts stopped)")
	preview.queue_free()
	await process_frame

	var main: Node = (load("res://game/main.tscn") as PackedScene).instantiate()
	root.add_child(main)
	main.start_fight_now()                      # SETUP
	main.p2.controller = null                   # SETUP: no CPU attacks, so no hit sparks
	for i in 120:
		await process_frame
	await _measure("B on   (fight, embers field full)")
	# Same fight, same HUD; only the embers are not drawn. (A first run used the title screen
	# as "off", but the title draws more HUD text than the fight, so "off" cost more than "on".)
	main.get_node("Embers").visible = false     # SETUP: draw off
	await _measure("B off  (same fight, Embers hidden)")

	print("")
	print("gpu_price: SUMMARY, milliseconds per frame (median / mean / p95)")
	for r in results:
		print("  %-44s GPU %6.3f / %6.3f / %6.3f   CPU %6.3f / %6.3f / %6.3f" % r)
	print("gpu_price: A on - A off GPU median %+.3f ms;  B on - B off GPU median %+.3f ms" % [
			results[0][1] - results[1][1], results[2][1] - results[3][1]])
	print("gpu_price: if every GPU value is 0.000, this renderer reports no GPU time here.")
	quit()


func _measure(label: String) -> void:
	for i in WARM:
		await process_frame
	var gpu := []
	var cpu := []
	for i in MEASURE:
		await process_frame
		gpu.append(RenderingServer.viewport_get_measured_render_time_gpu(vp))
		cpu.append(RenderingServer.viewport_get_measured_render_time_cpu(vp))
	var g := _stats(gpu)
	var c := _stats(cpu)
	results.append([label, g[0], g[1], g[2], c[0], c[1], c[2]])
	print("gpu_price: %s  GPU median %.3f ms" % [label, g[0]])


func _stats(v: Array) -> Array:
	var s := v.duplicate()
	s.sort()
	var total := 0.0
	for x in s:
		total += x
	return [s[s.size() / 2], total / s.size(), s[int(s.size() * 0.95)]]
