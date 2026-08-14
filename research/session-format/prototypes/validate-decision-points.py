#!/usr/bin/env python3
"""
PROTOTYPE — Decision Point Schema Validator v0.1

Throwaway script to sanity-check whether the reverse-engineered JSON Schema
covers the real decision-points.jsonl sample from cyber-game M8-M9.

Run:
    python research/session-format/prototypes/validate-decision-points.py

Expects:
    - research/session-format/schemas/decision-point-v0.1.schema.json
    - data/samples/cyber-game-m9/decision-points.jsonl
"""

import json
import jsonschema
from collections import Counter, defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SCHEMA_PATH = REPO_ROOT / "research" / "session-format" / "schemas" / "decision-point-v0.1.schema.json"
DATA_PATH = REPO_ROOT / "data" / "samples" / "cyber-game-m9" / "decision-points.jsonl"


def load_jsonl(path: Path) -> list[dict]:
    records = []
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


def main() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    records = load_jsonl(DATA_PATH)

    validator = jsonschema.Draft7Validator(schema)

    total = len(records)
    passed = 0
    per_record_errors: list[tuple[int, str, list[str]]] = []
    field_error_counts: Counter = Counter()
    field_occurrence_counts: Counter = Counter()
    all_field_names = set(schema["properties"].keys())

    for line_no, record in records:
        if "__json_error__" in record:
            per_record_errors.append((line_no, record.get("id", "?"), [record["__json_error__"]]))
            continue

        # Track which schema fields appear in the record (top-level only for v0.1)
        for field in all_field_names:
            field_occurrence_counts[field] += 1 if field in record else 0

        errors = list(validator.iter_errors(record))
        if not errors:
            passed += 1
            per_record_errors.append((line_no, record.get("id", "?"), []))
        else:
            messages = []
            for err in errors:
                path = "/".join(str(p) for p in err.absolute_path) or "<root>"
                field = err.absolute_path[0] if err.absolute_path else "<root>"
                field_error_counts[field] += 1
                messages.append(f"{path}: {err.message}")
            per_record_errors.append((line_no, record.get("id", "?"), messages))

    print("=" * 60)
    print("Decision Point Schema Validation Report (v0.1)")
    print("=" * 60)
    print(f"Schema : {SCHEMA_PATH}")
    print(f"Data   : {DATA_PATH}")
    print(f"Records: {total} | Passed: {passed} | Failed: {total - passed}")
    print()

    # Per-record summary
    print("Per-record results:")
    for line_no, record_id, errors in per_record_errors:
        status = "PASS" if not errors else "FAIL"
        detail = "" if not errors else f" ({len(errors)} error(s))"
        print(f"  Line {line_no:3d} [{record_id}]: {status}{detail}")
    print()

    # Per-field summary
    print("Per-field coverage & validation:")
    for field in sorted(all_field_names):
        present = field_occurrence_counts[field]
        errors = field_error_counts[field]
        coverage = f"present {present}/{total}"
        if errors == 0 and present == total:
            status = "OK all valid"
        elif errors:
            status = f"FAIL {errors} error(s)"
        else:
            status = "WARN missing in some"
        print(f"  {field:20s} | {coverage:15s} | {status}")
    print()

    # Detailed errors
    failed_records = [(ln, rid, errs) for ln, rid, errs in per_record_errors if errs]
    if failed_records:
        print("Detailed errors:")
        for line_no, record_id, errors in failed_records:
            print(f"  Line {line_no} [{record_id}]:")
            for msg in errors:
                print(f"    - {msg}")
    else:
        print("No schema violations found.")


if __name__ == "__main__":
    main()
