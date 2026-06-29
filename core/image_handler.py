import base64
import io
from typing import Optional

from PIL import Image


class ImageHandler:
    MAX_DIMENSION = 1024

    @staticmethod
    def encode_image(image_path: str, max_size: int = None) -> str:
        """Encode file path → base64 data URI."""
        if max_size is None:
            max_size = ImageHandler.MAX_DIMENSION
        img = Image.open(image_path)
        img = ImageHandler._normalize(img, max_size)
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{b64}"

    @staticmethod
    def encode_uploaded(uploaded_file, max_size: int = None) -> str:
        """Encode Streamlit UploadedFile → base64 data URI."""
        if max_size is None:
            max_size = ImageHandler.MAX_DIMENSION
        img = Image.open(uploaded_file)
        img = ImageHandler._normalize(img, max_size)
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{b64}"

    @staticmethod
    def validate_image(image_path: str) -> bool:
        try:
            Image.open(image_path).verify()
            return True
        except Exception:
            return False

    @staticmethod
    def _normalize(img: Image.Image, max_size: int) -> Image.Image:
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        if img.width > max_size or img.height > max_size:
            img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        return img