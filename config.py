"""
Central configuration for the News Verifier pipeline.
All keys are read from environment variables (use a .env file + python-dotenv,
or export them in your shell).
"""
import os

try:
    from dotenv import load_dotenv
    load_dotenv(override=True)  # reads a .env file in the current directory, if present; override existing env vars
except ImportError:
    pass  # python-dotenv not installed; env vars can still be set manually

# --- LLM providers (fill in whichever you have access to; the pipeline
#     will fall back through them in this order: Groq -> Gemini -> OpenRouter) ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct:free")

# --- Optional: Google Fact Check Tools API (free tier, needs a Google Cloud key) ---
GOOGLE_FACTCHECK_API_KEY = os.getenv("GOOGLE_FACTCHECK_API_KEY", "")

# --- Search ---
MAX_SEARCH_RESULTS_PER_CLAIM = int(os.getenv("MAX_SEARCH_RESULTS_PER_CLAIM", "6"))

# --- Trusted domain lists (extend freely) ---
# Used as a cheap, offline-first credibility signal before/alongside live search.
TRUSTED_INTL = {
    "reuters.com", "apnews.com", "bbc.com", "bbc.co.uk", "aljazeera.com",
    "afp.com", "factcheck.afp.com", "snopes.com", "politifact.com",
}
TRUSTED_BD = {
    "prothomalo.com", "thedailystar.net", "bdnews24.com", "tbsnews.net",
    "dhakatribune.com", "banglanews24.com", "jugantor.com", "ittefaq.com.bd",
    "rumorscanner.com",  # Bangladeshi fact-checking org
}
KNOWN_UNRELIABLE = set()  # add known fake-news / satire / propaganda domains here
