extends SceneTree
## A6 step 7: per-frame CPU cost of the two particle effects (CHANGE-BRIEF.md, "Price predictions
## and budget"). Run from the repo root, through the wrapper:
##   scripts/run-test.sh cost_effects.gd 60 300
## Source: the course chapter's Example 09 cost script is not in this repository or on this machine,
## so this script was written from the step's description, not adapted from Example 09's code
## (Claude Code, under Zhaohui's delegation, 2026-11-08).
##
## Cases, each in a fresh scene, with WARMUP frames before MEASURE measured frames:
##   E  empty      an empty Node2D: what the engine loop and this script's own sampler cost
##   G  game       main.tscn on its title screen; Effect A's four slots and Effect B not emitting
##   A  sparks     G + all four HitSpark slots alive at once (4 x 20 = 80 particles, the brief's peak)
##   B  embers     G + Embers emitting with the field full (48 particles, preprocess + > 2.5 s)
## The cases run twice, in the order E G A B, then B A G E, so a drift over the run shows up as a
## difference between the two passes instead of a difference between cases.
## The game stays on its title screen (phase "title") in G, A and B, so no fighter acts, no hit
## lands and no hitstop starts: the game's own work is the same in the three cases and A - G and
## B - G are the effects' cost. A running fight is not measured.
## Writes to game or engine state, each printed:
##   SETUP  A: each HitSpark slot is given a position in the hit band and restart()ed, staggered
##          every RETRIGGER frames (< the 36-tick lifetime), so all four bursts are alive on every
##          measured frame. Done here, not through a hit, because a hit would also start hitstop.
##   SETUP  B: Embers.restart() (as embers_controller.gd does on entering the fight), so it emits;
##          the controller leaves emitting alone outside a phase change, and the phase stays "title".
##
## What is measured, per rendered frame, in microseconds. CPUParticles2D simulates in its internal
## process notification, so the measure has to be the engine's frame time, not this script's code:
##   wall     Time.get_ticks_usec() between two successive frames: the whole frame (process,
##            internal process, the 60 Hz physics tick, the dummy renderer, this script)
##   harness  the part of it spent in this script's own per-frame code (the state check and A's
##            retrigger bookkeeping; the restart() calls themselves count as the effect's cost)
##   engine   wall - harness: the number the cases are compared on
## Not used: Performance.TIME_PROCESS and TIME_PHYSICS_PROCESS. The first run of this script
## (2026-11-08) read them every frame and got 0 in every case of pass 1 and one constant
## (107 536 / 406 µs) in every case of pass 2: in 4.7.2 they are refreshed about once per second
## of real time, not per frame, and at --fixed-fps the whole run takes well under 2 s of real
## time. They could not tell the cases apart, so the script would have been measuring itself.
## --fixed-fps 60 is checked through delta (1/60 on every measured frame); frames are not
## throttled to real time, so wall time per frame is the CPU work of that frame.
## A headless run uses the dummy renderer: no particle is drawn, so this is CPU time only.

const WARMUP := 240                      # 4 s at 60 fps: covers B's 2.5 s lifetime after restart()
const MEASURE := 1200                    # 20 s at 60 fps per case and pass
const RETRIGGER := 30                    # A: frames between two restarts of one slot (lifetime 36)
const SLOT_POINTS := [Vector2(170, 236), Vector2(200, 244), Vector2(230, 240), Vector2(260, 248)]
const SLOTS := ["HitSpark0", "HitSpark1", "HitSpark2", "HitSpark3"]
const METRICS := ["wall", "harness", "engine"]
const CASES := {"E": "empty scene", "G": "game, both effects off", "A": "Effect A, 4 bursts alive",
		"B": "Effect B, emitting, field full"}
const WALL_LIMIT_MS := 280000            # watchdog, under the wrapper's 300 s

var checks := 0
var failures := 0
var finished_run := false
var sampler: Sampler
var scene: Node
var results := {}                        # case -> pass -> metric -> PackedFloat64Array (µs)


## Records one sample per rendered frame, after every other node's _process. All of this script's
## per-frame code runs earlier in the same frame (on process_frame) and adds itself to harness_us.
class Sampler extends Node:
	var recording := false
	var samples := {}
	var deltas := PackedFloat64Array()
	var harness_us := 0
	var last_usec := 0
	var started_ms := 0
	var on_watchdog: Callable

	func _ready() -> void:
		process_priority = 1000
		started_ms = Time.get_ticks_msec()

	func begin() -> void:
		samples = {}
		for m in METRICS:
			samples[m] = PackedFloat64Array()
		deltas = PackedFloat64Array()
		recording = true

	func _process(delta: float) -> void:
		if Time.get_ticks_msec() - started_ms > WALL_LIMIT_MS:
			on_watchdog.call()
		var now := Time.get_ticks_usec()
		if recording:
			var wall := float(now - last_usec)
			samples["wall"].append(wall)
			samples["harness"].append(float(harness_us))
			samples["engine"].append(wall - harness_us)
			deltas.append(delta)
		harness_us = 0
		last_usec = now


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	sampler = Sampler.new()
	sampler.on_watchdog = _watchdog
	root.add_child(sampler)
	for i in 10:
		await process_frame
	print("cost_effects: Godot %s, %d physics ticks/s; headless dummy renderer, CPU time only" % [
		Engine.get_version_info().string, ProjectSettings.get_setting("physics/common/physics_ticks_per_second")])
	print("Each case: %d warm-up frames, then %d measured frames; two passes (E G A B, then B A G E)" % [
		WARMUP, MEASURE])
	print("Source: Example 09's script is not available here; written from the step's description.")
	for c in CASES:
		results[c] = {}
	var orders := [["E", "G", "A", "B"], ["B", "A", "G", "E"]]
	for p in orders.size():
		print("\n== pass %d ==" % (p + 1))
		for c in orders[p]:
			await run_case(c, p)
	report()
	finish()


