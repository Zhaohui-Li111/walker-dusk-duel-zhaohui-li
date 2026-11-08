extends SceneTree
## A6 Effect A (hit spark): headless state test of the trigger code (res://effects/hit_spark_pool.gd)
## against CHANGE-BRIEF.md, Effect A, observable rules 1-6. Run from the repo root, through the wrapper:
##   scripts/run-test.sh test_hit_spark_state.gd 60
## As in test_hurt_flash.gd, main's _physics_process stays on: the fight runs in the real loop and P1
## is driven by key events read by its PlayerController. The pool's trigger is never called.
## Writes to game state, each printed:
##   HARNESS  P2's controller is set to null when a round starts (scenarios A, B, C, E, F), so
##            Aotake stands still; scenario D keeps the game's own CpuController.
##   SETUP    scenario F calls the game's own main.start_fight_now() mid-burst (rule 6, Zhaohui's
##            choice (b)), inside a physics tick.
## What a headless run sees: each emitter's node state (emitting, position, speed_scale, parent) once
## per physics tick and once per frame, and its 'finished' signal. The dummy renderer draws nothing
## and CPUParticles2D has no live particle count, so the particles themselves are not seen.
## A "fire" is a slot whose emitting goes false -> true, or whose position changes while it is
## emitting, from one tick to the next (restart() has no signal of its own). The pool's own arrays
## are read only to report the all-four-busy fallback; no assertion of a fire depends on them.

const SLOT_NAMES := ["HitSpark0", "HitSpark1", "HitSpark2", "HitSpark3"]
const LIFETIME_TICKS := 36               # hit_spark.tscn lifetime 0.6 s x 60 ticks/s
const HITSTOP := 4                       # main.gd HITSTOP_FRAMES
const HOLD_TICKS := 3                    # how long each key is held down
const POS_EPS := 1.0                     # rule 2: within 1 px in Main coordinates
const WALL_LIMIT_MS := 100000            # watchdog, under the wrapper's 120 s

var checks := 0
var failures := 0
var finished_run := false
var main: Node
var pool: Node
var slots: Array = []
var ticklog: TickLog
var sampler: Sampler
var setup_call: SetupCall
var results := []                        # attack_resolved of both fighters
var finished_log := []                   # {tick, slot}
var round_ticks := []                    # ticks on which round_started was emitted
var life_unpaused := -1                  # scenario B: hit tick -> emitting false, in ticks


## Records every slot once per physics tick, after main (0), the pool (10) and SetupCall (50).
class TickLog extends Node:
	var main: Node
	var slots: Array = []
	var recording := false
	var ticks := {}
	var order := []
	var last_tick := -1
	var prev: Array = []
	var fires := []                      # {tick, slot, pos}

	func _ready() -> void:
		process_physics_priority = 1000

	func reset(m: Node, s: Array) -> void:
		main = m
		slots = s
		ticks.clear()
		order.clear()
		fires.clear()
		prev = []
		for i in s.size():
			prev.append([false, Vector2.INF, 1.0])

	func _physics_process(_delta: float) -> void:
		if not (recording and is_instance_valid(main)):
			return
		last_tick = Engine.get_physics_frames()
		var now := []
		for i in slots.size():
			var e: CPUParticles2D = slots[i]
			var st := [e.emitting, e.position, e.speed_scale]
			if st[0] and (not prev[i][0] or st[1] != prev[i][1]):
				fires.append({"tick": last_tick, "slot": i, "pos": st[1]})
			now.append(st)
		prev = now
		ticks[last_tick] = {"slots": now, "phase": main.phase, "paused": main.paused,
				"hitstop": main.hitstop, "p2": main.p2.position}
		order.append(last_tick)


## Records speed_scale once per rendered frame, after every other _process.
class Sampler extends Node:
	var main: Node
	var slots: Array = []
	var recording := false
	var frames := []                     # [process frame, paused, speeds]
	var started_ms := 0
	var on_watchdog: Callable

	func _ready() -> void:
		process_priority = 1000
		started_ms = Time.get_ticks_msec()

	func _process(_delta: float) -> void:
		if Time.get_ticks_msec() - started_ms > WALL_LIMIT_MS:
			on_watchdog.call()
		if recording and is_instance_valid(main):
			frames.append([Engine.get_process_frames(), main.paused,
					slots.map(func(e): return e.speed_scale)])


