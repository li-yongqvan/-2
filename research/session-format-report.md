# Claude Code 本地会话文件格式研究报告

**研究问题**：Claude Code 本地会话文件格式是什么？能从中提取哪些字段？  
**对应工单**：[li-yongqvan/-2#3](https://github.com/li-yongqvan/-2/issues/3)  
**研究分支**：`research/session-format`  
**日期**：2026-08-13

---

## 1. 文件存储位置

在 Windows 11 本机上，Claude Code 的会话相关数据分散在以下位置（用户主目录 `C:\Users\liyongquan` 下）：

| 路径 | 内容 | 格式 |
|------|------|------|
| `~/.claude/sessions/54200.json` | 当前运行会话的元数据 | 单条 JSON |
| `~/.claude/projects/<project-dir>/<sessionId>.jsonl` | 每个项目的完整会话记录 | JSONL |
| `~/.claude/projects/<project-dir>/<sessionId>/` | 该会话的附件/产物目录（如 `tool-results/`） | 目录 |
| `~/.claude/transcripts/ses_<id>.jsonl` | 简化版 transcript（旧版/备用） | JSONL |
| `~/.claude/history.jsonl` | 全局命令/提示历史 | JSONL |

实际观察到的项目目录名示例：

- `C--Users-liyongquan`（默认项目，对应 `C:\Users\liyongquan` 工作目录）
- `C--Users-liyongquan-Documents-AI----feishu-multi-bot-package-feishu-multi-bot-bots-hun-ya`
- `C--Users-liyongquan-Documents-Obsidian-Vault`

会话文件名即 `sessionId`，例如 `4d7d9ff2-6d84-471b-ae3f-88238be5c7e1.jsonl`。

---

## 2. 文件格式概览

两种主要会话文件都是 **JSON Lines（JSONL）**：每行一条独立 JSON，无换行转义。  
主要使用的**项目会话文件**比 `transcripts/` 下的简化版丰富得多。

### 2.1 当前会话元数据（`sessions/54200.json`）

```json
{
  "pid": 54200,
  "sessionId": "4d7d9ff2-6d84-471b-ae3f-88238be5c7e1",
  "cwd": "C:\\Users\\liyongquan",
  "startedAt": 1786613251344,
  "procStart": "134310868492359469",
  "version": "2.1.229",
  "peerProtocol": 1,
  "kind": "interactive",
  "entrypoint": "cli",
  "name": "liyongquan-db",
  "nameSource": "derived",
  "status": "busy",
  "updatedAt": 1786633109512,
  "statusUpdatedAt": 1786633109512
}
```

可提取字段：会话 ID、工作目录、启动时间戳、Claude Code 版本、入口（CLI）、运行状态等。

### 2.2 项目会话文件（`<sessionId>.jsonl`）

每行是一个事件/记录，字段 `type` 标识记录类型。  
以当前 `wayfinder` 会话为例，各类记录出现次数：

| type | 出现次数 | 说明 |
|------|---------|------|
| `assistant` | 76 | 模型回复 |
| `user` | 43 | 用户输入 / 工具结果回填 |
| `system` | 14 | 系统事件，如 `turn_duration` |
| `mode` | 12 | 会话模式变化 |
| `permission-mode` | 12 | 权限模式 |
| `last-prompt` | 11 | 最新提示快照 |
| `file-history-snapshot` | 11 | 文件历史快照 |
| `ai-title` | 11 | AI 生成的会话标题 |
| `attachment` | 8 | 环境附件（skill 列表、权限等） |
| `file-history-delta` | 1 | 文件历史增量 |
| `queue-operation` | 2 | 队列操作 |

### 2.3 简化 transcript（`transcripts/ses_*.jsonl`）

仅保留：

```json
{"type": "user", "timestamp": "2026-05-30T18:30:12.952Z", "content": "全局"}
{"type": "tool_use", "timestamp": "2026-05-30T18:30:19.468Z", "tool_name": "webfetch", "tool_input": {"url": "...", "format": "markdown"}}
{"type": "tool_result", "timestamp": "2026-05-30T18:30:23.543Z", "tool_name": "webfetch", "tool_input": {...}, "tool_output": {"output": "..."}}
```

只有 `user`、`tool_use`、`tool_result` 三种类型，无模型 thinking、无 attachment、无 token 用量。

---

## 3. 主要记录结构详解

### 3.1 `user` 记录

```json
{
  "parentUuid": "88486e73-5a40-4565-a02c-bc02ed0f3614",
  "isSidechain": false,
  "promptId": "92648815-d1d7-45e8-af68-e53a86aec936",
  "type": "user",
  "message": {
    "role": "user",
    "content": "<command-message>wayfinder</command-message>\n<command-name>/wayfinder</command-name>\n<command-args>开发一个项目...</command-args>"
  },
  "uuid": "88486e73-5a40-4565-a02c-bc02ed0f3614",
  "timestamp": "2026-08-13T09:29:41.500Z",
  "userType": "external",
  "entrypoint": "cli",
  "cwd": "C:\\Users\\liyongquan",
  "sessionId": "4d7d9ff2-6d84-471b-ae3f-88238be5c7e1",
  "version": "2.1.229",
  "gitBranch": "HEAD"
}
```

- `message.content` 可能是 **字符串**（用户直接输入）或 **列表**（工具结果、系统注入）。
- 当内容为列表且 `type: tool_result` 时，表示工具执行结果回传给模型。
- `isMeta: true` 表示系统元消息（如 skill 注入的 base directory 说明）。
- `toolUseResult` 字段记录工具调用是否成功。
- `sourceToolAssistantUUID` 把工具结果与之前的 assistant tool_use 关联起来。

### 3.2 `assistant` 记录

```json
{
  "parentUuid": "7178570c-cf92-417d-978c-c39afc91fa95",
  "isSidechain": false,
  "message": {
    "id": "msg_3fmYpoplmPGH5PiCbWsFhRhD",
    "type": "message",
    "role": "assistant",
    "content": [
      {
        "type": "thinking",
        "thinking": "用户调用 /wayfinder，带着一个 loose idea...",
        "signature": "z1xYSLHLQ4Yx..."
      }
    ],
    "model": "kimi-for-coding",
    "stop_reason": "tool_use",
    "stop_sequence": null,
    "usage": {
      "input_tokens": 30375,
      "cache_creation_input_tokens": 0,
      "cache_read_input_tokens": 16128,
      "output_tokens": 622,
      "output_tokens_details": {},
      "server_tool_use": {"web_search_requests": 0, "web_fetch_requests": 0},
      "service_tier": "standard",
      "cache_creation": {"ephemeral_1h_input_tokens": 0, "ephemeral_5m_input_tokens": 0},
      "inference_geo": "not_available",
      "iterations": [],
      "speed": "standard"
    },
    "stop_details": null
  },
  "attributionSkill": "wayfinder",
  "type": "assistant",
  "uuid": "1c867e5f-cd54-4f1e-b7e6-449b65ea3195",
  "timestamp": "2026-08-13T09:30:00.633Z",
  "effort": "high",
  "session_id": "4d7d9ff2-6d84-471b-ae3f-88238be5c7e1",
  "userType": "external",
  "entrypoint": "cli",
  "cwd": "C:\\Users\\liyongquan",
  "sessionId": "4d7d9ff2-6d84-471b-ae3f-88238be5c7e1",
  "version": "2.1.229",
  "gitBranch": "HEAD"
}
```

`message.content` 是**列表**，每个元素为内容块，常见 `type`：

| content block type | 说明 | 可提取字段 |
|-------------------|------|-----------|
| `thinking` | 扩展思考过程 | `thinking`, `signature` |
| `text` | 模型自然语言回复 | `text` |
| `tool_use` | 工具调用 | `id`, `name`, `input` |

模型 `stop_reason` 常见值：`tool_use`、`end_turn` 等。

### 3.3 `tool_use` 内容块示例

```json
{
  "type": "tool_use",
  "id": "tool_HW7bgkFRqgfVjJYLgjhoKuRm",
  "name": "Write",
  "input": {
    "file_path": "C:\\Users\\liyongquan\\wayfinder-map.html",
    "content": "<title>AI 协作者经验包 · Wayfinder 地图</title>\n<style>...</style>..."
  }
}
```

其他常见工具：`Bash`、`Read`、`Edit`、`Skill`、`Agent`、`TaskCreate`、`TaskUpdate`、`Artifact`、`mcp__github__create_issue` 等。

工具名即 Claude Code 工具名；MCP 工具以 `mcp__<server>__<tool>` 形式出现。

### 3.4 `tool_result` 内容块示例

```json
{
  "type": "tool_result",
  "tool_use_id": "tool_HW7bgkFRqgfVjJYLgjhoKuRm",
  "content": "File created successfully at C:\\Users\\liyongquan\\wayfinder-map.html"
}
```

`tool_use_id` 与之前 assistant `tool_use.id` 对应，构成调用-结果闭环。

### 3.5 `attachment` 记录

用于注入环境上下文，常见子类型：

| `attachment.type` | 说明 |
|------------------|------|
| `agent_listing_delta` | 可用 agent 类型列表 |
| `skill_listing` | 可用 skill 列表 |
| `command_permissions` | 当前允许的工具 |
| `task_reminder` | 任务提醒 |
| `plan_mode_exit` | 计划模式退出 |

### 3.6 `file-history-snapshot` 与 `file-history-delta`

```json
{
  "type": "file-history-snapshot",
  "messageId": "88a3afd7-bcef-4094-b819-24ce45f75932",
  "snapshot": {
    "messageId": "88a3afd7-bcef-4094-b819-24ce45f75932",
    "trackedFileBackups": {
      "wayfinder-map.html": {
        "backupFileName": "ade4571a4215fa24@v2",
        "version": 2,
        "backupTime": "2026-08-13T14:54:49.415Z",
        "realParentDir": "C:\\Users\\liyongquan"
      }
    },
    "timestamp": "2026-08-13T14:54:49.415Z"
  },
  "isSnapshotUpdate": false
}
```

可提取：每个被跟踪文件的备份文件名、版本、备份时间、父目录。  
这对应 Claude Code 的“可撤销编辑”历史，实际备份文件位于 `~/.claude/file-history/`。

### 3.7 `system` 记录

```json
{
  "parentUuid": "6f8b4dad-92a1-45a1-b1a1-da5398d6ac9a",
  "isSidechain": false,
  "type": "system",
  "subtype": "turn_duration",
  "durationMs": 44283,
  "messageCount": 13,
  "timestamp": "2026-08-13T09:30:25.798Z",
  "uuid": "0f249fa2-331a-4f31-bc70-9aa3642d5d8e",
  "isMeta": false,
  "userType": "external",
  "entrypoint": "cli",
  "cwd": "C:\\Users\\liyongquan",
  "sessionId": "4d7d9ff2-6d84-471b-ae3f-88238be5c7e1",
  "version": "2.1.229",
  "gitBranch": "HEAD"
}
```

 subtype 如 `turn_duration` 可用于统计每轮耗时。

### 3.8 `last-prompt` / `ai-title` / `mode` / `permission-mode`

```json
{"type": "last-prompt", "lastPrompt": "...", "leafUuid": "...", "sessionId": "..."}
{"type": "ai-title", "aiTitle": "展示人机协作的软件设计方法论", "sessionId": "..."}
{"type": "mode", "mode": "normal", "sessionId": "..."}
{"type": "permission-mode", "permissionMode": "default", "sessionId": "..."}
```

---

## 4. 可提取的字段清单

| 维度 | 可提取字段 | 位置 |
|------|-----------|------|
| **会话身份** | `sessionId`, `pid`, `name`, `version`, `entrypoint`, `kind` | 元数据 / 每行记录 |
| **时间** | `timestamp`, `startedAt`, `updatedAt`, `durationMs` | 各记录 / system subtype `turn_duration` |
| **项目上下文** | `cwd`, `gitBranch`, `project`（从目录名推断） | 每行记录 |
| **用户消息** | `message.content`（字符串或列表） | `type: user` |
| **助手消息** | `message.content[].text` | `type: assistant` |
| **思考过程** | `message.content[].thinking` | `type: assistant` |
| **工具调用** | `message.content[].{id, name, input}` | `type: assistant` |
| **工具结果** | `message.content[].{tool_use_id, content}` 或 `toolUseResult` | `type: user` |
| **文件读写** | `input.file_path`, `input.content`（Write/Edit/Read） | `tool_use` 块 |
| **Bash 命令** | `input.command`, `input.description` | `tool_use` 块 |
| **Skill 调用** | `input.skill`, `input.args`, `attributionSkill` | `tool_use` 块 / assistant 记录 |
| **Agent 调用** | `input.subagent_type`, `input.description` | `tool_use` 块 |
| **MCP 调用** | `mcp__<server>__<tool>` 名称及输入 | `tool_use` 块 |
| **Token 用量** | `input_tokens`, `output_tokens`, `cache_read_input_tokens`, `cache_creation_input_tokens`, `thinking_tokens` | `assistant.message.usage` |
| **模型信息** | `model`, `stop_reason`, `effort`, `speed`, `service_tier` | `assistant.message` |
| **文件历史** | `trackedFileBackups`（文件名、版本、备份时间） | `file-history-snapshot` |
| **环境附件** | skill/agent 列表、权限列表 | `type: attachment` |
| **会话标题** | `aiTitle` | `type: ai-title` |
| **最新提示** | `lastPrompt`, `leafUuid` | `type: last-prompt` |

---

## 5. 隐私与敏感信息考量

### 5.1 明确包含的敏感/个人信息

- **完整对话内容**：所有用户输入、模型回复、思考过程。
- **本地绝对路径**：`cwd`、`file_path`、`realParentDir` 等暴露用户目录结构（如 `C:\Users\liyongquan\...`）。
- **GitHub 仓库与 issue 标题**：`gh issue create` 等命令参数。
- **代码与文件内容**：`Write`/`Edit`/`Read` 的 `content` 字段可能包含项目源码。
- **网络资源**：`WebFetch` 抓取的外部页面内容。
- **Token 用量**：虽不敏感，但可用于成本分析。

### 5.2 是否包含 API 密钥/Token？

对当前会话前 200 行进行关键词扫描（`api_key`、`token`、`secret`、`password`、`authorization`、`private_key`）后：

- **未发现独立的 API 密钥字段**。
- 仅有 `input_tokens` / `output_tokens` / `cache_*_tokens` 等**用量 token**，不是访问凭证。
- 但 `Bash` 命令参数或工具输出中**理论上可能**出现凭据（如 `gh auth status` 输出、环境变量打印），需要逐会话人工审查。

### 5.3 处理建议

- 任何“经验包”处理流程都应**默认脱敏**：
  - 替换或截断用户名/主目录（`C:\Users\liyongquan` → `<HOME>`）。
  - 截断或哈希化绝对路径。
  - 对 Write/Edit 的 `content` 做敏感信息扫描（正则匹配密钥、token、密码模式）。
  - 提供开关决定是否保留 thinking 块（可能暴露内部推理）。
- 会话文件属于**本地隐私数据**，不应直接上传到公开仓库或外部服务。

---

## 6. 现有文档与稳定 Schema

### 6.1 官方文档

- **Anthropic 目前未提供公开的 Claude Code 会话文件 schema 文档**。
- 文件格式属于客户端内部实现，字段可能随版本变化。

### 6.2 社区/插件实现

在 `~/.claude/plugins/marketplaces/` 与 `~/.claude/skills/` 中发现若干第三方解析实现，可作为参考：

| 路径 | 说明 |
|------|------|
| `~/.claude/plugins/marketplaces/claude-night-market/plugins/scribe/src/scribe/session_parser.py` | 第三方 Claude Code / Codex 会话解析器，支持 `user`/`assistant`/`tool_use`/`tool_result`/`thinking` 提取 |
| `~/.claude/plugins/marketplaces/claude-night-market/plugins/scribe/commands/session-replay.md` | 基于 JSONL 生成会话回放 GIF/MP4 |
| `~/.claude/plugins/marketplaces/Claudest/docs/session-context-injection-spec.md` | 会话上下文摘要注入设计，包含决策点/开放线索提取启发式规则 |
| `~/.claude/skills/claude-mem/docs/SESSION_ID_ARCHITECTURE.md` | 区分 `contentSessionId` 与 `memorySessionId` 的架构说明 |

这些资料说明社区已把 Claude Code JSONL 视为事实标准，但 **schema 不是官方保证的 stable API**。

---

## 7. 对“经验包”系统的启示

基于以上结构，可从会话文件中自动提取并用于下游经验包生成的信号：

1. **决策点**：通过 `DECIDED`/`OPEN`/`NEXT`/`REJECTED` 等启发式标记（参考 Claudest 规范）从文本中提取。
2. **操作日志**：所有 `tool_use`（Read/Write/Edit/Bash/Skill/Agent/MCP）构成可回放的工作流。
3. **文件变更关联**：`file-history-snapshot` 把对话轮次与文件备份版本关联，便于与 git diff 对齐。
4. **成本信号**：`usage` 字段可评估哪些思考/操作消耗了大量 token。
5. **会话标题与主题**：`ai-title` 与 `last-prompt` 可用于聚类/检索。

---

## 8. 结论

- Claude Code 在本地以 **JSONL** 形式保存完整会话，主文件位于 `~/.claude/projects/<project>/<sessionId>.jsonl`。
- 每条记录有 `type` 字段，核心消息类型为 `user` 与 `assistant`；assistant 内容以块列表形式承载 `text` / `thinking` / `tool_use`。
- 可提取的字段覆盖：对话内容、思考过程、工具调用与结果、文件读写、Bash 命令、Skill/Agent/MCP 调用、token 用量、文件历史、项目上下文、时间戳等。
- 官方未公开稳定 schema，但第三方插件（scribe、claude-mem 等）已对该格式进行解析和再利用。
- 隐私风险主要来自：完整对话、本地绝对路径、源代码、外部抓取内容；API 密钥未以独立字段出现，但可能潜伏在命令参数或输出中，需脱敏处理。

---

## 附录：读取与会话分析脚本（本地临时使用）

以下 PowerShell/Python 片段可用于结构初探：

```python
import json
from collections import Counter

path = r"C:\Users\liyongquan\.claude\projects\C--Users-liyongquan\4d7d9ff2-6d84-471b-ae3f-88238be5c7e1.jsonl"
c = Counter()
with open(path, "r", encoding="utf-8") as f:
    for line in f:
        obj = json.loads(line)
        c[obj.get("type", "unknown")] += 1
print(c)
```

```python
# 提取 assistant 的所有 tool_use 名称
import json
from collections import Counter
tc = Counter()
path = r"C:\Users\liyongquan\.claude\projects\C--Users-liyongquan\4d7d9ff2-6d84-471b-ae3f-88238be5c7e1.jsonl"
with open(path, "r", encoding="utf-8") as f:
    for line in f:
        obj = json.loads(line)
        if obj.get("type") == "assistant":
            for block in obj.get("message", {}).get("content", []):
                if block.get("type") == "tool_use":
                    tc[block.get("name")] += 1
print(tc.most_common())
```
