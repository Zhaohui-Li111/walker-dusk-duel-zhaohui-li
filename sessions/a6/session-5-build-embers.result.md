我把 Effect B 搭好了，也用 `./scripts/run-test.sh test_embers_config.gd 60` 跑了配置测试：**82 项检查，失败 1 项，exit 1**。失败的是贴图检查，因为 `embers_soft.png` 还没生成。按约定，生成器的改动我写好了，但没有运行。

## 实际输出（摘录，完整日志在 `logs/test_embers_config_60fps.log`）

```
Godot Engine v4.7.2.stable.official.ed1daf0bf - https://godotengine.org

-- scene
ERROR: Resource file not found: res://effects/embers_soft.png (expected type: Texture2D)
   at: _load (core/io/resource_loader.cpp:325)
ERROR: res://effects/embers.tscn:26 - Parse Error: [ext_resource] referenced non-existent resource at: res://effects/embers_soft.png.
PASS: res://effects/embers.tscn loads as a PackedScene
...
PASS: emission_shape = 3 (brief 3)
PASS: emission_rect_extents = (280.0, 90.0) (brief (280.0, 90.0))
PASS: preprocess = 1.5 (brief 1.5)
...
FAIL: texture is res://effects/embers_soft.png (got null; run effects/make_textures.gd, then --import)
PASS: blend_mode = BLEND_MODE_MIX, normal (got 0)
-- the feature Effect A doesn't use
PASS: rectangle emission: Effect B 3, Effect A 0 (RECTANGLE = 3)
PASS: preprocess: Effect B 1.50 s, Effect A 0.00 s
-- in the tree
PASS: still not emitting after 5 frames in the tree (rule 5)
82 checks, 1 failed
```

除贴图那一项外，其余 81 项都通过了：表里每个值、两条色带、缩放曲线、混合模式、`process_mode = INHERIT`、加载后不发射，还有场景里设置的每个属性在 4.7.2 中都存在。没有用到我不确定是否存在的属性。

## 需要 Claude Code 依次运行的命令

```bash
"$GODOT" --headless --path godot --script res://effects/make_textures.gd
"$GODOT" --headless --path godot --import
./scripts/run-test.sh test_embers_config.gd 60
```

- **第一条：** 生成器的输出里应看到 `hit_spark_star.png (unchanged, not written)`。生成器现在会先和磁盘上的字节比较，相同就不写；不同时也不会覆盖，除非加 `-- --overwrite`。所以 `hit_spark_star.png` 一定保持逐字节不变。
- **第三条：** 生成后应为 85 项、0 失败（贴图会多出 3 项检查：4 × 4、全白、软圆点）。

## 新增和修改的文件

- `godot/effects/embers.tscn`：一个 `CPUParticles2D`，所有设置都写在场景文件里。brief 只有一个发射器，所以根节点就是这个发射器。
- `godot/effects/make_textures.gd`：新增 4 × 4 白色软圆点 `embers_soft.png`，加上上面说的防覆盖逻辑。
- `godot/tests/test_embers_config.gd`：配置测试，包括矩形发射和 preprocess 这两项"Effect A 没用的特性"的检查。
- `godot/previews/embers_preview.tscn` 和 `.gd`：640 × 360 画面，bg.png 按 1:1 绘制。第 10 帧开始发射，第 100 帧停止。只在预览里的实例上设了 `use_fixed_seed = true, seed = 7270`。

## 截帧命令

要等上面三条命令跑完再截。brief 要读到第 175 帧，所以录 180 帧：

```bash
mkdir -p captures/embers/r0
"$GODOT" --path godot --write-movie D:/courses/7270/walker-dusk-duel-zhaohui-li/captures/embers/r0/frame.png --fixed-fps 30 --quit-after 180 res://previews/embers_preview.tscn
```

预览默认只把 `emitting` 设为 true，不调用 `restart()`，和游戏里控制器的做法一致。brief 的待确认问题 3 是：之后再打开发射时，preprocess 会不会跑。为此可以再录一个对照版，第 10 帧额外调用 `restart()`：

```bash
mkdir -p captures/embers/r0-restart
"$GODOT" --path godot --write-movie D:/courses/7270/walker-dusk-duel-zhaohui-li/captures/embers/r0-restart/frame.png --fixed-fps 30 --quit-after 180 res://previews/embers_preview.tscn -- --restart
```

如果默认版第 10 帧是空的而对照版是满的，问题 3 的答案就是"不跑"。

## 一点观察，由你决定

brief 的意图写了"还有少量偏中性的浅色灰尘粒子"，但设置表里只有一个发射器，起始颜色只在 `#C58A55` 到 `#E8C49A` 这段琥珀色之间，做不出中性灰尘。我按设置表搭了，没有自己加。

我没有接入游戏，没碰任何 `.gdshader`，也没有提交。