## Runs one queued SETUP call inside a physics tick, after main and the pool, before TickLog.
class SetupCall extends Node:
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
	ticklog = TickLog.new()
	sampler = Sampler.new()
	sampler.on_watchdog = _watchdog
	setup_call = SetupCall.new()
	root.add_child(ticklog)
	root.add_child(sampler)
	root.add_child(setup_call)
	for i in 10:
		await process_frame
	print("hit spark state test: Godot %s, %d physics ticks/s; headless dummy renderer, nothing is drawn" % [
		Engine.get_version_info().string, ProjectSettings.get_setting("physics/common/physics_ticks_per_second")])
	check(ClassDB.class_has_signal("CPUParticles2D", "finished"), "harness",
			"CPUParticles2D has a 'finished' signal in this build (the pool frees slots on it)")
	await scenario_load()
	await scenario_single_hit()
	await scenario_retrigger()
	await scenario_free_fight()
	await scenario_pause()
	await scenario_round_reset_setup()
	finish()


# --- scenarios ---------------------------------------------------------------

func scenario_load() -> void:
	if not await start_fight("A: scene load -> title -> Enter -> intro -> fight, no attack (rules 1, 3, 4)", false, 30):
		await end_fight()
		return
	var title_ticks: Array = ticklog.order.filter(func(x): return ticklog.ticks[x]["phase"] == "title")
	var intro_ticks: Array = ticklog.order.filter(func(x): return ticklog.ticks[x]["phase"] == "intro")
	await wait_ticks(30)
	var any_on := ticklog.order.any(func(x): return ticklog.ticks[x]["slots"].any(func(s): return s[0]))
	check(ticklog.fires.is_empty() and not any_on and title_ticks.size() >= 30 and intro_ticks.size() >= 50, "1",
			"no slot emitting on any of %d ticks from scene load (%d title, %d intro, then fight), %d fires" % [
			ticklog.order.size(), title_ticks.size(), intro_ticks.size(), ticklog.fires.size()])
	var in_main := slots.size() == 4 and slots.all(func(e): return e is CPUParticles2D and e.get_parent() == main)
	var total := 0
	for e in slots:
		total += e.amount
	check(in_main and total == 80, "3, 4",
			"4 CPUParticles2D slots, each a child of Main, %d particles in all (brief: 4 x 20 = 80)" % total)
	var under_fighters := 0
	for f in [main.p1, main.p2]:
		under_fighters += f.find_children("*", "CPUParticles2D", true, false).size()
	check(under_fighters == 0, "4", "no particle emitter under P1 or P2 (%d found)" % under_fighters)
	await end_fight()


func scenario_single_hit() -> void:
	if not await start_fight("B: one punch on a standing Aotake (input only) (rules 1, 2, 4, 5)", false):
		await end_fight()
		return
	if not await walk_into_punch_range():
		await end_fight()
		return
	await tap(KEY_J, "J (punch)")
	await wait_until(func(): return hits().size() >= 1, 30)
	var h := hit(0)
	check(not h.is_empty(), "harness", "P1's punch from the J key hit P2 (%s)" % [result_names()])
	if h.is_empty():
		await end_fight()
		return
	await wait_ticks(LIFETIME_TICKS + HITSTOP + 10)
	var t: int = h["tick"]
	var f := fires_on(t)
	check(f.size() == 1 and ticklog.fires.size() == 1, "1",
			"exactly one slot fired, on the hit tick T = %d (slot %s), and no fire on any other tick (%d in all)" % [
			t, f.map(func(x): return x["slot"]), ticklog.fires.size()])
	if f.size() != 1:
		await end_fight()
		return
	var i: int = f[0]["slot"]
	var e: CPUParticles2D = slots[i]
	check(e.position.distance_to(h["point"]) <= POS_EPS and e.global_position.distance_to(main.to_global(h["point"])) <= POS_EPS,
			"2", "slot %d at %s, hit point %s (Main coordinates; global %s)" % [i, e.position, h["point"], e.global_position])
	var fall := fall_after(i, t)
	var moved: float = (tk(fall - 1).get("p2", Vector2.ZERO) as Vector2).distance_to(tk(t).get("p2", Vector2.ZERO))
	var still := true
	for x in range(t, fall):
		still = still and tk(x)["slots"][i][1] == h["point"]
	check(fall > t and still and moved > 3.0, "4",
			"the slot stayed at the hit point for its whole burst (T..T+%d) while P2 was pushed %.1f px" % [fall - t - 1, moved])
	life_unpaused = fall - t
	check(fall > t and life_unpaused >= LIFETIME_TICKS + HITSTOP - 1 and life_unpaused <= LIFETIME_TICKS + HITSTOP + 1, "5",
			"emitting went false %d ticks after the hit: 36-tick lifetime + %d hitstop ticks held at speed_scale 0 (want 39-41)" % [
			life_unpaused, HITSTOP])
	print("    'finished' after this burst on ticks %s (slot %d)" % [finished_log.map(func(x): return x["tick"] - t), i])
	await end_fight()


