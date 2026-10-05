extends Node2D
## The courtyard. Uses the generated background (res://art/env/bg.png, ENV-BG) when it exists;
## otherwise draws a Claude-coded placeholder in the CHARACTER-SHEET palette.

const BG_PATH := "res://art/env/bg.png"
const SKY := Color("5a4766")
const WALL := Color("3a3347")
const FLOOR := Color("2b2733")
const LANTERN := Color("f2a541")

var background: Texture2D


func _ready() -> void:
	if ResourceLoader.exists(BG_PATH):
		background = load(BG_PATH)
	else:
		print("Stage: placeholder background (no %s yet)" % BG_PATH)


func _draw() -> void:
	if background:
		draw_texture_rect(background, Rect2(0, 0, 640, 360), false)
		return
	draw_rect(Rect2(0, 0, 640, 100), SKY)
	draw_rect(Rect2(0, 100, 640, 205), WALL)
	draw_rect(Rect2(0, 305, 640, 55), FLOOR)
	for x in [70.0, 570.0]:
		draw_line(Vector2(x, 100), Vector2(x, 125), Color(0.08, 0.08, 0.08), 2.0)
		draw_circle(Vector2(x, 140), 15.0, LANTERN)
