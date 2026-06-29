from typing import Dict, List
from pydantic import BaseModel


class HardMetrics(BaseModel):
    cpu_load: float = 0.0
    latency_ms: float = 0.0
    error_rate: float = 0.0
    db_connections: int = 0
    cache_hit_rate: float = 0.0


class SoftMetrics(BaseModel):
    sentiment_score: float = 0.0
    social_volume: int = 0
    churn_risk: float = 0.0
    regional_outrage: List[str] = []


class TelemetryVector(BaseModel):
    hard: HardMetrics
    soft: SoftMetrics
    region: str = "Global"
    timestamp: str = ""


def calculate_agent_weights(tv: TelemetryVector) -> Dict[str, float]:
    """Map telemetry → voting weights. Normalizes to 1.0."""
    weights = {
        "Operator": 0.2,
        "Diplomat": 0.2,
        "Red Team": 0.15,
        "Compliance": 0.05,
    }

    # Error rate favors Operator
    if tv.hard.error_rate > 30:
        weights["Operator"] += 0.15

    # Sentiment crash favors Diplomat
    if tv.soft.sentiment_score < -50:
        weights["Diplomat"] += 0.2

    # Churn Risk favors Diplomat
    if tv.soft.churn_risk > 60:
        weights["Diplomat"] += 0.1

    # High social volume favors Red Team
    if tv.soft.social_volume > 1000:
        weights["Red Team"] += 0.05

    total = sum(weights.values())
    return {k: round(v / max(total, 0.01), 3) for k, v in weights.items()}