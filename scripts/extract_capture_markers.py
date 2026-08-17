#!/usr/bin/env python3
"""
Extract capture markers from a scrubbed Claude Code session JSONL.

Reads:
- a scrubbed session file (e.g. session-be0044d7-scrubbed.jsonl)
- an optional /capture skill sidecar file (e.g. be0044d7-capture-markers.jsonl)

Produces a single capture-markers-v0.2.jsonl with both inline #insight markers
and structured skill markers, validated against capture-marker-v0.2.schema.json.

Usage:
    python scripts/extract_capture_markers.py \
        --session data/samples/cyber-game-m9/session-be0044d7-scrubbed.jsonl \
        --sidecar ~/.claude/projects/C--Users-liyongquan--2/b88de51a-capture-markers.jsonl \
        --output data/samples/cyber-game-m9/capture-markers-v0.2.jsonl
"""

from __future__ import annotations

import argparse
import json
import os
import re
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
SCHEMA_PATH = REPO_ROOT / "research" / "session-format" / "schemas" / "capture-marker-v0.2.schema.json"

INSIGHT_RE = re.compile(
    r"#insight\s*(?:\[(?P<metadata>[^\]]+)\])?\s*:\s*(?P<summary>.+?)(?=\n|$)",
    re.IGNORECASE | re.DOTALL,
)

METHOD_TAGS = {
    "task_definition",
    "method_selection",
    "scope_tradeoff",
    "context_injection",
    "prompt_refinement",
    "constraint_declaration",
    "course_correction",
    "acceptance_termination",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if not path.exists():
        return records
    with path.open("r", encoding="utf-8") as f:
        for line_no, raw in enumerate(f, start=1):
            raw = raw.strip()
            if not raw:
                continue
            try:
                records.append(json.loads(raw))
            except json.JSONDecodeError as exc:
                print(f"warning: {path.name} line {line_no}: invalid JSON - {exc}", file=sys.stderr)
    return records


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def message_text(message: dict[str, Any]) -> str:
    """Extract searchable text from a Claude Code message object."""
    if not isinstance(message, dict):
        return ""
    content = message.get("content", "")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, dict):
                if block.get("type") == "text":
                    parts.append(block.get("text", ""))
                elif "text" in block and isinstance(block["text"], str):
                    parts.append(block["text"])
        return "\n".join(parts)
    return ""


def find_project_root(start: Path) -> Path | None:
    """Walk up until we find a git repo or experience-package markers."""
    current = start.resolve()
    for _ in range(64):
        if (current / ".git").exists():
            return current
        if (current / "docs" / "decisions").exists():
            return current
        if (current / "research" / "session-format").exists():
            return current
        parent = current.parent
        if parent == current:
            break
        current = parent
    return None


def normalize_short_slug(name: str) -> str:
    """Directory basename -> marker-id-safe short slug."""
    slug = name.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    if not slug:
        slug = "project"
    if slug[0].isdigit():
        slug = "p" + slug
    return slug[:32]


def read_short_slug(project_root: Path) -> str | None:
    config_path = project_root / ".claude" / "capture.json"
    if not config_path.exists():
        return None
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
        slug = data.get("short_slug")
        return normalize_short_slug(slug) if slug else None
    except (json.JSONDecodeError, OSError):
        return None


def get_short_slug(project_root: Path) -> str:
    configured = read_short_slug(project_root)
    if configured:
        return configured
    return normalize_short_slug(project_root.name)


def parse_metadata(metadata_text: str | None) -> dict[str, str]:
    result: dict[str, str] = {}
    if not metadata_text:
        return result
    for part in metadata_text.split(","):
        part = part.strip()
        if "=" in part:
            key, value = part.split("=", 1)
            result[key.strip().lower()] = value.strip()
    return result


def extract_insight_markers(
    session_records: list[dict[str, Any]],
    session_id: str,
    short_slug: str,
) -> list[dict[str, Any]]:
    markers: list[dict[str, Any]] = []
    seq = 0
    for record in session_records:
        if record.get("type") != "user" or record.get("isMeta"):
            continue
        msg = record.get("message", {}) or {}
        if msg.get("role") != "user":
            continue
        text = message_text(msg)
        if not text:
            continue

        for match in INSIGHT_RE.finditer(text):
            seq += 1
            metadata = parse_metadata(match.group("metadata"))
            summary = match.group("summary").strip()
            if len(summary) > 280:
                summary = summary[:279] + "…"

            method_tag = metadata.get("method")
            if method_tag and method_tag not in METHOD_TAGS:
                print(
                    f"warning: unknown method_tag '{method_tag}' in #insight; ignoring",
                    file=sys.stderr,
                )
                method_tag = None

            theme_tag = metadata.get("theme") or None
            commit = metadata.get("commit")
            notes = f"commit: {commit}" if commit else ""

            markers.append(
                {
                    "marker_id": f"cm-{short_slug}-{session_id[:8]}-{seq:03d}",
                    "marker_type": "insight",
                    "session_id": session_id,
                    "anchor_message_uuid": record.get("uuid"),
                    "anchor_confidence": "exact",
                    "timestamp": record.get("timestamp") or now_iso(),
                    "summary": summary,
                    "method_tag": method_tag,
                    "theme_tag": theme_tag,
                    "source": "inline",
                    "notes": notes,
                }
            )
    return markers


