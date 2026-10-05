extends Node
## Registers every input action in code so the bindings are readable in one place.
## Keyboard: A/D or arrows move, W/Up jump, S/Down crouch, J punch, K kick, L block,
## Esc/P pause, M mute music, N mute effects, Enter confirm, F1 collision debug.
## Gamepad: d-pad or left stick move, X punch, A kick, RB block, Start pause.

const BINDINGS := {
	"p1_left": [KEY_A, KEY_LEFT, JOY_BUTTON_DPAD_LEFT],
	"p1_right": [KEY_D, KEY_RIGHT, JOY_BUTTON_DPAD_RIGHT],
	"p1_jump": [KEY_W, KEY_UP, JOY_BUTTON_DPAD_UP],
	"p1_crouch": [KEY_S, KEY_DOWN, JOY_BUTTON_DPAD_DOWN],
	"p1_punch": [KEY_J, JOY_BUTTON_X],
	"p1_kick": [KEY_K, JOY_BUTTON_A],
	"p1_block": [KEY_L, JOY_BUTTON_RIGHT_SHOULDER],
	"pause": [KEY_ESCAPE, KEY_P, JOY_BUTTON_START],
	"confirm": [KEY_ENTER, KEY_KP_ENTER, KEY_SPACE],
	"mute_music": [KEY_M],
	"mute_sfx": [KEY_N],
	"debug_boxes": [KEY_F1],
}

## Keys from this list are joypad buttons; everything else is a keyboard keycode.
const JOY_ACTIONS := ["p1_left", "p1_right", "p1_jump", "p1_crouch", "p1_punch", "p1_kick", "p1_block", "pause"]


func _ready() -> void:
	for action in BINDINGS:
		if not InputMap.has_action(action):
			InputMap.add_action(action, 0.3)
		var codes: Array = BINDINGS[action]
		for i in codes.size():
			var is_joy: bool = action in JOY_ACTIONS and i == codes.size() - 1
			if is_joy:
				var jb := InputEventJoypadButton.new()
				jb.button_index = codes[i]
				InputMap.action_add_event(action, jb)
			else:
				var key := InputEventKey.new()
				key.physical_keycode = codes[i]
				InputMap.action_add_event(action, key)
	_add_stick("p1_left", JOY_AXIS_LEFT_X, -1.0)
	_add_stick("p1_right", JOY_AXIS_LEFT_X, 1.0)
	_add_stick("p1_jump", JOY_AXIS_LEFT_Y, -1.0)
	_add_stick("p1_crouch", JOY_AXIS_LEFT_Y, 1.0)


func _add_stick(action: String, axis: JoyAxis, dir: float) -> void:
	var m := InputEventJoypadMotion.new()
	m.axis = axis
	m.axis_value = dir
	InputMap.action_add_event(action, m)
