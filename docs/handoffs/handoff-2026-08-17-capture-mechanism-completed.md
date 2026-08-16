# Handoff · 2026-08-17 · Capture Mechanism 实现完成

> 本文件汇总了 Decision 0011（会话内轻量捕获机制）从设计对齐到 M1/M2 实现的全部结果。
> 如需可视化流程，可配合 Obsidian vault 中的 `Capture Mechanism Flow.canvas` 与 `Capture Mechanism Flow.md` 查看。

---

## 1. 设计对齐结果

通过 `/grill-me` 对齐了 15 个设计边界，完整记录见：

- `C:\Users\liyongquan\.claude\projects\C--Users-liyongquan\memory\grilling-decisions\0011-capture-mechanism-decisions.md`

核心边界摘要：

| # | 决策点 | 结论 |
|---|---|---|
| 1 | 启用范围 | 按项目启用，未关联项目时 `#insight` 不触发、`/capture` 报错 |
| 2 | 项目关联 | 自动映射 Claude Code 项目 slug + `.claude/capture.json` 可覆盖 |
| 3 | `#insight` 语法 | 行首/独立成段、`[]` 键值对、多标签、280 字符 soft limit |
| 4 | `/capture` 分工 | 标记 assistant 消息 + richer metadata；`#insight` 负责 user 消息快速便签 |
| 5 | 存储生命周期 | `#insight` 事后提取；`/capture` 实时追加 per-session sidecar；append-only |
| 6 | 晋升边界 | 默认 review，高歧义 method_tag 必须 grilling，事实性 marker 可跳过 |
| 7 | 锚定精度 | `#insight` 精确 UUID；`/capture` 可空，review 必须，timestamp 最近邻 ±3s |
| 8 | 隐私脱敏 | 实时轻量 + 批处理完整脱敏；摘要式代码引用；敏感模式 needs_review |
| 9 | schema 边界 | 首期仅 `insight`/`capture`；`method_tag` 可选；`theme_tag` 自由+建议 |
| 10 | 流水线集成 | 合并输出 `capture-markers-v0.2.jsonl`；不覆盖原始侧载；双验证 |
| 11 | skill 部署 | 源码在仓库 `.claude/skills/capture/`，安装脚本复制到 `~/.claude/skills/capture/` |
| 12 | 清单边界 | markers 为内部中间产物，不进发布清单；ExperienceUnit 保留 `candidate_markers` |
| 13 | `/capture` 交互 | 3 必问 + 1 可选备注；默认锚定上一条 assistant；可取消 |
| 14 | marker ID | `cm-<short-slug>-<session-short>-<seq>`；数字开头加 `p` |
| 15 | 验收 | M1 schema+脚本+skill；M2 端到端闭环 |

---

## 2. 新增与修改的文件

### 新增文件

| 文件 | 用途 |
|---|---|
| `research/session-format/schemas/capture-marker-v0.2.schema.json` | Capture marker schema |
| `scripts/extract_capture_markers.py` | 从 scrubbed session + sidecar 提取 markers |
| `.claude/skills/capture/SKILL.md` | `/capture` skill 定义与提示词 |
| `.claude/skills/capture/capture_helper.py` | skill helper：写 sidecar、ID 生成、轻量脱敏 |
| `scripts/install-capture-skill.py` | 安装 `/capture` skill 到 `~/.claude/skills/capture/` |
| `scripts/capture_m2_demo.py` | M2 端到端演示脚本 |
| `data/samples/cyber-game-m9/capture-markers-v0.2.jsonl` | cyber-game M9 占位文件 |
| `data/samples/capture-mechanism-demo/*` | M2 演示数据集 |

### 修改文件

| 文件 | 修改内容 |
|---|---|
| `scripts/scrubber.py` | 增加 `--sidecar-input` / `--sidecar-output`，支持 marker 脱敏 |
| `research/session-format/prototypes/validate-experience-v0.2.py` | 增加 capture markers 校验段 |
| `research/session-format/schemas/experience-unit-v0.2.schema.json` | 增加可选 `candidate_markers` 字段 |
| `docs/tools/index.md` | 增加 capture 工具说明 |
| `docs/decisions/0011-capture-mechanism.md` | Status 更新为 Accepted / M2 Completed |

### Obsidian 可视化

