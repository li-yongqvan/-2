# #1 Wayfinder Map 收尾计划书

**目标**：整理 #1 Wayfinder Map，使其从「M1/M2 密集决策期」过渡到「稳定维护期 + Phase 2 启动态」。

**当前状态**：#1 body 已较新，但 Frontier tickets 表格仍堆积大量已完成项，Blocking 关系图包含已关闭节点，视觉噪音较高。

---

## 1. 收尾目标

收尾后 #1 应满足：

1. **Frontier tickets 表格只显示当前 open/active 的 ticket**（目前仅剩 #10）。
2. **Decisions so far 完整收录所有已关闭/已接受的决策**（#2/#4/#6/#7/#8/#9/#11/#12/#13/#14/#15/#18 及 map maintenance process）。
3. **Blocking 关系图只保留活跃依赖关系**（已关闭节点移除或折叠）。
4. **Not yet specified 明确区分「留待 Phase 2」与「暂不处理」**：
   - Phase 2 处理：#10 police 第二经验包
   - 长期 fog：多人协作与版本管理
5. **执行一次 Map Audit**，确认 body、comments、GitHub API 状态一致。
6. **发布一条总结评论**，标志 M1/M2 收尾完成，Phase 2 启动。

---

## 2. 当前 #1 状态速览

| 维度 | 现状 |
|---|---|
| 开放 ticket | #10（police 第二经验包） |
| 已完成 decision | #2/#4/#6/#7/#8/#9/#11/#12/#13/#14/#15/#18 + map maintenance |
| Not yet specified | 多人协作与版本管理、#10 police 切片方案 |
| Out of scope | 暂无 |
| 主要问题 | Frontier 表格含大量已完成项，视觉噪音大；Blocking 图含已关闭节点 |

---

## 3. 任务清单与顺序

### Step 1: 准备本地干净副本

- [ ] 读取当前 #1 body（GitHub issue API 或 web）。
- [ ] 在本地创建 `wayfinder-map-body-vNEXT.md` 草稿。
- [ ] 对照 `docs/processes/map-maintenance.md` 的 Body Canonical Structure 检查各 section 完整性。

### Step 2: 清理 Frontier tickets 表格

- [ ] 仅保留 **#10 police** 为「无阻塞」。
- [ ] 其他已完成项从 Frontier 表格移除（它们已在 Decisions so far 中体现）。
- [ ] 如果希望保留历史，可在 Frontier 表格下方增加「Recently completed」折叠列表（可选，但建议不增加，避免重复）。

### Step 3: 验证 Decisions so far

- [ ] 确认 #13 capture mechanism、#14 final form、#15 acceptance criteria、#18 method ontology 均已加入。
- [ ] 确认 `docs/processes/map-maintenance.md` 以适当形式被引用（可在 Notes 或单独一行）。
- [ ] 去重：确保每个 decision 只出现一次。

### Step 4: 简化 Blocking 关系图

- [ ] 移除已关闭节点（#9/#12/#13/#14/#15/#18）。
- [ ] 保留活跃结构：
  ```
  #8 MVP 范围（已关闭）
     │
     ├──→ #10 处理 police 作为第二经验包
     │
     └──→ #2 数据结构（已完成）
              │
              ├──→ #4 时间对齐（已完成）
              │
              └──→ #6 审核工作流（已完成）
  ```
- [ ] 或进一步简化为只展示 #10 及其前置：
  ```
  #8 MVP 范围 → #10 police 第二经验包
  ```

### Step 5: 整理 Not yet specified

- [ ] 将 #10 的描述从 Not yet specified 移除（它已在 Frontier 中）。
- [ ] 保留「多人协作与版本管理」作为长期 fog，可加标注：「Phase 2 暂不解决」。

### Step 6: 更新 Notes

- [ ] 确认已发布 URL：`https://li-yongquan.github.io/experience-pack/`（仓库已重命名为 `experience-pack`）。
- [ ] 确认最终形态描述准确：组合形态（静态网站 + skill 语料），第一阶段搜索已完成。

### Step 7: 执行 Map Audit

按 `docs/processes/map-maintenance.md` 的 Audit 规格：

- [ ] Frontier 表格 open ticket 与 GitHub API open issues 一致。
- [ ] 标记已完成的 ticket 确实已关闭。
- [ ] Decisions so far 提到的 ticket 均有对应 closed issue。
- [ ] Not yet specified 无已解决项。
- [ ] Blocking 关系图节点与 Frontier 表格一致。
- [ ] Comments 中「body 已同步更新」确实对应 body 编辑记录。

**手工 audit 命令**：

```bash
gh issue view 1 --json body
gh issue list --state open --limit 50
gh issue list --state closed --limit 50
```

### Step 8: 提交 body 更新

- [ ] 将整理后的 body 写回 #1。
- [ ] 追加评论：
  > #1 Wayfinder Map M1/M2 收尾完成。Frontier 已清理为仅 #10；Decisions so far 补全至 #18；Blocking 关系图已简化；Map audit 0 discrepancies。Phase 2 聚焦 #10 police 第二经验包。

### Step 9: 关闭或保持 #1 开放

- [ ] **建议保持 #1 开放**：它作为 wayfinder map 是长期 living document。
- [ ] 如果坚持关闭 #1，需先完成 #10 和所有 Not yet specified；但这样会阻塞 Phase 2 启动，不推荐。

---

## 4. 验收标准

收尾完成的标准：

1. `gh issue view 1` 显示的 body 中，Frontier tickets 表格仅含 #10。
2. Decisions so far 包含 #2/#4/#6/#7/#8/#9/#11/#12/#13/#14/#15/#18，无重复。
3. Blocking 关系图不含已关闭节点。
4. Not yet specified 仅含「多人协作与版本管理」和（可选）#10 的 cross-reference。
5. 至少一条 comment 明确宣布 M1/M2 收尾完成。
6. 无 body/API 状态不一致（Map audit 通过）。

---

## 5. 风险与注意事项

| 风险 | 缓解 |
|---|---|
| 清理 Frontier 时误删活跃 ticket | 清理前对照 `gh issue list --state open` 核对 |
| Decisions so far 重复或遗漏 | 使用本地文本 diff 对比前后版本 |
| Blocking 图过度简化导致历史不可读 | 保留注释说明「历史节点见 Decisions so far」 |
| 多人协作 fog 被误判为已解决 | 明确标注「Phase 2 暂不处理」 |
| 仓库重命名导致 URL 失效 | 检查 body 中所有链接是否指向 `experience-pack` |

---

## 6. Phase 2 启动（收尾后立即开始）

收尾完成后，下一个焦点是 **#10 police 第二经验包**：

1. 用现有方法对 police 项目进行切片、脱敏、提取决策点。
2. 验证 capture mechanism 在 police 上的实际可用性。
3. 验证方法本体（collaboration_pattern 轴）是否能覆盖 police 的协作模式。
4. 产出 police 经验包的 v0.x 版本。

---

## 7. 建议调用的 Skills

- **`/wayfinder`** — 直接用于更新 #1 map。
- **`/grill-me`** — 如果需要决定「是否关闭 #1」或「Phase 2 优先级」。
- **`/implement`** — 如果决定写一个 `scripts/audit-wayfinder-map.py` 来自动化 Step 7。

---

**Generated**: 2026-08-17
**Plan Owner**: Wayfinder 维护者
**Expected Outcome**: #1 body 进入稳定维护态，Phase 2 聚焦 #10 police。
