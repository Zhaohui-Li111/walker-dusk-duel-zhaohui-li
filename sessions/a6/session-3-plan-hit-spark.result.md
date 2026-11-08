**计划（尚未编辑任何文件）**

我读了 `CLAUDE.md`、brief、`main.gd`、`main.tscn`、`fighter.gd`、`hit_spark.tscn` 和 `test_hurt_flash.gd`。`hit_spark.tscn` 及其设置不动，`.gdshader` 不碰，`main.gd` 也不改。

---

## Step 1 — 触发代码和场景接线

**新文件 `godot/effects/hit_spark_pool.gd`**（一个 `Node`，约 50 行）

**改 `godot/game/main.tscn`**
- 增加两个 ext_resource：`hit_spark.tscn` 和这个脚本。
- 在 `Effects` 之后加 4 个实例 `HitSpark0..3`，parent 都是 `"."`，即 `Main`。实例上不覆盖任何属性，设置全部留在 `hit_spark.tscn`。
- 再加一个节点 `HitSparkPool`，挂上面的脚本。

**这个节点做什么（只读游戏状态，只写自己的 4 个发射器）**
- `_ready`：从 `get_parent()` 取 `P1`、`P2` 和 4 个槽位。连接两个 fighter 的 `attack_resolved`，以及 `round_started` 和 `paused_changed`。
- **规则 1、2：** `result != "hit"` 时直接 return。是 `"hit"` 时选一个槽位，设 `slot.position = point`，然后调用 `slot.restart()`。`point` 本来就是 `Main` 坐标，槽位又是 `Main` 的子节点，所以位置不用换算。
- **规则 3（retrigger = overlap）：** 每个槽位有 busy 标记和一个启动序号。`restart()` 时设为 busy，收到该槽位的 `finished` 信号时清掉。新事件优先用空闲槽位，永远不会重启正在播的那一个。四个都 busy 时，重用序号最小（最旧）的那个，这是 brief 写的兜底。
- **规则 4：** 发射器挂在 `Main` 下，不挂在 fighter 下。
- **规则 5：**
  - `_physics_process` 的优先级设为 10，在 `main` 之后运行。`main.paused or main.hitstop > 0` 时 4 个槽位 `speed_scale = 0`，否则为 1。
  - `paused_changed` 触发时立刻再算一次。144 fps 下有些帧没有 physics tick，不这样做暂停那一帧会漏掉。
- **规则 6：** 收到 `round_started` 时，每个槽位先 `restart()` 再立刻 `emitting = false`，清掉粒子且不发射，并清空 busy 标记。

**有三点我无法提前确认**，因为本会话不能直接运行 godot，只能用 wrapper 跑 `godot/tests/` 里的文件：
1. 4.7.2 的 `CPUParticles2D` 有没有 `finished` 信号。
2. one-shot 播完后 `emitting` 会不会自己变回 false。
3. `speed_scale = 0` 时 `restart()` 会不会生成粒子（brief Q2）。

测试会先用 `ClassDB` 检查并打印这些。如果没有 `finished`，Step 1 改成按 tick 记录忙闲，我会先告诉你再改。

---

## Step 2 — 新测试 `godot/tests/test_hit_spark_state.gd`

结构照 `test_hurt_flash.gd`：
- `main._physics_process` 保持开启，P1 用 `Input.parse_input_event` 发键盘事件驱动。
- 不调用触发函数，不写 fighter 或 `main` 的任何状态。
- 两个只读记录器：
  - 每个 tick 一个：优先级 1000，记录每个槽位的 `emitting`、`position`、`speed_scale`，以及 `main.paused`、`main.hitstop`。
  - 每帧一个：记录 `speed_scale`。
- 两个 fighter 的 `attack_resolved` 都记下 tick、result 和 point，`finished` 也记 tick。
- 用 60 fps 运行，不等音频。

