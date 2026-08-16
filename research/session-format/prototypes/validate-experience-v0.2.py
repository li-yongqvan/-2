#!/usr/bin/env python3
"""
PROTOTYPE — Experience Package v0.2 Validator

Validates the full v0.2 intermediate data structure for issue #2:
- schema compliance
- id uniqueness
- cross-reference consistency
- session UUID reality
- git alignment
- dual-entry coverage
- privacy scan
- capture markers (optional)

Run:
    python research/session-format/prototypes/validate-experience-v0.2.py

Outputs a Markdown report to stdout.
"""

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

REPO_ROOT = Path(__file__).resolve().parents[3]
SAMPLE_DIR = REPO_ROOT / "data" / "samples" / "cyber-game-m9"
SCHEMA_DIR = REPO_ROOT / "research" / "session-format" / "schemas"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict]:
    records = []
    if not path.exists():
        return records
    with path.open("r", encoding="utf-8") as f:
        for line_no, raw in enumerate(f, start=1):
            raw = raw.strip()
            if not raw:
                continue
            try:
                records.append((line_no, json.loads(raw)))
            except json.JSONDecodeError as exc:
                records.append((line_no, {"__json_error__": str(exc)}))
    return records


def load_schema(name: str):
    path = SCHEMA_DIR / name
    if HAS_JSONSCHEMA:
        return jsonschema.Draft7Validator(load_json(path))
    return None


def validate_with_schema(validator, record: dict) -> list[str]:
    if not validator:
        return []
    return [f"{'/'.join(str(p) for p in err.absolute_path) or '<root>'}: {err.message}"
            for err in validator.iter_errors(record)]


def privacy_scan(text: str, manifest: dict) -> list[str]:
    hits = []
    for old, new in manifest.get("string_replacements", {}).items():
        if old in text and old != new:
            hits.append(f"string_replacement target '{old}'")
    for label, pattern in manifest.get("extra_secret_patterns", []):
        for match in re.finditer(pattern, text):
            hits.append(f"secret pattern '{label}' matched: {match.group(0)[:40]}")
    return hits


