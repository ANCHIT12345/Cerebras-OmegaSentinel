import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    API_KEY: str = os.getenv("CEREBRAS_API_KEY", "")
    BASE_URL: str = os.getenv("BASE_URL", "https://api.cerebras.ai/v1")
    MODEL: str = os.getenv("MODEL", "gemma-2-33b")
    LOG_FILE: str = "audit_trail.json"
    MAX_CONCURRENT: int = 8
    MAX_TOKENS: int = 4096


settings = Settings()