# --- cases -------------------------------------------------------------------

func run_case(c: String, pass_i: int) -> void:
	print("-- %s: %s" % [c, CASES[c]])
	if c == "E":
		scene = Node2D.new()
		scene.name = "Empty"
		root.add_child(scene)
	else:
		scene = load("res://game/main.tscn").instantiate()
		root.add_child(scene)
	await process_frame
	var slots: Array[CPUParticles2D] = []
	var embers: CPUParticles2D = null
	if c != "E":
		for n in SLOTS:
			slots.append(scene.get_node(n) as CPUParticles2D)
		embers = scene.get_node("Embers") as CPUParticles2D
	if c == "A":
		print("    SETUP (not a hit): 4 HitSpark slots positioned in the hit band and restart()ed, each every %d frames, staggered" % RETRIGGER)
	if c == "B":
		embers.restart()
		print("    SETUP (not a phase change): Embers.restart(), so it emits with preprocess; phase stays \"%s\"" % scene.phase)

	var bad := []                         # measured frames whose state is not the case's
	var physics_steps := PackedInt32Array()
	var spawns := 0
	var f := 0
	var total_frames := WARMUP + MEASURE + 1
	while f < total_frames:
		var t0 := Time.get_ticks_usec()
		var spawn_us := 0
		if c == "A":
			for k in slots.size():
				if (f + k * (RETRIGGER / 4)) % RETRIGGER == 0:
					var s0 := Time.get_ticks_usec()
					slots[k].position = SLOT_POINTS[k]
					slots[k].restart()
					spawn_us += Time.get_ticks_usec() - s0
					if f > WARMUP:
						spawns += 1
		if f == WARMUP:
			sampler.begin()
		sampler.harness_us += Time.get_ticks_usec() - t0 - spawn_us
		var ph0 := Engine.get_physics_frames()
		await process_frame
		var t2 := Time.get_ticks_usec()
		if f > WARMUP:
			physics_steps.append(Engine.get_physics_frames() - ph0)
			var why := _state_error(c, slots, embers)
			if why != "":
				bad.append("frame %d: %s" % [f - WARMUP, why])
		f += 1
		sampler.harness_us += Time.get_ticks_usec() - t2
	sampler.recording = false

	var data := {}
	for m in METRICS:
		data[m] = sampler.samples[m].slice(1)    # the first sample's interval began in the warm-up
	results[c][pass_i] = data
	check(bad.is_empty(), c, "state held on all %d measured frames%s" % [
		data["engine"].size(), "" if bad.is_empty() else " (first: %s; %d bad)" % [bad[0], bad.size()]])
	check(physics_steps.count(1) == physics_steps.size(), c,
			"exactly one physics tick per measured frame (%d of %d)" % [physics_steps.count(1), physics_steps.size()])
	var fixed := 0
	for d in sampler.deltas:
		if is_equal_approx(d, 1.0 / 60.0):
			fixed += 1
	check(fixed == sampler.deltas.size(), c, "fixed rate: delta == 1/60 s on %d of %d frames" % [
		fixed, sampler.deltas.size()])
	if c == "A":
		print("    SETUP: %d restart() calls in the measured frames (one per slot every %d frames)" % [spawns, RETRIGGER])
	if c != "E":
		var internal := []
		for s in slots:
			internal.append(s.is_processing_internal())
		print("    OBSERVE: is_processing_internal() at the end: HitSpark0-3 %s, Embers %s" % [
			internal, embers.is_processing_internal()])
	for m in METRICS:
		print("    %s" % fmt_stats(m, data[m]))
	scene.queue_free()
	scene = null
	await process_frame
	await process_frame


## "" when the scene is in the case's state on this frame, else what is wrong.
func _state_error(c: String, slots: Array[CPUParticles2D], embers: CPUParticles2D) -> String:
	if c == "E":
		return ""
	if scene.phase != "title" or scene.paused or scene.hitstop != 0:
		return "phase %s, paused %s, hitstop %d" % [scene.phase, scene.paused, scene.hitstop]
	var on := 0
	for s in slots:
		if s.emitting:
			on += 1
		if s.speed_scale != 1.0:
			return "a HitSpark slot has speed_scale %s" % s.speed_scale
	if embers.speed_scale != 1.0:
		return "Embers speed_scale %s" % embers.speed_scale
	var want_on := 4 if c == "A" else 0
	if on != want_on:
		return "%d HitSpark slots emitting, expected %d" % [on, want_on]
	if embers.emitting != (c == "B"):
		return "Embers emitting %s" % embers.emitting
	return ""


