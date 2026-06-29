# 🛡️ SENTINEL OMEGA

### Predictive Business Equilibrium Engine — Multimodal Multiverse Agents on Cerebras

> _Most agent systems are chatbots in a circle. Sentinel Omega ingests live enterprise telemetry and OCR'd visual evidence, streams a 5-agent debate at 1500+ tokens/sec on Cerebras, runs Monte Carlo across parallel universes, resolves competing corporate incentives via game theory, vetoes its own solutions against regulatory compliance, simulates the future to prevent side effects, and outputs a boardroom-ready financial impact report with an auditable causal chain._

> **All inference runs on `gemma-4-31b` via Cerebras — one model, no exceptions.** Images are OCR'd locally (RapidOCR) and the extracted text feeds the agents; the LLM stays text-only and honest.

---

## 📌 What Is It?

**Sentinel Omega** is an AI-powered **crisis war room** that simulates the human decision-making process during a high-stakes production incident — but runs it in **seconds instead of hours**.

Instead of asking one LLM "how do I fix this?", it spawns **five competing AI agents**, each with a different corporate incentive (reliability, brand, adversarial risk, legal compliance, executive mediation), OCRs your actual screenshots (dashboards, architecture diagrams, tweets, log images) and feeds each agent the extracted text, then lets them **debate, veto, and synthesize** until they find a solution where no stakeholder's KPI is destroyed — a **Nash Equilibrium**.

It then **time-travels** — simulating the state of the business at T+1 hour, T+24 hours, and T+7 days — to verify the fix doesn't create a bigger problem later. If the future fails, it re-debates.

---

## 🧠 Why Does This Exist?

### The Real Problem

When production crashes at 3 AM, a war room forms. Four people scream four different fixes:

| Person | Wants | Risk |
|---|---|---|
| **SRE** | Shut down features to save the DB | Users locked out |
| **Brand Lead** | Keep features live, apologize publicly | System collapses |
| **Security** | Check GDPR/SOC2 before any fix | Delays resolution |
| **CEO** | Status updates every 15 min | Distracts engineers |

They argue for **2–4 hours**. Money burns. Customers churn. Nobody wins.

### The Omega Solution

Turn that war room into **5 AI agents** that complete the same debate in **~9 seconds** — with structured reasoning, regulatory compliance, financial impact, and a downloadable post-mortem.

---

## 🏗️ How Is It Better Than General Solutions?

### vs. Single LLM Call (ChatGPT / Claude / Gemini web)

| Dimension | Single LLM Call | Sentinel Omega |
|---|---|---|
| **Perspectives** | One model, one opinion | 5 competing agents with different KPIs |
| **Critique** | Trusts its own first answer | Red Team agent tries to break every plan |
| **Compliance** | Might mention GDPR | Dedicated Compliance agent can VETO and force a redo |
| **Future Impact** | No temporal reasoning | Simulates T+1h, T+24h, T+7d; re-debates if future fails |
| **Financial Cost** | Says "this is bad" | Calculates exact $ downtime, fix cost, brand damage, net impact |
| **Explainability** | Black box | Full causal chain: root cause → cascade → resolution |
| **Self-Awareness** | Confidence theatre | Self-critique with 0–10 scores across 4 dimensions |
| **Memory** | Stateless | SQLite institutional memory — learns from every incident |
| **Multimodal** | Some models handle images | Images OCR'd locally; each agent reads the real extracted text for its role |
| **Speed (visible)** | Spinner, then a wall of text | Agents stream their thinking live at 1500+ tok/s; you watch the debate happen |
| **Speed** | Fast but shallow | 9 seconds for 12-stage recursive loop on Cerebras |

### vs. Traditional Monitoring Tools (Datadog, PagerDuty, Splunk)

| Dimension | Traditional Tools | Sentinel Omega |
|---|---|---|
| **What they do** | Show you the fire | Show the fire + debate the fix + predict the fallout |
| **Output** | Dashboards + alerts | Strategy + compliance check + financial impact + post-mortem |
| **Decision support** | "Page the on-call" | "Here's the plan, here's why, here's what happens if you don't" |
| **Cross-functional** | SRE-only | SRE + Brand + Legal + Executive mediation in one pass |
| **Post-incident** | Manual post-mortem writing | Auto-generated downloadable report |

