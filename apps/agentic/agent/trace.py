import json, time
from pathlib import Path

def append_trace(trace_path: str, step: str, inputs: dict, outputs: dict | None, ms: float, error: str | None = None):
    rec = {
        "ts": round(time.time(), 3),
        "step": step,
        "inputs": inputs,
        "outputs": outputs,
        "latency_ms": round(ms, 3),
        "error": error,
    }
    Path(trace_path).parent.mkdir(parents=True, exist_ok=True)
    with open(trace_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")