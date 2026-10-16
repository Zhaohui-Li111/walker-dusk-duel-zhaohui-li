# PROP-TAIKO: the code Claude Code ran through the Blender MCP (execute_blender_code)
# in Zhaohui's live Blender 5.2.2 on 2026-10-16, copied verbatim, one block per call.
# Call 1 ran in the scene left by build_makiwara.py (makiwara already saved). Call 2 is the
# fix for failure case 3: after the join the origin sat at Z 0.03 (the base bar's centre).
# See FRICTIONAL.md "PROP-TAIKO built". Headless re-run: tools/blender/reproduce.py.

# ---- call 1 of 2: build six parts as rotated objects, apply, join, apply, save ----
import bpy, bmesh, os, math
from mathutils import Vector

for o in [o for o in bpy.data.objects if o.type == 'MESH']:
    bpy.data.objects.remove(o, do_unlink=True)
for coll in (bpy.data.meshes, bpy.data.materials):
    for x in list(coll):
        if x.users == 0: coll.remove(x)

def srgb_to_lin(c):
    return c/12.92 if c <= 0.04045 else ((c+0.055)/1.055)**2.4
def make_mat(name, hexcol):
    mat = bpy.data.materials.new(name); mat.use_nodes = True
    bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    h = hexcol.lstrip('#'); rgb = [srgb_to_lin(int(h[i:i+2],16)/255) for i in (0,2,4)]
    bsdf.inputs["Base Color"].default_value = (*rgb, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.8
    mat.diffuse_color = (*rgb, 1.0)
    return mat
def part(name, kind, mat, loc, rot=(0,0,0), size=None, segs=None, r=None, depth=None):
    # geometry built centred on the object's origin; position/rotation go on the object
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    if kind == 'cube':
        bmesh.ops.create_cube(bm, size=1.0); bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    else:
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segs, radius1=r, radius2=r, depth=depth)
    bm.to_mesh(me); bm.free(); me.materials.append(mat)
    ob = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(ob)
    ob.location = loc; ob.rotation_euler = [math.radians(a) for a in rot]
    return ob

lacq = make_mat("Lacquer_D9482B", "#D9482B")
head = make_mat("Head_F2E6D0", "#F2E6D0")
stand = make_mat("Stand_1E1B22", "#1E1B22")
lean = math.degrees(math.atan2(0.10, 0.39))
parts = [
    part("base_bar", 'cube', stand, (0,0,0.03), size=(0.70,0.12,0.06)),
    part("drum_body",'cyl',  lacq,  (0,0,0.62), rot=(90,0,0), segs=12, r=0.30, depth=0.51),
    part("head_front",'cyl', head,  (0,-0.265,0.62), rot=(90,0,0), segs=12, r=0.33, depth=0.02),
    part("head_back", 'cyl', head,  (0, 0.265,0.62), rot=(90,0,0), segs=12, r=0.33, depth=0.02),
    part("leg_left",  'cube', stand, (-0.25,0,0.225), rot=(0, lean,0), size=(0.06,0.10,0.42)),
    part("leg_right", 'cube', stand, ( 0.25,0,0.225), rot=(0,-lean,0), size=(0.06,0.10,0.42)),
]
bpy.context.view_layer.update()
for p in parts:
    p.data.calc_loop_triangles()
    print(p.name, len(p.data.loop_triangles), "tris rot", [round(math.degrees(a),1) for a in p.rotation_euler], "dims", [round(d,3) for d in p.dimensions])
print("drum body before apply: rotation X =", round(math.degrees(parts[1].rotation_euler.x),1))
bpy.ops.object.select_all(action='DESELECT')
for p in parts: p.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)  # bake each part's rotation
print("after per-part apply:", [(p.name, [round(math.degrees(a),1) for a in p.rotation_euler]) for p in parts])
bpy.ops.object.join()
ob = bpy.context.active_object
ob.name = "PROP-TAIKO"; ob.data.name = "PROP-TAIKO"
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
me = ob.data; me.calc_loop_triangles()
vs = [v.co for v in me.vertices]
print("joined tris", len(me.loop_triangles), "dims", [round(d,4) for d in ob.dimensions],
      "x", round(min(v.x for v in vs),4), round(max(v.x for v in vs),4),
      "y", round(min(v.y for v in vs),4), round(max(v.y for v in vs),4),
      "z", round(min(v.z for v in vs),4), round(max(v.z for v in vs),4),
      "rot", tuple(ob.rotation_euler), "scale", tuple(ob.scale), "lean", round(lean,2))
