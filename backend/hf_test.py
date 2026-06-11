import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("HUGGINGFACE_API_KEY")

if not api_key or api_key == "your_hugging_face_api_token_here":
    print("API Key is missing or default in .env")
    exit()

headers = {"Authorization": f"Bearer {api_key}"}
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"

prompt = "Hello"
payload = {
    "inputs": f"<s>[INST] {prompt} [/INST]",
    "parameters": {"max_new_tokens": 50, "return_full_text": False}
}

try:
    print("Sending request to Hugging Face...")
    response = requests.post(API_URL, headers=headers, json=payload)
    print("Status Code:", response.status_code)
    try:
        print("Response JSON:", response.json())
    except:
        print("Response Text:", response.text)
    response.raise_for_status()
    print("Success!")
except Exception as e:
    print("Exception:", e)