---

## ⚡ Signature Features (what makes the speed *visible*)

Cerebras's whole identity is speed — so Sentinel Omega makes it visceral, not a hidden number:

- **⚡ Live Streaming War Room** — the 4 stakeholder agents + the CEO arbitrator stream their reasoning **token-by-token, in parallel**, straight into the UI. A global **swarm tokens/sec** counter ticks past 1500. You don't wait for an answer — you watch five minds argue a crisis in real time. (`gemma-4-31b` emits reasoning tokens via `delta.reasoning`; we stream them live and return the final answer for the debate logic.)
- **🐌 GPU Ghost Race** — a side-by-side replay: the Cerebras bar finishes the 12-stage pipeline while a standard-GPU "ghost" (≈60 tok/s) is still crawling through stage 2. Ends on `9.1s vs projected 94s · 10.3× faster`.
- **📤 Shareable Verdict Card** — one click renders a 1200×630 PNG "Omega Verdict" (net $ impact, agent votes, self-critique score, tok/s, `gemma-4-31b · Cerebras` badge) built for dropping straight into a tweet or Devpost.
- **🔎 Honest Multimodal (OCR)** — uploads (dashboards, logs, tweets, diagrams) are OCR'd locally with RapidOCR; the **real extracted text** is injected into the relevant agent. The model never pretends to "see" pixels. A `VISION: OCR live` badge shows when real text was extracted.

---

## 🔄 The 12-Stage Pipeline

```
┌──────────────────────────────────────────────────────────────┐
│                    SENTINEL OMEGA PIPELINE                    │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  1. TELEMETRY INPUT                                          │
│     Hard metrics (CPU, latency, errors)                      │
│     Soft metrics (sentiment, social volume, churn risk)      │
│     → Agent voting weights (who gets the most say)           │
│                    ↓                                         │
│  2. MONTE CARLO BURST                                        │
│     5–10 parallel simulations with randomized variations     │
│     → Probability distribution (47/50 fix works)             │
│                    ↓                                         │
│  3. MULTIMODAL DIVERGENCE                                    │
│     ⚙️ Operator (SRE)      — reads dashboard screenshot      │
│     🌐 Diplomat (Brand)    — reads angry tweets image        │
│     🔴 Red Team (Adversary)— reads architecture diagram      │
│     🏛️ Compliance (Legal)  — reads error log image           │
│     Each agent proposes or vetoes based on its KPI          │
│                    ↓                                         │
│  4. CEO MEDIATION                                            │
│     ⚖️ Arbitrator finds Nash Equilibrium                     │
│     Explicitly addresses every VETO                          │
│     → Draft Plan v1                                          │
│                    ↓                                         │
│  5. COMPLIANCE VETO CHECK                                    │
│     GDPR / SOC2 validation                                   │
│     If VETO → re-mediate (loop back to Stage 4)              │
│                    ↓                                         │
│  6. TEMPORAL SIMULATION                                      │
│     T+1 Hour  — immediate technical impact                   │
│     T+24 Hours — short-term market reaction                  │
│     T+7 Days  — long-term brand + tech debt                  │
│     If any FAIL → re-mediate with future feedback             │
│                    ↓                                         │
│  7. ECONOMIC IMPACT                                          │
│     $ cost_of_downtime + $ cost_of_fix                       │
│     $ brand_damage + $ revenue_recovered → $ net_impact      │
│                    ↓                                         │
│  8. CAUSAL CHAIN (XAI)                                       │
│     Root cause → cascade events → final impact               │
│     → Where the fix breaks the chain                         │
│                    ↓                                         │
│  9. SELF-CRITIQUE                                            │
│     Scores 0–10: Technical / Cultural / Economic / Temporal  │
│     Radar chart + recommended improvement                    │
│                    ↓                                         │
│ 10. INSTITUTIONAL MEMORY                                     │
│     SQLite: save crisis → resolution → effectiveness         │
│     Next incident searches past resolutions                 │
│                    ↓                                         │
│ 11. POST-MORTEM GENERATION                                   │
│     Formal incident report in Markdown                       │
│     Executive summary + root cause + timeline + scores       │
│                    ↓                                         │
│ 12. OUTPUT                                                   │
│     Final Hardened Strategy + Audit Trail (JSON)            │
│     + Post-Mortem (Markdown download)                       │
│                                                              │
│  *** ALL POWERED BY gemma-4-31b ON CEREBRAS ***              │
│  *** FULL PIPELINE: ~9 SECONDS ***                           │
└──────────────────────────────────────────────────────────────┘
```

