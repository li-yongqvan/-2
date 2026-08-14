# Decision 0008: Wayfinder 首个 MVP 范围

## Status

Accepted（经 grilling 达成一致）

## Context

Wayfinder 的目标是把一个项目从始至终散落的人机协作经验，从 Claude Code 会话（`.jsonl`）和 git 历史里打捞出来，经人工审核后沉淀为「可交互工具 + 结构化学习课程」。

前置决策：
- **#3**：会话文件位于 `~/.claude/projects/<project-dir>/<sessionId>.jsonl`，需脱敏路径、源码与潜在密钥。
- **#5**：决策点按 8 类保留（任务定义、方法选择、范围取舍、上下文注入、提示精炼、约束声明、方向修正、验收/终止），识别流程为「规则召回 → LLM 精排 → 人工 Review」。

本决策要解决 **#8** 的问题：为了验证整条流水线，选择哪个具体项目/会话来跑通第一个经验包，并明确隐私边界、切片方式和主题。

## Decision

| # | 决策点 | 结论 |
|---|---|---|
| 1 | 首包锚点项目 | **`cyber-game` 的 Milestone 8-9** |
| 2 | 后续候选 | **`police` 作为第二个经验包**，主题聚焦「论坛 MVP 微服务过度设计的教训」 |
| 3 | 切片方式 | **里程碑切片**，只取 M8-M9 主执行会话 + 子代理 + 记忆文件，不取完整项目 28 个会话 |
| 4 | 隐私边界 | 保留中文原始对话；脱敏本地路径、用户名、git 邮箱；文件快照替换为 git ref；扫描并脱敏密钥 |
| 5 | 首包方法主题 | **「Grill-me 驱动的里程碑范围切片」** |

## Why cyber-game M8-M9

- **里程碑弧线清晰**：M6（85 测试）→ M7（106 测试）→ M8-M9（133 测试），有完整记忆快照。
- **已有公开产物**：线上 Demo `https://li-yongqvan.github.io/cyber-game/`，源代码可公开。
- **AI 协作信号丰富**：Plan/Explore agents、TDD、`grill-me` 决策记录、skill 引用。
- **结构化决策已存在**：`grilling-decisions/m8-m9-sandbox-gamification-decisions.md` 记录了 16 条决策。
- **规模可控**：主会话约 3.6 MB / 854 行，适合单人人工审核。

## Why not other candidates as first anchor

- `week-news-submit-redesign`：公开且叙事清晰，但决策点和多代理结构较少，更适合作为第二或第三包。
- `feishu-multi-bot`：涉及 `.env`/API 凭证与群聊内容，脱敏成本高，不适合首包。
- `police`：仅有 1 个 commit，微服务架构对 MVP 验证过重，方法叙事不足；但适合作为后续「从过度设计中学习」的包。
- `forum-testing-skill` / `karpathy-coding-methodology` / `ai-cli-reference`：是参考资料，不是完整项目叙事。

## Session & Code Scope

**切片策略：里程碑切片，而非单次完整会话。**

主会话：
- `C:\Users\liyongquan\.claude\projects\C--Users-liyongquan\be0044d7-eb49-449b-b05b-2f71b3a742d7.jsonl`
- 标题：`阅读HANDOFF.md文档，执行M9的规划`
- 时间：2026-07-29
- 子代理：`...\be0044d7...\subagents\agent-abe9460ea165d5867.jsonl`

支持记忆产物：
- `cyber-game-milestone-8-9.md`
- `grilling-decisions/m8-m9-sandbox-gamification-decisions.md`
- `grilling-m9-qa-record.md`
- `grilling-auto-record-convention.md`

Git commit 范围（M7-M9 被 squash 为一个里程碑提交）：
```text
9da18db..dd93cc9
```
- `9da18db`：M6 - TCP SYN Flood & SYN Cookie defense
- `dd93cc9`：M9 - gamification, sandbox, progress persistence and docs

后续 CI/deploy 提交不包含在首包内。

## Privacy & Scrubbing Boundaries

| 内容 | 处理方式 |
|---|---|
| 本地路径 / Windows 用户名 / git 邮箱 | 脱敏为 `<HOME>`、`<USER>`、`<AUTHOR_EMAIL>` |
| `cyber-game` 源码 | 不脱敏，公开仓库 |
| 中文提示与对话 | 保留，是协作记录的核心 |
| 文件历史快照 | 替换为 `<code-ref: src/... @ dd93cc9>`，用 git diff 作为代码证据 |
| 密钥/token/密码 | 强制扫描并替换为 `<REDACTED_SECRET>` |

**边界决策：**
- 不随包发送原始文件历史快照，用 git diff 范围作为代码证据。
- 不包含与 cyber-game 无关的会话（`C--Users-liyongquan` 目录混有多个项目）。
- 保留中文提示与标题，它们是协作记录的一部分。
- 保留 `grilling-decisions` 与 `grilling-m9-qa-record` 的决策结构，仅脱敏文件路径。

## First Experience Package Theme

**主题：「Grill-me 驱动的里程碑范围切片：从 HANDOFF 到 M8-M9 架构决策」**

