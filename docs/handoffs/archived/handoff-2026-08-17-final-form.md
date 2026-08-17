# Handoff · 2026-08-17 · 确定经验包最终形态（final form）

> 下一个会话建议先读本文件，然后调用 `/grill-me` 或 `/grilling` 与用户对齐「经验包最终应该以什么形态发布」。

## Current State

AI 协作者经验包项目已解决「捕获机制」雾（#1 wayfinder map 中标记为已完成）。现在进入下一片 fog：**最终形态**。

#1 wayfinder map 的 **Not yet specified** 中列出候选：
- 静态网站
- Obsidian 知识库
- Claude Code skill
- 其他

当前已有一个 deployed 的双入口原型：https://li-yongquan.github.io/-2/dual-entry/，但它尚未被正式定位。需要回答的核心问题：

- 它是**可消费的发布产品**（继续打磨 UI/导航/搜索）？
- 它是**人工审核的副产品**（保持原型级别，重点在数据）？
- 它是**未来 skill 的训练语料**（为 Claude Code / Codex skill 提供结构化学习材料）？
- 还是某种**组合形态**？

## Key Artifacts (read these, do not duplicate)

- **Wayfinder 地图**: GitHub issue [#1](https://github.com/li-yongqvan/experience-pack/issues/1)
  - 最终形态 fog 在 "Not yet specified" 中
- **已完成的捕获机制**: `docs/decisions/0011-capture-mechanism.md`
  - Status: **Accepted / M2 Completed**
  - 捕获机制产出 `capture-marker-v0.2` + `#insight` 标签 + `/capture` skill
- **上一个 handoff**: `docs/handoffs/handoff-2026-08-16-capture-mechanism.md`
  - 包含捕获机制阶段的上下文与避坑记录
- **双入口原型代码**: `research/session-format/prototypes/dual-entry/`
- **已部署站点**: https://li-yongquan.github.io/-2/dual-entry/
- **MVP 范围决策**: `docs/decisions/0008-mvp-scope.md`
  - 首包主题为「Grill-me 驱动的里程碑范围切片」
- **审核工作流决策**: `docs/decisions/0009-review-workflow-prototype.md`
- **M9 验证报告**: `docs/decisions/0010-m9-playwright-verification.md`

## Suggested Skills for Next Agent

- **`/grill-me` 或 `/grilling`** — 与用户收敛最终形态决策，明确每种选项的受众、成本、维护责任。
- **`/prototype`** — 如果需要在决策前快速对比不同形态（例如：Obsidian vault 导出 vs 静态站增强 vs skill 输出）。
- **`/wayfinder`** — 决策确定后更新 #1 map，把最终形态 fog 移到 "Decisions so far"。

## What Has Been Done

- #12 锚点修复与 GitHub housekeeping 已完成。
- 捕获机制雾（M2）已完成：
  - `docs/decisions/0011-capture-mechanism.md` 已被接受。
  - `/capture` skill 已可用。
  - `data/samples/capture-mechanism-demo/` 跑通端到端闭环。
- 当前对话开始处理**最终形态**雾。

## Next Actions (in order)

1. 打开 #1 wayfinder map，确认「最终形态」是当前待决 fog。
2. 回顾双入口原型 `research/session-format/prototypes/dual-entry/` 与线上站点 https://li-yongquan.github.io/-2/dual-entry/。
3. 用 `/grill-me` 或 `/grilling` 与用户讨论并收敛到一种（或组合）形态：
   - **产品路线**: 目标学习者是谁？是否需要搜索、目录、进度跟踪、响应式设计？
   - **副产品路线**: 是否只保留最小浏览壳，资源投入回流数据质量与审核流程？
   - **语料路线**: 是否需要为 skill 提供训练/微调格式（如 `SKILL.md`、few-shot examples、context injection spec）？
   - **组合路线**: 数据一次生成，多形态输出（静态站 + Obsidian + skill 语料）。
4. 创建决策文档 `docs/decisions/0012-final-form.md`，记录结论、取舍理由、验收标准。
5. 如果开新 issue，建议编号 #13（#12 已关闭，#11 为捕获机制）。
6. 更新 #1 wayfinder map：
   - 把最终形态从 "Not yet specified" 移除
   - 加到 "Decisions so far"
   - 调整 Frontier tickets 与 blocking 关系图
7. 根据决策制定实施路线图（可另开任务 issue）。

## Pitfalls to Avoid

- **不要让「最终形态」阻塞 #10**：police 第二经验包可以在决策完成前先开始数据切片；形态决策影响的是输出格式，不是数据收集。
- **不要假设只能选一种**：同一套结构化数据很可能同时服务静态站（可读性）、Obsidian（个人知识库）、skill（可执行指导）。关键是决定**主输出**和**维护优先级**。
- **不要过度投资 UI  if 核心价值在数据**：如果目标受众是 AI 辅助学习者，搜索与证据链可能比动画和视觉设计更重要。
- **不要忽略 skill 形态的工程成本**：把经验包变成 Claude Code skill 需要定义 invocation、context injection、few-shot 示例，可能比静态站复杂一个数量级。
- **注意编号连续性**：#11 是捕获机制，#12 已关闭，下一个可用是 #13。

---

**Generated**: 2026-08-17
**Focus for next session**: converge on the final form of the experience package and document the decision.
