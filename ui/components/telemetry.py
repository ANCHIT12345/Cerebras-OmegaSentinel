import streamlit as st


def show_telemetry_bar(timings: dict, total: float):
    """Render per-stage timings as full-width scrollable metric-card grid (Orbitron numerals)."""
    st.markdown('<div class="section-header"><span class="section-tile bg-blue acc-blue">⏱️</span><span class="acc-blue">Execution Telemetry</span></div>', unsafe_allow_html=True)

    items = list(timings.items())
    # wrap into rows of 4 to avoid super-narrow columns
    row_size = 4
    import html
    rows = [items[i:i+row_size] for i in range(0, len(items), row_size)]
    for row in rows:
        cols = st.columns(row_size)
        for j, (k, v) in enumerate(row):
            with cols[j]:
                st.markdown(f"""
                <div class="metric-card" style="border-left-color:#00D4FF;">
                    <div class="label">{html.escape(k.replace("_"," ").title())}</div>
                    <div class="value" style="color:#00D4FF;">{v:.2f}s</div>
                </div>
                """, unsafe_allow_html=True)
    # total row
    st.markdown(f"""
    <div class="metric-card" style="border-left-color:#FFD700; max-width:340px;">
        <div class="label">TOTAL LATENCY</div>
        <div class="value">{total:.2f}s</div>
        <div style="font-size:0.7em;color:#8899A6;margin-top:4px;">Cerebras Node: CEREBRAS-01</div>
    </div>
    """, unsafe_allow_html=True)