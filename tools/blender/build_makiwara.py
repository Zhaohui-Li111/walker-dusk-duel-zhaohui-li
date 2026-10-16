# PROP-MAKIWARA: the code Claude Code ran through the Blender MCP (execute_blender_code)
# in Zhaohui's live Blender 5.2.2 on 2026-10-16, copied verbatim, one block per call.
# Call 1 ran in the scene left by build_lantern.py (lantern already saved); call 2 is the
# revision Zhaohui chose after looking (chamfered rope bands). See FRICTIONAL.md
# "PROP-MAKIWARA built" and "rope bands reshaped". Headless re-run: tools/blender/reproduce.py.

# ---- call 1 of 2: build five parts, join, apply, save ----
import bpy, bmesh, os
from mathutils import Vector

for o in [o for o in bpy.data.objects if o.type == 'MESH']:
    bpy.data.objects.remove(o, do_unlink=True)
for coll in (bpy.data.meshes, bpy.data.materials):
    for x in list(coll):
        if x.users == 0: coll.remove(x)

def srgb_to_lin(c):
    return c/12.92 if c <= 0.04045 else ((c+0.055)/1.055)**2.4

def make_mat(name, hexcol):
    mat = bpy.data.materials.new(name)
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

wood  = make_mat("Wood_8A5A3B", "#8A5A3B")
straw = make_mat("Straw_D8B676", "#D8B676")
rope  = make_mat("Rope_F2E6D0", "#F2E6D0")
stone = make_mat("Stone_6E6680", "#6E6680")

parts = [
    part("footing", 'cube', stone, (0,0,0.05), size=(0.30,0.30,0.10)),
    part("post",    'cube', wood,  (0,0,0.80), size=(0.12,0.08,1.40)),
    part("pad",     'cube', straw, (0,-0.07,1.20), size=(0.16,0.06,0.30)),
    part("rope_lo", 'cyl',  rope,  (0,-0.03,1.11), segs=8, r1=0.12, r2=0.12, depth=0.03),
    part("rope_hi", 'cyl',  rope,  (0,-0.03,1.29), segs=8, r1=0.12, r2=0.12, depth=0.03),
]
for p in parts:
    p.data.calc_loop_triangles()
    print(p.name, len(p.data.loop_triangles), "tris", [round(d,3) for d in p.dimensions])

bpy.ops.object.select_all(action='DESELECT')
for p in parts: p.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
ob = bpy.context.active_object
ob.name = "PROP-MAKIWARA"; ob.data.name = "PROP-MAKIWARA"
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
ob.data.calc_loop_triangles()
vs=[v.co for v in ob.data.vertices]
print("joined tris", len(ob.data.loop_triangles), "dims", [round(d,4) for d in ob.dimensions],
      "x", round(min(v.x for v in vs),4), round(max(v.x for v in vs),4),
      "y", round(min(v.y for v in vs),4), round(max(v.y for v in vs),4),
      "minZ", round(min(v.z for v in vs),4), "rot", tuple(ob.rotation_euler), "scale", tuple(ob.scale))
p = r"D:\courses\7270\walker-dusk-duel-zhaohui-li\blender\prop_makiwara.blend"
bpy.ops.wm.save_as_mainfile(filepath=p)
print(bpy.data.filepath, os.path.getsize(p))

# ---- call 2 of 2: replace the round rope bands with chamfered 0.19 x 0.17 rings, save ----
import bpy, bmesh, os
from mathutils import Vector

ob = bpy.data.objects["PROP-MAKIWARA"]
mats = {m.name: m for m in ob.data.materials}
me = ob.data
bm = bmesh.new(); bm.from_mesh(me)
rope_idx = me.materials.find("Rope_F2E6D0")
# remove the two round rope bands
rope_faces = [f for f in bm.faces if f.material_index == rope_idx]
rope_verts = {v for f in rope_faces for v in f.verts}
bmesh.ops.delete(bm, geom=list(rope_verts), context='VERTS')

hx, hy, cx, cy = 0.095, 0.085, 0.0, -0.03
c = 0.02  # chamfer
ring = [( hx, hy-c), ( hx-c, hy), (-hx+c, hy), (-hx, hy-c),
        (-hx,-hy+c), (-hx+c,-hy), ( hx-c,-hy), ( hx,-hy+c)]
def band(zc, h=0.03):
    lo = [bm.verts.new((cx+x, cy+y, zc-h/2)) for x,y in ring]
    hi = [bm.verts.new((cx+x, cy+y, zc+h/2)) for x,y in ring]
    fs = [bm.faces.new((lo[i], lo[(i+1)%8], hi[(i+1)%8], hi[i])) for i in range(8)]
    fs.append(bm.faces.new(list(reversed(lo))))
    fs.append(bm.faces.new(hi))
    for f in fs: f.material_index = rope_idx
    return fs
new = band(1.11) + band(1.29)
bmesh.ops.recalc_face_normals(bm, faces=new)
bm.to_mesh(me); bm.free(); me.update()
me.calc_loop_triangles()
vs = [v.co for v in me.vertices]
# corner clearance check: pad/post corners (±0.08, -0.10 / 0.04) inside x+|y-cy| <= hx+hy-c
corner = 0.08 + 0.07
print("chamfer sum", hx+hy-c, "box corner sum", corner)
print("tris", len(me.loop_triangles), "faces", len(me.polygons), "dims", [round(d,4) for d in ob.dimensions],
      "minZ", round(min(v.z for v in vs),4), "rot", tuple(ob.rotation_euler), "scale", tuple(ob.scale))
rv = [v.co for v in me.vertices if v.co.z > 1.0 and v.co.z < 1.4 and abs(v.co.x) > 0.081]
print("rope x span", round(min(v.x for v in rv),3), round(max(v.x for v in rv),3),
      "y span", round(min(v.y for v in rv),3), round(max(v.y for v in rv),3))
bpy.ops.wm.save_mainfile()
print(bpy.data.filepath, os.path.getsize(bpy.data.filepath))
