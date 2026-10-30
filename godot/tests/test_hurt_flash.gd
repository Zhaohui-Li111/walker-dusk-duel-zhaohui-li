extends SceneTree
## A5 step 2: headless checks of the hurt flash against CHANGE-BRIEF.md (Assignment 5, observable
## rules 1-6; rules 3, 4 and 5 as revised in revision 7). Run from the repo root, through the wrapper:
##   scripts/run-test.sh test_hurt_flash.gd 30      (and 60, 144)
## Unlike test_runner.gd, main's _physics_process stays on: the fight runs in the real loop at the
## wrapper's --fixed-fps, and P1 is driven by key events read by its PlayerController. The only
## writes to fight state are the SETUP steps revision 7 allows (lower P2's health; a second hit
## through the game's own P2.receive_hit() + P2.flush_ko() while P2 is in hurt); each is printed
## as SETUP. The second hit runs inside a physics tick, from SetupHit, as check_hit() would.
## Two recorder nodes only read:
##   Sampler  _process,         process_priority 1000: once per frame, after every other _process
##   TickLog  _physics_process, process_physics_priority 1000: once per tick, after main (0) and
##            the driver (100)
## SetupHit _physics_process, process_physics_priority 50: runs a queued SETUP call once, after main
##            has stepped the fighters and before the driver reads them
## Durations: game seconds = physics ticks / 60, real seconds = frames / fps. Under --fixed-fps
## every frame advances a fixed delta, so wall-clock time is used only by the watchdog.

const SHADER_PATH := "res://shaders/hurt_flash.gdshader"
const TICKS_PER_SECOND := 60.0       # physics/common/physics_ticks_per_second
const FADE_TICKS := 22               # HITSTOP_FRAMES 4 + HITSTUN 18 (rule 2)
const HOLD_TICKS := 3                # how long each key is held down
const WALL_LIMIT_MS := 100000        # watchdog, under the wrapper's 120 s

var checks := 0
var failures := 0
var fps := 0
var main: Node
var sampler: Sampler
var ticklog: TickLog
var setup_hit: SetupHit
var results := []                    # P1's attack_resolved: {tick, kind, result}
var p1_max := 0.0                    # rule 6, over every scenario
var p1_frames := 0
var p1_ticks := 0
var p2_flash_frames := 0
var finished := false


## Reads hurt_amount on every rendered frame, after every other _process of that frame.
class Sampler extends Node:
	var main: Node
	var ticklog: TickLog
	var recording := false
	var frames := []                 # [process frame, last physics tick, P1 value, P2 value]
	var last_delta := 0.0
	var started_ms := 0
	var on_watchdog: Callable

	static func amount(f: Fighter) -> float:
		var v: Variant = (f.sprite.material as ShaderMaterial).get_shader_parameter("hurt_amount")
		return -1.0 if v == null else float(v)

	func _ready() -> void:
		process_priority = 1000
		started_ms = Time.get_ticks_msec()

	func _process(delta: float) -> void:
		last_delta = delta
		if Time.get_ticks_msec() - started_ms > WALL_LIMIT_MS:
			on_watchdog.call()
		if recording and is_instance_valid(main):
			frames.append([Engine.get_process_frames(), ticklog.last_tick,
					amount(main.p1), amount(main.p2)])


## Reads the state and hurt_amount on every physics tick, after main and the driver.
class TickLog extends Node:
	var main: Node
	var recording := false
	var ticks := {}                  # physics tick -> record
	var order := []
	var last_tick := -1

	func _ready() -> void:
		process_physics_priority = 1000

	func _physics_process(_delta: float) -> void:
		if not (recording and is_instance_valid(main)):
			return
		last_tick = Engine.get_physics_frames()
		ticks[last_tick] = {"state": main.p2.state, "stun": main.p2.stun,
				"p2": Sampler.amount(main.p2), "p1": Sampler.amount(main.p1),
				"p1_state": main.p1.state, "paused": main.paused}
		order.append(last_tick)


