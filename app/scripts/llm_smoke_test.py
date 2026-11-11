import requests
import json

from app.core.config import get_settings

settings = get_settings()

api_key = settings.openrouter_api_key
model = settings.openrouter_model

openrouter_url = settings.openrouter_url


response = requests.post(
    url=openrouter_url,
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    },
    data=json.dumps(
        {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a professional financial "
                        "customer support assistant. "
                        "Provide clear and concise responses. "
                        "Never invent transaction information."
                        "Limit response to 50 words"
                    ),
                },
                {
                    "role": "user",
                    "content": "Why might a bank transfer be delayed? Here is my transaction ID:12336236",
                },
            ],
        }
    ),
)

# Extract the assistant message with reasoning_details
response = response.json()

response = response["choices"][0]["message"]
print(response)
