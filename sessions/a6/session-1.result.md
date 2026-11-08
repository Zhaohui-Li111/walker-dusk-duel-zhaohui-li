我重写了 `CLAUDE.md`，现在 119 行，七个部分按你给的顺序排列。只改了这一个文件，没有建 effect，也没有改任何脚本。git status 里另外两个已修改的文件（`prop_taiko.blend` 和 A5 的 `_qc/final.log`）在这次会话开始前就已经是修改状态。仓库根目录没有 `AGENTS.md`，所以第一行没有 `@AGENTS.md`。

**主要内容：**
- **Project context：** 两个 effect 都用 `CPUParticles2D`。Effect A 由 `Fighter.attack_resolved` 触发（`fighter.gd:19`，在 `:221-223` 发出），`main.gd:133-138` 接收这个信号，并在这里设置 hitstop。Effect B 由 `main.phase` 控制（`main.gd:24`）。信号 `round_started`、`round_over`、`paused_changed` 也都写了文件行号。effect 所在的场景是 `main.tscn` 的 `Main` 节点。`scripts/run-test.sh` 的三种用法都列了，包括 `realtime`。`realtime` 不加 `--fixed-fps`，日志写到 `logs/<name>_realtime.log`，但仍然是 headless。每个现有测试的基线数字都附了来源日志。
- **Ownership：** 保留了 `godot/shaders/` 的规则，新加了“effect 设置写在 `godot/effects/` 的场景文件里，不写在代码里”。这个目录现在还不存在。
- **Godot 4 names：** 属性分成三类：brief 的 ClassDB 探测确认存在的、确认不存在的、文件里无法确认的。无法确认的包括 `color_initial_ramp`、`initial_velocity_min`、`spread`、`gravity`、`preprocess`、`speed_scale` 等，要求先用 `ClassDB` 检查，缺了就报告，不拿别的属性顶替。

**需要你决定的几个问题（都写进了 Unconfirmed）：**
1. **phase 没有信号。** 它只是个普通变量，没有变化信号。如果不改 `main.gd`，Effect B 只能每个 tick 轮询。
2. **谁把 effect 接进 `main.tscn`，`main.gd` 能不能加代码，brief 都没说。** CLAUDE.md 里写的是改 `main.gd` 之前先问你。
3. **贴图写法和新规则有冲突。** brief 说两个贴图都是 “code-drawn”，和“设置写在场景文件里”这条规则矛盾。一个办法是只生成一次，存成资源文件，两边都满足。
4. **brief 里有一处行号写错了。** `phase` 引用的是 `main.gd:25`，实际在 `:24`。