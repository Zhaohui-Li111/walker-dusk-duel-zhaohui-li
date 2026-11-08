extends Node
## A6 Effect B (courtyard embers): starts and stops the Embers emitter that main.tscn parents to Main
## (CHANGE-BRIEF.md, Effect B, observable rules 1-5). main.phase has no change signal, so it is polled
## once per physics tick (Zhaohui's decision, 2026-11-08). Reads main.phase, main.paused and
## main.hitstop; writes nothing but the emitter's emitting and speed_scale. Every particle setting
## lives in res://effects/embers.tscn. Never touches visible or process_mode (rules 3 and 4).

var main: Node
var embers: CPUParticles2D
var _in_fight := false


func _ready() -> void:
	process_physics_priority = 10    # after main (0), so this tick's phase and hitstop are already set
	main = get_parent()
	embers = main.get_node("Embers") as CPUParticles2D
	main.paused_changed.connect(func(_p): _apply_speed())


func _physics_process(_delta: float) -> void:
	var fight: bool = main.phase == "fight"
	if fight and not _in_fight:
		# Rule 1 says "emitting = true"; restart() also sets emitting to true, and resets the
		# emitter's time so preprocess (1.5 s) runs again in every round, as rule 5 intends. Plain
		# emitting = true may only preprocess the first time (brief, Unconfirmed Q3). No embers are
		# erased: a K.O., the result screen and the 1 s intro always take longer than the 2.5 s
		# lifetime. (Claude Code, under Zhaohui's delegation, 2026-11-08.)
		embers.restart()
	elif _in_fight and not fight:
		embers.emitting = false      # rule 1: stop emitting; live particles finish their lifetime
	_in_fight = fight
	_apply_speed()


## Rule 2 and the settings table: the game's pause and hitstop do not pause the tree.
func _apply_speed() -> void:
	embers.speed_scale = 0.0 if (main.paused or main.hitstop > 0) else 1.0
