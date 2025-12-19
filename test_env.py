import os
from dotenv import load_dotenv

load_dotenv()

groq_key = os.getenv("GROQ_API_KEY")
print(f"GROQ_API_KEY loaded: {groq_key}")
print(f"Key length: {len(groq_key) if groq_key else 0}")
print(f"First 10 chars: {groq_key[:10] if groq_key else 'None'}")
print(f"Last 10 chars: {groq_key[-10:] if groq_key else 'None'}")
