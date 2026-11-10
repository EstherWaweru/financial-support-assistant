import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()


api_key = os.getenv("OPENROUTER_API_KEY")
model = os.getenv("OPENROUTER_MODEL")

response = requests.post(
  url="https://openrouter.ai/api/v1/chat/completions",
  headers={
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
  },
  data=json.dumps({
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
          )
        },
        {
                    "role": "user",
                    "content": "Why might a bank transfer be delayed? Here is my transaction ID:12336236",
                },
      ],
  })
)

# Extract the assistant message with reasoning_details
response = response.json()

response = response['choices'][0]['message']
print(response)