# --- report ------------------------------------------------------------------

func report() -> void:
	print("\n== SUMMARY: both passes pooled, microseconds per frame ==")
	print("%-34s %-8s %8s %8s %8s %8s %8s %8s" % ["case", "metric", "mean", "sd", "min", "median", "p95", "max"])
	var pooled := {}
	for c in CASES:
		pooled[c] = {}
		for m in METRICS:
			var a := PackedFloat64Array()
			for p in results[c]:
				a.append_array(results[c][p][m])
			pooled[c][m] = a
			var s := stats(a)
			print("%-34s %-8s %8.1f %8.1f %8.1f %8.1f %8.1f %8.1f" % [
				"%s %s" % [c, CASES[c]] if m == METRICS[0] else "", m,
				s.mean, s.sd, s.min, s.median, s.p95, s.max])

	print("\n== DRIFT: pass 1 vs pass 2 (engine), difference and its 95% interval ==")
	for c in CASES:
		var d := diff(results[c][1]["engine"], results[c][0]["engine"])
		print("    %s: pass 1 %.1f, pass 2 %.1f, difference %+.1f ± %.1f µs%s" % [c,
			stats(results[c][0]["engine"]).mean, stats(results[c][1]["engine"]).mean, d.delta, d.ci,
			"" if absf(d.delta) <= d.ci else "  <- the passes differ by more than the noise"])

	print("\n== DIFFERENCES (pooled): mean difference ± 95% interval (Welch, 1.96 x standard error); medians ==")
	var pairs := [["G", "E", "the game scene should cost more than an empty scene"],
			["A", "G", "Effect A's 80 particles should cost more than the game alone"],
			["B", "G", "Effect B's 48 particles should cost more than the game alone"],
			["A", "B", "A (80 particles) and B (48) are not predicted to cost the same"]]
	for pr in pairs:
		var d := diff(pooled[pr[0]]["engine"], pooled[pr[1]]["engine"])
		var med: float = stats(pooled[pr[0]]["engine"]).median - stats(pooled[pr[1]]["engine"]).median
		var same: bool = absf(d.delta) <= d.ci
		print("    %s - %s  engine  mean %+7.1f ± %4.1f µs, median %+7.1f µs  %s" % [
			pr[0], pr[1], d.delta, d.ci, med, "SAME within noise" if same else "separated"])
		if same:
			print("    WARNING: %s and %s report the same engine time, though %s: the script may be measuring itself, or the difference is below the noise" % [
				pr[0], pr[1], pr[2]])
	for c in CASES:
		var h := stats(pooled[c]["harness"])
		print("    harness share, %s: %.1f µs of %.1f µs wall (%.0f%%)" % [c, h.mean,
			stats(pooled[c]["wall"]).mean, 100.0 * h.mean / maxf(stats(pooled[c]["wall"]).mean, 0.001)])


func stats(a: PackedFloat64Array) -> Dictionary:
	var n := a.size()
	if n == 0:
		return {"n": 0, "mean": 0.0, "sd": 0.0, "min": 0.0, "median": 0.0, "p95": 0.0, "max": 0.0}
	var sum := 0.0
	for v in a:
		sum += v
	var mean := sum / n
	var sq := 0.0
	for v in a:
		sq += (v - mean) * (v - mean)
	var sd := sqrt(sq / maxi(n - 1, 1))
	var s := a.duplicate()
	s.sort()
	return {"n": n, "mean": mean, "sd": sd, "min": s[0], "median": s[n / 2],
			"p95": s[mini(int(n * 0.95), n - 1)], "max": s[n - 1]}


## a - b: difference of means and the half-width of its 95% interval.
func diff(a: PackedFloat64Array, b: PackedFloat64Array) -> Dictionary:
	var sa := stats(a)
	var sb := stats(b)
	var se := sqrt(sa.sd * sa.sd / maxi(sa.n, 1) + sb.sd * sb.sd / maxi(sb.n, 1))
	return {"delta": sa.mean - sb.mean, "ci": 1.96 * se}


func fmt_stats(m: String, a: PackedFloat64Array) -> String:
	var s := stats(a)
	return "%-8s n %d  mean %.1f  sd %.1f  min %.1f  median %.1f  p95 %.1f  max %.1f µs" % [
		m, s.n, s.mean, s.sd, s.min, s.median, s.p95, s.max]


# --- harness -----------------------------------------------------------------

func check(cond: bool, label: String, msg: String) -> void:
	checks += 1
	if not cond:
		failures += 1
	print("    %s [%s] %s" % ["PASS" if cond else "FAIL", label, msg])


func _watchdog() -> void:
	if finished_run:
		return
	check(false, "harness", "watchdog: not finished after %d s of wall-clock time" % (WALL_LIMIT_MS / 1000))
	finish()


func finish() -> void:
	if finished_run:
		return
	finished_run = true
	print("%d checks, %d failed" % [checks, failures])
	quit(1 if failures else 0)
