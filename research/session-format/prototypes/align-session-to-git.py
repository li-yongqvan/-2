#!/usr/bin/env python3
"""
PROTOTYPE — Align SessionFragment → Decision → Code chain v0.1

Throwaway script to reconstruct a "conversation → decision → code" chain from
v0.2 session fragments, decision points, and git evidence. Also generates
GitHunkEvidence by parsing `git diff` for matched files.

Run:
    python research/session-format/prototypes/align-session-to-git.py

Expects:
    - data/samples/cyber-game-m9/session-be0044d7-scrubbed.jsonl
    - data/samples/cyber-game-m9/session-fragments-v0.2.jsonl
    - data/samples/cyber-game-m9/decision-points-v0.2.jsonl
    - data/samples/cyber-game-m9/git-evidence-v0.2.jsonl
    - data/samples/cyber-game-m9/git-alignment.json

Outputs:
    - data/samples/cyber-game-m9/alignment-chain-v0.2.jsonl
    - data/samples/cyber-game-m9/git-hunk-evidence-v0.2.jsonl
    - data/samples/cyber-game-m9/alignment-chain-report.md

Rules decided by grilling (#4):
    1. Slice-level alignment: each SessionFragment/DecisionPoint is aligned individually.
    2. Message timestamp is the primary timeline anchor.
    3. Uncommitted-stage decisions are allowed to float (no git evidence) and may be
       back-filled by heuristic inference from later commits touching affected_files.
    4. Hunk-level evidence lives in a separate GitHunkEvidence schema.
"""

import json
import re
import subprocess
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
SAMPLE_DIR = REPO_ROOT / "data" / "samples" / "cyber-game-m9"

SESSION_PATH = SAMPLE_DIR / "session-be0044d7-scrubbed.jsonl"
FRAGMENTS_PATH = SAMPLE_DIR / "session-fragments-v0.2.jsonl"
DECISIONS_PATH = SAMPLE_DIR / "decision-points-v0.2.jsonl"
GIT_EVIDENCE_PATH = SAMPLE_DIR / "git-evidence-v0.2.jsonl"
ALIGNMENT_PATH = SAMPLE_DIR / "git-alignment.json"

OUT_CHAIN_PATH = SAMPLE_DIR / "alignment-chain-v0.2.jsonl"
OUT_HUNK_PATH = SAMPLE_DIR / "git-hunk-evidence-v0.2.jsonl"
OUT_REPORT_PATH = SAMPLE_DIR / "alignment-chain-report.md"
SCRUBBING_PATH = SAMPLE_DIR / "scrubbing-manifest.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_scrubber(manifest: dict):
    """Return a function that applies manifest string_replacements longest-first."""
    replacements = sorted(
        manifest.get("string_replacements", {}).items(),
        key=lambda kv: len(kv[0]),
        reverse=True,
    )

    def scrub(text: str) -> str:
        for old, new in replacements:
            text = text.replace(old, new)
        return text

    return scrub


def load_jsonl(path: Path) -> list[dict]:
    records = []
    with path.open("r", encoding="utf-8") as f:
        for raw in f:
            raw = raw.strip()
            if raw:
                records.append(json.loads(raw))
    return records


def load_session_messages(path: Path) -> dict[str, dict]:
    """Index session messages by uuid, extracting timestamp and role."""
    messages: dict[str, dict] = {}
    for record in load_jsonl(path):
        uuid = record.get("uuid")
        if not uuid:
            continue
        ts = record.get("timestamp")
        if ts:
            try:
                parsed = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            except ValueError:
                parsed = None
        else:
            parsed = None
        messages[uuid] = {
            "uuid": uuid,
            "type": record.get("type"),
            "timestamp": ts,
            "parsed_ts": parsed,
        }
    return messages


def fragment_timestamp(fragment: dict, messages: dict[str, dict]) -> datetime | None:
    """Primary anchor: message timestamp from the scrubbed session."""
    for uuid in fragment.get("message_uuids", []):
        msg = messages.get(uuid)
        if msg and msg.get("parsed_ts"):
            return msg["parsed_ts"]
    return None


