"""
config.py
---------
Central configuration for the Weather Bot project.
All settings are read from environment variables, loaded from your .env file.
Nothing is hardcoded here — change values in .env and they take effect
everywhere without touching any Python code.

To switch Gemini models (e.g. when you hit a free-tier RPM limit):
    1. Open .env
    2. Change ACTIVE_MODEL=gemini-2.5-flash to e.g. ACTIVE_MODEL=gemini-2.5-flash-lite
    3. Re-run your script — no code changes needed.

Why os.environ["KEY"] = value after os.getenv("KEY")?
    os.getenv() reads a value into a Python variable — only your code can see it.
    os.environ["KEY"] = value writes it back into the running process environment
    so that third-party SDKs (Google ADK, LiteLLM, etc.) can find it too.
    We only do this when the key actually exists, to avoid writing empty strings.
"""

import os
os.environ["OTEL_SDK_DISABLED"] = os.getenv("OTEL_SDK_DISABLED", "true")
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Google / Gemini
# ---------------------------------------------------------------------------

# Always set this one — it controls whether ADK uses Vertex AI or direct API.
# Default is "False" (direct API with GOOGLE_API_KEY), which is correct for
# free-tier / personal use.
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = os.getenv(
    "GOOGLE_GENAI_USE_VERTEXAI", "False"
)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

# ---------------------------------------------------------------------------
# Optional third-party model keys (only needed for 02_multimodel_agent.py)
# ---------------------------------------------------------------------------

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY:
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if ANTHROPIC_API_KEY:
    os.environ["ANTHROPIC_API_KEY"] = ANTHROPIC_API_KEY

# ---------------------------------------------------------------------------
# Model identifiers
# ---------------------------------------------------------------------------

# Change ACTIVE_MODEL in your .env to switch Gemini models instantly.
# Free-tier options to rotate between when you hit RPM limits:
#   gemini-2.5-flash
#   gemini-2.5-flash-lite
#   gemini-2.5-pro
ACTIVE_MODEL = os.getenv("ACTIVE_MODEL", "gemini-2.5-flash")

# LiteLLM model strings — only used in 02_multimodel_agent.py
MODEL_GPT = os.getenv("MODEL_GPT", "openai/gpt-3.5-turbo")
MODEL_CLAUDE = os.getenv("MODEL_CLAUDE", "anthropic/claude-sonnet-4-20250514")

# ---------------------------------------------------------------------------
# App identifier — used as a namespace for all sessions
# ---------------------------------------------------------------------------

APP_NAME = os.getenv("APP_NAME", "weather_tutorial_app")


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def get_active_model() -> str:
    """Returns the currently configured Gemini model name.
    Change ACTIVE_MODEL in .env to switch models without touching code."""
    return ACTIVE_MODEL


def print_config_status() -> None:
    """Prints a summary of which keys and models are configured.
    Useful to call at the top of a script to confirm your .env loaded correctly."""
    print("--- Config Status ---")
    print(f"  Google API Key  : {'✅ Set' if GOOGLE_API_KEY else ' Not set'}")
    print(f"  OpenAI API Key  : {'✅ Set' if OPENAI_API_KEY else '⚠️  Not set (optional)'}")
    print(f"  Anthropic Key   : {'✅ Set' if ANTHROPIC_API_KEY else '⚠️  Not set (optional)'}")
    print(f"  Active model    : {ACTIVE_MODEL}")
    print(f"  App name        : {APP_NAME}")