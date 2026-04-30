"""
runner_utils.py
---------------
Utility functions for running agents and handling their responses.
"""

from google.adk.runners import Runner
from google.genai import types


async def call_agent_async(
    query: str,
    runner: Runner,
    user_id: str,
    session_id: str,
) -> str:
    """Sends a query to the agent and waits for the final response.

    ADK runner yields a stream of events as it processes a request
    such as tool calls and intermediate thoughts. This helper iterates
    that stream and extracts the single final response event.

    Args:
        query: The user's message to send.
        runner: The configured Runner instance wrapping the agent.
        user_id: Identifies the user for session lookup.
        session_id: Identifies the conversation session.
    """
    print(f"\n>>> User Query: {query}")

    content = types.Content(
        role="user",
        parts=[types.Part(text=query)],
    )

    final_response_text = "Agent did not produce a final response."

    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=content,
    ):
        if event.is_final_response():
            if event.content and event.content.parts:
                final_response_text = event.content.parts[0].text
            elif event.actions and event.actions.escalate:
                final_response_text = (
                    f"Agent escalated: {event.error_message or 'No specific message.'}"
                )
            break

    print(f"<<< Agent Response: {final_response_text}")
    return final_response_text