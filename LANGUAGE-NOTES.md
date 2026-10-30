# LANGUAGE-NOTES — the Godot shading language (Assignment 5)

Written by Zhaohui Li, in my own words. Claude Code checked that each line reference points where
it says and typed the answers into this file as I wrote them; it did not write the answers.
Questions 1–5 were written in English by me; 6–8 in Chinese by me and translated by Claude (the
Chinese is in the appendix). Where Claude corrected a fact or added a line reference, the answer
says so. Line references are to `godot/shaders/` unless a path is given.

## Part 1 — the generated shader (`standard_generated.gdshader`)

The shader Godot 4.7.2 wrote when Zhaohui converted a StandardMaterial3D (albedo texture, normal
map and roughness texture: the granite files) with **Convert to ShaderMaterial** in the editor.
*Line numbers listed by Claude and checked against the file with a script (`sed -n`); checked
again by Zhaohui against the open file (2026-10-29).*

| Item | Line | The line |
|---|---|---|
| `shader_type` | 3 | `shader_type spatial;` |
| `render_mode` | 4 | `render_mode blend_mix, depth_draw_opaque, cull_back, diffuse_burley, specular_schlick_ggx;` |
| Inspector albedo colour | 6 | `uniform vec4 albedo : source_color;` |
| Inspector normal-map strength | 20 | `uniform float normal_scale : hint_range(-16.0, 16.0);` |
| Albedo sampler and its hints | 7 | `uniform sampler2D texture_albedo : source_color, filter_linear_mipmap, repeat_enable;` |
| Normal-map sampler and its hints | 19 | `uniform sampler2D texture_normal : hint_roughness_normal, filter_linear_mipmap, repeat_enable;` |
| Writes `ALBEDO` | 35 | `ALBEDO = albedo.rgb * albedo_tex.rgb;` |
| Writes `ROUGHNESS` | 43 | `ROUGHNESS = roughness_tex * roughness;` |
| Writes `NORMAL_MAP` | 46 | `NORMAL_MAP = texture(texture_normal, base_uv).rgb;` |

