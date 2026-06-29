from typing import Dict
from agents.kpi_config import KPI_CONFIG

PERSONA_EMOJIS = {
    "Operator": "⚙️",
    "Diplomat": "🌐",
    "Red Team": "🔴",
    "Compliance": "🏛️",
    "Arbitrator": "⚖️",
}

PERSONA_COLORS = {
    "Operator": "#00D4FF",
    "Diplomat": "#00FA9A",
    "Red Team": "#FF4B4B",
    "Compliance": "#9B59B6",
    "Arbitrator": "#FFD700",
}


def build_system_prompt(name: str) -> str:
    cfg = KPI_CONFIG[name]
    return (
        f"You are {name}. You have absolute authority over: {cfg['primary_kpi']}.\n"
        f"Secondary objective: {cfg['secondary_kpi']}.\n"
        f"Incentive: {cfg['incentive']}\n"
        f"Veto authority: {cfg['veto_authority']}\n"
        "You are part of a high-stakes war room. Be concise, decisive, and professional.\n"
        "If you VETO a proposal, start your response with EXACTLY the label in your veto_authority.\n"
        "Back your suggestions with concrete reasoning.\n"
    )


def build_personas() -> Dict[str, Dict]:
    out = {}
    for name in KPI_CONFIG.keys():
        out[name] = {
            "name": name,
            "system_prompt": build_system_prompt(name),
            "color": PERSONA_COLORS[name],
            "emoji": PERSONA_EMOJIS[name],
            "kpi_config": KPI_CONFIG[name],
            "image_key": KPI_CONFIG[name]["image_key"],
            "reasoning_effort": KPI_CONFIG[name].get("reasoning_effort", "high"),
        }
    return out