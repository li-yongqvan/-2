#!/usr/bin/env python3
"""
PROTOTYPE — Experience Unit Generator v0.2

Turns the v0.1 decision-point sample into a full v0.2 intermediate data structure:
- tag taxonomy
- session fragments (dialogue slices)
- git evidence (file-level, with optional hunk placeholders)
- decision-point v0.2 with back-references
- experience units
- course modules
- learning path

Run:
    python scripts/generate_experience_units_v0.2.py

Inputs (relative to repo root):
    - data/samples/cyber-game-m9/decision-points.jsonl
    - data/samples/cyber-game-m9/git-alignment.json
    - data/samples/cyber-game-m9/session-be0044d7-scrubbed.jsonl
    - data/samples/cyber-game-m9/subagent-abe9460ea165d5867-scrubbed.jsonl

Outputs (relative to repo root):
    - data/samples/cyber-game-m9/tags-v0.2.json
    - data/samples/cyber-game-m9/session-fragments-v0.2.jsonl
    - data/samples/cyber-game-m9/git-evidence-v0.2.jsonl
    - data/samples/cyber-game-m9/decision-points-v0.2.jsonl
    - data/samples/cyber-game-m9/experience-units-v0.2.jsonl
    - data/samples/cyber-game-m9/course-modules-v0.2.json
    - data/samples/cyber-game-m9/learning-paths-v0.2.json
    - data/samples/cyber-game-m9/experience-package-v0.2.json
    - data/samples/cyber-game-m9/.needs_review (heuristic alignment marker)
"""

import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_DIR = REPO_ROOT / "data" / "samples" / "cyber-game-m9"

DECISIONS_V01 = SAMPLE_DIR / "decision-points.jsonl"
GIT_ALIGNMENT = SAMPLE_DIR / "git-alignment.json"
SESSION_FILE = SAMPLE_DIR / "session-be0044d7-scrubbed.jsonl"
SUBAGENT_FILE = SAMPLE_DIR / "subagent-abe9460ea165d5867-scrubbed.jsonl"

OUTPUT_DIR = SAMPLE_DIR
CREATED_AT = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

# ---------------------------------------------------------------------------
# Tag taxonomy
# ---------------------------------------------------------------------------

CATEGORY_TO_METHOD_TAG = {
    "task_definition": "method.task_definition",
    "method_selection": "method.method_selection",
    "scope_tradeoff": "method.scope_tradeoff",
    "context_injection": "method.context_injection",
    "prompt_refinement": "method.prompt_refinement",
    "constraint_declaration": "method.constraint_declaration",
    "course_correction": "method.course_correction",
    "acceptance_termination": "method.acceptance_termination",
}

THEME_PATTERNS = [
    (r"^src/store/", "theme.state_management"),
    (r"^src/renderer/", "theme.rendering"),
    (r"^src/engine/", "theme.engine"),
    (r"^src/ui/", "theme.ui"),
    (r"^src/levels/", "theme.level_design"),
    (r"^tests/", "theme.testing"),
    (r"^vite\.config", "theme.build_tooling"),
    (r"^HANDOFF\.md$", "theme.planning"),
    (r"^README\.md$", "theme.documentation"),
]

