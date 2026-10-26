#!/usr/bin/env bash
# scripts/run-test.sh <test-file.gd> <fps>
# Godot 4.7.2 is not on PATH on Zhaohui's machine; set GODOT to the console build, e.g.
#   export GODOT=~/Downloads/Godot_v4.7.2-stable_win64.exe/Godot_v4.7.2-stable_win64_console.exe
set -o pipefail
godot="${GODOT:-godot}"
mkdir -p logs
log="logs/$(basename "$1" .gd)_${2}fps.log"
timeout 120 "$godot" --headless --path godot --script "res://tests/$1" --fixed-fps "$2" 2>&1 | tee "$log"
status=$?
if grep -qE "SHADER ERROR|SCRIPT ERROR" "$log"; then status=1; fi
exit $status
