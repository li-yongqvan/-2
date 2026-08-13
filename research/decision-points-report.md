# 自动识别对话中的关键决策点

> 研究任务 #5：wayfinder map of `li-yongqvan/-2`（AI experience pack）  
> 目标：在人类与 AI 协作的对话流中，自动发现值得沉淀为「经验包」的关键决策时刻。

---

## 1. 什么是「决策点」？

在本项目语境下，**决策点（decision point）**指对话中人类对以下任一方面做出明确选择、修正或承诺的时刻：

- **Workflow（工作流）**：选择怎么协作、分几步、用什么工具链。
- **Context Engineering（上下文工程）**：决定把哪些文件、记忆、外部资料注入对话。
- **Prompt Engineering（提示工程）**：改写、追加、精炼提示，以改变 AI 输出。
- **Constraint Engineering（约束工程）**：增加、放宽或调整约束条件（代码风格、范围、性能、依赖等）。

一个决策点通常具备三个特征：

1. **选择性**：存在至少两种可行路径，人类明确选了其中一条。
2. **可逆性（部分）**：该决定可以被后续对话修改、撤销或细化。
3. **可迁移性**：该决定对未来类似任务有参考价值，值得被记录、复用或教学。

> 反例：纯事实问答（「Python 的 list 怎么排序？」）、礼貌寒暄、单次且未被修改的代码生成，通常不构成决策点，除非它触发了后续大量修正。

---

## 2. 值得保留的对话时刻

基于项目目标，以下八类时刻最值得被识别并沉淀。

| 类别 | 典型场景 | 为什么值得保留 |
|------|----------|----------------|
| **任务/目标定义** | 「我想做一个周报提交页面」「我们来修这个 bug」 | 决定项目范围与成功标准 |
| **方法/流程选择** | 「用 TDD」「先写方案再写代码」「走 grilling 流程」 | 工作流（workflow）决策 |
| **范围取舍** | 「先不做登录」「忽略移动端」「只做核心链路」 | 范围约束，后续易膨胀 |
| **上下文注入** | 上传文件、引用 issue、调用 memory/skill、粘贴错误日志 | 上下文工程决策 |
| **提示精炼** | 「请用更简洁的方式」「加上异常处理」「给三个不同方案」 | 提示工程决策 |
| **约束声明/调整** | 「必须用 TypeScript」「不要超过 100 行」「禁止新增依赖」 | 约束工程决策 |
| **方向修正** | 「不对，应该是…」「回退到上一个版本」「我们换条路」 | 纠正偏差，反映真实迭代 |
| **验收/终止** | 「LGTM」「可以合并」「这个方向放弃」 | 决策闭环，形成可引用结论 |

这些时刻共同构成一个「决策谱系」：从目标出发，经过方法、上下文、提示、约束的多次调整，最终收敛到验收结论。

---

## 3. 自动检测的启发式信号

决策点检测应采用**多层信号融合**策略，而非单一规则。以下是可按优先级组合的信号。

### 3.1 词汇/句式信号（轻量、可解释）

**承诺类**

- 「我们…」「 let's …」「就按…来」「决定…」
- 「采用…」「使用…」「走…流程」「调用…skill」

**范围类**

- 「先不做…」「忽略…」「限定在…」「范围是…」
- 「MVP」「最小可用」「核心链路」

**约束类**

- 「必须…」「禁止…」「不超过…」「至少…」「只能…」
- 「no external deps」「pure TypeScript」「under 100 lines」

**修正类**

- 「不对」「错了」「重新…」「回退」「revert」「undo」「改回…」
- 「不是…而是…」「actually」「wait」

**验收类**

- 「LGTM」「可以了」「合并」「ship it」「到此为止」「放弃」

### 3.2 结构信号（来自对话元数据）

| 信号 | 说明 |
|------|------|
| **工具/Skill 调用** | 调用 `Skill`、`Run`、`TDD`、`grilling` 等，通常标志方法选择 |
| **文件操作** | 上传/读取/编辑文件，尤其是连续多次编辑同一文件 |
| **代码块生成后的用户回复** | AI 输出代码后用户立即回复，往往包含修正或确认 |
| **多轮同类工具调用** | 同一工具连续调用 3 次以上，暗示迭代收敛或卡壳 |
| **消息长度突变** | 用户消息突然变长（补充约束）或变短（给出结论） |
| **引用/链接** | 引用 issue、PR、文档、memory 条目，标志上下文工程 |

### 3.3 时序/交互模式信号

- **ABABA 式拉锯**：AI 给出方案 → 用户否定 → AI 修改 → 用户再否定，极大概率蕴含决策变化。
- **收敛模式**：连续多轮修改后用户说「好/可以/合并」，应标记为验收点。
- **发散模式**：用户连续提出多个不同方向（「或者…」「另一种方案…」），可能触发方法选择。
- **沉默后重启**：长时间停顿后用户提出新目标，可能是任务切换。

