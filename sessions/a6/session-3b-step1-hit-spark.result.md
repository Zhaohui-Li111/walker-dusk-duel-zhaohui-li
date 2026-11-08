Step 1 已完成：新增一个脚本 `godot/effects/hit_spark_pool.gd`，并接线 `godot/game/main.tscn`。两个测试在 60 下都通过：`test_hit_spark_config.gd` 69 / 0，`test_runner.gd` 94 / 0，与之前的数量相同。没有改其他文件，也没有 commit。

## Diff

**`godot/game/main.tscn`**（已修改）
```diff
-[gd_scene load_steps=7 format=3]
+[gd_scene load_steps=9 format=3]
 ...
 [ext_resource type="Script" path="res://game/audio_director.gd" id="6_audio"]
+[ext_resource type="PackedScene" path="res://effects/hit_spark.tscn" id="7_hit_spark"]
+[ext_resource type="Script" path="res://effects/hit_spark_pool.gd" id="8_hit_spark_pool"]
 ...
 [node name="Effects" type="Node2D" parent="."]
 script = ExtResource("4_effects")
 
+[node name="HitSpark0" parent="." instance=ExtResource("7_hit_spark")]
+
+[node name="HitSpark1" parent="." instance=ExtResource("7_hit_spark")]
+
+[node name="HitSpark2" parent="." instance=ExtResource("7_hit_spark")]
+
+[node name="HitSpark3" parent="." instance=ExtResource("7_hit_spark")]
+
+[node name="HitSparkPool" type="Node" parent="."]
+script = ExtResource("8_hit_spark_pool")
+
 [node name="HUD" type="CanvasLayer" parent="."]
```
四个实例上都没有覆盖任何属性，设置全部留在 `hit_spark.tscn`。它们排在 `Effects` 之后，所以画在 fighter 和旧火花上面。

**`godot/effects/hit_spark_pool.gd`**（新文件，全文）
```gdscript
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
```

## Test runs (`./scripts/run-test.sh`, fixed 60 fps)

- **`test_hit_spark_config.gd 60` → `69 checks, 0 failed`.** The full output is above. This test loads `hit_spark.tscn` on its own, so it shows the effect's settings are unchanged. It does not exercise the wiring.
- **`test_runner.gd 60` → `94 checks, 0 failed`.** This run loads the new `main.tscn`, so the pool's `_ready` runs. The output ends with a warning that 44 ObjectDB instances leaked at exit and an error that 8 resources were still in use. The committed log `HEAD:logs/test_runner_60fps.log` ends with the same two lines, so these were there before this change.

## What this proves, and what it doesn't

- **Proved:** `main.tscn` loads with the 4 emitters and the pool; existing behaviour and test counts are unchanged; Effect A's settings are unchanged.
- **Indirect only:** the `push_error` about a missing `finished` signal did not appear when `test_runner` loaded `main.tscn`. That suggests 4.7.2's `CPUParticles2D` has `finished`, but nothing has asserted it yet.
- **Not tested yet:** rules 1–6 themselves. That is Step 2, the state test.
  - The rule 6 SETUP check you chose (b) is not written yet either; it goes in Step 2.
  - Step 2 will also check whether `emitting` turns false on its own when a one-shot burst ends, and Q2 (does a burst spawn at `speed_scale` 0).
- **One edge case in rule 6:** after `restart()` + `emitting = false`, a slot may still send `finished` later. That only clears a busy flag that is already clear, and the 60-tick intro makes a new hit in between impossible, so it has no effect. The Step 2 test will log it.

There is no `.uid` file for `hit_spark_pool.gd` yet; Godot creates it the next time the editor or `--import` runs. Reply when you want Step 2.