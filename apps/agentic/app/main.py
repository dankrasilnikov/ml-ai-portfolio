from fastapi import FastAPI
from pydantic import BaseModel
from common.logging import log
import os

app = FastAPI(title="agentic-core")

class ChatIn(BaseModel):
    user_id: str
    message: str

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/chat")
def chat(inp: ChatIn):
    log("chat_in", user_id=inp.user_id, msg=inp.message)
    return {
        "user_id": inp.user_id,
        "reply": f"(stub) I heard: {inp.message}",
        "trace_id": "stub_001"
    }