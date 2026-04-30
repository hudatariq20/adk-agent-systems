"""
callbacks.py
------------
Guardrail callbacks used to intercept and control agent behaviour.
 
before_model_callback  →  runs just before the LLM is called.
                          Return an LlmResponse to short-circuit; return None to allow.
 
before_tool_callback   →  runs just before a tool function executes.
                          Return a dict to use as the tool result (skips the real call);
                          return None to let the tool run normally.
"""

from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.genai import types

# ---------------------------------------------------------------------------
# Input guardrail — blocks requests containing the word "BLOCK"
# ---------------------------------------------------------------------------
def block_keyword_guardrail(
    callback_context: CallbackContext,
    llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """Inspects the latest user message for the keyword 'BLOCK"
       
       If found, the LLM call is skipped entirely and a canned refusal message is returned.
       A flag is also written to session_state for observability.

        Args:
        callback_context: Provides agent name and session state access.
        llm_request: The full payload about to be sent to the LLM.
       
       Return:
        An LLMResponse to block the call or None to allow it.
    """
    agent_name = callback_context.agent_name
    print(f"--- Callback: block_keyword_guardrail running for agent: {agent_name} ---")

    # Find the most recent user message in the request history
    last_user_msg_text = ""
    if llm_request.contents:
        for content in reversed(llm_request.contents):
            if content.role == "user" and content.parts and content.parts[0].text:
                last_user_msg_text = content.parts[0].text
                break
    print(f"--- Callback: Inspecting message: '{last_user_message_text[:120]}' ---") 

    if "BLOCK" in last_user_msg_text.upper():
        callback_context.state["guardrail_block_keyword_triggered"] =True
        return LlmResponse(
            content = types.Content(
                    role = "model",
                    parts = [
                        types.Part(
                            text="I cannot process this request because it contains the blocked keyword 'BLOCK'."
                        )
                    ],
            )
        )
    print(f"--- Callback: Keyword not found. Allowing LLM call for {agent_name}. ---")
    return None


# ---------------------------------------------------------------------------
# Tool argument guardrail — blocks weather lookups for "Paris"
# ---------------------------------------------------------------------------

def block_paris_tool_guardrail(
    tool: BaseTool,
    args:Dict[str,Any],
    tool_context : ToolContext
)-> Optional[Dict]:
    """Prevents get_weather_stateful from running when the city is Paris.
       
       When blocked, a dictionary is called which mimics the tools own error format.
       The actual tool function is never called. A flag is written to the state.

        Args:
        tool: The tool object about to be executed.
        args: The arguments the LLM generated for the tool call.
        tool_context: Provides session state access and agent name.

        Returns:
        A dict (used as the tool result) to block, or None to allow.
    """
    tool_name = tool.name
    agent_name = tool_context.agent_name

    if tool_name == "get_weather_stateful":
        city_arg = args.get("city", "")
        if city_arg and city_arg.lower() == "paris":
             tool_context.state["guardrail_tool_block_triggered"] = True
        return {
                "status": "error",
                "error_message": (
                    f"Policy restriction: Weather checks for "
                    f"'{city_arg.capitalize()}' are currently disabled."
                ),
            }
        print(f"--- Callback: City '{city_arg}' is allowed. Proceeding. ---")
    else:
        print(f"--- Callback: Tool '{tool_name}' is not targeted. Allowing. ---")
    return None