## Runs one queued SETUP call inside a physics tick, between main (0) and the driver (100), the
## same place in the tick where check_hit() calls receive_hit().
class SetupHit extends Node:
	var pending: Callable
	var done_tick := -1

	func _ready() -> void:
		process_physics_priority = 50

	func _physics_process(_delta: float) -> void:
		if pending.is_valid():
			var fn := pending
			pending = Callable()
			done_tick = Engine.get_physics_frames()
			fn.call()


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	sampler = Sampler.new()
	ticklog = TickLog.new()
	sampler.ticklog = ticklog
	sampler.on_watchdog = _watchdog
	setup_hit = SetupHit.new()
	root.add_child(sampler)
	root.add_child(ticklog)
	root.add_child(setup_hit)
	# Godot consumes --fixed-fps, so fps comes from the frame delta once it has settled (the first
	# frames' delta is not 1/fps); the ticks-per-frame check in the first scenario confirms it.
	for i in 10:
		await process_frame
	fps = roundi(1.0 / sampler.last_delta)
	print("hurt flash test: Godot %s, %d fps, frame delta now %.6f s, %d physics ticks/s, time_scale %.2f" % [
		Engine.get_version_info().string, fps, sampler.last_delta,
		ProjectSettings.get_setting("physics/common/physics_ticks_per_second"), Engine.time_scale])
	check(fps > 0, "harness", "fps from the settled frame delta (%d)" % fps)
	if fps <= 0:
		finish()
		return
	print("frame numbers are Engine.get_process_frames(); headless uses the dummy renderer, so nothing is drawn")
	check(InputMap.has_action("p1_punch") and InputMap.has_action("p1_right") and InputMap.has_action("pause")
			and InputMap.has_action("confirm"), "harness", "input actions registered by the Controls autoload")
	await scenario_single_hit()
	await scenario_pause()
	await scenario_time_scale()
	await scenario_retrigger()
	await scenario_ko()
	await scenario_ko_mid_fade()
	print("\n== rule 6 over all scenarios ==")
	check(p1_frames > 0 and p1_max == 0.0 and p2_flash_frames > 0, "6",
			"P1's hurt_amount was 0.0 on all %d frames and %d ticks recorded, while P2 flashed on %d frames (max P1 %.4f)" % [
			p1_frames, p1_ticks, p2_flash_frames, p1_max])
	finish()


# --- scenarios ---------------------------------------------------------------

func scenario_single_hit() -> void:
	if not await start_fight("rules 1, 2, 6 and the shader: one punch on a standing Aotake (input only)"):
		await end_fight()
		return
	check_uniforms()
	if not await walk_into_punch_range():
		await end_fight()
		return
	await tap(KEY_J, "J (punch)")
	await wait_until(func(): return main.p2.state == "hurt", 30)
	await wait_until(func(): return main.p2.state != "hurt", 120)
	await wait_ticks(5)
	var t := hit_tick(0)
	check(t >= 0, "harness", "P1's punch from the J key hit P2 (%s)" % [results])
	if t < 0:
		await end_fight()
		return
	print_trace(t)
	check(tk(t - 1).get("state") != "hurt" and val(t - 1) == 0.0, "1",
			"0.0 on the tick before the hit (tick T-1: P2 '%s', %.4f)" % [tk(t - 1).get("state"), val(t - 1)])
	check(tk(t).get("state") == "hurt" and val(t) == 1.0, "1",
			"1.0 on the tick P2 enters hurt (tick T = %d: '%s', %.4f)" % [t, tk(t).get("state"), val(t)])
	var te := hurt_end_after(t)
	check(te >= 0 and val(te) == 0.0, "1",
			"0.0 on the tick P2 leaves hurt (tick T+%d: '%s', %.4f)" % [te - t, tk(te).get("state"), val(te)])
	var bad := ""
	for i in FADE_TICKS:
		var want := 1.0 if i <= 4 else float(FADE_TICKS - i) / 18.0
		if absf(val(t + i) - want) > 1e-6 and bad == "":
			bad = ": tick T+%d is %.4f, want %.4f" % [i, val(t + i), want]
	check(bad == "", "2", "1.0 on ticks T..T+4 (hitstop), then down 1/18 per tick to 1/18 at T+21 (ticks)%s" % bad)
	check_durations(t, te, 1.0)
	var mismatch := 0
	for s in sampler.frames:
		if ticklog.ticks.has(s[1]) and s[3] != val(s[1]):
			mismatch += 1
	check(mismatch == 0, "sampling",
			"each of %d frame samples equals the value set on that frame's last physics tick (%d differ)" % [
			sampler.frames.size(), mismatch])
	var per_frame := ticklog.order.size() / float(sampler.frames.size())
	check(absf(per_frame - TICKS_PER_SECOND / fps) < 0.1, "harness",
			"the loop ran %d ticks in %d frames = %.3f ticks per frame, want 60 / %d = %.3f" % [
			ticklog.order.size(), sampler.frames.size(), per_frame, fps, TICKS_PER_SECOND / fps])
	await end_fight()