映射到 8 类决策：
- **任务定义**：「本次执行 M9 的规划希望做什么？」
- **方法选择**：「验收深度要做到什么程度？」
- **范围取舍**：「M8-M9 合并推进还是拆分推进？」
- **上下文注入**：读 `HANDOFF.md` 与前期 milestone memory。
- **提示精炼**：后续 grilling 追问如何收窄选项。
- **约束声明**：「Router 在沙盒中占位」、「仅完成徽章」。
- **方向修正**：从「合并推进」转向「拆分推进」。
- **验收/终止**：最终「同意退出 plan mode 并开始执行验收」。

**学习者路径：** 原始 HANDOFF 提示 → 歧义浮现 → 跟随 `grill-me` 追问 → 查看架构决策与 git diff → 理解如何在里程碑边界用结构化提问避免过度构建。

## Deliverables for Closing #8

1. `docs/decisions/0008-mvp-scope.md` — 本文件。
2. `data/samples/cyber-game-m9/scrubbing-manifest.json` — 脱敏规则清单。
3. `data/samples/cyber-game-m9/session-be0044d7-scrubbed.jsonl` — 脱敏后的主会话 + 子代理。
4. `data/samples/cyber-game-m9/decision-points.jsonl` — 10-16 条标注决策。
5. `data/samples/cyber-game-m9/git-alignment.json` — 会话到 commit 范围的映射。
6. `packages/experience-m9-grilling-scope-slice/brief.md` — 第一个经验包简介。
7. `data/samples/cyber-game-m9/verification-report.md` — 验证清单结果。

## How This Unblocks Downstream Issues

| Ticket | 期待从 #8 得到什么 | #8 提供的内容 |
|---|---|---|
| **#2 Schema 设计** | 真实样本来验证字段、标签、切片粒度 | `decision-points.jsonl` 覆盖 8 类决策；区分 grill-me 决策与代码架构决策 |
| **#4 会话与 git diff 对齐** | 会话与 commit 有清晰对应关系 | 固定范围 `9da18db..dd93cc9`，会话内引用 M8-M9 文件；squash 分区作为边界案例 |
| **#6 人工审核工作流** | 数据量与敏感度决定 UI 形态 | 3.6 MB 主会话、低敏感度；16 条预结构化决策可供验证/拒绝 |
| **#7 双入口原型** | 方法主题丰富且项目时间线清晰 | `HANDOFF → grilling → commit → demo` 时间线；决策卡片可作为方法入口 |

## Verification Criteria

1. **无敏感数据泄露**
   - `grep -i "C:\\Users\\liyongquan" session-be0044d7-scrubbed.jsonl` 返回 0 条。
   - 密钥扫描无命中。

2. **决策覆盖度**
   - `decision-points.jsonl` 至少 10 条决策。
   - 覆盖至少 5 个决策类别。
   - 至少 1 条来自 `grilling-m9-qa-record.md`，1 条来自 `grilling-decisions/m8-m9-sandbox-gamification-decisions.md`。

3. **Git 对齐**
   - `git diff --name-only 9da18db..dd93cc9` 返回预期文件集合。
   - 决策点引用的源文件均落在该 diff 中。

4. **会话完整性**
   - 保留所有用户提示、agent 回复、工具调用边界。
   - 文件历史快照被移除或替换，而非仅截断。

5. **包可用性**
   - 审核者可在 UI 中直接打开脱敏会话与决策点。
   - Demo URL 可访问并展示 M9 功能（沙盒、进度徽章）。

6. **文档**
   - 本文件已提交，并交叉链接 #2/#4/#6/#7。

## Known Risks & Mitigations

| 风险 | 缓解 |
|---|---|
| `C--Users-liyongquan` 目录混合多个项目会话 | 按 `cwd` 与 `cyber-game` 内容过滤，仅包含 `be0044d7` 及其子代理 |
| M7-M9 被 squash 为一个 commit | 通过会话时间戳与文件引用划分 M8-M9，作为 squash 对齐的边界案例 |
| 中文转录可能增加 LLM 精排难度 | 保留原中文，要求 Schema 支持 bilingual 文本 |
| 主会话 3.6 MB，人工审核可能偏重 | 用 16 条预结构化决策做种子，审核者只需验证/拒绝 |

## Next Actions

1. ✅ 创建 `docs/decisions/0008-mvp-scope.md`。
2. 实现 scrubber，产出 `data/samples/cyber-game-m9/session-be0044d7-scrubbed.jsonl`。
3. 提取 `data/samples/cyber-game-m9/decision-points.jsonl` 并用 8 类分类法校验。
4. 构建 `data/samples/cyber-game-m9/git-alignment.json`。
5. 起草 `packages/experience-m9-grilling-scope-slice/brief.md`。
6. 执行验证清单，关闭 issue #8。

## Related Issues

- Parent map: [#1](https://github.com/li-yongqvan/-2/issues/1)
- This decision: [#8](https://github.com/li-yongqvan/-2/issues/8)
- Unblocked: [#2](https://github.com/li-yongqvan/-2/issues/2), [#4](https://github.com/li-yongqvan/-2/issues/4), [#6](https://github.com/li-yongqvan/-2/issues/6), [#7](https://github.com/li-yongqvan/-2/issues/7)
