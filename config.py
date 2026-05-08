from pathlib import Path
from dotenv import load_dotenv
import os

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_API_URL = os.getenv("GROQ_API_URL", "https://api.groq.com/openai/v1/chat/completions")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
MEMORY_DIR = BASE_DIR / "orcha_memory"
MEMORY_DIR.mkdir(exist_ok=True)

MOCK_MODE = os.getenv("MOCK_MODE", "false").lower() == "true"