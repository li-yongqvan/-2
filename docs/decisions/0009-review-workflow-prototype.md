# Decision 0009: 人工审核工作流原型

## Status

Prototype（用于验证 #6 的四个决策点，已跑通 cyber-game M8-M9 真实数据）

## Context

- **#2** 已为 ExperienceUnit v0.2 定义 `review_status` 字段（`draft / reviewed / approved / rejected`）和 `.needs_review` 清单。
- **#4** 已实现 hunk 级 git 对齐，决策点可引用代码证据。
- **#6** 要问的是：这些中间数据需要作者人工审核后才能发布，审核工作流应该长什么样？

四个待决策点：
1. 审核界面用什么工具实现？
2. 审核的最小操作集是什么？
3. 审核的触发时机是什么？
4. 如何保留“未审核 / 已审草稿 / 已发布”等状态？

## Decision

| # | 决策点 | 结论 |
|---|---|---|
| 1 | 工具选型 | **本地 Web UI（FastAPI + 最小 HTML/Jinja）**。浏览器入口，目前自用、未来可推广。 |
| 2 | 最小操作集 | **通过 / 拒绝 / 编辑备注**。合并、拆分、标签暂不进入最小闭环，待验证后再扩展。 |
| 3 | 触发时机 | **每次里程碑切片生成 `.needs_review` 后批量审**；审核 UI 启动后自动打开浏览器。当前原型暂不加发布前最终闸门。 |
| 4 | 状态机 | 复用 v0.2 schema 四态：`draft → reviewed → approved|rejected`，其中 `reviewed` 即“已审草稿/待拍板”。**review_status 转移保持宽松可反悔；发布清单由独立打包步骤生成，与审核状态解耦。** |
| 5 | 列表范围 | 显示 **全部 ExperienceUnit**，有 `.needs_review` 锚点的 unit 置顶并高亮。 |
| 6 | 持久化 | 状态变更写入 **sidecar `experience-units-reviewed-v0.2.jsonl`**，保留原始文件不变。 |
| 7 | 拒绝备注 | 拒绝时 **软提示填写理由，不强制**。 |
| 8 | diff 展示 | 审核界面 **不展示 diff**，只展示文件路径和证据 ID。 |

## State Machine

```
         ┌──────────────────────────────────────┐
         │                                      │
         ▼                                      │
draft ──(打开/编辑备注)──► reviewed ──(approve)──► approved
                               │                   │
                               └────(reject)──────► rejected

approved / rejected ──(发现错误)──► reviewed
```

- `draft`：未审核，作者尚未看过。
- `reviewed`：已看但尚未最终拍板，可理解为“已审草稿”。
- `approved`：通过，可被发布脚本读取，但**不会自动进入任何发布清单**。
- `rejected`：拒绝，不进入发布清单。

**关键原则**：`review_status` 可反悔；发布清单由独立的打包/发布步骤在某一时刻对 `approved` 单元做 snapshot 生成，从而避免误操作直接污染已发布产物。

## Prototype Location

```
research/session-format/prototypes/review-workflow/
├── main.py                 # FastAPI 应用
├── review_workflow.py      # 纯逻辑模块（状态机、加载/保存、统计）
├── templates/index.html    # 审核列表 UI
├── static/style.css        # 基础样式
├── requirements.txt
├── decisions.md            # 四个决策点的 grill-me 记录
└── README.md               # 运行说明、API、扩展点
```

## API Surface

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/` | 审核界面 |
| GET | `/api/state` | 状态机与统计 |
| GET | `/api/units` | 全部 ExperienceUnit（可 `?status=` 过滤） |
| GET | `/api/units/{unit_id}` | 单个单元 |
| POST | `/api/units/{unit_id}/approve` | 通过 |
| POST | `/api/units/{unit_id}/reject` | 拒绝 |
| POST | `/api/units/{unit_id}/edit` | 保存备注（form: `note`） |
| POST | `/api/reload` | 重新加载原始数据 |

## Demo Result（cyber-game M8-M9）

- 加载 20 个 ExperienceUnit，其中 16 个包含 `.needs_review` 锚点。
- 操作示例：
  - `unit-cyber-game-m9-001` → `approved`
  - `unit-cyber-game-m9-003` → `rejected`
  - `unit-cyber-game-m9-005` → `reviewed`（补充备注）
- 状态变更实时写回 `data/samples/cyber-game-m9/experience-units-reviewed-v0.2.jsonl`。

## Extension Points

1. **批量操作**：利用 `/api/units?status=draft` 过滤 + 前端复选框，实现全选通过/拒绝。
2. **合并/拆分**：新增 `/split` / `/merge` 端点，但会改变 schema，建议在最小闭环验证后引入。
3. **发布清单生成**：发布脚本读取 sidecar 中 `approved` 的单元并生成不可变的 package manifest；这是当前原型未实现、但设计里明确解耦的下一步。
4. **最终发布闸门**：当前选择暂不在 UI 内实现；未来若需要，可在发布脚本里要求所有 unit 必须先为 `approved`。
5. **权限/审计**：当前允许 approved/rejected 回退到 reviewed；未来若推广给团队使用，可加只读/可写权限、确认对话框或审计日志。
6. **代码 diff 视图**：当前只展示文件路径和证据 ID；#7 双入口原型中可扩展 hunk 级 diff 阅读体验。

## How This Unblocks Downstream Issues

| Ticket | 期待从 #6 得到什么 | #6 提供的内容 |
|---|---|---|
| **#7 双入口原型** | 审核后的 ExperienceUnit 如何被浏览/学习 | `approved` 单元列表 + 状态过滤，可作为双入口的数据源 |

## Related Issues

- Parent map: [#1](https://github.com/li-yongqvan/-2/issues/1)
- This decision: [#6](https://github.com/li-yongqvan/-2/issues/6)
- Blocked by: [#2](https://github.com/li-yongqvan/-2/issues/2), [#4](https://github.com/li-yongqvan/-2/issues/4)
- Unblocks: [#7](https://github.com/li-yongqvan/-2/issues/7)
