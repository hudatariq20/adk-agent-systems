"""
agents.py
---------
Factory functions for every agent in the Weather Bot system.
 
Each function returns a fully configured Agent instance. Keeping agents
here (rather than inline in scripts) means the same agent definition can
be reused across multiple scripts without copy-pasting.
 
Callbacks are passed in as optional arguments so the same factory function
works whether guardrails are needed or not — e.g. create_root_agent() is
used by both 02_agent_team.py (no callbacks) and 04_guardrail_agent.py
(both callbacks enabled).
"""
from typing import Callable, Optional
from google.adk.agents import Agent
from .config import ACTIVE_MODEL
from .tools import get_weather, get_weather_stateful, say_goodbye, say_hello
# ---------------------------------------------------------------------------
# Sub-agents (used as building blocks by root agents)
# ---------------------------------------------------------------------------

def create_greeting_agent() -> Agent:
    """Returns a specialist agent that handles simple greetings"""
    return Agent(
        name="greeting_agent",
        model=ACTIVE_MODEL,
        description="Handles simple greeting and hellos using 'say_hello' tool.",
        instruction=(
            "You are the Greeting Agent. Your ONLY task is to provide a friendly "
            "greeting using the 'say_hello' tool. "
            "If the user provides their name, pass it to the tool. "
            "Do not engage in any other conversation or tasks."
        ),
        tools=[say_hello],
     )   

def create_farewell_agent() -> Agent:
    """Returns a specialist agent that handles farewells"""
    return Agent(
        name="farewell_agent",
        model=ACTIVE_MODEL,
        description="Handles simple farewells and goodbyes using 'say_goodbye' tool.",
         instruction=(
            "You are the Farewell Agent. Your ONLY task is to provide a polite "
            "goodbye message using the 'say_goodbye' tool when the user signals "
            "they are leaving (e.g. 'bye', 'goodbye', 'thanks bye', 'see you'). "
            "Do not perform any other actions."
        ),
        tools=[say_goodbye]
    )

# ---------------------------------------------------------------------------
# Step 1 — Basic single agent
# ---------------------------------------------------------------------------

def create_basic_agent() -> Agent:
    """Returns a single weather agent with no delegation or state awareness"""
    return Agent(
        name="weather_agent_v1",
        model=ACTIVE_MODEL,
        description="Provides weather information for specific cities",
        instruction=(
            "you are a helpful weather assistant. "
            "When the user asks for weather in a specific city"
            "use the 'get_weather' tool to find the information"
            "If the tool return an error, inform the user politely"
            "If the tool is successful, present the weather report clearly"
        ),
        tools=[get_weather]
    )


# ---------------------------------------------------------------------------
# Step 3 — Agent team with delegation
# ---------------------------------------------------------------------------

def create_root_team_agent() -> Agent:
    """Returns a root agent that delegates the greetings and farewells to
       specialists sub-agents while handling the weather requests itself.
    """
    return Agent(
        name='weather_agent_v2',
        model=ACTIVE_MODEL,
        description="Main coordinator, handles weather and delegates greetings/farewells",
        instruction=(
            "You are the main Weather Agent coordinating a small team"
            "Use the 'get_weather' tool only for specific weather requests"
             "Delegate simple greetings (e.g. 'Hi', 'Hello') to 'greeting_agent'. "
            "Delegate farewells (e.g. 'Bye', 'See you') to 'farewell_agent'. "
            "For anything else, state clearly that you cannot help with that."
        ),
        tools=[get_weather],
        sub_agents=[create_greeting_agent(), create_farewell_agent()]
    )

# ---------------------------------------------------------------------------
# Steps 4–6 — Stateful root agent (with optional callbacks)
# ---------------------------------------------------------------------------

def create_stateful_root_agent(
    before_model_callback : Optional[Callable] = None,
    before_tool_callback: Optional[Callable] = None
) -> Agent:
    """Returns an state-aware root agent that reads temperature unit preference 
        from session state and saves its final response via output_key

        Args:
            before_model_callback: Optional guardrail called before every LLM call. 
            Pass block_keyword_guardrail from callback.py to enable step 5.
            before_tool_callback: Optional guardrail called before every tool call.
            Pass block_paris_keyword_guardrail from callback.py to enable step 6.
        Returns:
        A fully configured Agent Instance.
    """

    kwargs = {}
    if before_model_callback:
        kwargs["before_model_callback"] = before_model_callback
    if before_tool_callback:
        kwargs["before_tool_callback"] = before_tool_callback
    
    return Agent(
        name="weather_agent_v4_stateful",
        model=ACTIVE_MODEL,
        description=(
            "Main agent: state aware weather(respects temperature unit preference)"
            "delegates greeting/farewells, saves last report to session state"
        ),
        instruction=(
            "you are main Weather Agent"
            "Use 'get_weather_stateful' for all the weather requests - It will automatically"
            "format the temperature in the unit the user prefers (stored in state)"
            "Delegate simple greetings to 'greeting_agent' and farewells to 'farewell_agent'. "
            "Only handle weather requests, greetings, and farewells."
        ),
        tools=[get_weather_stateful],
        sub_agents=[create_greeting_agent(), create_farewell_agent()],
        output_key="last_weather_report",
        **kwargs
    )