func scenario_retrigger() -> void:
	if not await start_fight("C: two punches inside one lifetime, Aotake cornered (input only) (rule 3)", false):
		await end_fight()
		return
	send_key(KEY_D, true)
	print("    INPUT: D (walk right) held from after tick %d, pushing Aotake to the right wall" % ticklog.last_tick)
	var ok: bool = await wait_until(func(): return main.p2.position.x >= Fighter.ARENA_RIGHT - 0.01, 900)
	send_key(KEY_D, false)
	var idle: bool = await wait_until(func(): return main.p1.state == "idle", 30)
	check(ok and idle, "harness", "Aotake at the right wall (x %.1f), P1 stopped at x %.1f" % [main.p2.position.x, main.p1.position.x])
	await tap(KEY_J, "J (punch 1)")
	await wait_until(func(): return hits().size() >= 1, 30)
	await wait_until(func(): return main.p1.state == "idle", 60)
	await tap(KEY_J, "J (punch 2)")
	await wait_until(func(): return hits().size() >= 2, 30)
	await wait_ticks(LIFETIME_TICKS * 2 + 2 * HITSTOP + 10)
	check(hits().size() == 2, "harness", "both punches hit (%s)" % [result_names()])
	if hits().size() != 2:
		await end_fight()
		return
	var t1: int = hit(0)["tick"]
	var t2: int = hit(1)["tick"]
	var f1 := fires_on(t1)
	var f2 := fires_on(t2)
	check(t2 - t1 < LIFETIME_TICKS, "harness", "second hit %d ticks after the first, inside one 36-tick lifetime" % [t2 - t1])
	if f1.size() != 1 or f2.size() != 1:
		check(false, "3", "one fire on each hit tick (got %d and %d)" % [f1.size(), f2.size()])
		await end_fight()
		return
	var a: int = f1[0]["slot"]
	var b: int = f2[0]["slot"]
	print("    hit 1 tick %d -> slot %d at %s; hit 2 tick %d -> slot %d at %s" % [t1, a, f1[0]["pos"], t2, b, f2[0]["pos"]])
	check(a != b, "3", "the second hit used another slot (%d, then %d), not the active one" % [a, b])
	var kept := true
	for x in range(t1, t2 + 1):
		kept = kept and tk(x)["slots"][a][0] and tk(x)["slots"][a][1] == f1[0]["pos"]
	check(kept and tk(t2)["slots"][b][0], "3",
			"slot %d emitted on every tick T1..T2 at its own point, and on T2 both slots are emitting" % a)
	var fall_a := fall_after(a, t1)
	var fall_b := fall_after(b, t2)
	check(fall_a > t2 and fall_a < t2 + LIFETIME_TICKS and fall_a < fall_b, "3",
			"slot %d ran its own burst to the end: emitting false at T1+%d = T2+%d, before slot %d at T2+%d (a restart would end after T2+36)" % [
			a, fall_a - t1, fall_a - t2, b, fall_b - t2])
	await end_fight()


