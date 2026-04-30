"""
sessions.py
-----------
Helpers for creating and inspecting ADK sessions.
 
The InMemorySessionService is fine for local development and tutorials.
If you need state to survive a process restart, swap it out for a
persistent backend (e.g. a database-backed SessionService).
"""

from typing import Any,Dict, Optional
from google.adk.sessions import InMemorySessionService
from .config import APP_NAME

async def create_session(
    session_service: InMemorySessionService,
    user_id: str,
    session_id: str,
    initial_state: Optional[Dict[str,any]]=None,
    app_name:str = APP_NAME
) -> None:
    """Creates a new session, optionally pre-populated with state.

      Args:
        session_service: The session service instance to create the session in
        user_id: Identifies the user this session belongs to,
        session_id: a unique identifier for this conversation session,
        initial_state: Optional key-value pairs to seed the session state with (e.g, user preference), defaults to empty dictionary
        app_name: The application namespace. Defaults to the value in config.


    """
    await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id,
        state=initial_state or {},
    )
    print(f"✅ Session created — app='{app_name}', user='{user_id}', session='{session_id}'")
    if initial_state:
        print(f"   Initial state: {initial_state}")

async def print_session(
    session_service: InMemorySessionService,
    user_id: str,
    session_id:str,
    app_name: str = APP_NAME,
    label:str = "Session State"
)->None:
      """Fetches the current session and print its state dictionary.

        Args:
        session_service: The session service holding the session.
        user_id: The user the session belongs to.
        session_id: The session identifier.
        app_name: The application namespace. Defaults to the value in config.
        label: A heading printed above the state output.

      """
      session = await session_service.get_session(
        app_name=app_name,
        session_id=session_id,
        user_id=user_id
      )
      print(f"\n--- {label} ---")
      if session:
        for key,value in session.state.items():
            print(f"{key} : {value}")
      else:
        print(" ❌ Could not retrieve session.")


def update_state_directly(
    session_service: InMemorySessionService,
    user_id:str,
    session_id:str,
    updates: Dict[str,Any],
    app_name:str = APP_NAME,
)-> None:
    """Directly mutates the in-memory session state for testing purpose
       
       This bypasses the normal agent/tool state-update mechanism and should only be used in tests
       or tutorial scripts to simulate a setting change without building a full UI. It does not work
       with persistent backend sessions - for those, update state via tool actions or service API's

        Args:
        session_service: The InMemorySessionService holding the session.
        user_id: The user the session belongs to.
        session_id: The session identifier.
        updates: Key-value pairs to write into the session state.
        app_name: The application namespace. Defaults to the value in config.
    """
    try:
        stored = session_service.sessions[app_name][user_id][session_id]
        stored.state.update(updates)
        print(f"--- State updated directly: {updates} ---")

    except KeyError as e:
        print(f"❌ Could not update state. Session not found. Missing key: {e}")
