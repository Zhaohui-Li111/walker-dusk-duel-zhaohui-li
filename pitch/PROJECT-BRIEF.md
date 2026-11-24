# PROJECT-BRIEF — Dusk Duel, final project pitch (A8)

> **Version 1 · DRAFT · 2026-11-23.** Zhaohui answered the seven questions in Chinese (pasted in
> chat, 2026-11-23). Asked once whether the answers were written with another AI, Zhaohui answered
> "我自己写的" ("I wrote it myself"). Claude Code translated them and kept the original in the
> appendix. Claude Code also wrote the **exists today** list from the repository. Every Claude Code
> addition is marked *(Claude Code)*. Items Zhaohui still has to settle are marked **[OPEN]**.
> Later changes are appended as dated revisions.

**Working title:** Dusk Duel — A Complete Playable Fighting Game Vertical Slice
**Stack:** Godot 4.7.2 stable, GDScript, GL Compatibility renderer; desktop (Windows) today, Web
export planned *(Claude Code: from `godot/project.godot:35-36`; no `export_presets.cfg` exists yet)*.

## 1. What is it?

Dusk Duel, taken from its existing fighting game to a complete playable vertical slice. It is a
full game flow, not a single character controller or effects demo:
- **Title screen:** the game's title and start screen.
- **Gameplay:** the player fights a CPU opponent.
- **Combat feedback:** attack, hurt, spark, flame and animation feedback.
- **K.O. screen:** the win/loss decision and the end screen.
- **Replay:** a new round can start.

The planned export is a **Web build**, so someone without Godot can play it. It ships with a
reproducible test report: function tests, edge-case tests, visual checks and performance data.

*(Claude Code: title → round call → fight → K.O. → result → rematch, with the CPU opponent,
already runs today: commit `6317281`, 2026-10-05; see "Exists today". The new part is the Web
build and the report run against it. **[OPEN]** Zhaohui to say in a revision what the slice adds to
the game flow beyond that, if anything.)*

## 2. Role and reader

**Target role:** Gameplay Programmer / Game Developer Generalist. **Reader:** a studio's technical
lead and a recruiter.

In the first 60 seconds they should:
1. run the game and see the complete title screen;
2. start a match and feel the movement, attacks and hurt feedback;
3. see the full K.O. and restart flow.

They should not have to read a lot of code to see the project's value. The code and test report
are there to show the engineering further: game logic, rendering, animation state and test
automation.

*(Claude Code: two roles are named. **[OPEN]** Zhaohui to say which one the film leads with.)*

## 3. Comparables

1. **Street Fighter**, the reference for traditional fighting games: its core combat (character
   actions, attack feedback, hurt reactions, round win/loss). This project does not try to copy
   its complexity; it focuses on a small but complete fighting experience.
2. **Godot Engine**, the engine this project uses and that Zhaohui has used and studied. The project
   aims to show that Godot can combine character control, shaders, particles, animation and tests
   into one complete game, not only separate feature demos.

**The difference aimed for:** not more content than a mature game, but a small fighting game that
has all of: a complete game lifecycle; gameplay and visual effects that can be verified; a
reproducible test process; a version playable in a browser.

*(Claude Code: the handout asks for games or tools Zhaohui **actually played or used**, and what
this project does that they do not. **[OPEN]** Zhaohui to name which Street Fighter they played, and
to state what Dusk Duel gives a specific player that it does not. Godot is the engine this project
is built with, not a comparable game or tool; Zhaohui to decide whether to keep it.)*

## 4. What is out

To control scope, the project will not include:
- online play or multiplayer;
- more than one map: one fight scene only;
- character select or equipment systems;
- accounts, cloud saves or progress saves;
- a large roster of characters or moves.

A complete, stable, testable experience comes first, not a growing feature list.

## 5. What comes first

First milestone: from the title screen into the fight scene, and one basic attack-and-hurt
exchange. Specifically:
1. the game starts and shows the title screen;
2. clicking Start enters the fight scene;
3. the player and the CPU opponent both move;
4. a player attack triggers the opponent's hurt feedback;
5. both health values update correctly.

**How to show it ran:** a full screen recording; the Godot project and run instructions; automated
test results checking the scene change, hit detection and health updates; anyone can re-run it from
the README. This milestone does not need every effect, but it must prove the core gameplay loop.

