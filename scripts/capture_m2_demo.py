#!/usr/bin/env python3
"""
M2 end-to-end demo for the capture mechanism.

Generates a minimal sample dataset from capture markers + a scrubbed session,
producing decision points and experience units. This proves the loop:

    marker → extract → review → ExperienceUnit

Run:
    python scripts/capture_m2_demo.py

Outputs go to data/samples/capture-mechanism-demo/.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

REPO_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_DIR = REPO_ROOT / "data" / "samples" / "capture-mechanism-demo"
SCHEMA_DIR = REPO_ROOT / "research" / "session-format" / "schemas"

SESSION_ID = "aabbccdd-1234-5678-9abc-def012345678"
PROJECT_ROOT = REPO_ROOT

METHOD_TO_CATEGORY = {
    "task_definition": ("任务定义", "task_definition"),
    "method_selection": ("方法选择", "method_selection"),
    "scope_tradeoff": ("范围取舍", "scope_tradeoff"),
    "context_injection": ("上下文注入", "context_injection"),
    "prompt_refinement": ("提示精炼", "prompt_refinement"),
    "constraint_declaration": ("约束声明", "constraint_declaration"),
    "course_correction": ("方向修正", "course_correction"),
    "acceptance_termination": ("验收/终止", "acceptance_termination"),
}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if not path.exists():
        return records
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def load_schema(name: str):
    if not HAS_JSONSCHEMA:
        return None
    path = SCHEMA_DIR / name
    return jsonschema.Draft7Validator(json.loads(path.read_text(encoding="utf-8")))


def validate_all(outputs: dict[str, Any], validators: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key, data in outputs.items():
        validator = validators.get(key)
        if not validator:
            continue
        if isinstance(data, list):
            for i, item in enumerate(data):
                for err in validator.iter_errors(item):
                    path = "/".join(str(p) for p in err.absolute_path) or "<root>"
                    errors.append(f"{key}[{i}].{path}: {err.message}")
        else:
            for err in validator.iter_errors(data):
                path = "/".join(str(p) for p in err.absolute_path) or "<root>"
                errors.append(f"{key}.{path}: {err.message}")
    return errors


def generate_demo_session() -> None:
    """Write a synthetic scrubbed session with #insight markers."""
    session_file = SAMPLE_DIR / "session-demo-scrubbed.jsonl"
    session_file.parent.mkdir(parents=True, exist_ok=True)
    records = [
        {"type": "mode", "mode": "normal", "sessionId": SESSION_ID},
        {
            "parentUuid": None,
            "type": "user",
            "message": {
                "role": "user",
                "content": "我们在设计 capture mechanism。\n#insight[method=scope_tradeoff,theme=architecture]: 把 #insight 作为快速便签，/capture 作为 assistant 消息的 richer metadata 入口。",
            },
            "uuid": "11111111-1111-1111-1111-111111111111",
            "timestamp": "2026-08-17T10:00:00.000Z",
            "sessionId": SESSION_ID,
        },
        {
            "parentUuid": "11111111-1111-1111-1111-111111111111",
            "type": "assistant",
            "message": {
                "role": "assistant",
                "content": [{"type": "text", "text": "同意。这样既能低摩擦捕获，又能精确锚定 assistant 回复。"}],
            },
            "uuid": "22222222-2222-2222-2222-222222222222",
            "timestamp": "2026-08-17T10:00:05.000Z",
            "sessionId": SESSION_ID,
        },
        {
            "parentUuid": "22222222-2222-2222-2222-222222222222",
            "type": "user",
            "message": {
                "role": "user",
                "content": "还有，锚定失败时用 timestamp 最近邻回退，不要阻塞当前任务。\n#insight[method=constraint_declaration,theme=testing]: 锚定精度采用 confidence 分级，capture 阶段可空、review 阶段必须解决。",
            },
            "uuid": "33333333-3333-3333-3333-333333333333",
            "timestamp": "2026-08-17T10:01:00.000Z",
            "sessionId": SESSION_ID,
        },
    ]
    with session_file.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def generate_demo_sidecar() -> None:
    """Write a synthetic /capture skill sidecar."""
    sidecar_file = SAMPLE_DIR / "capture-sidecar.jsonl"
    markers = [
        {
            "marker_id": "cm-p2-aabbccdd-001",
            "marker_type": "capture",
            "session_id": SESSION_ID,
            "anchor_message_uuid": "",
            "timestamp": "2026-08-17T10:00:06.000Z",
            "summary": "Assistant agreed on splitting #insight and /capture responsibilities.",
            "method_tag": "scope_tradeoff",
            "theme_tag": "architecture",
            "source": "skill",
            "notes": "[anchor_target=previous_assistant]",
        }
    ]
    write_jsonl(sidecar_file, markers)


