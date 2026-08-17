# AI 协作者经验包 · Wayfinder

## cyber-game M8-M9 v0.2

首个可发布的经验包，主题：**Grill-me 驱动的里程碑范围切片：从 HANDOFF 到 M8-M9 架构决策**。

### 快速入口

- **双入口浏览原型**：[/experience-pack/dual-entry/](/experience-pack/dual-entry/) — 按方法主题或项目时间线浏览 20 个经验单元（新增 [/experience-pack/dual-entry/search/](/experience-pack/dual-entry/search/) 本地搜索）
- **经验包简介**：[packages/experience-m9-grilling-scope-slice/brief.md](/experience-pack/packages/experience-m9-grilling-scope-slice/brief.md)
- **目标 Demo**：[https://li-yongqvan.github.io/cyber-game/](https://li-yongqvan.github.io/cyber-game/)
- **样本数据**：[data/samples/cyber-game-m9/](/experience-pack/data/samples/cyber-game-m9/)
- **发布 ticket**：[#9](https://github.com/li-yongqvan/experience-pack/issues/9)

### 决策记录

| 编号 | 主题 | 文件 |
|---|---|---|
| 0008 | 首包 MVP 范围 | [`docs/decisions/0008-mvp-scope.md`](/experience-pack/docs/decisions/0008-mvp-scope.md) |
| 0009 | 人工审核工作流原型 | [`docs/decisions/0009-review-workflow-prototype.md`](/experience-pack/docs/decisions/0009-review-workflow-prototype.md) |
| 0010 | M9 Demo Playwright 验证 | [`docs/decisions/0010-m9-playwright-verification.md`](/experience-pack/docs/decisions/0010-m9-playwright-verification.md) |

### 索引

- [Schema 索引](/experience-pack/docs/schemas/) — 经验包 v0.2 全部 JSON Schema
- [工具脚本说明](/experience-pack/docs/tools/) — scrubber、生成器、验证器用法

### 核心叙事

```
HANDOFF.md（模糊指令）
    ↓
grill-me 追问：你到底要做什么？做到什么程度？输出到哪里？
    ↓
16 条范围/架构决策 + 4 条验收阶段 QA 决策
    ↓
commit dd93cc9：sandbox + gamification + progress persistence
    ↓
线上 Demo：https://li-yongqvan.github.io/cyber-game/
```

### 隐私说明

本包已脱敏：本地路径、Windows 用户名、文件历史快照、服务器凭据均已替换为占位符；原始中文对话保留作为协作记录。