p = r"D:\courses\7270\walker-dusk-duel-zhaohui-li\blender\prop_taiko.blend"
bpy.ops.wm.save_as_mainfile(filepath=p)
print(bpy.data.filepath, os.path.getsize(p))

# ---- call 2 of 2: move the origin to the underside centre (mesh was Z -0.03..0.92), save ----
import bpy, os
from mathutils import Matrix
ob = bpy.data.objects["PROP-TAIKO"]
print("before: location", tuple(round(c,4) for c in ob.location))
# move the origin to the centre of the underside: bake the object offset into the mesh
ob.data.transform(Matrix.Translation(ob.location))
ob.location = (0,0,0)
ob.data.update(); bpy.context.view_layer.update()
vs = [v.co for v in ob.data.vertices]
print("after: location", tuple(ob.location), "z", round(min(v.z for v in vs),4), round(max(v.z for v in vs),4),
      "x", round(min(v.x for v in vs),4), round(max(v.x for v in vs),4),
      "y", round(min(v.y for v in vs),4), round(max(v.y for v in vs),4))
ws = [ob.matrix_world @ v.co for v in ob.data.vertices]
print("world minZ", round(min(v.z for v in ws),4))
bpy.ops.wm.save_mainfile()
print(bpy.data.filepath, os.path.getsize(bpy.data.filepath))

# ---- hand edit by Zhaohui (mouse, Edit Mode, saved 16:28) — not code ----
# The saved file showed: lacquer body moved by (-0.0053, +0.0023, +0.0117) m; front drumhead's
# outer ring moved onto the inner plane (0 m thick, z-fighting with the body cap) and its inner
# ring scrambled (two vertices doubled). Zhaohui asked Claude to repair it ("我不太会改，你改吧").
# Re-running this file headless therefore does NOT reproduce the body offset; see FRICTIONAL.md.

# ---- call 3 of 4 (Claude, repair, partial): move the front head's outer cap back to y -0.275 ----
import bpy, bmesh
from mathutils import Vector
ob = bpy.data.objects["PROP-TAIKO"]
if ob.mode != 'OBJECT':
    bpy.ops.object.mode_set(mode='OBJECT')
me = ob.data
head_idx = me.materials.find("Head_F2E6D0")
bm = bmesh.new(); bm.from_mesh(me)
bm.faces.ensure_lookup_table()
# the front head's caps: Head-material n-gons whose centre is on the front (y < 0)
caps = [f for f in bm.faces if f.material_index == head_idx and len(f.verts) == 12 and f.calc_center_median().y < 0]
for f in caps:
    print("front head cap: normal", tuple(round(c,3) for c in f.normal), "y", round(f.calc_center_median().y,4))
outer = [f for f in caps if f.normal.y < -0.5]
inner = [f for f in caps if f.normal.y > 0.5]
print("outer caps", len(outer), "inner caps", len(inner))
assert len(outer) == 1 and len(inner) == 1, "cannot tell the outer face from the inner one"
for v in outer[0].verts:
    v.co.y = -0.275
bm.to_mesh(me); bm.free(); me.update()
vs = [v.co for v in me.vertices]
print("dims", [round(d,4) for d in ob.dimensions], "y", round(min(v.y for v in vs),4), round(max(v.y for v in vs),4),
      "loc", tuple(ob.location), "rot", tuple(ob.rotation_euler), "scale", tuple(ob.scale))
bpy.ops.wm.save_mainfile()
print("saved", bpy.data.filepath)

# ---- call 4 of 4 (Claude, repair): put all 24 front-head vertices back on the 12-gon ----
import bpy, math
ob = bpy.data.objects["PROP-TAIKO"]
if ob.mode != 'OBJECT':
    bpy.ops.object.mode_set(mode='OBJECT')
me = ob.data
# front drumhead = vertices 32..55 (topology unchanged from the committed file):
# even index = inner ring (y -0.255), odd = outer ring (y -0.275), 12-gon r 0.33 centred at z 0.62
for k in range(12):
    x = 0.33 * math.sin(math.radians(30 * k))
    z = 0.62 + 0.33 * math.cos(math.radians(30 * k))
    me.vertices[32 + 2*k].co = (x, -0.255, z)
    me.vertices[33 + 2*k].co = (x, -0.275, z)
me.update()
bpy.context.view_layer.update()
vs = [v.co for v in me.vertices]
print("dims", [round(d,4) for d in ob.dimensions], "z", round(min(v.z for v in vs),4), round(max(v.z for v in vs),4),
      "loc", tuple(ob.location), "rot", tuple(ob.rotation_euler), "scale", tuple(ob.scale))
bpy.ops.wm.save_mainfile()
print("saved", bpy.data.filepath)