**Annotations** *(Zhaohui's Chinese, below in the appendix, translated by Claude)*:

1. **Generated line 7 vs. my `granite.gdshader:3`.** `source_color` means this texture is read as a
   colour texture, with the matching colour-space handling. Both lines have `source_color` and
   `repeat_enable`, but the generated shader also uses `filter_linear_mipmap`, which means
   sampling uses linear filtering and mipmaps; my shader does not specify this filter mode.
2. **Generated line 19 vs. my `granite.gdshader:5`.** `hint_roughness_normal` means this texture is
   used for roughness- and normal-related data processing, suited to a texture that contains
   roughness and normal information; my `hint_normal` explicitly marks the texture as a normal
   map. The difference is the purpose of the hint: the generated shader uses the more specialised
   roughness-normal hint, while my shader only uses the normal hint.

   *Correction by Claude (Zhaohui asked Claude to finish this item):* the texture under
   `hint_roughness_normal` holds only normal data, not roughness. In Godot 4.7.2 (editor only,
   `drivers/gles3/storage/material_storage.cpp:953-967`) it does what `hint_normal` does — lets the
   importer detect a normal map — and also registers this normal map so that, when the material has
   a roughness texture with a `hint_roughness_*` hint (generated line 14), the editor sets that
   roughness texture's `roughness/src_normal` import option to it (the roughness limiter). This
   project's roughness import sets `roughness/mode=1` (Disabled) explicitly, so that did not
   happen here: no `.import` file changed after the conversion.

## Part 2 — questions

### 1. What does `shader_type` decide?

shader_type determines what kind of object a shader applies to and which built-in variables and
rendering features are available. The canvas_item type is used for 2D objects, such as sprites,
and provides variables like COLOR for modifying their appearance. (hurt_flash.gdshader:1)

The spatial type is used for 3D objects and provides 3D material properties such as ALBEDO,
ROUGHNESS, and NORMAL_MAP. Spatial shaders are affected by lighting by default, unless the
unshaded render mode is enabled. (granite.gdshader:1, hint_experiment.gdshader:1)

### 2. Which processor functions did you write, and what if the colour line moved into `vertex()`?

All three shaders use fragment(), which runs once for every pixel covered by the object, allowing
the shader to calculate the final colour and material properties per pixel.
(hurt_flash.gdshader:6, granite.gdshader:17, hint_experiment.gdshader:9)

If the colour calculation in hurt_flash.gdshader were moved into vertex(), it would run only once
per vertex (four vertices for a rectangular Sprite2D), and the resulting colours would be
interpolated across the pixels between them. Since the texture is sampled in fragment(), moving
the colour calculation into vertex() would also mean it could no longer use the texture's sampled
colour in the same way, potentially changing the sprite's appearance. (hurt_flash.gdshader:7)

### 3. Built-ins read and written; which are read-only?

My shaders read only two built-in variables: UV and COLOR. I also use the built-in functions
texture() and mix(), but these are functions, not variables. UV is read-only because it is an
input provided by the rendering engine, while COLOR can be both read and written.
(granite.gdshader:18, hint_experiment.gdshader:11, hurt_flash.gdshader:7)

Two built-ins I write are ALBEDO and ROUGHNESS, which control the surface colour and roughness of
a 3D material. (granite.gdshader:19-20)

### 4. Does each hint change only the Inspector, or also the value the shader receives?

The hints do not all have the same effect. hint_range(...) only controls the Inspector slider
range; it does not change the value received by the shader. In my test, setting the value to 2.0
through code still returned 2.0, and the resulting pixel values followed the extrapolation of mix.
(hurt_flash.gdshader:3, granite.gdshader:9, 13-14; TEST-REPORT, A5)

source_color on a color uniform provides color-aware handling in the Inspector. In my
Compatibility project, it does not change the numeric value received by the shader because the
GLES3 material code does not perform color-space conversion on uniforms. (hurt_flash.gdshader:4,
granite.gdshader:8)

source_color on a texture sampler can affect how sampled color values are decoded. However, in my
Godot 4.7.2 Compatibility renderer experiment, both quads displayed 64 / 128 / 192, rather than
the predicted 137 / 188 / 224 for quad B, which uses the sampler without source_color. The
Compatibility shader decodes ALBEDO regardless of the sampler hint, then encodes it on output,
which explains why the two results were identical in this experiment. (granite.gdshader:3,
hint_experiment.gdshader:4; TEST-REPORT, A5)

hint_normal identifies a texture as a normal map, allowing Godot's texture importer to recognise
and process it accordingly. In the Compatibility renderer, if no texture is bound, it also provides
a default flat normal. (granite.gdshader:5; material_storage.cpp:953, 1029-1030)

filter_nearest changes the texture sampling result by selecting the nearest texel instead of
blending neighboring texels, producing sharp boundaries between the three grey bands.
repeat_enable allows texture coordinates outside the 0–1 range to repeat the texture rather than
clamp at its edges. (hint_experiment.gdshader:4-5, granite.gdshader:3-5)

### 5. Does `hint_range` clamp a value set from code?

My prediction was that hint_range(0.0, 1.0) would not clamp a value set from code, and the
experiment confirmed it: after setting the value to 2.0, the material read back 2.0. The red flash
test was inconclusive because both values produced (254, 0, 0), so the capture script (run by
Claude) repeated the test with a grey flash color. At 1.0, the pixel was (128, 128, 128); at 2.0,
it was (34, 167, 254), matching the extrapolation of mix rather than a clamped result. The blue
channel reaches 254 because the sprite's alpha is 254, limiting the displayed value.
(hurt_flash.gdshader:3; evidence/a5/hurt_flash_grey_1_0.png, hurt_flash_grey_2_0.png)

*Three factual corrections by Claude, at Zhaohui's request to finish the remaining work: "the
shader read back" → "the material read back"; "I repeated the test" → "the capture script (run by
Claude) repeated the test"; the evidence path. The reasoning is unchanged.*

### 6. Which line makes the albedo sample as colour and the normal map as data?

*Zhaohui's answer in Chinese (below), translated by Claude.*

In the generated shader, `source_color` on line 7 makes the albedo texture be treated as colour,
and `hint_roughness_normal` on line 19 is used for the normal texture. In my granite.gdshader the
corresponding lines are line 3 and line 5, but I use `hint_normal`, while the generated shader
uses `hint_roughness_normal`. (standard_generated.gdshader:7, 19; granite.gdshader:3, 5)

### 7. Why can't `fragment()` read what the neighbouring pixel is computing?

*Zhaohui's answer in Chinese (below), translated by Claude; the line references were added by Claude.*

Each pixel in fragment() is computed independently and in parallel, so one pixel cannot directly
read the value a neighbouring pixel is computing. Game state reaches the shader from code through
uniforms; for example, the driver controls how strongly the hurt flash shows by setting
`hurt_amount`. (hurt_flash.gdshader:3, 7; godot/fighter/hurt_flash.gd)

### 8. Two things the Godot shading language provides that plain GLSL does not

*Zhaohui's answer in Chinese (below), translated by Claude; the line references were added by Claude.*

The Godot shading language provides dedicated shader types and rendering interfaces: for example,
you declare the shader type with `shader_type`, and you do not need to write a `main()` function
yourself as in plain GLSL. It also provides Inspector hints such as `hint_range` and
`source_color`, and built-in variables such as `UV` and `ALBEDO`, which make it easier for the
developer to access rendering data and control the material. (hurt_flash.gdshader:1, 3, 4;
granite.gdshader:18, 19)

## Appendix — Zhaohui's original Chinese for the Part 1 annotations and questions 6–8

- **Annotation 1.** Generated line 7 vs. my line 3：source_color 表示这张纹理会按颜色纹理读取，并进行相应
  的颜色空间处理。两者都有 source_color 和 repeat_enable，但生成的 shader 额外使用了
  filter_linear_mipmap，表示采样时使用线性过滤和 mipmap；我的 shader 没有指定这个过滤方式。
- **Annotation 2.** Generated line 19 vs. my line 5：hint_roughness_normal 表示这张纹理用于粗糙度和法线
  相关的数据处理，适合包含粗糙度与法线信息的纹理；我的 hint_normal 则明确将纹理标记为法线贴图。两者的
  区别在于提示用途不同，生成的 shader 使用更专门的 roughness-normal 提示，而我的 shader 只使用
  normal 提示。

- **6.** 生成的 shader 中，第 7 行的 source_color 让 Albedo 纹理按颜色处理，第 19 行的
  hint_roughness_normal 用于法线纹理。我的 granite.gdshader 中对应的是第 3 行和第 5 行，不过我使用的
  是 hint_normal，而生成的 shader 使用的是 hint_roughness_normal。
- **7.** fragment() 中的每个像素都是独立并行计算的，因此一个像素无法直接读取旁边像素正在计算的值。
  游戏状态通过 uniform 从代码传入 shader，例如 driver 通过设置 hurt_amount 来控制受伤闪烁的程度。
- **8.** Godot 着色语言提供了专门的 shader 类型和渲染接口，例如使用 shader_type 声明 shader 类型，不
  需要像普通 GLSL 那样自己编写 main() 函数。另外，它还提供了 hint_range、source_color 等 Inspector
  提示，以及 UV、ALBEDO 等内置变量，让开发者可以更方便地访问渲染数据和控制材质。
