# Handoff · 2026-08-16 · 设计 Claude Code 会话内捕获机制

> 下一个会话建议先读本文件，然后调用 `/grill-me` 或 `/grilling` 与用户对齐捕获机制设计，再进入实现。

## Current State

我们正在解决 AI 协作者经验包项目中的「捕获机制」雾（#1 wayfinder map 中未解决的 fog 之一）。当前流水线完全依赖**事后打捞**：项目结束后用 `/grill-me` 做结构化追问，再用脚本切片生成 `DecisionPoint` + `SessionFragment`，最后经 review-workflow 审核。

目标：在 Claude Code 对话**进行中**提供一种轻量方式，让用户能标记「这是一条经验」，降低事后回忆的丢失率。

## Key Artifacts (do not duplicate — read these)

- **设计提案（ADR）**: `docs/decisions/0011-capture-mechanism.md`
  - 主机制：`#insight: <一句话总结>` 内联标签
  - 次机制：`/capture` skill，写入侧载 marker 文件
  - 新增产物：`capture-marker-v0.2.schema.json` + `capture-markers-v0.2.jsonl`
  - 核心原则：capture 只是信号，仍需走 grilling / review-workflow 才能成为正式决策点
- **Wayfinder 地图**: GitHub issue [#1](https://github.com/li-yongqvan/-2/issues/1)
  - 捕获机制 fog 在 "Not yet specified" 中
- **现有 grilling 约定**: `C:\Users\liyongquan\.claude\projects\C--Users-liyongquan\memory\grilling-auto-record-convention.md`
  - grilling 用于高歧义结构化共识；capture 用于 opportunistic 洞察标记
- **审核工作流**: `docs/decisions/0009-review-workflow-prototype.md`
  - capture markers 最终仍要进入这套审核流程
- **上一个 handoff**: `docs/handoffs/handoff-2026-08-16-capture-mechanism.md`
  - 五段式版本，包含更详细的下一步与避坑记录

## Suggested Skills for Next Agent

- **`/grill-me` 或 `/grilling`** — 与用户 stress-test 捕获机制设计，确认边界（inline vs skill、隐私、与 decision point 的关系）。
- **`/implement`** — 实现 `scripts/extract_capture_markers.py`、schema 更新、验证脚本扩展。
- **`/prototype`** — 如果需要快速验证 `/capture` skill 的交互流程。
- **`/wayfinder`** — 捕获机制被接受后，更新 #1 map 把它从 fog 移到 "Decisions so far"。

## What Has Been Done

- #12 锚点修复与 GitHub housekeeping 已完成（#1 body 更新、#12 closed）。
- 分析了 #1 wayfinder map 上剩余的 fog。
- 产出了 capture mechanism 的 ADR：`docs/decisions/0011-capture-mechanism.md`。
- 同步了 [mattpocock/skills](https://github.com/mattpocock/skills) 到 `C:\Users\liyongquan\.codex\skills\`：新增 `wait-what` 和 `writing-for-agents`，更新了 21 个 skill。

## Next Actions (in order)

1. 用户审阅 `docs/decisions/0011-capture-mechanism.md`。
2. 用 `/grill-me` 或 `/grilling` 确认 3–5 个关键设计决策（inline tag 语法、侧载文件位置、anchor 回退策略）。
3. 在 GitHub 创建 issue #11（Task: 实现会话内捕获机制）。
4. 实现 `research/session-format/schemas/capture-marker-v0.2.schema.json`。
5. 实现 `scripts/extract_capture_markers.py`：解析 `#insight` 与 `/capture` skill 侧载文件。
6. 实现 `/capture` skill 原型（建议位置：`research/session-format/prototypes/capture-skill/`）。
7. 用一个真实或测试会话跑通：标记 → 提取 → 审核 → 生成 ExperienceUnit。
8. 更新 `validate-experience-v0.2.py` 校验 markers。
9. 更新 `docs/tools/index.md` 增加 capture 工具说明。
10. 更新 #1 wayfinder map，关闭 capture mechanism fog。

## Pitfalls to Avoid

- **不要把 capture marker 当成决策**：它只是一个信号，最终仍需 grilling / review。
- **不要修改 Claude Code 本身**：只使用内联文本 + 侧载文件 + 离线脚本，符合 #1 的约束。
- **隐私红线**：marker summary 必须经过与 session 相同的 `scrubbing-manifest.json` 脱敏，不能夹带路径、密钥、源码。
- **`anchor_message_uuid` 可能拿不到**：`/capture` skill 无法直接获取 UUID 时，用 `timestamp` 最近邻匹配回退。
- **Issue 编号**：设计文档已预占 #11，创建 issue 时注意对齐。
- **Location 混淆**：Matt 的 `handoff` skill 要求写到 temp 目录；本项目的 `handoff-packager` 要求写到 `docs/handoffs/`。本项目任务优先使用项目目录版本，但内容结构参考 Matt 的简洁风格。

---

**Generated**: 2026-08-16
**Focus for next session**: confirm capture mechanism design and implement the minimum viable pipeline (schema + extractor + one end-to-end test).
