#!/usr/bin/env python3
"""
Wayfinder session scrubber.

Reads Claude Code session JSONL files and produces a privacy-safe version
for use in experience packages.

Usage:
    python scripts/scrubber.py \
        --input ~/.claude/projects/C--Users-liyongquan/be0044d7-eb49-449b-b05b-2f71b3a742d7.jsonl \
        --output data/samples/cyber-game-m9/session-be0044d7-scrubbed.jsonl \
        --manifest data/samples/cyber-game-m9/scrubbing-manifest.json \
        --sidecar-input ~/.claude/projects/C--Users-liyongquan--2/b88de51a-capture-markers.jsonl \
        --sidecar-output data/samples/cyber-game-m9/b88de51a-capture-markers-scrubbed.jsonl
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

DEFAULT_SECRET_PATTERNS = [
    # API keys / tokens (generic)
    (r"(?i)(api[_-]?key|apikey|token|secret|password|passwd|pwd)\s*[:=]\s*['\"]?([a-z0-9_\-]{16,})['\"]?", "<REDACTED_SECRET>"),
    # Bearer tokens
    (r"(?i)bearer\s+[a-z0-9_\-\.]{20,}", "<REDACTED_SECRET>"),
    # Private keys
    (r"-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----", "<REDACTED_SECRET>"),
    # GitHub personal access tokens (classic or fine-grained)
    (r"gh[pousr]_[A-Za-z0-9_]{36,}", "<REDACTED_SECRET>"),
    # AWS access key id + secret
    (r"AKIA[0-9A-Z]{16}", "<REDACTED_SECRET>"),
    (r"(?i)aws[_-]?secret[_-]?access[_-]?key\s*[:=]\s*['\"]?([a-z0-9/+=]{40})['\"]?", "<REDACTED_SECRET>"),
]


def load_manifest(manifest_path: Path) -> dict[str, Any]:
    with manifest_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def build_replacements(manifest: dict[str, Any]) -> list[tuple[str, str]]:
    """Build ordered replacement list. Longest strings first to avoid partial matches."""
    rules = manifest.get("string_replacements", [])
    # Sort by length descending so e.g. PROJECT_ROOT matches before HOME.
    return sorted(rules.items(), key=lambda kv: len(kv[0]), reverse=True)


def scrub_text(text: str, replacements: list[tuple[str, str]], secret_patterns: list[tuple[str, str]]) -> str:
    if not isinstance(text, str):
        return text

    # Ordered literal replacements.
    for old, new in replacements:
        text = text.replace(old, new)

    # Secret regex replacements.
    for pattern, replacement in secret_patterns:
        text = re.sub(pattern, replacement, text)

    return text


def scrub_value(value: Any, replacements: list[tuple[str, str]], secret_patterns: list[tuple[str, str]]) -> Any:
    if isinstance(value, str):
        return scrub_text(value, replacements, secret_patterns)
    if isinstance(value, list):
        return [scrub_value(item, replacements, secret_patterns) for item in value]
    if isinstance(value, dict):
        return {k: scrub_value(v, replacements, secret_patterns) for k, v in value.items()}
    return value


def scrub_record(record: dict[str, Any], replacements: list[tuple[str, str]], secret_patterns: list[tuple[str, str]]) -> dict[str, Any]:
    record_type = record.get("type")

    # Drop file-history-snapshot payloads but keep the record shell.
    if record_type == "file-history-snapshot":
        snapshot = record.get("snapshot", {})
        scrubbed_snapshot = {
            "messageId": snapshot.get("messageId"),
            "trackedFileBackups": "<file-backups-redacted>",
            "timestamp": snapshot.get("timestamp"),
        }
        record["snapshot"] = scrubbed_snapshot
        return record

    return scrub_value(record, replacements, secret_patterns)


def scrub_file(input_path: Path, output_path: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    replacements = build_replacements(manifest)
    secret_patterns = [(p, r) for p, r in DEFAULT_SECRET_PATTERNS]
    if manifest.get("extra_secret_patterns"):
        secret_patterns.extend((p, r) for p, r in manifest["extra_secret_patterns"])

    output_path.parent.mkdir(parents=True, exist_ok=True)

    stats = {
        "input_lines": 0,
        "output_lines": 0,
        "file_history_snapshots": 0,
        "secrets_detected": 0,
    }

    with input_path.open("r", encoding="utf-8") as infile, output_path.open("w", encoding="utf-8") as outfile:
        for line in infile:
            stats["input_lines"] += 1
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                # Preserve malformed lines as-is after basic scrubbing.
                outfile.write(scrub_text(line, replacements, secret_patterns) + "\n")
                stats["output_lines"] += 1
                continue

            if record.get("type") == "file-history-snapshot":
                stats["file_history_snapshots"] += 1

            scrubbed = scrub_record(record, replacements, secret_patterns)
            outfile.write(json.dumps(scrubbed, ensure_ascii=False) + "\n")
            stats["output_lines"] += 1

    # Run a post-pass secret scan on the output for reporting.
    with output_path.open("r", encoding="utf-8") as f:
        output_text = f.read()
    for pattern, _ in secret_patterns:
        stats["secrets_detected"] += len(re.findall(pattern, output_text))

    return stats


def scrub_markers(input_path: Path | None, output_path: Path | None, manifest: dict[str, Any]) -> dict[str, Any]:
    """Scrub a capture-markers JSONL sidecar file."""
    stats = {"input_markers": 0, "output_markers": 0, "secrets_detected": 0}
    if not input_path or not output_path:
        return stats
    if not input_path.exists():
        # Touch an empty scrubbed file so downstream scripts can still open it.
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("", encoding="utf-8")
        return stats

    replacements = build_replacements(manifest)
    secret_patterns = [(p, r) for p, r in DEFAULT_SECRET_PATTERNS]
    if manifest.get("extra_secret_patterns"):
        secret_patterns.extend((p, r) for p, r in manifest["extra_secret_patterns"])

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with input_path.open("r", encoding="utf-8") as infile, output_path.open("w", encoding="utf-8") as outfile:
        for line in infile:
            line = line.strip()
            if not line:
                continue
            stats["input_markers"] += 1
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                outfile.write(scrub_text(line, replacements, secret_patterns) + "\n")
                stats["output_markers"] += 1
                continue

            scrubbed = scrub_value(record, replacements, secret_patterns)
            outfile.write(json.dumps(scrubbed, ensure_ascii=False) + "\n")
            stats["output_markers"] += 1

    with output_path.open("r", encoding="utf-8") as f:
        output_text = f.read()
    for pattern, _ in secret_patterns:
        stats["secrets_detected"] += len(re.findall(pattern, output_text))

    return stats


def main() -> int:
    parser = argparse.ArgumentParser(description="Scrub Claude Code session JSONL for Wayfinder.")
    parser.add_argument("--input", required=True, type=Path, help="Input JSONL session file.")
    parser.add_argument("--output", required=True, type=Path, help="Output scrubbed JSONL file.")
    parser.add_argument("--manifest", required=True, type=Path, help="Scrubbing manifest JSON.")
    parser.add_argument("--sidecar-input", type=Path, default=None, help="Optional capture markers sidecar JSONL.")
    parser.add_argument("--sidecar-output", type=Path, default=None, help="Output scrubbed capture markers JSONL.")
    args = parser.parse_args()

    manifest = load_manifest(args.manifest)
    session_stats = scrub_file(args.input, args.output, manifest)
    marker_stats = scrub_markers(args.sidecar_input, args.sidecar_output, manifest)

    print(json.dumps({"session": session_stats, "markers": marker_stats}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