TAG_TAXONOMY = {
    "version": "0.2.0",
    "axes": [
        {"id": "method", "label_en": "Decision Method", "label_zh": "决策方法"},
        {"id": "project_phase", "label_en": "Project Phase", "label_zh": "项目阶段"},
        {"id": "theme", "label_en": "Technical Theme", "label_zh": "技术主题"},
        {"id": "skill", "label_en": "Collaboration Skill", "label_zh": "协作技能"},
    ],
    "tags": [
        # method
        {"id": "method.task_definition", "axis_id": "method", "label_en": "Task Definition", "label_zh": "任务定义"},
        {"id": "method.method_selection", "axis_id": "method", "label_en": "Method Selection", "label_zh": "方法选择"},
        {"id": "method.scope_tradeoff", "axis_id": "method", "label_en": "Scope Tradeoff", "label_zh": "范围取舍"},
        {"id": "method.context_injection", "axis_id": "method", "label_en": "Context Injection", "label_zh": "上下文注入"},
        {"id": "method.prompt_refinement", "axis_id": "method", "label_en": "Prompt Refinement", "label_zh": "提示精炼"},
        {"id": "method.constraint_declaration", "axis_id": "method", "label_en": "Constraint Declaration", "label_zh": "约束声明"},
        {"id": "method.course_correction", "axis_id": "method", "label_en": "Course Correction", "label_zh": "方向修正"},
        {"id": "method.acceptance_termination", "axis_id": "method", "label_en": "Acceptance / Termination", "label_zh": "验收/终止"},
        # project_phase
        {"id": "phase.m9", "axis_id": "project_phase", "label_en": "Milestone 9", "label_zh": "M9 里程碑"},
        # theme
        {"id": "theme.state_management", "axis_id": "theme", "label_en": "State Management", "label_zh": "状态管理"},
        {"id": "theme.rendering", "axis_id": "theme", "label_en": "Rendering", "label_zh": "渲染"},
        {"id": "theme.engine", "axis_id": "theme", "label_en": "Simulation Engine", "label_zh": "仿真引擎"},
        {"id": "theme.ui", "axis_id": "theme", "label_en": "UI Components", "label_zh": "UI 组件"},
        {"id": "theme.level_design", "axis_id": "theme", "label_en": "Level Design", "label_zh": "关卡设计"},
        {"id": "theme.testing", "axis_id": "theme", "label_en": "Testing", "label_zh": "测试"},
        {"id": "theme.build_tooling", "axis_id": "theme", "label_en": "Build Tooling", "label_zh": "构建工具"},
        {"id": "theme.planning", "axis_id": "theme", "label_en": "Planning", "label_zh": "规划"},
        {"id": "theme.documentation", "axis_id": "theme", "label_en": "Documentation", "label_zh": "文档"},
        # skill
        {"id": "skill.grilling", "axis_id": "skill", "label_en": "Grill-me", "label_zh": "Grill-me 追问"},
        {"id": "skill.plan_mode", "axis_id": "skill", "label_en": "Plan Mode", "label_zh": "Plan Mode"},
    ],
}

TAG_IDS = {t["id"] for t in TAG_TAXONOMY["tags"]}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_jsonl(path: Path) -> list[dict]:
    records = []
    if not path.exists():
        return records
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def write_jsonl(path: Path, records: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def write_json(path: Path, data) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def message_text(message: dict) -> str:
    """Extract searchable text from a Claude Code message object."""
    if not isinstance(message, dict):
        return ""
    content = message.get("content", "")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict):
                if block.get("type") == "text":
                    parts.append(block.get("text", ""))
                elif "name" in block:
                    parts.append(block.get("name", ""))
                    inp = block.get("input", {})
                    if isinstance(inp, dict):
                        parts.append(json.dumps(inp, ensure_ascii=False))
        return "\n".join(parts)
    return ""


def decision_search_text(decision: dict) -> list[str]:
    """Return candidate substrings to search for in the session, longest first."""
    candidates = [
        decision.get("title", ""),
        decision.get("question", ""),
        decision.get("selected_option", ""),
    ]
    # Split title/question into sentences/phrases and take the longest meaningful ones
    fragments = []
    for text in candidates:
        if not text:
            continue
        # Chinese punctuation + period
        for sent in re.split(r"[。！？\n]", text):
            sent = sent.strip()
            if len(sent) >= 8:
                fragments.append(sent)
    fragments.sort(key=len, reverse=True)
    # Deduplicate while preserving order
    seen = set()
    result = []
    for frag in fragments:
        if frag not in seen:
            seen.add(frag)
            result.append(frag)
    return result


def find_anchor_uuid(messages: list[dict], decision: dict) -> tuple[str | None, str]:
    """Find the most relevant message UUID for a decision. Returns (uuid, quality)."""
    candidates = decision_search_text(decision)
    for frag in candidates:
        matches = []
        for msg in messages:
            if frag in message_text(msg.get("message", {})):
                matches.append(msg.get("uuid"))
        if len(matches) == 1:
            return matches[0], "manual"
    # Fallback: first user message among uuid-bearing records
    for msg in messages:
        if msg.get("type") == "user":
            return msg.get("uuid"), "heuristic"
    return None, "heuristic"


def build_tag_ids(decision: dict) -> list[str]:
    tags = [
        CATEGORY_TO_METHOD_TAG[decision["category_en"]],
        "phase.m9",
        "skill.grilling",
    ]
    seen_themes = set()
    for path in decision.get("affected_files", []):
        for pattern, tag_id in THEME_PATTERNS:
            if re.search(pattern, path) and tag_id not in seen_themes:
                seen_themes.add(tag_id)
                tags.append(tag_id)
    return tags


