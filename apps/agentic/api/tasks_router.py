import uuid
from pathlib import Path
from time import perf_counter

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional
from apps.agentic.agent.graph import run_pipeline
from apps.agentic.app.db import get_db, Task
from apps.agentic.app.metrics_config import REQS, LAT

tasks_router = APIRouter(prefix="/tasks", tags=["tasks"])


class LeadIn(BaseModel):
    company: str
    question: str
    website: Optional[str] = None
    contact: Optional[str] = None


@tasks_router.post("/lead")
def create_lead_task(payload: LeadIn, db: Session = Depends(get_db)):
    t0 = perf_counter()
    tid = f"t_{uuid.uuid4().hex[:8]}"

    traces_dir = Path(__file__).resolve().parents[1] / "data" / "traces"
    traces_dir.mkdir(parents=True, exist_ok=True)
    trace_path = (traces_dir / f"{tid}.jsonl").as_posix()

    task = Task(id=tid, status="queued", trace_path=trace_path)

    db.add(task)
    db.commit()

    try:
        data = payload.model_dump()
        _ = run_pipeline(task_id=tid, trace_path=trace_path, payload=data)

        task.status = "done"
        task.last_error = None
    except Exception as e:
        task.status = "error"
        task.last_error = repr(e)
    finally:
        db.add(task)
        db.commit()

    try:
        return {"task_id": tid, "status": task.status}
    finally:
        REQS.labels("/tasks/lead").inc()
        LAT.labels("/tasks/lead").observe(perf_counter() - t0)


@tasks_router.get("/{task_id}")
def get_task(task_id: str, db: Session = Depends(get_db)):
    t0 = perf_counter()
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="task not found")

    try:
        return {
            "task_id": task.id,
            "status": task.status,
            "created_at": task.created_at.isoformat(),
            "last_error": task.last_error,
            "trace_path": task.trace_path,
        }
    finally:
        REQS.labels("/tasks/task_id").inc()
        LAT.labels("/tasks/task_id").observe(perf_counter() - t0)
