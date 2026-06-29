"""SENTINEL OMEGA — War Room Dashboard."""
import asyncio
import json
import os
import sys
import time
from datetime import datetime

import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Ensure .env loaded
from dotenv import load_dotenv
load_dotenv()

from agents.orchestrator import OmegaOrchestrator
from core.image_handler import ImageHandler
from core.telemetry import TelemetryVector, HardMetrics, SoftMetrics, calculate_agent_weights
from core.memory import InstitutionalMemory
from data.scenario_library import ScenarioLibrary
from utils.logger import audit_logger

from ui.components.radar_chart import show_radar_chart
from ui.components.monte_carlo import show_monte_carlo_chart
from ui.components.speed_compare import show_speed_comparison, ghost_race
from ui.components.agent_card import show_agent_card
from ui.components.telemetry import show_telemetry_bar

from core.streaming import run_omega_streamed
from core.verdict_card import render_verdict_png
from core.ocr import extract_evidence

# ──────────────────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────────────────
st.set_page_config(
    layout="wide",
    page_title="Sentinel Omega",
    page_icon="🛡️",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=JetBrains+Mono:wght@400;500;700&display=swap');
/* ══════════════════════════════════════════════════════
   SENTINEL OMEGA — SOC COMMAND CENTER THEME
   ══════════════════════════════════════════════════════ */

/* ── Base ── */
.stApp, .main, section[data-testid="stMain"] {
    background-color: #0A0C10 !important;
    color: #C8CDD3 !important;
    font-family: 'JetBrains Mono', monospace !important;
    letter-spacing: -0.01em;
}
.stApp::before {
    content: "";
    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    background:
        radial-gradient(ellipse at 15% 20%, rgba(0,212,255,0.05) 0%, transparent 50%),
        radial-gradient(ellipse at 85% 80%, rgba(255,75,75,0.04) 0%, transparent 55%);
    pointer-events: none; z-index: 0;
}
/* drifting grid overlay */
.stApp::after {
    content: "";
    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    background-image:
        linear-gradient(rgba(80,100,120,0.06) 1px, transparent 1px),
        linear-gradient(90deg, rgba(80,100,120,0.06) 1px, transparent 1px);
    background-size: 48px 48px;
    mask-image: radial-gradient(ellipse at center, black 0%, transparent 75%);
    -webkit-mask-image: radial-gradient(ellipse at center, black 0%, transparent 75%);
    animation: grid-drift 30s linear infinite;
    pointer-events: none; z-index: 0;
}
@keyframes grid-drift {
    0%   { transform: translate(0,0); }
    100% { transform: translate(48px,48px); }
}

/* ── Typography ── */
h1, h2, h3, h4, h5, .section-header, [data-testid="stMetricLabel"] {
    font-family: 'Orbitron', sans-serif !important;
    letter-spacing: 0.02em !important;
}
.stMarkdown, .stText, p, li, code, pre {
    font-family: 'JetBrains Mono', monospace !important;
}

/* ── Glassmorphic Cards (generic) ── */
.glass-card {
    background: rgba(22,27,34,0.55);
    backdrop-filter: blur(14px) saturate(140%);
    -webkit-backdrop-filter: blur(14px) saturate(140%);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 15px;
    padding: 20px;
    margin-bottom: 16px;
}

/* ── Section Headers with accent avatar tile ── */
.section-header {
    display: flex; align-items: center; gap: 12px;
    margin: 24px 0 12px 0;
    font-family: 'Orbitron', sans-serif !important;
    font-weight: 700;
    font-size: 1.15em;
    letter-spacing: 0.04em;
}
.section-tile {
    width: 40px; height: 40px;
    border-radius: 10px;
    display: inline-flex; align-items: center; justify-content: center;
    box-shadow: inset 0 0 0 1.5px rgba(255,255,255,0.15);
    flex-shrink: 0;
    font-size: 1.1em;
}

/* ── Accent colors per section ── */
.acc-red    { color: #FF4B4B; } .bg-red    { background: rgba(255,75,75,0.14); border-color: rgba(255,75,75,0.3); box-shadow: inset 0 0 0 1.5px rgba(255,75,75,0.2); }
.acc-blue   { color: #00D4FF; } .bg-blue   { background: rgba(0,212,255,0.14); border-color: rgba(0,212,255,0.3); box-shadow: inset 0 0 0 1.5px rgba(0,212,255,0.2); }
.acc-green   { color: #00FA9A; } .bg-green  { background: rgba(0,250,154,0.14); border-color: rgba(0,250,154,0.3); box-shadow: inset 0 0 0 1.5px rgba(0,250,154,0.2); }
.acc-purple  { color: #B084FF; } .bg-purple { background: rgba(176,132,255,0.14); border-color: rgba(176,132,255,0.3); box-shadow: inset 0 0 0 1.5px rgba(176,132,255,0.2); }
.acc-gold    { color: #FFD700; } .bg-gold   { background: rgba(255,215,0,0.14); border-color: rgba(255,215,0,0.3); box-shadow: inset 0 0 0 1.5px rgba(255,215,0,0.2); }
.acc-emerald { color: #54E0C4; } .bg-emerald{ background: rgba(84,224,196,0.14); border-color: rgba(84,224,196,0.3); box-shadow: inset 0 0 0 1.5px rgba(84,224,196,0.2); }

/* ── Header Bar ── */
.soc-header {
    position: relative;
    background: linear-gradient(180deg, rgba(18,22,30,0.9), rgba(18,22,30,0.6));
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 15px;
    padding: 18px 24px;
    margin-bottom: 20px;
    display: flex; align-items: center; gap: 16px;
    overflow: hidden;
}
.soc-header::after {
    content: ""; position: absolute; top: 0; left: -100%;
    width: 50%; height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.04), transparent);
    animation: sweep 6s ease-in-out infinite;
}
@keyframes sweep {
    0%, 100% { left: -50%; }
    50%      { left: 100%; }
}
.soc-title {
    font-family: 'Orbitron', sans-serif; font-weight: 900; font-size: 1.5em;
    letter-spacing: 0.08em; color: #FFD700;
    text-shadow: 0 0 20px rgba(255,215,0,0.3);
}
.soc-sub { font-size: 0.75em; color: #8899A6; letter-spacing: 0.04em; }
.chip {
    display: inline-flex; align-items: center; gap: 6px;
    font-family: 'Orbitron', sans-serif; font-size: 0.65em; font-weight: 700;
    letter-spacing: 0.06em; text-transform: uppercase;
    padding: 5px 14px; border-radius: 20px;
    border: 1px solid rgba(255,255,255,0.15);
    background: rgba(255,255,255,0.06);
    color: #C8CDD3;
}
.chip-ok   { color: #00FA9A; border-color: rgba(0,250,154,0.4); background: rgba(0,250,154,0.1); }
.chip-warn { color: #FFD700; border-color: rgba(255,215,0,0.4); background: rgba(255,215,0,0.1); }
.dot-critical {
    width: 10px; height: 10px; border-radius: 50%; background: #FF4B4B;
    box-shadow: 0 0 8px rgba(255,75,75,0.6);
    animation: pulse-red 2s ease-in-out infinite;
}
@keyframes pulse-red { 0%,100% { opacity:1; box-shadow:0 0 4px rgba(255,75,75,0.4); } 50% { opacity:0.4; box-shadow:0 0 14px rgba(255,75,75,0.8); } }

/* ── Pill Badges ── */
.badge { display: inline-block; font-family:'Orbitron',sans-serif; font-size:0.7em; font-weight:700; letter-spacing:0.05em; text-transform:uppercase; padding: 4px 12px; border-radius: 20px; }
.badge-ok   { color:#00FA9A; background:rgba(0,250,154,0.15); border:1px solid rgba(0,250,154,0.4); }
.badge-warn { color:#FFD700; background:rgba(255,215,0,0.15); border:1px solid rgba(255,215,0,0.4); }
.badge-alert{ color:#FF4B4B; background:rgba(255,75,75,0.15); border:1px solid rgba(255,75,75,0.4); animation: flash-red 2.5s ease-in-out infinite; }
@keyframes flash-red { 0%,100% { box-shadow:0 0 0 rgba(255,75,75,0); } 50% { box-shadow: 0 0 8px rgba(255,75,75,0.6); } }

/* ── Metric Cards ── */
.metric-card {
    background: rgba(18,22,30,0.6);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.08);
    border-left: 3px solid #FFD700;
    border-radius: 12px;
    padding: 14px 16px;
    margin: 0 0 12px 0;
}
.metric-card .label {
    font-family:'Orbitron',sans-serif; font-size:0.65em; letter-spacing:0.08em;
    text-transform:uppercase; color:#8899A6; margin-bottom:6px;
}
.metric-card .value {
    font-family:'Orbitron',sans-serif; font-weight:700; font-size:1.6em; color:#FFD700;
    text-shadow: 0 0 12px rgba(255,215,0,0.15);
}
.metric-card.spacer { border-left-color: transparent; }

/* ── Golden Frame ── */
.golden-frame {
    border: 2px solid rgba(255,215,0,0.6);
    border-radius: 15px;
    background: linear-gradient(135deg, rgba(30,26,16,0.8), rgba(18,18,18,0.9));
    backdrop-filter: blur(12px);
    padding: 28px;
    box-shadow: 0 0 24px rgba(255,215,0,0.15), inset 0 1px 0 rgba(255,255,255,0.1);
    position: relative; overflow: hidden;
    color: #E0E0E0;
}
.golden-frame::after {
    content:""; position:absolute; top:0; left:-100%; width:40%; height:100%;
    background: linear-gradient(90deg, transparent, rgba(255,215,0,0.06), transparent);
    animation: sweep 7s ease-in-out infinite;
}
.golden-frame pre, .golden-frame code, .golden-frame table, .golden-frame .table-wrapper {
    max-width: 100%; overflow-x: auto; display: block;
}
.golden-frame table { border-collapse: collapse; }
.golden-frame table td, .golden-frame table th {
    border: 1px solid rgba(255,215,0,0.2); padding: 6px 10px;
}

/* ── Overflow Fix: code blocks, tables, pre ── */
pre, code, table, .table-wrapper, [data-testid="stMarkdownContainer"] pre,
[data-testid="stMarkdownContainer"] table {
    max-width: 100% !important; overflow-x: auto !important;
}
[data-testid="stMarkdownContainer"] table { display: block; overflow-x: auto; }
.stCodeBlock, .stCode {
    max-width: 100% !important; overflow-x: auto !important;
}

/* ── Streamlit element overrides ── */
div[data-testid="stMetric"] {
    background: rgba(18,22,30,0.6);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.08);
    border-left: 3px solid #FFD700;
    border-radius: 12px;
    padding: 14px 16px;
}
div[data-testid="stMetricValue"] {
    font-family:'Orbitron',sans-serif !important; font-weight:700;
}
.stButton > button {
    border: 2px solid #FFD700;
    background: rgba(255,215,0,0.12);
    color: #FFD700;
    font-family:'Orbitron',sans-serif; font-weight:700; letter-spacing:0.06em;
    border-radius: 10px; text-transform: uppercase;
    transition: all 0.25s ease;
}
.stButton > button:hover {
    background: #FFD700; color:#0A0C10; box-shadow: 0 0 18px rgba(255,215,0,0.35);
}

/* ── Elsevier-style scoped component card ── */
.scoped-card {
    background: rgba(22,27,34,0.5);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 15px;
    padding: 18px;
    max-width: 100%;
    overflow-x: auto;
}
.scoped-card [data-testid="stMarkdownContainer"] {
    max-width: 100%; overflow-x: auto;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] { gap: 8px; }
.stTabs [data-baseweb="tab"] {
    border-radius: 10px 10px 0 0;
    background: rgba(22,27,34,0.5);
    backdrop-filter: blur(8px);
    border: 1px solid transparent;
    font-family:'Orbitron',sans-serif; font-size:0.75em; letter-spacing:0.04em;
}
.stTabs [aria-selected="true"] {
    background: rgba(255,215,0,0.15) !important;
    border-color: rgba(255,215,0,0.4) !important;
    color: #FFD700 !important;
}

/* ── Expanders ── */
.streamlit-expanderHeader, details summary {
    font-family:'Orbitron',sans-serif !important; font-size:0.8em; letter-spacing:0.03em;
    background: rgba(22,27,34,0.5); border-radius: 10px;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: rgba(14,16,20,0.85) !important;
    backdrop-filter: blur(16px);
    border-right: 1px solid rgba(255,255,255,0.06);
}

/* ── Progress bar ── */
.stProgress > div > div > div { background-color: #FFD700; }

/* ── Info/alert/success/warning/error boxes ── */
.stAlert, [data-testid="stAlert"] {
    border-radius: 12px; backdrop-filter: blur(8px);
}

/* ── Pagination / selectbox ── */
[data-baseweb="menu"], [data-baseweb="select"] { font-family:'JetBrains Mono',monospace !important; }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────
# HEADER BAR (glassmorphic, status chips, pulse dot, shimmer)
# ──────────────────────────────────────────────────────────
st.markdown("""
<div class="soc-header">
    <span style="font-size:1.8em;">🛡️</span>
    <div>
        <div class="soc-title">SENTINEL OMEGA</div>
        <div class="soc-sub">Predictive Business Equilibrium Engine · Multimodal Multiverse Agents on Cerebras</div>
    </div>
    <div style="margin-left:auto; display:flex; gap:10px; align-items:center;">
        <span class="chip chip-ok">● CONNECTED</span>
        <span class="chip"><span class="dot-critical"></span> SEV-1 CRITICAL</span>
        <span class="chip chip-warn">CEREBRAS-01</span>
        <span class="chip chip-warn">GEMMA-4-31B</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────
# TOP STATUS BAR — metric cards with Orbitron numerals
# ──────────────────────────────────────────────────────────
_m1, _m2, _m3, _m4 = st.columns(4)
for col, label, val, delta, accent in [
    (_m1, "System Health", "CRITICAL", "−40% Error", "bg-red acc-red"),
    (_m2, "Global Sentiment", "−78", "Viral Outrage", "bg-blue acc-blue"),
    (_m3, "Active Agents", "5 / 5", "reasoning: high", "bg-green acc-green"),
    (_m4, "Cerebras Node", "ONLINE", "100 RPM Cap", "bg-gold acc-gold"),
]:
    with col:
        cls = accent.split()[0]  # bg-*
        st.markdown(f"""
        <style> div.soc-m-{accent.split()[0]} {{ background: rgba(18,22,30,0.6); backdrop-filter: blur(10px);
                  border: 1px solid rgba(255,255,255,0.08); border-left: 3px solid; border-radius: 12px; padding:14px 16px; }}
        </style>
        <div class="metric-card {accent.split()[1]}" style="border-left-color: {{'bg-red':'#FF4B4B','bg-blue':'#00D4FF','bg-green':'#00FA9A','bg-gold':'#FFD700'}}['{accent.split()[0]}']">
            <div class="label">{label}</div>
            <div class="value">{val}</div>
            <div style="font-size:0.7em;color:#8899A6;margin-top:4px;">{delta}</div>
        </div>
        """, unsafe_allow_html=True)

st.caption("")  # spacer

st.divider()

# ──────────────────────────────────────────────────────────
# SIDEBAR — COMMAND PANEL
# ──────────────────────────────────────────────────────────
with st.sidebar:
    st.header("🕹️ Command Panel")

    # ─── SEARCHABLE SCENARIO LIBRARY (10k+) ───
    lib = ScenarioLibrary()
    st.markdown(f"📚 **Scenario Library:** {lib.total:,} scenarios")
    search_query = st.text_input(
        "🔍 Search scenarios",
        placeholder="e.g. fintech SEV-1 cache | aerospace Global | healthcare breach",
        help="Type keywords. Multiple terms are AND-matched across title, sector, crisis_type, region, severity.",
    )
    matching = lib.search(search_query, limit=100)
    if not matching:
        st.warning("No matches — try fewer/different terms.")
        scenario_text = ""
        selected_scenario = ""
    else:
        st.caption(f"{len(matching)} match{'es' if len(matching)!=1 else ''} found")
        options = [f"[{m['severity']}] {m['title']}" for m in matching]
        choice = st.selectbox("Select Crisis Target", options)
        selected_scenario = choice
        match_idx = options.index(choice)
        scenario_text = matching[match_idx]["context"]
        chosen = matching[match_idx]
        # Surface the chosen scenario's metadata
        with st.expander("Scenario Details"):
            st.json({
                "id": chosen.get("id"),
                "sector": chosen.get("sector"),
                "crisis_type": chosen.get("crisis_type"),
                "region": chosen.get("region"),
                "severity": chosen.get("severity"),
                "time_context": chosen.get("time_context"),
                "suggested_image_keys": (chosen.get("image_keys") or "").split(",") if chosen.get("image_keys") else [],
            })

    st.markdown("### 📸 Upload Visual Evidence")
    st.caption("Images are OCR'd locally — agents read the extracted text (gemma-4-31b is text-only).")
    arch_img = st.file_uploader("Architecture Diagram", type=["png", "jpg", "jpeg"], key="arch")
    dash_img = st.file_uploader("Dashboard Screenshot (Grafana/Datadog)", type=["png", "jpg", "jpeg"], key="dash")
    tweet_img = st.file_uploader("Social Media Screenshot", type=["png", "jpg", "jpeg"], key="tweet")
    log_img = st.file_uploader("Error Log Image", type=["png", "jpg", "jpeg"], key="log")

    st.markdown("### 🎛️ Telemetry Input")
    error_rate = st.slider("Error Rate %", 0, 100, 40)
    sentiment = st.slider("Sentiment Score", -100, 100, -78)
    social_vol = st.slider("Social Volume (posts/min)", 0, 5000, 1200)
    churn_risk = st.slider("Churn Risk %", 0, 100, 65)

    st.markdown("### 🎲 Monte Carlo Sims")
    n_mc = st.slider("Number of Simulations", 3, 10, 7,
                     help="Higher = more accurate probability. Caps at 10 to respect rate limits.")

    st.markdown("### 📚 Institutional Memory")
    try:
        mem = InstitutionalMemory()
        history = mem.list_all(limit=5)
        if history:
            for h in history:
                st.write(f"📋 **Inc {h['id']}** — {h['scenario'][:40]}... (Score: {h['overall']:.1f})")
        else:
            st.write("No past incidents recorded.")
    except Exception:
        st.write("Memory offline.")

    run_btn = st.button("🚀 TRIGGER OMEGA SIMULATION", use_container_width=True)

# ──────────────────────────────────────────────────────────
# MAIN EXECUTION
# ──────────────────────────────────────────────────────────
if run_btn:
    # Encode images to base64
    images = {}
    if arch_img:
        images["architecture"] = ImageHandler.encode_uploaded(arch_img)
    if dash_img:
        images["dashboard"] = ImageHandler.encode_uploaded(dash_img)
    if tweet_img:
        images["twitter"] = ImageHandler.encode_uploaded(tweet_img)
    if log_img:
        images["error_log"] = ImageHandler.encode_uploaded(log_img)

    # OCR evidence so gemma-4-31b reasons over real image text (honest multimodal)
    evidence = {k: extract_evidence(uri) for k, uri in images.items()}
    evidence = {k: v for k, v in evidence.items() if v}
    vision_live = bool(evidence)

    if not images:
        st.info("ℹ️ No images uploaded. Running text-only analysis.")

    # Build telemetry vector
    telemetry = TelemetryVector(
        hard=HardMetrics(
            cpu_load=85.0, latency_ms=2400.0,
            error_rate=float(error_rate),
            db_connections=980, cache_hit_rate=12.0,
        ),
        soft=SoftMetrics(
            sentiment_score=float(sentiment),
            social_volume=int(social_vol),
            churn_risk=float(churn_risk),
            regional_outrage=["JP", "US-East"],
        ),
        region="Global",
        timestamp=datetime.now().isoformat(),
    )

    # ─── LIVE WAR ROOM — stream the debate token-by-token at Cerebras speed ───
    st.markdown('<div class="section-header"><span class="section-tile bg-gold acc-gold">⚡</span><span class="acc-gold">Live War Room — Agents Thinking on Cerebras</span></div>', unsafe_allow_html=True)
    tps_box = st.empty()
    stage_box = st.empty()
    AGENTS = ["Operator", "Diplomat", "Red Team", "Compliance"]
    cols = st.columns(4)
    card_ph = {a: cols[i].empty() for i, a in enumerate(AGENTS)}
    st.markdown("**⚖️ Arbitrator — CEO Mediation**")
    arb_ph = st.empty()

    buffers = {a: "" for a in AGENTS}
    buffers["Arbitrator"] = ""

    def _render(agent):
        txt = buffers[agent][-1100:]  # tail — keep card light
        ph = arb_ph if agent == "Arbitrator" else card_ph.get(agent)
        if ph is None:
            return
        ph.markdown(
            f'<div class="glass-card" style="min-height:150px; font-family:JetBrains Mono,monospace; font-size:0.72em; white-space:pre-wrap; line-height:1.45;">'
            f'<div class="acc-gold" style="font-weight:700; margin-bottom:6px;">{agent}</div>{txt}▌</div>',
            unsafe_allow_html=True,
        )

    for a in AGENTS:
        _render(a)

    orch = OmegaOrchestrator(n_mc_sims=n_mc)
    start_time = time.time()
    tok = 0
    results = None
    err = None

    for ev in run_omega_streamed(orch, scenario_text, telemetry, images, evidence):
        et = ev.get("type")
        if et == "token":
            agent = ev["agent"]
            buffers.setdefault(agent, "")
            buffers[agent] += ev["delta"]
            tok += max(len(ev["delta"]) // 4, 1)
            elapsed = max(time.time() - start_time, 0.01)
            tps_box.markdown(
                f'<div class="acc-green" style="font-family:Orbitron,sans-serif; font-weight:900; font-size:1.6em;">'
                f'{tok/elapsed:,.0f} <span style="font-size:0.5em; color:#8899A6;">SWARM TOKENS/SEC</span></div>',
                unsafe_allow_html=True,
            )
            _render(agent)
        elif et == "stage":
            stage_box.markdown(
                f'<span class="badge badge-warn">{ev["name"].replace("_"," ").upper()}</span> '
                f'<span style="color:#8899A6; font-size:0.8em;">{ev["seconds"]:.2f}s</span>',
                unsafe_allow_html=True,
            )
        elif et == "done":
            results = ev["results"]
        elif et == "error":
            err = ev["error"]

    if err or results is None:
        st.error(f"Omega engine failed: {err or 'no results'}")
        st.stop()

    total_time = time.time() - start_time
    tps_box.markdown(
        f'<div class="acc-green" style="font-family:Orbitron,sans-serif; font-weight:900; font-size:1.6em;">'
        f'✅ COMPLETE — {total_time:.2f}s</div>', unsafe_allow_html=True)

    # Persist so widget reruns (e.g. forecast slider) don't wipe results
    st.session_state["last_results"] = results
    st.session_state["last_total"] = total_time
    st.session_state["last_images"] = images
    st.session_state["last_audit"] = audit_logger.get_all()
    st.session_state["last_vision_live"] = vision_live

# Render from session_state — survives reruns from the forecast slider etc.
if "last_results" in st.session_state:
    results = st.session_state["last_results"]
    total_time = st.session_state["last_total"]
    images = st.session_state["last_images"]
    audit_all = st.session_state["last_audit"]
    vision_live = st.session_state.get("last_vision_live", False)

    st.caption("🟢 VISION: OCR live — agents read real text from your images"
               if vision_live else
               "⚪ VISION: evidence noted (no readable text / no images) — text-only reasoning")

    # ─── Display Uploaded Images ───
    if images:
        st.markdown('<div class="section-header"><span class="section-tile bg-green acc-green">📸</span><span class="acc-green">Visual Evidence Uploaded</span></div>', unsafe_allow_html=True)
        img_cols = st.columns(min(len(images), 4))
        for i, (key, uri) in enumerate(list(images.items())[:4]):
            with img_cols[i]:
                st.image(uri, caption=key.title(), use_container_width=True)

    st.divider()

    # ─── Monte Carlo Results ───
    st.markdown('<div class="section-header"><span class="section-tile bg-purple acc-purple">🎲</span><span class="acc-purple">Monte Carlo Multiverse Burst</span></div>', unsafe_allow_html=True)
    mc = results["probability_map"]
    show_monte_carlo_chart(mc)
    with st.expander("View Raw Simulation Results"):
        for i, (res, mod) in enumerate(zip(mc["raw_results"], mc["modifiers_used"])):
            st.write(f"**Sim {i+1}** ({mod[:60]}...):")
            st.write(res)

    st.divider()

    # ─── Agent Weights ───
    st.markdown('<div class="section-header"><span class="section-tile bg-blue acc-blue">⚖️</span><span class="acc-blue">Agent Voting Weights (Telemetry-Driven)</span></div>', unsafe_allow_html=True)
    weights = results["weights"]
    w_cols = st.columns(len(weights))
    for i, (agent, w) in enumerate(weights.items()):
        with w_cols[i]:
            st.metric(agent, f"{int(w*100)}%")
            st.progress(w)

    st.divider()

    # ─── The War Room (tabs to avoid narrow-column overflow) ───
    st.markdown('<div class="section-header"><span class="section-tile bg-red acc-red">⚔️</span><span class="acc-red">The War Room — Multimodal Agent Debate</span></div>', unsafe_allow_html=True)
    divergence = results["divergence"]
    tab_labels = [f"{d['name']}" for d in divergence]
    war_tabs = st.tabs(tab_labels)
    for i, (res, tab) in enumerate(zip(divergence, war_tabs)):
        with tab:
            w = weights.get(res["name"])
            show_agent_card(res, weight=w)

    st.divider()

    # ─── Compliance Check ───
    comp = results["compliance"]
    if comp["status"] == "PASSED":
        st.markdown('<div style="margin:14px 0;"><span class="badge badge-ok">✅ COMPLIANCE CHECK PASSED</span></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="margin:14px 0;"><span class="badge badge-alert">⛔ COMPLIANCE VETOED</span></div>', unsafe_allow_html=True)
        with st.expander("Veto Reason"):
            st.write(comp["reason"])

    st.divider()

    # ─── Temporal Forecast ───
    st.markdown('<div class="section-header"><span class="section-tile bg-emerald acc-emerald">⏳</span><span class="acc-emerald">Temporal Forecast</span></div>', unsafe_allow_html=True)
    temporal = results["temporal"]
    time_options = ["Present"] + [t.time_label for t in temporal]
    selected_time = st.select_slider("Forecast Time Jump", options=time_options, value="Present")

    if selected_time != "Present":
        match = next((t for t in temporal if t.time_label == selected_time), None)
        if match:
            status_class = {"SUCCESS": "badge-ok", "FAIL": "badge-alert", "DEGRADED": "badge-warn"}.get(match.status, "badge-warn")
            st.markdown(f'<div style="margin-bottom:14px;"><span class="badge {status_class}">{match.status}</span></div>', unsafe_allow_html=True)
            tc1, tc2 = st.columns(2)
            with tc1:
                st.write(f"**System:** {match.system_health}")
                st.write(f"**Sentiment:** {match.brand_sentiment}")
            with tc2:
                st.write(f"**Financial:** {match.financial_impact}")
                st.write(f"**Regulatory:** {match.regulatory_risk}")
            st.info(f"**Forecast:** {match.narrative}")

    st.divider()

    # ─── Economic Impact ───
    st.markdown('<div class="section-header"><span class="section-tile bg-gold acc-gold">💰</span><span class="acc-gold">Economic Impact</span></div>', unsafe_allow_html=True)
    econ = results["economics"]
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Downtime Cost", f"${econ.cost_of_downtime:,.0f}")
    c2.metric("Fix Cost", f"${econ.cost_of_fix:,.0f}")
    c3.metric("Brand Damage", f"${econ.brand_damage_cost:,.0f}")
    c4.metric("Revenue Saved", f"${econ.revenue_recovered:,.0f}")
    c5.metric("NET IMPACT", f"${econ.net_impact:,.0f}")
    st.caption(econ.summary)

    st.divider()

    # ─── Causal Chain (XAI) ───
    st.markdown('<div class="section-header"><span class="section-tile bg-red acc-red">🔗</span><span class="acc-red">Causal Chain (Explainability)</span></div>', unsafe_allow_html=True)
    chain = results["causal_chain"]
    st.write(f"**Root Cause:** {chain.root_cause}")
    for event in chain.cascade_events:
        st.write(f"↓ {event}")
    st.write(f"**Final Impact (if untreated):** {chain.final_impact}")
    st.write(f"**Resolution breaks chain at:** {chain.resolution_link}")

    st.divider()

    # ─── Self-Critique Radar ───
    st.markdown('<div class="section-header"><span class="section-tile bg-purple acc-purple">📊</span><span class="acc-purple">Self-Critique Radar</span></div>', unsafe_allow_html=True)
    crit = results["self_critique"]
    show_radar_chart(crit)
    st.info(f"**Improvement:** {crit.recommended_improvement}")

    st.divider()

    # ─── FINAL VERIFIED STRATEGY (golden frame) ───
    st.markdown('<div class="section-header"><span class="section-tile bg-gold acc-gold">🏆</span><span class="acc-gold">Final Verified Omega Strategy</span></div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="golden-frame">
        {results["final_strategy"]["text"]}
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # ─── Speed Comparison ───
    show_speed_comparison(total_time)

    # ─── GPU Ghost Race ───
    est_tokens = sum(len(d.get("text", "")) for d in results["divergence"]) // 4 + 2000
    ghost_race(total_time, est_tokens, gpu_tps=60.0)

    st.divider()

    # ─── Telemetry Bar ───
    show_telemetry_bar(results["timings"], total_time)

    st.divider()

    # ─── Downloads ───
    st.markdown('<div class="section-header"><span class="section-tile bg-blue acc-blue">📥</span><span class="acc-blue">Downloads</span></div>', unsafe_allow_html=True)
    dc1, dc2, dc3 = st.columns(3)
    with dc1:
        st.download_button(
            "📥 Download Audit Trail (JSON)",
            data=json.dumps(audit_all, indent=2, default=str),
            file_name="audit_trail.json",
            mime="application/json",
        )
    with dc2:
        st.download_button(
            "📋 Download Post-Mortem Report (Markdown)",
            data=results["post_mortem"],
            file_name=f"post_mortem_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown",
        )
    with dc3:
        st.download_button(
            "📤 Download Verdict Card (PNG)",
            data=render_verdict_png(results),
            file_name="omega_verdict.png",
            mime="image/png",
        )


# ──────────────────────────────────────────────────────────
# EMPTY STATE
# ──────────────────────────────────────────────────────────
if not run_btn and "last_results" not in st.session_state:
    st.markdown("""
<div class="glass-card" style="max-width:780px; margin-top:30px;">
    <div style="font-family:'Orbitron',sans-serif; font-weight:700; font-size:1.2em; color:#FFD700; letter-spacing:0.04em; margin-bottom:14px;">
        👈 Select a Crisis Scenario and Upload Visual Evidence
    </div>
    <div style="color:#C8CDD3; line-height:1.7;">
        <strong style="color:#00D4FF;">Sentinel Omega</strong> is a Predictive Business Equilibrium Engine that:
        <ol style="margin-top:10px;">
            <li><strong>Ingests telemetry + images</strong> — dashboards, diagrams, tweets, logs (reference only)</li>
            <li><strong>Runs Monte Carlo simulations</strong> across 7 parallel universes</li>
            <li><strong>Debates the crisis</strong> with 4 competing agents</li>
            <li><strong>Finds the Nash Equilibrium</strong> — no KPI destroyed</li>
            <li><strong>Forecasts the future</strong> at T+1h, T+24h, T+7d</li>
            <li><strong>Calculates economic impact</strong> in USD</li>
            <li><strong>Generates a causal chain</strong> for full explainability</li>
            <li><strong>Self-scores</strong> its own solution across 4 dimensions</li>
            <li><strong>Produces a post-mortem</strong> report ready for the boardroom</li>
        </ol>
        <div style="margin-top:16px;"><span class="badge badge-warn">🎲 START</span>
        <span style="margin-left:8px;">Set telemetry on the left and hit TRIGGER OMEGA SIMULATION.</span></div>
    </div>
</div>
    """, unsafe_allow_html=True)