func scenario_pause() -> void:
	if not await start_fight("rule 4, pause: P pressed mid-fade, then P again (input only)"):
		await end_fight()
		return
	if not await walk_into_punch_range():
		await end_fight()
		return
	await tap(KEY_J, "J (punch)")
	await wait_until(func(): return main.p2.state == "hurt" and main.p2.stun <= 10, 60)
	await tap(KEY_P, "P (pause)")
	await wait_ticks(40)
	await tap(KEY_P, "P (resume)")
	await wait_until(func(): return main.p2.state != "hurt", 120)
	await wait_ticks(5)
	var t := hit_tick(0)
	check(t >= 0, "harness", "P1's punch from the J key hit P2 (%s)" % [results])
	if t < 0:
		await end_fight()
		return
	var paused: Array = ticklog.order.filter(func(x): return ticklog.ticks[x]["paused"])
	check(paused.size() >= 20, "4", "the P key paused the fight through main's input handler (%d paused ticks)" % paused.size())
	if paused.is_empty():
		await end_fight()
		return
	var first_p: int = paused[0]
	var last_p: int = paused[-1]
	var frozen := val(first_p - 1)
	var stun_frozen: int = tk(first_p - 1).get("stun", -1)
	var same: bool = paused.all(func(x): return val(x) == frozen and tk(x)["stun"] == stun_frozen and tk(x)["state"] == "hurt")
	var frame_vals: Array = sampler.frames.filter(func(s): return s[1] >= first_p and s[1] <= last_p).map(func(s): return s[3])
	same = same and frame_vals.all(func(v): return v == frozen)
	check(same and frozen > 0.0 and frozen < 1.0, "4",
			"hurt_amount frozen at %.4f (stun %d) on all %d paused ticks and %d frames" % [
			frozen, stun_frozen, paused.size(), frame_vals.size()])
	var after := last_p + 1
	check(not tk(after).get("paused", true) and absf(val(after) - (frozen - 1.0 / 18.0)) < 1e-6, "4",
			"after the second P it resumes from there: %.4f -> %.4f on the first running tick, want %.4f" % [
			frozen, val(after), frozen - 1.0 / 18.0])
	var te := hurt_end_after(t)
	var running := 0
	for x in range(t, te):
		if not tk(x).get("paused", true):
			running += 1
	check(te >= 0 and running == FADE_TICKS and val(te) == 0.0, "4",
			"%d running ticks of flash, paused ticks not counted (want 22), 0.0 at the end (ticks)" % running)
	await end_fight()


