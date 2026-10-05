class_name Intent
extends RefCounted
## What a controller wants this frame. Player input, the CPU and scripted tests all produce
## the same Intent, so the fighter code never knows who is driving it.

var move := 0.0          # -1 = screen left, +1 = screen right
var jump := false        # pressed this frame
var crouch := false      # held
var block := false       # held
var attack := ""         # "punch" / "kick" pressed this frame, else ""
