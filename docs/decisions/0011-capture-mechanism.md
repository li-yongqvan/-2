# Decision 0011: 会话内轻量捕获机制（Capture Mechanism）

## Status

**Accepted / M2 Completed** — schema、提取脚本、skill、安装脚本已就绪，并在 `data/samples/capture-mechanism-demo/` 跑通端到端闭环（marker → extract → review → ExperienceUnit）。

- 父地图：[#1 AI 协作者经验包 · Wayfinder](https://github.com/li-yongqvan/-2/issues/1)
- 解决 fog：**对话过程中快速标记「这是一条经验」的机制**
- 前置决策：[#8 MVP 范围](0008-mvp-scope.md)、[#9 审核工作流](0009-review-workflow-prototype.md)、[#12 锚点精确修复](0010-m9-playwright-verification.md#5-v03-锚点-uuid-精确修复12)
- 约定参考：`grilling-auto-record-convention.md`

---

## Context

当前经验包流水线是**事后打捞**模式：

1. 项目推进中发生关键对话。
2. 项目结束后（或里程碑节点）调用 `/grill-me` 做结构化追问，把模糊共识变成决策记录。
3. 用 `scripts/scrubber.py` 脱敏会话，用 `scripts/generate_decision_points.py` 把 grilling 决策转成 `decision-points-v0.2.jsonl`。
4. 用 `scripts/generate_experience_units_v0.2.py` 生成 ExperienceUnit，再经 review-workflow 人工审核。

这套模式在 cyber-game M8-M9 上跑通了 20 个经验单元，但有一个明显缺口：

> 对话进行时，用户意识到「这是一条经验」，却无法在不中断流程的情况下把它标记下来。

结果：
- 很多小规模洞察（一句有效的提示修正、一次快速的工具选择、一个反直觉的约束声明）依赖事后回忆，容易丢失。
- grilling 变成「批量补课」，负担重、覆盖不均。
- #1 wayfinder map 的 **Not yet specified** 中明确列出「对话过程中快速标记『这是一条经验』的机制」待解决。

本决策要设计一套**轻量、不修改 Claude Code 本身、与现有 v0.2 schema 兼容**的捕获机制。

---

## Decision

| # | 决策点 | 结论 |
|---|---|---|
| 1 | 捕获时机 | **会话内进行**，不等到项目结束或 grilling 阶段。 |
| 2 | 主要机制 | **内联标签 `#insight`**。用户在任何 user 消息里写 `#insight: <一句话总结>` 即可标记。 |
| 3 | 次要机制 | **`/capture` skill**。当用户需要结构化元数据（方法维度、主题标签）或想标记某条 assistant 消息时调用。 |
| 4 | 存储位置 | **不改 Claude Code 核心**。`#insight` 留在会话 JSONL 原文中；`/capture` skill 写入侧载文件 `~/.claude/projects/<project-dir>/<sessionId>-capture-markers.jsonl`。 |
| 5 | 数据产物 | 新增 `capture-marker-v0.2.schema.json` 与 `capture-markers-v0.2.jsonl`，作为经验包中间数据的一部分。 |
| 6 | 与决策点的关系 | **捕获标记是信号，不是决策**。标记仍需经过 grilling / 审核才能晋升为 `DecisionPoint` + `SessionFragment`。 |
| 7 | 与 grilling 的分工 | grilling 用于**高歧义、需要结构化共识**的决策；capture 用于**低摩擦、 opportunistic 的洞察标记**。两者互补，不替代。 |
| 8 | 锚定方式 | marker 通过 `anchor_message_uuid` 与会话消息关联；若 skill 无法直接拿到 UUID，可用 `timestamp` 由离线脚本做最近消息匹配。 |
| 9 | 隐私边界 | marker 中的 summary 和引用文本需经过与 session 相同的 `scrubbing-manifest.json` 脱敏规则；不保存原始密钥、路径、源码。 |

---

## Mechanism Details

### 主路径：内联 `#insight` 标签

用户在日常对话中可直接写：

```text
#insight: 这里把 M8-M9 合并推进改为拆分推进，是范围取舍的关键转折。
```

或带可选元数据：

```text
#insight[method=scope_tradeoff,theme=architecture]: 决定拆分 M8-M9，先交付沙盒再补徽章系统。
```

**解析规则（`scripts/extract_capture_markers.py`）：**

```regex
#insight\s*(?:\[(?<metadata>[^\]]+)\])?\s*:\s*(?<summary>.+?)(?=\n|$)
```

- `metadata` 为可选键值对，支持 `method`、`theme`、`commit`。
- `summary` 为一句话描述，长度限制 280 字符（超过则截断并加 `…`）。
- 一条 user 消息可包含多个 `#insight` 标签。
- 解析时把 marker 的 `anchor_message_uuid` 设为包含该标签的 user 消息 UUID。

### 次路径：`/capture` skill

当用户不想把元数据塞进自然语言，或想标记 assistant 的某条回复时：

```text
/capture
```

Skill 执行：
1. 提问：「一句话总结这条经验？」
2. 提问：「方法维度？（可选：task_definition / scope_tradeoff / ...）」
3. 提问：「主题标签？（可选：engine / ui / state_management / ...）」
4. 把结果追加到侧载文件：

```jsonl
{
  "marker_id": "cm-cyber-game-be0044d7-001",
  "marker_type": "capture",
  "session_id": "be0044d7-eb49-449b-b05b-2f71b3a742d7",
  "anchor_message_uuid": "",
  "timestamp": "2026-08-16T10:15:00.000Z",
  "summary": "决定拆分 M8-M9，先交付沙盒再补徽章系统。",
  "method_tag": "scope_tradeoff",
  "theme_tag": "architecture",
  "source": "skill",
  "notes": ""
}
```

若 skill 无法直接获得 `anchor_message_uuid`，可留空；离线脚本按 `timestamp` 最近邻匹配到 `assistant` 或 `user` 消息。

### 数据结构：`capture-marker-v0.2.schema.json`

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://github.com/li-yongqvan/-2/research/session-format/schemas/capture-marker-v0.2.schema.json",
  "title": "AI Collaboration Experience Package - Capture Marker v0.2",
  "description": "A lightweight, in-session signal that a conversation moment may be experience-worthy. Prototype / v0.2.",
  "type": "object",
  "required": [
    "marker_id",
    "marker_type",
    "session_id",
    "timestamp",
    "summary",
    "source"
  ],
  "properties": {
    "marker_id": {
      "type": "string",
      "pattern": "^cm-[a-z0-9]+(?:-[a-z0-9]+)*-[0-9]+$",
      "description": "Globally unique marker identifier"
    },
    "marker_type": {
      "type": "string",
      "enum": ["insight", "capture", "question", "correction"],
      "description": "Inline tag vs structured skill capture"
    },
    "session_id": {
      "type": "string",
      "format": "uuid",
      "description": "Claude Code session UUID"
    },
    "anchor_message_uuid": {
      "type": "string",
      "format": "uuid",
      "description": "Most representative message UUID for this marker"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "When the marker was created"
    },
    "summary": {
      "type": "string",
      "minLength": 1,
      "maxLength": 280,
      "description": "One-line human-readable summary"
    },
    "method_tag": {
      "type": "string",
      "enum": [
        "task_definition",
        "method_selection",
        "scope_tradeoff",
        "context_injection",
        "prompt_refinement",
        "constraint_declaration",
        "course_correction",
        "acceptance_termination"
      ],
      "description": "Optional method dimension from 8-category taxonomy"
    },
    "theme_tag": {
      "type": "string",
      "description": "Optional technical theme"
    },
    "source": {
      "type": "string",
      "enum": ["inline", "skill", "manual"],
      "description": "How the marker was created"
    },
    "notes": {
      "type": "string",
      "description": "Reviewer notes or caveats"
    }
  },
  "additionalProperties": false
}
```

---

## Pipeline Integration

```
会话进行中
  ├── user 写 #insight ──────────────────┐
  └── user 调用 /capture skill ──────────┤
                                          ▼
                    ~/.claude/projects/<project>/<sessionId>-capture-markers.jsonl
                                          │
                                          ▼
事后批处理（保留现有脚本不变，新增脚本）
  ├── scripts/scrubber.py                  │
  │   └── 脱敏会话 + markers              │
  │                                        ▼
  └── scripts/extract_capture_markers.py
        └── data/samples/<project>/capture-markers-v0.2.jsonl
                    │
                    ▼
  ┌─────────────────┴─────────────────┐
  ▼                                   ▼
grilling / 人工审核              generate_experience_units_v0.2.py
  │                                   │
  ▼                                   ▼
decision-points-v0.2.jsonl      ExperienceUnit（含 candidate_markers）
  │                                   │
  └───────────┬───────────────────────┘
              ▼
      review-workflow → approved
              │
              ▼
      dual-entry / course-module
```

**对现有脚本的影响：**

| 脚本 | 改动 |
|---|---|
| `scripts/scrubber.py` | 读取侧载 markers，对 summary 做同样脱敏；输出 `*-capture-markers-scrubbed.jsonl`。 |
| `scripts/extract_capture_markers.py` | **新增**。从 scrubbed session + markers 提取并校验 `#insight` 与 skill markers。 |
| `scripts/generate_decision_points.py` | 可选：把 marker 作为 candidate，在 grilling 时提示用户「这里有 N 个未处理标记」。 |
| `scripts/generate_experience_units_v0.2.py` | 可选：把 marker 写入 ExperienceUnit 的 `candidate_markers` 字段（schema 扩展待定）。 |
| `validate-experience-v0.2.py` | 校验 marker ID 唯一性、anchor_message_uuid 存在性。 |

---

## Privacy & Scrubbing

捕获机制增加了新的敏感信息入口，必须继承现有边界：

| 风险 | 缓解 |
|---|---|
| summary 里写进路径/密钥 | 用同一套 `scrubbing-manifest.json` 扫描并替换；skill 的 summary 输入框给出提示。 |
| marker 侧载文件泄露 | 侧载文件留在 `~/.claude/projects/` 下，不进入 git；脱敏后才复制到 `data/samples/`。 |
| 标记assistant回复涉及源码 | marker 只保存 summary，不保存完整代码块；代码证据仍由 git diff 提供。 |
| 用户误标记私人对话 | review-workflow 中可 reject；`source=inline` 的 marker 默认进入 `.needs_review`。 |

---

## How This Connects to Existing Conventions

### 与 `grilling-auto-record-convention` 的关系

- **grilling**：在**歧义高、需要结构化共识**时，通过 `AskUserQuestion` 追问用户，最终形成 `grilling-decisions/*.md`。
- **capture**：在**对话流中 opportunistic 地标记洞察**，不中断当前任务，后续可升级为 grilling 主题或直接进入审核。

类比：grilling 是「结案报告」，capture 是「现场便签」。

### 与 #1 Wayfinder Map 的关系

- 直接消除 #1 中「对话过程中快速标记『这是一条经验』的机制」这一片 fog。
- 让 #10（police 第二经验包）有**前置数据收集**手段，而不是等项目结束后再从头 grilling。

---

## Verification Criteria

1. **Inline tag 提取**
   - 在测试会话中写 `#insight: 测试标记`，运行 `extract_capture_markers.py` 后，`capture-markers-v0.2.jsonl` 包含 1 条记录。
   - `anchor_message_uuid` 对应到包含该标签的 user 消息。

2. **Skill 侧载写入**
   - 调用 `/capture` skill 后，`~/.claude/projects/<project>/<sessionId>-capture-markers.jsonl` 追加 1 行有效 JSON。
   - 脱敏后 `summary` 中不含原始路径或密钥。

3. **Schema 校验**
   - `validate-experience-v0.2.py` 扩展后，marker 文件 0 schema errors，0 missing anchor UUIDs。

4. **与现有流程不冲突**
   - 不调用 capture 机制的会话仍能正常生成经验包。
   - 已存在的 cyber-game M8-M9 样本数据不受影响。

5. **最小闭环可用**
   - 至少在一个真实或测试会话上完成：标记 → 提取 → 审核 → 生成 ExperienceUnit。

---

## Deliverables

1. `docs/decisions/0011-capture-mechanism.md` — 本 handoff 文档。
2. `research/session-format/schemas/capture-marker-v0.2.schema.json` — marker schema。
3. `scripts/extract_capture_markers.py` — 解析 `#insight` 与 skill markers。
4. `.claude/skills/capture/` 或 `research/session-format/prototypes/capture-skill/` — `/capture` skill 定义与提示词。
5. `data/samples/cyber-game-m9/capture-markers-v0.2.jsonl` —  retroactive 为空或补 1–2 条示范 marker。
6. 更新 `scripts/scrubber.py` 以处理侧载 markers。
7. 更新 `docs/tools/index.md` 增加 capture 工具说明。
8. 更新 `validate-experience-v0.2.py` 校验 markers。
9. （可选）更新 `generate_experience_units_v0.2.py` 读取 `candidate_markers`。

---

## Next Actions

1. 评审本决策：确认 `#insight` 语法、`/capture` skill 范围、marker schema。
2. 创建 `capture-marker-v0.2.schema.json`。
3. 实现 `scripts/extract_capture_markers.py` 并用一个本地测试会话验证。
4. 设计 `/capture` skill 的最小提示词（2–3 轮问答）。
5. 跑通一次端到端：测试会话 → `#insight` → 提取 → 审核 → ExperienceUnit。
6. 更新 #1 wayfinder map，把「捕获机制 fog」移到 Decisions so far。

---

## Open Questions

| 问题 | 建议处理 |
|---|---|
| `/capture` skill 如何准确获取当前 `session_id` 和最近消息 UUID？ | 先用 `timestamp` 最近邻匹配；若 Claude Code skill API 暴露 session 上下文再优化。 |
| 是否允许 `#insight` 出现在 assistant 消息中？ | 初期只允许 user 消息，避免解析模型生成的内容。 |
| marker 是否要支持 `correction` 类型（「刚才那条经验是错的」）？ | 可扩展 `marker_type` enum，初期不实现。 |
| 是否把 capture-markers 纳入 `experience-package-v0.2.json` 清单？ | 是，作为可选中间数据文件。 |

---

## Related Issues

- Parent map: [#1](https://github.com/li-yongqvan/-2/issues/1)
- This decision: **#13**（实现记录与验证）
- Blocked by: [#2](https://github.com/li-yongqvan/-2/issues/2)、[#6](https://github.com/li-yongqvan/-2/issues/6)
- Unblocks: [#10](https://github.com/li-yongqvan/-2/issues/10) 第二经验包 police 的前置数据收集