func scenario_time_scale() -> void:
	if not await start_fight("rule 4, time scale: one punch under Engine.time_scale = 0.5 (input only)"):
		await end_fight()
		return
	if not await walk_into_punch_range():
		await end_fight()
		return
	Engine.time_scale = 0.5
	print("    CONDITION (engine setting under test, no fight state): Engine.time_scale = 0.5")
	await tap(KEY_J, "J (punch)")
	await wait_until(func(): return main.p2.state == "hurt", 30)
	await wait_until(func(): return main.p2.state != "hurt", 120)
	await wait_ticks(5)
	Engine.time_scale = 1.0
	var t := hit_tick(0)
	check(t >= 0, "harness", "P1's punch from the J key hit P2 (%s)" % [results])
	if t < 0:
		await end_fight()
		return
	check_durations(t, hurt_end_after(t), 0.5)
	await end_fight()


func scenario_retrigger() -> void:
	if not await start_fight("rule 3 (revision 7): punch 1 by input, second hit by SETUP through P2.receive_hit()"):
		await end_fight()
		return
	if not await walk_into_punch_range():
		await end_fight()
		return
	await tap(KEY_J, "J (punch 1)")
	var t1 := await second_hit_in_hurt(false)
	if t1 < 0:
		await end_fight()
		return
	var t2 := setup_hit.done_tick
	await wait_until(func(): return main.p2.state != "hurt", 60)
	await wait_ticks(5)
	print("    tick trace (T2 = %d, the SETUP hit tick; punch 1 hit at T2-%d):" % [t2, t2 - t1])
	for i in range(-1, 18 + 2):
		var r := tk(t2 + i)
		if not r.is_empty():
			print("      T2%+3d  P2 %-5s stun %2d  hurt_amount %.4f" % [i, r["state"], r["stun"], r["p2"]])
	var in_hurt: bool = tk(t2 - 1).get("state") == "hurt"
	check(in_hurt, "3", "the SETUP hit lands while P2 is still in hurt from punch 1 (P2 '%s' on tick T2-1, T1+%d)" % [
		tk(t2 - 1).get("state"), t2 - 1 - t1])
	check(in_hurt and val(t2 - 1) < 1.0 and val(t2) == 1.0 and tk(t2).get("stun") == Fighter.HITSTUN, "3",
			"hurt_amount jumps back to 1.0 on the SETUP hit tick (%.4f -> %.4f, stun %s)" % [
			val(t2 - 1), val(t2), tk(t2).get("stun")])
	var te2 := hurt_end_after(t2)
	var bad := ""
	for x in range(t2 + 1, te2 if te2 >= 0 else t2 + 1):
		var want := float(tk(x).get("stun", -1)) / float(Fighter.HITSTUN)
		if absf(val(x) - want) > 1e-6 and bad == "":
			bad = ": tick T2+%d is %.4f, stun %s / 18 = %.4f" % [x - t2, val(x), tk(x).get("stun"), want]
	check(te2 > t2 + 1 and bad == "", "3",
			"on every following tick in hurt (T2+1..T2+%d) hurt_amount equals stun / HITSTUN%s" % [te2 - t2 - 1, bad])
	print("    WHY no 4-tick hold: hitstop is set only when the attacker emits attack_resolved (main.gd:137-138);"
			+ " receive_hit() alone does not emit it, so stun counts down from the next tick")
	check(in_hurt and te2 - t2 == Fighter.HITSTUN and val(te2) == 0.0, "3",
			"0.0 at 18 ticks after the SETUP hit, no hitstop hold: P2 leaves hurt at T2+%d with %.4f (ticks)" % [
			te2 - t2, val(te2)])
	await end_fight()


