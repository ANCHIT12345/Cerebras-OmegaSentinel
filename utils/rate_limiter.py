import asyncio
from typing import Callable

import logging
logger = logging.getLogger("rare.limiter")


class RateLimiter:
    """Async semaphore guard. Keep under 100 RPM / 100K TPM."""
    def __init__(self, max_concurrent: int = 8):
        self._sem = asyncio.Semaphore(max_concurrent)
        self._active_count = 0

    async def __aenter__(self):
        await self._sem.acquire()
        self._active_count += 1
        return self

    async def __aexit__(self, exc_type, exc, tb):
        self._active_count -= 1
        self._sem.release()

    @property
    def active(self) -> int:
        return self._active_count