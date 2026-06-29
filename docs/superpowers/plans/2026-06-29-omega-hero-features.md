# Omega Hero Features Implementation Plan

> **For agentic workers:** Implement task-by-task. Steps use checkbox (`- [ ]`) syntax. Repo is NOT git — skip commit steps; verify via the `__main__` self-check in each new module instead.

**Goal:** Add live-streaming war room, GPU ghost race, shareable verdict card, and honest OCR-multimodal to Sentinel Omega for the Cerebras hackathon.

**Architecture:** Add a streaming generator to the API client; bridge async orchestrator → Streamlit via a thread+queue so debate tokens render live in parallel cards. Ghost race + verdict card are pure post-run rendering (no API). OCR is upload-time preprocessing feeding extracted text to gemma-4-31b.

**Tech Stack:** Python, Streamlit 1.58, `cerebras-cloud-sdk` (AsyncCerebras), Pillow (present), RapidOCR (new, optional).

## Global Constraints

- Inference model: **gemma-4-31b ONLY**. No other inference model. (`MODEL` env.)
- `event_cb=None` MUST preserve today's blocking behavior — `benchmarks/speed_test.py` and `tests/test_multimodal.py` keep passing unchanged.
- No UI copy may claim the model "sees" images. Multimodality = OCR preprocessing only.
- New deps optional with graceful fallback; never hard-crash if RapidOCR missing.

---

### Task 1: Streaming API call

**Files:**
- Modify: `core/api.py`

**Interfaces:**
- Produces: `async def call_gemma_stream(system_prompt, user_text, images=None, reasoning_effort="medium", max_tokens=4096, on_delta=None) -> str` — streams via `stream=True`, calls `on_delta(text)` per chunk, returns full accumulated text. No `json_schema` (free-text only).

- [ ] **Step 1:** Add `call_gemma_stream` to `core/api.py`:

```python
async def call_gemma_stream(
    system_prompt: str,
    user_text: str,
    images: Optional[List[str]] = None,
    reasoning_effort: str = "medium",
    max_tokens: int = 4096,
    on_delta=None,
) -> str:
    """Streaming variant of call_gemma. Calls on_delta(str) per token chunk; returns full text."""
    if images:
        user_text = f"[{len(images)} image(s) attached as evidence]\n\n{user_text}"
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_text})
    kwargs: Dict[str, Any] = {
        "model": settings.MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "stream": True,
    }
    if reasoning_effort in ("low", "medium", "high"):
        kwargs["reasoning_effort"] = reasoning_effort
    parts = []
    try:
        stream = await client.chat.completions.create(**kwargs)
        async for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            if delta:
                parts.append(delta)
                if on_delta:
                    on_delta(delta)
    except Exception as e:
        logger.error(f"Stream call failed: {e}")
        raise
    return "".join(parts)
```

- [ ] **Step 2:** Verify import compiles: `python -c "import core.api"` (from `sentinel-omega/`, venv active). Expected: no error.

---

### Task 2: Thread+queue streaming bridge

**Files:**
- Create: `core/streaming.py`

**Interfaces:**
- Consumes: `OmegaOrchestrator.run_omega(..., event_cb=...)` (Task 3).
- Produces: `def run_omega_streamed(orch, scenario, telemetry, images, evidence=None) -> Iterator[dict]` — yields event dicts; the terminal `{"type":"done","results":{...}}` carries the final results.

- [ ] **Step 1:** Create `core/streaming.py`:

```python
"""Bridge: run async run_omega in a worker thread, yield its events to a sync (Streamlit) consumer."""
import threading
import queue
import asyncio
from typing import Iterator, Dict, Any, Optional


def run_omega_streamed(orch, scenario, telemetry, images, evidence: Optional[dict] = None) -> Iterator[Dict[str, Any]]:
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
        except Exception as e:
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
```

- [ ] **Step 2:** Run self-check: `python -m core.streaming`. Expected: `OK streaming bridge`.

---

### Task 3: Orchestrator emits events + accepts OCR evidence

**Files:**
- Modify: `agents/orchestrator.py`

**Interfaces:**
- Consumes: `call_gemma_stream` (Task 1).
- Produces: `run_omega(scenario, telemetry, images, evidence=None, event_cb=None)`. When `event_cb` set, divergence + mediation stream via `call_gemma_stream` with `on_delta` emitting `{"type":"token","agent":name,"delta":str}`; each non-streamed stage emits `{"type":"stage","name":str,"seconds":float}`. `evidence: dict[image_key,str]` injected into divergence prompts.

