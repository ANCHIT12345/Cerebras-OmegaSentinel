"""Bridge: run async run_omega in a worker thread, yield its events to a sync (Streamlit) consumer."""
import threading
import queue
import asyncio
from typing import Iterator, Dict, Any, Optional


def run_omega_streamed(orch, scenario, telemetry, images, evidence: Optional[dict] = None) -> Iterator[Dict[str, Any]]:
    """Yield event dicts from run_omega. Terminal {"type":"done","results":{...}} carries final results.
    On failure yields {"type":"error","error":str}."""
    q: "queue.Queue[dict]" = queue.Queue()
    SENTINEL = {"type": "_end"}

    def worker():
        async def go():
            results = await orch.run_omega(
                scenario, telemetry, images, evidence=evidence, event_cb=q.put
            )
            q.put({"type": "done", "results": results})
        try:
            asyncio.run(go())
        except Exception as e:  # noqa: BLE001 — surface any failure to the UI thread
            q.put({"type": "error", "error": str(e)})
        finally:
            q.put(SENTINEL)

    t = threading.Thread(target=worker, daemon=True)
    t.start()
    while True:
        ev = q.get()
        if ev is SENTINEL:
            break
        yield ev
    t.join(timeout=1)


if __name__ == "__main__":
    # self-check: fake orchestrator emits 3 token events then returns results
    class _Fake:
        async def run_omega(self, *a, evidence=None, event_cb=None, **k):
            for i in range(3):
                event_cb({"type": "token", "agent": "X", "delta": str(i)})
            return {"ok": True}

    evs = list(run_omega_streamed(_Fake(), "s", None, {}))
    assert [e["type"] for e in evs] == ["token", "token", "token", "done"], evs
    assert evs[-1]["results"] == {"ok": True}
    print("OK streaming bridge")