### 3.4 语义漂移信号（需嵌入或 LLM）

- **主题转移**：前后两句的语义中心显著变化（可用 sentence embedding 余弦距离衡量）。
- **意图转移**：从「询问」到「命令」、从「探索」到「决策」。
- **情绪/确信度变化**：用户从犹豫（「也许」「试试」）到笃定（「就这个」）。

### 3.5 信号优先级建议

建议按「强规则 → 结构规则 → 语义规则」逐层过滤：

1. **强规则命中**（如显式出现「决定」「采用」「回退」「LGTM」）直接标记为高置信度决策点。
2. **结构规则命中**（如 skill 调用、连续文件修改）作为中置信度候选。
3. **语义漂移**作为低置信度候选，交由 LLM 二次确认。

---

## 4. LLM 分类/标注步骤

### 4.1 是否必要？

**建议引入 LLM 作为第二道分类器**，原因如下：

- 自然语言决策点高度依赖上下文，纯规则召回率低、误报高。
- LLM 可综合词汇、结构、语义三类信号，输出结构化标签。
- 可解释性强：LLM 可给出判断理由，便于人工 review。

但 LLM 不应是第一步。先用规则召回候选，再用 LLM 精排，可显著降低成本与延迟。

### 4.2 输入与输出设计

**输入**：一段对话窗口（建议 5–10 轮，包含用户与 AI 消息、工具调用记录、文件变更摘要）。

**输出 schema**：

```json
{
  "decision_points": [
    {
      "turn_range": [3, 5],
      "type": "constraint_engineering",
      "subtype": "add_dependency_constraint",
      "confidence": 0.87,
      "summary": "用户明确要求使用 TypeScript 且禁止新增外部依赖",
      "quote": "请用 TypeScript 实现，不要引入新依赖",
      "reversibility": "medium",
      "transfer_value": "high",
      "reason": "该约束直接影响后续代码实现方案，对未来同类项目有参考价值"
    }
  ]
}
```

**类型枚举**：

- `goal_definition`：目标/任务定义
- `workflow_selection`：工作流/方法选择
- `scope_decision`：范围取舍
- `context_engineering`：上下文注入/调整
- `prompt_engineering`：提示精炼
- `constraint_engineering`：约束声明/调整
- `direction_correction`：方向修正/回退
- `acceptance_closure`：验收/终止

### 4.3 推荐 Prompt（可直接使用）

```markdown
You are an annotator for human-AI collaboration conversations. Your job is to identify "decision points" — moments where the human explicitly chooses, adjusts, or commits to a course of action regarding workflow, context engineering, prompt engineering, or constraint engineering.

Given the following conversation segment, output a JSON object with a list of decision points. For each decision point, include:
- turn_range: the turn indices involved
- type: one of [goal_definition, workflow_selection, scope_decision, context_engineering, prompt_engineering, constraint_engineering, direction_correction, acceptance_closure]
- subtype: a more specific label (optional)
- confidence: 0.0 to 1.0
- summary: one-sentence description
- quote: the exact or paraphrased user utterance that signals the decision
- reversibility: low / medium / high
- transfer_value: low / medium / high — how useful this decision is for future similar tasks
- reason: why this is a decision point

Rules:
1. Only include moments where the human makes a clear choice, correction, or commitment.
2. Do not mark routine Q&A, greetings, or pure acknowledgments.
3. If a decision is later revised, mark both the original and the revision.
4. Be conservative: a missed decision point is better than a false one.

Conversation:
{{conversation_segment}}

Output only valid JSON.
```

### 4.4 评估标准

| 指标 | 说明 | 目标值 |
|------|------|--------|
| **Precision@k** | 前 k 个候选中确实是决策点的比例 | ≥ 0.80 |
| **Recall** | 人工标注决策点中被自动检出的比例 | ≥ 0.70 |
| **类型准确率** | 决策点类型与人工标注一致的比例 | ≥ 0.75 |
| **F1** | 综合精确率与召回率 | ≥ 0.75 |
| **人均 review 时间** | 人工确认/拒绝一个候选所需时间 | ≤ 15 秒 |
| **有用率** | 被保留并进入经验包的决策点比例 | ≥ 0.60 |

评估方法：

1. 准备 100–200 段真实对话，由 2 名标注者独立标注决策点。
2. 对比规则系统、LLM、规则+LLM 三者的表现。
3. 对 LLM 输出进行人工审核，统计误报类型并回流优化 prompt。

---

## 5. 自动检测 + 人工审核的混合流程

推荐的流水线如下：

