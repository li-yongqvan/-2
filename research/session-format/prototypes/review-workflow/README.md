# 人工审核工作流原型

**问题**：终端处理产出的结构化中间数据，需要作者人工审核后才能发布。这个审核工作流长什么样？

这是一个可丢弃的本地 Web UI 原型，用来验证四个决策点：

1. **工具选型**：本地 Web UI（FastAPI + Jinja/HTML），不依赖 Obsidian/CLI。
2. **最小操作集**：通过 ✅ / 拒绝 ❌ / 编辑备注 📝。
3. **触发时机**：每次里程碑切片生成 `.needs_review` 后批量审。
4. **状态机**：复用 v0.2 schema 的 `review_status` 四态（`draft / reviewed / approved / rejected`）。

## 运行

```bash
cd research/session-format/prototypes/review-workflow
pip install -r requirements.txt
python main.py
```

启动后浏览器会自动打开 `http://127.0.0.1:8765`。

默认加载 `data/samples/cyber-game-m9/` 的真实数据，审核结果写入同目录的 sidecar 文件 `experience-units-reviewed-v0.2.jsonl`，原始 `experience-units-v0.2.jsonl` 保持不变。

可通过环境变量指定样本目录：

```bash
REVIEW_SAMPLE_DIR=/path/to/sample REVIEW_OUTPUT_FILENAME=reviewed.jsonl python main.py
```

## 状态机

```
draft ──(打开/保存备注)──► reviewed ──(approve)──► approved
                                └────(reject)────► rejected

approved / rejected ──(发现错误)──► reviewed
```

- `draft`：未审核
- `reviewed`：已看但尚未最终拍板（即“已审草稿”）
- `approved`：通过，可被发布脚本读取，但不会自动进入发布清单
- `rejected`：拒绝，不进入发布清单

**发布清单解耦**：审核状态可反悔；发布清单由独立的打包/发布步骤在某一时刻对 `approved` 单元做 snapshot 生成，避免误操作污染已发布产物。

## 代码结构

- `review_workflow.py`：纯逻辑模块（状态机、加载/保存、统计）。无 UI/终端代码，可直接迁移到生产代码。
- `main.py`：FastAPI 外壳，驱动 `review_workflow.py`。
- `templates/index.html`：最小 HTML/Jinja 审核列表。
- `static/style.css`：基础样式。
- `decisions.md`：四个决策点的 grill-me 记录。

## API

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/` | 审核界面 |
| GET | `/api/state` | 状态机与统计 |
| GET | `/api/units` | 全部 ExperienceUnit |
| GET | `/api/units/{unit_id}` | 单个单元 |
| POST | `/api/units/{unit_id}/approve` | 通过 |
| POST | `/api/units/{unit_id}/reject` | 拒绝 |
| POST | `/api/units/{unit_id}/edit` | 保存备注（form: `note`） |
| POST | `/api/reload` | 重新加载原始数据 |

## 扩展点

- **批量操作**：在 `/api/units` 上加 `?status=draft` 过滤，配合前端复选框即可实现全选通过/拒绝。
- **合并/拆分**：增加 `POST /api/units/{unit_id}/split` 等端点，但会改变 schema，建议在验证完最小闭环后再引入。
- **发布清单生成**：发布脚本读取 `experience-units-reviewed-v0.2.jsonl`，仅导出某一时刻 `review_status == "approved"` 的单元，并生成不可变的 package manifest。
- **最终发布闸门**：当前原型暂不在 UI 内实现；未来可在发布脚本里要求所有 unit 必须先为 `approved`。
- **权限/审计**：当前允许 approved/rejected 回退到 reviewed；未来若推广给团队使用，可加只读/可写权限或审计日志。
- **代码 diff 视图**：当前只展示文件路径和证据 ID；#7 双入口原型中可扩展 hunk 级 diff 阅读体验。
