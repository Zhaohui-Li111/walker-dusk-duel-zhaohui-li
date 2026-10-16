# Export the prop mesh in an open .blend as binary glTF (.glb), +Y up, transforms applied.
# This is the script Claude Code ran headless on 2026-10-16 to make godot/props3d/models/*.glb
# (Blender 5.2.2's export_format enum list is empty in RNA, so 'GLB' is passed and a TypeError
# would list the valid values). Run once per prop, from the repo root (Windows, Git Bash):
#   /d/blender/blender.exe -b blender/prop_lantern.blend --factory-startup --python-exit-code 1 \
#       --python tools/blender/export_glb.py -- "$(cygpath -w "$PWD")\\godot\\props3d\\models\\prop_lantern.glb"
# Then re-import in Godot: godot --headless --path godot --import
import bpy, sys, os
out = sys.argv[sys.argv.index("--")+1]
bpy.ops.object.select_all(action='DESELECT')
props = [o for o in bpy.data.objects if o.type=='MESH']
for o in props: o.select_set(True)
try:
    r = bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', use_selection=True, export_yup=True,
                                  export_apply=True, export_cameras=False, export_lights=False)
except TypeError as e:
    print("EXP enum error", e); raise
print("EXP", [o.name for o in props], r, out, os.path.getsize(out))
