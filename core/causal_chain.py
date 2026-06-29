"""Causal Chain XAI — Root Cause → Cascade → Resolution."""
from typing import Optional, Dict
from pydantic import BaseModel, Field
from typing import List

from core.api import call_gemma_json
from utils.rate_limiter import RateLimiter
import logging

logger = logging.getLogger("rare.causal")


class CausalChain(BaseModel):
    root_cause: str
    cascade_events: List[str] = Field(default_factory=list)
    final_impact: str
    resolution_link: str
    full_chain_text: str


SCHEMA = {
    "type": "object",
    "properties": {
        "root_cause": {"type": "string"},
        "cascade_events": {"type": "array", "items": {"type": "string"}},
        "final_impact": {"type": "string"},
        "resolution_link": {"type": "string"},
        "full_chain_text": {"type": "string"},
    },
    "required": ["root_cause", "cascade_events", "final_impact", "resolution_link", "full_chain_text"],
}


class CausalChainGenerator:
    def __init__(self, rate_limiter: RateLimiter):
        self.rate_limiter = rate_limiter

    async def generate(self, strategy, telemetry, images: Optional[Dict[str, str]] = None) -> CausalChain:
        async with self.rate_limiter:
            user = (
                f"STRATEGY:\n{strategy}\n\n"
                f"ERROR RATE: {telemetry.hard.error_rate}%\n"
                f"SENTIMENT: {telemetry.soft.sentiment_score}\n\n"
                "Build a Causal Chain:\n"
                "1. root_cause: The original trigger\n"
                "2. cascade_events: Ordered list of domino effects\n"
                "3. final_impact: End state if untreated\n"
                "4. resolution_link: Where the strategy breaks the chain\n"
                "5. full_chain_text: Markdown formatted vertical flowchart string\n\n"
                "Return valid JSON."
            )
            image_list = list(images.values()) if images else None
            try:
                data = await call_gemma_json(
                    "You are an explainability (XAI) engine. Always return strictly valid JSON.",
                    user, "CausalChain", SCHEMA, images=image_list, reasoning_effort="high",
                )
                return CausalChain(**data)
            except Exception as e:
                logger.warning(f"Causal chain failed: {e}")
                return CausalChain(
                    root_cause="unknown", cascade_events=[],
                    final_impact="unknown", resolution_link="unknown",
                    full_chain_text=f"Chain generation failed: {e}",
                )