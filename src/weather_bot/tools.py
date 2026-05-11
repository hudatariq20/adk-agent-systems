from typing import Optional
from google.adk.tools.tool_context import ToolContext

# weather tools.
def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city

    Args:
        city(str) : The name of the city (e.g., "New York", "London", "Tokyo").

    Returns:
        dict: A dictionary containing weather information.
              Includes a 'status' key ('success' or 'error')
              If 'success', includes a 'report' key with weather details.
              If 'error', includes an 'error_message' key.
    """
    print(f"--- Tool: get_weather called for city: {city} ---")
    city_normalized = city.lower().replace(" ", "")

    mock_weather_db = {
        "newyork": {
            "status": "success",
            "report": "The weather in New York is sunny with a temperature of 25°C.",
        },
        "london": {
            "status": "success",
            "report": "It's cloudy in London with a temperature of 15°C.",
        },
        "tokyo": {
            "status": "success",
            "report": "Tokyo is experiencing light rain and a temperature of 18°C.",
        },
    }

    if city_normalized in mock_weather_db:
        return mock_weather_db[city_normalized]
    return {
        "status": "error",
        "error_message": f"Sorry, I don't have weather information for '{city}'.",
    }


def get_weather_stateful(city: str, tool_context: ToolContext) -> dict:
    """Retrieves the current weather and converts the temperature unit based on user's preference
     stored in session state.

     Args:
          city (str): The name of the city
          tool_context (ToolContext) : Injected by ADK; Provides read/write access to session state

    Returns:
            dict: A dictionary with 'status' and either 'report' or 'error_message'.
    """
    print(f"--- Tool: get_weather_stateful called for city: {city} ---")
    preferred_unit = tool_context.state.get(
        "user_preference_temperature_unit", "Celsius")
    print(
        f"--- Tool: Reading state 'user_preference_temperature_unit': {preferred_unit} ---")

    city_normalized = city.lower().replace(" ", "")
    # Internal data always stored in Celsius
    mock_weather_db = {
        "newyork": {"temp_c": 25, "condition": "sunny"},
        "london":  {"temp_c": 15, "condition": "cloudy"},
        "tokyo":   {"temp_c": 18, "condition": "light rain"},
    }
    data = mock_weather_db[city_normalized]
    temp_c = data["temp_c"]

    if preferred_unit == "Fahrenheit":
        temp_value = (temp_c * 9/5) + 32
        temp_unit = "°F"
    else:
        temp_value = temp_c
        temp_unit = "°C"

    report = (
        f"The weather in {city} is {data['condition']}"
        f"with a temperature of {temp_value:.0f}{temp_unit}"
    )

    # write last checked city back to the state for use by other agents/tools
    tool_context.state["last_city_checked_stateful"] = city
    print(f"--- Tool: Updated state 'last_city_checked_stateful': {city} ---")

    return {"status": "success", "report": report}

# ---------------------------------------------------------------------------
# Greeting / farewell tools
# ---------------------------------------------------------------------------


def say_hello(name: Optional[str] = None) -> str:
    """Provides a friendly greeting. Uses the person's name if provided
    Args:
        name (str, optional): The name of the person to greet.

    Returns:
        str: A friendly greeting message.

    """
    if name:
        print(f"--- Tool: say_hello called with name: {name} ---")
        return f"Hello, {name}!"

    print(f"--- Tool: say_hello called without a name ---")
    return "Hello there!"


def say_goodbye() -> str:
    """Provides a polite farewell message to conclude the conversation."""
    print("--- Tool: say_goodbye called ---")
    return "Goodbye! Have a great day."
