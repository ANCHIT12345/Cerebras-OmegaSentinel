#!/usr/bin/env python3
"""Test multimodal API call — verify image analysis works."""
import asyncio
import os
import sys
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.api import call_gemma
from core.image_handler import ImageHandler


async def test_text_only():
    print("Test 1: Text-only call...")
    text = await call_gemma(
        "You are a test assistant. Reply in one sentence.",
        "Say 'API OK' if you understand.",
        reasoning_effort="low",
    )
    print(f"  Response: {text[:100]}")
    assert "OK" in text.upper(), "Text call failed"
    print("  ✅ Text-only call WORKS\n")


async def test_image():
    # Create a tiny test image (1x1 pixel)
    import io
    from PIL import Image
    img = Image.new("RGB", (100, 100), color=(255, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    import base64
    b64 = f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode()}"

    print("Test 2: Multimodal (image + text) call...")
    text = await call_gemma(
        "You are a vision test. Describe the image in one sentence.",
        "Describe what color you see in this image.",
        images=[b64],
        reasoning_effort="low",
    )
    print(f"  Response: {text[:200]}")
    print("  ✅ Multimodal call WORKS (model accepted image)\n")


async def main():
    try:
        await test_text_only()
    except Exception as e:
        print(f"  ❌ Text-only call FAILED: {e}")
        print("  Check your API key and network.")
        return

    try:
        await test_image()
    except Exception as e:
        print(f"  ⚠️  Multimodal call failed: {e}")
        print("  The model may not accept images via this endpoint.")
        print("  Text-only mode will still work for the debate.")


if __name__ == "__main__":
    print("=" * 50)
    print("  SENTINEL OMEGA — API Connectivity Test")
    print("=" * 50 + "\n")
    asyncio.run(main())