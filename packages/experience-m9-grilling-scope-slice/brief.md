# 经验包：Grill-me 驱动的里程碑范围切片

## 一句话简介

通过一个真实的 cyber-game M8-M9 里程碑，展示如何在 Claude Code 里用 `grill-me` 技能把模糊的「执行 M9 规划」拆解为可验收、可执行的子任务，并在每一步做出明确的范围与架构决策。

## 适合谁看

- 刚接触 AI 辅助开发、容易把「帮我做」直接丢给 AI 的人
- 在里程碑边界经常过度设计、做超出当期范围的功能的人
- 想学习如何用结构化提问来收敛需求、控制范围的人

## 学习目标

看完本包后，学习者能够：

1. 识别一个模糊任务中隐含的范围、验收、输出位置歧义。
2. 使用 `grill-me` 式追问把大任务切成可验收的小块。
3. 在 8 类决策（任务定义、方法选择、范围取舍、上下文注入、提示精炼、约束声明、方向修正、验收/终止）中定位自己的当前决策。
4. 把决策与代码变更对应起来，理解「为什么这里要这样写」。

## 核心叙事

```
HANDOFF.md（模糊指令）
    ↓
grill-me 追问：你到底要做什么？做到什么程度？输出到哪里？
    ↓
16 条范围/架构决策（M8-M9） + 4 条验收阶段 QA 决策
    ↓
commit dd93cc9：sandbox + gamification + progress persistence
    ↓
线上 Demo：https://li-yongqvan.github.io/cyber-game/
```

## 素材清单

| 素材 | 位置 | 用途 |
|---|---|---|
| 脱敏主会话 | `data/samples/cyber-game-m9/session-be0044d7-scrubbed.jsonl` | 展示原始对话与 AI 协作过程 |
| 脱敏子代理 | `data/samples/cyber-game-m9/subagent-abe9460ea165d5867-scrubbed.jsonl` | 展示多代理决策提取 |
| 决策点 | `data/samples/cyber-game-m9/decision-points.jsonl` | 20 条结构化决策 |
| Git 对齐 | `data/samples/cyber-game-m9/git-alignment.json` | 会话到 commit 的映射 |
| 脱敏规则 | `data/samples/cyber-game-m9/scrubbing-manifest.json` | 隐私处理方法 |

## 关键决策示例

### 示例 1：范围取舍 — M8-M9 合并还是拆分？

- **问题**：两个里程碑一次做完，还是分两次验收？
- **选项 A**：合并推进，减少交接开销，但改动量大。
- **选项 B**：拆分推进，每次独立验收，风险可控。
- **选择**：B. 拆分推进。
- **代码影响**：`src/store/simulatorStore.ts`、`src/store/progressStore.ts` 的拆分实现。

### 示例 2：约束声明 — Router 在沙盒中占位

- **问题**：Router 的三层转发还没实现，沙盒里怎么办？
- **选项 A**：阻塞 M8 先实现 Router。
- **选项 B**：用 Firewall 代替 Router。
- **选项 C**：占位 Router，标注"即将上线"。
- **选择**：C. 占位 Router。
- **代码影响**：`src/engine/devices/Router.ts` 维持占位，`src/ui/Sandbox.tsx` 中 Router 按钮带提示。

### 示例 3：验收/终止 — 退出 plan mode 开始执行

- **问题**：细节已收敛，是否退出 plan mode 跑验收？
- **选择**：同意退出并开始执行。
- **教学点**： grilling 不是无止境讨论，而是为了获得「可以动手」的明确信号。

## 双入口浏览建议

### 按项目时间线

1. 读 `HANDOFF.md` 中的 M9 目标
2. 看 grill-me 如何追问歧义
3. 浏览 16 条决策记录
4. 查看 `dd93cc9` 的代码变更
5. 打开 Demo 验证结果

### 按方法主题

- **任务定义**：Q1「本次执行 M9 的规划希望做什么？」
- **范围取舍**：决策 1「M8-M9 合并还是拆分？」、决策 12「徽章评分粒度」
- **约束声明**：决策 11「关卡解锁规则」、决策 15「Router 占位」
- **验收/终止**：Q4「是否退出 plan mode 开始执行？」

## 可交互设计草图

1. **对话时间轴**：左侧显示用户提示，右侧显示 AI 回复，关键决策点高亮并可点击展开。
2. **决策卡片**：每张卡片显示问题、选项、选择、代码影响，点击文件跳转到 git diff。
3. **方法主题过滤器**：按 8 类决策筛选卡片。
4. **代码证据面板**：显示决策对应的 git diff 片段。

## 隐私说明

本包已做以下脱敏：
- 本地路径替换为 `<HOME>`、`<PROJECT_ROOT>`、`<CLAUDE_HOME>`。
- Windows 用户名替换为 `<USER>`。
- 文件历史快照替换为占位符。
- 会话中发现的服务器凭据已替换为 `<SERVER_IP>`、`<SERVER_PASSWORD>`。
- 原始中文对话保留作为协作记录。

## 后续扩展

- 把同一条 `grill-me` 流程应用到 `police` 项目，做成「从过度设计中学习」的第二包。
- 增加「反事实路径」：如果当时选了 A（合并推进），代码结构会是什么样子？
- 增加互动练习：给学习者一个模糊任务，让他们写出自己的 grill-me 追问清单。