func scenario_free_fight() -> void:
	if not await start_fight("D: a whole round against the game's CpuController, then Enter (rules 1, 2, 3, 6 real path)", true):
		await end_fight()
		return
	await tap(KEY_J, "J (punch from across the arena, a whiff)")
	await wait_ticks(20)
	send_key(KEY_L, true)
	print("    INPUT: L (block) held from after tick %d" % ticklog.last_tick)
	await wait_ticks(200)
	send_key(KEY_L, false)
	send_key(KEY_D, true)
	print("    INPUT: D held and J tapped every 24 ticks from after tick %d, until a K.O." % ticklog.last_tick)
	var limit := Engine.get_physics_frames() + 4000
	while main.phase == "fight" and Engine.get_physics_frames() < limit:
		send_key(KEY_J, true)
		await wait_ticks(HOLD_TICKS)
		send_key(KEY_J, false)
		await wait_ticks(21)
	send_key(KEY_D, false)
	check(main.phase == "ko" or main.phase == "result", "harness", "the round ended in a K.O. (phase %s)" % main.phase)
	await wait_until(func(): return main.phase == "result", 120)
	var by := {}
	for r in results:
		var k := "%s %s" % [r["who"], r["result"]]
		by[k] = by.get(k, 0) + 1
	print("    results: %s" % [by])
	check(by.get("P1 hit", 0) > 0 and by.get("P2 hit", 0) > 0 and (by.get("P1 blocked", 0) + by.get("P2 blocked", 0)) > 0
			and (by.get("P1 whiff", 0) + by.get("P2 whiff", 0)) > 0, "harness",
			"the round produced hits by both fighters, blocks and whiffs")
	var n_rounds := round_ticks.size()
	await tap(KEY_ENTER, "Enter (rematch on the result screen)")
	await wait_until(func(): return round_ticks.size() > n_rounds, 30)
	await wait_ticks(40)
	if round_ticks.size() > n_rounds:
		var rs: int = round_ticks[-1]
		var off: bool = not tk(rs).get("slots", [[true]]).any(func(s): return s[0])
		var later: Array = ticklog.fires.filter(func(x): return x["tick"] >= rs)
		var last_fire: int = ticklog.fires[-1]["tick"] if not ticklog.fires.is_empty() else -1
		check(off and later.is_empty(), "6",
				"real path: on the round_started tick (%d) no slot is emitting and none fires in the next 40 ticks (last burst fired %d ticks earlier, so this path cannot show a live burst being cleared)" % [
				rs, rs - last_fire])
	else:
		check(false, "6", "Enter on the result screen started a new round")
	await end_fight()


func scenario_pause() -> void:
	if not await start_fight("E: P pressed mid-burst for 40 ticks, then P again (input only) (rule 5)", false):
		await end_fight()
		return
	if not await walk_into_punch_range():
		await end_fight()
		return
	await tap(KEY_J, "J (punch)")
	await wait_until(func(): return hits().size() >= 1, 30)
	await wait_ticks(HITSTOP + 6)
	await tap(KEY_P, "P (pause)")
	await wait_ticks(40)
	await tap(KEY_P, "P (resume)")
	await wait_ticks(LIFETIME_TICKS + 10)
	var h := hit(0)
	if h.is_empty() or fires_on(h["tick"]).size() != 1:
		check(false, "harness", "the punch hit and one slot fired (%s)" % [result_names()])
		await end_fight()
		return
	var t: int = h["tick"]
	var i: int = fires_on(t)[0]["slot"]
	var paused: Array = ticklog.order.filter(func(x): return ticklog.ticks[x]["paused"])
	var frozen := paused.all(func(x): return ticklog.ticks[x]["slots"].all(func(s): return s[2] == 0.0))
	var pf: Array = sampler.frames.filter(func(s): return s[1])
	var frozen_f := pf.all(func(s): return s[2].all(func(v): return v == 0.0))
	check(paused.size() >= 40 and frozen and pf.size() >= 40 and frozen_f, "5",
			"speed_scale 0 on all 4 slots on all %d paused ticks and %d paused frames" % [paused.size(), pf.size()])
	var fall := fall_after(i, t)
	var during: bool = paused.all(func(x): return x < fall and ticklog.ticks[x]["slots"][i][0])
	var life := fall - t
	check(during and life_unpaused > 0 and absi(life - life_unpaused - paused.size()) <= 1, "5",
			"the burst's clock stopped while paused: emitting false %d ticks after the hit = %d unpaused (scenario B) + %d paused" % [
			life, life_unpaused, paused.size()])
	await end_fight()


