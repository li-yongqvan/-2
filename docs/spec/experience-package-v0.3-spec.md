# AI 协作者经验包 · v0.3 Buildable Spec

> **Version**: v0.3  
> **Status**: Shipped · maintenance / trigger-pending  
> **Scope**: 把 Claude Code 本地会话与 git 历史转化为可发布的、双入口可浏览的 AI 协作经验包。  
> **Canonical Map**: [#1 Wayfinder Map](https://github.com/li-yongqvan/experience-pack/issues/1)  
> **Updated**: 2026-08-17

---

## 1. 文档定位

本 spec 是 #1 Wayfinder Map 的 **buildable 版本**。它把地图中的 Destination、Decisions、Frontier、Out of scope 翻译成可执行的工程规格，供后续协作者/AI 按图施工。

**读完本 spec 后应该能回答**：
- 一个经验包由哪些文件组成？
- 从原始会话到发布站点要经过哪几步？
- 每个 ExperienceUnit 必须满足什么条件才能进入发布清单？
- 静态站有哪些页面、路由、交互？
- 哪些内容现在做，哪些 deferred，哪些不做？

---

## 2. Status & Scope

### 2.1 当前版本状态

| 项 | 值 |
|---|---|
| 版本 | v0.3 |
| 主产物 | dual-entry 静态网站 + 结构化中间数据 |
| 已发布 | `https://li-yongqvan.github.io/experience-pack/` |
| 已验证样本 | cyber-game M8-M9 |
| 开放 Frontier | #10 police 第二经验包（⏸ deferred） |
| v1.0 触发器 | 新人 onboarding / 低使用率信号 / 用户主动重启 |

### 2.2 In Scope（v0.3 已覆盖）

- 离线批处理：scrubber、decision-point 生成、ExperienceUnit 生成、验证。
- 会话内轻量捕获：`#insight` 标签 + `/capture` skill。
- 人工审核工作流：本地 FastAPI Web UI，四态状态机。
- 双入口静态站：Astro 生成，`/by-method`、`/by-project`、`/unit/{id}`、前端本地搜索。
- 验收标准：A/B 类门控 + soft warnings + 发布清单解耦。
- Wayfinder map 维护流程。

### 2.3 Deferred（明确不做，等触发器）

| 项 | 触发器 |
|---|---|
| #10 police 第二经验包 | 新人入职复用 / 低使用率 / 用户主动重启 |
| v1.0 严格门控 | 上述任一触发器 + 至少 2 个项目切片验证 |
| skill 训练语料输出 | v1.0 前后评估 |
| Obsidian vault 导出 | 无当前需求 |
| 进度跟踪 / 用户认证 | 内容量增大后评估 |

### 2.4 Out of Scope（现在不做）

- 修改 Claude Code 本身。
- 多人协作场景。
- 后端服务/数据库/动态部署。
- 真实项目案例的大规模 A/B 测试（v1.0 后）。

---

## 3. Destination

> 把一个项目从开头到结尾散落的有价值经验和错误，从人机对话与代码变更中打捞出来，经人工审核后沉淀为 **可交互工具 + 结构化学习课程**，让后人理解“我是如何与 AI 协作的”。

**核心约束**：
- 项目只是载体，**方法**才是内容核心。
- 组织结构采用 **C3 双入口**：方法主题 × 项目时间线。
- 信息采集来源锁定 **Claude Code 本地会话记录** + **git 历史/diff**。
- 终端处理先产出**结构化中间数据（JSON/YAML）**，再经人工审核生成最终产物。
- 消费方式为**探索式浏览**。

---

## 4. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         INPUT LAYER                                 │
│  Claude Code session JSONL  +  git history/diff  +  capture markers │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      SCRUB & EXTRACT LAYER                          │
│  scripts/scrubber.py              scripts/extract_capture_markers.py │
│       │                                        │                    │
│       ▼                                        ▼                    │
│  scrubbed session + markers         capture-markers-v0.2.jsonl      │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    STRUCTURE LAYER (v0.2 schema)                    │
│  decision-points-v0.2.jsonl                                         │
│  session-fragments-v0.2.jsonl                                       │
│  git-evidence-v0.2.jsonl / git-hunk-evidence-v0.2.jsonl             │
│  experience-units-v0.2.jsonl                                        │
│  tags-v0.2.json                                                     │
│  course-modules-v0.2.json                                           │
│  learning-paths-v0.2.json                                           │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       REVIEW LAYER                                  │
│  research/session-format/prototypes/review-workflow/ (FastAPI UI)   │
│  Sidecar: experience-units-reviewed-v0.2.jsonl                      │
│  States: draft → reviewed → approved | rejected                     │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      PUBLISH LAYER                                  │
│  scripts/publish_experience_package.py --version v0.x.y             │
│  Output: release/experience-package-v0.x.y/                         │
│          ├── manifest.json                                          │
│          ├── approved-units.jsonl                                   │
│          └── (symlink/copy of public assets)                        │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    CONSUMPTION LAYER                                │
│  research/session-format/prototypes/dual-entry/ (Astro static site) │
│  Routes: /by-method, /by-project, /unit/{id}, /search               │
│  Deployed to: https://li-yongqvan.github.io/experience-pack/        │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 5. Data Layer Spec

### 5.1 Schema 家族

所有中间数据位于 `research/session-format/schemas/` 和 `data/samples/<project>/`。

| Schema 文件 | 对应数据文件 | 说明 |
|---|---|---|
| `tag-v0.2.schema.json` | `tags-v0.2.json` | 标签轴与标签定义 |
| `session-fragment-v0.2.schema.json` | `session-fragments-v0.2.jsonl` | 会话片段，UUID 锚定 |
| `git-evidence-v0.2.schema.json` | `git-evidence-v0.2.jsonl` | 文件级代码证据 |
| `git-hunk-evidence-v0.2.schema.json` | `git-hunk-evidence-v0.2.jsonl` | hunk 级代码证据 |
| `decision-point-v0.2.schema.json` | `decision-points-v0.2.jsonl` | 决策点 |
| `experience-unit-v0.2.schema.json` | `experience-units-v0.2.jsonl` | 经验单元外壳 |
| `course-module-v0.2.schema.json` | `course-modules-v0.2.json` | 课程模块 |
| `learning-path-v0.2.schema.json` | `learning-paths-v0.2.json` | 学习路径 |
| `capture-marker-v0.2.schema.json` | `capture-markers-v0.2.jsonl` | 会话内捕获标记 |
| `method-ontology-v0.2.json` | — | method / collaboration_pattern 权威来源 |

### 5.2 Core Entity: ExperienceUnit

一个 `ExperienceUnit` 是经验包的最小可消费单元。

```json
{
  "unit_id": "unit-cyber-game-m9-001",
  "version": "0.2",
  "review_status": "approved",
  "entry_points": {
    "method": ["method.scope_tradeoff"],
    "timeline": ["phase.m9"],
    "theme": ["theme.architecture"],
    "skill": ["skill.grilling"]
  },
  "decision_point_id": "dp-cyber-game-m9-001",
  "session_fragment_ids": ["sf-cyber-game-m9-001"],
  "git_evidence_ids": ["ge-cyber-game-m9-001"],
  "tag_ids": ["method.scope_tradeoff", "phase.m9", "theme.architecture", "skill.grilling"],
  "candidate_marker_ids": ["cm-cyber-game-001"],
  "needs_review": []
}
```

**要求**：
- 每个 unit 必须至少包含一个 `method` 标签和一个 `project_phase`（timeline）标签，以满足双入口。
- `review_status` 四态：`draft` / `reviewed` / `approved` / `rejected`。
- `needs_review` 数组记录 warnings（如 git-alignment 文件未命中）。

### 5.3 Tag Axes（C3 双入口）

| 轴 | 用途 | 最小要求 |
|---|---|---|
| `method` | 方法主题入口 | unit 必须 |
| `project_phase` | 项目时间线入口 | unit 必须 |
| `theme` | 技术主题交叉索引 | 推荐 |
| `skill` | 协作技能索引 | 推荐 |
| `collaboration_pattern` | 交互模式索引（新增） | 可选 |

**权威来源**：`research/session-format/schemas/method-ontology-v0.2.json`。

### 5.4 Capture Marker

捕获标记是会话内的轻量信号，不直接等于决策。

```json
{
  "marker_id": "cm-cyber-game-001",
  "marker_type": "insight",
  "session_id": "be0044d7-eb49-449b-b05b-2f71b3a742d7",
  "anchor_message_uuid": "bdd8a305-3c16-4ce5-be1e-1fd08b9634b0",
  "timestamp": "2026-08-16T10:15:00.000Z",
  "summary": "决定拆分 M8-M9，先交付沙盒再补徽章系统。",
  "method_tag": "scope_tradeoff",
  "theme_tag": "architecture",
  "source": "inline",
  "notes": ""
}
```

---

## 6. Pipeline Spec

### 6.1 完整流程

```
raw session (.jsonl)
       │
       ▼
┌─────────────────────┐
│ scripts/scrubber.py │  ← 脱敏路径、用户名、密钥；输出 scrubbed session
└─────────────────────┘
       │
       ├──► capture markers 侧载文件 ──► scripts/extract_capture_markers.py
       │                                          │
       ▼                                          ▼
session-fragments-v0.2.jsonl          capture-markers-v0.2.jsonl
       │                                          │
       ▼                                          ▼
┌─────────────────────────────────────┐
│ scripts/generate_decision_points.py │  ← 规则召回 + LLM 精排
└─────────────────────────────────────┘
       │
       ▼
decision-points-v0.2.jsonl
       │
       ▼
┌──────────────────────────────────────┐
│ scripts/align-session-to-git.py      │  ← 会话 ↔ git diff 对齐
└──────────────────────────────────────┘
       │
       ├──► git-evidence-v0.2.jsonl
       └──► git-hunk-evidence-v0.2.jsonl
       │
       ▼
┌──────────────────────────────────────────┐
│ scripts/generate_experience_units_v0.2.py │
└──────────────────────────────────────────┘
       │
       ├──► experience-units-v0.2.jsonl
       ├──► course-modules-v0.2.json
       ├──► learning-paths-v0.2.json
       └──► experience-package-v0.2.json
       │
       ▼
┌──────────────────────────────────────────────────┐
│ research/session-format/prototypes/review-workflow/ │
└──────────────────────────────────────────────────┘
       │
       ▼
approved ExperienceUnit
       │
       ▼
┌──────────────────────────────────────────┐
│ scripts/publish_experience_package.py    │
└──────────────────────────────────────────┘
       │
       ▼
release/experience-package-v0.x.y/
       │
       ▼
┌──────────────────────────────────────────────────┐
│ research/session-format/prototypes/dual-entry/   │
└──────────────────────────────────────────────────┘
       │
       ▼
GitHub Pages: https://li-yongqvan.github.io/experience-pack/
```

### 6.2 脚本职责

| 脚本 | 输入 | 输出 | 关键行为 |
|---|---|---|---|
| `scripts/scrubber.py` | 原始 `.jsonl` + `scrubbing-manifest.json` | 脱敏会话 + markers | 替换路径、用户名、密钥 |
| `scripts/extract_capture_markers.py` | scrubbed session + markers | `capture-markers-v0.2.jsonl` | 解析 `#insight`，校验 schema |
| `scripts/generate_decision_points.py` | session fragments + markers | `decision-points-v0.2.jsonl` | 8 类分类 |
| `scripts/align-session-to-git.py` | session fragments + git log | git evidence files | 时间对齐 |
| `scripts/generate_experience_units_v0.2.py` | 上述全部 | v0.2 家族 | 组装 unit/module/path |
| `validate-experience-v0.2.py` | v0.2 家族 | 验证报告 | hard gates / warnings |
| `scripts/publish_experience_package.py` | approved units | release 目录 | 生成 manifest |

---

## 7. Consumption Layer Spec

### 7.1 技术栈

- **框架**：Astro 4.x
- **数据**：build 时读取 JSON/JSONL，生成静态页面
- **搜索**：前端本地搜索（第一阶段），build 时生成索引 JSON
- **样式**：自定义 CSS，响应式
- **部署**：GitHub Pages

### 7.2 路由与页面

| 路由 | 功能 | 数据来源 |
|---|---|---|
| `/` | 双入口首页，展示方法主题和项目时间线 | `tags-v0.2.json` + `course-modules-v0.2.json` |
| `/by-method` | 按 method tag 分组展示 ExperienceUnit | `experience-units-v0.2.jsonl` |
| `/by-project` | 按 project_phase / course module 分组展示 | `course-modules-v0.2.json` |
| `/unit/{id}` | 三栏详情页：对话片段 / 代码 diff / 方法说明 | unit + fragments + evidence + decision point |
| `/search` | 前端本地搜索 approved units | build 时生成的 `search-index.json` |

### 7.3 详情页布局

```
┌─────────────────────────────────────────────────────────────┐
│  Unit Title + Tags + Status Badge                           │
├─────────────────┬─────────────────────┬─────────────────────┤
│                 │                     │                     │
│  Conversation   │     Code Diff       │   Method Note       │
│  Fragments      │   (hunk-level)      │   (decision point)  │
│                 │                     │                     │
│  - collapsible  │   - +/- line highlight                     │
│  - timestamp    │   - file path       │   - why / impact    │
│  - speaker      │   - expandable      │   - related tags    │
│                 │                     │                     │
├─────────────────┴─────────────────────┴─────────────────────┤
│  Timeline (chronological navigation within module)          │
└─────────────────────────────────────────────────────────────┘
```

### 7.4 搜索功能（Phase 1）

- **范围**：仅索引 `review_status == approved` 的 ExperienceUnit。
- **粒度**：按 capture/insight 切片匹配（unit title、summary、decision question、tags）。
- **实现**：build 时生成 `search-index.json`；前端用轻量搜索库（如 fuse.js）或原生 filter。
- **结果展示**：标题 + 摘要 + 所属项目/主题 + 链接到 `/unit/{id}`。
- **约束**：不引入后端/数据库。

---

## 8. Capture Mechanism Spec

### 8.1 主路径：内联 `#insight`

用户在对话中写：

```text
#insight[method=scope_tradeoff,theme=architecture]: 决定拆分 M8-M9，先交付沙盒再补徽章系统。
```

解析规则：

```regex
#insight\s*(?:\[(?<metadata>[^\]]+)\])?\s*:\s*(?<summary>.+?)(?=\n|$)
```

- `metadata` 支持 `method`、`theme`、`commit` 键值对。
- `summary` 限制 280 字符，超长截断加 `…`。
- 一条消息可含多个 `#insight`。
- `anchor_message_uuid` 设为包含该标签的 user 消息 UUID。

### 8.2 次路径：`/capture` skill

调用 `/capture` 后，skill 通过 2–3 轮问答收集：

1. 一句话总结
2. 方法维度（可选）
3. 主题标签（可选）

输出到侧载文件：

```
~/.claude/projects/<project-dir>/<sessionId>-capture-markers.jsonl
```

### 8.3 隐私边界

- marker summary 和引用文本需经 `scrubbing-manifest.json` 脱敏。
- 不保存原始密钥、路径、源码。
- marker 只保存 summary，代码证据仍由 git diff 提供。

---

## 9. Review Workflow Spec

### 9.1 状态机

```
         ┌──────────────────────────────────────┐
         │                                      │
         ▼                                      │
draft ──► reviewed ──(approve)──► approved    │
            │                        │         │
            └────(reject)────► rejected ◄──────┘
            │
            └────(edit note)──► reviewed
```

- `draft`：未审核
- `reviewed`：已看未拍板
- `approved`：通过，可被 publish 读取
- `rejected`：拒绝

### 9.2 UI 最小操作集

| 操作 | 行为 | 持久化 |
|---|---|---|
| Approve | review_status → approved | sidecar JSONL |
| Reject | review_status → rejected | sidecar JSONL |
| Edit Note | 修改备注 | sidecar JSONL |

### 9.3 Sidecar 文件

```
data/samples/<project>/experience-units-reviewed-v0.2.jsonl
```

只保存 `unit_id`、`review_status`、`note`、`reviewed_at`、`reviewed_by`，不修改原始 unit 文件。

### 9.4 发布解耦原则

> `approved` 状态**不会自动进入**发布清单。发布清单由独立的 `publish` 步骤在某一时刻对 approved 单元做 snapshot 生成。

---

## 10. Quality Gates & Acceptance Criteria

### 10.1 A 类 Hard Gates（必须为零）

| 检查项 | 说明 | 执行方式 |
|---|---|---|
| `schema_errors == 0` | 所有中间数据符合 v0.2 schema | `validate-experience-v0.2.py` |
| `missing_session_uuids == 0` | message UUID 真实存在 | `validate-experience-v0.2.py` |
| `duplicate_ids == 0` | 无重复 ID | `validate-experience-v0.2.py` |
| `cross_reference_errors == 0` | 引用均有效 | `validate-experience-v0.2.py` |
| `privacy_hits == 0` | 无敏感字符串/密钥 | `validate-experience-v0.2.py` |
| `dual_entry_failures == 0` | 每个 unit 有 method + project_phase tag | `validate-experience-v0.2.py` |

任何 A 类错误存在时，`publish` 必须拒绝生成清单。

### 10.2 B 类 Quality Gates（v0.x 有证据即可；v1.0 更严格）

| 原则 | 验收问题 |
|---|---|
| 模块应该是深的 | 各 schema 接口职责是否单一清晰？ |
| 简单接口比简单实现更重要 | 脚本和站点 API 是否对常见用例简单？ |
| 通用代码与专用代码分开 | 流水线脚本与项目专用样本是否解耦？ |
| 不同层应有不同抽象 | session → fragment → decision → unit → module 层级是否清晰？ |
| 设计两次 | 关键接口是否考虑过第二种设计？ |

### 10.3 Soft Warnings（可接受但需记录）

| 类型 | 示例 | 处理要求 |
|---|---|---|
| git-alignment 未命中 | affected_file 不在 changed_files 中 | 写入 `.needs_review`，说明原因，关联 decision/unit |
| affected_files 差异 | hunk 时间与 git diff 不完全一致 | 在验证报告中标注 |
| unresolved capture markers | `anchor_confidence` 为 unresolved | 默认进入 `.needs_review` |

### 10.4 审核完成度

**v0.x**：
- `draft` → 不允许发布
- `reviewed` → 允许，但需记录备注
- `approved` → 核心学习路径必须全部 approved

**v1.0**：
- 所有 ExperienceUnit 必须 `approved`

---

## 11. Release Process

### 11.1 发布命令

```bash
python scripts/publish_experience_package.py --version v0.3.0
```

### 11.2 Publish 步骤职责

1. 读取 sidecar 中 approved / 部分 reviewed 的 unit。
2. 运行 A 类 hard gates 检查。
3. 生成不可变 manifest（unit 列表、版本、时间戳、checksum）。
4. 输出到 `release/experience-package-v0.x.y/`。

### 11.3 Manifest 结构

```json
{
  "version": "v0.3.0",
  "generated_at": "2026-08-17T00:00:00Z",
  "project": "cyber-game",
  "units": ["unit-cyber-game-m9-001", "..."],
  "modules": ["cm-cyber-game-m9-scope"],
  "learning_paths": ["lp-cyber-game-m9"],
  "checksum": "sha256:...",
  "quality_report": {
    "schema_errors": 0,
    "missing_uuids": 0,
    "privacy_hits": 0,
    "soft_warnings": 4
  }
}
```

### 11.4 站点部署

```bash
cd research/session-format/prototypes/dual-entry
ASTRO_BASE='/experience-pack/' npm run build
# 将 dist/ 复制到 GitHub Pages 分支或 docs/ 目录
```

---

## 12. Wayfinder Map Maintenance

见 `docs/processes/map-maintenance.md`。核心原则：

1. **New Ticket**：先 add to map body，再 claim。
2. **Close Ticket**：先 update map body，再 close。
3. **Map Audit**：每 5 个 ticket 变更或每次 release 前跑一次，目标 0 discrepancies。
4. **Body Canonical Structure**：Destination / Notes / Decisions so far / Frontier tickets / Blocking 关系图 / Not yet specified / Out of scope。

---

## 13. File Organization

```
docs/
  decisions/              # 决策记录（ADR）
  processes/              # 可重复流程
  spec/                   # 本 buildable spec
  handoffs/               # 会话交接文档
    archived/             # 过期 handoffs
research/
  session-format/         # schema、原型、研究报告
    schemas/
    prototypes/
      review-workflow/    # 审核 UI 原型
      dual-entry/         # 静态站原型
      validate-experience-v0.2.py
scripts/                  # 生产流水线脚本
data/
  samples/                # 样本经验包
    cyber-game-m9/
    capture-mechanism-demo/
release/                  # 发布产物（由 publish 脚本生成）
```

---

## 14. Verification Checklist

一个经验包达到 v0.x 可发布前，必须：

- [ ] A 类 hard gates 全部为零
- [ ] Soft warnings 已记录并关联到具体 unit/decision
- [ ] 核心学习路径上的 unit 已 approved
- [ ] dual-entry 站点本地或 staging 可访问
- [ ] 搜索功能可正常返回 approved unit
- [ ] Map audit 0 discrepancies
- [ ] #1 body 已同步更新

---

## 15. Appendix

### A. 决策索引

| # | 决策 | 文件 | 状态 |
|---|---|---|---|
| #3 | 会话文件格式 | `research/session-format-report.md` | 已完成 |
| #5 | 8 类决策方法 | 见 method ontology | 已完成 |
| #8 | MVP 范围 | `docs/decisions/0008-mvp-scope.md` | 已完成 |
| #2 | 中间数据结构 | `research/session-format-report.md` §8 | 已完成 |
| #4 | 会话与 git 对齐 | 见 decision #4 / align-session-to-git.py | 已完成 |
| #6 | 审核工作流 | `docs/decisions/0009-review-workflow-prototype.md` | 已完成 |
| #7 | 双入口原型 | `research/session-format/prototypes/dual-entry/` | 已完成 |
| #9 | cyber-game M8-M9 发布 | `docs/decisions/0010-m9-playwright-verification.md` | 已完成 |
| #12 | 锚点精确修复 | 见 0010 §5 | 已完成 |
| #13 | 捕获机制 | `docs/decisions/0011-capture-mechanism.md` | 已完成 |
| #14 | 最终形态 | `docs/decisions/0012-final-form.md` | 已完成 |
| #15 | 验收标准 | `docs/decisions/0013-acceptance-criteria.md` | 已完成 |
| #18 | 方法本体 | `docs/decisions/0014-method-ontology.md` | 已完成 |

### B. 术语表

| 术语 | 定义 |
|---|---|
| ExperienceUnit | 最小可消费经验单元 |
| DecisionPoint | 结构化描述的决策点 |
| SessionFragment | 会话切片，按 UUID 锚定 |
| GitEvidence | 与决策相关的代码变更证据 |
| Capture Marker | 会话内轻量洞察标记 |
| Review Status | draft / reviewed / approved / rejected |
| Soft Warning | 可接受但需记录的异常 |
| Hard Gate | 必须为零的阻塞性错误 |

### C. 触发器备忘

重新启动下一阶段工作的条件：

1. 有新人入职并尝试使用经验包。
2. #14 搜索功能部署 30 天后，站点访问量/搜索量明显低于预期。
3. 用户主动决定重启（police / 其他项目 / 全局重构）。