*(Claude Code: all five steps already run today, so under the honesty rule they are past tense:
commit `6317281`; `test_runner.gd` 94 / 0 checks the round flow, hits and health headless. The game
starts with Enter or Space; there is no Start button to click (`README.md`, Controls). **[OPEN]**
Zhaohui to name a first piece that does not exist yet. The Web export is one candidate.)*

## 6. Risk

**Main risk:** the Web export and the desktop build may differ in look and performance. The project
uses the GL Compatibility renderer; shaders, particles and some effects can differ across GPUs,
browsers and runtimes, especially shader colour and texture sampling; particle count, transparency
and blending; the effect of VSync on frame rate and GPU load; rendering performance on the Web.

**What to do about it:**
1. make the Web export an early check, not a last step;
2. set up visual tests for the main shaders and particle effects;
3. compare desktop and Web in the same scene under the same test conditions;
4. record GPU use, frame rate and the necessary performance figures;
5. give effects that do not survive a simpler fallback.

## 7. Why this project?

It combines skills Zhaohui already has with skills to learn.

**Existing skills, with evidence:**

| Skill | Evidence |
|---|---|
| Blender 3D asset making | `a3` |
| Godot shaders and materials | `a5` |
| Hurt flash effect | `a5` |
| Particle systems and GPU effects | `a6` |
| VSync toggle and performance experiment | `a6` |
| Flame and animation effects | `a7` |
| Edge-case tests | `a7` |
| Technical tuning and documentation | `TUNING.md` |
| Godot Compatibility rendering | current project settings |

These are not planned learning; they are already in the project and can be checked and shown.

**Skills to learn:**
1. **Full game architecture:** turning separate features into one stable game lifecycle.
2. **Gameplay state management:** better transitions between title, fight, win/loss and rematch.
3. **AI opponent:** a CPU opponent that behaves sensibly at a fair difficulty.
4. **Cross-platform testing:** checking that desktop and the Web export agree.
5. **Performance profiling:** a more standard GPU and CPU performance test process.
6. **Release engineering:** Web export, deployment, and delivery others can reproduce.

The value is that the project does not ask Zhaohui to repeat techniques already learned from
scratch, but to integrate them and solve problems closer to real game development. The aim is not
only a good-looking demo but a game with a complete experience, engineering documents and test
evidence, which other developers can reproduce.

*(Claude Code, consistency notes:*
- *Items 1–3 under "Skills to learn" already exist in a first form (round flow and
  `cpu_controller.gd`, commit `6317281`). **[OPEN]** Zhaohui to say what is new in each: for
  example, what the CPU opponent will do that it does not do today.*
- *The `a6` performance row is backed by a real measurement: Intel UHD Graphics, OpenGL 3.3,
  Compatibility, Windows 11; GPU cost of Effect A +0.012 ms and Effect B +0.004 ms (median), from
  `godot/tests/gpu_price.gd`, run by Claude Code at Zhaohui's request; the editor's Visual Profiler
  read 0 GPU time (`TEST-REPORT.md`, "GPU price"; `logs/gpu_price_windowed.log`).*
- *The `a3` Blender props are in the A5 prop room, not in the fight scene. **[OPEN]** Zhaohui to say
  whether they count for this project.)*

## Exists today *(Claude Code, from the repository, 2026-11-23)*

| What | Where it can be seen | Check |
|---|---|---|
| Full round: title → round call → fight → K.O. → result → rematch; CPU opponent | commit `6317281` (2026-10-05), A2 note `SUBMISSION-A2.md` | `test_runner.gd` 94 / 0 |
| Generated art and audio, one image per fighter state, four event sounds, music loop | A2 (`SOURCES.md`, `ASSET-LOG.md`) | Zhaohui's playtest notes, `TEST-REPORT.md` |
| Three Blender 3D props | tag `a3` | `check_props3d.gd` 49 / 0 |
| Hurt-flash shader, granite and hint materials (shaders hand-written by Zhaohui) | tag `a5` | `test_hurt_flash.gd` 69 / 0 at 30, 60, 144 fps; `test_materials.gd` 96 / 0; three mutations |
| Hit sparks and ember particles; CPU and GPU cost measured on Intel UHD Graphics | tag `a6`; `godot/tests/gpu_price.gd` (commit `7888427`) | `test_hit_spark_*` 69 / 0 and 57 / 0; `test_embers_*` 85 / 0 and 38 / 0 |
| Lantern flame cycle and kick arc rig, both on the fight's own clock | tag `a7` | `test_lantern_readback` 47 / 0; `test_kick_readback` 52 / 0; `test_anim_states` 58 / 0; `test_kick_edges` 38 / 0; pins 19 / 0 |
| Three films built with Brutalist (A5, A6, A7) | Google Drive links in `README.md` | toolkit gate reports in `youtube/` |

