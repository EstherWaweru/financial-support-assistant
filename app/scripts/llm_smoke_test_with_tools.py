import requests

from app.core.config import get_settings

from app.services.llm_tools import TRANSACTION_TOOLS

settings = get_settings()

api_key = settings.openrouter_api_key
model = settings.openrouter_model

openrouter_url = settings.openrouter_url


def request_with_tools(message: str) -> dict:
    if not api_key or not model:
        raise ValueError("OpenRouter configuration is missing")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a financial customer support assistant. "
                    "Use the available tools when you need "
                    "transaction-specific information. "
                    "Never invent transaction details."
                ),
            },
            {
                "role": "user",
                "content": message,
            },
        ],
        "tools": TRANSACTION_TOOLS,
        "tool_choice": "auto",
        "temperature": 0.3,
    }

    response = requests.post(
        openrouter_url,
        headers=headers,
        json=payload,
        timeout=30.0,
    )

    response.raise_for_status()

    return response.json()


result = request_with_tools("What is the status of transaction 12336236?")

message = result["choices"][0]["message"]

print("Assistant message:")
print(message)

print("\nTool calls:")
print(message.get("tool_calls"))
