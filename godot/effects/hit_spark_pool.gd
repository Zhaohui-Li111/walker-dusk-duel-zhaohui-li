extends Node
## A6 Effect A (hit spark): starts the four pooled HitSpark emitters that main.tscn parents to Main
## (CHANGE-BRIEF.md, Effect A, observable rules 1-6). Reads the fight's signals, main.paused and
## main.hitstop; writes nothing but its own emitters' position, emitting and speed_scale. Every
## particle setting lives in res://effects/hit_spark.tscn.

const SLOT_NAMES := ["HitSpark0", "HitSpark1", "HitSpark2", "HitSpark3"]

var main: Node
var slots: Array[CPUParticles2D] = []
var busy: Array[bool] = []
var started: Array[int] = []         # start order of each slot's current burst, for "oldest"
var _next := 0


func _ready() -> void:
	process_physics_priority = 10    # after main (0), so this tick's hitstop is already set
	main = get_parent()
	for i in SLOT_NAMES.size():
		var slot := main.get_node(SLOT_NAMES[i]) as CPUParticles2D
		slots.append(slot)
		busy.append(false)
		started.append(-1)
		if slot.has_signal("finished"):
			slot.finished.connect(_on_slot_finished.bind(i))
		else:
			push_error("hit_spark_pool: CPUParticles2D has no 'finished' signal; slots never become free")
	for f in [main.get_node("P1"), main.get_node("P2")]:
		f.attack_resolved.connect(_on_attack_resolved)
	main.round_started.connect(_on_round_started)
	main.paused_changed.connect(func(_p): _apply_speed())


func _physics_process(_delta: float) -> void:
	_apply_speed()


## Rules 1-3: one burst per "hit", at its point, in a free slot; the oldest slot if all four are busy.
func _on_attack_resolved(_f: Node, _kind: String, result: String, point: Vector2) -> void:
	if result != "hit":
		return
	var i := busy.find(false)
	if i < 0:
		i = started.find(started.min())
	var slot := slots[i]
	slot.position = point
	slot.restart()
	busy[i] = true
	started[i] = _next
	_next += 1


func _on_slot_finished(i: int) -> void:
	busy[i] = false


## Rule 5: the game's pause and hitstop do not pause the tree, so the emitters are frozen here.
func _apply_speed() -> void:
	var s := 0.0 if (main.paused or main.hitstop > 0) else 1.0
	for slot in slots:
		slot.speed_scale = s


## Rule 6: a new round clears every burst without emitting a new one.
func _on_round_started(_n: int) -> void:
	for i in slots.size():
		slots[i].restart()
		slots[i].emitting = false
		busy[i] = false
		started[i] = -1
