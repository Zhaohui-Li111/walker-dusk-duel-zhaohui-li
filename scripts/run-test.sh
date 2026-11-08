#!/usr/bin/env bash
# scripts/run-test.sh <test-file.gd> <fps|realtime> [timeout-seconds]
# A6 wrapper (course handout), plus one local addition: Godot 4.7.2 is not on PATH on
# Zhaohui's machine, so GODOT may name the console build, e.g.
#   export GODOT=~/Downloads/Godot_v4.7.2-stable_win64.exe/Godot_v4.7.2-stable_win64_console.exe
set -o pipefail
godot="${GODOT:-godot}"
mkdir -p logs
if [ "$2" = "realtime" ]; then
	fps_args=(); tag="realtime"
else
	fps_args=(--fixed-fps "$2"); tag="${2}fps"
fi
log="logs/$(basename "$1" .gd)_${tag}.log"
timeout "${3:-120}" "$godot" --headless "${fps_args[@]}" --path godot --script "res://tests/$1" 2>&1 | tee "$log"
status=$?
if grep -qE "SHADER ERROR|SCRIPT ERROR" "$log"; then status=1; fi
exit $status