- [ ] **Step 1:** Add `from core.api import call_gemma_stream` and `Callable` import.

- [ ] **Step 2:** Change signature: `async def run_omega(self, scenario, telemetry, images, evidence=None, event_cb=None)`. Store `self._event_cb = event_cb` and `self._evidence = evidence or {}` at top.

- [ ] **Step 3:** After each existing `timings[...]` assignment for the structured stages (monte_carlo, mediation, compliance, temporal, economics, causal_chain, self_critique), add:

```python
if event_cb: event_cb({"type": "stage", "name": "<stage>", "seconds": timings["<stage>"]})
```

- [ ] **Step 4:** In `_call_agent`, add `stream: bool = False` param. When `stream and self._event_cb`:

```python
def _delta(d, _n=name):
    self._event_cb({"type": "token", "agent": _n, "delta": d})
text = await call_gemma_stream(
    persona["system_prompt"], user_text, images=image_uris,
    reasoning_effort=persona.get("reasoning_effort", "high"),
    max_tokens=settings.MAX_TOKENS, on_delta=_delta,
)
```
else keep the existing `call_gemma` path. (Wrap both in the existing try/except + veto detection + audit_logger.log_event.)

- [ ] **Step 5:** In `_run_divergence`, pass `stream=True` to `_call_agent`, and inject evidence into `user_text`:

```python
ev_text = self._evidence.get(persona["image_key"], "") if persona["image_key"] else ""
if ev_text:
    user_text += f"\n\nEVIDENCE EXTRACTED FROM YOUR IMAGE (OCR):\n{ev_text[:1500]}"
```

- [ ] **Step 6:** In `_run_mediation`, pass `stream=True` to its `_call_agent` call.

- [ ] **Step 7:** Verify non-streaming path intact: `python -c "import agents.orchestrator"`. Expected: no error. (Full run tested via dashboard in Task 7.)

---

### Task 4: GPU ghost race component

**Files:**
- Modify: `ui/components/speed_compare.py`

**Interfaces:**
- Produces: `def ghost_race(real_seconds: float, real_tokens: int, gpu_tps: float = 60.0)` — renders two-bar HTML race + verdict. `projected = real_tokens/gpu_tps; speedup = projected/real_seconds`.

- [ ] **Step 1:** Append `ghost_race` to `speed_compare.py`. Bars via `st.markdown(unsafe_allow_html=True)` with CSS keyframe widths (Cerebras bar 100% fast, ghost `100*real_seconds/projected`% over same duration). Verdict line: `f"{real_seconds:.1f}s vs projected {projected:.0f}s · {speedup:.1f}× faster"`.

- [ ] **Step 2:** Add `__main__` assert: `projected = 6000/60 == 100`; `speedup = 100/9 ≈ 11.1`. `python -m ui.components.speed_compare` prints `OK ghost`.

---

### Task 5: Verdict card PNG

**Files:**
- Create: `core/verdict_card.py`

**Interfaces:**
- Produces: `def render_verdict_png(results: dict) -> bytes` — 1200×630 PNG via Pillow.

- [ ] **Step 1:** Create `core/verdict_card.py`. Draw dark card (bg `#0A0C10`), title "OMEGA VERDICT", net $ impact (`results["economics"].net_impact`), avg confidence, agent veto count, `gemma-4-31b · Cerebras` badge. Use `PIL.ImageDraw`, default font fallback (`ImageFont.load_default()` if truetype missing). Return PNG bytes via `BytesIO`.

- [ ] **Step 2:** `__main__` self-check: render from stub dict (minimal `economics` object with `net_impact`), assert bytes start with `b"\x89PNG"`. `python -m core.verdict_card` prints `OK verdict`.

---

### Task 6: OCR evidence extraction

**Files:**
- Create: `core/ocr.py`
- Modify: `requirements.txt` (note optional dep)

**Interfaces:**
- Produces: `def extract_evidence(image) -> str` — accepts PIL Image / path / bytes; returns extracted text or `""` on any failure/missing dep.

- [ ] **Step 1:** Create `core/ocr.py` using RapidOCR, lazy-imported inside the function, whole body in try/except returning `""` on failure. Cache the engine in a module global.

