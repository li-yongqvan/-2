# 工具脚本说明

`scripts/` 目录包含从 Claude Code 会话到结构化经验包的可复用批处理脚本。

## `scripts/scrubber.py`

**用途**：脱敏 Claude Code 本地会话 JSONL 文件。

**处理内容**：
- 本地路径替换为 `<HOME>` / `<PROJECT_ROOT>` / `<CLAUDE_HOME>`
- Windows 用户名替换为 `<USER>`
- git 邮箱替换为 `<GIT_EMAIL>`
- 文件历史快照替换为占位符
- 服务器凭据等敏感值按 `scrubbing-manifest.json` 规则替换

**输出**：`*-scrubbed.jsonl`。

## `scripts/generate_decision_points.py`

**用途**：从 grilling 决策记录生成结构化 `decision-points.jsonl`。

**输入**：grilling 决策 markdown（如 `grilling-decisions/`）。
**输出**：符合 `decision-point-v0.2.schema.json` 的 JSONL。

## `scripts/generate_experience_units_v0.2.py`

**用途**：从决策点、会话片段、git 证据、标签等生成 `experience-units-v0.2.jsonl`。

**输出**：符合 `experience-unit-v0.2.schema.json`，包含双入口 `entry_points`（method / project_phase）。

## 验证脚本

- `research/session-format/prototypes/validate-experience-v0.2.py`：全面校验 v0.2 样本
- `research/session-format/prototypes/validate-decision-points.py`：校验决策点
- `research/session-format/prototypes/align-session-to-git.py`：从会话片段生成 git 对齐链

## 运行示例

```bash
python scripts/scrubber.py \
  --input ~/.claude/projects/cyber-game/be0044d7.jsonl \
  --manifest data/samples/cyber-game-m9/scrubbing-manifest.json \
  --output data/samples/cyber-game-m9/session-be0044d7-scrubbed.jsonl

python scripts/generate_decision_points.py \
  --input grilling-decisions/ \
  --output data/samples/cyber-game-m9/decision-points-v0.2.jsonl

python scripts/generate_experience_units_v0.2.py \
  --samples data/samples/cyber-game-m9/ \
  --output data/samples/cyber-game-m9/experience-units-v0.2.jsonl
```