## Will exist

- A Web export of the slice, playable in a browser *(Claude Code: no export preset exists yet)*.
- A test report re-run against the Web build and compared with desktop.
- **[OPEN]** What else is new: Zhaohui's revision of questions 1, 5 and 7.

---

## Appendix — Zhaohui's answers, original (2026-11-23)

Kept as pasted, including the closing advice section, which does not answer a question and is not
translated above.

我建议选择 ① Dusk Duel 完整垂直切片（Vertical Slice），但把技术重点放在 Gameplay、Shader/VFX 和可复现测试上。

原因是：仓库目前已经有角色、材质、粒子、动画和部分测试。如果继续只做某个独立功能，会浪费已有积累。把它整合成一个可以直接运行、可以体验、可以验证的完整游戏，更容易向招聘官证明你的综合开发能力。

下面是第一天的回答，可以直接作为作业初稿。

Day 1 — Project Definition

1. 项目是什么？
我选择方向 ①：Dusk Duel — A Complete Playable Fighting Game Vertical Slice。
项目目标是将现有的 Dusk Duel 格斗游戏开发成一个完整的可玩垂直切片。
它不仅仅是一个角色控制器或者特效 Demo，而是一个从开始到结束都可以完整体验的游戏流程：
- Title Screen：游戏标题和开始界面。
- Gameplay：玩家与 CPU 对手进行格斗。
- Combat Feedback：攻击、受击、火花、火焰和动画反馈。
- K.O. Screen：胜负判定和结束画面。
- Replay：支持重新开始一局游戏。
最终计划导出 Web 版本，让没有安装 Godot 的人也可以直接体验。
同时提供一份可复现的测试报告，记录功能测试、边界条件测试、视觉效果验证和性能数据。

2. 职位和读者
Target Position: Gameplay Programmer / Game Developer Generalist
主要读者是游戏开发团队的技术主管（Technical Lead）和招聘官。
我希望他们打开项目后的前 60 秒能够完成三件事：
1. 直接运行游戏，看到完整的标题界面。
2. 开始一局比赛，体验角色移动、攻击和受击反馈。
3. 看到完整的 K.O. 和重新开始流程。
我不希望招聘官必须阅读大量代码才能理解项目的价值。
代码和测试报告则用于进一步展示我的工程能力，包括游戏逻辑、渲染、动画状态管理和测试自动化。

3. 对比对象
我选择两个参考对象：
1. Street Fighter
它是传统格斗游戏的参考对象。
我希望借鉴它的核心战斗体验，包括角色动作、攻击反馈、受击表现和回合胜负机制。
我的项目不会试图复刻它的复杂度，而是专注于实现一个小规模但完整的格斗体验。
2. Godot Engine
Godot 是这个项目使用的游戏引擎，也是我实际使用和研究的工具。
我希望通过这个项目展示 Godot 不仅可以用于制作独立的功能 Demo，还可以整合角色控制、Shader、粒子系统、动画和测试，形成一个完整的游戏产品。
我的项目希望做到的差异：
重点不是比成熟游戏拥有更多内容，而是让一个小型格斗游戏同时具备：
- 完整的游戏生命周期。
- 可验证的 Gameplay 和视觉效果。
- 可复现的测试流程。
- 可以在浏览器中体验的交付版本。

4. 刻意不做什么
为了控制开发范围，我决定暂时不做：
- 不做联网对战和 Multiplayer。
- 不做多个地图，只保留一个战斗场景。
- 不做复杂的角色选择和装备系统。
- 不做账号、云存档和进度保存。
- 不追求大量角色和技能。
项目优先保证一个完整、稳定、可测试的游戏体验，而不是不断增加功能。

