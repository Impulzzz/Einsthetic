from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
print(f"API Key: {api_key}")
print(f"Testing Groq API...")

try:
    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": "Say hello"}],
        max_tokens=10
    )
    print(f"SUCCESS! Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"ERROR: {e}")
