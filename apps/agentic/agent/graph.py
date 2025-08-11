from __future__ import annotations
from typing import TypedDict, Literal
from time import perf_counter
from langgraph.graph import StateGraph, START, END
from apps.agentic.app.metrics_config import AGENT_STEP_LATENCY
from .trace import append_trace

class State(TypedDict, total=False):
    task_id: str
    mode: Literal["lead_research","qa"]
    input: dict
    plan: list
    reply: str
    trace_path: str

def _step(name):
    def wrap(fn):
        def inner(state: State) -> State:
            t0 = perf_counter()
            err = None
            out_state = state
            try:
                out_state = fn(state) or state
                return out_state
            except Exception as e:
                err = repr(e)
                raise
            finally:
                dt = perf_counter() - t0
                AGENT_STEP_LATENCY.labels(name).observe(dt)
                # Для трейса берём минимальный inputs/outputs
                inputs = {"task_id": state.get("task_id"), "mode": state.get("mode")}
                outputs = {k: out_state.get(k) for k in ("plan","reply") if k in out_state}
                append_trace(state["trace_path"], name, inputs, outputs, ms=dt*1000, error=err)
        return inner
    return wrap


@_step("listener")
def listener(state: State) -> State:
    st = dict(state)
    st.setdefault("mode", "lead_research")
    st.setdefault("plan", [])
    return st

@_step("router")
def router(state: State) -> State:
    st = dict(state)
    inp = st.get("input") or {}
    st["mode"] = "lead_research" if inp.get("question") else "qa"
    st["plan"] = [{"step": "draft_reply"}]
    return st

@_step("reply")
def reply(state: State) -> State:
    st = dict(state)
    c = (st.get("input") or {}).get("company","ACME")
    q = (st.get("input") or {}).get("question","—")
    st["reply"] = f"[stub] Company={c}; Answer to: {q}"
    return st


def build_graph():
    g = StateGraph(State)
    g.add_node("listener", listener)
    g.add_node("router", router)
    g.add_node("reply", reply)
    g.add_edge(START, "listener")
    g.add_edge("listener", "router")
    g.add_edge("router", "reply")
    g.add_edge("reply", END)
    return g.compile()


graph = build_graph()

def run_pipeline(task_id: str, trace_path: str, payload: dict) -> dict:
    init_state: State = {"task_id": task_id, "trace_path": trace_path, "input": payload}
    final = graph.invoke(init_state)
    return final