5. 第一个要跑起来的部分是什么？
第一个里程碑是：
从标题界面进入战斗场景，并完成一次基本的攻击和受击交互。
具体包括：
1. 游戏能够正常启动并显示标题界面。
2. 点击 Start 后进入战斗场景。
3. 玩家和 CPU 对手能够正常移动。
4. 玩家攻击时，对手能够触发受击反馈。
5. 双方生命值能够正确更新。
如何证明它真的运行起来：
- 提供一段完整的屏幕录制。
- 提供对应的 Godot 项目和运行说明。
- 提供自动化测试结果，验证场景切换、攻击判定和生命值更新。
- 确保其他人能够按照 README 中的步骤重新运行。
这个里程碑不要求完成全部特效，但必须证明核心 Gameplay Loop 已经成立。

6. 一个具体的风险，以及应对方法
主要风险：Web 导出与桌面端的视觉效果和性能表现可能存在差异。
目前项目使用 Godot GL Compatibility 渲染器。
Shader、粒子和部分视觉效果在不同 GPU、浏览器和运行环境中可能出现差异。
尤其是：
- Shader 的颜色和纹理采样表现。
- 粒子的数量、透明度和混合效果。
- VSync 对帧率和 GPU 负载的影响。
- Web 环境下的渲染性能。
应对方法：
1. 将 Web 导出作为早期验证目标，而不是等到最后才测试。
2. 对主要 Shader 和粒子效果建立视觉测试。
3. 使用相同场景和测试条件比较桌面端与 Web 端。
4. 记录 GPU 使用情况、帧率和必要的性能指标。
5. 对无法兼容的效果提供更简单的 fallback 实现。
这样可以避免项目开发完成后才发现 Web 版本无法正常运行。

7. 为什么选这个项目？
这个项目能够将我已经掌握的技术与需要进一步学习的技能结合起来。
已经具备的技能：
技能	已有证据
Blender 3D 资产制作	a3
Godot Shader 和材质	a5
受击闪白效果	a5
粒子系统和 GPU 效果	a6
VSync 切换和性能实验	a6
火焰和动画效果	a7
Edge Case 测试	a7
技术调参和文档记录	TUNING.md
Godot Compatibility 渲染	现有项目配置
这些不是计划中准备学习的内容，而是已经在项目中实现、可以进一步核对和展示的成果。
需要进一步学习的技能：
1. 完整游戏架构： 将独立功能整合成一个稳定的游戏生命周期。
2. Gameplay State Management： 更好地管理标题、战斗、胜负和重赛之间的状态转换。
3. AI Opponent： 实现行为合理、难度适中的 CPU 对手。
4. Cross-platform Testing： 验证桌面端和 Web 导出的兼容性。
5. Performance Profiling： 建立更规范的 GPU 和 CPU 性能测试流程。
6. Release Engineering： 完成 Web 导出、部署和其他人可复现的交付流程。
我认为这个项目的价值在于，它不要求我从零开始重复已经掌握的技术，而是要求我把这些技术整合起来，解决更接近真实游戏开发的问题。
最终希望交付的不只是一个看起来不错的 Demo，而是一个有完整体验、有工程文档、有测试证据、能够被其他开发者复现的游戏项目。

我的几个额外建议
有三个地方我认为第一天就应该明确，避免后续项目范围失控。
1. 不要把项目变成纯粹的视觉展示。
你已经有 a5、a6、a7 的 Shader 和 VFX 工作。如果最后只是展示几个特效，反而无法体现你整合系统的能力。
完整游戏流程应该是主线，视觉效果是加分项。
2. a6 的 GPU 性能数据暂时不要写成已验证结论。
尤其是 F9 VSync 切换实验，要核对测试条件、GPU、帧率和数据后，才能作为性能证据。
3. 注意区分已有成果和本次新增成果。
例如：
- a3：已有 Blender 资产。
- a5：已有 Shader 和受击闪白。
- a6：已有粒子与 VSync 实验。
- a7：已有火焰、踢腿动画和 Edge 测试。
- 本次新增：完整游戏流程、CPU AI、Web 发布、跨平台测试报告。
这样招聘官能够清楚看到你在这个项目中真正完成了什么。
最后一个判断： 我认为这个项目最值得展示的不是你能写多少 Shader，而是你能否把已经实现的多个技术模块，整合成一个陌生人拿到仓库就能运行、体验和验证的完整产品。这个目标也更符合 Gameplay Programmer / Generalist 的求职定位。

