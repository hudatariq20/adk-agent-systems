"""
scripts/03_stateful_agent.py
-----------------------------
Steps 3 & 4: An agent team with delegation + session state memory.
 
This script combines both tutorial steps since they build on each other
naturally — the team structure (Step 3) is the same one that gets state
awareness added (Step 4).
 
Run:
    python scripts/03_stateful_agent.py
 
What to look for:
    - "say_hello" tool fires for "Hello there!" (greeting_agent handled it).
    - "get_weather" tool fires for weather requests (root agent handled it).
    - "say_goodbye" tool fires for "Thanks, bye!" (farewell_agent handled it).
    - London report uses °C (initial preference).
    - New York report uses °F (after manual state update).
    - Final state printout confirms all three values persisted.
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from weather_bot.agents import create_stateful_root_agent
from weather_bot.config import APP_NAME
from weather_bot.runner_utils import call_agent_async
from weather_bot.sessions import create_session, print_session,update_state_directly

USER_ID = "user_state_demo"
SESSION_ID = "session_state_demo_001"
INITIAL_STATE = {"user_preference_temperature_unit": "Celsius"}

async def main() -> None:
    print("\n" + "=" * 60)
    print("Steps 3 & 4 — Agent Team + Session State")
    print("=" * 60)

    session_service = InMemorySessionService()
    await create_session(session_service, USER_ID, SESSION_ID, initial_state=INITIAL_STATE)

    agent = create_stateful_root_agent()
    runner = Runner(agent=agent, app_name = APP_NAME, session_service = session_service)
    
    interact = lambda q : call_agent_async(q, runner, USER_ID, SESSION_ID)
    # --- Step 3: delegation ---
    print("\n--- Delegation Tests ---")
    await interact("Hello there!")
    await interact("Thanks, bye!")

    # --- Step 4: state-aware weather ---
    print("\n--- State Tests ---")

    print("\n--- Turn 1: London (expect Celsius) ---")
    await interact("What's the weather in London?")
    
     # Simulate a user changing their unit preference (e.g. via a settings page)
    print("\n--- Simulating user changing preference to Fahrenheit ---")
    update_state_directly(
        session_service,
        USER_ID,
        SESSION_ID,
        {"user_preference_temperature_unit" : "Fahrenheit"}
    )
    print("\n--- Turn 2: New York (expect Fahrenheit) ---")
    await interact("Tell me the weather in New York.")

    # Confirm final state
    await print_session(
        session_service, USER_ID, SESSION_ID,
        label="Final Session State",
    )


if __name__ == "__main__":
    asyncio.run(main())