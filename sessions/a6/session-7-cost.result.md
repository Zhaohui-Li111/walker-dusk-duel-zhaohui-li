我写好了 `godot/tests/cost_effects.gd`，并用 `./scripts/run-test.sh cost_effects.gd 60 300` 跑过：**24 项检查，0 失败**，退出码 0。四个场景之间的差别都超过了噪声。没有提交，也没有改任何效果或玩法文件；仓库里只多了 `godot/tests/cost_effects.gd` 和 `logs/cost_effects_60fps.log` 两个新文件。

Example 09 的原脚本不在仓库里，也不在这台机器上。这个脚本是按任务描述写的，文件头里写明了这一点。

### 第一次运行：脚本只测到了它自己
第一版用 `Performance.TIME_PROCESS` / `TIME_PHYSICS_PROCESS` 计时，结果完全不能用：
- 第 1 轮四个场景全是 0。
- 第 2 轮四个场景全是同一个常数（107536 / 406 µs）。

原因：这两个监视器大约每秒（按真实时间）才刷新一次，不是每帧刷新。而 `--fixed-fps` 下整个运行只用了不到 2 秒真实时间。脚本把这些数报成了 "SAME within noise" 和 "identical process means: the monitor may not be updating"。

另外，`OS.get_cmdline_args()` 里读不到 `--fixed-fps`，所以第一版误报成 "fixed fps off (realtime)"。

### 现在的测法
- **主指标 `engine`**：每帧的墙钟时间减去脚本自己的逐帧代码时间。在 `--fixed-fps` 下帧不按真实时间节流，所以墙钟时间就是这一帧的 CPU 工作量，其中包括 CPUParticles2D 的内部处理和那一个物理 tick。
- **固定帧率**：改为检查每帧的 `delta == 1/60`。
- **场景状态**：G、A、B 都停在标题画面，没人出招，也没有 hitstop，所以 A − G、B − G 就是效果本身的开销。
- **A（SETUP）**：脚本自己交错 `restart()` 四个槽，保证每个测量帧都有 4 簇火花同时存活。
- **B（SETUP）**：脚本调用 `Embers.restart()` 让它开始发射，再预热 4 秒，让粒子场填满。
- **样本量**：每个场景先预热 240 帧，再测 1200 帧。整组跑两轮，第二轮倒序，用来检查漂移。

### 真实输出（摘自 `logs/cost_effects_60fps.log`）
```
== SUMMARY: both passes pooled, microseconds per frame ==
case                               metric       mean       sd      min   median      p95      max
E empty scene                      engine        5.8      2.7      3.0      5.0     11.0     30.0
G game, both effects off           engine       38.2      7.3     35.0     37.0     42.0    189.0
A Effect A, 4 bursts alive         engine       49.4     11.2     45.0     47.0     54.0    278.0
B Effect B, emitting, field full   engine       45.1     13.4     40.0     43.0     50.0    383.0

== DRIFT: pass 1 vs pass 2 (engine), difference and its 95% interval ==
    E: pass 1 6.3, pass 2 5.3, difference -1.0 ± 0.2 µs  <- the passes differ by more than the noise
    G: pass 1 38.3, pass 2 38.1, difference -0.3 ± 0.6 µs
    A: pass 1 49.7, pass 2 49.1, difference -0.6 ± 0.9 µs
    B: pass 1 45.4, pass 2 44.9, difference -0.6 ± 1.1 µs

== DIFFERENCES (pooled): mean difference ± 95% interval (Welch, 1.96 x standard error); medians ==
    G - E  engine  mean   +32.4 ±  0.3 µs, median   +32.0 µs  separated
    A - G  engine  mean   +11.2 ±  0.5 µs, median   +10.0 µs  separated
    B - G  engine  mean    +6.9 ±  0.6 µs, median    +6.0 µs  separated
    A - B  engine  mean    +4.3 ±  0.7 µs, median    +4.0 µs  separated
    harness share, A: 1.8 µs of 51.2 µs wall (3%)
24 checks, 0 failed
```
每个场景每一轮的 wall / harness / engine 明细都在日志里。

### 怎么读这些数
- **效果开销**：A 约 0.011 ms/帧，B 约 0.007 ms/帧，都远低于你的预算（0.25 / 0.50 ms），也都低于你的预测（0.08 / 0.05 ms）。实测值要不要、怎么写进 brief 由你决定，我没有改 brief。
- **E 的漂移**：两轮之间差 1 µs，在 6 µs 的量级上算明显，但对效果之间的比较没有影响。计时分辨率是 1 µs，最大值里的尖峰来自操作系统的调度。
- **没测到的部分**：没测打斗进行中的开销，也没测 GPU 时间。headless 用的是 dummy 渲染器，不画粒子。GPU 时间还需要你在窗口模式下用 Visual Profiler 测。