# Print the numbers the A3 brief checks for every mesh in a .blend: size, lowest point, location,
# rotation, scale, triangle count, materials, and a fingerprint of the vertex positions (used by
# reproduce.py to compare a re-run against the committed file). From the repo root:
#   /d/blender/blender.exe -b blender/prop_taiko.blend --factory-startup --python-exit-code 1 \
#       --python tools/blender/check_blend.py
import bpy, hashlib

def fingerprint(ob):
    pts = sorted(tuple(round(c, 4) + 0.0 for c in ob.matrix_world @ v.co) for v in ob.data.vertices)
    return hashlib.sha1(repr(pts).encode()).hexdigest()[:12]

for o in bpy.data.objects:
    if o.type != 'MESH':
        continue
    o.data.calc_loop_triangles()
    ws = [o.matrix_world @ v.co for v in o.data.vertices]
    print("CHK", bpy.path.basename(bpy.data.filepath), o.name, [round(d, 3) for d in o.dimensions],
          "minZ", round(min(v.z for v in ws), 4), "loc", tuple(round(c, 3) for c in o.location),
          "rot", tuple(round(a, 3) for a in o.rotation_euler), "scale", tuple(o.scale),
          "tris", len(o.data.loop_triangles), "mats", [m.name for m in o.data.materials],
          "verts", fingerprint(o))