func scenario_round_reset_setup() -> void:
	if not await start_fight("F: SETUP main.start_fight_now() mid-burst, then a new punch (rule 6, Zhaohui's choice (b))", false):
		await end_fight()
		return
	if not await walk_into_punch_range():
		await end_fight()
		return
	await tap(KEY_J, "J (punch 1)")
	await wait_until(func(): return hits().size() >= 1, 30)
	await wait_ticks(HITSTOP + 6)
	var h := hit(0)
	if h.is_empty() or fires_on(h["tick"]).size() != 1:
		check(false, "harness", "punch 1 hit and one slot fired (%s)" % [result_names()])
		await end_fight()
		return
	var i: int = fires_on(h["tick"])[0]["slot"]
	check(tk(ticklog.last_tick)["slots"][i][0], "harness", "slot %d is mid-burst (hit tick +%d)" % [i, ticklog.last_tick - h["tick"]])
	var fin_before := finished_log.size()
	setup_call.done_tick = -1
	setup_call.pending = func():
		print("    SETUP (not input): main.start_fight_now() on tick T+%d, slot %d emitting" % [
			Engine.get_physics_frames() - h["tick"], i])
		main.start_fight_now()
	await wait_until(func(): return setup_call.done_tick >= 0, 10)
	var s: int = setup_call.done_tick
	await wait_ticks(LIFETIME_TICKS + 10)
	var off: bool = not tk(s).get("slots", [[true]]).any(func(x): return x[0])
	var quiet: Array = ticklog.fires.filter(func(x): return x["tick"] > h["tick"])
	check(s >= 0 and off and quiet.is_empty(), "6",
			"on the SETUP tick every slot stopped emitting (slot %d was mid-burst), and no slot fired in the next %d ticks" % [
			i, LIFETIME_TICKS + 10])
	print("    'finished' after the SETUP on ticks %s (slot: ticks after SETUP)" % [
		finished_log.slice(fin_before).map(func(x): return "%d: %d" % [x["slot"], x["tick"] - s])])
	if not await walk_into_punch_range():
		await end_fight()
		return
	await tap(KEY_J, "J (punch 2, in the new round)")
	await wait_until(func(): return hits().size() >= 2, 30)
	await wait_ticks(5)
	var h2 := hit(1)
	var f2: Array = fires_on(h2["tick"]) if not h2.is_empty() else []
	check(f2.size() == 1 and (f2[0]["pos"] as Vector2).distance_to(h2["point"]) <= POS_EPS, "6",
			"after the reset the next hit fires one slot (%s) at its point" % [f2.map(func(x): return "slot %d at %s" % [x["slot"], x["pos"]])])
	await end_fight()


# --- checks over every scenario ---------------------------------------------

## Rules 1 and 2 over the whole scene: on every tick, fires == "hit" results of both fighters, each
## at its point; rule 3's fallback reported if it happened; rule 5 on every tick and frame.
func check_scene() -> void:
	var hit_by := {}
	for r in results:
		if r["result"] == "hit":
			hit_by.get_or_add(r["tick"], []).append(r)
	var fire_by := {}
	for f in ticklog.fires:
		fire_by.get_or_add(f["tick"], []).append(f)
	var bad := []
	var fallback := 0
	for t in hit_by:
		var fs: Array = fire_by.get(t, []).duplicate()
		if fs.size() != hit_by[t].size():
			bad.append("tick %d: %d hits, %d fires" % [t, hit_by[t].size(), fs.size()])
			continue
		for r in hit_by[t]:
			var j := -1
			for k in fs.size():
				if (fs[k]["pos"] as Vector2).distance_to(r["point"]) <= POS_EPS:
					j = k
			if j < 0:
				bad.append("tick %d: no fire at %s" % [t, r["point"]])
				continue
			if not (r["busy"] as Array).has(false):
				fallback += 1
				var oldest: int = r["started"].find(r["started"].min())
				if fs[j]["slot"] != oldest:
					bad.append("tick %d: all busy, fired slot %d, oldest %d" % [t, fs[j]["slot"], oldest])
			fs.remove_at(j)
	for t in fire_by:
		if not hit_by.has(t):
			bad.append("tick %d: fire with no hit" % t)
	var other := results.filter(func(r): return r["result"] != "hit").size()
	check(bad.is_empty(), "1, 2",
			"scene: %d fires for %d hits, one per hit on its tick within 1 px of its point; none on %d other results or any other tick%s" % [
			ticklog.fires.size(), hit_by.values().reduce(func(n, a): return n + a.size(), 0), other,
			"" if bad.is_empty() else ": " + ", ".join(bad.slice(0, 5))])
	print("    rule 3 fallback (all four slots busy at a hit): %d time(s)%s" % [fallback,
		"" if fallback else "; not exercised in this scene"])
	var wrong := []
	for t in ticklog.order:
		var r: Dictionary = ticklog.ticks[t]
		var want := 0.0 if (r["paused"] or r["hitstop"] > 0) else 1.0
		if not r["slots"].all(func(s): return s[2] == want):
			wrong.append(t)
	var held: int = ticklog.order.filter(func(t): return ticklog.ticks[t]["hitstop"] > 0).size()
	check(wrong.is_empty(), "5",
			"scene: speed_scale 0 on all 4 slots on every tick with main.paused or main.hitstop > 0 (%d hitstop ticks), 1 on the other %d ticks%s" % [
			held, ticklog.order.size() - held, "" if wrong.is_empty() else ": wrong on ticks %s" % [wrong.slice(0, 5)]])


