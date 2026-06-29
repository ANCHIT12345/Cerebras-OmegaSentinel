"""Monte Carlo Burst — 5-10 parallel sims, each a slight variation."""
import asyncio
import random
from typing import Dict, List, Optional

from core.api import call_gemma
from utils.rate_limiter import RateLimiter
import logging

logger = logging.getLogger("rare.mc")

MODIFIERS = [
    "What if the error rate spikes to 80% in the next 5 minutes?",
    "What if the JP market starts trending #BoycottYourBrand?",
    "What if the DB fails over successfully on the first try?",
    "What if a secondary cache node also fails simultaneously?",
    "What if the CEO tweets publicly about the outage?",
    "What if traffic drops 50% due to news coverage?",
    "What if a competitor offers a flash discount at the same time?",
    "What if the rollback fails and requires manual DB intervention?",
    "What if the payment processor throttles your API keys?",
    "What if a Tier-1 retailer pulls integration in 30 minutes?",
]


async def _simulate(scenario: str, modifier: str, image_uri: Optional[str]) -> str:
    user = (
        f"SCENARIO:\n{scenario}\n\n"
        f"VARIATION:\n{modifier}\n\n"
        "Predict the outcome in 2-3 sentences. "
        "Start your first sentence with exactly one of: 'SUCCESS:' 'FAIL:' or 'DEGRADED:'."
    )
    images = [image_uri] if image_uri else None
    return await call_gemma(
        "You are a Monte Carlo crisis simulator. Be terse. Always prefix your answer with the outcome label.",
        user, images=images, reasoning_effort="medium",
    )


class MonteCarloEngine:
    def __init__(self, rate_limiter: RateLimiter, n_sims: int = 7):
        self.rate_limiter = rate_limiter
        self.n_sims = n_sims

    async def run(self, scenario: str, images: Optional[Dict[str, str]] = None) -> Dict:
        selected = random.sample(MODIFIERS, min(self.n_sims, len(MODIFIERS)))
        image_uri = images.get("dashboard") if images else None

        async def _guarded(modifier):
            async with self.rate_limiter:
                try:
                    return await _simulate(scenario, modifier, image_uri)
                except Exception as e:
                    logger.warning(f"MC sim failed: {e}")
                    return f"DEGRADED: exception {type(e).__name__}"

        results = await asyncio.gather(*[_guarded(m) for m in selected])

        def _classify(r: str) -> str:
            head = r.upper()[:200]
            # Strict prefix wins first
            for label in ("FAIL", "DEGRADED", "SUCCESS"):
                if head.startswith(label):
                    return label.lower()
            # Then heuristic keyword search (fail before degrady before success)
            if "FAIL" in head or "COLLAPSE" in head or "CATASTROPHIC" in head or "BLACKOUT" in head:
                return "fail"
            if "DEGRADED" in head or "PARTIAL" in head or "UNSTABLE" in head or "RISK" in head:
                return "degraded"
            return "success"

        buckets = [_classify(r) for r in results]
        success = sum(1 for b in buckets if b == "success")
        fail = sum(1 for b in buckets if b == "fail")
        degraded = sum(1 for b in buckets if b == "degraded")
        total = len(results)
        return {
            "total_sims": total,
            "success": success,
            "fail": fail,
            "degraded": degraded,
            "confidence": round(success / max(total, 1), 2),
            "raw_results": results,
            "modifiers_used": selected,
        }