def run_extractor() -> None:
    session_file = SAMPLE_DIR / "session-demo-scrubbed.jsonl"
    sidecar_file = SAMPLE_DIR / "capture-sidecar.jsonl"
    output_file = SAMPLE_DIR / "capture-markers-v0.2.jsonl"
    cmd = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "extract_capture_markers.py"),
        "--session",
        str(session_file),
        "--sidecar",
        str(sidecar_file),
        "--output",
        str(output_file),
        "--project-root",
        str(PROJECT_ROOT),
    ]
    subprocess.run(cmd, check=True)


def build_tag_taxonomy(markers: list[dict[str, Any]]) -> dict[str, Any]:
    tags: list[dict[str, Any]] = [
        {"id": "phase.demo", "axis_id": "project_phase", "label_en": "Demo Phase", "label_zh": "演示阶段"},
        {"id": "skill.capture", "axis_id": "skill", "label_en": "Capture", "label_zh": "捕获机制"},
    ]
    seen_methods: set[str] = set()
    seen_themes: set[str] = set()
    for marker in markers:
        method = marker.get("method_tag")
        if method and method not in seen_methods:
            seen_methods.add(method)
            category_zh, category_en = METHOD_TO_CATEGORY.get(method, (method, method))
            tags.append(
                {
                    "id": f"method.{method}",
                    "axis_id": "method",
                    "label_en": category_en.replace("_", " ").title(),
                    "label_zh": category_zh,
                }
            )
        theme = marker.get("theme_tag") or "general"
        if theme not in seen_themes:
            seen_themes.add(theme)
            tags.append(
                {
                    "id": f"theme.{theme}",
                    "axis_id": "theme",
                    "label_en": theme.replace("_", " ").title(),
                    "label_zh": theme.replace("_", " ").title(),
                }
            )
    return {
        "version": "0.2.0",
        "axes": [
            {"id": "method", "label_en": "Decision Method", "label_zh": "决策方法"},
            {"id": "project_phase", "label_en": "Project Phase", "label_zh": "项目阶段"},
            {"id": "theme", "label_en": "Technical Theme", "label_zh": "技术主题"},
            {"id": "skill", "label_en": "Collaboration Skill", "label_zh": "协作技能"},
        ],
        "tags": tags,
    }


def find_message_index(messages: list[dict[str, Any]], uuid: str) -> int:
    for i, msg in enumerate(messages):
        if msg.get("uuid") == uuid:
            return i
    return -1


def make_fragment(marker: dict[str, Any], messages: list[dict[str, Any]], seq: int) -> dict[str, Any] | None:
    anchor_uuid = marker.get("anchor_message_uuid")
    if not anchor_uuid:
        return None
    idx = find_message_index(messages, anchor_uuid)
    if idx < 0:
        return None
    window = messages[max(0, idx - 1) : min(len(messages), idx + 2)]
    uuids = [m.get("uuid") for m in window]
    participants: set[str] = set()
    for m in window:
        role = (m.get("message") or {}).get("role") or m.get("type")
        if role in ("user", "assistant", "system"):
            participants.add(role)
    quality_map = {"exact": "manual", "nearest": "heuristic", "unresolved": "inferred"}
    return {
        "fragment_id": f"frag-capture-demo-{seq:03d}",
        "session_id": marker["session_id"],
        "source_session_file": "session-demo-scrubbed.jsonl",
        "anchor_message_uuid": anchor_uuid,
        "start_message_uuid": window[0].get("uuid"),
        "end_message_uuid": window[-1].get("uuid"),
        "message_uuids": uuids,
        "summary": f"Fragment for marker {marker['marker_id']}: {marker['summary']}",
        "participants": sorted(participants) or ["user"],
        "includes_subagent": any(m.get("agentId") for m in window),
        "alignment_quality": quality_map.get(marker.get("anchor_confidence", "heuristic"), "heuristic"),
    }


def make_decision_point(marker: dict[str, Any], seq: int) -> dict[str, Any]:
    method = marker.get("method_tag") or "scope_tradeoff"
    category_zh, category_en = METHOD_TO_CATEGORY.get(method, (method, method))
    quality_map = {"exact": "manual", "nearest": "heuristic", "unresolved": "inferred"}
    return {
        "id": f"capture-demo-{seq:03d}",
        "title": marker["summary"],
        "category": category_zh,
        "category_en": category_en,
        "source": f"capture marker {marker['marker_id']} → review",
        "source_type": "grilling",
        "question": f"如何处理这条 capture 洞察：{marker['summary']}?",
        "options": [
            {"label": "采纳为经验单元", "consequence": "生成 ExperienceUnit 并进入审核"},
            {"label": "暂不采纳", "consequence": "marker 保留为候选，不生成单元"},
        ],
        "selected_option": "采纳为经验单元",
        "rationale": "Marker 锚定清晰、方法维度明确，适合作为演示单元。",
        "affected_files": ["scripts/extract_capture_markers.py", ".claude/skills/capture/SKILL.md"],
        "unresolved_tail": "",
        "timestamp": marker["timestamp"],
        "related_commit": "0000000",
        "session_fragment_ids": [f"frag-capture-demo-{seq:03d}"],
        "tag_ids": [f"method.{method}", "phase.demo", f"theme.{marker.get('theme_tag') or 'general'}", "skill.capture"],
        "related_message_uuids": [marker["anchor_message_uuid"]] if marker.get("anchor_message_uuid") else [],
        "alignment_quality": quality_map.get(marker.get("anchor_confidence", "heuristic"), "heuristic"),
    }


