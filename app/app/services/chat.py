import json

import requests

from app.core.config import get_settings
from app.utils.llm_tools import TRANSACTION_TOOLS

from app.utils.llm_tool_executor import execute_tool_call

MAX_TOOL_ROUNDS = 3  # This is for defining the max number of times the model can call the tools before producing final result

settings = get_settings()

api_key = settings.openrouter_api_key
model = settings.openrouter_model

openrouter_url = settings.openrouter_url


def generate_response(message: str, customer_id: str) -> str:
    if not api_key or not model:
        raise ValueError("OpenRouter configuration is missing")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    messages = [
        {
            "role": "system",
            "content": (
                "You are a professional financial "
                "customer support assistant. "
                "Use available tools when transaction-specific "
                "information is required. "
                "Only report transaction details returned by tools. "
                "Provide clear and concise responses. "
                "Never invent transaction information."
                "Limit response to 50 words."
            ),
        },
        {
            "role": "user",
            "content": message,
        },
    ]

    for round_number in range(MAX_TOOL_ROUNDS + 1):

        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.3,
            "tools": TRANSACTION_TOOLS,
            "tools_choice": "auto",
        }

        response = requests.post(
            url=openrouter_url,
            headers=headers,
            json=payload,
            timeout=30.0,
        )

        response.raise_for_status()

        result = response.json()

        assistant_message = result["choices"][0]["message"]

        tool_calls = assistant_message.get("tool_calls")

        # No tool requested: return the normal response.
        if not tool_calls:
            return assistant_message.get("content") or ""

        # Prevent additional tool execution after the limit.
        if round_number == MAX_TOOL_ROUNDS:
            return (
                "I couldn't complete your request. "
                "Please try again or contact support."
            )

        # Add the assistant's original tool request to the conversation.
        messages.append(assistant_message)

        # Execute each requested tool.
        for tool_call in tool_calls:
            tool_result = execute_tool_call(
                tool_call=tool_call,
                customer_id=customer_id,
            )

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": json.dumps(tool_result),
                }
            )
    return "Unable to complete your request"
