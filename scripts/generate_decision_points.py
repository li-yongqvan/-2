#!/usr/bin/env python3
"""
Generate decision-points.jsonl for cyber-game M8-M9 MVP experience package.

Sources:
- docs/decisions/0008-mvp-scope.md
- ~/.claude/projects/.../memory/grilling-decisions/m8-m9-sandbox-gamification-decisions.md
- ~/.claude/projects/.../memory/grilling-m9-qa-record.md
"""

import json
from pathlib import Path

DECISIONS = [
    # From grilling-decisions/m8-m9-sandbox-gamification-decisions.md
    {
        "id": "cyber-game-m9-001",
        "title": "M8-M9 合并推进还是拆分推进？",
        "category": "范围取舍",
        "category_en": "scope_tradeoff",
        "source": "grilling-decisions/m8-m9-sandbox-gamification-decisions.md",
        "source_type": "grilling",
        "question": "HANDOFF.md 里 M8（沙盒）和 M9（游戏化+发布）原本是分开的两个里程碑。合并推进可以一次交付三件事，减少交接开销；拆分推进更安全，每步可独立验收，降低回滚粒度。",
        "options": [
            {"label": "A. 合并推进", "consequence": "一次性交付沙盒+游戏化+发布准备，验收标准集中，但单次改动量大、回滚粒度粗"},
            {"label": "B. 拆分推进", "consequence": "先 M8 沙盒，再 M9 游戏化+发布；两次独立验收，风险可控，但 M9 需要依赖 M8 的进度存储"}
        ],
        "selected_option": "B. 拆分推进",
        "rationale": "风险可控，每步可独立验收。",
        "affected_files": ["src/store/simulatorStore.ts", "src/store/progressStore.ts", "HANDOFF.md"],
        "unresolved_tail": "M9 依赖 M8 的 progressStore 骨架——M8 验收时 progressStore 还未完整实现，需确保 M8 不耦合进度逻辑。",
        "timestamp": "2026-07-29T05:16:56.947Z",
        "related_commit": "dd93cc9"
    },
    {
        "id": "cyber-game-m9-002",
        "title": "教学版沙盒的核心目标是什么？",
        "category": "任务定义",
        "category_en": "task_definition",
        "source": "grilling-decisions/m8-m9-sandbox-gamification-decisions.md",
        "source_type": "grilling",
        "question": "沙盒的用户定位决定了引擎 API 的开发深度。如果目标是'自由搭建网络'，Simulator 需要完整动态拓扑 API；如果目标是'观察已知场景'，大部分引擎改动可推迟。",
        "options": [
            {"label": "A. 自由搭建优先", "consequence": "必须实现完整动态拓扑 API、设备参数编辑、任意连线/断线，引擎层改动最大"},
            {"label": "B. 预设体验优先", "consequence": "预设场景加载后即可运行；引擎 API 只需支持加载已有 NetworkConfig，增删能力推迟到完整版"}
        ],
        "selected_option": "B. 预设体验优先",
        "rationale": "教学版先保证可运行的预设场景，降低引擎改动量。",
        "affected_files": ["src/engine/Simulator.ts", "src/levels/sandboxPresets.ts", "src/ui/Sandbox.tsx"],
        "unresolved_tail": "后续完整版沙盒需要从'预设体验'升级到'自由搭建'，引擎 API 的接口设计应提前留好扩展槽。",
        "timestamp": "2026-07-29T05:16:56.947Z",
        "related_commit": "dd93cc9"
    },
    {
        "id": "cyber-game-m9-003",
        "title": "教学版沙盒是否支持增删设备/链路？",
        "category": "范围取舍",
        "category_en": "scope_tradeoff",
        "source": "grilling-decisions/m8-m9-sandbox-gamification-decisions.md",
        "source_type": "grilling",
        "question": "'预设体验优先'确立后，仍需要决定玩家能在多大程度上修改预设场景。只读拖拽最省工作但限制实验价值；允许增删设备的'轻量编辑'比完整自由搭建更实用。",
        "options": [
            {"label": "A. 只读预设+拖拽", "consequence": "引擎零改动，Simulator 无需动态 API，但玩家只能看不能改"},
            {"label": "B. 预设+轻量编辑", "consequence": "Simulator 需要 addDevice/removeDevice/addLink/removeLink/moveDevice/toJson，是全部引擎变更中最复杂的一项"},
            {"label": "C. 自由搭建", "consequence": "需要完整的设备参数编辑、任意接口创建/删除、路由表配置等，改动量最大"}
        ],
        "selected_option": "B. 预设+轻量编辑",
        "rationale": "在预设基础上提供轻量编辑能力，平衡教学价值与实现成本。",
        "affected_files": ["src/engine/Simulator.ts", "src/engine/Device.ts", "src/engine/factories.ts", "src/engine/Link.ts"],
        "unresolved_tail": "设备接口数量在沙盒中固定（主机 1 个、交换机 4 个），完整版需要动态添加/删除接口的能力。",
        "timestamp": "2026-07-29T05:16:56.947Z",
        "related_commit": "dd93cc9"
    },
    {
        "id": "cyber-game-m9-004",
        "title": "沙盒提供多少个预设？",
        "category": "范围取舍",
        "category_en": "scope_tradeoff",
        "source": "grilling-decisions/m8-m9-sandbox-gamification-decisions.md",
        "source_type": "grilling",
        "question": "预设数量影响初始开发量和用户覆盖。关卡配置复用零成本，沙盒专用预设需要设计拓扑和 IP 规划。",
        "options": [
            {"label": "A. 7 个", "consequence": "4 个关卡 + 3 个沙盒专用，覆盖面最广"},
            {"label": "B. 6 个", "consequence": "减少一个沙盒专用预设"},
            {"label": "C. 4 个", "consequence": "仅复用关卡配置，不新增沙盒专用场景"}
        ],
        "selected_option": "A. 7 个",
        "rationale": "覆盖面最广，包含 blank、small-lan、star、dmz 等教学场景。",
        "affected_files": ["src/levels/sandboxPresets.ts", "src/ui/Sandbox.tsx"],
        "unresolved_tail": "预设的 IP 网段规划需避免与关卡默认 192.168.x.x 冲突（已使用 10.0.x.x 子网）。",
        "timestamp": "2026-07-29T05:16:56.947Z",
        "related_commit": "dd93cc9"
    },
    {
        "id": "cyber-game-m9-005",
        "title": "Simulator 动态编辑时是重新创建还是增量变更？",
        "category": "方法选择",
        "category_en": "method_selection",
        "source": "grilling-decisions/m8-m9-sandbox-gamification-decisions.md",
        "source_type": "grilling",
        "question": "增删设备/链路时有两种实现路线。重新创建 Simulator 最安全，但会丢失运行时状态；增量变更保留状态，但需维护内部结构同步。",
        "options": [
            {"label": "A. 重新创建 Simulator", "consequence": "每次编辑 new Simulator(newConfig)，简单安全，但丢在途包、ARP 表、连接状态"},
            {"label": "B. 增量变更 Simulator", "consequence": "新增 addDevice/removeDevice/addLink/removeLink/moveDevice，需仔细维护 interfaceToLink、linkId、promiscuousHooks"}
        ],
        "selected_option": "B. 增量变更",
        "rationale": "保证沙盒体验连贯性，编辑时不丢失运行时状态。",
        "affected_files": ["src/engine/Simulator.ts", "src/engine/Interface.ts"],
        "unresolved_tail": "从构造函数中提取 addLinkInternal 重构以减少代码重复。",
        "timestamp": "2026-07-29T05:16:56.947Z",
        "related_commit": "dd93cc9"
    },
    {
        "id": "cyber-game-m9-006",
        "title": "拖拽时设备位置在哪一层更新？",
        "category": "方法选择",
        "category_en": "method_selection",
        "source": "grilling-decisions/m8-m9-sandbox-gamification-decisions.md",
        "source_type": "grilling",
        "question": "位置更新可以发生在渲染层、引擎层或拖拽结束后提交，各有优劣。",
        "options": [
            {"label": "A. 渲染层先更新", "consequence": "响应最快，但渲染与引擎短暂不同步"},
            {"label": "B. 引擎层先更新", "consequence": "架构最一致，但可能粘滞"},
            {"label": "C. 拖拽结束提交", "consequence": "renderer 维护拖拽偏移量，pointerup 时一次性提交最终位置并触发 rebuild。最简单"}
        ],
        "selected_option": "C. 拖拽结束提交",
        "rationale": "实现最简单，避免渲染与引擎状态频繁同步。",
        "affected_files": ["src/renderer/TopologyRenderer.ts", "src/engine/Device.ts"],
        "unresolved_tail": "拖拽过程中链路端点不会实时跟随（需通过下一决策解决）。",
        "timestamp": "2026-07-29T05:16:56.947Z",
        "related_commit": "dd93cc9"
    },
    {
        "id": "cyber-game-m9-007",
        "title": "拖拽过程中链路是否实时跟随？",
        "category": "方法选择",
        "category_en": "method_selection",
        "source": "grilling-decisions/m8-m9-sandbox-gamification-decisions.md",
        "source_type": "grilling",
        "question": "拖拽结束提交意味着拖拽中链路不会移动——节点飞了线没动，体验差。但如果让链路实时跟随，需要 renderer 内部额外维护关联链路的更新。",
        "options": [
            {"label": "A. 拖拽中实时更新链路", "consequence": "pointermove 中同时调用 updateLinksForDevice + updatePacketsForDevice，视觉上实时跟随；需 renderer 维护拖拽节点与受影响链路的引用关系"},
            {"label": "B. 拖拽结束统一 rebuild", "consequence": "简单但链路端点短暂不同步"}
        ],
        "selected_option": "A. 拖拽中实时更新链路（严格控制在 renderer 内部，不提交到引擎）",
        "rationale": "提升视觉体验，同时保持引擎状态只在拖拽结束更新。",
        "affected_files": ["src/renderer/TopologyRenderer.ts"],
        "unresolved_tail": "pointermove 中高频调用可能产生性能压力；后续可加入 requestAnimationFrame 节流。",
        "timestamp": "2026-07-29T05:16:56.947Z",
        "related_commit": "dd93cc9"
    },
    {
        "id": "cyber-game-m9-008",
        "title": "沙盒状态放在现有 simulatorStore 还是独立 slice？",
        "category": "方法选择",
        "category_en": "method_selection",
        "source": "grilling-decisions/m8-m9-sandbox-gamification-decisions.md",
        "source_type": "grilling",
        "question": "simulatorStore 目前管理所有运行时状态。如果沙盒直接共享 store，会'看到' objectives、levelComplete 等关卡字段——这些在沙盒中无意义。",
        "options": [
            {"label": "A. 共享 store", "consequence": "沙盒和关卡公用一个 store，减少代码分支，但沙盒会看到无关的 level 字段"},
            {"label": "B. 独立沙盒 slice", "consequence": "在 simulatorStore 内增加 sandboxMode/sandboxPreset/linkMode/linkSource 字段，沙盒模式下 objectives/levelMeta 设空值"}
        ],
        "selected_option": "B. 独立沙盒 slice",
        "rationale": "逻辑隔离，避免沙盒被关卡字段污染。",
        "affected_files": ["src/store/simulatorStore.ts", "src/ui/Sandbox.tsx"],
        "unresolved_tail": "独立 slice 仍然在同一个 Zustand store 内，如后续沙盒逻辑膨胀，可考虑真正拆成独立 store。",
        "timestamp": "2026-07-29T05:16:56.947Z",
        "related_commit": "dd93cc9"
    },
    {
        "id": "cyber-game-m9-009",
        "title": "进度持久化放在 simulatorStore 还是独立 store？",
        "category": "方法选择",
        "category_en": "method_selection",
        "source": "grilling-decisions/m8-m9-sandbox-gamification-decisions.md",
        "source_type": "grilling",
        "question": "Zustand 的 persist middleware 会序列化 store 中所有 partialize 选中的字段。如果 persist 挂在 simulatorStore 上，Simulator 实例（不可序列化）必须排除，但 runtime 和持久化状态会混在一起。",
        "options": [
            {"label": "A. 单一 store + persist", "consequence": "通过 partialize 只序列化 unlocked/completed，其余不持久化。但 runtime 和持久化状态混在一起"},
            {"label": "B. 独立 progress store", "consequence": "新建 progressStore.ts，仅管理 unlocked/completed，独立 persist。两个 store 之间需要协调"}
        ],
        "selected_option": "B. 独立 progress store",
        "rationale": "持久化状态与运行时状态分离，结构更清晰。",
        "affected_files": ["src/store/progressStore.ts", "src/store/simulatorStore.ts"],
        "unresolved_tail": "两个 store 之间的调用方向是单向的（simulatorStore → progressStore），但如果未来需要反向查询，会增加耦合。",
        "timestamp": "2026-07-29T05:16:56.947Z",
        "related_commit": "dd93cc9"
    },
    {
        "id": "cyber-game-m9-010",
        "title": "关卡完成时 simulatorStore 如何通知 progressStore？",
        "category": "方法选择",
        "category_en": "method_selection",
        "source": "grilling-decisions/m8-m9-sandbox-gamification-decisions.md",
        "source_type": "grilling",
        "question": "两个独立 store 后需要确定协调方式。直接调用最简单但耦合，事件总线解耦但增加抽象，组件层协调依赖 React 生命周期。",
        "options": [
            {"label": "A. store 直接调用", "consequence": "simulatorStore.checkObjectives 中 import 并调用 progressStore.getState().recordCompletion()，代码最直接"},
            {"label": "B. 事件总线", "consequence": "需要新增 pub/sub 机制"},
            {"label": "C. 组件层协调", "consequence": "LevelPlayer 监听 levelComplete 状态变化，调用 progressStore 记录。store 间无直接耦合"}
        ],
        "selected_option": "A. store 直接调用",
        "rationale": "代码最直接，当前只有一个消费方。",
        "affected_files": ["src/store/simulatorStore.ts"],
        "unresolved_tail": "如果未来有多个地方需要响应关卡完成事件，直接调用模式会扩散，可能需要升级为事件总线。",
        "timestamp": "2026-07-29T05:16:56.947Z",
        "related_commit": "dd93cc9"
    },
    {
        "id": "cyber-game-m9-011",
        "title": "关卡解锁规则是怎样的？",
        "category": "约束声明",
        "category_en": "constraint_declaration",
        "source": "grilling-decisions/m8-m9-sandbox-gamification-decisions.md",
        "source_type": "grilling",
        "question": "解锁规则影响 Home.tsx 的渲染逻辑和 progressStore 的 unlock 判断。线性解锁最简单；跳跃解锁更灵活但允许跳关可能破坏教学递进性。",
        "options": [
            {"label": "A. 线性解锁", "consequence": "完成 01 解锁 02，以此类推。实现最简单"},
            {"label": "B. 跳跃解锁", "consequence": "完成任意关卡后自动解锁下一个未解锁关卡"},
            {"label": "C. 线性+调试开关", "consequence": "线性解锁为基础，但允许通过设置或调试入口手动解锁全部关卡"}
        ],
        "selected_option": "A. 线性解锁（01 和 sandbox 默认已解锁）",
        "rationale": "实现最简单，保证教学递进性。",
        "affected_files": ["src/store/progressStore.ts", "src/ui/Home.tsx"],
        "unresolved_tail": "没有手动解锁全部关卡的调试入口，开发者测试需要手动通关每个前置关卡。",
        "timestamp": "2026-07-29T05:16:56.947Z",
        "related_commit": "dd93cc9"
    },
    {
        "id": "cyber-game-m9-012",
        "title": "徽章评分要做到什么粒度？",
        "category": "范围取舍",
        "category_en": "scope_tradeoff",
        "source": "grilling-decisions/m8-m9-sandbox-gamification-decisions.md",
        "source_type": "grilling",
        "question": "评分粒度决定 progressStore 和 LevelMeta 的数据结构。金银铜需要新增时间/步数计数器；仅完成徽章最轻量。",
        "options": [
            {"label": "A. 按 tick + 操作步数", "consequence": "需要新增 tick 计数器和 action 计数器，LevelMeta 需增加 parTime/parSteps"},
            {"label": "B. 只按时间", "consequence": "只需 tick 计数器，但评分维度不够全面"},
            {"label": "C. 仅完成徽章", "consequence": "仅记录 completedAt 时间戳，LevelMeta 不增加任何字段。最简单"}
        ],
        "selected_option": "C. 仅完成徽章",
        "rationale": "M9 先保证进度系统可用，复杂评分留给后续版本。",
        "affected_files": ["src/store/progressStore.ts", "src/types/level.ts", "src/ui/Home.tsx"],
        "unresolved_tail": "后续完整版评分升级需要新增 tick 计数器和 parTime/parSteps 到 LevelMeta。",
        "timestamp": "2026-07-29T05:16:56.947Z",
        "related_commit": "dd93cc9"
    },
    {
        "id": "cyber-game-m9-013",
        "title": "沙盒导出 JSON 的格式是什么？",
        "category": "方法选择",
        "category_en": "method_selection",
        "source": "grilling-decisions/m8-m9-sandbox-gamification-decisions.md",
        "source_type": "grilling",
        "question": "导出格式决定了 exportSandboxScene action 的实现和后续导入功能的基础。纯 NetworkConfig 最简单但缺少元数据；SandboxScene 带元数据但需要新类型。",
        "options": [
            {"label": "A. NetworkConfig", "consequence": "直接调用 simulator.toJson()，与关卡配置同结构，零额外工作。但无法区分'场景'和'关卡配置'"},
            {"label": "B. SandboxScene", "consequence": "包装一层 { version, name, createdAt, config: NetworkConfig }，为未来扩展预留空间"}
        ],
        "selected_option": "B. SandboxScene（含最小元数据）",
        "rationale": "为未来导入/版本管理预留空间。",
        "affected_files": ["src/store/simulatorStore.ts", "src/engine/Simulator.ts"],
        "unresolved_tail": "SandboxScene 目前仅用于导出，导入功能留给完整版。",
        "timestamp": "2026-07-29T05:16:56.947Z",
        "related_commit": "dd93cc9"
    },
    {
        "id": "cyber-game-m9-014",
        "title": "SandboxScene 的元数据包含哪些字段？",
        "category": "范围取舍",
        "category_en": "scope_tradeoff",
        "source": "grilling-decisions/m8-m9-sandbox-gamification-decisions.md",
        "source_type": "grilling",
        "question": "元数据字段数量决定格式的复杂度和未来扩展性。最小元数据保留扩展空间但不膨胀。",
        "options": [
            {"label": "A. 最小元数据", "consequence": "version + name + createdAt + config，为未来扩展留口子"},
            {"label": "B. 标准元数据", "consequence": "加 description、tags，更完整但教学版不一定需要"},
            {"label": "C. 完整运行时快照", "consequence": "加当前 tick、在途包、ARP 表等，可实现完全恢复，但复杂且不稳定"}
        ],
        "selected_option": "A. 最小元数据",
        "rationale": "保持格式简单，保留扩展性。",
        "affected_files": ["src/store/simulatorStore.ts"],
        "unresolved_tail": "version 字段目前固定为 1，后续格式变更时需要版本迁移逻辑。",
        "timestamp": "2026-07-29T05:16:56.947Z",
        "related_commit": "dd93cc9"
    },
    {
        "id": "cyber-game-m9-015",
        "title": "Router 设备在沙盒中是什么状态？",
        "category": "约束声明",
        "category_en": "constraint_declaration",
        "source": "grilling-decisions/m8-m9-sandbox-gamification-decisions.md",
        "source_type": "grilling",
        "question": "Router 目前是占位实现（没有完整三层转发逻辑）。如果沙盒预设不需要 Router，可以不实现；但沙盒工具栏是否出现 Router 按钮影响用户体验。",
        "options": [
            {"label": "A. 必须先实现 Router", "consequence": "完整实现 Router 的三层路由/转发/ARP 代理，工作量大，阻塞 M8"},
            {"label": "B. 继续用 Firewall", "consequence": "用 Firewall 代替 Router 做三层转发，Router 不出现在沙盒"},
            {"label": "C. 占位 Router", "consequence": "沙盒工具栏仍有 Router 按钮，标注'即将上线'，点击后创建占位设备（不可转发）"}
        ],
        "selected_option": "C. 占位 Router",
        "rationale": "不阻塞 M8，同时保留 UI 占位提示。",
        "affected_files": ["src/engine/devices/Router.ts", "src/ui/Sandbox.tsx", "src/engine/factories.ts"],
        "unresolved_tail": "Router 三层转发是完整版沙盒和 M10+ 的核心任务。",
        "timestamp": "2026-07-29T05:16:56.947Z",
        "related_commit": "dd93cc9"
    },
    {
        "id": "cyber-game-m9-016",
        "title": "沙盒中 DevicePanel 是只读还是可编辑？",
        "category": "范围取舍",
        "category_en": "scope_tradeoff",
        "source": "grilling-decisions/m8-m9-sandbox-gamification-decisions.md",
        "source_type": "grilling",
        "question": "设备参数编辑能力决定教学版沙盒的'轻量编辑'有多轻量。只读最简单，允许编辑名称和网络参数增加实用性但需要新增 store action。",
        "options": [
            {"label": "A. 只读设备面板", "consequence": "复用现有 DevicePanel 组件，零改动"},
            {"label": "B. 仅编辑名称", "consequence": "需要新增 updateDeviceConfig action，仅修改 device.name"},
            {"label": "C. 编辑名称+网络参数", "consequence": "需要新增 updateDeviceConfig action + 沙盒专用设备配置面板"}
        ],
        "selected_option": "C. 编辑名称+网络参数（MAC 由系统生成不可改）",
        "rationale": "提升沙盒教学价值，同时控制改动范围。",
        "affected_files": ["src/store/simulatorStore.ts", "src/ui/Sandbox.tsx", "src/engine/Device.ts"],
        "unresolved_tail": "接口级别的编辑（修改 MAC、增减接口、修改 IP 而不仅是第一接口）留给完整版。",
        "timestamp": "2026-07-29T05:16:56.947Z",
        "related_commit": "dd93cc9"
    },
    # From grilling-m9-qa-record.md
    {
        "id": "cyber-game-m9-017",
        "title": "Q1：本次「执行 M9 的规划」希望做什么？",
        "category": "任务定义",
        "category_en": "task_definition",
        "source": "grilling-m9-qa-record.md",
        "source_type": "grilling-qa",
        "question": "M9 在代码库中已实际完成，grill-me 的核心任务是确认这次到底要做什么。",
        "options": [
            {"label": "A. 验收当前已实现的 M9", "consequence": "确认没有回归，再衔接到 M10+"},
            {"label": "B. 重新实现/改造 M9", "consequence": "在已经 green 的状态上重复造轮子"},
            {"label": "C. 以 M9 为起点，直接进入 M10+ 规划", "consequence": "跳过验收，直接进入下一阶段规划"},
            {"label": "D. 其他", "consequence": ""}
        ],
        "selected_option": "A. 验收当前已实现的 M9",
        "rationale": "从代码和文档看 M9 已完成，先跑验收清单确认没有回归。",
        "affected_files": [],
        "unresolved_tail": "",
        "timestamp": "2026-07-29T09:26:04.898Z",
        "related_commit": "dd93cc9"
    },
    {
        "id": "cyber-game-m9-018",
        "title": "Q2：验收深度要做到什么程度？",
        "category": "方法选择",
        "category_en": "method_selection",
        "source": "grilling-m9-qa-record.md",
        "source_type": "grilling-qa",
        "question": "需要确定 M9 验收的彻底程度，平衡效率与置信度。",
        "options": [
            {"label": "A. 仅运行自动化校验", "consequence": "能确认代码健康，但无法确认玩家进度等 UI 状态"},
            {"label": "B. 自动化校验 + 启动开发服务器做快速冒烟", "consequence": "在效率和置信度之间最平衡"},
            {"label": "C. 自动化校验 + 完整手动验收清单", "consequence": "最彻底但耗时较长，很多清单项其实是 M7/M8 的回归内容"},
            {"label": "D. 其他", "consequence": ""}
        ],
        "selected_option": "B. 自动化校验 + 启动开发服务器做快速冒烟",
        "rationale": "M9 核心是玩家进度和首页状态，需要浏览器里看一眼才能确认；完整清单耗时太长。",
        "affected_files": [],
        "unresolved_tail": "",
        "timestamp": "2026-07-29T09:26:04.898Z",
        "related_commit": "dd93cc9"
    },
    {
        "id": "cyber-game-m9-019",
        "title": "Q3：是否需要把验收结果写回计划文件或更新 HANDOFF.md？",
        "category": "方法选择",
        "category_en": "method_selection",
        "source": "grilling-m9-qa-record.md",
        "source_type": "grilling-qa",
        "question": "当前处在 plan mode，验收结论写到哪里最自然。",
        "options": [
            {"label": "A. 不写回任何文档", "consequence": "验收结果无法追溯"},
            {"label": "B. 更新当前的个人计划文件", "consequence": "最自然，不会污染项目文档"},
            {"label": "C. 更新项目 HANDOFF.md", "consequence": "会成为项目历史记录，但当前阶段可能过早"},
            {"label": "D. 同时更新计划文件与 HANDOFF.md", "consequence": "同步成本高"}
        ],
        "selected_option": "B. 更新当前的个人计划文件",
        "rationale": "plan mode 中写入本次计划文件最自然，后续如需项目历史记录再单独更新 HANDOFF.md。",
        "affected_files": [],
        "unresolved_tail": "",
        "timestamp": "2026-07-29T09:26:04.898Z",
        "related_commit": "dd93cc9"
    },
    {
        "id": "cyber-game-m9-020",
        "title": "Q4：是否同意退出 plan mode 并开始执行验收？",
        "category": "验收/终止",
        "category_en": "acceptance_termination",
        "source": "grilling-m9-qa-record.md",
        "source_type": "grilling-qa",
        "question": "细节已收敛，需要确认是否从 plan mode 退出并开始执行。",
        "options": [
            {"label": "A. 同意，退出 plan mode 并开始执行 M9 验收", "consequence": "进入实际执行"},
            {"label": "B. 还需要补充或修改某些细节，继续讨论", "consequence": "停留在 plan mode"},
            {"label": "C. 保持 plan mode，只把计划写到文件里，暂不动手执行", "consequence": "计划与执行分离"}
        ],
        "selected_option": "A. 同意，退出 plan mode 并开始执行 M9 验收",
        "rationale": "细节已收敛，下一步就是实际跑命令验证。",
        "affected_files": [],
        "unresolved_tail": "",
        "timestamp": "2026-07-29T09:26:04.898Z",
        "related_commit": "dd93cc9"
    }
]


def main():
    repo_root = Path(__file__).resolve().parent.parent
    output_path = repo_root / "data/samples/cyber-game-m9/decision-points.jsonl"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        for decision in DECISIONS:
            f.write(json.dumps(decision, ensure_ascii=False) + "\n")
    print(f"Wrote {len(DECISIONS)} decision points to {output_path}")


if __name__ == "__main__":
    main()
