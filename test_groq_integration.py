import requests
import json

print("Testing Groq Question Generation (Updated Test)...")
print("="*60)

# Test with dev login session
session = requests.Session()
login_resp = session.get("http://127.0.0.1:5000/dev/login", allow_redirects=False)
print(f"1. Dev login status: {login_resp.status_code}")

# Generate a question
print("\n2. Requesting question generation...")
print("   Subject: Algorithms, Difficulty: Medium")

response = session.post(
    "http://127.0.0.1:5000/api/generate_question",
    json={
        "subject": "Algorithms",
        "difficulty": "Medium",
        "topic": "Sorting"
    }
)

print(f"\n3. Response Status: {response.status_code}")

if response.status_code == 200:
    try:
        question = response.json()
        print("\n[SUCCESS] Question generated!")
        print(f"\nFull Question Data:")
        print(json.dumps(question, indent=2))
        
        # Check if it's a mock
        if "MOCK" in question.get('question', ''):
            print("\n[WARNING] Got MOCK question - Groq API may have failed")
        else:
            print("\n[VERIFIED] Real question from Groq API!")
    except json.JSONDecodeError:
        print(f"\n[ERROR] Invalid JSON response: {response.text[:200]}")
else:
    print(f"\n[ERROR] Failed with status {response.status_code}")
    print(f"Response: {response.text[:200]}")
