import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Scraping Targets
RBI_BASE_URL = "https://www.rbi.org.in"
RBI_PRESS_RELEASE_LIST_URL = "https://www.rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx"
MOCK_SERVER_PORT = 8000
MOCK_SERVER_URL = f"http://localhost:{MOCK_SERVER_PORT}"

# Playwright Settings
PLAYWRIGHT_TIMEOUT_MS = int(os.getenv("PLAYWRIGHT_TIMEOUT_MS", 30000))
HEADLESS_MODE = os.getenv("HEADLESS_MODE", "true").lower() == "true"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)

# LLM Extraction Settings
# Automatically detect OpenAI API key or Gemini API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Choose LLM Endpoint
if GEMINI_API_KEY and not OPENAI_API_KEY:
    # Use Gemini's OpenAI compatibility endpoint
    LLM_API_KEY = GEMINI_API_KEY
    LLM_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
    LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.5-flash")
else:
    LLM_API_KEY = OPENAI_API_KEY or "mock-key-for-offline"
    LLM_BASE_URL = os.getenv("OPENAI_BASE_URL")  # None defaults to official OpenAI API
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")

# Save outputs
OUTPUT_FILE = "regulatory_updates.json"
