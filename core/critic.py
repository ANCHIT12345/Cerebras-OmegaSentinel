"""Self-Critique Engine — grades the solution across 4 dimensions."""
from pydantic import BaseModel, Field
from typing import Dict, Optional

from core.api import call_gemma_json
from utils.rate_limiter import RateLimiter
import logging

logger = logging.getLogger("rare.critic")


class CritiqueScores(BaseModel):
    technical_soundness: int = 5
    cultural_sensitivity: int = 5
    economic_optimality: int = 5
    temporal_sustainability: int = 5
    overall_score: float = 5.0
    recommended_improvement: str = ""


SCHEMA = {
    "type": "object",
    "properties": {
        "technical_soundness": {"type": "integer"},
        "cultural_sensitivity": {"type": "integer"},
        "economic_optimality": {"type": "integer"},
        "temporal_sustainability": {"type": "integer"},
        "overall_score": {"type": "number"},
        "recommended_improvement": {"type": "string"},
    },
    "required": ["technical_soundness", "cultural_sensitivity", "economic_optimality", "temporal_sustainability", "overall_score", "recommended_improvement"],
}


class SelfCritic:
    def __init__(self, rate_limiter: RateLimiter):
        self.rate_limiter = rate_limiter

    async def score(self, strategy: str, economics, causal_chain) -> CritiqueScores:
        async with self.rate_limiter:
            user = (
                f"STRATEGY:\n{strategy}\n\n"
                f"NET FINANCIAL IMPACT: ${economics.net_impact:,.0f}\n"
                f"ROOT CAUSE: {causal_chain.root_cause}\n"
                f"FINAL IMPACT (if untreated): {causal_chain.final_impact}\n\n"
                "Grade this solution 0-10 on each dimension:\n"
                "- technical_soundness (will the fix work?)\n"
                "- cultural_sensitivity (will humans accept it?)\n"
                "- economic_optimality (cost-effective?)\n"
                "- temporal_sustainability (will it hold up over time?)\n"
                "overall_score = average of all four (one decimal).\n"
                "recommended_improvement = exactly one sentence.\n"
                "Return valid JSON."
            )
            try:
                data = await call_gemma_json(
                    "You are an impartial quality auditor. Return strictly valid JSON.",
                    user, "CritiqueScores", SCHEMA, reasoning_effort="medium",
                )
                return CritiqueScores(**data)
            except Exception as e:
                logger.warning(f"Critique failed: {e}")
                return CritiqueScores(
                    overall_score=5.0,
                    recommended_improvement=f"Scoring failed: {e}",
                )