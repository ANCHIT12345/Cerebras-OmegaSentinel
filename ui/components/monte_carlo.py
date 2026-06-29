import streamlit as st
import plotly.graph_objects as go


def show_monte_carlo_chart(mc):
    """Histogram of Monte Carlo outcomes."""
    fig = go.Figure(data=[
        go.Bar(
            x=["SUCCESS", "DEGRADED", "FAIL"],
            y=[mc["success"], mc["degraded"], mc["fail"]],
            marker_color=["#00FA9A", "#FFD700", "#FF4B4B"],
            text=[f"{mc['success']} sims", f"{mc['degraded']} sims", f"{mc['fail']} sims"],
            textposition="auto",
        )
    ])
    fig.update_layout(
        template="plotly_dark",
        xaxis_title="Outcome",
        yaxis_title="Simulations",
        title=f"Monte Carlo Burst — {mc['total_sims']} Universes | Confidence: {mc['confidence']*100:.0f}%",
        title_font_color="#FFD700",
        height=300,
    )
    st.plotly_chart(fig, use_container_width=True)