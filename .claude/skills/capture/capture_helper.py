#!/usr/bin/env python3
"""
Helper for the /capture Claude Code skill.

Appends a capture marker to the per-session sidecar file:
    ~/.claude/projects/<project-slug>/<sessionId>-capture-markers.jsonl

Usage:
    python capture_helper.py append --json-file /path/to/input.json

input.json fields:
    summary (required), method_tag, theme_tag, notes, anchor_target
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

DEFAULT_SECRET_PATTERNS = [
    (r"(?i)(api[_-]?key|apikey|token|secret|password|passwd|pwd)\s*[:=]\s*['\"]?([a-z0-9_\-]{16,})['\"]?", "<REDACTED_SECRET>"),
    (r"(?i)bearer\s+[a-z0-9_\-\.]{20,}", "<REDACTED_SECRET>"),
    (r"-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----", "<REDACTED_SECRET>"),
    (r"gh[pousr]_[A-Za-z0-9_]{36,}", "<REDACTED_SECRET>"),
    (r"AKIA[0-9A-Z]{16}", "<REDACTED_SECRET>"),
]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def encode_project_slug(path: Path) -> str:
    r"""Mirror Claude Code's project slug encoding: C:\Users\foo -> C--Users-foo."""
    raw = str(path.resolve())
    slug = re.sub(r"[\\/]", "-", raw)
    slug = re.sub(r":", "-", slug)
    return slug.strip("-")


def normalize_short_slug(name: str) -> str:
    slug = name.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    if not slug:
        slug = "project"
    if slug[0].isdigit():
        slug = "p" + slug
    return slug[:32]


def find_project_root(start: Path) -> Path:
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
    raise RuntimeError(f"Could not find project root from {start}")


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


def light_scrub(text: str, project_root: Path) -> str:
    if not isinstance(text, str):
        return text
    home = str(Path.home())
    proj = str(project_root.resolve())
    # Longest first to avoid partial replacements.
    for old, new in sorted([(proj, "<PROJECT_ROOT>"), (home, "<HOME>")], key=lambda kv: len(kv[0]), reverse=True):
        text = text.replace(old, new)
    for pattern, replacement in DEFAULT_SECRET_PATTERNS:
        text = re.sub(pattern, replacement, text)
    return text


def next_sequence(sidecar_path: Path) -> int:
    if not sidecar_path.exists():
        return 1
    count = 0
    with sidecar_path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                count += 1
    return count + 1


def cmd_append(args: argparse.Namespace) -> int:
    json_file = Path(args.json_file)
    if not json_file.exists():
        print(f"error: input file not found: {json_file}", file=sys.stderr)
        return 1

    try:
        payload = json.loads(json_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"error: invalid JSON input: {exc}", file=sys.stderr)
        return 1

    summary = payload.get("summary", "").strip()
    if not summary:
        print("error: summary is required", file=sys.stderr)
        return 1

    try:
        project_root = find_project_root(Path.cwd())
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    session_id = os.environ.get("CLAUDE_CODE_SESSION_ID")
    if not session_id:
        print(
            "error: CLAUDE_CODE_SESSION_ID not set. "
            "Make sure /capture is run inside a Claude Code session.",
            file=sys.stderr,
        )
        return 1

    project_slug = encode_project_slug(project_root)
    short_slug = get_short_slug(project_root)

    claude_home = Path.home() / ".claude"
    project_dir = claude_home / "projects" / project_slug
    sidecar_path = project_dir / f"{session_id}-capture-markers.jsonl"

    project_dir.mkdir(parents=True, exist_ok=True)

    method_tag = payload.get("method_tag") or None
    theme_tag = payload.get("theme_tag") or None
    notes = payload.get("notes", "")
    anchor_target = payload.get("anchor_target", "previous_assistant")

    notes = light_scrub(notes, project_root)
    summary = light_scrub(summary, project_root)

    if method_tag and method_tag not in {
        "task_definition",
        "method_selection",
        "scope_tradeoff",
        "context_injection",
        "prompt_refinement",
        "constraint_declaration",
        "course_correction",
        "acceptance_termination",
    }:
        print(f"warning: unknown method_tag '{method_tag}'; ignoring", file=sys.stderr)
        method_tag = None

    seq = next_sequence(sidecar_path)
    marker = {
        "marker_id": f"cm-{short_slug}-{session_id[:8]}-{seq:03d}",
        "marker_type": "capture",
        "session_id": session_id,
        "anchor_message_uuid": "",
        "anchor_confidence": "unresolved",
        "timestamp": now_iso(),
        "summary": summary,
        "method_tag": method_tag,
        "theme_tag": theme_tag,
        "source": "skill",
        "notes": notes + (f" [anchor_target={anchor_target}]" if anchor_target else ""),
    }

    with sidecar_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(marker, ensure_ascii=False) + "\n")

    print(
        json.dumps(
            {
                "status": "ok",
                "marker_id": marker["marker_id"],
                "sidecar": str(sidecar_path),
                "anchor_target": anchor_target,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture skill helper")
    sub = parser.add_subparsers(dest="command", required=True)

    append_parser = sub.add_parser("append")
    append_parser.add_argument("--json-file", required=True, help="JSON file with capture fields")

    args = parser.parse_args()
    if args.command == "append":
        return cmd_append(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