## Rule 5 mid-fade (revision 7): punch 1 by input, then health lowered and the K.O. hit by SETUP.
func scenario_ko_mid_fade() -> void:
	if not await start_fight("rule 5 (revision 7): a K.O. hit mid-fade, by SETUP through P2.receive_hit()"):
		await end_fight()
		return
	if not await walk_into_punch_range():
		await end_fight()
		return
	await tap(KEY_J, "J (punch 1)")
	var t1 := await second_hit_in_hurt(true)
	if t1 < 0:
		await end_fight()
		return
	var t := setup_hit.done_tick
	await wait_until(func(): return main.phase == "ko", 30)
	await wait_ticks(30)
	print("    P2 on ticks T-1..T+2: %s" % [range(-1, 3).map(func(i): return "'%s' %.4f" % [tk(t + i).get("state"), val(t + i)])])
	check(tk(t - 1).get("state") == "hurt" and val(t - 1) > 0.0, "5",
			"on the tick before, P2 was mid-fade in hurt ('%s', %.4f)" % [tk(t - 1).get("state"), val(t - 1)])
	check(tk(t).get("state") == "ko" and val(t) == 0.0, "5",
			"on the K.O. tick P2 is in 'ko' and hurt_amount is 0.0 ('%s', %.4f)" % [tk(t).get("state"), val(t)])
	var later: Array = ticklog.order.filter(func(x): return x >= t)
	var max_tick := 0.0
	for x in later:
		max_tick = maxf(max_tick, absf(val(x)))
	var max_frame := 0.0
	var later_frames := 0
	for s in sampler.frames:
		if s[1] >= t:
			later_frames += 1
			max_frame = maxf(max_frame, absf(s[3]))
	check(later.size() >= 30 and max_tick == 0.0 and later_frames > 0 and max_frame == 0.0, "5",
			"no tail: hurt_amount 0.0 on all %d ticks and %d frames from the K.O. tick on (max %.4f, %.4f)" % [
			later.size(), later_frames, max_tick, max_frame])
	await end_fight()


func scenario_ko() -> void:
	if not await start_fight("rule 5: a K.O. hit, health lowered by SETUP"):
		await end_fight()
		return
	if not await walk_into_punch_range():
		await end_fight()
		return
	main.p2.health = 5
	print("    SETUP (not input): P2.health %d -> 5, so one punch (8 damage) is a K.O." % Fighter.MAX_HEALTH)
	await tap(KEY_J, "J (punch)")
	await wait_until(func(): return main.phase == "ko", 30)
	await wait_ticks(5)
	var t := hit_tick(0)
	check(t >= 0, "harness", "the punch from the J key hit P2 (%s)" % [results])
	if t < 0:
		await end_fight()
		return
	check(tk(t).get("state") == "ko" and val(t) == 0.0, "5",
			"on the K.O. tick P2 is in 'ko' and hurt_amount is 0.0 ('%s', %.4f)" % [tk(t).get("state"), val(t)])
	var hurt_ticks: Array = ticklog.order.filter(func(x): return ticklog.ticks[x]["state"] == "hurt")
	var max_tick := 0.0
	for x in ticklog.order:
		max_tick = maxf(max_tick, absf(val(x)))
	var max_frame := 0.0
	for s in sampler.frames:
		max_frame = maxf(max_frame, absf(s[3]))
	check(hurt_ticks.is_empty() and max_tick == 0.0 and max_frame == 0.0, "5",
			"no flash at all: P2 never in hurt, hurt_amount 0.0 on all %d ticks and %d frames (no tail)" % [
			ticklog.order.size(), sampler.frames.size()])
	await end_fight()


# --- checks ------------------------------------------------------------------

