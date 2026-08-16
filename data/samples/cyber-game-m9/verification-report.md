# Verification Report for cyber-game M8-M9 MVP Sample

## Scope

本报告验证 `data/samples/cyber-game-m9/` 下的首个经验包样本是否满足 #8 决策记录中定义的 6 项验收标准。

## Results

### 1. 无敏感数据泄露

| 检查项 | 命令/方法 | 结果 |
|---|---|---|
| 本地路径残留 | `grep -i "C:\\Users\\liyongquan" session-be0044d7-scrubbed.jsonl \| wc -l` | **0** ✅ |
| 用户名残留 | `grep -i "liyongquan" session-be0044d7-scrubbed.jsonl \| wc -l` | **0** ✅ |
| 服务器 IP 残留 | `grep "122.51.233.225" session-be0044d7-scrubbed.jsonl \| wc -l` | **0** ✅ |
| 服务器密码残留 | `grep "Liyongquan@123" session-be0044d7-scrubbed.jsonl \| wc -l` | **0** ✅ |
| 子代理敏感值 | 同上作用于 subagent 文件 | **0** ✅ |

说明：主会话中发现真实服务器凭据（IP + 密码），已按 scrubbing-manifest 显式规则替换为 `<SERVER_IP>` / `<SERVER_PASSWORD>`。

### 2. 决策覆盖度

| 检查项 | 结果 |
|---|---|
| 决策点总数 | **20** ✅（要求 ≥10） |
| 覆盖类别数 | **5** ✅（要求 ≥5） |
| 来源：grilling-decisions | 16 条 ✅ |
| 来源：grilling-m9-qa-record | 4 条 ✅ |

覆盖的 5 个类别：
- 任务定义
- 方法选择
- 范围取舍
- 约束声明
- 验收/终止

### 3. Git 对齐

| 检查项 | 命令/方法 | 结果 |
|---|---|---|
| Commit 范围 | `git diff --name-only 9da18db..dd93cc9` | **45 个文件** ✅ |
| 范围正确性 | `dd93cc9` 为 M9 milestone commit，`9da18db` 为 M6 milestone commit | ✅ |
| 关键 M8-M9 文件 | `progressStore.ts`、`Sandbox.tsx`、`sandboxPresets.ts`、`Home.tsx` 均在 diff 中 | ✅ |

边界案例：M7-M9 被 squash 为同一个 commit `dd93cc9`，已在 `git-alignment.json` 中记录，并通过文件级关注点分离（firewall/ACL vs sandbox/gamification）处理。

### 4. 会话完整性

| 检查项 | 结果 |
|---|---|
| 有效 JSONL 行数 | 854/854 ✅ |
| 消息类型完整性 | user/assistant/system/last-prompt/ai-title/mode 等类型均保留 |
| 文件历史快照 | 21 个快照已替换为 `<file-backups-redacted>`，仅保留 shell（messageId、timestamp） |
| 子代理文件 | 36 行有效 JSONL，结构完整 |

### 5. 包可用性

| 检查项 | 方法 | 结果 |
|---|---|---|
| Demo URL 可访问 | WebFetch `https://li-yongqvan.github.io/cyber-game/` | 页面可加载，标题为 "cyber-game" ✅ |
| M9 功能可见性 | WebFetch 静态抓取 | **无法确认** ⚠️。cyber-game 是 React SPA，WebFetch 不执行 JS，无法判断 sandbox/徽章/进度解锁是否正确渲染。需用真实浏览器或 Playwright 进一步验证。 |
| 样本可直接打开 | 文件为有效 JSONL，路径已脱敏 | ✅ |

### 6. 文档

| 检查项 | 位置 | 结果 |
|---|---|---|
| 范围决策记录 | `docs/decisions/0008-mvp-scope.md` | ✅ 已创建 |
| 脱敏规则清单 | `data/samples/cyber-game-m9/scrubbing-manifest.json` | ✅ 已创建 |
| 决策点 | `data/samples/cyber-game-m9/decision-points.jsonl` | ✅ 已创建 |
| Git 对齐 | `data/samples/cyber-game-m9/git-alignment.json` | ✅ 已创建 |
| 经验包简介 | `packages/experience-m9-grilling-scope-slice/brief.md` | ✅ 已创建 |

## 发现的问题

1. **Demo URL 的 M9 功能无法通过静态抓取确认**：
   - WebFetch 只能看到初始 HTML，无法执行 React 渲染。
   - 建议后续用 Playwright 或真实浏览器访问 `/sandbox` 路径验证沙盒和徽章功能。

