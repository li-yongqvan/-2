# AI 协作者经验包 · Wayfinder

> 把一个项目从开头到结尾散落的有价值经验和错误，从人机对话与代码变更中打捞出来，经人工审核后沉淀为 **可交互工具 + 结构化学习课程**，让后人理解“我是如何与 AI 协作的”。

## 已发布经验包

### v0.2 · cyber-game M8-M9 里程碑范围切片

- **方法主题**：Grill-me 驱动的里程碑范围切片：从 HANDOFF 到 M8-M9 架构决策
- **在线浏览**：https://li-yongqvan.github.io/-2/dual-entry/
- **课程简介**：[`packages/experience-m9-grilling-scope-slice/brief.md`](packages/experience-m9-grilling-scope-slice/brief.md)
- **样本数据**：[`data/samples/cyber-game-m9/`](data/samples/cyber-game-m9/)
- **目标 Demo**：https://li-yongqvan.github.io/cyber-game/
- **发布 ticket**：[#9](https://github.com/li-yongqvan/-2/issues/9)
- **决策记录**：
  - [`docs/decisions/0008-mvp-scope.md`](docs/decisions/0008-mvp-scope.md) — 首包 MVP 范围
  - [`docs/decisions/0009-review-workflow-prototype.md`](docs/decisions/0009-review-workflow-prototype.md) — 人工审核工作流
  - [`docs/decisions/0010-m9-playwright-verification.md`](docs/decisions/0010-m9-playwright-verification.md) — M9 Demo 验证报告

## 仓库导航

| 目录 | 内容 |
|---|---|
| [`docs/`](docs/) | GitHub Pages 源目录，含决策记录、schema 索引、工具说明 |
| [`docs/schemas/`](docs/schemas/) | 经验包 v0.2 JSON Schema 索引 |
| [`docs/tools/`](docs/tools/) | 脱敏/生成/验证脚本说明 |
| [`research/session-format/schemas/`](research/session-format/schemas/) | 9 个 JSON Schema 源文件 |
| [`scripts/`](scripts/) | 可复用批处理脚本 |
| [`research/session-format/prototypes/`](research/session-format/prototypes/) | 原型工具（会话-git 对齐、审核工作流、双入口浏览） |

## 核心理念

- 核心不是项目本身，而是展示“人与 AI 的协作方法”。
- 组织结构采用 **C3 双入口**：既可以从“方法主题”进入，也可以从“项目时间线”进入。
- 信息采集来源锁定 **Claude Code 本地会话记录** + **git 历史/diff**。
- 终端处理必须先产出结构化中间数据（JSON/JSONL），再经人工审核生成最终产物。

## 当前 frontier

- [#9](https://github.com/li-yongqvan/-2/issues/9) · 把 cyber-game M8-M9 经验包打磨到可发布 — **已完成 ✅**
- [#10](https://github.com/li-yongqvan/-2/issues/10) · 用同样方法处理 police 项目作为第二经验包 — 待开始

详情见 Wayfinder 地图：[#1](https://github.com/li-yongqvan/-2/issues/1)