## Names and types from get_shader_uniform_list() on each fighter's own material; defaults from
## the shader source text. Nothing is set and read back.
func check_uniforms() -> void:
	var src := FileAccess.get_file_as_string(SHADER_PATH)
	check(src != "", "defaults", "read the shader source text from %s (%d bytes)" % [SHADER_PATH, src.length()])
	var mats := []
	for f: Fighter in [main.p1, main.p2]:
		var mat := f.sprite.material as ShaderMaterial
		var ok := mat != null and mat.shader != null and mat.shader.resource_path == SHADER_PATH
		check(ok, "wiring", "%s's Sprite2D has a ShaderMaterial of %s" % [f.display_name, SHADER_PATH])
		if not ok:
			continue
		mats.append(mat)
		var list := mat.shader.get_shader_uniform_list()
		print("    %s uniform list: %s" % [f.display_name, list.map(func(u): return "%s: %s, hint %d '%s'" % [
			u["name"], type_string(u["type"]), u["hint"], u["hint_string"]])])
		check(not list.is_empty(), "parse", "%s: get_shader_uniform_list() is not empty (%d), so the shader parsed" % [
			f.display_name, list.size()])
		var types := {}
		var range_ok := false
		for u in list:
			types[u["name"]] = u["type"]
			if u["name"] == "hurt_amount":
				var parts: PackedStringArray = String(u["hint_string"]).split(",")
				range_ok = u["hint"] == PROPERTY_HINT_RANGE and parts.size() >= 2 \
						and parts[0].to_float() == 0.0 and parts[1].to_float() == 1.0
		check(types.size() == 2 and types.get("hurt_amount", -1) == TYPE_FLOAT and types.get("flash_color", -1) == TYPE_COLOR,
				"names/types", "%s: exactly hurt_amount (float) and flash_color (vec4 source_color, listed as Color): %s" % [
				f.display_name, types.keys().map(func(k): return "%s=%s" % [k, type_string(types[k])])])
		check(range_ok, "names/types", "%s: hurt_amount is listed with a 0..1 range hint" % f.display_name)
		check(mat.shader.code == src, "wiring", "%s: the material's shader code is the text of the file" % f.display_name)
	if mats.size() == 2:
		check(mats[0] != mats[1] and mats[0].shader == mats[1].shader, "6",
				"P1 and P2 have different ShaderMaterial instances (ids %d, %d) of one shader" % [
				mats[0].get_instance_id(), mats[1].get_instance_id()])
	check(_found(src, "uniform\\s+float\\s+hurt_amount\\s*:\\s*hint_range\\(\\s*0\\.0\\s*,\\s*1\\.0\\s*\\)\\s*=\\s*0\\.0\\s*;"),
			"defaults", "source text: uniform float hurt_amount : hint_range(0.0, 1.0) = 0.0")
	check(_found(src, "uniform\\s+vec4\\s+flash_color\\s*:\\s*source_color\\s*=\\s*vec4\\(\\s*1\\.0\\s*,\\s*0\\.0\\s*,\\s*0\\.0\\s*,\\s*1\\.0\\s*\\)\\s*;"),
			"defaults", "source text: uniform vec4 flash_color : source_color = vec4(1.0, 0.0, 0.0, 1.0)")
	check(_found(src, "COLOR\\.rgb\\s*=\\s*mix\\(\\s*COLOR\\.rgb\\s*,\\s*flash_color\\.rgb\\s*,\\s*hurt_amount\\s*\\)\\s*;")
			and not _found(src, "COLOR\\.a\\s*=|COLOR\\s*=[^=]") and not _found(src, "render_mode"),
			"brief", "source text: the colour line as written, nothing assigns COLOR or COLOR.a, no render_mode")


## Rule 2 (time_scale 1) or rule 4 (time_scale 0.5): game time from ticks, real time from frames.
func check_durations(t: int, te: int, time_scale: float) -> void:
	var rule := "2" if time_scale == 1.0 else "4"
	check(te >= 0 and te - t == FADE_TICKS, rule,
			"game time: %d ticks / 60 = %.3f s, want 22 ticks = 0.367 s (ticks, exact)" % [te - t, (te - t) / TICKS_PER_SECOND])
	var on := -1
	var off := -1
	for s in sampler.frames:
		if on < 0 and s[3] > 0.0:
			on = s[0]
		elif on >= 0 and s[3] == 0.0:
			off = s[0]
			break
	# Revision 7: the fight steps by physics ticks with frame data that ignores delta, and under
	# --fixed-fps Engine.time_scale does not change the ticks per frame, so the flash lasts 22 ticks
	# = 0.367 s of real time at any time_scale.
	var want := FADE_TICKS / TICKS_PER_SECOND
	if time_scale != 1.0:
		print("    expected real time 0.367 s, not 0.367 / %.1f (revision 7): the fight steps by ticks, and time_scale does not change the tick count" % time_scale)
	var real := (off - on) / float(fps)
	check(on >= 0 and off > on and absf(real - want) <= 1.0 / fps + 1e-9, rule,
			"real time at time_scale %.1f: frames %d..%d = %d frames / %d fps = %.4f s, want %.3f ± %.4f s (frames)" % [
			time_scale, on, off, off - on, fps, real, want, 1.0 / fps])