def main() -> None:
    parser = argparse.ArgumentParser(description="Experience Package v0.2 Validator")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat soft warnings as errors (used for v1.0 or strict checks).",
    )
    args = parser.parse_args()

    print("# Experience Package v0.2 Validation Report\n")
    if args.strict:
        print("> **Strict mode enabled**: soft warnings are treated as errors.\n")
    print(f"- Sample directory: `{SAMPLE_DIR.relative_to(REPO_ROOT)}`")
    print(f"- jsonschema available: {'yes' if HAS_JSONSCHEMA else 'no (structural checks only)'}\n")

    errors: list[str] = []
    warnings: list[str] = []
    soft_warnings: list[str] = []

    # Load schemas
    schema_validators = {
        "tag": load_schema("tag-v0.2.schema.json"),
        "session_fragment": load_schema("session-fragment-v0.2.schema.json"),
        "git_evidence": load_schema("git-evidence-v0.2.schema.json"),
        "git_hunk_evidence": load_schema("git-hunk-evidence-v0.2.schema.json"),
        "decision_point": load_schema("decision-point-v0.2.schema.json"),
        "experience_unit": load_schema("experience-unit-v0.2.schema.json"),
        "course_module": load_schema("course-module-v0.2.schema.json"),
        "learning_path": load_schema("learning-path-v0.2.schema.json"),
        "capture_marker": load_schema("capture-marker-v0.2.schema.json"),
    }

    # Load data
    tags_data = load_json(SAMPLE_DIR / "tags-v0.2.json")
    session_fragments = load_jsonl(SAMPLE_DIR / "session-fragments-v0.2.jsonl")
    git_evidences = load_jsonl(SAMPLE_DIR / "git-evidence-v0.2.jsonl")
    git_hunk_evidences = load_jsonl(SAMPLE_DIR / "git-hunk-evidence-v0.2.jsonl")
    decision_points = load_jsonl(SAMPLE_DIR / "decision-points-v0.2.jsonl")
    experience_units = load_jsonl(SAMPLE_DIR / "experience-units-v0.2.jsonl")
    course_modules = load_json(SAMPLE_DIR / "course-modules-v0.2.json")
    learning_paths = load_json(SAMPLE_DIR / "learning-paths-v0.2.json")
    capture_markers = load_jsonl(SAMPLE_DIR / "capture-markers-v0.2.jsonl")

    git_alignment = load_json(SAMPLE_DIR / "git-alignment.json")
    scrubbing_manifest = load_json(SAMPLE_DIR / "scrubbing-manifest.json")
    session_messages = load_jsonl(SAMPLE_DIR / "session-be0044d7-scrubbed.jsonl")
    subagent_messages = load_jsonl(SAMPLE_DIR / "subagent-abe9460ea165d5867-scrubbed.jsonl")
    grilling_messages = load_jsonl(SAMPLE_DIR / "session-4241638d-grilling-scrubbed.jsonl")

    all_session_uuids = {m.get("uuid") for _, m in session_messages + subagent_messages + grilling_messages if m.get("uuid")}
    changed_files = set(git_alignment.get("changed_files", []))
    key_files = set(git_alignment.get("key_files_for_m8_m9", []))
    allowed_git_files = changed_files | key_files

    tag_axis_by_id = {t["id"]: t["axis_id"] for t in tags_data["tags"]}

    def check_unique(items: list[tuple[int, dict]], id_field: str, label: str) -> dict:
        seen = {}
        duplicates = []
        for line_no, item in items:
            if "__json_error__" in item:
                errors.append(f"{label} line {line_no}: invalid JSON - {item['__json_error__']}")
                continue
            item_id = item.get(id_field)
            if item_id in seen:
                duplicates.append((item_id, seen[item_id], line_no))
            else:
                seen[item_id] = line_no
        for item_id, first, second in duplicates:
            errors.append(f"{label}: duplicate {id_field} '{item_id}' at lines {first} and {second}")
        return seen

    # Schema + uniqueness checks
    print("## 1. Schema & Uniqueness\n")

    tag_errors = validate_with_schema(schema_validators["tag"], tags_data)
    if tag_errors:
        errors.append(f"tags-v0.2.json schema errors: {tag_errors}")

    fragment_ids = check_unique(session_fragments, "fragment_id", "session-fragments-v0.2.jsonl")
    for line_no, frag in session_fragments:
        if "__json_error__" in frag:
            continue
        errs = validate_with_schema(schema_validators["session_fragment"], frag)
        for e in errs:
            errors.append(f"session-fragments line {line_no}: {e}")

    evidence_ids = check_unique(git_evidences, "evidence_id", "git-evidence-v0.2.jsonl")
    for line_no, ev in git_evidences:
        if "__json_error__" in ev:
            continue
        errs = validate_with_schema(schema_validators["git_evidence"], ev)
        for e in errs:
            errors.append(f"git-evidence line {line_no}: {e}")

    hunk_evidence_ids = check_unique(git_hunk_evidences, "evidence_id", "git-hunk-evidence-v0.2.jsonl")
    for line_no, ev in git_hunk_evidences:
        if "__json_error__" in ev:
            continue
        errs = validate_with_schema(schema_validators["git_hunk_evidence"], ev)
        for e in errs:
            errors.append(f"git-hunk-evidence line {line_no}: {e}")

    decision_ids = check_unique(decision_points, "id", "decision-points-v0.2.jsonl")
    for line_no, dp in decision_points:
        if "__json_error__" in dp:
            continue
        errs = validate_with_schema(schema_validators["decision_point"], dp)
        for e in errs:
            errors.append(f"decision-points line {line_no}: {e}")

    unit_ids = check_unique(experience_units, "unit_id", "experience-units-v0.2.jsonl")
    for line_no, unit in experience_units:
        if "__json_error__" in unit:
            continue
        errs = validate_with_schema(schema_validators["experience_unit"], unit)
        for e in errs:
            errors.append(f"experience-units line {line_no}: {e}")

    module_ids = {m["module_id"]: True for m in course_modules}
    for i, mod in enumerate(course_modules, start=1):
        errs = validate_with_schema(schema_validators["course_module"], mod)
        for e in errs:
            errors.append(f"course-modules item {i}: {e}")

    path_ids = {p["path_id"]: True for p in learning_paths}
    for i, path in enumerate(learning_paths, start=1):
        errs = validate_with_schema(schema_validators["learning_path"], path)
        for e in errs:
            errors.append(f"learning-paths item {i}: {e}")

    marker_ids = check_unique(capture_markers, "marker_id", "capture-markers-v0.2.jsonl")
    for line_no, marker in capture_markers:
        if "__json_error__" in marker:
            continue
        errs = validate_with_schema(schema_validators["capture_marker"], marker)
        for e in errs:
            errors.append(f"capture-markers line {line_no}: {e}")

    print(f"- Decision points: {len(decision_ids)}")
    print(f"- Experience units: {len(unit_ids)}")
    print(f"- Session fragments: {len(fragment_ids)}")
    print(f"- Git evidences: {len(evidence_ids)}")
    print(f"- Git hunk evidences: {len(hunk_evidence_ids)}")
    print(f"- Course modules: {len(module_ids)}")
    print(f"- Learning paths: {len(path_ids)}")
    print(f"- Capture markers: {len(marker_ids)}")
    print()

    # Cross-reference checks
    print("## 2. Cross-Reference Consistency\n")

    for line_no, unit in experience_units:
        if "__json_error__" in unit:
            continue
        if unit.get("decision_id") not in decision_ids:
            errors.append(f"experience-units line {line_no}: decision_id '{unit.get('decision_id')}' not found")
        for fid in unit.get("session_fragment_ids", []):
            if fid not in fragment_ids:
                errors.append(f"experience-units line {line_no}: session_fragment_id '{fid}' not found")
        for eid in unit.get("git_evidence_ids", []):
            if eid not in evidence_ids:
                errors.append(f"experience-units line {line_no}: git_evidence_id '{eid}' not found")
        for hid in unit.get("git_hunk_evidence_ids", []):
            if hid not in hunk_evidence_ids:
                errors.append(f"experience-units line {line_no}: git_hunk_evidence_id '{hid}' not found")
        for tid in unit.get("tag_ids", []):
            if tid not in tag_axis_by_id:
                errors.append(f"experience-units line {line_no}: tag_id '{tid}' not in taxonomy")
        for mid in unit.get("course_module_ids", []):
            if mid not in module_ids:
                errors.append(f"experience-units line {line_no}: course_module_id '{mid}' not found")
        for pid in unit.get("learning_path_ids", []):
            if pid not in path_ids:
                errors.append(f"experience-units line {line_no}: learning_path_id '{pid}' not found")
        for cmid in unit.get("candidate_markers", []):
            if cmid not in marker_ids:
                soft_warnings.append(f"experience-units line {line_no}: candidate_marker '{cmid}' not found")

    for line_no, dp in decision_points:
        if "__json_error__" in dp:
            continue
        euid = dp.get("experience_unit_id")
        if euid and euid not in unit_ids:
            errors.append(f"decision-points line {line_no}: experience_unit_id '{euid}' not found")
        for fid in dp.get("session_fragment_ids", []):
            if fid not in fragment_ids:
                errors.append(f"decision-points line {line_no}: session_fragment_id '{fid}' not found")
        for eid in dp.get("git_evidence_ids", []):
            if eid not in evidence_ids:
                errors.append(f"decision-points line {line_no}: git_evidence_id '{eid}' not found")
        for hid in dp.get("git_hunk_evidence_ids", []):
            if hid not in hunk_evidence_ids:
                errors.append(f"decision-points line {line_no}: git_hunk_evidence_id '{hid}' not found")
        for tid in dp.get("tag_ids", []):
            if tid not in tag_axis_by_id:
                errors.append(f"decision-points line {line_no}: tag_id '{tid}' not in taxonomy")

    for i, mod in enumerate(course_modules, start=1):
        for seq in mod.get("unit_sequence", []):
            uid = seq.get("unit_id")
            if uid not in unit_ids:
                errors.append(f"course-modules item {i}: unit_id '{uid}' not found")

    for i, path in enumerate(learning_paths, start=1):
        for seq in path.get("modules", []):
            mid = seq.get("module_id")
            if mid not in module_ids:
                errors.append(f"learning-paths item {i}: module_id '{mid}' not found")

    print("- Checked unit → decision/fragment/evidence/hunk_evidence/tag/module/path links")
    print("- Checked unit → candidate_markers links")
    print("- Checked decision → unit/fragment/evidence/hunk_evidence/tag links")
    print("- Checked module/path → unit/module links\n")

    # Session UUID reality
    print("## 3. Session UUID Reality\n")

    missing_uuids = 0
    for line_no, frag in session_fragments:
        if "__json_error__" in frag:
            continue
        for uuid in frag.get("message_uuids", []):
            if uuid not in all_session_uuids:
                missing_uuids += 1
                errors.append(f"session-fragments line {line_no}: uuid '{uuid}' not found in session files")

    for line_no, marker in capture_markers:
        if "__json_error__" in marker:
            continue
        anchor_uuid = marker.get("anchor_message_uuid")
        if anchor_uuid and anchor_uuid not in all_session_uuids:
            soft_warnings.append(f"capture-markers line {line_no}: anchor_message_uuid '{anchor_uuid}' not found in session files")

    print(f"- Session UUIDs checked: {sum(len(frag[1].get('message_uuids', [])) for frag in session_fragments if '__json_error__' not in frag[1])}")
    print(f"- Missing UUIDs: {missing_uuids}\n")

    # Git alignment
    print("## 4. Git Alignment\n")

    missing_files = 0
    for line_no, ev in git_evidences:
        if "__json_error__" in ev:
            continue
        fp = ev.get("file_path")
        if fp and fp not in allowed_git_files:
            missing_files += 1
            soft_warnings.append(f"git-evidence line {line_no}: file_path '{fp}' not in git-alignment changed_files/key_files")

    for line_no, ev in git_hunk_evidences:
        if "__json_error__" in ev:
            continue
        fp = ev.get("file_path")
        if fp and fp not in allowed_git_files:
            missing_files += 1
            soft_warnings.append(f"git-hunk-evidence line {line_no}: file_path '{fp}' not in git-alignment changed_files/key_files")

    print(f"- Git evidence files: {len(evidence_ids)}")
    print(f"- Git hunk evidence files: {len(hunk_evidence_ids)}")
    print(f"- Files outside git-alignment: {missing_files}\n")

    # Dual entry
    print("## 5. Dual-Entry Coverage\n")

    dual_entry_failures = 0
    for line_no, unit in experience_units:
        if "__json_error__" in unit:
            continue
        axes = {tag_axis_by_id.get(tid) for tid in unit.get("tag_ids", [])}
        if "method" not in axes or "project_phase" not in axes:
            dual_entry_failures += 1
            errors.append(f"experience-units line {line_no}: missing method or project_phase tag (axes: {axes})")

    print(f"- Units with method + phase tags: {len(experience_units) - dual_entry_failures}/{len(experience_units)}\n")

    # Capture markers
    print("## 6. Capture Markers\n")

    unresolved_anchors = 0
    for line_no, marker in capture_markers:
        if "__json_error__" in marker:
            continue
        confidence = marker.get("anchor_confidence")
        if confidence in (None, "unresolved"):
            unresolved_anchors += 1
            soft_warnings.append(f"capture-markers line {line_no}: unresolved anchor for marker '{marker.get('marker_id')}'")

    print(f"- Capture markers: {len(capture_markers)}")
    print(f"- Unresolved anchors: {unresolved_anchors}\n")

    # Privacy scan
    print("## 7. Privacy Scan\n")

    privacy_hits = 0
    files_to_scan = [
        SAMPLE_DIR / "tags-v0.2.json",
        SAMPLE_DIR / "session-fragments-v0.2.jsonl",
        SAMPLE_DIR / "git-evidence-v0.2.jsonl",
        SAMPLE_DIR / "git-hunk-evidence-v0.2.jsonl",
        SAMPLE_DIR / "decision-points-v0.2.jsonl",
        SAMPLE_DIR / "experience-units-v0.2.jsonl",
        SAMPLE_DIR / "course-modules-v0.2.json",
        SAMPLE_DIR / "learning-paths-v0.2.json",
        SAMPLE_DIR / "capture-markers-v0.2.jsonl",
    ]
    for path in files_to_scan:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        hits = privacy_scan(text, scrubbing_manifest)
        for hit in hits:
            privacy_hits += 1
            errors.append(f"{path.name}: {hit}")

    print(f"- Files scanned: {sum(1 for p in files_to_scan if p.exists())}")
    print(f"- Privacy hits: {privacy_hits}\n")

    # Summary
    print("## Summary\n")

    if args.strict:
        # In strict mode, soft warnings block publication.
        errors.extend(soft_warnings)
        soft_warnings = []

    if errors:
        print(f"**Errors:** {len(errors)}")
        for e in errors:
            print(f"- {e}")
        print()

    if warnings:
        print(f"**Warnings:** {len(warnings)}")
        for w in warnings:
            print(f"- {w}")
        print()

    if soft_warnings:
        print(f"**Soft warnings:** {len(soft_warnings)}")
        print("_Soft warnings are acceptable for v0.x but must be reviewed and recorded. "
              "Use `--strict` to treat them as errors._\n")
        for w in soft_warnings:
            print(f"- {w}")
        print()

    if not errors and not warnings and not soft_warnings:
        print("All checks passed. v0.2 sample data is valid and ready for downstream use.")
    elif not errors:
        print("No errors. Warnings / soft warnings should be reviewed but do not block downstream use.")
    else:
        print("Validation failed. Fix errors before committing or publishing.")


if __name__ == "__main__":
    main()
