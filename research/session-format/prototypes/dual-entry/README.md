# Dual Entry Prototype

#7 可交互工具的双入口浏览原型。

**问题**：ExperienceUnit v0.2 已经有了 `entry_points`（method / timeline / theme / skill），浏览端应该提供什么样的入口体验？

这是一个可丢弃的 Astro 静态站原型，用来验证四个决策点：

1. **双入口形态**：两条独立路由 `/by-method` 和 `/by-project`，共享详情页 `/unit/{id}`。
2. **详情页布局**：三栏（左=对话片段，中=代码 diff，右=方法说明）。
3. **交互深度**：evidence 默认折叠，点击展开；时间轴；diff 行级 +/- 高亮。
4. **技术栈**：Astro 静态生成，数据来自真实 JSON/JSONL。

## 运行

```bash
cd research/session-format/prototypes/dual-entry
npm install
npm run dev
```

启动后访问 `http://localhost:4321`（Astro 默认端口）。

## Build

```bash
npm run build
```

产物在 `dist/`。可通过环境变量覆盖 base path，方便 #9 部署到 GitHub Pages：

```bash
ASTRO_BASE='/-2/' npm run build
```

## 数据

原型从 `data/samples/cyber-game-m9/` 真实加载，未写死：

- `experience-units-v0.2.jsonl`
- `session-fragments-v0.2.jsonl`
- `git-hunk-evidence-v0.2.jsonl`
- `decision-points-v0.2.jsonl`
- `tags-v0.2.json`
- `course-modules-v0.2.json`

## 结构

```
src/
  layouts/Base.astro       # 站点导航与 HTML 骨架
  components/
    UnitCard.astro         # 列表卡片
    Timeline.astro         # 决策时间轴
    DiffViewer.astro       # 可折叠 hunk diff + 行高亮
  pages/
    index.astro            # 双入口首页
    by-method.astro        # 按方法主题分组
    by-project.astro       # 按课程模块/项目时间线分组
    unit/[id].astro        # 三栏详情页
  data/loader.ts           # JSON/JSONL 加载与索引
public/styles.css          # 样式
```

## 扩展点

- **GitHub Pages 部署**：调整 `astro.config.mjs` 的 `base`，与 #9 的发布路径对齐。
- **轮次导航**：当前 sample 数据没有完整 message round，后续可接入真实 session 切片后在 `DiffViewer` 旁增加轮次切换。
- **全文搜索**：可在 build 时生成搜索索引 JSON，前端用轻量 fuse.js 搜索 unit title/question。
- **审核操作**：可复用 #5 review-workflow 原型的状态机，给详情页加 approve/reject 按钮（当前只读）。
- **响应式细化**：三栏在窄屏上目前是垂直堆叠，可进一步优化各栏优先级与折叠策略。

## 依赖

- [Astro](https://astro.build/) — 静态站点生成器