# --- helpers -----------------------------------------------------------------

func start_fight(title: String) -> bool:
	print("\n== %s ==" % title)
	main = load("res://game/main.tscn").instantiate()
	main.round_started.connect(func(_n): main.p2.controller = null)
	root.add_child(main)
	sampler.main = main
	ticklog.main = main
	results.clear()
	sampler.frames.clear()
	ticklog.ticks.clear()
	ticklog.order.clear()
	main.p1.attack_resolved.connect(func(_f, kind, result, _p):
		results.append({"tick": Engine.get_physics_frames(), "kind": kind, "result": result}))
	await process_frame
	check(main.is_physics_processing() and main.p1.controller is PlayerController, "harness",
			"main's _physics_process is on and P1 is driven by its PlayerController")
	await tap(KEY_ENTER, "Enter (title)")
	var ok := await wait_until(func(): return main.phase == "fight", 120)
	check(ok, "harness", "Enter on the title started round 1; the intro ran into the fight (phase %s)" % main.phase)
	print("    HARNESS (writes no fight state): P2's controller set to null when the round starts, so Aotake stands still")
	sampler.recording = true
	ticklog.recording = true
	return ok


func end_fight() -> void:
	sampler.recording = false
	ticklog.recording = false
	setup_hit.pending = Callable()
	for k in [KEY_D, KEY_J, KEY_P, KEY_ENTER]:
		send_key(k, false)
	Engine.time_scale = 1.0
	for s in sampler.frames:
		p1_max = maxf(p1_max, absf(s[2]))
		p1_frames += 1
		if s[3] > 0.0:
			p2_flash_frames += 1
	for x in ticklog.order:
		p1_max = maxf(p1_max, absf(float(ticklog.ticks[x]["p1"])))
		p1_ticks += 1
	if is_instance_valid(main):
		main.queue_free()
	await process_frame
	await process_frame


func walk_into_punch_range() -> bool:
	var gap := punch_gap()
	send_key(KEY_D, true)
	print("    INPUT: D (walk right) held from after tick %d" % ticklog.last_tick)
	var ok: bool = await wait_until(func(): return main.p2.position.x - main.p1.position.x <= gap, 300)
	send_key(KEY_D, false)
	var idle: bool = await wait_until(func(): return main.p1.state == "idle", 30)
	check(ok and idle, "harness", "P1 walked to punch range with the D key (gap %.1f px, target <= %.1f) and stopped" % [
		main.p2.position.x - main.p1.position.x, gap])
	return ok and idle


