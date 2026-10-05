extends Node
## Plays every sound in the slice. It only LISTENS to game signals and never changes game state,
## so a missing, muted or failing sound cannot change what happens (CHANGE-BRIEF event map).
##
##   attack_resolved "hit"     -> SFX-HIT
##   attack_resolved "blocked" -> SFX-BLOCK
##   attack_resolved "whiff"   -> SFX-WHIFF
##   attack_resolved "interrupted" -> nothing
##   knocked_out               -> SFX-KO, music stops
##   round_started             -> music restarts from 0 if it was stopped (rematch)
##   paused_changed            -> music ducks -12 dB with a low-pass; effects pause
##
## Missing files are allowed: the request is still counted (for tests) but nothing plays.

const SFX_FILES := {
	"SFX-WHIFF": "res://audio/sfx/whiff",
	"SFX-HIT": "res://audio/sfx/hit",
	"SFX-BLOCK": "res://audio/sfx/block",
	"SFX-KO": "res://audio/sfx/ko",
}
const MUSIC_FILE := "res://audio/music/loop"
const RESULT_SOUND := {"hit": "SFX-HIT", "blocked": "SFX-BLOCK", "whiff": "SFX-WHIFF"}
const DUCK_DB := -12.0
const DUCK_CUTOFF_HZ := 900.0

var requests := {}            # sound id -> times requested
var events := []              # [sound id, ...] in order, for tests
var music_state := "stopped"  # stopped | playing | ducked
var music_starts := 0         # times the loop was (re)started from 0
var players := {}
var music: AudioStreamPlayer
var music_bus := -1
var sfx_bus := -1
var missing := []


func _ready() -> void:
	music_bus = _ensure_bus("Music")
	sfx_bus = _ensure_bus("SFX")
	if AudioServer.get_bus_effect_count(music_bus) == 0:
		var lp := AudioEffectLowPassFilter.new()
		lp.cutoff_hz = DUCK_CUTOFF_HZ
		AudioServer.add_bus_effect(music_bus, lp)
	AudioServer.set_bus_effect_enabled(music_bus, 0, false)
	for id in SFX_FILES:
		var p := AudioStreamPlayer.new()
		p.bus = "SFX"
		p.max_polyphony = 4
		p.stream = _load_audio(SFX_FILES[id], id)
		add_child(p)
		players[id] = p
		requests[id] = 0
	music = AudioStreamPlayer.new()
	music.bus = "Music"
	music.stream = _load_audio(MUSIC_FILE, "MUS-LOOP")
	if music.stream and "loop" in music.stream:
		music.stream.loop = true          # OGG: loop at the file's end (the cut is made at a bar line)
	add_child(music)
	if missing:
		print("AudioDirector: no file yet for ", ", ".join(missing), " (requests are still counted)")


func connect_game(main: Node, fighters: Array) -> void:
	for f in fighters:
		f.attack_resolved.connect(_on_attack_resolved)
		f.knocked_out.connect(_on_knocked_out)
	main.round_started.connect(_on_round_started)
	main.paused_changed.connect(_on_paused_changed)


func start_music() -> void:
	music_starts += 1
	music_state = "playing"
	if music.stream:
		music.play(0.0)


func stop_music() -> void:
	music_state = "stopped"
	music.stop()


func toggle_mute(bus_name: String) -> bool:
	var i := AudioServer.get_bus_index(bus_name)
	AudioServer.set_bus_mute(i, not AudioServer.is_bus_mute(i))
	return AudioServer.is_bus_mute(i)


func is_muted(bus_name: String) -> bool:
	return AudioServer.is_bus_mute(AudioServer.get_bus_index(bus_name))


func play(id: String) -> void:
	requests[id] += 1
	events.append(id)
	var p: AudioStreamPlayer = players[id]
	if p.stream:
		p.play()


func _on_attack_resolved(_f, _kind: String, result: String, _point: Vector2) -> void:
	if RESULT_SOUND.has(result):
		play(RESULT_SOUND[result])


func _on_knocked_out(_f) -> void:
	play("SFX-KO")
	stop_music()


func _on_round_started(_n: int) -> void:
	if music_state == "stopped":
		start_music()


func _on_paused_changed(paused: bool) -> void:
	AudioServer.set_bus_volume_db(music_bus, DUCK_DB if paused else 0.0)
	AudioServer.set_bus_effect_enabled(music_bus, 0, paused)
	if music_state != "stopped":
		music_state = "ducked" if paused else "playing"
	for id in players:
		players[id].stream_paused = paused


func _ensure_bus(bus_name: String) -> int:
	var i := AudioServer.get_bus_index(bus_name)
	if i == -1:
		AudioServer.add_bus()
		i = AudioServer.bus_count - 1
		AudioServer.set_bus_name(i, bus_name)
		AudioServer.set_bus_send(i, "Master")
	return i


func _load_audio(base: String, id: String) -> AudioStream:
	for ext in [".ogg", ".wav"]:
		if ResourceLoader.exists(base + ext):
			return load(base + ext)
	missing.append(id)
	return null