## Revision 2 · 2026-11-23 · Questions 3, 5 and 7 revised by Zhaohui

Zhaohui pasted revised answers to questions 3, 5 and 7, each in English and Chinese. The English
below is **Zhaohui's own English, as given**; Claude Code changed nothing in it. Chinese originals
are kept below as R3, R5 and R7. These replace the answers to 3, 5 and 7 in Version 1, which are
kept as written. Provenance: asked once whether this revision was written with another AI,
Zhaohui answered "我自己写的" ("I wrote it myself"), 2026-11-23. Recorded as given.

### 3. Reference projects (replaces Version 1, question 3)

My main reference is the The King of Fighters series, which I have personally played.

I appreciate its fast-paced combat, character movement, attack timing, and defensive mechanics.
These experiences influenced how I think about building a fighting game.

Dusk Duel takes a smaller and more accessible approach. Rather than focusing on a large character
roster or competitive multiplayer, it focuses on providing a complete single-player fighting
experience.

I want to make Dusk Duel accessible to players who want a quick fighting match without installing
a large game, finding an online opponent, or going through a complicated setup.

The game already supports basic CPU behaviors, including approaching the player, attacking, and
defending. My next goal is to make these behaviors more deliberate and engaging.

*(Claude Code:*
- *Godot is no longer listed as a comparable; Zhaohui's note says to name it in the stack instead.*
- *The CPU behaviours named exist: `godot/fighter/cpu_controller.gd` walks in when out of kick
  range, kicks in range after a 40-tick cooldown at 50 %, blocks a close attack at 55 %, steps back
  when too close, and re-decides every 10 ticks with a seeded generator (commit `6317281`).*
- *"Without installing a large game" depends on the Web build, which does not exist yet; in the
  film it is a "will".*
- ***[OPEN]** which King of Fighters game(s) Zhaohui played, so the film can name one.)*

### 5. First milestone (replaces Version 1, question 5)

**Milestone 1: Complete a Full Match in a Web Browser**

The core gameplay loop has already been implemented and tested. The existing test suite currently
reports 94 passing tests and 0 failures (6317281).

My first new milestone is to export Dusk Duel to the Web and verify that a player can complete an
entire match directly in a browser.

The acceptance criteria are:
1. The game loads successfully in a supported browser.
2. The player can start a match from the title screen.
3. Character movement, attacks, and defensive interactions work correctly.
4. CPU opponents can approach, attack, and defend.
5. Shader effects, particles, and animations render correctly.
6. The match can reach the K.O. screen.
7. The player can restart and complete another match.

I will provide a browser-based gameplay recording, the exported build, and a reproducible test
report documenting the browser environment and any compatibility issues.

*(Claude Code:*
- *Correction of a fact Claude Code supplied: commit `6317281` is where the round flow and CPU
  opponent first appear, but its `test_runner.gd` had fewer checks. **94 / 0** is today's count,
  logged at commit `8049c54` (2026-11-22, `logs/test_runner_60fps.log:24`).*
- *Criterion 5 ("render correctly") is judged by eye against desktop captures; a headless run draws
  nothing, so no automated check can settle it. **[OPEN]** Zhaohui to name the browser(s) and machine
  the milestone will be checked on.)*

### 7. Why this project? (replaces Version 1, question 7)

I chose this project because it allows me to build on my existing gameplay programming experience
while tackling new engineering challenges.

Skills I have already developed:

| Skill | Existing evidence |
|---|---|
| 3D asset creation | Blender assets (a3) |
| Shader and material development | Hit flash effects and shader tests (a5) |
| Particle systems | Hit sparks and ember particles (a6) |
| Animation and visual effects | Lantern fire and kick arc animation (a7) |
| Gameplay testing | Edge-case tests and TUNING.md (a7) |
| Game flow implementation | Complete title-to-combat-to-K.O.-to-replay loop |
| CPU opponent behavior | Basic approaching, attacking, and defending behaviors |

Skills I want to develop further:

1. **Advanced CPU behavior:** Improve the existing CPU opponent with more deliberate
   decision-making, distance-aware attack selection, better defensive timing, and adjustable
   difficulty levels. The goal is to make combat more engaging rather than simply making the
   opponent attack more frequently.
2. **Cross-platform game delivery:** Learn how to package and deploy a Godot game for the Web,
   identify browser-specific rendering or input issues, and ensure that the complete gameplay loop
   works outside the development environment.