| 场景（全部用真实输入） | 断言 | 规则 |
|---|---|---|
| A 场景加载 → 标题 → Enter → intro → fight | 每个 tick 和每帧 4 个槽位都是 `emitting == false`；正好 4 个 `CPUParticles2D`，parent 是 `Main`，每个 `amount` 20，峰值 80；P1/P2 下没有发射器 | 1（加载时不触发）、3、4 |
| B 一次命中（P2 的 controller 设为 null，A5 的做法）：按 D 走近，按 J | 命中 tick 上正好一个槽位从 false 变 true，`position` 与 `point` 相差 ≤ 1 px，其他槽位不变；之后 P2 被击退，槽位位置不变 | 1、2、4（预测失败 3） |
| C 一个寿命内两次命中：先按住 D 把 P2 推到右墙（推开靠游戏自己的 `_separate`），再 J…J，间隔约 23 tick，小于 36+4 | 第二次用了另一个槽位；第一个槽位全程 `emitting` 为 true，位置没变；T2 时两个都在播；第一个槽位的 `finished` 先到，且早于 T2+36，证明它没被重启；两个都结束后，下一次命中用空闲槽位 | 3（预测失败 2） |
| D 自由对打：P2 用游戏自己的 `CpuController`；P1 先按住 L 格挡，再在远处空挥 J，再贴近出拳，最后打满一局到 K.O. | 每个 tick 上，槽位触发数 = 该 tick 的 `"hit"` 数，两名 fighter 都算，位置都对；只有 blocked、whiff 或 interrupted 的 tick，以及其他所有 tick，都是 0 次触发；hit、blocked、whiff 每种至少出现一次，否则测试判 FAIL；四个都忙时检查最旧槽位被移到新的 `point` | 1、2、3 |
| E hitstop 和暂停 | 命中后 `hitstop > 0` 的 tick 上 `speed_scale == 0`，之后恢复为 1；按 P 暂停期间每个 tick、每一帧都是 0，再按 P 恢复为 1；暂停约 40 tick 后，`finished` 至少晚 40 tick，说明 CPU 模拟确实停了；打印 Q2 的观察结果 | 5（预测失败 1） |
| F 局重置：D 的 K.O. 之后，在结果画面按 Enter | `round_started` 之后 4 个槽位都不在发射、都空闲，之后第一次命中仍正常触发 | 6（见下） |

**规则 6 有个缺口需要你决定。** 真实操作中 K.O. 后要过 `KO_FRAMES` = 90 tick 才能开下一局，而火花寿命只有 36+4 tick。所以 `round_started` 时不可能有正在播的火花，"清掉活跃 burst"这条路径真实输入走不到。可选：
- (a) 只测上面的真实路径，并写明这一点没被覆盖；
- (b) 另加一个标为 SETUP 的检查：在一次 burst 中途调用 `main.start_fight_now()`。它调用的是游戏自己的开局函数，不是触发函数。

同样，四个槽位全满时的兜底在场景 D 里不一定会出现。如果没出现，测试会打印"未覆盖"，不会算作通过。

## Step 3 — 运行

全部通过 `./scripts/run-test.sh`：
- 新测试：60。
- `test_hit_spark_config.gd`：60。
- `test_runner.gd`：60，必须仍是 94 / 0（`main.tscn` 改了）。
- `test_hurt_flash.gd`：30、60、144，必须仍是 69 / 0。
- `check_props3d.gd`：60。
- `test_materials.gd`：60。
- `calibrate_normal_map.gd`：60。

`capture_*.gd` 需要窗口，不跑。

---

**无头测试能证明的：** 节点状态，即何时、哪个槽位、在哪里开始发射，`speed_scale`、parent、忙闲，以及 CPU 模拟的进度（通过 `finished` 的时间）。

**无头测试证明不了的：**
- 是否画出了任何东西：dummy renderer 不绘制；`CPUParticles2D` 也没有公开的存活粒子数。
- 单个粒子的位置、数量，以及 burst 在 `speed_scale` 0 时到底何时出现（Q2 只能间接看）。

**只能由人检查的：**
- 外观：亮度、白到青的变化、星形、加色混合在灯笼处是否可读、15–30 px 的范围（Q1）。
- 第 22 帧两团 burst 是否清楚地分开。
- hitstop 定格看起来是否合适。
- 和 fighter、旧 `effects.gd` 火花的绘制先后顺序。
- GPU 时间（Visual Profiler）。

要我开始 Step 1 吗？另外请选规则 6 用 (a) 还是 (b)。