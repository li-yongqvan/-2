# Map Maintenance Process

**Status**: P1 Process — 已生效，需严格执行  
**Owner**: Wayfinder 维护者（当前为项目作者 + AI 协作者）  
**关联**: [#1 Wayfinder Map](https://github.com/li-yongqvan/-2/issues/1), `memory/keep-wayfinder-map-body-in-sync.md`

---

## Why

#1 Wayfinder Map 是 AI 协作者经验包项目的「当前 canonical 状态」。如果 body 与 comments/frontier/实际 ticket 状态不一致，后续 agent 和读者会看到分裂的信息：

- body 显示某 ticket 仍在 frontier，comments 却说已关闭；
- 新创建的子 ticket（如 #9、#10）未写进 body，从地图中「消失」；
- Decisions so far 与 Frontier tickets 表格过期，导致决策链断裂。

因此，**任何对 wayfinder 地图的重大变更都必须先回写 body，再做评论或关闭动作**。

---

## Body Canonical Structure

#1 body 必须保持以下结构，方便脚本解析和人工审阅：

```markdown
## Destination

## Notes

## Decisions so far

## Frontier tickets（前沿决策点）

| # | Ticket | 类型 | 状态 |

### Blocking 关系图

> 注：...已关闭。开放中：...

## Not yet specified

## Out of scope
```

---

## New Ticket Checklist

**原则：先 add to map body，再 claim。**

创建新 ticket（或认领新任务）前，按以下顺序操作：

- [ ] 确认该 ticket 确实属于 #1 Wayfinder Map 的范围。
- [ ] 打开 #1 body 编辑模式。
- [ ] 在 **Frontier tickets** 表格新增一行，填写 `#`、标题、类型、`无阻塞` 或具体阻塞项。
- [ ] 如果该 ticket 阻塞/被阻塞于其他 ticket，更新 **Blocking 关系图**。
- [ ] 如果该 ticket 是从某个已关闭 ticket 派生，在 **Decisions so far** 或 notes 中补充关联说明。
- [ ] 保存 body。
- [ ] 创建 GitHub issue 并关联 parent map #1。
- [ ] 在 #1 追加一条评论：`新增 #N 到 Frontier；body 已同步更新。`

---

## Close Ticket Checklist

**原则：先 update map body，再 close。**

关闭 ticket 前，按以下顺序操作：

- [ ] 确认该 ticket 的验收标准已满足（或明确决定不做了）。
- [ ] 对照 `docs/decisions/0013-acceptance-criteria.md` 确认：A 类 hard gates 为零，soft warnings 已记录并复核。
- [ ] 打开 #1 body 编辑模式。
- [ ] 在 **Frontier tickets** 表格中更新该 ticket 状态为 `**已完成 ✅**` 或 `已关闭`。
- [ ] 如果关闭原因是「已完成」，在 **Decisions so far** 新增一条总结，附 ticket 链接和关键结论。
- [ ] 更新 **Blocking 关系图**，移除已关闭节点或调整箭头。
- [ ] 更新表格下方的注释：`注：#3、#5、#8、...、#N 已关闭。开放中：...`
- [ ] 如果该 ticket 关闭了某个 **Not yet specified** 项，同步从该列表移除。
- [ ] 保存 body。
- [ ] 关闭 GitHub issue（附 resolution comment）。
- [ ] 在 #1 追加一条评论：`#N 已关闭；body 已同步更新。`

---

## Map Audit

### 触发条件

- **每 N 个 ticket 变更后**跑一次 audit。建议 `N = 5`。
- 每次 milestone 或 release 前必须跑一次 audit。
- 发现 body 与 comments / API 状态明显不一致时，立即跑 audit。

### Audit 脚本规格（`scripts/audit-wayfinder-map.py`）

输入：
- `#1` body（通过 GitHub API 或本地缓存读取）
- GitHub issues API 返回的 open/closed 状态
- PR / commit 关联信息

输出：
- `wayfinder-map-audit-report.md`

检查项：

| # | 检查项 | 失败时的动作 |
|---|---|---|
| 1 | Frontier 表格中列出的 open ticket 与 GitHub API 的 open issues 一致 | 标记 `body-stale-open` |
| 2 | Frontier 表格中标记为已完成的 ticket 确实在 GitHub 已关闭 | 标记 `body-stale-closed` |
| 3 | Decisions so far 中提到的 ticket 均有对应 closed issue | 标记 `missing-decision-link` |
| 4 | Not yet specified 中未出现已关闭/已解决项 | 标记 `resolved-but-not-removed` |
| 5 | Blocking 关系图中的节点与 Frontier 表格一致 | 标记 `blocking-graph-drift` |
| 6 | 所有 #1 comments 提到的「body 已同步更新」确实对应 body 编辑记录 | 标记 `unsynced-comment` |

### Audit 后的修复流程

1. 运行 audit 脚本生成报告。
2. 人工确认报告中的 discrepancies。
3. 按 **New Ticket / Close Ticket Checklist** 修复 body。
4. 重新跑 audit 直到 0 discrepancies。
5. 在 #1 追加评论：`Map audit 完成，0 discrepancies。`

---

## Priority

**P1**。

原因：
- #1 body 是所有后续 agent 读取项目状态的第一入口。
- body 漂移会直接导致错误决策、重复劳动、frontier 误判。
- 该流程成本低（每次 ticket 变更多花 1–2 分钟），收益高。

---

## Related Artifacts

- `#1` Wayfinder Map: https://github.com/li-yongqvan/-2/issues/1
- `memory/keep-wayfinder-map-body-in-sync.md` — 本流程的前身记忆
- `docs/decisions/0008-mvp-scope.md` — wayfinder MVP 范围决策
- `docs/handoffs/` — 各阶段 handoff 文档
