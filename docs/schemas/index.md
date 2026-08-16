# Schema 索引

经验包 v0.2 的 JSON Schema 家族，位于 [`research/session-format/schemas/`](/research/session-format/schemas/)。

| Schema | 版本 | 用途 |
|---|---|---|
| `tag-v0.2.schema.json` | v0.2 | 标签分类体系（method / project_phase 等双入口轴） |
| `session-fragment-v0.2.schema.json` | v0.2 | Claude Code 会话切片，锚定到决策点 |
| `git-evidence-v0.2.schema.json` | v0.2 | 文件级代码变更证据 |
| `git-hunk-evidence-v0.2.schema.json` | v0.2 | Hunk 级代码变更证据 |
| `decision-point-v0.2.schema.json` | v0.2 | 结构化决策点（问题、选项、选择、理由、影响文件） |
| `decision-point-v0.1.schema.json` | v0.1 | 早期决策点 schema（保留用于对比） |
| `experience-unit-v0.2.schema.json` | v0.2 | 经验单元：决策 + 会话片段 + 代码证据 + 标签 + 课程映射 |
| `course-module-v0.2.schema.json` | v0.2 | 课程模块：按主题或时序组织的经验单元序列 |
| `learning-path-v0.2.schema.json` | v0.2 | 学习路径：模块组合或标签驱动的完整路径 |

## 使用方式

每个 schema 可直接用于校验对应 JSON/JSONL 文件。例如：

```bash
python research/session-format/prototypes/validate-experience-v0.2.py
```

该脚本会校验 `data/samples/cyber-game-m9/` 下全部 v0.2 文件的 schema 合规性、ID 唯一性、跨引用一致性与隐私扫描。

## 样本文件

| Schema | 样本文件 |
|---|---|
| Tag | `data/samples/cyber-game-m9/tags-v0.2.json` |
| Session Fragment | `data/samples/cyber-game-m9/session-fragments-v0.2.jsonl` |
| Git Evidence | `data/samples/cyber-game-m9/git-evidence-v0.2.jsonl` |
| Git Hunk Evidence | `data/samples/cyber-game-m9/git-hunk-evidence-v0.2.jsonl` |
| Decision Point | `data/samples/cyber-game-m9/decision-points-v0.2.jsonl` |
| Experience Unit | `data/samples/cyber-game-m9/experience-units-v0.2.jsonl` |
| Course Module | `data/samples/cyber-game-m9/course-modules-v0.2.json` |
| Learning Path | `data/samples/cyber-game-m9/learning-paths-v0.2.json` |
