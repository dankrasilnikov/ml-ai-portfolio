from time import perf_counter

from apps.agentic.common.logging import log
from apps.agentic.app.metrics_config import REQS, LAT
from fastapi import APIRouter
from pydantic import BaseModel

chat_router = APIRouter(prefix="/chat", tags=["chat"])

class ChatIn(BaseModel):
    user_id: str
    message: str


@chat_router.post("")
def chat(inp: ChatIn):
    t0 = perf_counter()
    log("chat_in", user_id=inp.user_id, msg=inp.message)
    try:
        return {
            "user_id": inp.user_id,
            "reply": f"(stub) I heard: {inp.message}",
            "trace_id": "stub_001"
        }
    finally:
        REQS.labels("/chat").inc()
        LAT.labels("/chat").observe(perf_counter() - t0)