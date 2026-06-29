# Sentinel Omega — Hackathon Hero Features

**Date:** 2026-06-29
**Goal:** Add unique, judge-winning features across all 3 Cerebras hackathon tracks (Multiverse Agents, People's Choice, Enterprise Impact) in a single working day.
**Hard constraint:** Inference is **gemma-4-31b only**. The hackathon exists to showcase gemma-4-31b. No other model (no vision model) may be used for inference.

---

## Why these features

Rival projects lean on 3D eye-candy and toy speed races. Cerebras's identity is **speed**. Sentinel Omega already has the substance (5-agent debate, Monte Carlo, temporal, economics, causal chain). What it lacks:

1. The speed is **invisible** — the current progress bar fires all 6 stage labels instantly *before* the real `asyncio.run`, so it's theater, not measurement (`ui/dashboard.py:481-486`).
2. Streaming exists in the SDK (`AsyncCerebras`, `stream=True`) but is unused — everything blocks.
3. The README sells "multimodal vision," but `core/api.py:39-42` turns image uploads into a text note because the model can't see them. A judge testing this sinks the Multiverse track.

Four features fix all of the above.

---

## Feature 1 — Live Streaming War Room (centerpiece)

**What:** Replace the fake progress bar with real token-by-token streaming of the **debate** stages — the 4 divergence agents (parallel) and the CEO mediation. Each agent card fills live; a global **swarm tokens/sec** counter ticks at 1500+. Structured stages (Monte Carlo, temporal, economics, causal, critique) keep **real** per-stage timings.

**Why debate-only:** divergence + mediation are free-text (no `response_format` JSON schema) → cleanly streamable. The JSON-schema stages don't stream meaningfully and aren't the visual money-shot. Scope the streaming to where it pays off.

**Components:**
- `core/api.py` → new `call_gemma_stream(...)` async generator. Same args as `call_gemma` minus `json_schema`. Sets `stream=True`, yields content deltas (`chunk.choices[0].delta.content`). Accumulates full text and returns it via a final sentinel or an out-param so callers still get the complete string for downstream stages.
- `agents/orchestrator.py` → `run_omega` gains optional `event_cb: Callable[[dict], None] = None`. When set, `_call_agent` for divergence/mediation uses `call_gemma_stream` and emits events `{"type":"token","agent":name,"delta":str,"t_per_s":float}`, plus `{"type":"stage","name":...,"seconds":float}` for non-streamed stages and `{"type":"done",...}`. When `event_cb` is None, behaviour is identical to today (non-streaming) — backward compatible, keeps `benchmarks/` and `tests/` working.
- `core/streaming.py` → thread+queue bridge. `run_omega_streamed(orchestrator, args...) -> Iterator[dict]`: spawns a worker thread that runs `asyncio.run(run_omega(..., event_cb=queue.put))`, main thread yields from the `queue.Queue` until a `done` event carrying the final results dict. This is the only non-trivial piece.
- `ui/dashboard.py` → run block consumes the iterator: 4 `st.empty()` agent-card placeholders + 1 metric placeholder for swarm t/s. On `token` events, append delta to that agent's buffer and re-render its card. On `done`, store results to `session_state` and render the existing results sections (already wired from the earlier session-state fix).

**Ceiling / fallback (`// ponytail:`):** if the thread+queue bridge is flaky in the installed Streamlit (1.58), fall back to **sequential** streaming — agents stream one card at a time via `st.write_stream`. Lower risk, still visually strong. Decision made at implementation time based on a smoke test.

**Self-check:** `core/streaming.py` ships a `__main__` that runs a fake 3-event producer through the bridge and asserts the consumer receives them in order ending with `done`. No live API needed.

---

## Feature 2 — GPU Ghost Race

**What:** A post-run replay animation in the speed section. Two bars race using the **real** measured tokens and wall-time: the Cerebras bar zooms to 100%; a GPU ghost bar (fixed conservative baseline, default 60 t/s) crawls. Ends on a verdict like `9.1s vs projected 94s · 10.3× faster`.

**Why post-run replay, not live:** deterministic, no streaming-sync complexity, reliably screenshot-able for the demo video. Zero API cost.

**Components:**
- `ui/components/speed_compare.py` → extend (or add `ghost_race(real_tokens, real_seconds, gpu_tps=60)`): renders the two-bar race. Implementation is a short HTML/CSS block with a keyframed width animation injected via `st.markdown(unsafe_allow_html=True)`, plus the numeric verdict. Total tokens come from summing streamed token counts; if unavailable, estimate from output character counts (`chars/4`).

**Self-check:** trivial math (`speedup = projected_gpu_seconds / real_seconds`); a one-line `assert` in `__main__` that 6000 tokens at real 9s vs 60 t/s gives ~11× guards the formula.

---

## Feature 3 — Shareable Verdict Card

**What:** One-click PNG "Omega Verdict" card — strategy headline, net $ impact, confidence, agent vote summary, total t/s, Cerebras + gemma-4-31b badge. Built for dropping into a tweet / Devpost submission. Drives People's Choice virality.

**Components:**
- `core/verdict_card.py` → `render_verdict_png(results: dict) -> bytes`. Pure **Pillow** (already a dep): draws a dark-theme 1200×630 (OG image size) card with the SOC palette. Returns PNG bytes.
- `ui/dashboard.py` → `st.download_button("📤 Download Verdict Card (PNG)", data=render_verdict_png(results), file_name="omega_verdict.png", mime="image/png")` in the Downloads section.

**Why Pillow not Plotly/kaleido:** no new dependency, full layout control, deterministic output. 1200×630 = standard social/OG card size.

**Self-check:** `__main__` renders a card from a stub results dict and asserts the output is non-empty PNG bytes (magic header `\x89PNG`).

---

## Feature 4 — Honest Multimodal (gemma-4-31b only)

**Constraint:** gemma-4-31b is text-only and is the only allowed inference model. Real multimodality must therefore live in **preprocessing**, not the LLM — OCR the uploaded images locally and feed the *real extracted text* (log lines, dashboard metrics, tweet text, diagram labels) into the agents. This is a legitimate, honest multimodal pipeline: images genuinely change the agents' reasoning, and gemma-4-31b stays the sole model.

**Components:**
- `core/ocr.py` → `extract_evidence(image_bytes_or_uri) -> str`. Uses **RapidOCR** (`rapidocr-onnxruntime`, pip-only, no system binary, cross-platform). Returns extracted text, truncated to a sane length. Wrapped in try/except: if the dep is missing or OCR fails, returns `""`.
- `ui/dashboard.py` → on upload, run OCR per image; store extracted text alongside the base64 in the images dict (or a parallel `evidence_text` dict).
- `agents/orchestrator.py` `_run_divergence` → inject the per-role extracted evidence text into each agent's `user_text` (replacing today's "cannot be processed" note when text was extracted).
- `core/api.py:39-42` → keep the text-note fallback ONLY for the no-OCR-text case, reworded to be accurate ("evidence text extracted via OCR" vs nothing).
- **Honesty badge** in the UI: `VISION: OCR live` when evidence text was extracted, `VISION: evidence noted (no text found)` otherwise. Never claims the model "sees" images.

