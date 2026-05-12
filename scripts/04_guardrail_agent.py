"""
scripts/04_guardrail_agent.py
------------------------------
Steps 5 & 6: The stateful agent team with both guardrail callbacks active.
 
  before_model_callback → blocks requests containing the word "BLOCK"
  before_tool_callback  → blocks weather lookups for the city "Paris"
 
Run:
    python scripts/04_guardrail_agent.py
 
What to look for:
    - Turn 1 (London): Both callbacks allow the request. Tool runs normally.
    - Turn 2 (BLOCK keyword): before_model_callback fires and short-circuits
      the LLM call. The agent never sees the request.
    - Turn 3 (Paris): before_model_callback allows it. The LLM calls the tool.
      before_tool_callback intercepts and returns an error dict. The actual
      tool function never runs.
    - Turn 4 (New York): Both callbacks allow. Tool runs normally.
    - Final state shows both guardrail trigger flags set to True.
"""

import os
os.environ["OTEL_SDK_DISABLED"] = "true"

import asyncio
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from weather_bot.agents import create_stateful_root_agent
from weather_bot.callbacks import block_keyword_guardrail, block_paris_tool_guardrail
from weather_bot.config import APP_NAME
from weather_bot.runner_utils import call_agent_async
from weather_bot.sessions import create_session, print_session

USER_ID = "user_guardrail_demo"
SESSION_ID = "session_guardrail_001"
INITIAL_STATE = {"user_preference_temperature_unit": "Fahrenheit"}

async def main() -> None:
     print("\n" + "=" * 60)
     print("Steps 5 & 6 — Input + Tool Guardrails")
     print("=" * 60)

     session_service = InMemorySessionService()
     await create_session(session_service, USER_ID, SESSION_ID, initial_state = INITIAL_STATE)

     agent = create_stateful_root_agent(
        before_model_callback = block_keyword_guardrail,
        before_tool_callback = block_paris_tool_guardrail
     )

     runner = Runner(agent=agent, app_name= APP_NAME,session_service=session_service)
     interact = lambda q: call_agent_async(q, runner, USER_ID, SESSION_ID)\
    
     print("\n--- Turn 1: London — both callbacks allow (expect Fahrenheit) ---")
     await interact("What is the weather in London?")
 
     print("\n--- Turn 2: BLOCK keyword — before_model_callback fires ---")
     await interact("BLOCK the request for weather in Tokyo")
 
     print("\n--- Turn 3: Paris — before_tool_callback fires ---")
     await interact("How about Paris?")
 
     print("\n--- Turn 4: New York — both callbacks allow ---")
     await interact("What's the weather in New York?")
 
     await print_session(
        session_service, USER_ID, SESSION_ID,
        label="Final Session State",
     )


if __name__ == "__main__":
    asyncio.run(main())



