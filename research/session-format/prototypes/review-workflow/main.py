"""
PROTOTYPE — Manual review workflow UI for ExperienceUnit v0.2.

Question being answered:
    "终端处理产出的结构化中间数据，需要作者人工审核后才能发布。
     这个审核工作流长什么样？"

Run:
    cd research/session-format/prototypes/review-workflow
    pip install -r requirements.txt
    python main.py

Then open http://127.0.0.1:8765
"""

from __future__ import annotations

import json
import os
import threading
import webbrowser
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

import review_workflow as rw


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[4]  # research/session-format/prototypes/review-workflow
DEFAULT_SAMPLE_DIR = REPO_ROOT / "data" / "samples" / "cyber-game-m9"
SAMPLE_DIR = Path(os.environ.get("REVIEW_SAMPLE_DIR", DEFAULT_SAMPLE_DIR))
OUTPUT_FILENAME = os.environ.get("REVIEW_OUTPUT_FILENAME", "experience-units-reviewed-v0.2.jsonl")

UNITS_PATH = SAMPLE_DIR / "experience-units-v0.2.jsonl"
OUTPUT_PATH = SAMPLE_DIR / OUTPUT_FILENAME


# ---------------------------------------------------------------------------
# In-memory state
# ---------------------------------------------------------------------------

app = FastAPI(title="Review Workflow Prototype")
app.mount("/static", StaticFiles(directory=str(Path(__file__).parent / "static")), name="static")
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

units: list[dict[str, Any]] = []
units_by_id: dict[str, dict[str, Any]] = {}
anchors: list[dict[str, Any]] = []
anchors_by_unit: dict[str, list[dict[str, Any]]] = {}
decisions: dict[str, dict[str, Any]] = {}


def reload_data() -> None:
    global units, units_by_id, anchors, anchors_by_unit, decisions
    units, anchors, decisions = rw.load_sample(SAMPLE_DIR)
    units_by_id = {u["unit_id"]: u for u in units}
    anchors_by_unit = rw.group_anchors_by_unit(units, anchors)


def save_state() -> None:
    """Persist current in-memory units to the reviewed output file."""
    rw.write_jsonl(OUTPUT_PATH, units)


def unit_for_review(unit_id: str) -> dict[str, Any] | None:
    unit = units_by_id.get(unit_id)
    if unit is None:
        return None
    return unit


def review_unit_ids() -> list[str]:
    """Units that have at least one .needs_review anchor."""
    return [uid for uid, items in anchors_by_unit.items() if items]


@app.on_event("startup")
def startup() -> None:
    reload_data()
    url = "http://127.0.0.1:8765"
    print(f"Loaded {len(units)} units, {len(anchors)} review anchors from {SAMPLE_DIR}")
    print(f"Review UI: {url}")
    # Auto-open browser after a short delay so the server is ready.
    threading.Timer(0.8, lambda: webbrowser.open(url)).start()


# ---------------------------------------------------------------------------
# HTML routes
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    review_ids = review_unit_ids()
    # Show every unit; anchored ones come first so the reviewer sees them immediately.
    def _sort_key(unit: dict[str, Any]) -> tuple[int, str]:
        return (0 if unit["unit_id"] in review_ids else 1, unit["unit_id"])

    sorted_units = sorted(units, key=_sort_key)
    stats = rw.compute_stats(units)
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "units": sorted_units,
            "anchors_by_unit": anchors_by_unit,
            "decisions": decisions,
            "stats": stats,
            "total": len(units),
            "review_count": len(review_ids),
            "sample_dir": str(SAMPLE_DIR),
            "output_path": str(OUTPUT_PATH),
        },
    )


# ---------------------------------------------------------------------------
# JSON API
# ---------------------------------------------------------------------------

@app.get("/api/units")
def list_units(status: str | None = None) -> JSONResponse:
    result = list(units_by_id.values())
    if status:
        result = [u for u in result if u.get("review_status") == status]
    return JSONResponse(result)


@app.get("/api/units/{unit_id}")
def get_unit(unit_id: str) -> JSONResponse:
    unit = unit_for_review(unit_id)
    if unit is None:
        return JSONResponse({"error": "Unit not found"}, status_code=404)
    return JSONResponse(unit)


@app.post("/api/units/{unit_id}/approve")
def approve_unit(unit_id: str) -> JSONResponse:
    unit = unit_for_review(unit_id)
    if unit is None:
        return JSONResponse({"error": "Unit not found"}, status_code=404)
    updated = rw.review(unit, "approved")
    units_by_id[unit_id] = updated
    idx = next(i for i, u in enumerate(units) if u["unit_id"] == unit_id)
    units[idx] = updated
    save_state()
    return JSONResponse({"unit_id": unit_id, "review_status": "approved"})


@app.post("/api/units/{unit_id}/reject")
def reject_unit(unit_id: str) -> JSONResponse:
    unit = unit_for_review(unit_id)
    if unit is None:
        return JSONResponse({"error": "Unit not found"}, status_code=404)
    updated = rw.review(unit, "rejected")
    units_by_id[unit_id] = updated
    idx = next(i for i, u in enumerate(units) if u["unit_id"] == unit_id)
    units[idx] = updated
    save_state()
    return JSONResponse({"unit_id": unit_id, "review_status": "rejected"})


@app.post("/api/units/{unit_id}/edit")
def edit_unit(request: Request, unit_id: str, note: str = Form("")) -> JSONResponse:
    unit = unit_for_review(unit_id)
    if unit is None:
        return JSONResponse({"error": "Unit not found"}, status_code=404)

    # Editing a note moves a draft unit into "reviewed" so it is no longer
    # counted as untouched, but does not auto-approve/reject.
    target_status = "reviewed" if unit.get("review_status") == "draft" else unit.get("review_status", "reviewed")
    updated = rw.review(unit, target_status, note)
    units_by_id[unit_id] = updated
    idx = next(i for i, u in enumerate(units) if u["unit_id"] == unit_id)
    units[idx] = updated
    save_state()
    return JSONResponse({"unit_id": unit_id, "review_status": target_status, "reviewer_notes": note.strip()})


@app.get("/api/state")
def state_summary() -> JSONResponse:
    return JSONResponse(
        {
            "statuses": rw.REVIEW_STATUSES,
            "transitions": {k: sorted(v) for k, v in rw.ALLOWED_TRANSITIONS.items()},
            "stats": rw.compute_stats(units),
            "sample_dir": str(SAMPLE_DIR),
            "output_path": str(OUTPUT_PATH),
        }
    )


@app.post("/api/reload")
def reload() -> RedirectResponse:
    reload_data()
    return RedirectResponse(url="/", status_code=303)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8765)
