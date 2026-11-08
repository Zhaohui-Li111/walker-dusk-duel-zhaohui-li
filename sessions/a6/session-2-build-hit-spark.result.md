Effect A 的场景、配置测试和预览都写好了，但配置测试还没通过：**66 项里 65 项通过，1 项失败**。失败的原因是新画的星形 PNG 还没被 Godot 导入。导入要用 `godot --headless --path godot --import`，这次会话里我没有权限执行，只有 `./scripts/run-test.sh` 能跑。

## 新增文件（都没有提交）

- `godot/effects/make_textures.gd`：画一次 8×8 的八角星，存成 `godot/effects/hit_spark_star.png`（这一步已经跑过，PNG 已生成）。
- `godot/effects/hit_spark.tscn`：一个 `CPUParticles2D`。brief 设置表里的每个值都写在这个场景文件里，`emitting = false`，所以加载时不会自己发射。
- `godot/tests/test_hit_spark_config.gd`：加载场景，逐项读回设置。它还检查场景文件里写的每个属性在 4.7.2 里都存在，所以误用 Godot 3 的属性名会在这里失败。
- `godot/previews/hit_spark_preview.tscn` 和 `.gd`：640×360、不加 Camera2D，和游戏里的显示比例一样。`bg.png` 按 1:1 画。四个槽位轮流使用，第 10 帧发射一次；`retrigger` 打开时（默认开）第 22 帧用下一个槽位再发射一次，不会重启第一个爆发。

没有把效果接进游戏，没有动 `main.tscn` / `main.gd`，也没有碰任何 `.gdshader` 文件。

## 需要你确认的几点

- **场景是单个发射器，不是一个根节点下挂四个子节点。** brief 里的四个槽位是同一个发射器的四个副本，不是叠在一起的几层效果。规则 4 要求槽位的父节点是 `Main`，如果中间多一层根节点，"父节点是 `Main`" 这个检查就会失败。所以四个槽位留给后面的控制器去实例化，预览里先由预览脚本实例化。
- **缩放曲线的切线是我选的。** brief 只给了三个点，我用了直线连接。测试里对应的两项写明了"Claude Code's tangent choice"。
- **星形的具体形状是我选的。** brief 只说"中心宽、尖端细"。我用的是外半径 4 px、内半径 1.25 px、尖锐度 3，参数在 `make_textures.gd` 里。
- 所有用到的属性 `ClassDB` 都确认存在，没有拿不准的。附带确认：`CPUParticles2D` 没有 `visibility_rect`，和 brief 写的"不适用"一致。
- 预览还没有运行过，因为它也要用到这张没导入的 PNG。

## 配置测试的实际输出

`./scripts/run-test.sh test_hit_spark_config.gd 60`，退出码 1：

```
Godot Engine v4.7.2.stable.official.ed1daf0bf - https://godotengine.org

-- scene
ERROR: No loader found for resource: res://effects/hit_spark_star.png (expected type: Texture2D)
   at: _load (core/io/resource_loader.cpp:332)
ERROR: res://effects/hit_spark.tscn:20 - Parse Error: [ext_resource] referenced non-existent resource at: res://effects/hit_spark_star.png.
PASS: res://effects/hit_spark.tscn loads as a PackedScene
PASS: scene has one node, the emitter (node count 1)
PASS: root node type is CPUParticles2D (got CPUParticles2D)
-- every property the scene file sets exists in Godot 4.7.2-stable (official)
PASS: CPUParticles2D.material exists
  ... (22 more "exists" lines, all PASS)
PASS: CPUParticles2D has no 'alpha_curve' (brief's correction)
PASS: CPUParticles2D has no 'scale_min' (brief's correction)
PASS: CPUParticles2D has no 'scale_max' (brief's correction)
PASS: CPUParticles2D has no 'amount_ratio' (brief's correction)
   info: CPUParticles2D has visibility_rect = false (brief: not applicable to this CPU design)
-- settings table
PASS: amount = 20 (brief 20)
  ... (18 more settings, all PASS)
PASS: color_ramp stop 0: 0.00 #EAFBFF alpha 1.00 (brief 0.00 #EAFBFF alpha 1.00)
PASS: color_ramp stop 1: 0.35 #83DFF2 alpha 0.75 (brief 0.35 #83DFF2 alpha 0.75)
PASS: color_ramp stop 2: 1.00 #83DFF2 alpha 0.00 (brief 1.00 #83DFF2 alpha 0.00)
PASS: scale_amount_curve point 0 = (0.0, 1.0) (brief (0.0, 1.0))
PASS: scale_amount_curve point 1 = (0.7, 0.65) (brief (0.7, 0.65))
PASS: scale_amount_curve point 2 = (1.0, 0.0) (brief (1.0, 0.0))
PASS: scale_amount_curve(0.35) = 0.8250, linear between points 0.8250 (Claude Code's tangent choice)
PASS: scale_amount_curve(0.85) = 0.3250, linear between points 0.3250 (Claude Code's tangent choice)
FAIL: texture is res://effects/hit_spark_star.png (got null)
PASS: blend_mode = BLEND_MODE_ADD (got 1)
-- in the tree
PASS: still not emitting after 5 frames in the tree (rule 1)
66 checks, 1 failed
```

中间的 PASS 行省略了，完整日志在 `logs/test_hit_spark_config_60fps.log`。纹理导入成功后，还有三项纹理检查会跑：8×8 尺寸、中心不透明的白色、八个尖角。所以总数会变成 68 项。

## 接下来请你运行

在 repo 根目录执行：先导入，再重跑测试，然后录预览。

```bash
godot --headless --path godot --import
./scripts/run-test.sh test_hit_spark_config.gd 60

mkdir -p evidence/a6/hit_spark/dark evidence/a6/hit_spark/lantern
godot --path godot --write-movie D:/courses/7270/walker-dusk-duel-zhaohui-li/evidence/a6/hit_spark/dark/frame.png --fixed-fps 30 --quit-after 60 res://previews/hit_spark_preview.tscn
godot --path godot --write-movie D:/courses/7270/walker-dusk-duel-zhaohui-li/evidence/a6/hit_spark/lantern/frame.png --fixed-fps 30 --quit-after 60 res://previews/hit_spark_preview.tscn -- --lantern
```

- 第一次录制放在暗处 (364, 202)，第二次放在灯笼旁 (510, 208)，两个位置都是 brief 给的。
- 想看不带第二次发射的版本，把 `-- --lantern` 换成 `-- --no-retrigger`。
- 预览会在终端打印每次发射的帧号，可以用来和 `frame000000NN.png` 对照。

我在这里停下。