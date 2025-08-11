from time import perf_counter

from fastapi import APIRouter
from pydantic import BaseModel
from common.metrics_config import REQS, LAT

tasks_router = APIRouter(prefix="/tasks", tags=["tasks"])

class LeadIn(BaseModel):
    company: str
    website: str
    question: str
    contact: str


@tasks_router.post("/lead")
def create_lead_task(payload: LeadIn):
    # TODO: создать запись в SQLite и вернуть task_id
    t0 = perf_counter()
    try:
        return {"task_id": "t_001", "status": "queued"}
    finally:
        REQS.labels("/tasks/lead").inc()
        LAT.labels("/tasks/lead").observe(perf_counter() - t0)


@tasks_router.get("/{task_id}")
def get_task(task_id: str):
    # TODO: прочитать из SQLite
    t0 = perf_counter()
    try:
        return {"task_id": task_id, "status": "running"}
    finally:
        REQS.labels("/tasks/task_id").inc()
        LAT.labels("/tasks/task_id").observe(perf_counter() - t0)