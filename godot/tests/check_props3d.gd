extends SceneTree
## Headless checks for the A3 3D props against CHANGE-BRIEF.md. Run from the repo root:
##   godot --headless --path godot --script res://tests/check_props3d.gd
## For each prop in props3d/prop_room.tscn it prints the AABB size and min Y, the scale and
## rotation of every node, the tallest axis, the triangle count and each surface's albedo hex.
## Exit code 0 = all passed.

const TOL := 0.02
const PROPS := {
	"PROP-LANTERN": {"size": Vector3(0.60, 1.40, 0.60), "tris": 150,
		"colours": ["6e6680", "f5c542", "4e475c"]},
	"PROP-MAKIWARA": {"size": Vector3(0.30, 1.50, 0.30), "tris": 120,
		"colours": ["8a5a3b", "d8b676", "f2e6d0", "6e6680"]},
	"PROP-TAIKO": {"size": Vector3(0.70, 0.95, 0.55), "tris": 200,
		"colours": ["d9482b", "f2e6d0", "1e1b22"]},
}
var failures := 0
var checks := 0


func _initialize() -> void:
	create_timer(30.0).timeout.connect(func(): print("TIMEOUT after 30 s"); quit(2))
	_run.call_deferred()


func _run() -> void:
	var room: Node3D = load("res://props3d/prop_room.tscn").instantiate()
	root.add_child(room)
	await process_frame
	for prop_name in PROPS:
		var spec: Dictionary = PROPS[prop_name]
		var prop := room.get_node(prop_name) as Node3D
		print("- ", prop_name)
		var meshes: Array[MeshInstance3D] = []
		_collect(prop, meshes)
		check(meshes.size() > 0, "has a mesh")
		# transforms: every node under the prop, prop root included
		for n in [prop] + _descendants(prop):
			if n is Node3D:
				var s: Vector3 = n.scale
				var r: Vector3 = n.rotation_degrees
				print("    node %-16s scale %s rot %s" % [n.name, s, r])
				check(s.is_equal_approx(Vector3.ONE), "%s scale is 1,1,1" % n.name)
				check(r.length() < 0.01, "%s rotation is 0,0,0" % n.name)
		# world AABB, relative to where the prop was placed
		var box := AABB()
		var tris := 0
		var hexes := []
		for i in meshes.size():
			var mi := meshes[i]
			var b := mi.global_transform * mi.get_aabb()
			box = b if i == 0 else box.merge(b)
			for si in mi.mesh.get_surface_count():
				var arr := mi.mesh.surface_get_arrays(si)
				var idx: PackedInt32Array = arr[Mesh.ARRAY_INDEX]
				var nverts: int = (arr[Mesh.ARRAY_VERTEX] as PackedVector3Array).size()
				tris += (idx.size() if idx.size() > 0 else nverts) / 3
				var mat := mi.get_active_material(si)
				if mat is BaseMaterial3D:
					hexes.append((mat as BaseMaterial3D).albedo_color.to_html(false))
				else:
					hexes.append("(no BaseMaterial3D)")
		var size := box.size
		var min_y := box.position.y - prop.global_position.y
		print("    size %.3f x %.3f x %.3f (x, y, z)  min y %.4f  tris %d  albedo %s"
				% [size.x, size.y, size.z, min_y, tris, hexes])
		for axis in 3:
			check(absf(size[axis] - spec.size[axis]) <= TOL,
					"size axis %d = %.3f, brief %.2f" % [axis, size[axis], spec.size[axis]])
		check(absf(min_y) <= 0.01, "min y %.4f is 0.00 +- 0.01" % min_y)
		var tallest := 0 if size.x >= size.y and size.x >= size.z else (1 if size.y >= size.z else 2)
		check(tallest == 1, "tallest axis is Y")
		check(tris > 0 and tris <= spec.tris, "%d triangles within budget %d" % [tris, spec.tris])
		for c in spec.colours:
			check(c in hexes, "albedo #%s present" % c)
	print("%d checks, %d failed" % [checks, failures])
	quit(1 if failures > 0 else 0)


func check(ok: bool, what: String) -> void:
	checks += 1
	if not ok:
		failures += 1
		print("    FAIL: ", what)


func _collect(n: Node, out: Array[MeshInstance3D]) -> void:
	if n is MeshInstance3D:
		out.append(n)
	for c in n.get_children():
		_collect(c, out)


func _descendants(n: Node) -> Array:
	var out := []
	for c in n.get_children():
		out.append(c)
		out += _descendants(c)
	return out
