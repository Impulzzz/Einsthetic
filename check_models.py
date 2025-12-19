import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
try:
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    # In v1.56, it might be client.models.list() or similar.
    # We'll try to iterate directly or print dir
    print("Attempting to list models...")
    for m in client.models.list():
        print(f"Model: {m.name}")
except Exception as e:
    print(f"Error: {e}")