3. **Performance profiling and optimization:** Establish repeatable performance benchmarks for CPU
   and GPU workloads, investigate the cost of particle effects and shaders, and evaluate
   performance under different rendering conditions.
4. **Gameplay quality and reliability:** Expand the existing tests to cover more complex combat
   interactions, repeated matches, state transitions, and edge cases.

I am particularly interested in Gameplay Programming because it combines game mechanics, system
design, real-time interactions, and problem-solving.

Rather than building another isolated technical demo, I want to turn the existing Dusk Duel
implementation into a polished, playable, and independently verifiable game.

*(Claude Code:*
- *Evidence for the two new rows: game flow and CPU behaviour, commit `6317281` (2026-10-05);
  `test_runner.gd` 94 / 0 at `8049c54`.*
- *Point 3 builds on a measurement that exists: A6's CPU and GPU cost on Intel UHD Graphics
  (`TEST-REPORT.md`, "GPU price").*
- *Role: this answer leads with Gameplay Programming. **[OPEN]** Zhaohui to confirm the film names
  Gameplay Programmer as the target role (question 2 still lists two).*
- ***[OPEN]** question 1 is not revised: Version 1 lists the title, fight, K.O. and replay as the
  slice's content, which all exist. The new content now named across 3, 5 and 7 is the Web build,
  the stronger CPU opponent with difficulty levels, and the wider tests.)*

### Will exist (replaces the Version 1 list, from Revision 2; Claude Code)

- A Web export that plays a full match and a rematch in a browser (Milestone 1).
- A CPU opponent with more deliberate decisions, distance-aware attack choice, better block timing
  and adjustable difficulty.
- Repeatable CPU and GPU benchmarks, desktop against Web.
- Wider tests: complex combat interactions, repeated matches, state transitions, edge cases.
- A test report a stranger can re-run, including the browser environment.

### Originals (2026-11-23, as pasted)

R3. 我的主要参考对象是《拳皇》系列，这是我实际玩过的格斗游戏。我比较欣赏它快节奏的战斗体验、角色移动、攻击时机和防御机制。这些体验影响了我对格斗游戏设计的理解。Dusk Duel 采取了规模更小、更加轻量化的方向。它不追求庞大的角色阵容或竞技性联网对战，而是专注于提供完整的单人格斗体验。我希望让那些只想快速体验一局格斗游戏的玩家能够轻松开始游戏，而不需要下载安装大型游戏、寻找在线对手或进行复杂的配置。目前游戏已经支持 CPU 自动接近玩家、攻击和防御。下一步，我希望让这些行为更加合理、更有策略性，从而提升单人对战体验。关于 Godot： 我建议从这一题删除。它是开发工具，不是玩家体验上的对比对象。可以在项目技术栈部分介绍。

R5. 里程碑 1：在浏览器中完整完成一局比赛。核心 Gameplay 流程已经实现并通过测试。目前已有的测试套件报告为 94 项通过、0 项失败（提交 6317281）。我的第一个新增里程碑是将 Dusk Duel 导出为 Web 版本，并验证玩家能否直接在浏览器中完整完成一局比赛。验收标准：1. 游戏能够在支持的浏览器中成功加载。2. 玩家能够从标题界面开始比赛。3. 角色移动、攻击和防御交互正常。4. CPU 对手能够正常接近、攻击和防御。5. Shader、粒子和动画能够正常渲染。6. 比赛能够正常进入 K.O. 画面。7. 玩家能够重新开始并完成下一局比赛。最终提供浏览器游戏录屏、Web 导出版本，以及记录浏览器环境和兼容性问题的可复现测试报告。这里有一个重要区别：94/0 是已有测试证据，Web 浏览器完整对战则是尚未完成的新目标。

