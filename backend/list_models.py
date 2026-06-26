import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

import google.genai as genai
client = genai.Client(api_key=api_key)

print("Available generation models:")
for m in client.models.list():
    if "generateContent" in m.supported_actions:
        print(m.name)