```
对话流
  │
  ▼
┌─────────────────┐
│  规则召回层      │  ← 词汇/结构/时序信号，快速筛选候选
│  (低延迟、高召回) │
└─────────────────┘
  │
  ▼
┌─────────────────┐
│  LLM 精排层      │  ← 对候选窗口做分类、置信度、摘要
│  (可解释、结构化) │
└─────────────────┘
  │
  ▼
┌─────────────────┐
│  候选队列        │  ← 按置信度与转移价值排序
└─────────────────┘
  │
  ▼
┌─────────────────┐
│  人工 Review     │  ← 确认 / 编辑 / 合并 / 丢弃
│  (wayfinder UI)  │
└─────────────────┘
  │
  ▼
┌─────────────────┐
│  经验包沉淀      │  ← 进入可学习、可检索、可复用的决策库
└─────────────────┘
```

### 5.1 各阶段要点

**规则召回层**

- 使用正则 + 关键词 + 工具调用元数据，生成候选片段。
- 每个候选附带触发信号，便于后续解释。
- 目标：召回率优先，允许较高误报。

**LLM 精排层**

- 对候选片段做二分类 + 多标签分类。
- 输出摘要、引用、置信度，减少人工阅读成本。
- 对高置信度（≥ 0.90）候选可自动进入待审队列；低置信度（< 0.60）直接丢弃；中间区间强制人工审核。

**人工 Review 层**

- 提供「确认」「编辑」「合并」「丢弃」四键操作。
- 展示原始对话片段、AI 摘要、触发信号，帮助快速判断。
- 允许标注者修正类型、补充理由、关联相关决策点。
- Review 结果回流训练/优化规则与 prompt。

### 5.2 反馈闭环

- **误报分析**：每周汇总被丢弃的候选，提炼新的排除规则。
- **漏报挖掘**：随机抽样未被召回的对话，人工补充决策点，反向优化召回策略。
- **Prompt 迭代**：根据类型错误和摘要质量问题，微调 LLM prompt。
- **人工偏好学习**：记录不同标注者的修正模式，逐步统一标准。

---

## 6. 落地建议

### 6.1 最小可行方案（MVP）

1. **收集数据**：从现有项目记忆（如 `grilling-decisions/`、`memory/`）中提取 50–100 段已记录的决策对话作为金标准。
2. **实现规则召回器**：覆盖 3.1 与 3.2 中的高频信号。
3. **接入 LLM 分类器**：使用上述 prompt，输出 JSON。
4. **构建 Review UI**：一个简单列表页，显示候选、置信度、操作按钮。
5. **沉淀经验包**：确认后的决策点写入结构化 Markdown/JSON，供 wayfinder map 引用。

### 6.2 技术选型建议

| 组件 | 建议 |
|------|------|
| 规则引擎 | Python `regex` + 自定义信号字典，便于迭代 |
| 语义漂移 | OpenAI/MiniMax 等嵌入模型计算余弦距离 |
| LLM 分类器 | Claude / GPT-4o / 同量级模型，JSON mode |
| 存储 | SQLite/PostgreSQL 存候选，Markdown 存沉淀 |
| Review UI | 优先复用现有项目前端栈（如 Vite + React） |

### 6.3 与 wayfinder map 的衔接

每个被确认的决策点可以成为 wayfinder map 上的一个节点：

- 节点类型对应决策类别（workflow、context、prompt、constraint）。
- 节点之间用「细化」「修正」「回退」等边连接，形成决策谱系。
- 节点内容包含：原始引用、摘要、转移价值、可复用建议。

---

## 7. 风险与缓解

| 风险 | 缓解措施 |
|------|----------|
| **规则召回率低** | 从金标准数据倒推高频信号，持续补充规则 |
| **LLM 幻觉摘要** | 要求输出必须包含 `quote` 字段，人工可一键定位原文 |
| **人工审核负担重** | 提高高置信度自动通过阈值，低置信度自动丢弃 |
| **类型标准不统一** | 建立标注指南，双人标注 + Kappa 一致性校验 |
| **隐私/敏感信息泄露** | 候选与沉淀中自动过滤密钥、token、个人身份信息 |

---

## 8. 下一步行动

1. 在 `research/decision-points` 分支建立 `experiments/` 目录，放入规则召回器原型。
2. 收集并标注 100 段真实对话作为评估集。
3. 跑通「规则 + LLM + 人工 review」的最小闭环。
4. 输出下一份报告：《决策点标注指南与评估结果》。

---

## 参考

- 本项目相关记忆：
  - `grilling-decisions/m8-m9-sandbox-gamification-decisions.md`
  - `memory/Grilling Auto Record Convention.md`
  - `memory/Grilling M8-M9 Sandbox/Gamification Decisions.md`
- GitHub Issue: https://github.com/li-yongqvan/-2/issues/5