def run_git_diff(repo: Path, parent: str, commit: str, file_path: str) -> str:
    """Run git diff for a single file. Returns empty string on failure."""
    cmd = ["git", "diff", f"{parent}..{commit}", "--", file_path]
    try:
        result = subprocess.run(
            cmd,
            cwd=str(repo),
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
        )
        return result.stdout if result.returncode == 0 else ""
    except Exception:
        return ""


def parse_diff_hunks(diff_text: str) -> list[dict]:
    """Parse unified diff into hunks. Minimal, prototype-grade parser."""
    hunks: list[dict] = []
    lines = diff_text.splitlines()
    i = 0
    # Skip header lines until first hunk
    while i < len(lines) and not lines[i].startswith("@@"):
        i += 1
    while i < len(lines):
        line = lines[i]
        if not line.startswith("@@"):
            i += 1
            continue
        # Example: @@ -10,3 +15,5 @@ func header
        m = re.match(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@(.*)$", line)
        if not m:
            i += 1
            continue
        old_start = int(m.group(1))
        old_lines = int(m.group(2)) if m.group(2) else 1
        new_start = int(m.group(3))
        new_lines = int(m.group(4)) if m.group(4) else 1
        header = m.group(5).strip()
        hunk_lines: list[str] = []
        i += 1
        while i < len(lines):
            next_line = lines[i]
            if next_line.startswith("@@"):
                break
            if next_line.startswith("diff --git") or next_line.startswith("index "):
                break
            hunk_lines.append(next_line)
            i += 1
        hunks.append(
            {
                "old_start": old_start,
                "old_lines": old_lines,
                "new_start": new_start,
                "new_lines": new_lines,
                "header": header,
                "lines": "\n".join(hunk_lines),
            }
        )
    return hunks


def build_hunk_id(commit_sha: str, file_path: str, index: int) -> str:
    safe_file = re.sub(r"[^a-z0-9_.-]", "_", file_path.lower()).strip("_")
    return f"git-hunk-{commit_sha}-{safe_file}-{index}"


def build_code_ref(file_path: str, commit_sha: str) -> str:
    return f"<code-ref: {file_path} @ {commit_sha}>"


def generate_hunk_evidence(
    git_evidence: dict,
    repo: Path | None,
    scrub: callable,
) -> list[dict]:
    """Generate GitHunkEvidence records from a GitEvidence file record."""
    if not repo or git_evidence.get("kind") != "file":
        return []
    commit = git_evidence["commit_sha"]
    parent = git_evidence["parent_commit_sha"]
    file_path = git_evidence["file_path"]
    diff_text = run_git_diff(repo, parent, commit, file_path)
    if not diff_text:
        return []
    hunks = parse_diff_hunks(diff_text)
    records = []
    for idx, hunk in enumerate(hunks):
        scrubbed_lines = scrub(hunk.get("lines", ""))
        scrubbed_header = scrub(hunk.get("header", ""))
        records.append(
            {
                "evidence_id": build_hunk_id(commit, file_path, idx),
                "commit_sha": commit,
                "parent_commit_sha": parent,
                "file_path": file_path,
                "hunk_index": idx,
                "diff_command": f"git diff {parent}..{commit} -- {file_path}",
                "code_ref": build_code_ref(file_path, commit),
                "hunk": {
                    **hunk,
                    "header": scrubbed_header,
                    "lines": scrubbed_lines,
                },
                "notes": git_evidence.get("notes", ""),
                "alignment_quality": "heuristic",
            }
        )
    return records


def infer_evidence(
    decision: dict,
    alignment: dict,
    repo: Path | None,
) -> list[dict]:
    """Heuristic back-fill: if a decision has affected_files and the commit range
    touches one of those files, synthesise a GitEvidence and its hunks."""
    affected = set(decision.get("affected_files", []))
    if not affected:
        return []
    commit_range = alignment.get("commit_range", {})
    parent = commit_range.get("from")
    commit = commit_range.get("to")
    changed_files = set(alignment.get("changed_files", []))
    matched_files = affected & changed_files
    if not matched_files or not repo:
        return []

    inferred = []
    for file_path in sorted(matched_files):
        evidence_id = f"git-{commit}-{re.sub(r'[^a-z0-9_.-]', '_', file_path.lower()).strip('_')}"
        evidence = {
            "evidence_id": evidence_id,
            "commit_sha": commit,
            "parent_commit_sha": parent,
            "kind": "file",
            "file_path": file_path,
            "diff_command": f"git diff {parent}..{commit} -- {file_path}",
            "code_ref": build_code_ref(file_path, commit),
            "notes": f"Inferred from decision {decision['id']} affected_files intersecting commit range changed_files.",
        }
        inferred.append(evidence)
    return inferred


def build_chain(
    fragments: list[dict],
    decisions: list[dict],
    git_evidence_list: list[dict],
    hunk_evidence_list: list[dict],
    messages: dict[str, dict],
) -> list[dict]:
    """Build conversation → decision → code chain entries."""
    fragment_by_id = {f["fragment_id"]: f for f in fragments}
    evidence_by_id = {e["evidence_id"]: e for e in git_evidence_list}
    hunk_by_id = {h["evidence_id"]: h for h in hunk_evidence_list}

    chains = []
    for decision in decisions:
        fragment_ids = decision.get("session_fragment_ids", [])
        fragment_entries = [
            {
                "fragment_id": fid,
                "summary": fragment_by_id.get(fid, {}).get("summary", ""),
                "alignment_quality": fragment_by_id.get(fid, {}).get("alignment_quality", ""),
                "anchor_ts": (
                    fragment_by_id.get(fid, {}).get("_anchor_ts").isoformat()
                    if fid in fragment_by_id and fragment_by_id[fid].get("_anchor_ts")
                    else None
                ),
            }
            for fid in fragment_ids
        ]

        git_ids = decision.get("git_evidence_ids", [])
        git_entries = []
        for eid in git_ids:
            ev = evidence_by_id.get(eid)
            if ev:
                git_entries.append(
                    {
                        "evidence_id": ev["evidence_id"],
                        "kind": ev.get("kind"),
                        "file_path": ev.get("file_path"),
                        "commit_sha": ev.get("commit_sha"),
                    }
                )

        hunk_ids = decision.get("git_hunk_evidence_ids", [])
        hunk_entries = []
        for hid in hunk_ids:
            h = hunk_by_id.get(hid)
            if h:
                hunk_entries.append(
                    {
                        "evidence_id": h["evidence_id"],
                        "file_path": h["file_path"],
                        "hunk_index": h["hunk_index"],
                        "hunk_header": h["hunk"]["header"],
                    }
                )

        chains.append(
            {
                "decision_id": decision["id"],
                "title": decision["title"],
                "category": decision.get("category"),
                "timestamp": decision.get("timestamp"),
                "related_commit": decision.get("related_commit"),
                "alignment_quality": decision.get("alignment_quality"),
                "fragments": fragment_entries,
                "code": {"file_evidence": git_entries, "hunk_evidence": hunk_entries},
                "has_git_evidence": bool(git_entries or hunk_entries),
                "inferred": decision.get("_inferred", False),
            }
        )
    return chains


def write_jsonl(path: Path, records: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def main() -> None:
    alignment = json.loads(ALIGNMENT_PATH.read_text(encoding="utf-8"))
    manifest = load_json(SCRUBBING_PATH) if SCRUBBING_PATH.exists() else {}
    scrub = build_scrubber(manifest)

    repo_path = Path(alignment.get("repo_path", ""))
    repo = repo_path if repo_path.exists() and (repo_path / ".git").exists() else None
    if repo is None:
        print(f"WARN: repo {repo_path} not available; hunk parsing and inference disabled.")

    messages = load_session_messages(SESSION_PATH)
    fragments = load_jsonl(FRAGMENTS_PATH)
    decisions = load_jsonl(DECISIONS_PATH)
    git_evidence_list = load_jsonl(GIT_EVIDENCE_PATH)

    # Annotate fragments with anchor timestamp
    for frag in fragments:
        frag["_anchor_ts"] = fragment_timestamp(frag, messages)

    # Generate hunk evidence from explicit file evidence
    hunk_evidence_list: list[dict] = []
    for ev in git_evidence_list:
        hunk_evidence_list.extend(generate_hunk_evidence(ev, repo, scrub))

    # Heuristic back-fill for decisions with no git evidence
    for decision in decisions:
        if not decision.get("git_evidence_ids"):
            inferred = infer_evidence(decision, alignment, repo)
            if inferred:
                decision["_inferred"] = True
                decision["git_evidence_ids"] = [e["evidence_id"] for e in inferred]
                git_evidence_list.extend(inferred)
                for e in inferred:
                    hunk_evidence_list.extend(generate_hunk_evidence(e, repo, scrub))

    # Cross-reference hunk evidence into decision points
    file_to_hunks = defaultdict(list)
    for h in hunk_evidence_list:
        file_to_hunks[(h["commit_sha"], h["file_path"])].append(h["evidence_id"])

    evidence_by_id = {e["evidence_id"]: e for e in git_evidence_list}
    for decision in decisions:
        hunk_ids: list[str] = []
        for eid in decision.get("git_evidence_ids", []):
            ev = evidence_by_id.get(eid)
            if ev and ev.get("kind") == "file":
                key = (ev["commit_sha"], ev["file_path"])
                hunk_ids.extend(file_to_hunks.get(key, []))
        if hunk_ids:
            decision["git_hunk_evidence_ids"] = hunk_ids

    chains = build_chain(fragments, decisions, git_evidence_list, hunk_evidence_list, messages)

    write_jsonl(OUT_CHAIN_PATH, chains)
    write_jsonl(OUT_HUNK_PATH, hunk_evidence_list)

    # Markdown report
    total = len(chains)
    covered = sum(1 for c in chains if c["has_git_evidence"])
    inferred_count = sum(1 for c in chains if c["inferred"])
    report_lines = [
        "# Alignment Chain Report (prototype v0.1)",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        f"Total decisions: {total}",
        f"Decisions with git evidence: {covered}",
        f"Decisions with inferred evidence: {inferred_count}",
        f"Hunk evidence records: {len(hunk_evidence_list)}",
        "",
        "## Chain entries",
        "",
    ]
    for chain in chains:
        status = "✅" if chain["has_git_evidence"] else "⏳"
        report_lines.append(f"### {status} {chain['decision_id']}: {chain['title']}")
        report_lines.append(f"- Category: {chain['category']} | Quality: {chain['alignment_quality']}")
        report_lines.append("- Fragments:")
        for f in chain["fragments"]:
            report_lines.append(f"  - `{f['fragment_id']}` — {f['summary'][:80]}...")
        report_lines.append("- Code evidence:")
        for e in chain["code"]["file_evidence"]:
            report_lines.append(f"  - file `{e['file_path']}` @ `{e['commit_sha']}`")
        for h in chain["code"]["hunk_evidence"]:
            report_lines.append(f"  - hunk `{h['evidence_id']}` header: `{h['hunk_header']}`")
        if chain["inferred"]:
            report_lines.append("- _Evidence was inferred from affected_files; needs review._")
        report_lines.append("")

    OUT_REPORT_PATH.write_text("\n".join(report_lines), encoding="utf-8")

    print("=" * 60)
    print("Session → Decision → Code alignment prototype")
    print("=" * 60)
    print(f"Repo available      : {repo is not None} ({repo_path})")
    print(f"Messages indexed    : {len(messages)}")
    print(f"Fragments           : {len(fragments)}")
    print(f"Decisions           : {total}")
    print(f"Git evidence (total): {len(git_evidence_list)}")
    print(f"Hunk evidence       : {len(hunk_evidence_list)}")
    print(f"Covered decisions   : {covered}/{total}")
    print(f"Inferred decisions  : {inferred_count}")
    print()
    print(f"Wrote: {OUT_CHAIN_PATH}")
    print(f"Wrote: {OUT_HUNK_PATH}")
    print(f"Wrote: {OUT_REPORT_PATH}")


if __name__ == "__main__":
    main()
