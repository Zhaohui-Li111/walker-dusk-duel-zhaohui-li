I've done step 1. The driver is a new file, `godot/fighter/hurt_flash.gd`, and the only scene change is one node added to `fighter.tscn`. Both existing tests pass at 60 fps (94 and 49 checks, 0 failed). I did not edit any `.gdshader`, existing script or existing test, I wrote no probe or new test, and I have not committed.

## Diff

New file `godot/fighter/hurt_flash.gd`:

```gdscript
extends Node
## Hurt flash driver (A5). A child of the fighter's Sprite2D. Gives that sprite its own
## ShaderMaterial of hurt_flash.gdshader, so a hit on one fighter never flashes the other, and
## sets hurt_amount once per physics tick from the fighter's state. Presentation only: it reads
## state and stun and never writes game state. flash_color keeps the shader's default.

const SHADER := preload("res://shaders/hurt_flash.gdshader")

var material: ShaderMaterial

@onready var sprite: Sprite2D = get_parent()
@onready var fighter: Fighter = sprite.get_parent()


func _ready() -> void:
	# main.gd steps the fighters at the default priority 0; a higher value runs after it, so the
	# value set here is the one for the state of this same tick.
	process_physics_priority = 100
	material = ShaderMaterial.new()
	material.shader = SHADER
	sprite.material = material


func _physics_process(_delta: float) -> void:
	var amount := 0.0
	if fighter.state == "hurt":
		amount = float(fighter.stun) / float(Fighter.HITSTUN)
	material.set_shader_parameter("hurt_amount", amount)
```

`godot/fighter/fighter.tscn`:

```diff
-[gd_scene load_steps=2 format=3]
+[gd_scene load_steps=3 format=3]
 
 [ext_resource type="Script" path="res://fighter/fighter.gd" id="1_fighter"]
+[ext_resource type="Script" path="res://fighter/hurt_flash.gd" id="2_hurt_flash"]
 ...
+
+[node name="HurtFlash" type="Node" parent="Sprite2D"]
+script = ExtResource("2_hurt_flash")
```

## Test output

`./scripts/run-test.sh test_runner.gd 60`:
```
Godot Engine v4.7.2.stable.official.ed1daf0bf - https://godotengine.org

- test_walk_and_facing
...
- test_mute_never_changes_the_fight
    with sound [0, 42, "result", 344.42, 408.25, 18] / muted [0, 42, "result", 344.42, 408.25, 18]
94 checks, 0 failed
WARNING: 66 ObjectDB instances were leaked at exit (run with `--verbose` for details).
   at: cleanup (core/object/object.cpp:2536)
ERROR: 10 resources still in use at exit (run with --verbose for details).
   at: clear (core/io/resource.cpp:822)
```
(The tests I cut from the middle printed the same lines as before, including `hit 17, blocked 5, whiff 2, interrupted 9`.)

`./scripts/run-test.sh check_props3d.gd 60`:
```
Godot Engine v4.7.2.stable.official.ed1daf0bf - https://godotengine.org

floor top y 0.0000
- PROP-LANTERN ... tris 100  albedo ["6e6680", "f5c542", "4e475c"]
- PROP-MAKIWARA ... tris 92  albedo ["6e6680", "8a5a3b", "d8b676", "f2e6d0"]
- PROP-TAIKO ... tris 168  albedo ["1e1b22", "d9482b", "f2e6d0"]
49 checks, 0 failed
```

**There are no `SHADER ERROR` or `SCRIPT ERROR` lines.** A search of both logs for those strings, and for `hurt_flash`, finds nothing.

The warning and error at the end of the test_runner run are not new: the committed baseline log ends with the same two lines. The leaked-object count is lower than the baseline's (66, was 86). I haven't looked into why. The 10 resources still in use is unchanged. The only resulting change is the rewritten `logs/test_runner_60fps.log`; the props3d log came out identical.

## What these runs prove

- `hurt_flash.gd` parses and loads.
- `fighter.tscn`, with the new node, still loads inside `main.tscn`.
- Both fighters' `_ready()` ran with no script error. So the paths `get_parent()` → Sprite2D → Fighter resolved, and `res://shaders/hurt_flash.gdshader` loaded without a shader error.
- Adding the node did not change any of the 94 fight, sound and music checks. That fits the driver writing nothing to game state, but it only shows the effect on what those tests measure.
- The props room is untouched (49/49).

## What they do not prove

- **The driver in the real loop: not tested.** `test_runner.gd` turns off physics on `main` only (`test_runner.gd:48`) and calls `step()` itself. My node's `_physics_process` does still run, but nothing checks `hurt_amount`, and its order relative to `main` is not tested here.
- **Rules 1–6: none checked.** That covers the value on the hit tick and the tick it ends, the 0.367 s at 30/60/144, retrigger, time scale and pause, K.O. leaving no tail, and P1 staying at 0 while P2 flashes. That is step 2.
- **Priority ordering: not observed.** Godot's documentation says higher values run later, so 100 should run after `main` at 0, but no run has shown it yet.
- **Uniform names and types: not checked.** `set_shader_parameter` with a misspelled name raises no error, so a clean run does not show that `hurt_amount` matches the shader. Only `get_shader_uniform_list()` in step 2 shows that.
- **Pixels: not shown.** Headless runs use the dummy renderer, so nothing about colour, blending or how the flash reads in play. Those are the windowed captures and the playtest.

One more thing: Godot did not create a `hurt_flash.gd.uid` file during these headless runs. The editor or `--import` will make one, and it should be committed along with the script.