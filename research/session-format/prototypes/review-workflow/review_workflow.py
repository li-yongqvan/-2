"""
PROTOTYPE — Review workflow state machine for ExperienceUnit v0.2.

Pure logic module: no I/O beyond the helpers below, no terminal/UI code.
The FastAPI shell in main.py imports and drives this.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# State machine
# ---------------------------------------------------------------------------

REVIEW_STATUSES = ["draft", "reviewed", "approved", "rejected"]

# Which transitions are legal from the current status.
# The prototype intentionally keeps the graph permissive so reviewers can
# recover from mis-clicks; production may lock rejected/approved behind a
# confirmation or admin flag.
ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    "draft": {"reviewed", "approved", "rejected"},
    "reviewed": {"draft", "approved", "rejected"},
    "approved": {"reviewed", "draft", "rejected"},
    "rejected": {"reviewed", "draft", "approved"},
}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def transition(unit: dict[str, Any], target_status: str) -> dict[str, Any]:
    """Return a new-like unit dict with the updated review_status and timestamp."""
    current = unit.get("review_status", "draft")
    if target_status not in ALLOWED_TRANSITIONS.get(current, set()):
        raise ValueError(f"Illegal transition: {current} -> {target_status}")

    updated = dict(unit)
    updated["review_status"] = target_status
    updated["updated_at"] = now_iso()
    return updated


def set_note(unit: dict[str, Any], note: str) -> dict[str, Any]:
    """Update reviewer_notes and bump updated_at. Does not change status."""
    updated = dict(unit)
    updated["reviewer_notes"] = note.strip()
    updated["updated_at"] = now_iso()
    return updated


def review(unit: dict[str, Any], target_status: str, note: str | None = None) -> dict[str, Any]:
    """Apply a review action (approve / reject / edit-note)."""
    updated = transition(unit, target_status)
    if note is not None:
        updated = set_note(updated, note)
    return updated


# ---------------------------------------------------------------------------
# Data loading / saving
# ---------------------------------------------------------------------------


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if not path.exists():
        return records
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def load_sample(sample_dir: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, dict[str, Any]]]:
    """
    Load ExperienceUnits, .needs_review anchors, and decision points from a v0.2 sample directory.

    Returns:
        - units: all ExperienceUnit records (review_status defaults to "draft")
        - anchors: raw .needs_review items
        - decisions: dict decision_id -> decision point record
    """
    units_path = sample_dir / "experience-units-v0.2.jsonl"
    needs_review_path = sample_dir / ".needs_review"
    decisions_path = sample_dir / "decision-points-v0.2.jsonl"

    units = read_jsonl(units_path)
    for unit in units:
        unit.setdefault("review_status", "draft")
        unit.setdefault("reviewer_notes", "")
        unit.setdefault("updated_at", unit.get("created_at", now_iso()))

    anchors: list[dict[str, Any]] = []
    if needs_review_path.exists():
        payload = json.loads(needs_review_path.read_text(encoding="utf-8"))
        anchors = payload.get("items", [])

    decisions = {d["id"]: d for d in read_jsonl(decisions_path)}

    return units, anchors, decisions


def group_anchors_by_unit(
    units: list[dict[str, Any]], anchors: list[dict[str, Any]]
) -> dict[str, list[dict[str, Any]]]:
    """Map unit_id -> list of .needs_review items for that decision."""
    by_unit: dict[str, list[dict[str, Any]]] = {u["unit_id"]: [] for u in units}
    decision_to_unit = {u["decision_id"]: u["unit_id"] for u in units}
    for anchor in anchors:
        unit_id = decision_to_unit.get(anchor["decision_id"])
        if unit_id:
            by_unit.setdefault(unit_id, []).append(anchor)
    return by_unit


# ---------------------------------------------------------------------------
# Stats / helpers for the UI
# ---------------------------------------------------------------------------


def compute_stats(units: list[dict[str, Any]]) -> dict[str, int]:
    stats = {status: 0 for status in REVIEW_STATUSES}
    for unit in units:
        stats[unit.get("review_status", "draft")] += 1
    return stats
