# PROP-LANTERN: the code Claude Code ran through the Blender MCP (execute_blender_code)
# in Zhaohui's live Blender 5.2.2 on 2026-10-16, copied verbatim, one block per call.
# Call 1 started from the default scene (Cube, Light, Camera); call 2 saved the file.
# See FRICTIONAL.md "PROP-LANTERN built". To re-run it headless into a scratch file, see
# tools/blender/reproduce.py (it substitutes the save path).

# ---- call 1 of 2: clear the default meshes, build six parts, join, apply ----
import bpy, bmesh
from mathutils import Matrix, Vector

# clear the default scene meshes
for o in [o for o in bpy.data.objects if o.type == 'MESH']:
    bpy.data.objects.remove(o, do_unlink=True)
for m in list(bpy.data.meshes):
    if m.users == 0: bpy.data.meshes.remove(m)

def srgb_to_lin(c):
    return c/12.92 if c <= 0.04045 else ((c+0.055)/1.055)**2.4

def make_mat(name, hexcol):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    h = hexcol.lstrip('#')
    rgb = [srgb_to_lin(int(h[i:i+2],16)/255) for i in (0,2,4)]
    bsdf.inputs["Base Color"].default_value = (*rgb, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.8
    mat.diffuse_color = (*rgb, 1.0)
    return mat

def part(name, kind, mat, loc, size=None, segs=None, r1=None, r2=None, depth=None):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    if kind == 'cube':
        bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    else:
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segs,
                              radius1=r1, radius2=r2, depth=depth)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    bmesh.ops.translate(bm, vec=Vector(loc), verts=bm.verts)
    bm.to_mesh(me); bm.free()
    me.materials.append(mat)
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob

stone = make_mat("Stone_6E6680", "#6E6680")
panel = make_mat("LitPanel_F5C542", "#F5C542")
roof  = make_mat("Roof_4E475C", "#4E475C")

parts = [
    part("base",   'cyl',  stone, (0,0,0.075), segs=8, r1=0.30, r2=0.30, depth=0.15),
    part("shaft",  'cyl',  stone, (0,0,0.425), segs=8, r1=0.09, r2=0.09, depth=0.55),
    part("firebox",'cube', stone, (0,0,0.85),  size=(0.36,0.36,0.30)),
    part("panel",  'cube', panel, (0,-0.185,0.85), size=(0.20,0.02,0.18)),
    part("roof",   'cone', roof,  (0,0,1.125), segs=6, r1=0.30, r2=0.0, depth=0.25),
    part("finial", 'cone', roof,  (0,0,1.325), segs=6, r1=0.05, r2=0.0, depth=0.15),
]
for p in parts:
    p.data.calc_loop_triangles()
    print(p.name, len(p.data.vertices), "verts", len(p.data.loop_triangles), "tris", [round(d,3) for d in p.dimensions])

# join into one object
bpy.ops.object.select_all(action='DESELECT')
for p in parts: p.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
ob = bpy.context.active_object
ob.name = "PROP-LANTERN"; ob.data.name = "PROP-LANTERN"
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
ob.data.calc_loop_triangles()
xs=[v.co for v in ob.data.vertices]
print("joined", ob.name, "tris", len(ob.data.loop_triangles), "dims", [round(d,4) for d in ob.dimensions],
      "minZ", round(min(v.z for v in xs),4), "loc", tuple(ob.location), "rot", tuple(ob.rotation_euler), "scale", tuple(ob.scale),
      "mats", [m.name for m in ob.data.materials])

# ---- call 2 of 2: save ----
import bpy, os
d = r"D:\courses\7270\walker-dusk-duel-zhaohui-li\blender"
os.makedirs(d, exist_ok=True)
p = os.path.join(d, "prop_lantern.blend")
bpy.ops.wm.save_as_mainfile(filepath=p)
print(bpy.data.filepath, os.path.getsize(p))
