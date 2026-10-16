# Re-run the three build_<asset>.py files headless, saving into a scratch folder instead of
# blender/, so the committed .blend files are never overwritten. Each build file is executed
# exactly as Claude ran it in the live session; only the save folder in the text is swapped.
# From the repo root:
#   /d/blender/blender.exe -b --factory-startup --python-exit-code 1 \
#       --python tools/blender/reproduce.py -- <scratch folder>
# then run check_blend.py on each scratch .blend and compare its "verts" fingerprint with the
# committed file's.
import bpy, os, sys

here = os.path.dirname(os.path.abspath(__file__))
out = os.path.abspath(sys.argv[sys.argv.index("--") + 1])
live = r"D:\courses\7270\walker-dusk-duel-zhaohui-li\blender"
os.makedirs(out, exist_ok=True)
for asset in ("lantern", "makiwara", "taiko"):
    src = open(os.path.join(here, f"build_{asset}.py"), encoding="utf-8").read()
    assert live in src, f"build_{asset}.py no longer names the live save folder"
    src = src.replace(live, out)
    print(f"--- build_{asset}.py")
    exec(compile(src, f"build_{asset}.py", "exec"), {"__name__": "__main__"})