def slug_from_id(decision_id: str) -> str:
    """cyber-game-m9-001 -> cyber-game-m9"""
    return re.sub(r"-[0-9]+$", "", decision_id)


def make_fragment_id(decision_id: str) -> str:
    session_slug = "be0044d7"
    return f"frag-{session_slug}-{slug_from_id(decision_id).replace('-', '')}-{int(decision_id.split('-')[-1]):03d}"


def make_evidence_id(commit_sha: str, file_path: str) -> str:
    safe = re.sub(r"[^a-zA-Z0-9_.-]", "_", file_path).strip("_").lower()
    return f"git-{commit_sha}-{safe}"


def make_unit_id(decision_id: str) -> str:
    return f"unit-{slug_from_id(decision_id)}-{int(decision_id.split('-')[-1]):03d}"

# ---------------------------------------------------------------------------
# Main generation
# ---------------------------------------------------------------------------

def main() -> None:
    decisions_v01 = load_jsonl(DECISIONS_V01)
    decisions_v01_by_num = {int(d["id"].split("-")[-1]): d for d in decisions_v01}
    git_alignment = json.loads(GIT_ALIGNMENT.read_text(encoding="utf-8"))
    messages = load_jsonl(SESSION_FILE)
    subagent_messages = load_jsonl(SUBAGENT_FILE)
    all_messages = messages + subagent_messages
    # Keep only records that have a uuid (conversational/user/assistant/system records)
    uuid_messages = [m for m in all_messages if isinstance(m, dict) and m.get("uuid")]

    commit_sha = git_alignment["commit_range"]["to"]
    parent_commit_sha = git_alignment["commit_range"]["from"]
    changed_files = set(git_alignment.get("changed_files", []))

    session_id = git_alignment["session_id"]
    session_file_rel = str(SESSION_FILE.relative_to(REPO_ROOT)).replace("\\", "/")

    fragments = []
    git_evidences = []
    decisions_v02 = []
    units = []
    needs_review = []

    # Map to avoid duplicate git evidence ids
    evidence_by_id = {}

    for decision in decisions_v01:
        decision_id = decision["id"]
        unit_id = make_unit_id(decision_id)
        fragment_id = make_fragment_id(decision_id)

        # Tags
        tag_ids = build_tag_ids(decision)

        # Session fragment
        anchor_uuid, quality = find_anchor_uuid(all_messages, decision)
        if quality == "heuristic":
            needs_review.append({
                "decision_id": decision_id,
                "reason": "anchor_message_uuid was determined heuristically",
                "anchor_uuid": anchor_uuid,
            })

        if anchor_uuid:
            uuid_to_index = {msg.get("uuid"): i for i, msg in enumerate(uuid_messages)}
            anchor_index = uuid_to_index.get(anchor_uuid, 0)
            start_index = max(0, anchor_index - 2)
            end_index = min(len(uuid_messages) - 1, anchor_index + 3)
            window = uuid_messages[start_index:end_index + 1]
            message_uuids = [m.get("uuid") for m in window]
            start_uuid = window[0].get("uuid")
            end_uuid = window[-1].get("uuid")
        else:
            message_uuids = []
            start_uuid = end_uuid = anchor_uuid

        participants = set()
        for msg in window if anchor_uuid else []:
            role = msg.get("message", {}).get("role")
            if role in ("user", "assistant", "system"):
                participants.add(role)
            msg_type = msg.get("type")
            if msg_type == "user":
                participants.add("user")
            elif msg_type == "assistant":
                participants.add("assistant")
            elif msg_type == "system":
                participants.add("system")

        fragment = {
            "fragment_id": fragment_id,
            "session_id": session_id,
            "source_session_file": session_file_rel,
            "anchor_message_uuid": anchor_uuid,
            "start_message_uuid": start_uuid,
            "end_message_uuid": end_uuid,
            "message_uuids": message_uuids,
            "summary": f"Session fragment for decision {decision_id}: {decision['title']}",
            "participants": sorted(participants),
            "includes_subagent": any(m.get("agentId") for m in (window if anchor_uuid else [])),
            "alignment_quality": quality,
        }
        fragments.append(fragment)

        # Git evidence
        evidence_ids = []
        for file_path in decision.get("affected_files", []):
            evidence_id = make_evidence_id(commit_sha, file_path)
            if evidence_id not in evidence_by_id:
                in_changed = file_path in changed_files
                evidence = {
                    "evidence_id": evidence_id,
                    "commit_sha": commit_sha,
                    "parent_commit_sha": parent_commit_sha,
                    "kind": "file",
                    "file_path": file_path,
                    "diff_command": f"git diff {parent_commit_sha}..{commit_sha} -- {file_path}",
                    "code_ref": f"<code-ref: {file_path} @ {commit_sha}>",
                    "notes": "" if in_changed else "Mentioned in decision but not present in git-alignment changed_files; likely discussed or anticipated rather than modified in this commit.",
                }
                if not in_changed:
                    needs_review.append({
                        "decision_id": decision_id,
                        "reason": f"affected_file '{file_path}' not found in git-alignment changed_files",
                    })
                evidence_by_id[evidence_id] = evidence
                git_evidences.append(evidence)
            evidence_ids.append(evidence_id)

        # Decision v0.2
        decision_v02 = dict(decision)
        decision_v02.update({
            "experience_unit_id": unit_id,
            "session_fragment_ids": [fragment_id],
            "git_evidence_ids": evidence_ids,
            "tag_ids": tag_ids,
            "related_message_uuids": [anchor_uuid] if anchor_uuid else [],
            "alignment_quality": quality,
        })
        decisions_v02.append(decision_v02)

        # Experience unit
        method_tag = CATEGORY_TO_METHOD_TAG[decision["category_en"]]
        entry_points = [
            {"type": "method", "label": decision["category"], "tag_id": method_tag},
            {"type": "timeline", "label": "M9 里程碑", "tag_id": "phase.m9"},
        ]
        # Add theme entry if available
        theme_tags = [t for t in tag_ids if t.startswith("theme.")]
        if theme_tags:
            entry_points.append({"type": "theme", "label": "技术主题", "tag_id": theme_tags[0]})

        unit = {
            "unit_id": unit_id,
            "decision_id": decision_id,
            "session_fragment_ids": [fragment_id],
            "git_evidence_ids": evidence_ids,
            "tag_ids": tag_ids,
            "course_module_ids": [],
            "learning_path_ids": [],
            "entry_points": entry_points,
            "related_unit_ids": [],
            "review_status": "draft",
            "reviewer_notes": "Auto-generated from v0.1 decision point. Review fragment anchors and tag assignments.",
            "created_at": CREATED_AT,
            "updated_at": CREATED_AT,
        }
        units.append(unit)

    # -----------------------------------------------------------------------
    # Course modules
    # -----------------------------------------------------------------------
    module_assignments = {
        "mod-scope-and-state": [1, 3, 4, 8, 9, 12],
        "mod-sandbox-and-rendering": [2, 5, 6, 7, 13, 14, 15, 16],
        "mod-grilling-workflow": [10, 11, 17, 18, 19, 20],
    }

    module_meta = {
        "mod-scope-and-state": {
            "title": "范围取舍与状态管理",
            "description": "M8-M9 拆分、沙盒范围、状态持久化等关键范围与状态决策。",
            "entry_type": "mixed",
            "learning_objectives": [
                "识别里程碑边界处的范围风险",
                "在拆分与合并之间做出可验收的决策",
                "将运行时状态与持久化状态分离"
            ],
        },
        "mod-sandbox-and-rendering": {
            "title": "沙盒与渲染交互",
            "description": "教学版沙盒、拖拽、实时链路、设备面板等交互与引擎决策。",
            "entry_type": "method",
            "learning_objectives": [
                "在教学版沙盒中平衡功能与成本",
                "设计渲染层与引擎层的状态边界",
                "用占位策略避免阻塞里程碑"
            ],
        },
        "mod-grilling-workflow": {
            "title": "Grill-me 工作流与验收",
            "description": "用 grill-me 把模糊任务收敛为可执行计划，并在适当时机退出 plan mode。",
            "entry_type": "method",
            "learning_objectives": [
                "用结构化追问澄清任务歧义",
                "确定验收深度与输出位置",
                "判断何时从计划转向执行"
            ],
        },
    }

    unit_by_num = {int(u["unit_id"].split("-")[-1]): u for u in units}
    unit_to_decision = {u["unit_id"]: decisions_v01_by_num[int(u["unit_id"].split("-")[-1])] for u in units}
    course_modules = []
    for module_id, nums in module_assignments.items():
        meta = module_meta[module_id]
        seq = []
        for n in nums:
            unit = unit_by_num[n]
            decision = unit_to_decision[unit["unit_id"]]
            unit["course_module_ids"].append(module_id)
            rationale = f"{decision['category']}：{decision['title']}"
            seq.append({"unit_id": unit["unit_id"], "rationale": rationale})
        course_modules.append({
            "module_id": module_id,
            **meta,
            "prerequisites": [],
            "unit_sequence": seq,
            "estimated_duration_minutes": 15 + len(seq) * 3,
        })

    # -----------------------------------------------------------------------
    # Learning path
    # -----------------------------------------------------------------------
    learning_path = {
        "path_id": "path-grilling-milestone",
        "title": "Grill-me 驱动的里程碑范围切片",
        "description": "跟随 cyber-game M8-M9 完整决策链，学习如何用 grill-me 把模糊里程碑拆分为可验收任务。",
        "entry_points": [
            {"type": "module", "label": "从范围与状态管理开始", "value": "mod-scope-and-state"},
            {"type": "module", "label": "从 Grill-me 工作流开始", "value": "mod-grilling-workflow"},
            {"type": "tag", "label": "按方法主题浏览", "value": "method.scope_tradeoff"},
        ],
        "modules": [
            {"module_id": "mod-grilling-workflow", "rationale": "先澄清任务与验收标准"},
            {"module_id": "mod-scope-and-state", "rationale": "再做范围与状态拆分"},
            {"module_id": "mod-sandbox-and-rendering", "rationale": "最后落实到交互实现"},
        ],
        "estimated_duration_minutes": sum(m.get("estimated_duration_minutes", 0) for m in course_modules),
    }
    for unit in units:
        unit["learning_path_ids"].append(learning_path["path_id"])

    # -----------------------------------------------------------------------
    # Write outputs
    # -----------------------------------------------------------------------
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    write_json(OUTPUT_DIR / "tags-v0.2.json", TAG_TAXONOMY)
    write_jsonl(OUTPUT_DIR / "session-fragments-v0.2.jsonl", fragments)
    write_jsonl(OUTPUT_DIR / "git-evidence-v0.2.jsonl", git_evidences)
    write_jsonl(OUTPUT_DIR / "decision-points-v0.2.jsonl", decisions_v02)
    write_jsonl(OUTPUT_DIR / "experience-units-v0.2.jsonl", units)
    write_json(OUTPUT_DIR / "course-modules-v0.2.json", course_modules)
    write_json(OUTPUT_DIR / "learning-paths-v0.2.json", [learning_path])

    package_manifest = {
        "version": "0.2.0",
        "package_id": "experience-cyber-game-m9-grilling-scope-slice",
        "title": "Grill-me 驱动的里程碑范围切片",
        "source_project": "cyber-game",
        "files": {
            "tags": "tags-v0.2.json",
            "session_fragments": "session-fragments-v0.2.jsonl",
            "git_evidence": "git-evidence-v0.2.jsonl",
            "decision_points": "decision-points-v0.2.jsonl",
            "experience_units": "experience-units-v0.2.jsonl",
            "course_modules": "course-modules-v0.2.json",
            "learning_paths": "learning-paths-v0.2.json",
        },
        "schema_base": "research/session-format/schemas",
        "notes": "v0.2 prototype. Session fragment anchors are heuristic until manually reviewed.",
    }
    write_json(OUTPUT_DIR / "experience-package-v0.2.json", package_manifest)

    if needs_review:
        review_path = OUTPUT_DIR / ".needs_review"
        with review_path.open("w", encoding="utf-8") as f:
            json.dump({"count": len(needs_review), "items": needs_review}, f, ensure_ascii=False, indent=2)
            f.write("\n")

    print(f"Generated {len(decisions_v02)} decisions, {len(fragments)} fragments, {len(git_evidences)} git evidences, {len(course_modules)} modules, 1 learning path.")
    if needs_review:
        print(f"Wrote {len(needs_review)} review item(s) to {OUTPUT_DIR / '.needs_review'}")


if __name__ == "__main__":
    main()