def load_sidecar_markers(path: Path) -> list[dict[str, Any]]:
    records = load_jsonl(path)
    cleaned: list[dict[str, Any]] = []
    for record in records:
        if not isinstance(record, dict):
            continue
        record.setdefault("source", "skill")
        record.setdefault("marker_type", "capture")
        cleaned.append(record)
    return cleaned


def resolve_anchor_by_timestamp(
    marker: dict[str, Any],
    session_records: list[dict[str, Any]],
    tolerance_seconds: float = 3.0,
) -> dict[str, Any]:
    """Fill anchor_message_uuid for sidecar markers that lack one."""
    if marker.get("anchor_message_uuid"):
        marker.setdefault("anchor_confidence", "exact")
        return marker

    marker_ts = marker.get("timestamp")
    if not marker_ts:
        marker["anchor_confidence"] = "unresolved"
        return marker

    try:
        marker_dt = datetime.fromisoformat(marker_ts.replace("Z", "+00:00"))
    except ValueError:
        marker["anchor_confidence"] = "unresolved"
        return marker

    best_uuid = None
    best_delta = tolerance_seconds + 1.0
    for record in session_records:
        if record.get("type") not in ("user", "assistant"):
            continue
        ts = record.get("timestamp")
        if not ts:
            continue
        try:
            rec_dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except ValueError:
            continue
        delta = abs((marker_dt - rec_dt).total_seconds())
        if delta <= tolerance_seconds and delta < best_delta:
            best_delta = delta
            best_uuid = record.get("uuid")

    if best_uuid:
        marker["anchor_message_uuid"] = best_uuid
        marker["anchor_confidence"] = "nearest"
    else:
        marker["anchor_confidence"] = "unresolved"
    return marker


def validate_marker(
    marker: dict[str, Any],
    validator: Any,
) -> list[str]:
    errors: list[str] = []
    if validator:
        for err in validator.iter_errors(marker):
            path = "/".join(str(p) for p in err.absolute_path) or "<root>"
            errors.append(f"{path}: {err.message}")
    else:
        for key in ("marker_id", "marker_type", "session_id", "timestamp", "summary", "source"):
            if key not in marker:
                errors.append(f"missing required field '{key}'")
    return errors


def discover_session_id(session_records: list[dict[str, Any]]) -> str | None:
    for record in session_records:
        sid = record.get("sessionId") or record.get("session_id")
        if sid:
            return sid
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract capture markers from a scrubbed session.")
    parser.add_argument("--session", required=True, type=Path, help="Scrubbed session JSONL.")
    parser.add_argument("--sidecar", type=Path, default=None, help="Optional /capture skill sidecar JSONL.")
    parser.add_argument("--output", required=True, type=Path, help="Output capture-markers JSONL.")
    parser.add_argument(
        "--project-root",
        type=Path,
        default=None,
        help="Project root for short-slug detection (defaults to auto-detect from cwd).",
    )
    parser.add_argument(
        "--tolerance",
        type=float,
        default=3.0,
        help="Timestamp matching tolerance in seconds for sidecar anchors (default: 3).",
    )
    args = parser.parse_args()

    session_records = load_jsonl(args.session)
    session_id = discover_session_id(session_records)
    if not session_id:
        print(f"error: could not determine session_id from {args.session}", file=sys.stderr)
        return 1

    project_root = args.project_root
    if not project_root:
        project_root = find_project_root(Path.cwd())
    if not project_root:
        print("error: could not detect project root; pass --project-root", file=sys.stderr)
        return 1

    short_slug = get_short_slug(project_root)

    # Load schema validator if available.
    validator = None
    if HAS_JSONSCHEMA and SCHEMA_PATH.exists():
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        validator = jsonschema.Draft7Validator(schema)

    # Extract inline #insight markers.
    inline_markers = extract_insight_markers(session_records, session_id, short_slug)

    # Load and anchor sidecar markers.
    sidecar_markers: list[dict[str, Any]] = []
    if args.sidecar and args.sidecar.exists():
        sidecar_markers = load_sidecar_markers(args.sidecar)
        for marker in sidecar_markers:
            resolve_anchor_by_timestamp(marker, session_records, args.tolerance)

    # Merge, sort by timestamp, renumber IDs for canonical output.
    all_markers = inline_markers + sidecar_markers
    all_markers.sort(key=lambda m: m.get("timestamp") or now_iso())

    renumbered: list[dict[str, Any]] = []
    for seq, marker in enumerate(all_markers, start=1):
        marker["marker_id"] = f"cm-{short_slug}-{session_id[:8]}-{seq:03d}"
        marker["session_id"] = session_id
        errors = validate_marker(marker, validator)
        for err in errors:
            print(f"warning: {marker.get('marker_id')} - {err}", file=sys.stderr)
        renumbered.append(marker)

    write_jsonl(args.output, renumbered)

    print(
        json.dumps(
            {
                "session_id": session_id,
                "project_root": str(project_root),
                "short_slug": short_slug,
                "inline_markers": len(inline_markers),
                "sidecar_markers": len(sidecar_markers),
                "output": str(args.output),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