| 文件 | 位置 |
|---|---|
| `Capture Mechanism Flow.canvas` | `C:\Users\liyongquan\Documents\Obsidian Vault\` |
| `Capture Mechanism Flow.md` | `C:\Users\liyongquan\Documents\Obsidian Vault\` |

---

## 3. M1 验证结果

- `#insight` 解析：合成会话中 2 个 inline marker 正确提取。
- `/capture` sidecar：helper 成功写入 `~/.claude/projects/C--Users-liyongquan--2/<session>-capture-markers.jsonl`。
- 合并提取：inline + sidecar 按 timestamp 排序、重新编号；sidecar 按 ±3 秒锚定到 assistant 消息，`anchor_confidence=nearest`。
- Schema 校验：3 条 marker 全部 OK。
- `validate-experience-v0.2.py`：**No errors**（仅 4 个既有 git-alignment warning）。
- `/capture` skill 已通过 `install-capture-skill.py` 安装到全局 skills 目录。

---

## 4. M2 端到端验证结果

运行：

```bash
python scripts/capture_m2_demo.py
```

产物目录：`data/samples/capture-mechanism-demo/`

生成内容：

| 产物 | 数量 | 说明 |
|---|---|---|
| `capture-markers-v0.2.jsonl` | 3 | 2 inline `#insight` + 1 `/capture` sidecar |
| `session-fragments-v0.2.jsonl` | 3 | 每个 marker 对应一个 fragment |
| `decision-points-v0.2.jsonl` | 3 | 由 marker 晋升的决策点 |
| `experience-units-v0.2.jsonl` | 3 | 包含 `candidate_markers` 的单元，状态 approved |
| `tags-v0.2.json` | 1 | 自动生成的 taxonomy |
| `experience-package-v0.2.json` | 1 | 发布清单 |

结果：**全部 schema 校验通过**，实现了 `marker → extract → review → ExperienceUnit` 闭环。

---

## 5. 如何使用

### 安装 skill

```bash
python scripts/install-capture-skill.py
```

安装后**重启 Claude Code 或新开一个会话**，`/capture` 即可全局使用。

### 方式 A：内联 `#insight`

在任意 user 消息里写：

```text
#insight[method=scope_tradeoff,theme=architecture]: 决定拆分 M8-M9，先交付沙盒再补徽章系统。
```

### 方式 B：调用 `/capture`

输入 `/capture`，按提示回答即可。skill 会把 marker 写入侧载文件：

```text
~/.claude/projects/<project-slug>/<sessionId>-capture-markers.jsonl
```

### 事后提取

```bash
python scripts/extract_capture_markers.py \
  --session <scrubbed-session>.jsonl \
  --sidecar ~/.claude/projects/<project-slug>/<sessionId>-capture-markers.jsonl \
  --output capture-markers-v0.2.jsonl
```

如果只有 `#insight`、没有 `/capture`，可省略 `--sidecar`。

### 脱敏侧载

```bash
python scripts/scrubber.py \
  --input <raw-session>.jsonl \
  --output <scrubbed-session>.jsonl \
  --manifest <scrubbing-manifest>.json \
  --sidecar-input <sessionId>-capture-markers.jsonl \
  --sidecar-output <sessionId>-capture-markers-scrubbed.jsonl
```

### 验证产物

```bash
python research/session-format/prototypes/validate-experience-v0.2.py
```

---

## 6. 未解决的尾巴

| 尾巴 | 当前状态 |
|---|---|
| `/capture` skill 精确获取消息 UUID | 先用 timestamp 最近邻回退；若 Claude Code skill API 未来暴露 session 上下文，再升级为 `exact` |
| 实时轻量脱敏规则 | helper 已实现路径 + 常见 secret 模式；更复杂的规则可后续扩展 |
| 哪些 `method_tag` 必须 grilling | M2 demo 中 auto-approved；实际 review 阶段由审核者/生成脚本决定 |

---

## 7. 相关链接

- GitHub issue（实现记录）：[#13](https://github.com/li-yongqvan/-2/issues/13)
- 设计决策：`docs/decisions/0011-capture-mechanism.md`
- grill-me 决策记录：`C:\Users\liyongquan\.claude\projects\C--Users-liyongquan\memory\grilling-decisions\0011-capture-mechanism-decisions.md`
- Schema：`research/session-format/schemas/capture-marker-v0.2.schema.json`
- 提取脚本：`scripts/extract_capture_markers.py`
- Skill 源码：`.claude/skills/capture/`
- M2 演示：`scripts/capture_m2_demo.py`
- 工具说明：`docs/tools/index.md`

---

**Generated**: 2026-08-17
**Status**: Decision 0011 Accepted / M2 Completed
