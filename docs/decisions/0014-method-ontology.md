# Decision 0014: 方法本体与标签体系（Method Ontology / Taxonomy）

## Status

**Accepted** — 经 `/grill-me` 与用户对齐，作为 #18 跟踪。

- 父地图：[#1 AI 协作者经验包 · Wayfinder](https://github.com/li-yongqvan/experience-pack/issues/1)
- 解决 fog：**完整的“协作方法”清单是什么，以及如何与标签、捕获机制联动**
- 前置决策：[#5 决策点分类](https://github.com/li-yongqvan/experience-pack/issues/5)、[#13 捕获机制](0011-capture-mechanism.md)、[#14 最终形态](0012-final-form.md)、[#15 验收标准](0013-acceptance-criteria.md)
- 关联流程：[`docs/processes/map-maintenance.md`](../processes/map-maintenance.md)

---

## Context

经验包项目已解决捕获机制雾（#13）、最终形态雾（#14）、验收标准雾（#15）。#1 Wayfinder Map 的 **Not yet specified** 中仍有一片关键 fog：

> 完整的“协作方法”清单是什么？方法标签如何与 `#insight[method=...]` 和 `/capture` skill 联动？方法本体最终输出是什么？

现有 8 类决策方法来自 [#5](https://github.com/li-yongqvan/experience-pack/issues/5)：任务定义、方法选择、范围取舍、上下文注入、提示精炼、约束声明、方向修正、验收/终止。这些 tag 同时被 `decision-point-v0.2.schema.json`、`capture-marker-v0.2.schema.json` 和 `tags-v0.2.json` 使用。

本决策通过与用户对齐，确定方法本体的范围、层级、来源与最终产物。

---

## Decision

| # | 决策点 | 结论 |
|---|---|---|
| 1 | 现有 8 类决策方法是否足够？ | **作为 baseline 保持不变**。cyber-game 和 police 若出现无法归类的决策，再按“新增/合并/拆分”流程扩展。 |
| 2 | 是否新增其他维度？ | **新增 `collaboration_pattern` 轴**，初始 tag 为 `collaboration_pattern.grilling`、`collaboration_pattern.plan_mode`、`collaboration_pattern.prototype`、`collaboration_pattern.capture`、`collaboration_pattern.review`；「反模式」和「工具使用技巧」暂不加。 |
| 3 | 标签是扁平还是层级？ | **保持扁平**。当某个 axis 下 tag 数量 ≥ 15 或出现明显子群时，再考虑用 `parent_id` 引入层级。 |
| 4 | `method` 值域来源？ | **`method-ontology-v0.2.json` 是 method 与 collaboration_pattern 的权威来源**。`capture-marker-v0.2.schema.json` 的 enum 是它的快照，必须同步维护；`tags-v0.2.json` 必须包含该来源定义的全部 tag。 |
| 5 | 最终产物？ | `docs/decisions/0014-method-ontology.md`、`research/session-format/schemas/method-ontology-v0.2.json`、更新 `tags-v0.2.json`、更新 `capture-marker-v0.2.schema.json`（新增 `collaboration_pattern_tag`）。 |

---

## Method Axis（8 + 0）

保持 [#5](https://github.com/li-yongqvan/experience-pack/issues/5) 定义的 8 类：

| tag id | 中文 | 英文 |
|---|---|---|
| `method.task_definition` | 任务定义 | Task Definition |
| `method.method_selection` | 方法选择 | Method Selection |
| `method.scope_tradeoff` | 范围取舍 | Scope Tradeoff |
| `method.context_injection` | 上下文注入 | Context Injection |
| `method.prompt_refinement` | 提示精炼 | Prompt Refinement |
| `method.constraint_declaration` | 约束声明 | Constraint Declaration |
| `method.course_correction` | 方向修正 | Course Correction |
| `method.acceptance_termination` | 验收/终止 | Acceptance / Termination |

扩展条件：police 或其他项目出现 3 条以上无法归入现有 8 类的决策点时，触发扩展评审。

---

## Collaboration Pattern Axis（新增）

`collaboration_pattern` axis 用来标记“这条经验是通过哪种人机协作交互模式得到的”，而不是“这条经验在做什么决策”。

| tag id | 中文 | 英文 |
|---|---|---|
| `collaboration_pattern.grilling` | Grill-me 追问 | Grill-me |
| `collaboration_pattern.plan_mode` | Plan Mode | Plan Mode |
| `collaboration_pattern.prototype` | 原型验证 | Prototype |
| `collaboration_pattern.capture` | 捕获机制 | Capture Mechanism |
| `collaboration_pattern.review` | 审阅 / Review | Review |

引入原因：
- 搜索时需要能回答“grill-me / plan mode / prototype / capture / review 都在哪些场景下被用过”。
- `collaboration_pattern` 维度不污染 `method` 轴的语义；`method` 仍只描述决策内容。
- 当前项目已有 `/grill-me`、Plan Mode、`/capture`、`/prototype`、code-review 等真实机制，素材充足。

---

## Why 保持 8 类 baseline

- cyber-game M9 的 20 条 decision points 已完整覆盖 8 类，说明当前分类足以描述项目切片。
- 过早扩展会导致标签稀疏、搜索聚合时噪声大。
- “先应用，发现 gap 再扩展”符合 `docs/processes/map-maintenance.md` 的增量原则。

## Why 只加 collaboration_pattern，不加反模式和工具技巧

- `collaboration_pattern` 维度有现成的机制（grilling / plan mode / prototype / capture / review）和真实样本，不是空架子。
- 「反模式」和「工具使用技巧」目前素材不足；强行加入会变成只有少数几条 tag 的“死维度”。
- 当 capture 积累到 20+ 条有明显反面教材或可复制技巧时，再单独开 decision 评审。

## Why 扁平

- 当前 method 8 个、theme 8 个、skill 2 个，层级会过度设计。
- 扁平更匹配 `#insight[method=scope_tradeoff]` 的短语法。
- `tag-v0.2.schema.json` 已预留 `parent_id`，未来分层是后向兼容的增量改动。

## Why method-ontology-v0.2.json 作为权威来源

- 避免 `#insight[method=...]` 里出现 schema 认识但 taxonomy 里没有的“幽灵 tag”。
- 最终形态的搜索聚合（#14）会从 ontology 读取 method / collaboration_pattern 维度，schema 必须与之一致。
- 当前阶段手动同步 schema enum；未来 tag 多了再考虑自动生成。

---

## Verification Criteria

1. `docs/decisions/0014-method-ontology.md` 已提交并链接到 #1、#18。
2. `research/session-format/schemas/method-ontology-v0.2.json` 包含 method 8 个值与 collaboration_pattern 5 个值。
3. `data/samples/cyber-game-m9/tags-v0.2.json` 包含 `collaboration_pattern` axis 与 5 个 collaboration_pattern tag。
4. `data/samples/capture-mechanism-demo/tags-v0.2.json` 同步包含 `collaboration_pattern` axis。
5. `capture-marker-v0.2.schema.json` 新增可选 `collaboration_pattern_tag` enum，值域与 ontology 一致。
6. `capture-marker-v0.2.schema.json` 的 `method_tag` enum 与 `method-ontology-v0.2.json` 的 method axis 一致。
7. `validate-experience-v0.2.py` 对现有样本数据仍输出 0 schema errors（新增 axis 不破坏旧数据）。
8. #1 Wayfinder Map 将方法本体 fog 从 Not yet specified 移除，并加入 Decisions so far；#18 关闭。

---

## Deliverables

1. `docs/decisions/0014-method-ontology.md` — 本文件。
2. `research/session-format/schemas/method-ontology-v0.2.json` — 方法本体权威值列表。
3. 更新 `data/samples/cyber-game-m9/tags-v0.2.json`。
4. 更新 `data/samples/capture-mechanism-demo/tags-v0.2.json`。
5. 更新 `research/session-format/schemas/capture-marker-v0.2.schema.json`。
6. #1 Wayfinder Map 更新：把方法本体从 Not yet specified 移到 Decisions so far，关闭 #18。

---

## Open Questions

| 问题 | 建议处理 |
|---|---|
| police 项目中是否会出现第 9 类 method？ | 推进 #10 时观察；若出现 3 条以上无法归类，再开 decision 扩展。 |
| 反模式/工具技巧维度何时加入？ | 当 capture 积累 ≥ 20 条且有明确反面教材或可复制技巧时评审。 |
| 是否需要 schema enum 自动生成脚本？ | tag 数量 ≥ 15 或 method axis 扩展时再考虑，当前手动同步成本更低。 |
| `skill` 轴与 `collaboration_pattern` 轴的重叠（如 `skill.grilling` 与 `collaboration_pattern.grilling`）是否清理？ | 本期保留；未来若 dual-entry 渲染出现重复，再评估合并或重命名。 |

---

## Related Issues

- Parent map: [#1](https://github.com/li-yongqvan/experience-pack/issues/1)
- This decision: **#18**
- Blocked by: [#5](https://github.com/li-yongqvan/experience-pack/issues/5)、[#13](https://github.com/li-yongqvan/experience-pack/issues/13)、[#14](https://github.com/li-yongqvan/experience-pack/issues/14)、[#15](https://github.com/li-yongqvan/experience-pack/issues/15)
- Unblocks: #14 最终形态的搜索聚合、#10 police 第二经验包的标签使用
