# 0010 · cyber-game M8-M9 Demo 与工具链验证

**状态**：已完成 ✅  
**日期**：2026-08-16  
**关联**：#9（发布 cyber-game M8-M9 经验包 v0.2）  
**验证人**：Claude Code 自动 + 人工复核  

## 目标

补齐 `data/samples/cyber-game-m9/verification-report.md` 中标记的待补项：

1. 用 Playwright 访问 `https://li-yongqvan.github.io/cyber-game/sandbox` 确认沙盒页面渲染。
2. 用 Playwright 访问首页确认关卡锁定/解锁状态与徽章显示。
3. 在审核 UI 原型中加载 `session-be0044d7-scrubbed.jsonl` 和 `decision-points.jsonl` 做端到端测试。
4. 人工复核 `data/samples/cyber-game-m9/.needs_review` 中的 16 个启发式会话片段锚点。

## 1. cyber-game Demo Playwright 验证

### 环境

- Playwright：1.62.1
- 浏览器：Chromium for Testing 151.0.7922.34
- 脚本：`scripts/verify-cyber-game-m9-demo.js`
- 报告：`playwright-report.json`

### 结果

| 检查项 | URL | 结果 | 关键信号 |
|---|---|---|---|
| 首页关卡与锁定/解锁 | `/` | ✅ 通过 | 标题 "Cyber Game"、沙盒模式按钮、ARP 欺骗关卡、🔒 锁定图标 |
| 沙盒页面渲染 | `/sandbox`（客户端导航） | ✅ 通过 | "沙盒实验室"、预设场景、添加设备（主机/交换机/防火墙/攻击者/路由器）、链路工具、专家模式 |

### 说明

- cyber-game 是 React SPA，直接访问 `/sandbox` 会返回 GitHub Pages 404；验证脚本改为从首页点击"沙盒模式"按钮进行客户端导航。
- 首页截图显示 M1-M9 关卡卡片，其中 ARP 欺骗与沙盒模式可点击，其余关卡显示 🔒 锁定图标，符合 Milestone 8-9 进度解锁设计。
  - ![首页截图](0010-screenshots/homepage.png)
- 沙盒页面截图显示完整沙盒 UI，证明 M9 沙盒功能已部署并可交互。
  - ![沙盒截图](0010-screenshots/sandbox.png)
- 机器可读报告：`0010-screenshots/playwright-report.json`

## 2. review-workflow 端到端验证

### 环境

- Python：3.14
- FastAPI + uvicorn + jinja2 + python-multipart
- 样本目录：`data/samples/cyber-game-m9/`

### 操作

```bash
cd research/session-format/prototypes/review-workflow
python main.py
curl http://127.0.0.1:8765/api/state
curl http://127.0.0.1:8765/api/units
```

### 结果

| 检查项 | 结果 |
|---|---|
| 服务启动 | ✅ 成功 |
| 加载 ExperienceUnit 数量 | ✅ 20/20 |
| 加载 review anchors 数量 | ✅ 20/20 |
| `/api/state` 状态机 | ✅ draft/reviewed/approved/rejected 四态及转换完整 |
| `/api/units` 返回数据 | ✅ 首条 `unit-cyber-game-m9-001` 结构完整，含 entry_points、git_evidence_ids、tag_ids 等 |

### 说明

审核 UI 原型可成功加载脱敏会话与结构化决策点，作为后续人工 review 的入口可用。

## 3. `.needs_review` 启发式锚点复核

### 复核方法

1. 读取 `data/samples/cyber-game-m9/.needs_review`。
2. 提取所有 `anchor_uuid` 并在 `session-be0044d7-scrubbed.jsonl` 的 `uuid` 字段中校验存在性。
3. 检查该锚点消息的内容与角色。

### 结果

| 检查项 | 结果 |
|---|---|
| 16 个启发式锚点 UUID 存在性 | ✅ 全部存在于会话 `uuid` 字段 |
| 唯一锚点数量 | ⚠️ 仅 1 个唯一 UUID（`5e19a6f2-a91b-4306-8a57-402dc28ce5d6`） |
| 锚点消息类型 | ⚠️ `local-command-caveat` meta 消息，无实际对话内容 |

### 结论

- 当前启发式策略将所有 16 个 grilling-decisions 来源的决策片段锚点都定位到了会话开头同一条 meta 消息上，虽然 UUID 存在，但不具备语义精确性。
- 该问题不影响 v0.2 发布：dual-entry 原型、schema 验证、决策点展示均不依赖精确的 `anchor_message_uuid`。
- 建议在后续迭代（#10 之前）为每个决策点匹配到真正的 grill-me 追问消息；本次发布保持数据不变，避免重新生成内容。

### 4 个 affected_file 警告

来自 `verification-report.md` 的原有说明，无需修改：

- `src/engine/Link.ts`
- `src/engine/Interface.ts`
- `src/types/level.ts`
- `src/engine/devices/Router.ts`

这些文件出现在决策 `affected_files` 中，但不在 `git-alignment.changed_files` 中，说明它们是决策讨论或后续依赖文件，而非本次 commit 实际修改的文件。

## 4. 待补项关闭清单

- [x] Playwright 访问 `/sandbox` 确认沙盒页面渲染
- [x] Playwright 访问首页确认关卡锁定/解锁状态与徽章显示
- [x] 在审核 UI 原型中加载会话与决策点做端到端测试
- [x] 人工复核 `.needs_review` 中的 16 个启发式会话片段锚点（存在性通过，精确定位留待后续迭代）

## 5. v0.3 锚点 UUID 精确修复（#12）

**日期**：2026-08-16  
**关联**：#12（精确复核 cyber-game M9 的 16 个启发式会话片段锚点）

