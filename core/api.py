"""Shared Cerebras API client + JSON-structured output helper."""
import json
import logging


def _enforce_strict(schema: dict) -> None:
    """Recursively add additionalProperties:false to every object schema."""
    if not isinstance(schema, dict):
        return
    if schema.get("type") == "object":
        schema.setdefault("additionalProperties", False)
    for v in schema.values():
        if isinstance(v, dict):
            _enforce_strict(v)
        elif isinstance(v, list):
            for item in v:
                if isinstance(item, dict):
                    _enforce_strict(item)
from typing import Optional, List, Dict, Any

from cerebras.cloud.sdk import AsyncCerebras

from core.config import settings

logger = logging.getLogger("rare.api")

client = AsyncCerebras(api_key=settings.API_KEY)


async def call_gemma(
    system_prompt: str,
    user_text: str,
    images: Optional[List[str]] = None,
    reasoning_effort: str = "medium",
    json_schema: Optional[Dict] = None,
    max_tokens: int = 4096,
) -> str:
    """Single canonical API call. Returns text content."""
    # ponytail: Cerebras models don't support image input. Send content as plain string,
    # not list format — list format triggers multimodal mode even with text-only items.
    if images:
        user_text = f"[{len(images)} image(s) uploaded by user — visual evidence attached but cannot be processed by this model]\n\n{user_text}"

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_text})

    kwargs: Dict[str, Any] = {
        "model": settings.MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
    }
    if reasoning_effort in ("low", "medium", "high"):
        kwargs["reasoning_effort"] = reasoning_effort
    if json_schema:
        # Force strict: Cerebras requires additionalProperties:false on all object schemas
        schema = json_schema.get("schema", json_schema)
        _enforce_strict(schema)
        kwargs["response_format"] = {
            "type": "json_schema",
            "json_schema": {
                "name": json_schema.get("name", "Output"),
                "schema": schema,
                "strict": True,
            },
        }

    try:
        print(f"\n{'='*80}\nDEBUG API CALL — model={settings.MODEL}")
        print(f"MESSAGES: {json.dumps(messages, default=str)[:2000]}")
        print(f"KWARGS keys: {list(kwargs.keys())}")
        print(f"{'='*80}\n")
        resp = await client.chat.completions.create(**kwargs)
        return resp.choices[0].message.content
    except Exception as e:
        logger.error(f"API call failed: {e}")
        print(f"\nAPI ERROR: {e}\n")
        raise


async def call_gemma_stream(
    system_prompt: str,
    user_text: str,
    images: Optional[List[str]] = None,
    reasoning_effort: str = "medium",
    max_tokens: int = 4096,
    on_delta=None,
) -> str:
    """Streaming variant of call_gemma. Calls on_delta(str) per token chunk; returns full text.
    Free-text only (no json_schema) — used for the streamed debate stages."""
    if images:
        user_text = f"[{len(images)} image(s) attached as evidence]\n\n{user_text}"

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_text})

    kwargs: Dict[str, Any] = {
        "model": settings.MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "stream": True,
    }
    if reasoning_effort in ("low", "medium", "high"):
        kwargs["reasoning_effort"] = reasoning_effort

    parts: List[str] = []
    try:
        stream = await client.chat.completions.create(**kwargs)
        async for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            if delta:
                parts.append(delta)
                if on_delta:
                    on_delta(delta)
    except Exception as e:
        logger.error(f"Stream call failed: {e}")
        raise
    return "".join(parts)


async def call_gemma_json(
    system_prompt: str,
    user_text: str,
    schema_name: str,
    schema_body: Dict,
    images: Optional[List[str]] = None,
    reasoning_effort: str = "medium",
) -> Dict:
    """Same as call_gemma but auto-parses JSON."""
    js = {"name": schema_name, "schema": schema_body, "strict": True}
    text = await call_gemma(
        system_prompt, user_text, images=images,
        reasoning_effort=reasoning_effort, json_schema=js,
    )
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # try to extract JSON block
        import re
        m = re.search(r"\{[\s\S]*\}", text)
        if m:
            return json.loads(m.group(0))
        raise