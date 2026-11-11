import requests

from app.core.config import get_settings

settings = get_settings()

api_key = settings.openrouter_api_key
model = settings.openrouter_model

openrouter_url = settings.openrouter_url


def generate_response(message: str) -> str:
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
                    "You are a professional financial "
                    "customer support assistant. "
                    "Provide clear and concise responses. "
                    "Never invent transaction information."
                    "Limit response to 50 words."
                ),
            },
            {
                "role": "user",
                "content": message,
            },
        ],
        "temperature": 0.3,
    }

    response = requests.post(
        url=openrouter_url,
        headers=headers,
        json=payload,
        timeout=30.0,
    )

    response.raise_for_status()

    result = response.json()

    return result["choices"][0]["message"]["content"]
