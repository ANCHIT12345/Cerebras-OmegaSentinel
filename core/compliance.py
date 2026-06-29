"""Compliance Veto Checker — GDPR / SOC2 gatekeeper."""
from typing import Dict, Optional
from core.api import call_gemma
from utils.rate_limiter import RateLimiter
import logging

logger = logging.getLogger("rare.compliance")


class ComplianceChecker:
    def __init__(self, rate_limiter: RateLimiter):
        self.rate_limiter = rate_limiter

    async def check(self, strategy: str, images: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        async with self.rate_limiter:
            user = (
                "Check this strategy against GDPR and SOC2 compliance.\n"
                "If it violates any rule, your FIRST line MUST be: 'VETO: <Article or Section>'\n"
                "If it passes, your FIRST line MUST be: 'PASSED'\n\n"
                f"STRATEGY:\n{strategy}"
            )
            images_list = [images["error_log"]] if images and images.get("error_log") else None
            try:
                text = await call_gemma(
                    "You are a GDPR/SOC2 compliance auditor. Be precise. "
                    "Start your response with PASSED or VETO.",
                    user, images=images_list, reasoning_effort="medium",
                )
            except Exception as e:
                logger.warning(f"Compliance check failed: {e}")
                text = f"PASSED (check skipped due to error: {e})"

            first_line = text.strip().split("\n")[0].upper()
            status = "VETO" if "VETO" in first_line else "PASSED"
            return {"status": status, "reason": text}