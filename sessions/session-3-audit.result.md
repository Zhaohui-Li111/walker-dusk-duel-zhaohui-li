I wrote `godot/MATERIALS.md` and `godot/tests/test_materials.gd`. The test passes: **96 checks, 0 failed**, exit code 0 and no `SCRIPT ERROR` or `SHADER ERROR`. The full output is above and in `logs/test_materials_60fps.log`. I didn't change any shader, material, scene or `.import` file, and I haven't committed anything.

The first run had one failure and a script error, both bugs in my test rather than the project. A material embedded in a scene has a path like `prop_room.tscn::Mat_floor`, not an empty one. And comparing vertex normals exactly found no matches, so I switched to an angle check. After those fixes, every check that pins a brief value passed without any expectation being adjusted.

**What matches the brief:**
- Uniform names, types, hints, defaults and groups, in both shaders.
- All five texture import rows.
- The plinth tint is exactly #6E6680, and both granite materials use the same shader path.
- Every `material_override` points to a `.tres` file.
- The normal maps: `granite_wall_nor_gl_1k.png` scores 0.3545 as OpenGL and 1.6455 as DirectX; the dx file scores the other way round.

**Findings (details and file lines in MATERIALS.md):**
1. **The floor texture is stretched 2.25 : 1.** A BoxMesh gives each face a third × a half of the texture whatever the face's size, and `uv_scale` applies one number to both directions. On the floor, one copy of the texture covers 3.0 m along X but only 1.33 m along Z.
2. **The plinth is stretched too:** 1.5 : 1 on top and 4 : 1 on its sides. Each face shows about a third × a half of the texture, not the "about once" in the brief's "What differs" line. That contradicts the brief's own UV note.
3. **The grain is a different size on the floor and the plinth.**
4. **The floor's mesh still has its old built-in material,** hidden under the granite override and never drawn. CLAUDE.md's "today the floor's material is an embedded StandardMaterial3D" is out of date.
5. **Each hint-experiment material binds a sampler it never reads.** Both bind the grey PNG to both samplers, and `read_as_color` picks which one is sampled. I haven't checked whether GL Compatibility can treat one texture as colour on one sampler and as data on the other. If quads A and B measure the same, look here first.
6. **Smaller notes:**
   - The roughness map stores three compressed channels and only red is read. That is what the brief's import table asks for.
   - The compressed textures were imported for desktop formats only, while `project.godot` also sets Compatibility for mobile.
   - The prop room's reflections come from the purple background, so at `roughness_scale` 0 the glossy highlight will look purple, not white.

The attribution section uses only the Poly Haven facts from the brief (source, author, licence, file source, date checked, pointer to `ATTRIBUTION.md`).

**What the headless test cannot establish:**
- Anything on screen, because the dummy renderer draws nothing: the hint experiment's measured greys, how the granite looks under the Sun, whether the stretching is noticeable, and the purple highlight.
- How the GPU samples the compressed textures. The curl ratio is computed from the source PNGs, not from what the GPU samples.
- Whether the Compatibility renderer converts colour for `source_color` the way the hint predictions assume.
- I also didn't do the brief's "delete `godot/.godot` and reimport" step for failure case 7, since it wipes the import cache. The test ran against the current one.

All of these need a windowed capture.

`git status` shows three new files: `godot/MATERIALS.md`, `godot/tests/test_materials.gd` and `logs/test_materials_60fps.log`. Your earlier `prop_taiko.blend` change is still uncommitted and untouched.