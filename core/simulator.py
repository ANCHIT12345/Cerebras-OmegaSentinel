"""Temporal Forecast — predict state at T+1h, T+24h, T+7d."""
import asyncio
import json
from typing import Dict, List, Optional

from pydantic import BaseModel
from core.api import call_gemma_json
from utils.rate_limiter import RateLimiter
import logging

logger = logging.getLogger("rare.sim")


class FutureState(BaseModel):
    time_label: str
    status: str
    system_health: str
    brand_sentiment: str
    financial_impact: str
    regulatory_risk: str
    narrative: str


JUMPS = ["T+1 Hour", "T+24 Hours", "T+7 Days"]

SCHEMA = {
    "type": "object",
    "properties": {
        "system_health": {"type": "string"},
        "brand_sentiment": {"type": "string"},
        "financial_impact": {"type": "string"},
        "regulatory_risk": {"type": "string"},
        "status": {"type": "string"},
        "narrative": {"type": "string"},
    },
    "required": ["system_health", "brand_sentiment", "financial_impact", "regulatory_risk", "status", "narrative"],
}


class TemporalSimulator:
    def __init__(self, rate_limiter: RateLimiter):
        self.rate_limiter = rate_limiter

    async def simulate(self, strategy: str, scenario: str, images: Optional[Dict[str, str]] = None) -> List[FutureState]:
        image_list = list(images.values()) if images else None

        async def _jump(time_label):
            async with self.rate_limiter:
                user = (
                    f"STRATEGY APPLIED:\n{strategy}\n\n"
                    f"CRISIS CONTEXT:\n{scenario}\n\n"
                    f"TIME JUMP: {time_label}\n\n"
                    "Predict: system_health, brand_sentiment, financial_impact, regulatory_risk.\n"
                    "status must be exactly 'SUCCESS', 'FAIL', or 'DEGRADED'.\n"
                    "Return valid JSON."
                )
                try:
                    data = await call_gemma_json(
                        "You are a temporal forecasting engine. Always return strictly valid JSON.",
                        user, "FutureState", SCHEMA, images=image_list, reasoning_effort="high",
                    )
                    return FutureState(time_label=time_label, **data)
                except Exception as e:
                    logger.warning(f"Temporal jump {time_label} failed: {e}")
                    return FutureState(
                        time_label=time_label, status="DEGRADED",
                        system_health="unknown", brand_sentiment="unknown",
                        financial_impact="unknown", regulatory_risk="unknown",
                        narrative=f"Forecast failed: {e}",
                    )

        tasks = [_jump(t) for t in JUMPS]
        return list(await asyncio.gather(*tasks))