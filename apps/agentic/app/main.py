from time import perf_counter

from apps.agentic.common.logging import log
from .db import init_db
from apps.agentic.app.metrics_config import REQS, LAT
from fastapi import FastAPI
from pydantic import BaseModel
from apps.agentic.api.tasks_router import tasks_router
from apps.agentic.api.metrics_router import metrics_router
from apps.agentic.api.chat_router import chat_router

app = FastAPI(title="agentic-core")


@app.on_event("startup")
def _startup():
    init_db()
    log(f"[DB] init OK")

API_VERSION_PREFIX = "/api/v1"

app.include_router(tasks_router, prefix=API_VERSION_PREFIX)
app.include_router(metrics_router, prefix=API_VERSION_PREFIX)
app.include_router(chat_router, prefix=API_VERSION_PREFIX)

class ChatIn(BaseModel):
    user_id: str
    message: str


@app.get("/health")
def health():
    t0 = perf_counter()
    try:
        return {"ok": True}
    finally:
        REQS.labels("/health").inc()
        LAT.labels("/health").observe(perf_counter() - t0)


