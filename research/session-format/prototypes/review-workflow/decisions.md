# 人工审核工作流 — Grill-me 决策记录

> 关联 Issue: [#6 · 人工审核工作流设计](https://github.com/li-yongqvan/-2/issues/6)  
> 记录时间: 2026-08-14  
> 决策数量: 4  

---

## 决策 1：审核界面用什么工具实现？

**为什么需要选**：结构化中间数据（v0.2 ExperienceUnit）产出后，作者需要一种低摩擦、可交互、能审阅长文本和代码证据的方式来批量处理 `.needs_review` 中的锚点。工具选择会直接影响审核意愿和出错率。

**选项与后果**：

| 选项 | 后果 |
|---|---|
| A. Obsidian 插件 | 与现有笔记工作流结合好，但把经验包产出强耦合到 Obsidian；非 Obsidian 用户无法使用，且插件开发成本高。 |
| B. 本地 Web UI | 跨平台、零账号依赖、易于分享端口；能同时展示决策文本、会话片段、Git 证据；适合批量审阅。 |
| C. 命令行 TUI | 与生成脚本同环境，启动快；但长文本和代码证据在终端里可读性差，键盘操作对非开发者不友好。 |
| D. 直接编辑 YAML/JSON | 实现成本最低；但手工改结构化文件容易破坏 schema、丢失时间戳，且无法给出操作引导。 |

**选定**：B. 本地 Web UI（FastAPI + 最小 HTML/Jinja 模板）。

**受影响的文件/模块**：
- `research/session-format/prototypes/review-workflow/main.py` — FastAPI 应用入口
- `research/session-format/prototypes/review-workflow/review_workflow.py` — 纯状态机/数据加载模块
- `research/session-format/prototypes/review-workflow/templates/index.html` — 审核列表与操作界面

**未解决的尾巴**：未来如果要在 Obsidian 里查看已发布经验包，可以复用同一套 JSON 数据，而不是把审核界面本身做成插件。

---

## 决策 2：审核的最小操作集是什么？

**为什么需要选**：操作集决定了状态机复杂度和 UI  affordance。一次性支持合并、拆分、标签会引入 schema 变更，使原型偏离“验证工作流手感”的核心问题。

**选项与后果**：

| 选项 | 后果 |
|---|---|
| A. 通过 / 拒绝 / 合并 / 拆分 / 打标签 / 补充说明 | 功能完整，但合并/拆分会改变 unit/fragment 边界，需要在原型里做 schema 编辑，复杂度爆炸。 |
| B. 通过 / 拒绝 / 编辑备注（approve / reject / edit note） | 最小闭环：表达审核结论并留下理由；不改变数据结构，只更新 `review_status` 与 `reviewer_notes`。 |
| C. 仅通过 / 拒绝 | 更极简，但无法记录“为什么拒绝/批准”，后续无法追溯。 |

**选定**：B. 通过 / 拒绝 / 编辑备注。

**受影响的文件/模块**：
- `review_workflow.py` 中的 `ReviewAction` 与状态转移函数
- `templates/index.html` 中每行的操作按钮与备注编辑表单

**未解决的尾巴**：合并/拆分/标签可作为 #7 双入口原型的后续能力，待最小闭环验证通过后再引入。

---

## 决策 3：审核的触发时机是什么？

**为什么需要选**：审核如果堆到项目结束，作者会忘记决策上下文；如果每次会话都审，又可能因迭代太快导致重复劳动。需要找到与 v0.2 链路匹配的触发点。

**选项与后果**：

| 选项 | 后果 |
|---|---|
| A. 每次会话后批量审 | 上下文最新， heuristic 锚点可以立即确认或修正；与“里程碑切片 → 脱敏 → 决策点 → hunk 对齐 → 待审核”的 v0.2 链路天然对齐。 |
| B. 项目结束后统一审 | 一次处理所有经验包，但数月前的会话细节已模糊，审核质量下降。 |
| C. 实时审（每生成一个 ExperienceUnit 就弹窗） | 打断性强，且一个切片通常生成多个 unit，逐条弹窗体验差。 |

**选定**：A. 每次会话（里程碑切片）处理完成后批量审；**审核 UI 启动后自动打开浏览器**。当前原型暂不在发布前加最终确认闸门。

**受影响的文件/模块**：
- `scripts/generate_experience_units_v0.2.py` 生成 `.needs_review` 后的调用约定
- 原型启动参数 `--sample-dir`：直接指向某个切片目录即可批量加载
- `main.py` 启动事件中的 `webbrowser.open()` 调用

**未解决的尾巴**：发布前的最终闸门当前不实现；未来可由发布脚本通过“只读取 `approved` unit”来隐式保证。

---

## 决策 4：如何保留“未审核 / 已审草稿 / 已发布”等状态？

**为什么需要选**：v0.2 schema 已经定义了 `ExperienceUnit.review_status` 枚举（`draft / reviewed / approved / rejected`），需要确定这些状态如何流转、是否够用。

**选项与后果**：

| 选项 | 后果 |
|---|---|
| A. 直接复用 schema 四态，简化两阶段（草稿 → 已发布） | 无法表达“ reviewer 已看但还没最终拍板”的中间状态，容易把半成品误发布。 |
| B. 复用四态并增加“已发布”扩展状态 | 需要修改 schema，超出 prototype 范围。 |
| C. 四态按“draft → reviewed → approved/rejected”使用 | `reviewed` 作为“已审草稿/待拍板”，`approved`/`rejected` 为终态；发布时只取 `approved`。语义清晰且不改动 schema。 |

**选定**：C. 四态工作流，且 **review_status 转移保持宽松可反悔；发布清单由独立的打包步骤生成，与 review_status 解耦**，避免误操作直接污染发布产物。

```
draft ──(打开/编辑备注)──► reviewed ──(approve)──► approved
                               └────(reject)────► rejected

approved/rejected ──(发现错误)──► reviewed
```

**受影响的文件/模块**：
- `review_workflow.py` 中的 `ReviewStateMachine`
- `templates/index.html` 中的状态徽章与允许操作
- `experience-unit-v0.2.schema.json` 已存在的 `review_status` 字段

**未解决的尾巴**：发布清单的生成逻辑需要单独设计（#7/#9），它读取 sidecar 或原始 unit 文件中的 `approved` 项，而不是依赖 UI 中的实时状态。

---

## Grilling 后追加决定

以下问题不是 #6 body 里列出的 4 个决策点，但在 grilling 过程中被明确：

### 5. 审核列表显示全部 unit 还是只显示有待审锚点的 unit？

**选定**：显示 **全部 ExperienceUnit**，但有 `.needs_review` 锚点的 unit 置顶并高亮（`⚠️ 待审锚点` 徽章）。这样一次审核流程即可处理所有单元，而不需要先审锚点单元、再换地方处理干净单元。

**影响文件**：`main.py`（排序逻辑）、`templates/index.html`（锚点徽章）、`static/style.css`（高亮样式）。

### 6. 状态变更写回原始文件还是 sidecar？

**选定**：写入 **sidecar 文件 `experience-units-reviewed-v0.2.jsonl`**，保留原始 `experience-units-v0.2.jsonl` 不变。发布脚本优先读取 sidecar，缺失时回退到原始文件。

### 7. 拒绝时是否强制填写备注？

**选定**：**不强制**，但 UI 会在备注为空时点“拒绝”时弹出确认：`拒绝建议填写理由。确定继续拒绝吗？`。

### 8. 审核界面是否展示代码 diff / hunk 证据？

**选定**：**不展示**。当前原型只显示文件路径和证据 ID；diff 阅读体验作为 #7 双入口原型中“代码证据视图”的扩展点。

---