### 发现

v0.2 中 16 个 grilling-decisions 来源的片段（cyber-game-m9-001 ~ 016）全部锚定到同一条 `local-command-caveat` meta 消息（`5e19a6f2-a91b-4306-8a57-402dc28ce5d6`），无实际对话语义。复核后发现这些 grill-me 追问发生在另一个原始会话：

- **原始会话 ID**：`4241638d-64f0-431f-ad35-50e40b6313e0`
- **原始文件**：`C:\Users\liyongquan\.claude\projects\C--Users-liyongquan\4241638d-64f0-431f-ad35-50e40b6313e0.jsonl`
- **线索**：`grilling-m9-qa-record.md` 中的 `originSessionId: 4241638d-...`

同时发现 017–020 的 `anchor_message_uuid` 也锚到了 `file-history-delta` 而非真正的追问消息，一并修复。

### 修复内容

1. 从原始会话提取 16 组 grill-me 追问 + 用户回答消息，按现有 `scrubbing-manifest.json` 脱敏后保存为 `data/samples/cyber-game-m9/session-4241638d-grilling-scrubbed.jsonl`。
2. 更新 `session-fragments-v0.2.jsonl`（001–020）：
   - `session_id` → 真实会话 ID
   - `source_session_file` → 对应 scrubbed jsonl
   - `anchor_message_uuid` / `start_message_uuid` / `end_message_uuid` / `message_uuids` → 真实追问与回答 UUID
   - `participants` → `["assistant", "user"]`
   - `alignment_quality` → `manual`
3. 更新 `decision-points-v0.2.jsonl` 的 `related_message_uuids`。
4. 更新 `validate-experience-v0.2.py` 与 `align-session-to-git.py`，使验证脚本可加载新会话文件。
5. 重新生成 `.needs_review`：移除 16 条 heuristic 锚点条目，保留 4 条 git-alignment 文件未命中警告。

### 验证结果

```bash
python research/session-format/prototypes/validate-experience-v0.2.py
```

| 检查项 | v0.2 | v0.3 |
|---|---|---|
| Schema errors | 0 | 0 |
| Missing session UUIDs | 16 | 0 |
| Duplicate anchor | 1 | 0 |
| Privacy hits | 0 | 0 |
| Git alignment file warnings | 4 | 4 |

### 16 个锚点修复前后对照

| 决策 | 修复前（caveat meta） | 修复后（真实追问） |
|---|---|---|
| 001 | `5e19a6f2-...` | `bdd8a305-3c16-4ce5-be1e-1fd08b9634b0` |
| 002 | `5e19a6f2-...` | `bd61494c-6930-47c7-a336-897a1b134726` |
| 003 | `5e19a6f2-...` | `65b09d7e-9cf1-4345-8dfe-902c88213741` |
| 004 | `5e19a6f2-...` | `860dfdcc-0cb2-4150-9a8d-c37ffbfce5b0` |
| 005 | `5e19a6f2-...` | `49ff4ef6-ee70-44b6-b5ab-0ffc34b427f5` |
| 006 | `5e19a6f2-...` | `574fe6e3-2906-467f-8348-465ce3dc8733` |
| 007 | `5e19a6f2-...` | `0e2ffea6-4262-4563-9956-c9ec6c0384aa` |
| 008 | `5e19a6f2-...` | `97e36654-01f4-4bec-abc9-5b1b8edd0701` |
| 009 | `5e19a6f2-...` | `54acd7e8-1c36-4c15-86e7-0ecab962fbbf` |
| 010 | `5e19a6f2-...` | `c3ecb75d-82a3-44e2-9d71-f58ed3af88be` |
| 011 | `5e19a6f2-...` | `8d32d5c2-bda7-47e9-8ad4-1ab1f1a36142` |
| 012 | `5e19a6f2-...` | `14f909f5-92b1-4655-921d-15fcbd5ccbc8` |
| 013 | `5e19a6f2-...` | `188aeee4-e999-4b41-bd2a-4b52abcd2600` |
| 014 | `5e19a6f2-...` | `420712c1-2988-431b-af85-313d4c3e9738` |
| 015 | `5e19a6f2-...` | `14e62a36-c752-4d17-9677-7fbbe49d7c6a` |
| 016 | `5e19a6f2-...` | `2dea8335-a9fb-4bf2-8037-ea70f0bb082c` |

### 017–020 一并修复

| 决策 | 修复前（file-history-delta） | 修复后（真实追问） |
|---|---|---|
| 017 | `8407641e-...` | `35267e67-0a52-43d0-a577-97ca81136c96` |
| 018 | `8407641e-...` | `2e37687c-d7b3-41c8-945e-c81823b271aa` |
| 019 | `8407641e-...` | `673088f0-7d65-4867-98a5-a2bcddf85c0b` |
| 020 | `8407641e-...` | `921b0eda-e21f-4b19-8e64-b5c56f880ea4` |

### 结论

- 16 个启发式会话片段锚点已全部精确化，`.needs_review` 中不再有需要复核的锚点问题。
- 剩余 4 条 git-alignment 文件未命中警告属于决策 `affected_files` 与实际 commit 修改范围的差异，不影响 #12 关闭。
- 修复后的数据对 #10（police 项目迁移）更友好，因为 anchor 不再指向无意义的 meta 消息。

## 参考

- 线上 Demo：https://li-yongqvan.github.io/cyber-game/
- 双入口原型：/dual-entry/
- 原验证报告：`data/samples/cyber-game-m9/verification-report.md`
- 发布 ticket：#9
- 锚点修复 ticket：#12
- 父地图：#1
