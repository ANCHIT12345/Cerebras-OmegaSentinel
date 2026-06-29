"""Economic Impact Calculator — USD deltas."""
from typing import Optional, Dict

from pydantic import BaseModel
from core.api import call_gemma_json
from utils.rate_limiter import RateLimiter
import logging

logger = logging.getLogger("rare.econ")


class EconomicImpact(BaseModel):
    cost_of_downtime: float
    cost_of_fix: float
    brand_damage_cost: float
    revenue_recovered: float
    net_impact: float
    summary: str


SCHEMA = {
    "type": "object",
    "properties": {
        "cost_of_downtime": {"type": "number"},
        "cost_of_fix": {"type": "number"},
        "brand_damage_cost": {"type": "number"},
        "revenue_recovered": {"type": "number"},
        "net_impact": {"type": "number"},
        "summary": {"type": "string"},
    },
    "required": ["cost_of_downtime", "cost_of_fix", "brand_damage_cost", "revenue_recovered", "net_impact", "summary"],
}


class EconomicCalculator:
    def __init__(self, rate_limiter: RateLimiter):
        self.rate_limiter = rate_limiter

    async def calculate(self, strategy: str, telemetry, images: Optional[Dict[str, str]] = None) -> EconomicImpact:
        async with self.rate_limiter:
            user = (
                f"STRATEGY:\n{strategy}\n\n"
                f"METRICS:\n- Error Rate: {telemetry.hard.error_rate}%\n"
                f"- Sentiment Score: {telemetry.soft.sentiment_score}\n"
                f"- Social Volume: {telemetry.soft.social_volume} posts/min\n"
                f"- Churn Risk: {telemetry.soft.churn_risk}%\n\n"
                "Estimate USD values for: cost_of_downtime, cost_of_fix, brand_damage_cost, revenue_recovered.\n"
                "net_impact = revenue_recovered - (cost_of_downtime + cost_of_fix + brand_damage_cost).\n"
                "Keep numbers realistic for a major e-commerce incident.\n"
                "Return valid JSON."
            )
            try:
                data = await call_gemma_json(
                    "You are a CFO forensic accountant. Return strictly valid JSON in USD.",
                    user, "EconomicImpact", SCHEMA,
                    reasoning_effort="medium",
                )
                return EconomicImpact(**data)
            except Exception as e:
                logger.warning(f"Economics calc failed: {e}")
                return EconomicImpact(
                    cost_of_downtime=50000, cost_of_fix=2000,
                    brand_damage_cost=120000, revenue_recovered=100000,
                    net_impact=-72000, summary=f"Fallback estimates due to error: {e}",
                )