# --- helpers -----------------------------------------------------------------

func start_fight(title: String, cpu: bool, title_ticks := 0) -> bool:
	print("\n== %s ==" % title)
	main = load("res://game/main.tscn").instantiate()
	pool = main.get_node("HitSparkPool")
	slots = SLOT_NAMES.map(func(n): return main.get_node(n))
	results.clear()
	finished_log.clear()
	round_ticks.clear()
	sampler.frames.clear()
	ticklog.reset(main, slots)
	sampler.main = main
	sampler.slots = slots
	# Connected before main enters the tree, so these run before the pool's handler (snapshot of
	# the pool's busy state for the fallback report) and before main's.
	for f in [main.get_node("P1"), main.get_node("P2")]:
		f.attack_resolved.connect(func(_f, kind, result, point):
			results.append({"tick": Engine.get_physics_frames(), "who": "P1" if f.name == "P1" else "P2",
				"kind": kind, "result": result, "point": point,
				"busy": pool.busy.duplicate(), "started": pool.started.duplicate()}))
	for i in slots.size():
		slots[i].finished.connect(func(): finished_log.append({"tick": Engine.get_physics_frames(), "slot": i}))
	main.round_started.connect(func(_n): round_ticks.append(Engine.get_physics_frames()))
	if not cpu:
		main.round_started.connect(func(_n): main.p2.controller = null)
	ticklog.recording = true
	sampler.recording = true
	root.add_child(main)
	await process_frame
	check(main.is_physics_processing() and main.p1.controller is PlayerController, "harness",
			"main's _physics_process is on and P1 is driven by its PlayerController")
	await wait_ticks(title_ticks)
	await tap(KEY_ENTER, "Enter (title)")
	var ok := await wait_until(func(): return main.phase == "fight", 120)
	check(ok, "harness", "Enter on the title started round 1; the intro ran into the fight (phase %s)" % main.phase)
	if not cpu:
		print("    HARNESS (writes no fight state): P2's controller set to null when the round starts, so Aotake stands still")
	return ok


func end_fight() -> void:
	for k in [KEY_D, KEY_J, KEY_L, KEY_P, KEY_ENTER]:
		send_key(k, false)
	setup_call.pending = Callable()
	ticklog.recording = false
	sampler.recording = false
	if is_instance_valid(main):
		check_scene()
		var kept := slots.duplicate()
		main.queue_free()
		await process_frame
		await process_frame
		check(kept.all(func(e): return not is_instance_valid(e)), "4",
				"freeing Main freed all 4 slots with it")


func walk_into_punch_range() -> bool:
	var gap: float = main.p1.reach("punch") + main.p2.body_half_width() - 8.0
	send_key(KEY_D, true)
	print("    INPUT: D (walk right) held from after tick %d" % ticklog.last_tick)
	var ok: bool = await wait_until(func(): return main.p2.position.x - main.p1.position.x <= gap, 300)
	send_key(KEY_D, false)
	var idle: bool = await wait_until(func(): return main.p1.state == "idle", 30)
	check(ok and idle, "harness", "P1 walked to punch range with the D key (gap %.1f px, target <= %.1f) and stopped" % [
		main.p2.position.x - main.p1.position.x, gap])
	return ok and idle


func hits() -> Array:
	return results.filter(func(r): return r["result"] == "hit")


func hit(index: int) -> Dictionary:
	var h := hits()
	return h[index] if h.size() > index else {}


func result_names() -> Array:
	return results.map(func(r): return "%s %s %s" % [r["who"], r["kind"], r["result"]])


func fires_on(t: int) -> Array:
	return ticklog.fires.filter(func(f): return f["tick"] == t)


## First recorded tick after t0 on which slot i is not emitting, or -1.
func fall_after(i: int, t0: int) -> int:
	for t in ticklog.order:
		if t > t0 and not ticklog.ticks[t]["slots"][i][0]:
			return t
	return -1


func tk(t: int) -> Dictionary:
	return ticklog.ticks.get(t, {})


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


func check(cond: bool, rule: String, msg: String) -> void:
	checks += 1
	if not cond:
		failures += 1
	print("%s [%s] %s" % ["PASS" if cond else "FAIL", rule, msg])


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