---

## 🎭 The Five Agents

| Agent | Emoji | Role | KPI | Veto Power | Image Focus |
|---|---|---|---|---|---|
| **Operator** | ⚙️ | Site Reliability Engineer | Uptime ≥ 99.99% | `HARD_VETO` if plan risks total blackout | Dashboard screenshot |
| **Diplomat** | 🌐 | Brand Custodian | NPS ≥ 50, Churn < 5% | `BRAND_VETO` if plan is deceptive | Twitter screenshot |
| **Red Team** | 🔴 | Adversarial Auditor | Find the Single Point of Failure | `SYSTEMIC_VETO` if hidden failure detected | Architecture diagram |
| **Compliance** | 🏛️ | Legal Gatekeeper | GDPR / SOC2 adherence | `REGULATORY_VETO` if regulation violated | Error log image |
| **Arbitrator** | ⚖️ | CEO / Mediator | Nash Equilibrium (no KPI destroyed) | `FINAL_AUTHORITY` (binding) | All images |

### How the Debate Works

1. All 4 non-CEO agents run in **parallel** (`asyncio.gather`)
2. Each sees the image relevant to their role + the telemetry + Monte Carlo results
3. Each proposes a solution or issues a VETO
4. The Arbitrator reads all 4 positions + all images, finds the **Nash Equilibrium**, explicitly resolves every VETO
5. If Compliance vetoes, the Arbitrator re-mediates and the fix is re-checked
6. If the temporal simulation predicts a future failure, the Arbitrator re-mediates again

---

## 📊 Key Features

### 🎲 Monte Carlo Multiverse Burst
Runs 5–10 parallel simulations with randomized crisis variations ("What if the JP market starts trending #Boycott?", "What if the DB fails over successfully?"). Returns a probability distribution: *"47 out of 50 simulations show the fix resolves the issue."*

### ⏳ Temporal Forecasting
After a strategy is chosen, the system predicts the business state at three future time points. If any prediction is `FAIL`, it automatically re-enters the debate loop to harden the strategy.

### 💰 Economic Impact Calculator
Translates technical decisions into boardroom language:
- Cost of Downtime: $50,000/min
- Cost of Fix: $2,000 (cloud + engineering)
- Brand Damage: $120,000 (churn simulation)
- Net Impact: -$72,000

### 🔗 Causal Chain (Explainable AI)
Shows the full domino effect:
```
DB Connection Pool Exhausted
  ↓ Because: Marketing campaign drove 10x traffic
  ↓ Which caused: API timeouts
  ↓ Which led to: Customer tweets going viral
  ↓ Resulting in: 30% sentiment drop in JP market
Resolution breaks chain at: Connection pool auto-scaling + circuit breaker
```

### 📊 Self-Critique Radar
The system grades its own solution across 4 dimensions (0–10):
- Technical Soundness
- Cultural Sensitivity
- Economic Optimality
- Temporal Sustainability

### 🗄️ Institutional Memory
Every crisis + resolution is saved to SQLite. Before generating a new solution, the system searches past incidents: *"A similar incident occurred 3 weeks ago. Resolution was X. Effectiveness: 87%."*

### 📋 Auto-Generated Post-Mortem
A formal incident report in Markdown — executive summary, timeline, root cause, resolution, economic impact, temporal forecast, self-critique, lessons learned, prevention checklist. Downloadable from the UI.

### 🔒 Compliance Veto
A dedicated agent checks every proposed solution against GDPR and SOC2. If it violates any article, it issues a `REGULATORY_VETO` and the system **must** regenerate.

---

## 🗺️ Scenario Library

The project ships with **12,000 procedurally generated crisis scenarios** across:

- **10 sectors**: e-commerce, fintech, healthcare, telecom, logistics, gaming, SaaS, energy, media, aerospace
- **20 crisis types**: cache poisoning, DDoS, DB exhaustion, thundering herd, cert expiry, DNS failure, cascading failure, memory leak, ransomware, data breach, API meltdown, payment throttle, cache stampede, dependency outage, CDN failure, replication lag, queue poisoning, disk full, network partition, SSL chain break
- **9 regions**: US-East, US-West, EU-West, EU-Central, APAC-Tokyo, APAC-Singapore, LATAM-São-Paulo, MEA-Dubai, Global
- **3 severity levels**: SEV-1, SEV-2, SEV-3
- **10 time contexts**: peak hours, Black Friday, Sunday night, holiday weekend, etc.

Search with multi-term AND queries: `"fintech SEV-1 cache"` returns all fintech cache crises at SEV-1 severity.

---

## 🚀 How To Use It

### Prerequisites
- Python 3.11+
- A Cerebras API key (get one at [cerebras.ai](https://cerebras.ai))
- 4 images (optional but recommended for multimodal track): architecture diagram, dashboard screenshot, social media screenshot, error log image

### Installation

```bash
# 1. Clone / navigate to project
cd sentinel-omega/

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate          # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set your Cerebras API key
echo "CEREBRAS_API_KEY=csk-your-key-here" > .env
echo "MODEL=gemma-4-31b" >> .env

# 5. Generate the scenario database (12,000 scenarios)
python data/generate_scenarios.py

# 6. Launch the War Room Dashboard
streamlit run ui/dashboard.py
# or: python main.py
```

### Using the Dashboard

1. **Search a scenario** — Type keywords in the sidebar search box (e.g. `"fintech cache SEV-1"`). Select from matching results.
2. **Upload visual evidence** — Drag and drop PNG/JPG images:
   - Architecture diagram → Red Team agent analyzes it for single points of failure
   - Dashboard screenshot → Operator agent reads the graph for bottlenecks
   - Twitter screenshot → Diplomat agent gauges real human anger from actual tweets
   - Error log image → Compliance agent checks for PII or regulatory violations
3. **Tune telemetry sliders** — Set error rate, sentiment score, social volume, churn risk. These determine each agent's voting power.
4. **Click "🚀 TRIGGER OMEGA SIMULATION"** — The full 12-stage pipeline runs in ~9 seconds.
5. **Explore the results**:
   - Monte Carlo histogram (probability distribution)
   - Agent weight bars (who had the most voting power)
   - War Room grid (4 agent responses with VETO badges)
   - Compliance badge (PASSED or VETOED)
   - Temporal forecast slider (Present → T+1h → T+24h → T+7d)
   - Economic impact (5 financial metrics)
   - Causal chain (explainability flowchart)
   - Self-critique radar chart
   - Final Hardened Strategy (golden frame)
   - Speed comparison (Cerebras vs estimated GPU)
6. **Download** the audit trail (JSON) and post-mortem report (Markdown).

### Running the Benchmark

```bash
python benchmarks/speed_test.py
```
Runs the full Omega loop with defaults and prints per-stage timings + estimated 10x speed advantage over standard GPUs.

### Testing the API

```bash
python tests/test_multimodal.py
```
Verifies:
1. Text-only API call works
2. Multimodal (image + text) API call works

---

## 📁 Project Structure

```
sentinel-omega/
├── agents/
│   ├── base_agent.py           # Abstract Base Class (ABC) for all agents
│   ├── personas.py             # System prompts + persona configs
│   ├── kpi_config.py           # KPI definitions + veto authorities
│   └── orchestrator.py        # The Omega Loop engine (async)
├── core/
│   ├── config.py               # Environment + model settings
│   ├── api.py                  # Shared Cerebras client + JSON schema enforcement
│   ├── telemetry.py            # TelemetryVector + agent weight calculator
│   ├── image_handler.py        # base64 encoding / resizing / validation
│   ├── monte_carlo.py          # Parallel Monte Carlo Burst engine
│   ├── simulator.py            # Temporal Forecast (T+1h / T+24h / T+7d)
│   ├── economics.py            # Economic Impact Calculator (USD)
│   ├── causal_chain.py         # Explainable AI causal chain generator
│   ├── critic.py               # Self-Critique scoring engine
│   ├── compliance.py           # GDPR / SOC2 veto checker
│   ├── memory.py               # SQLite Institutional Memory
│   └── post_mortem.py          # Formal incident report generator
├── ui/
│   ├── dashboard.py            # Main Streamlit War Room app
│   └── components/
│       ├── agent_card.py       # Persona card renderer
│       ├── monte_carlo.py      # Monte Carlo histogram
│       ├── radar_chart.py      # Self-critique spider chart
│       ├── speed_compare.py    # Cerebras vs GPU bar chart
│       └── telemetry.py        # Per-stage timing bar
├── data/
│   ├── scenarios.json          # 3 hand-crafted base scenarios
│   ├── scenarios.db            # 12,000 generated scenarios (SQLite)
│   ├── scenario_library.py     # Search class for the scenario DB
│   └── generate_scenarios.py   # Scenario generator script
├── utils/
│   ├── logger.py               # JSON Audit Trail logger
│   └── rate_limiter.py         # Async semaphore (100 RPM guard)
├── benchmarks/
│   └── speed_test.py           # Latency benchmark script
├── tests/
│   └── test_multimodal.py      # API connectivity + vision test
├── .env                        # API keys
├── requirements.txt
├── main.py                     # Entry point
└── README.md                   # This file
```

---

## ⚡ Performance

| Stage | Typical Time |
|---|---|
| Monte Carlo (7 sims) | ~0.3s |
| Divergence (4 agents parallel) | ~0.4s |
| CEO Mediation | ~0.2s |
| Compliance Check | ~0.2s |
| Temporal Simulation (3 jumps) | ~0.3s |
| Economics | ~0.2s |
| Causal Chain | ~0.2s |
| Self-Critique | ~0.2s |
| **Total** | **~9s** |
| Estimated GPU equivalent | ~90s (10x) |

All times measured on Cerebras with `gemma-4-31b` and `reasoning_effort: high`.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **AI Model** | `gemma-4-31b` via Cerebras API — **sole inference model** |
| **Streaming** | `AsyncCerebras` `stream=True`; reasoning tokens bridged to Streamlit via a thread+queue |
| **Multimodal** | RapidOCR (`rapidocr-onnxruntime`) — local image→text, fed to the agents |
| **Orchestration** | `asyncio.gather` with `Semaphore(8)` rate limiting |
| **Data Models** | Pydantic v2 `BaseModel` for all inter-module transfers |
| **Architecture** | Abstract Base Classes, modular service-oriented design |
| **Frontend** | Streamlit (`layout="wide"`, dark SOC theme) |
| **Charts** | Plotly (histogram, radar, bar comparison) |
| **Memory** | SQLite (institutional incident database) |
| **Logging** | Custom JSON audit trail |
| **Config** | `python-dotenv` + environment variables |

---

## 🎤 The Pitch (60-Second Demo Script)

> _"We didn't build a chatbot. We didn't build an agent system. We built **Sentinel Omega** — the world's first Predictive Business Equilibrium Engine._
>
> _It ingests live telemetry and images — your actual dashboards, architecture diagrams, tweets, error logs. It runs Monte Carlo simulations across 7 parallel universes. It resolves competing corporate incentives using game theory — 5 agents with different KPIs debate until they find the Nash Equilibrium._
>
> _It vetoes its own solutions against GDPR and SOC2 compliance. It simulates the future at T+1 hour, T+24 hours, and T+7 days to prevent side effects. It calculates the dollar impact. It generates a causal chain for full explainability. It self-scores its own solution._
>
> _Powered by gemma-4-31b on Cerebras, the full 12-stage pipeline runs in 9 seconds — what would take a standard GPU 90 seconds and a human war room 4 hours._
>
> _This isn't a prototype. This is the future of enterprise resilience."_

---

## 📜 License

Built for the Cerebras Hackathon. Use it, learn from it, ship it.

---

## 🏆 Hackathon Tracks

| Track | Focus |
|---|---|
| **Track 1** — Multiverse Agents ($2K) | Multimodal image analysis + 5-agent game-theoretic debate + Monte Carlo |
| **Track 2** — People's Choice ($2K) | 60s demo video: upload dashboard → agents fight → CEO resolves → speed comparison |
| **Track 3** — Enterprise Impact ($1K) | Compliance veto, post-mortem PDF, SQLite memory, $ impact, production-ready architecture |