## After punch 1 (input) hit P2: waits until P2 is mid-fade in hurt (hitstop over), then queues the
## revision 7 SETUP: P2.receive_hit(P1, punch damage) and P2.flush_ko(), as check_hit() calls them.
## With lower_health, P2.health is first set to the punch damage so that hit is a K.O.
## Returns punch 1's hit tick, or -1; the SETUP tick is setup_hit.done_tick.
func second_hit_in_hurt(lower_health: bool) -> int:
	await wait_until(func(): return results.size() >= 1, 30)
	var t1 := hit_tick(0)
	check(t1 >= 0, "harness", "punch 1 from the J key hit P2 (%s)" % [results])
	if t1 < 0:
		return -1
	var mid: bool = await wait_until(func(): return main.p2.state == "hurt" and main.p2.stun <= 10, 30)
	check(mid, "harness", "P2 is mid-fade in hurt from punch 1 (stun %d, hurt_amount %.4f)" % [
		main.p2.stun, Sampler.amount(main.p2)])
	if not mid:
		return -1
	var damage: int = Fighter.ATTACKS["punch"]["damage"]
	if lower_health:
		var h0: int = main.p2.health
		main.p2.health = damage
		print("    SETUP (not input): P2.health %d -> %d, so the next %d-damage hit is a K.O." % [h0, damage, damage])
	setup_hit.done_tick = -1
	setup_hit.pending = func():
		print("    SETUP (not input): on tick T1+%d, P2 '%s' stun %d: P2.receive_hit(P1, %d) then P2.flush_ko(), as check_hit() does" % [
			Engine.get_physics_frames() - t1, main.p2.state, main.p2.stun, damage])
		main.p2.receive_hit(main.p1, damage)
		main.p2.flush_ko()
	var ran: bool = await wait_until(func(): return setup_hit.done_tick >= 0, 10)
	check(ran, "harness", "the SETUP hit ran inside a physics tick (tick %d)" % setup_hit.done_tick)
	return t1 if ran else -1


## Origin distance at which P1's punch box overlaps P2's hurtbox, with 8 px to spare.
func punch_gap() -> float:
	return main.p1.reach("punch") + main.p2.body_half_width() - 8.0


func send_key(code: Key, pressed: bool) -> void:
	var ev := InputEventKey.new()
	ev.keycode = code
	ev.physical_keycode = code
	ev.pressed = pressed
	Input.parse_input_event(ev)


func tap(code: Key, label: String) -> void:
	send_key(code, true)
	print("    INPUT: %s pressed after tick %d" % [label, ticklog.last_tick])
	await wait_ticks(HOLD_TICKS)
	send_key(code, false)
	await process_frame


func wait_until(cond: Callable, max_ticks: int) -> bool:
	var limit := Engine.get_physics_frames() + max_ticks
	while not cond.call():
		if Engine.get_physics_frames() > limit:
			return false
		await process_frame
	return true


func wait_ticks(n: int) -> void:
	var limit := Engine.get_physics_frames() + n
	while Engine.get_physics_frames() < limit:
		await process_frame


func hit_tick(index: int) -> int:
	var hits := results.filter(func(r): return r["result"] == "hit")
	return hits[index]["tick"] if hits.size() > index else -1


func tk(t: int) -> Dictionary:
	return ticklog.ticks.get(t, {})


func val(t: int) -> float:
	return float(tk(t).get("p2", -1.0))


func hurt_end_after(t0: int) -> int:
	var t := t0
	while ticklog.ticks.has(t) and ticklog.ticks[t]["state"] == "hurt":
		t += 1
	return t if ticklog.ticks.has(t) else -1


func print_trace(t: int) -> void:
	print("    tick trace (T = %d, the hit tick):" % t)
	for i in range(-1, FADE_TICKS + 2):
		var r := tk(t + i)
		if not r.is_empty():
			print("      T%+3d  P2 %-5s stun %2d  hurt_amount %.4f   P1 %-5s %.4f" % [
				i, r["state"], r["stun"], r["p2"], r["p1_state"], r["p1"]])


func _found(src: String, pattern: String) -> bool:
	return RegEx.create_from_string(pattern).search(src) != null


func check(cond: bool, rule: String, msg: String) -> void:
	checks += 1
	if not cond:
		failures += 1
	print("%s [%s] %s" % ["PASS" if cond else "FAIL", rule, msg])


func _watchdog() -> void:
	if finished:
		return
	check(false, "harness", "watchdog: not finished after %d s of wall-clock time" % (WALL_LIMIT_MS / 1000))
	finish()


func finish() -> void:
	if finished:
		return
	finished = true
	Engine.time_scale = 1.0
	print("%d checks, %d failed" % [checks, failures])
	quit(1 if failures else 0)
