# Handoff · 2026-08-17 · 确定经验包验收标准雾（Acceptance Criteria）

> 下一个会话建议先读本文件，然后调用 `/grill-me` 或 `/grilling` 与用户对齐「一个经验包做到什么程度算完成、算可发布」。

## Current State

AI 协作者经验包项目已解决两片 fog：
- **捕获机制雾**（M2）：`docs/decisions/0011-capture-mechanism.md` 已 Accepted，`/capture` skill 已可用。
- **最终形态雾**：已确定 dual-entry 站点 / 静态网站为发布形态（或已收敛为组合形态，需由当前 handoff 读取最新状态确认）。

另已将地图维护流程正式化：`docs/processes/map-maintenance.md`。

现在进入下一片 fog：**验收标准**（Acceptance Criteria / Quality Gates / "done" criteria）。

#1 wayfinder map 的 **Not yet specified** 中尚未明确：
- 一个经验包发布前必须满足哪些硬条件？
- 哪些 warnings 可接受，哪些必须清零？
- 审核状态 `approved` 是自动进入发布清单，还是需要额外的人工发布闸门？
- v0.x 到 v1.0 的晋级标准是什么？

## Key Artifacts (read these, do not duplicate)

- **Wayfinder 地图**: GitHub issue [#1](https://github.com/li-yongqvan/experience-pack/issues/1)
  - 验收标准 fog 在 "Not yet specified" 中
- **捕获机制决策**: `docs/decisions/0011-capture-mechanism.md`
  - Status: Accepted / M2 Completed
- **地图维护流程**: `docs/processes/map-maintenance.md`
  - 本流程要求验收标准确定后，ticket 关闭前必须更新 body
- **审核工作流决策**: `docs/decisions/0009-review-workflow-prototype.md`
  - 状态机：`draft → reviewed → approved|rejected`
  - 关键原则：发布清单与审核状态解耦
- **双入口原型 / 最终形态产物**: `research/session-format/prototypes/dual-entry/`
- **已部署站点**: https://li-yongquan.github.io/-2/dual-entry/
- **v0.2 验证脚本**: `research/session-format/prototypes/validate-experience-v0.2.py`
  - 当前输出：schema errors、missing UUIDs、git alignment warnings、dual-entry coverage、privacy hits
- **M9 验证报告**: `docs/decisions/0010-m9-playwright-verification.md`
  - 包含 Playwright 验证、review-workflow 端到端验证的范例

## Suggested Skills for Next Agent

- **`/grill-me` 或 `/grilling`** — 与用户收敛验收标准：硬条件、warning 容忍度、发布闸门、版本晋级规则。
- **`/to-spec`** — 如果验收标准需要写成可执行的 spec/ checklist。
- **`/implement`** — 验收标准确定后，把 checklist 写进验证脚本或 CI。
- **`/wayfinder`** — 验收标准确定后更新 #1 map，把该 fog 移到 "Decisions so far"。

## What Has Been Done

- #12 锚点修复与 GitHub housekeeping 已完成。
- 捕获机制雾完成并 Accepted。
- 最终形态雾已收敛（请确认当前结论是否已写入决策文档）。
- 地图维护流程已正式化为 `docs/processes/map-maintenance.md`。
- 当前对话开始处理**验收标准**雾。

## Next Actions (in order)

1. 打开 #1 wayfinder map，确认「验收标准」是当前待决 fog。
2. 回顾现有验证脚本输出和当前 `.needs_review` 内容，了解已有 warnings 分布。
3. 用 `/grill-me` 或 `/grilling` 与用户讨论并收敛以下决策：
   - **Hard gates（必须为零）**：哪些指标必须清零才能发布？（例如：schema errors = 0、missing UUIDs = 0、privacy hits = 0）
   - **Soft warnings（可接受但需记录）**：哪些 warnings 可以保留？（例如：git-alignment 文件未命中、affected_files 与实际 diff 的差异）
   - **审核完成度**：所有 ExperienceUnit 必须 `approved` 吗？还是允许部分 `reviewed`？
   - **发布闸门**：`approved` 状态是否自动进入发布清单？还是需要一个独立的「publish」步骤？
   - **版本晋级**：v0.2 → v0.3 的标准是什么？v1.0 的标准是什么？（例如：v1.0 要求所有锚点精确、所有 unit approved、通过端到端验证）
   - **自动化 vs 人工**：哪些验收项由脚本强制执行？哪些由人工 sign-off？
4. 创建决策文档 `docs/decisions/0013-acceptance-criteria.md`，记录结论、取舍理由、验收 checklist。
5. 本雾气解决作为 **#15** 跟踪（#11 capture、#12 closed、#13 final form、#14 预留/占用）。
6. 更新 `validate-experience-v0.2.py` 或其他脚本，使验收标准可执行（例如：新增 `--strict` 模式，把某些 warnings 提升为 errors）。
7. 更新 `docs/processes/map-maintenance.md` 中的 Close Ticket Checklist，把「确认验收标准已满足」加入关闭前置条件。
8. 更新 #1 wayfinder map：
   - 把验收标准从 "Not yet specified" 移除
   - 加到 "Decisions so far"
   - 调整 Frontier tickets 与 blocking 关系图

## Pitfalls to Avoid

- **不要把验收标准定得过高而阻塞发布**：v0.x 可以容忍部分 warnings，v1.0 才要求全部清零。
- **不要只依赖脚本**：有些验收项（如叙事完整性、学习者体验）需要人工判断。
- **不要与审核状态混淆**：`approved` 是作者审核状态，不是发布闸门；发布清单应由独立步骤生成。
- **不要忽略 `.needs_review` 的分类**：现有 4 条 git-alignment 警告是合理的「软警告」，验收标准应明确它们的地位。
- **注意 issue 编号**：#11 capture、#12 closed、#13 final form、#14 预留/占用，验收标准雾用 **#15**。
- **同步更新地图维护流程**：验收标准确定后，`docs/processes/map-maintenance.md` 的 checklist 要跟着更新。

---

**Generated**: 2026-08-17
**Focus for next session**: converge on acceptance criteria / quality gates for the experience package and make them executable.
