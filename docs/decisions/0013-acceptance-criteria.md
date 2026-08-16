# Decision 0013: 经验包验收标准与质量门控

## Status

**Accepted** — 经 `/grill-me` 与用户对齐，作为 #15 跟踪。

- 父地图：[#1 AI 协作者经验包 · Wayfinder](https://github.com/li-yongqvan/-2/issues/1)
- 解决 fog：**一个经验包做到什么程度算完成、算可发布**
- 前置决策：[#8 MVP 范围](0008-mvp-scope.md)、[#9 审核工作流](0009-review-workflow-prototype.md)、[#11 捕获机制](0011-capture-mechanism.md)、[#12 最终形态](0012-final-form.md)
- 关联流程：[`docs/processes/map-maintenance.md`](../processes/map-maintenance.md)

---

## Context

经验包项目已解决捕获机制雾（M2）与最终形态雾，地图维护流程也已正式化。但 #1 wayfinder map 的 **Not yet specified** 中仍缺一片关键 fog：

> 一个经验包发布前必须满足哪些硬条件？哪些 warnings 可接受？审核状态 `approved` 是否自动进入发布清单？v0.x 到 v1.0 的晋级标准是什么？

本决策通过与用户对齐，把验收标准分为 **A 类硬门控**、**B 类质量门控** 与 **soft warnings**，并明确版本晋级、发布闸门与自动化/人工分工。

---

## Decision

| # | 决策点 | 结论 |
|---|---|---|
| 1 | 分层思路 | v0.x（预览版）与 v1.0（正式版）采用不同门控；v0.x 可容忍部分 warnings，v1.0 要求更严格 |
| 2 | A 类硬门控 | schema errors、missing UUIDs、duplicate IDs、cross-reference errors、privacy hits、dual-entry failures 必须为零 |
| 3 | B 类质量门控 | 模块深度、接口简单性、通用/专用分离、抽象层级一致；v0.x 有证据即可，v1.0 更严格 |
| 4 | Soft warnings | 允许 git-alignment 文件未命中、affected_files 差异、unresolved capture markers；必须记录原因、关联 unit/decision、人工复核 |
| 5 | 审核完成度（v0.x） | 不允许 draft 进入发布；允许 reviewed；核心学习路径必须 approved |
| 6 | 审核完成度（v1.0） | 所有 ExperienceUnit 必须 approved |
| 7 | 发布闸门 | 保留 #0009 原则：`approved` 与发布清单解耦；独立 `publish` 步骤生成不可变 manifest |
| 8 | 版本晋级 | v0.x→v0.(x+1)：hard gates 保持为零，不新增未记录 warnings；v0.x→v1.0：warnings 清零/记录、全部 approved、端到端验证通过 |
| 9 | 真实案例测试 | 放在 v1.0 上线之后，不作为 v1.0 阻塞项 |
| 10 | 自动化/人工分工 | A 类 hard gates 由脚本强制执行；B 类质量门控和学习体验由人工 sign-off；v1.0 前由项目作者本人负责测试 |

---

## Acceptance Criteria Detail

### A 类硬门控（必须为零）

| 检查项 | 说明 | 执行方式 |
|---|---|---|
| `schema_errors == 0` | 所有中间数据文件符合 v0.2 schema | `validate-experience-v0.2.py` |
| `missing_session_uuids == 0` | 所有 session fragment 引用的 message UUID 真实存在 | `validate-experience-v0.2.py` |
| `duplicate_ids == 0` | tag/fragment/evidence/decision/unit/module/path/marker ID 无重复 | `validate-experience-v0.2.py` |
| `cross_reference_errors == 0` | unit → decision/fragment/evidence/tag/module/path 等引用均有效 | `validate-experience-v0.2.py` |
| `privacy_hits == 0` | 经验包数据中不含脱敏清单定义的敏感字符串或密钥模式 | `validate-experience-v0.2.py` |
| `dual_entry_failures == 0` | 每个 ExperienceUnit 至少包含 method 和 project_phase 两个维度的 tag | `validate-experience-v0.2.py` |

任何 A 类错误存在时，`publish` 步骤必须拒绝生成发布清单。

### B 类质量门控（v0.x 有证据即可；v1.0 更严格）

| 原则 | 验收问题 | 证据形式 |
|---|---|---|
| 模块应该是深的 | `ExperienceUnit` / `DecisionPoint` / `CourseModule` 等接口职责是否单一清晰？ | 代码审查 / schema review |
| 简单接口比简单实现更重要 | 验证脚本、发布脚本、双入口站点的 API 是否对常见用例简单？ | 使用示例 / 脚本签名审查 |
| 通用代码与专用代码分开 | `scripts/` 中通用流水线与 cyber-game 专用样本是否解耦？ | 目录结构 / 导入关系审查 |
| 不同层应有不同抽象 | session → fragment → decision → unit → module → path 层级引用是否清晰无跳跃？ | 数据流审查 |
| 设计两次 | 关键接口是否考虑过第二种设计？ | 决策文档中的备选方案记录 |
| 增量是抽象概念 | 版本升级是否基于架构成熟度而非单纯加功能？ | 版本说明 |

### Soft Warnings（可接受但需记录）

| 类型 | 示例 | 处理要求 |
|---|---|---|
| git-alignment 文件未命中 | `affected_file 'src/engine/Link.ts' not found in git-alignment changed_files` | 写入 `.needs_review`，说明原因，关联 decision/unit |
| affected_files 与实际 diff 差异 | hunk 切片时间与 git diff 时间不完全一致 | 在验证报告中标注 |
| unresolved capture markers | `anchor_confidence` 为 `unresolved` | 默认进入 `.needs_review`，经 grilling 或审核后处理 |

Soft warnings 允许存在，但：

1. 必须在验证报告或 `.needs_review` 中写明原因；
2. 每个 warning 必须关联到具体 decision 或 ExperienceUnit；
3. 不得无限制累积；每次 release 前需人工复核并决定「修复 / 接受 / 转 issue」。

### 审核完成度

```text
v0.x:
  - draft → 不允许进入发布清单
  - reviewed → 允许，但需记录备注
  - approved → 核心学习路径必须全部 approved

v1.0:
  - 所有 ExperienceUnit 必须 approved
```

### 发布闸门

沿用 #0009 关键原则：

> `approved` 是作者审核状态，**不会自动进入发布清单**；发布清单由独立的 `publish` 步骤在某一时刻对 `approved` 单元做 snapshot 生成。

推荐命令：

```bash
python scripts/publish_experience_package.py --version v0.3.0
```

`publish` 步骤职责：

1. 读取 sidecar 中 approved / 部分 reviewed 的 unit；
2. 运行 A 类 hard gates 检查；
3. 生成不可变的 package manifest（包含 unit 列表、版本、时间戳、checksum）；
4. 输出到 `release/` 或 `dist/` 目录。

发布清单一旦生成即不可变；后续新 approved 的 unit 需下次 publish 才能进入。

### 版本晋级

**v0.x → v0.(x+1)**：

- A 类 hard gates 保持为零；
- 不允许新增未记录的 soft warnings；
- 新增/重构的 ExperienceUnit 必须满足当前版本审核要求；
- 双入口站点和验证脚本仍可正常运行。

**v0.x → v1.0**：

- 所有 A 类 hard gates 为零；
- 所有 soft warnings 已修复，或在发布说明中明确接受并记录原因；
- 所有 ExperienceUnit 状态为 `approved`；
- 通过端到端验证：
  - 静态站点可访问；
  - 双入口导航正常；
  - 学习路径可完成；
- 发布清单由独立 `publish` 步骤生成并附带 checksum；
- 关键决策文档完整。

**v1.0 之后**：

- 真实项目案例的大规模验证和外部学习者试用放在 v1.0 上线后进行；
- 不作为 v1.0 发布阻塞项。

---

## Automation vs Manual Sign-off

| 维度 | 脚本自动化 | 人工 sign-off |
|---|---|---|
| A 类 hard gates | ✅ 强制执行 | — |
| B 类质量门控 | — | ✅ review-workflow + checklist |
| 学习体验（叙事、可读性） | — | ✅ 作者判断（v1.0 前由本人测试） |
| 发布清单确认 | 脚本生成 | ✅ 作者确认后执行 publish |
| Soft warnings 复核 | 脚本输出 | ✅ 每次 release 前人工决定 |

### v0.x 发布前人工 checklist

```markdown
- [ ] 已阅读所有 soft warnings 并理解原因
- [ ] 核心学习路径上的 ExperienceUnit 已 approved
- [ ] 发布清单内容已核对
- [ ] 站点已在本地或 staging 验证可访问
```

### v1.0 发布前人工 checklist

```markdown
- [ ] 所有 ExperienceUnit 已 approved
- [ ] 所有 soft warnings 已修复或记录
- [ ] 端到端验证通过
- [ ] 发布清单已生成并核对
```

---

## Verification Criteria

1. `validate-experience-v0.2.py` 默认模式输出清晰的 errors / warnings 分类；
2. `validate-experience-v0.2.py --strict` 模式把 soft warnings 提升为 errors；
3. 当前 cyber-game M9 样本数据在默认模式下 A 类 hard gates 为零；
4. 当前 4 条 git-alignment soft warnings 被正确分类并记录原因；
5. `docs/processes/map-maintenance.md` 的 Close Ticket Checklist 包含「确认验收标准已满足」；
6. #1 wayfinder map 把「验收标准 fog」移到 Decisions so far，并新增 #15 到 Frontier tickets（随后关闭）。

---

## Open Questions

| 问题 | 建议处理 |
|---|---|
| `publish` 脚本具体实现位置？ | 新增 `scripts/publish_experience_package.py`，本决策只定义行为契约 |
| package manifest schema？ | 作为最终形态（#14）的后续工作，本决策不展开 |
| 是否引入 CI 自动跑验证脚本？ | v1.0 前可先用本地脚本；CI 作为增强项后续讨论 |

---

## Related Issues

- Parent map: [#1](https://github.com/li-yongqvan/-2/issues/1)
- This decision: **#15**
- Blocked by: [#2](https://github.com/li-yongqvan/-2/issues/2)、[#6](https://github.com/li-yongqvan/-2/issues/6)、[#9](https://github.com/li-yongqvan/-2/issues/9)、[#13](https://github.com/li-yongqvan/-2/issues/13)
- Unblocks: [#14](https://github.com/li-yongqvan/-2/issues/14) 最终形态第一阶段搜索功能的发布质量基础
