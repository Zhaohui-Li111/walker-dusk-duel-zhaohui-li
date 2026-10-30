# MATERIALS — audit of the A5 materials

Audited 2026-10-29 by Claude Code from the files as committed at `7863c1f`. Nothing below was
changed by the audit. Each row is pinned by `godot/tests/test_materials.gd`
(`./scripts/run-test.sh test_materials.gd 60`, log `logs/test_materials_60fps.log`).
Paths are relative to `godot/`.

## Materials

| Material | Shader | Uniform values set | Textures bound |
|---|---|---|---|
| `props3d/materials/granite_floor.tres` | `shaders/granite.gdshader` | `tint` = `Color(1, 1, 1, 1)` (#FFFFFF), `uv_scale` = 6.0, `roughness_scale` = 1.0, `normal_strength` = 1.0 (`:14-17`) | `albedo_texture` → `granite_wall_diff_1k.png`, `roughness_texture` → `granite_wall_rough_1k.png`, `normal_texture` → `granite_wall_nor_gl_1k.png` (`:11-13`) |
| `props3d/materials/granite_plinth.tres` | `shaders/granite.gdshader` | `tint` = `Color(0.43137255, 0.4, 0.5019608, 1)` (#6E6680), `uv_scale` = 1.0, `roughness_scale` = 1.0, `normal_strength` = 1.0 (`:14-17`) | same three textures (`:11-13`) |
| `hint_experiment/hint_as_color.tres` | `shaders/hint_experiment.gdshader` | `read_as_color` = true (`:11`) | `grey_as_color` and `grey_as_data` → `hint_experiment/hint_grey_3x1.png` (`:9-10`) |
| `hint_experiment/hint_as_data.tres` | `shaders/hint_experiment.gdshader` | `read_as_color` = false (`:11`) | `grey_as_color` and `grey_as_data` → `hint_experiment/hint_grey_3x1.png` (`:9-10`) |

All four set every uniform their shader declares; none relies on a shader default. All four use
`render_priority = 0`.

Wiring: `prop_room.tscn` `Floor` and `StonePlinth` take the two granite files as
`material_override` (`props3d/prop_room.tscn:43`, `:48`); `hint_experiment.tscn`
`QuadA_source_color` and `QuadB_no_hint` take the two hint files (`hint_experiment/hint_experiment.tscn:35`, `:40`).
Every path is a `.tres` file, not an embedded sub-resource.

## Uniforms and samplers

### `shaders/granite.gdshader` (`shader_type spatial;`, no `render_mode`)

Non-sampler uniforms, as written:

| Group | Uniform | Type | Hint | Default | Line |
|---|---|---|---|---|---|
| `surface` | `tint` | `vec4` | `source_color` | `vec4(1.0, 1.0, 1.0, 1.0)` | `:8` |
| `surface` | `uv_scale` | `float` | `hint_range(0.25, 8.0)` | `1.0` | `:9` |
| `detail` | `roughness_scale` | `float` | `hint_range(0.0, 1.0)` | `1.0` | `:13` |
| `detail` | `normal_strength` | `float` | `hint_range(0.0, 2.0)` | `1.0` | `:14` |

These match the uniform table confirmed in CHANGE-BRIEF Revision 3.

Samplers (import settings: `compress/mode`, `compress/normal_map`, `mipmaps/generate`):

| Sampler | Hints as written | Floor binds | Plinth binds | Import settings | Line |
|---|---|---|---|---|---|
| `albedo_texture` | `source_color, repeat_enable` | `granite_wall_diff_1k.png` | same | 2 (VRAM Compressed), 2 (Disabled), true | `:3` |
| `roughness_texture` | `repeat_enable` | `granite_wall_rough_1k.png` | same | 2 (VRAM Compressed), 2 (Disabled), true | `:4` |
| `normal_texture` | `hint_normal, repeat_enable` | `granite_wall_nor_gl_1k.png` | same | 2 (VRAM Compressed), 1 (Enable), true | `:5` |

Not bound by any material: `granite_wall_nor_dx_1k.png`, 0 (Lossless), 2 (Disabled), false;
calibration only, as the brief says.

*Review (Claude, 2026-10-29), measured with `load(...).get_image().get_format()` after import:*
diff and rough are `FORMAT_DXT1` (17), compressed, with mipmaps; nor_gl is `FORMAT_RGTC_RG` (21),
compressed, with mipmaps; nor_dx is `FORMAT_RGB8` (4), uncompressed, no mipmaps.

### `shaders/hint_experiment.gdshader` (`shader_type spatial;`, `render_mode unshaded;`)

| Uniform | Type | Hints as written | Default | `hint_as_color` binds / sets | `hint_as_data` binds / sets | Import settings | Line |
|---|---|---|---|---|---|---|---|
| `grey_as_color` | `sampler2D` | `source_color, filter_nearest` | — | `hint_grey_3x1.png` | `hint_grey_3x1.png` | 0 (Lossless), 2 (Disabled), false | `:4` |
| `grey_as_data` | `sampler2D` | `filter_nearest` | — | `hint_grey_3x1.png` | `hint_grey_3x1.png` | same file | `:5` |
| `read_as_color` | `bool` | — | `true` | true | false | — | `:7` |

All five import rows match the table in the CHANGE-BRIEF A5 material plan.
`get_shader_uniform_list()` returns all seven granite uniforms (samplers type 24 Object, `tint`
type 20 Color, the floats type 3) and all three hint uniforms (samplers 24, `read_as_color`
type 1 Bool), so both shaders parse.

## Lights and environment

| Scene | Setting | Value | Evidence |
|---|---|---|---|
| `props3d/prop_room.tscn` | Tonemap | Linear (0), exposure 1.0 — Godot defaults, not written in the file | `:28-33`; read from the loaded `Environment` |
| | Background | Colour (1), #5A4766 | `:29-30` |
| | Ambient light | source Colour (2), #8C8599, energy 0.35 | `:31-33` |
| | Reflected light | source Background (0), the default, not written in the file | read from the loaded `Environment` |
| | Glow, fog, SSAO, adjustments | all off (defaults) | read from the loaded `Environment` |
| | `Sun` (only light) | DirectionalLight3D, energy 0.7, colour white, shadows on, rotation (−50°, 30°, 0°) | `:50-53` |
| `hint_experiment/hint_experiment.tscn` | Tonemap | Linear (0), exposure 1.0 | `:11-12` |
| | Background | Colour (1), #1A1A1A | `:7-8` |
| | Ambient / reflected light | both Disabled (1) | `:9-10` |
| | Glow, fog, volumetric fog, adjustments | off | `:13-16` |
| | Lights | none (the quads are `unshaded`) | — |

Project: `renderer/rendering_method="gl_compatibility"`, also for mobile (`project.godot:35-36`);
`hdr_2d` not set.

## Findings

1. **The floor's granite is stretched 2.25 : 1.** A `BoxMesh` maps each face to a third × a half of
   the UV square whatever the face's size, and `uv_scale` is one float applied to both axes
   (`granite.gdshader:18`). On the 6 × 4 m top face at `uv_scale` 6.0 one copy of the texture
   covers **3.000 m along X and 1.333 m along Z**. `make_granite_materials.gd:11-13` says "2 x 3"
   copies but not that they are not square. Test line: `Floor face (0.0, 1.0, 0.0) at uv_scale
   6.0: 3.000 m per copy along X, 1.333 m along Z (stretch 2.25 : 1)`.
2. **The plinth is stretched too, worst on its sides,** and **does not show the texture "about
   once".** Top face: 2.400 m × 1.600 m per copy (1.50 : 1); +Z side (0.8 × 0.3 m): 2.400 m along X,
   0.600 m along Y (4.00 : 1). Each face shows about a third × a half of the texture. That agrees
   with the brief's own UV note ("each face shows about a third by a half of the texture at
   `uv_scale = 1`") but not with its "What differs" line ("the 0.8 m plinth about once").
3. **The grain is a different size on the floor and the plinth** (floor 3.0 / 1.33 m per copy;
   plinth top 2.4 / 1.6 m; plinth sides 2.4 / 0.6 m), so granite sitting on granite may not read as
   the same stone. Only a capture can say whether it matters.
4. **Unused material on the floor mesh.** `Mesh_floor` still has `material =
   SubResource("Mat_floor")`, a StandardMaterial3D (`prop_room.tscn:9-11`, `:14`), which the
   `material_override` hides. It is dead data (the audit's "costs nothing at draw time" was removed in review: nobody
   measured it), and CLAUDE.md's line
   "Today the floor's material is an embedded `StandardMaterial3D`" is out of date: the override
   is now in place (`prop_room.tscn:43`).
5. **Each hint material binds a sampler it never reads.** Both materials bind `hint_grey_3x1.png` to
   both samplers (`hint_as_color.tres:9-10`, `hint_as_data.tres:9-10`); the shader samples only
   one, chosen by `read_as_color` (`hint_experiment.gdshader:10-14`). Harmless, but it means one
   texture is bound under two different hints in the same draw. This audit has not checked whether
   GL Compatibility can decode one texture as sRGB on one sampler and not on the other; the
   window measurement answers that, and a result where A and B are the same would point here first.
6. **The roughness map is stored as DXT1 (`get_format()` = 17, three channels) and only `.r` is
   read** (`granite.gdshader:20`; `granite_wall_rough_1k.png.import:19`, `:8` `s3tc_bptc`).
   Wasteful, but it is what the brief's import table asks for.
7. **Desktop-only VRAM formats.** The three VRAM-compressed textures were imported for
   `s3tc_bptc` only (`.import:8` of each), while `project.godot:36` sets Compatibility for mobile
   as well. A mobile export would need ETC2/ASTC imports. Not a problem for this assignment, which
   runs on desktop.
8. **Reflections are set to come from the purple background.** `reflected_light_source` is left at
   Background (0) in the prop room (read from the loaded `Environment`), so specular reflections
   are expected to take the #5A4766 background colour. *Review: this is a prediction, not a
   measurement; no capture has been taken.* If it holds, it shows at `roughness_scale` 0 ("glossy
   highlight" in the brief's uniform table) as a purple tint; the interface sweep checks it.
9. **Normal maps are in the right convention.** Curl ratio (`tests/normal_map_check.gd`, files
   decoded with `Image.load_from_file` as RGB8, format 4, from 16-bit PNGs):
   `granite_wall_nor_gl_1k.png` 0.3545 as OpenGL, 1.6455 as DirectX; `granite_wall_nor_dx_1k.png`
   the other way round. The material binds the GL file to a `hint_normal` sampler with
   `compress/normal_map` = 1, as planned (brief predicted failures 4 and 5 not seen).
11. *Added in review (Claude, 2026-10-29):* **the normal map is imported as two channels,
    `FORMAT_RGTC_RG` (21).** With `compress/normal_map` = 1 (Enable,
    `granite_wall_nor_gl_1k.png.import`), Godot keeps only X and Y and drops Z. The audit's
    sampler table gave the import setting but not this consequence. Not a fault.
    *Corrected 2026-10-29 (Claude):* this finding first said that `hint_normal` makes the shader
    rebuild Z. That was wrong. In Godot 4.7.2's Compatibility scene shader, Z is rebuilt for
    **every** `NORMAL_MAP` write whatever the hint (`drivers/gles3/shaders/scene.glsl:2359`,
    "always ignore Z, as it can be RG packed"). What `hint_normal` (`granite.gdshader:5`) does
    there is give a flat default normal texture when none is bound
    (`drivers/gles3/storage/material_storage.cpp:1029-1030`) and let the importer detect the file as
    a normal map (`:953`).
10. **No inconsistencies** with the brief in the uniform names, types, hints, defaults or groups,
    the five import rows, the tint (#6E6680 exactly), the shared shader path, or the
    `material_override` wiring (brief predicted failure 7 not seen in the current import cache;
    the brief's "after deleting `godot/.godot` and reimporting" step was not done in this audit).

## Attribution

Granite textures: Poly Haven *Granite Wall*, `https://polyhaven.com/a/granite_wall`. Authors:
Dimitrios Savva (all roles, per the Poly Haven API). Licence: CC0. Files: 1k PNG from
`dl.polyhaven.org`. Date checked: 2026-10-26. Credits and SHA-256 per file:
`godot/props3d/textures/ATTRIBUTION.md`.

`hint_experiment/hint_grey_3x1.png` is written by `hint_experiment/write_hint_png.gd` in this
repository; it has no outside source.
