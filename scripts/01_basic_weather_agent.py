"""
scripts/01_basic_weather_agent.py
----------------------------------
Step 1: A single agent that looks up weather for a city using a mock tool.
 
Run:
    python scripts/01_basic_weather_agent.py
 
What to look for:
    - "--- Tool: get_weather called ---" confirms the agent used the tool.
    - The Paris query returns a tool error, and the agent relays it politely.
"""

import asyncio
import sys
import os
#Allow running from the project root without installing the package
sys.path.insert(0,os.path.join(os.path.dirname(__file__), "..","src"))

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from weather_bot.agents import create_basic_agent
from weather_bot.config import APP_NAME
from weather_bot.runner_utils import call_agent_async
from weather_bot.sessions import create_session

USER_ID = "user_basic"
SESSION_ID = "session_basic_001"

async def main() -> None:
    print("\n" + "=" * 60)
    print("Step 1 — Basic Weather Agent")
    print("=" * 60)

    session_service = InMemorySessionService()
    await create_session(session_service, USER_ID, SESSION_ID)

    agent = create_basic_agent()
    runner = Runner(agent=agent, app_name=APP_NAME, session_service=session_service)

    await call_agent_async("What is the weather like in London?", runner, USER_ID, SESSION_ID)
    await call_agent_async("How about Paris?", runner, USER_ID, SESSION_ID)
    await call_agent_async("Tell me the weather in New York?", runner, USER_ID, SESSION_ID)




if __name__ == "__main__":
    asyncio.run(main())