**Ceiling / fallback (`// ponytail:`):** RapidOCR is the one new dependency and the install is the only risk. If it won't install cleanly in the time box, this feature degrades to the honest badge + the accurate text note — no false claim either way. Marked optional in `requirements.txt` (separate `requirements-ocr.txt` or a commented line).

**Self-check:** `core/ocr.py` `__main__` runs `extract_evidence` on a Pillow-generated image containing known text and asserts the known words appear (skips with a clear message if RapidOCR isn't installed).

---

## Architecture summary

| File | Change |
|---|---|
| `core/api.py` | + `call_gemma_stream()` generator; reword image fallback note |
| `core/streaming.py` | **new** — thread+queue bridge `run_omega_streamed()` + self-check |
| `core/verdict_card.py` | **new** — Pillow PNG card + self-check |
| `core/ocr.py` | **new** — RapidOCR `extract_evidence()` + self-check |
| `agents/orchestrator.py` | optional `event_cb`; stream divergence+mediation; inject OCR text |
| `ui/dashboard.py` | consume streamed events into live cards; ghost race; verdict download; OCR on upload; honesty badge |
| `ui/components/speed_compare.py` | + `ghost_race()` |
| `requirements.txt` | OCR dep noted as optional |

**Backward compatibility:** `event_cb=None` preserves today's blocking path, so `benchmarks/speed_test.py` and `tests/test_multimodal.py` keep working unchanged.

## Build order
1. `call_gemma_stream` + `core/streaming.py` bridge (+ smoke test) — unblocks the centerpiece.
2. Dashboard live war-room wiring.
3. GPU ghost race.
4. Verdict card.
5. OCR multimodal (last — only new dependency, has a clean fallback).

## Out of scope (YAGNI)
- Streaming the JSON-schema stages.
- Live (vs replay) GPU race.
- A real vision model (explicitly disallowed by the gemma-4-31b constraint).
- Any new 3D/WebGL visualization — rivals already own that lane; speed is the differentiator.

## Notes
- Repo is not a git repository, so the spec is written but not committed. Run `git init` if version control is wanted.
