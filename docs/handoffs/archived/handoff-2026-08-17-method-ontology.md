# Handoff · 2026-08-17 · 确定方法本体雾（Method Ontology / Taxonomy）

> 下一个会话建议先读本文件，然后调用 `/grill-me` 或 `/grilling` 与用户对齐「协作方法清单与标签体系」。

## Current State

AI 协作者经验包项目已解决多片 fog：
- **捕获机制雾**（#11）：Accepted，`/capture` skill 可用。
- **最终形态雾**（#14）：Accepted，确定为「组合形态，以静态网站为主消费入口 + 未来 skill 语料」。
- **验收标准雾**（#15）：Accepted，A 类/B 类门控、版本晋级、发布闸门已明确。
- **地图维护流程**：已正式化为 `docs/processes/map-maintenance.md`。

现在进入下一片 fog：**方法本体**（Method Ontology / Taxonomy）。

#1 wayfinder map 的 **Not yet specified** 中尚未明确：
- 完整的「协作方法」清单是什么？（当前只有 8 类决策方法）
- 是否还需要「元方法」「反模式」「工具使用技巧」等维度？
- 方法标签如何与 capture mechanism 的 `#insight[method=...]` 语法联动？
- 方法本体最终输出是什么？（schema 扩展？taxonomy 文档？skill 提示词？）

## Key Artifacts (read these, do not duplicate)

- **Wayfinder 地图**: GitHub issue [#1](https://github.com/li-yongqvan/experience-pack/issues/1)
  - 方法本体 fog 在 "Not yet specified" 中
- **捕获机制决策**: `docs/decisions/0011-capture-mechanism.md`
  - `#insight[method=...]` 语法依赖方法本体
- **最终形态决策**: `docs/decisions/0012-final-form.md`
  - 搜索功能需要按「方法主题」聚合
- **验收标准决策**: `docs/decisions/0013-acceptance-criteria.md`
  - 方法标签一致性可能影响 B 类质量门控
- **现有标签体系**: `data/samples/cyber-game-m9/tags-v0.2.json`
  - 当前 4 个轴：`method`、`project_phase`、`theme`、`skill`
- **现有 8 类决策方法**: `research/session-format/schemas/decision-point-v0.2.schema.json`
  - 任务定义、方法选择、范围取舍、上下文注入、提示精炼、约束声明、方向修正、验收/终止
- **地图维护流程**: `docs/processes/map-maintenance.md`
  - 要求新 ticket 先 add to map body，关闭 ticket 先 update map body
- ** police 项目**（可选实证素材）: #10 待开始

## Suggested Skills for Next Agent

- **`/grill-me` 或 `/grilling`** — 与用户收敛方法清单：现有 8 类是否足够、缺什么、哪些需要合并/拆分。
- **`/research`** — 如果要对比其他方法论（如 Bach/Kaner/Bolton 的测试流派、Karpathy 编程五操作法等已有记忆）。
- **`/prototype`** — 如果要把方法标签快速应用到 police 或 cyber-game 样本上做验证。
- **`/wayfinder`** — 方法本体确定后更新 #1 map，把该 fog 移到 "Decisions so far"。

## What Has Been Done

- #12 锚点修复与 GitHub housekeeping 已完成。
- 捕获机制、最终形态、验收标准三片 fog 已 Accepted。
- 地图维护流程已正式化。
- 当前对话准备开始处理方法本体雾。

## Next Actions (in order)

1. 在 GitHub 创建 **#16**（Task: 确定方法本体与标签体系）。
2. **同步 #1 Wayfinder Map**（按 `docs/processes/map-maintenance.md` 的 New Ticket Checklist）：
   - 在 **Frontier tickets** 表格新增 #16。
   - 更新 **Blocking 关系图**（#16 可被 #11、#14、#15 解锁，阻塞于无）。
   - 在 #1 追加评论：`新增 #16 到 Frontier；body 已同步更新。`
3. 收集实证素材：
   - 读取 `data/samples/cyber-game-m9/` 中的决策点与 capture markers。
   - （可选）从 #10 police 项目取 3–5 条初步决策或 capture markers。
4. 用 `/grill-me` 或 `/grilling` 与用户对齐以下问题：
   - 现有 8 类决策方法是否足够覆盖 cyber-game 和 police？
   - 是否需要新增「元方法」「反模式」「工具使用技巧」等维度？
   - 方法标签应该是**扁平列表**还是**层级 taxonomy**？
   - `#insight[method=...]` 中 `method` 的值域从哪里读取？（硬编码 enum / 动态 taxonomy 文件）
   - 方法本体最终产物是什么？建议输出：
     - `docs/decisions/0014-method-ontology.md`
     - 更新 `research/session-format/schemas/tag-v0.2.schema.json`
     - 更新 `research/session-format/schemas/capture-marker-v0.2.schema.json` 的 `method_tag` enum
     - 更新 `data/samples/cyber-game-m9/tags-v0.2.json`
5. 创建决策文档 `docs/decisions/0014-method-ontology.md`。
6. 更新相关 schema 与样本数据。
7. **关闭 #16 前，先更新 #1 Wayfinder Map**：
   - 把方法本体从 "Not yet specified" 移除。
   - 加到 "Decisions so far"。
   - 更新 Frontier tickets 与 Blocking 关系图。
   - 在 #1 追加评论：`#16 已关闭；body 已同步更新。`

## Pitfalls to Avoid

- **不要闭门造车列完美清单**：方法本体应从实际项目（cyber-game、police）中归纳，而不是凭空设计。
- **不要把方法本体变成 #10 的阻塞项**：可以先应用现有 8 类到 police，发现 gap 再扩展。
- **不要忽略与 capture mechanism 的联动**：`#insight[method=...]` 的值域必须与方法本体一致，否则用户会打无效标签。
- **不要一次引入太多维度**：初期保持扁平；层级 taxonomy 可以在有 20+ 个标签后再考虑。
- **注意 issue 编号连续性**：#11 capture、#12 closed、#13 预留/占用、#14 final form、#15 acceptance criteria，方法本体用 **#16**。
- **严格遵循地图维护流程**：创建 #16 和关闭 #16 时都必须先更新 #1 body。

---

**Generated**: 2026-08-17
**Focus for next session**: converge on the method ontology/taxonomy, create #16, sync #1 map, and update related schemas.
