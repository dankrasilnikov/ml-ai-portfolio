import json, time, sys

def log(event: str, **kw):
    rec = {"ts": round(time.time(),3), "event": event, **kw}
    sys.stdout.write(json.dumps(rec, ensure_ascii=False) + "\n")
    sys.stdout.flush()