```python
"""Local OCR so gemma-4-31b reasons over real image text. Honest multimodality; the LLM never sees pixels."""
import io
import numpy as np  # rapidocr pulls numpy
from PIL import Image

_engine = None

def extract_evidence(image) -> str:
    global _engine
    try:
        from rapidocr_onnxruntime import RapidOCR
        if _engine is None:
            _engine = RapidOCR()
        if isinstance(image, (bytes, bytearray)):
            image = Image.open(io.BytesIO(image))
        elif isinstance(image, str):
            image = Image.open(image)
        arr = np.array(image.convert("RGB"))
        result, _ = _engine(arr)
        if not result:
            return ""
        return "\n".join(line[1] for line in result)[:2000]
    except Exception:
        return ""
```

- [ ] **Step 2:** Add to `requirements.txt`: `rapidocr-onnxruntime  # optional: OCR multimodal evidence`.

- [ ] **Step 3:** `__main__` self-check: build a PIL image with known text via `ImageDraw`, run `extract_evidence`, assert known word present OR print skip if RapidOCR not installed. `python -m core.ocr`.

---

### Task 7: Dashboard wiring (streaming cards, ghost, verdict, OCR, badge)

**Files:**
- Modify: `ui/dashboard.py`

**Interfaces:**
- Consumes: `run_omega_streamed` (Task 2), `ghost_race` (Task 4), `render_verdict_png` (Task 5), `extract_evidence` (Task 6).

- [ ] **Step 1:** Imports: `from core.streaming import run_omega_streamed`, `from core.verdict_card import render_verdict_png`, `from core.ocr import extract_evidence`, `from ui.components.speed_compare import ghost_race`.

- [ ] **Step 2:** On image upload (in the `if run_btn:` encode block), after building `images`, build `evidence = {k: extract_evidence(base64-or-file) for ...}`. Set `vision_live = any(evidence.values())`. Store both in session_state.

- [ ] **Step 3:** Replace the fake `_stage(...)` block + blocking `asyncio.run(orch.run_omega(...))` with the streamed consumer:
  - Create 4 `st.empty()` agent-card placeholders (Operator/Diplomat/Red Team/Compliance) + 1 `st.empty()` for swarm t/s + 1 for current stage.
  - Maintain `buffers = {name: ""}`, `start = time.time()`, `tok = 0`.
  - `for ev in run_omega_streamed(orch, scenario, telemetry, images, evidence):` handle `token` (append delta to buffer, `tok+=len(delta)//4 or 1`, re-render that agent card, update swarm t/s = `tok/(time.time()-start)`), `stage` (update stage line), `done` (`results = ev["results"]`), `error` (`st.error`; `st.stop()`).

- [ ] **Step 4:** Honesty badge near results header: `st.caption("VISION: OCR live" if vision_live else "VISION: evidence noted (no text found)")`.

- [ ] **Step 5:** In speed section, after `show_speed_comparison(total_time)`, add `ghost_race(total_time, est_tokens, gpu_tps=60)` where `est_tokens = sum(len(d["text"]) for d in results["divergence"])//4 + 2000`.

- [ ] **Step 6:** In Downloads section add: `st.download_button("📤 Download Verdict Card (PNG)", data=render_verdict_png(results), file_name="omega_verdict.png", mime="image/png")`.

- [ ] **Step 7:** Manual smoke: `streamlit run ui/dashboard.py`, trigger a sim. Expected: agent cards fill live, swarm t/s ticks, stages advance, ghost race + verdict download appear, no crash. (Needs valid `CEREBRAS_API_KEY`.)

---

## Self-Review

- **Spec coverage:** F1 streaming → T1/T2/T3/T7. F2 ghost → T4/T7. F3 verdict → T5/T7. F4 OCR multimodal → T6/T3(inject)/T7(badge). ✓
- **Backward compat:** `event_cb=None` default preserves blocking path (T3). ✓
- **Type consistency:** `run_omega_streamed` yields events consumed in T7; `event_cb=q.put` matches event dict shapes; `render_verdict_png/ghost_race/extract_evidence` signatures match call sites. ✓
- **Self-checks:** every new module (streaming, verdict_card, ocr) + speed_compare has a `__main__` assert. ✓
- **Risk:** thread+queue bridge (T2) and RapidOCR install (T6) — both have fallbacks noted in spec.