R7. 我选择这个项目，是因为它能够建立在我已有的 Gameplay 编程经验之上，同时让我面对新的工程挑战。已经掌握并有证据支持的技能：3D 资产制作 — Blender 道具（a3）；Shader 和材质开发 — 受击闪白效果及 Shader 测试（a5）；粒子系统 — 受击火花和余烬粒子（a6）；动画和视觉效果 — 灯笼火焰和踢腿弧线动画（a7）；Gameplay 测试 — Edge Case 测试及 TUNING.md（a7）；游戏流程实现 — 完整的标题、战斗、K.O. 和重赛流程；CPU 对手行为 — 已实现基础的自动接近、攻击和防御。希望进一步提升的技能：1. 高级 CPU 行为：在现有 CPU 对手基础上，增加更合理的决策机制、基于距离的攻击选择、更合适的防御时机和可调节的难度等级。目标是让对战更有趣，而不是简单地让 CPU 更频繁地攻击。2. 跨平台游戏交付：学习如何将 Godot 游戏打包并部署到 Web，识别浏览器特有的渲染和输入问题，确保游戏脱离开发环境后仍然能够完整运行。3. 性能分析与优化：建立可重复的 CPU 和 GPU 性能基准，分析粒子效果和 Shader 的资源开销，并评估不同渲染条件下的性能表现。4. Gameplay 质量与可靠性：扩展现有测试，覆盖更复杂的战斗交互、连续重赛、状态转换和边界情况。我尤其希望发展 Gameplay Programming 方向，因为它结合了游戏机制、系统设计、实时交互和问题解决能力。相比于再制作一个孤立的技术 Demo，我希望将现有的 Dusk Duel 实现进一步发展成一个完整、精致、可玩，并且能够被独立验证的游戏作品。

## Revision 3 · 2026-11-23 · Four open points settled by Zhaohui

Zhaohui answered four questions from Claude Code in chat (originals: "1.97版 2.就在这台机器，EDGE
3.对 4.是的"). Translated by Claude Code.

1. **Comparable named:** *The King of Fighters '97* ("97版"), which Zhaohui played.
2. **Milestone 1 is checked** on this machine, in Microsoft Edge. *(Claude Code: the machine is the
   one in A6's measurements: Windows 11, Intel UHD Graphics, OpenGL 3.3. The Edge version is to be
   recorded in the test report when the Web build is run.)*
3. **Target role:** Gameplay Programmer. This settles question 2's two roles.
4. **Question 1:** Zhaohui confirmed ("是的", "yes") Claude Code's summary of what is new: the
   **Web build**, the **stronger CPU opponent with adjustable difficulty**, and the **wider tests**.
   The title → fight → K.O. → replay flow listed in Version 1 already exists (commit `6317281`).
   *(Claude Code: this wording is Claude Code's summary, which Zhaohui confirmed with one word; it
   is not Zhaohui's own sentence.)*

With this revision no **[OPEN]** item from Versions 1 and 2 is left except the length of this brief
(the handout asks for one page).

## Current lists (Claude Code, 2026-11-24, from Versions 1–3; no answer changed)

The handout asks the brief to end with these two lists, so they are repeated here as they now stand.

### Exists today

| What | Where it can be seen |
|---|---|
| Full round: title → round call → fight → K.O. → result → rematch, with a CPU opponent that walks in, kicks, blocks and steps back | commit `6317281`; `test_runner.gd` 94 / 0 (`logs/test_runner_60fps.log:24`, at `8049c54`); the A8 capture (`youtube/walker-dusk-duel-zhaohui-li-a8-pitch/capture/a8_round.log`) |
| Generated art and audio, one image per fighter state | A2 (`SOURCES.md`, `ASSET-LOG.md`) |
| Three Blender 3D props | tag `a3` (`check_props3d.gd` 49 / 0) |
| Hurt-flash shader and materials, hand-written shaders | tag `a5` (`test_hurt_flash` 69 / 0 at 30/60/144 fps; `test_materials` 96 / 0) |
| Hit sparks and embers; GPU cost measured on Intel UHD Graphics (+0.012 / +0.004 ms) | tag `a6`; `TEST-REPORT.md` "GPU price" |
| Lantern flame cycle and kick arc rig; edge tests; tuning log | tag `a7` (`test_kick_edges` 38 / 0; pins 19 / 0; `TUNING.md`) |
| This pitch film | `pitch/README.md` (filename, SHA-256) |

### Will exist

- A Web export that plays a full match and a rematch in Microsoft Edge on this machine (Milestone 1).
- A CPU opponent with more deliberate decisions, distance-aware attack choice, better block timing
  and adjustable difficulty.
- Repeatable CPU and GPU benchmarks, desktop against Web.
- Wider tests: complex combat interactions, repeated matches, state transitions, edge cases.
- A test report a stranger can re-run, naming the browser environment.
