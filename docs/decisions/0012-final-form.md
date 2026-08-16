# Decision 0012: 经验包最终形态

## Status

**Accepted** — 经 `/grill-me` 与用户达成一致。采用「最终形态愿景 + 分阶段推进」策略，不一步到位。

- 父地图：[#1 AI 协作者经验包 · Wayfinder](https://github.com/li-yongqvan/-2/issues/1)
- 解决 fog：**经验包的最终发布形态**
- 前置决策：[#8 MVP 范围](0008-mvp-scope.md)、[#11 捕获机制](0011-capture-mechanism.md)
- 实现任务：[#14](https://github.com/li-yongqvan/-2/issues/14)

---

## Context

#1 wayfinder map 的 **Not yet specified** 中列出候选：

- 静态网站
- Obsidian 知识库
- Claude Code skill
- 其他

当前已有一个 deployed 的双入口原型：`https://li-yongqvan.github.io/-2/dual-entry/`，但它尚未被正式定位。需要回答的核心问题是：

- 它是**可消费的发布产品**（继续打磨 UI/导航/搜索）？
- 它是**人工审核的副产品**（保持原型级别，重点在数据）？
- 它是**未来 skill 的训练语料**（为 Claude Code / Codex skill 提供结构化学习材料）？
- 还是某种**组合形态**？

本决策在 grilling 后收敛为：**组合形态，但以静态网站为主消费入口，并为未来 skill 准备训练语料；同时明确不一步到位，分阶段推进。**

---

## Decision

| # | 决策点 | 结论 |
|---|---|---|
| 1 | 最终定位 | **组合形态**：内部新人培养产品 + 未来 skill 训练语料 |
| 2 | 目标受众 | **刚入职的开发/AI 协作新人** |
| 3 | 主消费形态 | **静态网站**（在现有双入口原型上增强） |
| 4 | 网站组织方式 | **混合：项目 × 主题** |
| 5 | 网站必需功能 | 搜索、目录/导航、响应式 |
| 6 | 网站暂不需要 | 进度跟踪（降低初期复杂度） |
| 7 | skill 语料形态 | **SKILL.md + few-shot examples + context injection spec** |
| 8 | 内容审核流程 | **双轨制**：草稿区 → 正式发布区 |
| 9 | 维护责任 | **AI 辅助初筛 + 人工最终确认** |
| 10 | 发布节奏 | **按里程碑发布** |
| 11 | 与现有原型关系 | **在现有双入口原型上增量增强**，不重新设计 |
| 12 | 推进策略 | **分阶段推进**，第一阶段优先落地搜索功能 |

---

## Phase 1: 静态网站搜索功能

### 范围

- **数据范围**：仅搜索「正式发布区」内容，不包含草稿区。
- **实现方式**：前端本地搜索（当前内容量小，部署简单）。
- **搜索粒度**：按 capture/insight 切片匹配，而非整篇文章。

### 验收标准

1. 在 `https://li-yongqvan.github.io/-2/dual-entry/` 上可输入关键词搜索。
2. 搜索结果按 capture/insight 切片展示，包含标题、摘要、所属项目/主题。
3. 支持响应式布局。
4. 不引入后端服务或数据库。

---

## Why 组合形态

- 静态网站门槛低、可搜索、可分享，最适合刚入职的新人快速消费。
- 同一套结构化数据（capture markers、decision points、experience units）可以复用为 skill 语料，避免重复维护。
- skill 是未来形态，但工程成本远高于静态站，需要单独迭代，不应阻塞网站交付。
- 不一步到位可以降低初期投入，先验证「新人是否愿意用」，再决定是否追加功能。

## Why 静态网站为主消费形态

- 已有部署基础，重构成本可控。
- 不需要安装 Obsidian 或 Claude Code 就能访问。
- 搜索和目录是新人培养的核心需求，静态站最容易实现。

## Why 暂不需要进度跟踪

- 增加状态存储、用户认证或本地持久化，复杂度上升一个数量级。
- 初期可以通过内容组织（项目 × 主题）和按里程碑发布提供隐性学习路径。
- 若后续有强需求，可在 Obsidian 或 skill 形态中补。

## Why 双轨审核 + AI 初筛

- capture 机制产出的是 opportunistic 信号，质量不稳定，不能直接发布。
- 纯人工审核容易堆积，纯 AI 审核容易漏掉语境问题。
- 双轨制让原始 captures 进入草稿区，经 AI 初筛 + 人工确认后再进入正式发布区。

## Why 按里程碑发布

- 经验包内容本身就是项目切片，按 milestone 发布天然匹配内容节奏。
- 便于新人跟踪项目演进，也便于维护者批量审核。

---

## Verification Criteria

1. **决策文档**
   - 本文件已提交并链接到 #1、#13。

2. **第一阶段交付**
   - 双入口原型增加搜索功能并重新部署。
   - 搜索覆盖正式发布区内容。
   - 移动端可正常浏览和搜索。

3. **与现有流程不冲突**
   - 不改动 capture mechanism 的数据结构。
   - 不阻塞 #10 police 第二经验包的推进。

4. **后续阶段可扩展**
   - 目录结构预留「项目 × 主题」扩展点。
   - skill 语料格式在决策中已明确，后续可独立实施。

---

## Deliverables

1. `docs/decisions/0012-final-form.md` — 本文件。
2. #1 wayfinder map 更新：把「最终形态」从 Not yet specified 移到 Decisions so far。
3. #13 任务 issue：跟踪第一阶段搜索功能实施。
4. （第一阶段）双入口原型搜索功能增强与部署。

---

## Next Actions

1. ✅ 创建 `docs/decisions/0012-final-form.md`。
2. 更新 #1 wayfinder map。
3. 创建 #14 任务 issue，指定第一阶段目标为搜索功能。
4. 实施第一阶段：在 dual-entry 原型上加前端本地搜索。
5. 部署并验证。
6. 后续阶段（待 #14 完成后规划）：目录重组织、双轨审核流程 UI、skill 语料产出。

---

## Related Issues

- Parent map: [#1](https://github.com/li-yongqvan/-2/issues/1)
- This decision: **#14**（实现记录与验证）
- Blocked by: [#8](https://github.com/li-yongqvan/-2/issues/8)、[#11](https://github.com/li-yongqvan/-2/issues/11)
- Unblocks: 第一阶段搜索功能实施