def make_experience_unit(marker: dict[str, Any], decision: dict[str, Any], seq: int) -> dict[str, Any]:
    method = marker.get("method_tag") or "scope_tradeoff"
    theme = marker.get("theme_tag") or "general"
    return {
        "unit_id": f"unit-capture-demo-{seq:03d}",
        "decision_id": decision["id"],
        "session_fragment_ids": decision["session_fragment_ids"],
        "git_evidence_ids": [],
        "tag_ids": decision["tag_ids"],
        "candidate_markers": [marker["marker_id"]],
        "course_module_ids": [],
        "learning_path_ids": [],
        "entry_points": [
            {"type": "method", "label": decision["category"], "tag_id": f"method.{method}"},
            {"type": "timeline", "label": "演示阶段", "tag_id": "phase.demo"},
            {"type": "theme", "label": theme.replace("_", " ").title(), "tag_id": f"theme.{theme}"},
        ],
        "related_unit_ids": [],
        "review_status": "approved",
        "reviewer_notes": "Auto-approved in M2 end-to-end demo.",
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }


def main() -> int:
    print("Generating M2 demo inputs...")
    generate_demo_session()
    generate_demo_sidecar()

    print("Running extract_capture_markers.py...")
    run_extractor()

    markers = load_jsonl(SAMPLE_DIR / "capture-markers-v0.2.jsonl")
    messages = [m for m in load_jsonl(SAMPLE_DIR / "session-demo-scrubbed.jsonl") if m.get("uuid")]

    print(f"Loaded {len(markers)} markers, {len(messages)} session messages.")

    # Build outputs
    tags = build_tag_taxonomy(markers)
    fragments: list[dict[str, Any]] = []
    decisions: list[dict[str, Any]] = []
    units: list[dict[str, Any]] = []

    for seq, marker in enumerate(markers, start=1):
        fragment = make_fragment(marker, messages, seq)
        if fragment is None:
            print(f"warning: could not build fragment for {marker['marker_id']} (missing anchor)", file=sys.stderr)
            continue
        decision = make_decision_point(marker, seq)
        unit = make_experience_unit(marker, decision, seq)
        fragments.append(fragment)
        decisions.append(decision)
        units.append(unit)

    write_json(SAMPLE_DIR / "tags-v0.2.json", tags)
    write_jsonl(SAMPLE_DIR / "session-fragments-v0.2.jsonl", fragments)
    write_jsonl(SAMPLE_DIR / "decision-points-v0.2.jsonl", decisions)
    write_jsonl(SAMPLE_DIR / "experience-units-v0.2.jsonl", units)

    package_manifest = {
        "version": "0.2.0",
        "package_id": "experience-capture-mechanism-demo",
        "title": "Capture Mechanism M2 End-to-End Demo",
        "source_project": "-2",
        "files": {
            "tags": "tags-v0.2.json",
            "session_fragments": "session-fragments-v0.2.jsonl",
            "decision_points": "decision-points-v0.2.jsonl",
            "experience_units": "experience-units-v0.2.jsonl",
            "capture_markers": "capture-markers-v0.2.jsonl",
        },
        "schema_base": "research/session-format/schemas",
        "notes": "M2 demo generated from synthetic capture markers.",
    }
    write_json(SAMPLE_DIR / "experience-package-v0.2.json", package_manifest)

    # Validation
    validators = {
        "capture_marker": load_schema("capture-marker-v0.2.schema.json"),
        "session_fragment": load_schema("session-fragment-v0.2.schema.json"),
        "decision_point": load_schema("decision-point-v0.2.schema.json"),
        "experience_unit": load_schema("experience-unit-v0.2.schema.json"),
    }
    outputs = {
        "capture_marker": markers,
        "session_fragment": fragments,
        "decision_point": decisions,
        "experience_unit": units,
    }
    errors = validate_all(outputs, validators)

    print(f"\nGenerated {len(fragments)} fragments, {len(decisions)} decisions, {len(units)} units.")
    if errors:
        print("\nValidation errors:")
        for e in errors:
            print(f"- {e}")
        return 1

    print("\nAll generated artifacts passed schema validation.")
    print(f"Demo directory: {SAMPLE_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