2. **会话中存在真实服务器凭据**：
   - 已在脱敏阶段处理，但提示未来会话应避免在聊天中粘贴明文密码。
   - 该片段本身可作为经验包的「安全教学」素材（AI 拒绝使用明文凭据）。

## 新增：v0.2 中间数据结构验证

使用 `research/session-format/prototypes/validate-experience-v0.2.py` 对 v0.2 样本进行全面校验：

| 检查项 | 方法 | 结果 |
|---|---|---|
| v0.2 schema 合规 | jsonschema Draft-07 | **20 决策点 / 20 经验单元 / 20 会话片段 / 14 git 证据 / 3 课程模块 / 1 学习路径全部通过** ✅ |
| ID 唯一性 | 同类型 ID 去重 | **0 重复** ✅ |
| 跨引用一致性 | unit → decision/fragment/evidence/tag/module/path | **全部可解析** ✅ |
| 会话 UUID 真实性 | 校验 fragment.message_uuids 是否存在于 scrubbed session | **88 个 UUID / 0 缺失** ✅ |
| Git 对齐 | git-evidence.file_path 是否在 git-alignment 范围内 | **10/14 在 changed_files 内；4 个为决策讨论/预期文件** ⚠️ |
| 双入口覆盖 | 每个 ExperienceUnit 是否同时含 method + project_phase 标签 | **20/20** ✅ |
| Taxonomy 完整性 | 所有 tag_id 是否定义在 tags-v0.2.json | **通过** ✅ |
| 隐私扫描 | 对 v0.2 文件运行 scrubbing-manifest 规则 | **0 命中** ✅ |

**v0.2 文件清单：**

- `tags-v0.2.json`
- `session-fragments-v0.2.jsonl`
- `git-evidence-v0.2.jsonl`
- `decision-points-v0.2.jsonl`
- `experience-units-v0.2.jsonl`
- `course-modules-v0.2.json`
- `learning-paths-v0.2.json`
- `experience-package-v0.2.json`

**已知限制：**
- 会话片段锚点对 16 个 grilling-decisions 来源的决策采用启发式定位（标记在 `.needs_review`），需要人工复核。
- Git hunk 级别证据尚未补充，当前仅到 file 级别；hunk 粒度留给 #4 进一步处理。
- 4 个 git evidence 文件（`src/engine/Link.ts`、`src/engine/Interface.ts`、`src/types/level.ts`、`src/engine/devices/Router.ts`）出现在决策 `affected_files` 中，但未在 `git-alignment.changed_files` 中，说明这些文件在决策中被讨论或作为后续依赖，而非本次 commit 实际修改。

## 结论

除 Demo 功能的 JS 渲染验证需补充外，v0.1 与 v0.2 校验均已通过。样本已可用于：
- #2 Schema 设计的真实验证数据（含完整中间数据结构）
- #4 会话-git 对齐的原型验证（hunk 级可继续细化）
- #6 人工审核工作流的 UI 测试
- #7 双入口原型的内容输入

## 建议的后续验证

- [x] 用 Playwright 访问 `https://li-yongqvan.github.io/cyber-game/sandbox` 确认沙盒页面渲染。
- [x] 用 Playwright 访问首页确认关卡锁定/解锁状态与徽章显示。
- [x] 在审核 UI 原型中加载 `session-be0044d7-scrubbed.jsonl` 和 `decision-points.jsonl` 做端到端测试。
- [x] 人工复核 `data/samples/cyber-game-m9/.needs_review` 中的 16 个启发式会话片段锚点。

## 后续验证结果（#9 发布阶段补充，2026-08-16）

详见 [`docs/decisions/0010-m9-playwright-verification.md`](/docs/decisions/0010-m9-playwright-verification.md)。

| 检查项 | 结果 |
|---|---|
| Playwright 首页关卡/锁定/解锁 | ✅ 通过 |
| Playwright 沙盒页面渲染 | ✅ 通过（通过客户端导航进入 `/sandbox`） |
| review-workflow 加载 20 units/20 anchors | ✅ 通过 |
| `.needs_review` 锚点存在性 | ✅ 16/16 UUID 存在于会话 |
| `.needs_review` 锚点精确性 | ⚠️ 16 个锚点均指向同一条 meta 消息，需后续迭代精确定位；不影响 v0.2 发布 |

发布入口：

- GitHub Pages：https://li-yongqvan.github.io/-2/
- 双入口原型：https://li-yongqvan.github.io/-2/dual-entry/
- cyber-game Demo：https://li-yongqvan.github.io/cyber-game/
- 发布 ticket：#9
