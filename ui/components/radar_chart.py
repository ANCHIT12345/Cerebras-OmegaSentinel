import streamlit as st
import plotly.graph_objects as go


def show_radar_chart(scores):
    """Radar spider chart for self-critique."""
    values = [
        scores.technical_soundness,
        scores.cultural_sensitivity,
        scores.economic_optimality,
        scores.temporal_sustainability,
        scores.technical_soundness,
    ]
    theta = ["Technical", "Cultural", "Economic", "Temporal", "Technical"]
    fig = go.Figure(data=go.Scatterpolar(
        r=values, theta=theta, fill="toself",
        line=dict(color="#FFD700", width=2),
        fillcolor="rgba(255, 215, 0, 0.2)",
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(range=[0, 10], tickfont=dict(color="#E0E0E0"))),
        template="plotly_dark",
        height=350,
        title=dict(text=f"Solution Quality: {scores.overall_score:.1f}/10", font=dict(color="#FFD700")),
    )
    st.plotly_chart(fig, use_container_width=True)