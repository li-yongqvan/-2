# Handoff · 2026-08-17 · 实施 #14：双入口原型搜索功能（Final Form Phase 1）

> 下一个会话建议先读本文件，然后调用 `/implement` 开始实现 dual-entry 站点的前端本地搜索功能。

## Current State

经验包最终形态决策（`docs/decisions/0012-final-form.md`）已 Accepted，Phase 1 目标明确：在现有双入口原型上增加**前端本地搜索功能**。

本任务对应 **#14**。当前会话准备开始实施。

## Key Artifacts (read these, do not duplicate)

- **最终形态决策**: `docs/decisions/0012-final-form.md`
  - Phase 1 范围：前端本地搜索、仅搜索正式发布区、按 capture/insight 切片匹配、响应式、无后端
  - 验收标准：可输入关键词搜索、结果按切片展示、响应式、不引入后端
- **验收标准决策**: `docs/decisions/0013-acceptance-criteria.md`
  - A 类 hard gates、B 类质量门控、版本晋级规则
- **双入口原型代码**: `research/session-format/prototypes/dual-entry/`
  - Astro 静态站，当前已部署到 GitHub Pages
- **已部署站点**: https://li-yongquan.github.io/-2/dual-entry/
- **地图维护流程**: `docs/processes/map-maintenance.md`
  - #14 进度变化时需同步 #1 body
- **Wayfinder 地图**: GitHub issue [#1](https://github.com/li-yongqvan/-2/issues/1)
  - 最终形态已移到 Decisions so far；#14 应在 Frontier tickets 中

## Suggested Skills for Next Agent

- **`/implement`** — 主力 skill，实现搜索组件、索引生成、结果渲染。
- **`/prototype`** — 如果需要快速对比搜索 UI 方案（搜索框位置、结果卡片样式）。
- **`/wayfinder`** — #14 阶段性完成或关闭时更新 #1 map。
- **`/grill-me` 或 `/grilling`** — 如果出现未预期的设计分歧（例如搜索粒度、是否搜索主题标签）。

## What Has Been Done

- 捕获机制雾（#11）、最终形态雾（#12/0012）、验收标准雾（#15/0013）均已 Accepted。
- 地图维护流程已正式化为 `docs/processes/map-maintenance.md`。
- 方法本体雾的手off 已准备（#16），但尚未开始实施。
- 当前准备进入 #14 Phase 1 实施。

## Next Actions (in order)

1. 确认 **#14** issue 已存在；若不存在则创建，并按 `docs/processes/map-maintenance.md` 同步 #1 body。
2. 分析 `research/session-format/prototypes/dual-entry/` 的当前结构：
   - 页面路由：`/by-method`、`/by-project`、`/unit/{id}`
   - 数据源：ExperienceUnit JSONL / JSON
   - 构建命令：`ASTRO_BASE=/-2 npm run build`，输出复制到 `docs/dual-entry/`
3. 设计搜索索引：
   - 输入：approved ExperienceUnit 列表（正式发布区）
   - 字段：title、summary、capture/insight summaries、tags、project_phase
   - 输出：静态 JSON 索引文件，构建时生成
4. 实现搜索 UI：
   - 在首页或全局导航添加搜索框
   - 搜索结果页或下拉面板
   - 结果卡片显示：标题、摘要、所属项目/主题、链接到 `/unit/{id}`
5. 确保响应式布局（移动端可用）。
6. 本地验证搜索功能。
7. 重新构建并复制到 `docs/dual-entry/`。
8. 提交代码并部署到 GitHub Pages。
9. 线上验证：https://li-yongquan.github.io/-2/dual-entry/
10. 对照 `docs/decisions/0013-acceptance-criteria.md` 的 A 类门控做最终检查。
11. #14 完成后，按地图维护流程更新 #1 body，关闭 #14。

## Pitfalls to Avoid

- **不要搜索草稿区**：Phase 1 只搜索正式发布区内容，避免 capture 的 opportunistic 信号混入。
- **不要引入后端或数据库**：保持静态网站形态，搜索必须是前端本地索引。
- **不要破坏现有路由**：`/by-method`、`/by-project`、`/unit/{id}` 必须继续可用。
- **不要忘记重新构建 `docs/dual-entry/`**：Astro 源文件改动后必须执行构建 + 复制，GitHub Pages 才会更新。
- **不要一次性做 Phase 2+ 的事情**：Phase 1 只聚焦搜索；目录重组织、双轨审核 UI、skill 语料产出留到后续。
- **注意隐私**：搜索索引只包含已脱敏的 approved 内容。
- **Issue 编号**：#14 是最终形态实现；方法本体是 #16，不要混淆。

---

**Generated**: 2026-08-17
**Focus for next session**: implement frontend local search for the dual-entry Astro site and deploy Phase 1.
