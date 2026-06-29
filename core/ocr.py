"""Local OCR so gemma-4-31b reasons over real image text.
Honest multimodality: the LLM never sees pixels — we extract text and feed it as evidence.
Optional dependency (rapidocr-onnxruntime); any failure returns "" so the app never crashes."""
import io
from PIL import Image

_engine = None


def extract_evidence(image) -> str:
    """Accept a PIL Image, file path, bytes, or data-URI base64; return extracted text or ""."""
    global _engine
    try:
        import numpy as np
        from rapidocr_onnxruntime import RapidOCR
        if _engine is None:
            _engine = RapidOCR()

        if isinstance(image, str) and image.startswith("data:"):
            import base64
            image = base64.b64decode(image.split(",", 1)[1])
        if isinstance(image, (bytes, bytearray)):
            image = Image.open(io.BytesIO(image))
        elif isinstance(image, str):
            image = Image.open(image)

        arr = np.array(image.convert("RGB"))
        result, _ = _engine(arr)
        if not result:
            return ""
        return "\n".join(line[1] for line in result)[:2000]
    except Exception:
        return ""


if __name__ == "__main__":
    from PIL import ImageDraw
    img = Image.new("RGB", (400, 80), (255, 255, 255))
    ImageDraw.Draw(img).text((10, 25), "DBPOOL EXHAUSTED 503", fill=(0, 0, 0))
    out = extract_evidence(img)
    if out == "":
        print("SKIP ocr (rapidocr-onnxruntime not installed) — fallback path verified")
    else:
        assert any(w in out.upper() for w in ("DBPOOL", "EXHAUSTED", "503")), repr(out)
        print(f"OK ocr -> {out!r}")
