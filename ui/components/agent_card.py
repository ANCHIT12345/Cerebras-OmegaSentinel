import streamlit as st


ACCENT_MAP = {
    "Operator": "red", "Diplomat": "green", "Red Team": "red",
    "Compliance": "purple", "Arbitrator": "gold",
}
GLYPH = {
    "Operator": "⚙️", "Diplomat": "🌐", "Red Team": "🔴",
    "Compliance": "🏛️", "Arbitrator": "⚖️",
}
ACC_CSS = {
    "red":    ("rgba(255,75,75,0.14)",  "rgba(255,75,75,0.3)",
                "rgba(255,75,75,0.2)",  "#FF4B4B"),
    "blue":   ("rgba(0,212,255,0.14)",  "rgba(0,212,255,0.3)",
                "rgba(0,212,255,0.2)",  "#00D4FF"),
    "green":  ("rgba(0,250,154,0.14)",  "rgba(0,250,154,0.3)",
                "rgba(0,250,154,0.2)",  "#00FA9A"),
    "purple": ("rgba(176,132,255,0.14)","rgba(176,132,255,0.3)",
                "rgba(176,132,255,0.2)","#B084FF"),
    "gold":   ("rgba(255,215,0,0.14)",  "rgba(255,215,0,0.3)",
                "rgba(255,215,0,0.2)",  "#FFD700"),
}


def show_agent_card(agent_result, weight=None):
    name = agent_result["name"]
    text = agent_result["text"]
    veto = agent_result.get("veto")
    accent = ACCENT_MAP.get(name, "blue")
    bg, border, ring, color = ACC_CSS[accent]
    glyph = GLYPH.get(name, "👤")

    # header avatar tile + name + weight pill + veto badge
    weight_html = ""
    if weight is not None:
        pi = int(weight * 100)
        weight_html = f'<span class="badge badge-warn" style="margin-left:8px;">VOTING POWER {pi}%</span>'
    veto_html = ""
    if veto:
        veto_html = f'<span class="badge badge-alert" style="margin-left:8px;">⛔ {veto}</span>'

    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:12px; margin-bottom:12px;">
        <span style="width:40px; height:40px; border-radius:10px;
                     display:inline-flex; align-items:center; justify-content:center;
                     font-size:1.1em; background:{bg}; border:1px solid {border};
                     box-shadow: inset 0 0 0 1.5px {ring}; flex-shrink:0;">{glyph}</span>
        <span style="font-family:'Orbitron',sans-serif; font-weight:700; color:{color};
                     letter-spacing:0.04em; font-size:1.05em;">{name}</span>
        {weight_html}{veto_html}
    </div>
    <div class="scoped-card" style="background:rgba(22,27,34,0.5);
         backdrop-filter:blur(12px); border:1px solid {border}; border-radius:15px;
         padding:18px; max-width:100%; overflow-x:auto; color:#C8CDD3;">
        <div data-testid="stMarkdownContainer" style="max-width:100%; overflow-x:auto;">{text}</div>
    </div>
    """, unsafe_allow_html=True)