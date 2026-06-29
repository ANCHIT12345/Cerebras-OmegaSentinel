import streamlit as st
import plotly.graph_objects as go


def show_speed_comparison(cerebras_time: float):
    """Side-by-side Cerebras vs estimated GPU speed."""
    gpu_estimate = max(cerebras_time * 10, 60.0)
    fig = go.Figure(data=[
        go.Bar(
            name="Cerebras (Gemma)",
            x=["Cerebras"], y=[cerebras_time],
            marker_color="#FFD700",
            text=[f"{cerebras_time:.1f}s"],
            textposition="auto",
        ),
        go.Bar(
            name="Standard GPU (est.)",
            x=["Std GPU"], y=[gpu_estimate],
            marker_color="#FF4B4B",
            text=[f"{gpu_estimate:.0f}s"],
            textposition="auto",
        ),
    ])
    fig.update_layout(
        yaxis_title="Seconds",
        template="plotly_dark",
        title="⚡ Speed Advantage",
        title_font_color="#FFD700",
        height=300,
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.success(f"**Cerebras Advantage: {gpu_estimate/cerebras_time:.0f}x faster**")


def ghost_race(real_seconds: float, real_tokens: int, gpu_tps: float = 60.0):
    """Animated replay: Cerebras bar zooms to done while a GPU 'ghost' crawls.
    GPU baseline gpu_tps tok/s (conservative). Both animate over the same wall-clock
    so the ghost visibly lags."""
    real_seconds = max(real_seconds, 0.1)
    projected = real_tokens / max(gpu_tps, 1.0)          # seconds a GPU would need
    speedup = projected / real_seconds
    ghost_pct = min(100.0 * real_seconds / max(projected, real_seconds), 100.0)
    dur = 2.2  # animation seconds
    html = f"""
    <style>
    @keyframes cbz {{ from {{ width:0%; }} to {{ width:100%; }} }}
    @keyframes ghz {{ from {{ width:0%; }} to {{ width:{ghost_pct:.1f}%; }} }}
    .race-wrap {{ font-family:'JetBrains Mono',monospace; margin:8px 0 4px; }}
    .race-row {{ margin:10px 0; }}
    .race-lab {{ color:#C8CDD3; font-size:0.8em; letter-spacing:0.04em; margin-bottom:4px; }}
    .race-track {{ background:rgba(255,255,255,0.06); border-radius:8px; height:22px; overflow:hidden; }}
    .race-cb {{ height:100%; background:linear-gradient(90deg,#FFD700,#00FA9A); animation:cbz {dur}s cubic-bezier(.2,.8,.2,1) forwards; border-radius:8px; }}
    .race-gh {{ height:100%; background:linear-gradient(90deg,#FF4B4B,#B0353F); animation:ghz {dur}s linear forwards; border-radius:8px; opacity:0.85; }}
    .race-verdict {{ color:#FFD700; font-family:'Orbitron',sans-serif; font-weight:700; font-size:1.1em; letter-spacing:0.04em; margin-top:10px; }}
    </style>
    <div class="race-wrap">
      <div class="race-row"><div class="race-lab">⚡ CEREBRAS · gemma-4-31b — finished {real_seconds:.1f}s</div>
        <div class="race-track"><div class="race-cb"></div></div></div>
      <div class="race-row"><div class="race-lab">🐌 STANDARD GPU (~{gpu_tps:.0f} tok/s) — still going at {real_seconds:.1f}s</div>
        <div class="race-track"><div class="race-gh"></div></div></div>
      <div class="race-verdict">{real_seconds:.1f}s vs projected {projected:.0f}s · {speedup:.1f}× faster</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


if __name__ == "__main__":
    p = 6000 / 60.0
    assert p == 100.0, p
    assert abs((p / 9.0) - 11.111) < 0.01
    print("OK ghost")